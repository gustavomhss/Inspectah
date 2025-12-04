from __future__ import annotations
from dataclasses import dataclass, asdict, field as dataclass_field
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit, urlunsplit

try:  # pragma: no cover
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from ..config import FIELDS_DIR
from .iel import evaluate_expression, validate_expression


@dataclass
class FieldDefinition:
    name: str
    type: str
    path: str
    transforms: List[str] = dataclass_field(default_factory=list)
    default: Optional[Any] = None


@dataclass
class ComputedFieldDefinition:
    name: str
    type: str
    expression: str
    fallback: Any


@dataclass
class FieldSchema:
    schema_id: str
    version: int
    status: str
    description: str
    owner: str
    created_at: datetime
    updated_at: datetime
    fields: List[FieldDefinition]
    computed_fields: List[ComputedFieldDefinition] = dataclass_field(default_factory=list)


@dataclass
class FieldValue:
    name: str
    type: str
    value: Any


def parse_rfc822_date(value: str) -> datetime:
    if value is None:
        raise ValueError("date value cannot be None")
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("date value cannot be empty")
    try:
        parsed = parsedate_to_datetime(trimmed)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"unable to parse RFC822 date: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def normalize_url(value: str) -> str:
    if value is None:
        raise ValueError("url value cannot be None")
    trimmed = value.strip()
    if not trimmed:
        raise ValueError("url value cannot be empty")
    parsed = urlsplit(trimmed)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"invalid url: {value}")
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, parsed.fragment))


_TRANSFORMS = {
    "parse_rfc822_date": parse_rfc822_date,
    "normalize_url": normalize_url,
}


def _extract_path(payload: Dict[str, Any], path: str) -> Any:
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def apply_field_definitions(definitions: List[FieldDefinition], payload: Dict[str, Any]) -> List[FieldValue]:
    results: List[FieldValue] = []
    for definition in definitions:
        value = _extract_path(payload, definition.path)
        if value is None and definition.default is not None:
            value = definition.default
        if value is None:
            continue
        for transform in definition.transforms:
            func = _TRANSFORMS.get(transform)
            if func is None:
                raise ValueError(f"unknown transform {transform}")
            value = func(value)
        results.append(FieldValue(name=definition.name, type=definition.type, value=value))
    return results


def _schema_root(custom_dir: Optional[Path] = None) -> Path:
    root = (custom_dir or FIELDS_DIR) / "schemas"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _schema_dir(schema_id: str, registry_dir: Optional[Path] = None) -> Path:
    root = _schema_root(registry_dir)
    schema_dir = root / schema_id
    schema_dir.mkdir(parents=True, exist_ok=True)
    return schema_dir


def _manifest_path(schema_id: str, registry_dir: Optional[Path]) -> Path:
    return _schema_dir(schema_id, registry_dir) / "manifest.json"


def _load_manifest(schema_id: str, registry_dir: Optional[Path]) -> Dict[str, Any]:
    manifest_path = _manifest_path(schema_id, registry_dir)
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text())


def _write_manifest(schema_id: str, manifest: Dict[str, Any], registry_dir: Optional[Path]) -> None:
    manifest_path = _manifest_path(schema_id, registry_dir)
    manifest_path.write_text(json.dumps(manifest, indent=2))


def _write_schema_file(schema: FieldSchema, registry_dir: Optional[Path]) -> Path:
    schema_dir = _schema_dir(schema.schema_id, registry_dir)
    path = schema_dir / f"v{schema.version}.yaml"
    payload = {
        "schema_id": schema.schema_id,
        "version": schema.version,
        "status": schema.status,
        "description": schema.description,
        "owner": schema.owner,
        "created_at": schema.created_at.isoformat(),
        "updated_at": schema.updated_at.isoformat(),
        "fields": [asdict(field) for field in schema.fields],
        "computed_fields": [asdict(field) for field in schema.computed_fields],
    }
    if yaml is not None:
        path.write_text(yaml.safe_dump(payload, sort_keys=False))
    else:
        path.write_text(json.dumps(payload, indent=2))
    return path


def _next_version(schema_id: str, registry_dir: Optional[Path]) -> int:
    manifest = _load_manifest(schema_id, registry_dir)
    return int(manifest.get("latest_version", 0)) + 1


def _validate_computed_fields(entries: List[ComputedFieldDefinition], *, allowed_vars: Optional[List[str]] = None) -> None:
    allowed = allowed_vars or []
    for entry in entries:
        if not entry.expression:
            raise ValueError(f"computed field {entry.name} must have expression")
        validate_expression(entry.expression, allowed_variables=allowed + [entry.name])


