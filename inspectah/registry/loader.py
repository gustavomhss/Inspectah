from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:  # pragma: no cover - executed depending on environment
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    yaml = None

from ..config import FIELDS_DIR, SOURCES_DIR
from ..fields.designer import FieldDefinition


@dataclass
class SourceConfig:
    id: str
    type: str
    name: str
    url: str
    schedule_minutes: int
    enabled: bool


@dataclass
class FieldConfig:
    source_id: str
    definitions: List[FieldDefinition]


_REQUIRED_SOURCE_KEYS = {"id", "type", "name", "url", "schedule_minutes", "enabled"}
_REQUIRED_FIELD_KEYS = {"name", "type", "path"}
_EXPECTED_FIELDS_D8 = {"title", "url", "published_at", "source_name"}


def _decode_mapping(text: str, path: Path) -> Dict[str, object]:
    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except Exception as exc:  # pragma: no cover
            raise ValueError(f"invalid yaml: {path}") from exc
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid config (expecting JSON-compatible YAML) in {path}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"unexpected structure in {path}")
    return data


def load_sources(directory: Optional[Path] = None) -> Dict[str, SourceConfig]:
    dir_path = directory or SOURCES_DIR
    results: Dict[str, SourceConfig] = {}
    if not dir_path.exists():
        return results
    for path in sorted(dir_path.glob("*.yaml")):
        data = _decode_mapping(path.read_text(), path)
        missing = _REQUIRED_SOURCE_KEYS - data.keys()
        if missing:
            raise ValueError(f"missing keys {sorted(missing)} in {path}")
        try:
            schedule = int(data["schedule_minutes"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"schedule_minutes must be int in {path}") from exc
        enabled = data["enabled"]
        if not isinstance(enabled, bool):
            raise ValueError(f"enabled must be bool in {path}")
        cfg = SourceConfig(
            id=str(data["id"]),
            type=str(data["type"]),
            name=str(data["name"]),
            url=str(data["url"]),
            schedule_minutes=schedule,
            enabled=enabled,
        )
        results[cfg.id] = cfg
    return results


def load_fields(directory: Optional[Path] = None) -> Dict[str, FieldConfig]:
    dir_path = directory or FIELDS_DIR
    configs: Dict[str, FieldConfig] = {}
    if not dir_path.exists():
        return configs
    for path in sorted(dir_path.glob("*.yaml")):
        data = _decode_mapping(path.read_text(), path)
        if "source_id" not in data:
            raise ValueError(f"missing source_id in {path}")
        fields_data = data.get("fields")
        if not isinstance(fields_data, list) or not fields_data:
            raise ValueError(f"fields must be a non-empty list in {path}")
        definitions: List[FieldDefinition] = []
        seen_names = set()
        for entry in fields_data:
            if not isinstance(entry, dict):
                raise ValueError(f"field entry must be mapping in {path}")
            missing = _REQUIRED_FIELD_KEYS - entry.keys()
            if missing:
                raise ValueError(f"missing field keys {sorted(missing)} in {path}")
            name = str(entry["name"])
            seen_names.add(name)
            transforms = entry.get("transforms", [])
            if transforms is None:
                transforms = []
            if not isinstance(transforms, list):
                raise ValueError(f"transforms must be list for field {name} in {path}")
            default = entry.get("default")
            definitions.append(
                FieldDefinition(
                    name=name,
                    type=str(entry["type"]),
                    path=str(entry["path"]),
                    transforms=[str(t) for t in transforms],
                    default=default,
                )
            )
        source_id = str(data["source_id"])
        if source_id == "rss_news_minimal":
            missing_expected = _EXPECTED_FIELDS_D8 - seen_names
            if missing_expected:
                raise ValueError(f"rss_news_minimal missing fields {sorted(missing_expected)}")
        configs[source_id] = FieldConfig(source_id=source_id, definitions=definitions)
    return configs


def get_source_config(source_id: str) -> SourceConfig:
    sources = load_sources()
    if source_id not in sources:
        raise KeyError(f"unknown source {source_id}")
    return sources[source_id]


def get_field_config(source_id: str) -> FieldConfig:
    fields = load_fields()
    if source_id not in fields:
        raise KeyError(f"missing fields for {source_id}")
    return fields[source_id]
