from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _resolve_path(value: str | Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / value
    return path.resolve()


def _load_yaml(path: Path) -> Mapping[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        raise ValueError(f"{path} is empty")
    if not isinstance(data, Mapping):
        raise ValueError(f"{path} must contain a mapping")
    return data


@dataclass(slots=True)
class SourceConfig:
    id: str
    name: str
    type: str
    sample_file: Path
    description: str | None = None
    config_path: Path | None = None
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FieldDefinition:
    name: str
    type: str
    required: bool
    description: str
    sources: Dict[str, str]
    transforms: List[str] = field(default_factory=list)


@dataclass(slots=True)
class DomainConfig:
    domain: str
    name: str
    description: str
    timezone: str
    dedup_fields: List[str]
    search_fields: List[str]
    filters: Dict[str, Dict[str, Any]]
    fields: List[FieldDefinition]
    sources: Dict[str, SourceConfig]
    supporting_fields: List[str] = field(default_factory=list)
    raw: Dict[str, Any] = field(default_factory=dict)

    @property
    def out_dir(self) -> Path:
        return REPO_ROOT / "out" / self.domain

    @property
    def canonical_records_path(self) -> Path:
        return self.out_dir / "canonical_records.json"

    @property
    def summary_path(self) -> Path:
        return self.out_dir / "collection_summary.json"

    @property
    def evidence_root(self) -> Path:
        return REPO_ROOT / "out" / "evidence" / self.domain

    @property
    def queries_root(self) -> Path:
        return REPO_ROOT / "out" / "queries"


def _parse_sources(entries: List[Mapping[str, Any]]) -> Dict[str, SourceConfig]:
    sources: Dict[str, SourceConfig] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("source entry must be a mapping")
        source_id = str(entry.get("id", "")).strip()
        if not source_id:
            raise ValueError("source entry missing 'id'")
        cfg_path = entry.get("config")
        data: Mapping[str, Any]
        if cfg_path:
            config_path = _resolve_path(cfg_path)
            data = _load_yaml(config_path)
        else:
            config_path = None
            data = entry
        sample_file = data.get("sample_file")
        if not sample_file:
            raise ValueError(f"source {source_id} missing sample_file")
        source = SourceConfig(
            id=str(data.get("id", source_id)),
            name=str(data.get("name", source_id)),
            type=str(data.get("type", "rss")).lower(),
            description=data.get("description"),
            sample_file=_resolve_path(str(sample_file)),
            config_path=config_path,
            raw=dict(data),
        )
        sources[source.id] = source
    return sources


def _parse_fields(entries: List[Mapping[str, Any]]) -> List[FieldDefinition]:
    fields: List[FieldDefinition] = []
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("field entry must be a mapping")
        name = str(entry.get("name", "")).strip()
        if not name:
            raise ValueError("field entry missing name")
        sources_data = entry.get("sources")
        if not isinstance(sources_data, Mapping):
            raise ValueError(f"field {name} missing sources mapping")
        fields.append(
            FieldDefinition(
                name=name,
                type=str(entry.get("type", "string")).lower(),
                required=bool(entry.get("required", True)),
                description=str(entry.get("description", "")),
                sources={str(k): str(v) for k, v in sources_data.items()},
                transforms=[str(t).lower() for t in entry.get("transforms", [])],
            )
        )
    return fields


def load_domain_config(domain: str = "dominio_piloto") -> DomainConfig:
    path = _resolve_path(f"config/fields/{domain}.yaml")
    data = _load_yaml(path)
    sources_entries = data.get("sources")
    if not isinstance(sources_entries, list) or not sources_entries:
        raise ValueError(f"{path} missing 'sources'")
    fields_entries = data.get("fields")
    if not isinstance(fields_entries, list) or not fields_entries:
        raise ValueError(f"{path} missing 'fields'")
    dedup_fields = [str(value) for value in data.get("dedup_fields", []) if str(value)]
    if not dedup_fields:
        raise ValueError(f"{path} missing 'dedup_fields'")
    search_fields = [str(value) for value in data.get("search_fields", [])]
    filters = {str(name): dict(payload) for name, payload in dict(data.get("filters", {})).items()}
    supporting_fields = [str(field.get("name")) for field in data.get("supporting_fields", []) if field.get("name")]
    return DomainConfig(
        domain=str(data.get("domain", domain)),
        name=str(data.get("name", domain)),
        description=str(data.get("description", "")),
        timezone=str(data.get("timezone", "UTC")),
        dedup_fields=dedup_fields,
        search_fields=search_fields,
        filters=filters,
        fields=_parse_fields(fields_entries),
        sources=_parse_sources(sources_entries),
        supporting_fields=supporting_fields,
        raw=json.loads(json.dumps(data)),
    )


def load_sources_config(domain: str = "dominio_piloto") -> Dict[str, SourceConfig]:
    return load_domain_config(domain).sources


def load_fields_config(domain: str = "dominio_piloto") -> List[FieldDefinition]:
    return load_domain_config(domain).fields
