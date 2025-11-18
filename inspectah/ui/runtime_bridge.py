from __future__ import annotations

import numbers
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

import yaml
from fastapi.encoders import jsonable_encoder
from inspectah.sprint6 import collector, config as sprint6_config, query_engine

from .schemas import (
    CanonicalRecord,
    ConsolidatedDecision,
    EvidencePackage,
    FieldSchema,
    QueryFilters,
    SourceSchema,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCES_DIR = REPO_ROOT / "config" / "sources"


def is_runtime_available() -> bool:
    try:
        sprint6_config.load_domain_config()
    except Exception:
        return False
    return True


def list_sources() -> List[SourceSchema]:
    sources: List[SourceSchema] = []
    for path in sorted(SOURCES_DIR.glob("*.yaml")):
        data = _load_yaml(path)
        sources.append(_serialize_source(data, path))
    return sorted(sources, key=lambda src: src.id)


def get_source(source_id: str) -> SourceSchema | None:
    path = _source_file(source_id)
    if not path.exists():
        return None
    return _serialize_source(_load_yaml(path), path)


def update_source(source_id: str, updates: Mapping[str, Any]) -> SourceSchema:
    path = _source_file(source_id)
    if not path.exists():
        raise FileNotFoundError(f"Fonte {source_id} não encontrada")
    data = _load_yaml(path)
    for key, value in updates.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip() and key != "notes":
            continue
        _set_nested(data, key, value)
    _write_yaml(path, data)
    return _serialize_source(data, path)


def create_source(payload: Mapping[str, Any]) -> SourceSchema:
    source_id = str(payload.get("id", "")).strip()
    if not source_id:
        raise ValueError("Campo 'id' obrigatório para criar fonte")
    path = _source_file(source_id)
    if path.exists():
        raise ValueError(f"Fonte {source_id} já existe")
    data: Dict[str, Any] = {"id": source_id}
    for key, value in payload.items():
        if key == "id" or value is None:
            continue
        if "." in key:
            _set_nested(data, key, value)
        else:
            data[key] = value
    data.setdefault("name", source_id)
    data.setdefault("type", "rss")
    data.setdefault("sample_file", "")
    data.setdefault("notes", [])
    data.setdefault("enabled", True)
    _write_yaml(path, data)
    return _serialize_source(data, path)


def list_fields(domain: str = "dominio_piloto") -> List[FieldSchema]:
    cfg = sprint6_config.load_domain_config(domain)
    fields: List[FieldSchema] = []
    for field in cfg.fields:
        fields.append(
            FieldSchema(
                name=field.name,
                title=getattr(field, "title", None) or field.name.replace("_", " ").title(),
                type=field.type,
                required=field.required,
                description=field.description,
                sources=dict(field.sources),
            )
        )
    return fields


def get_samples_by_source(limit: int = 3, domain: str = "dominio_piloto") -> Dict[str, List[CanonicalRecord]]:
    records = _load_canonical_records(domain)
    buckets: Dict[str, List[CanonicalRecord]] = {}
    for record in records:
        canonical = CanonicalRecord.model_validate(record)
        for supporting in canonical.supporting_sources:
            source_id = supporting.get("source_id")
            if not source_id:
                continue
            slot = buckets.setdefault(source_id, [])
            if len(slot) < limit:
                slot.append(canonical)
    return buckets


def run_query(filters: QueryFilters, domain: str = "dominio_piloto") -> List[CanonicalRecord]:
    result = query_engine.run_query(
        domain=domain,
        from_date=filters.from_date,
        to_date=filters.to_date,
        categoria=filters.categoria,
        regiao=filters.regiao,
        fonte=filters.fonte,
        search=filters.search,
        page=1,
        page_size=50,
    )
    return [CanonicalRecord.model_validate(item) for item in result.items]


def consolidate(records: Sequence[CanonicalRecord]) -> ConsolidatedDecision:
    prices = [float(record.price_brl) for record in records if isinstance(record.price_brl, numbers.Real)]
    if not prices:
        return ConsolidatedDecision(
            strategy="median",
            value=None,
            sample_count=0,
            sources_used=[],
            explanation="Nenhum preço disponível para consolidação.",
            supporting_records=[],
        )
    sorted_prices = sorted(prices)
    mid = len(sorted_prices) // 2
    if len(sorted_prices) % 2 == 1:
        value = sorted_prices[mid]
    else:
        value = (sorted_prices[mid - 1] + sorted_prices[mid]) / 2
    sources_used = sorted({support.get("source_id", "") for record in records for support in record.supporting_sources if support.get("source_id")})
    supporting_records = [record.item_id for record in records]
    formatted_prices = ", ".join(f"R$ {price:.2f}" for price in sorted_prices)
    explanation = f"Mediana dos preços coletados ({formatted_prices})."
    return ConsolidatedDecision(
        strategy="median",
        value=value,
        sample_count=len(sorted_prices),
        sources_used=sources_used,
        explanation=explanation,
        supporting_records=supporting_records,
    )


def get_record(item_id: str, domain: str = "dominio_piloto") -> CanonicalRecord | None:
    for record in _load_canonical_records(domain):
        if str(record.get("item_id")) == item_id:
            return CanonicalRecord.model_validate(record)
    return None


def resolve_evidence_packages(record: CanonicalRecord) -> List[EvidencePackage]:
    packages: List[EvidencePackage] = []
    for entry in record.supporting_sources:
        packages.append(
            EvidencePackage(
                source_id=entry.get("source_id"),
                item_id=entry.get("item_id"),
                manifest_path=entry.get("manifest_path"),
                evidence_path=entry.get("evidence_path"),
                collected_at=entry.get("collected_at"),
                hash_sha256=entry.get("hash_sha256"),
            )
        )
    return packages


def _set_nested(data: Dict[str, Any], dotted_path: str, value: Any) -> None:
    if "." not in dotted_path:
        data[dotted_path] = value
        return
    parts = dotted_path.split(".")
    cursor: Dict[str, Any] = data
    for part in parts[:-1]:
        if part not in cursor or not isinstance(cursor[part], dict):
            cursor[part] = {}
        cursor = cursor[part]
    cursor[parts[-1]] = value


def _load_yaml(path: Path) -> Dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ValueError(f"{path} deve conter um mapeamento YAML")
    return payload


def _write_yaml(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(jsonable_encoder(data), sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding="utf-8")


def _serialize_source(data: Mapping[str, Any], path: Path) -> SourceSchema:
    transport_url = ""
    transport = data.get("transport")
    if isinstance(transport, Mapping):
        transport_url = str(transport.get("url", ""))
    enabled = True
    if "enabled" in data:
        enabled = bool(data["enabled"])
    if "disabled" in data:
        enabled = not bool(data["disabled"])
    notes = data.get("notes") or []
    if isinstance(notes, str):
        notes = [notes]
    return SourceSchema(
        id=str(data.get("id")),
        name=str(data.get("name") or data.get("id")),
        type=str(data.get("type", "")),
        description=data.get("description"),
        path=str(path),
        transport_url=transport_url or None,
        enabled=enabled,
        notes=[str(note) for note in notes] if isinstance(notes, list) else [],
        raw=dict(data),
    )


def _source_file(source_id: str) -> Path:
    filename = f"{source_id}.yaml" if not source_id.endswith(".yaml") else source_id
    return SOURCES_DIR / filename


def _load_canonical_records(domain: str) -> List[Dict[str, Any]]:
    cfg = sprint6_config.load_domain_config(domain)
    if not cfg.canonical_records_path.exists():
        collector.collect_once(domain)
    return query_engine.load_canonical_records(domain)
