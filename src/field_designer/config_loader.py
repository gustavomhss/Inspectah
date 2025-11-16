from __future__ import annotations
import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping

try:  # pragma: no cover - runtime dependency optional
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

DEFAULT_CONFIG_DIR = Path("configs/sources")
CONFIG_DIR_ENV = "INSPECTAH_SOURCES_CONFIG_DIR"


def _resolve_path(value: str | Path, base_dir: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


@dataclass(slots=True)
class FieldMapping:
    name: str
    type: str
    path: str
    required: bool = True
    default: Any | None = None
    description: str | None = None


@dataclass(slots=True)
class SourceConfig:
    id: str
    name: str
    type: str
    description: str | None
    sample_file: Path
    fields: List[FieldMapping] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    dedup_fields: List[str] = field(default_factory=list)
    canonical_path: str | None = None
    timestamp_path: str | None = None
    raw: Dict[str, Any] = field(default_factory=dict)


def _load_yaml(path: Path) -> Mapping[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if data is None:
        raise ValueError(f"config file {path} is empty")
    if not isinstance(data, MutableMapping):
        raise ValueError(f"config file {path} must contain a mapping")
    return data


def _load_field_mappings(data: Mapping[str, Any]) -> List[FieldMapping]:
    fields_data = data.get("fields")
    if not isinstance(fields_data, list) or not fields_data:
        raise ValueError("fields must be a non-empty list")
    mappings: List[FieldMapping] = []
    for entry in fields_data:
        if not isinstance(entry, Mapping):
            raise ValueError("field entry must be a mapping")
        try:
            mapping = FieldMapping(
                name=str(entry["name"]),
                type=str(entry["type"]),
                path=str(entry["path"]),
                required=bool(entry.get("required", True)),
                default=entry.get("default"),
                description=entry.get("description"),
            )
        except KeyError as exc:  # pragma: no cover - validated above
            raise ValueError(f"missing key {exc} in field definition") from exc
        mappings.append(mapping)
    return mappings


def _resolve_config_dir(custom_dir: str | Path | None = None) -> Path:
    candidate = custom_dir or os.environ.get(CONFIG_DIR_ENV)
    if candidate:
        return Path(candidate).expanduser().resolve()
    return DEFAULT_CONFIG_DIR.resolve()


def load_source_configs(config_dir: str | Path | None = None) -> Dict[str, SourceConfig]:
    directory = _resolve_config_dir(config_dir)
    if not directory.exists():
        raise FileNotFoundError(f"configs directory {directory} does not exist")
    base_dir = Path.cwd()
    configs: Dict[str, SourceConfig] = {}
    for path in sorted(directory.glob("*.yaml")):
        data = _load_yaml(path)
        required = {"id", "name", "type", "sample_file"}
        missing = required - data.keys()
        if missing:
            raise ValueError(f"missing keys {sorted(missing)} in {path}")
        sample_file = _resolve_path(str(data["sample_file"]), base_dir)
        dedup_fields = [str(entry) for entry in data.get("dedup_fields", [])]
        canonical_path = data.get("canonical_path")
        timestamp_path = data.get("timestamp_path")
        cfg = SourceConfig(
            id=str(data["id"]),
            name=str(data["name"]),
            type=str(data["type"]).lower(),
            description=data.get("description"),
            sample_file=sample_file,
            fields=_load_field_mappings(data),
            options=dict(data.get("options", {})),
            dedup_fields=dedup_fields,
            canonical_path=str(canonical_path) if canonical_path else None,
            timestamp_path=str(timestamp_path) if timestamp_path else None,
            raw=dict(data),
        )
        configs[cfg.id] = cfg
    if not configs:
        raise ValueError(f"no source configs found in {directory}")
    return configs


def get_source_config(source_id: str, *, config_dir: str | Path | None = None) -> SourceConfig:
    configs = load_source_configs(config_dir)
    if source_id not in configs:
        raise KeyError(f"unknown source config {source_id}")
    return configs[source_id]