def create_schema(
    schema_id: str,
    fields: List[FieldDefinition],
    *,
    computed_fields: Optional[List[ComputedFieldDefinition]] = None,
    status: str = "draft",
    description: str = "",
    owner: str = "",
    registry_dir: Optional[Path] = None,
) -> FieldSchema:
    version = _next_version(schema_id, registry_dir)
    now = datetime.now(timezone.utc)
    computed = computed_fields or []
    allowed_vars = [f.name for f in fields]
    _validate_computed_fields(computed, allowed_vars=allowed_vars)
    schema = FieldSchema(
        schema_id=schema_id,
        version=version,
        status=status,
        description=description,
        owner=owner,
        created_at=now,
        updated_at=now,
        fields=fields,
        computed_fields=computed,
    )
    _write_schema_file(schema, registry_dir)
    manifest = _load_manifest(schema_id, registry_dir)
    versions = manifest.get("versions", {})
    versions[str(version)] = {
        "status": status,
        "description": description,
        "owner": owner,
        "created_at": schema.created_at.isoformat(),
        "updated_at": schema.updated_at.isoformat(),
    }
    manifest.update({"schema_id": schema_id, "latest_version": version, "versions": versions})
    _write_manifest(schema_id, manifest, registry_dir)
    return schema


def update_schema(
    schema_id: str,
    fields: List[FieldDefinition],
    *,
    computed_fields: Optional[List[ComputedFieldDefinition]] = None,
    status: str = "active",
    description: Optional[str] = None,
    owner: Optional[str] = None,
    registry_dir: Optional[Path] = None,
) -> FieldSchema:
    manifest = _load_manifest(schema_id, registry_dir)
    if not manifest:
        raise ValueError(f"schema {schema_id} not found")
    version = int(manifest["latest_version"]) + 1
    now = datetime.now(timezone.utc)
    computed = computed_fields or []
    allowed_vars = [f.name for f in fields]
    _validate_computed_fields(computed, allowed_vars=allowed_vars)
    schema = FieldSchema(
        schema_id=schema_id,
        version=version,
        status=status,
        description=description or manifest["versions"][str(manifest["latest_version"])].get("description", ""),
        owner=owner or manifest["versions"][str(manifest["latest_version"])].get("owner", ""),
        created_at=datetime.fromisoformat(manifest["versions"][str(manifest["latest_version"])]["created_at"])
        if manifest.get("versions")
        else now,
        updated_at=now,
        fields=fields,
        computed_fields=computed,
    )
    _write_schema_file(schema, registry_dir)
    versions = manifest.get("versions", {})
    versions[str(version)] = {
        "status": status,
        "description": schema.description,
        "owner": schema.owner,
        "created_at": schema.created_at.isoformat(),
        "updated_at": schema.updated_at.isoformat(),
    }
    manifest.update({"schema_id": schema_id, "latest_version": version, "versions": versions})
    _write_manifest(schema_id, manifest, registry_dir)
    return schema


def load_schema(schema_id: str, version: Optional[int] = None, *, registry_dir: Optional[Path] = None) -> FieldSchema:
    manifest = _load_manifest(schema_id, registry_dir)
    if not manifest:
        raise ValueError(f"schema {schema_id} not found")
    target_version = version or int(manifest["latest_version"])
    schema_dir = _schema_dir(schema_id, registry_dir)
    path = schema_dir / f"v{target_version}.yaml"
    if not path.exists():
        raise ValueError(f"schema version {target_version} for {schema_id} not found")
    if yaml is not None:
        data = yaml.safe_load(path.read_text())
    else:
        data = json.loads(path.read_text())
    fields = [
        FieldDefinition(
            name=entry["name"],
            type=entry["type"],
            path=entry["path"],
            transforms=entry.get("transforms", []),
            default=entry.get("default"),
        )
        for entry in data.get("fields", [])
    ]
    computed = [
        ComputedFieldDefinition(
            name=entry["name"],
            type=entry["type"],
            expression=entry["expression"],
            fallback=entry["fallback"],
        )
        for entry in data.get("computed_fields", [])
    ]
    return FieldSchema(
        schema_id=data["schema_id"],
        version=int(data["version"]),
        status=data.get("status", "draft"),
        description=data.get("description", ""),
        owner=data.get("owner", ""),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        fields=fields,
        computed_fields=computed,
    )


def list_schemas(*, registry_dir: Optional[Path] = None) -> List[FieldSchema]:
    root = _schema_root(registry_dir)
    schemas: List[FieldSchema] = []
    if not root.exists():
        return schemas
    for schema_dir in sorted(root.iterdir()):
        if not schema_dir.is_dir():
            continue
        schema_id = schema_dir.name
        try:
            schemas.append(load_schema(schema_id, registry_dir=registry_dir))
        except ValueError:
            continue
    return schemas


def evaluate_computed_fields(
    computed_fields: List[ComputedFieldDefinition],
    values: Dict[str, Any],
    *,
    history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {}
    for computed in computed_fields:
        try:
            result = evaluate_expression(computed.expression, values, history=history)
            if result is None:
                result = computed.fallback
        except Exception:
            result = computed.fallback
        results[computed.name] = result
    return results


__all__ = [
    "FieldDefinition",
    "FieldValue",
    "ComputedFieldDefinition",
    "FieldSchema",
    "parse_rfc822_date",
    "normalize_url",
    "apply_field_definitions",
    "create_schema",
    "update_schema",
    "load_schema",
    "list_schemas",
    "evaluate_computed_fields",
]
