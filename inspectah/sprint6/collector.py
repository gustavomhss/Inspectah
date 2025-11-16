from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .config import DomainConfig, FieldDefinition, SourceConfig, load_domain_config
from .parsers import load_records


def collect_once(domain: str = "dominio_piloto") -> Dict[str, Any]:
    cfg = load_domain_config(domain)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    cfg.evidence_root.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    canonical_index: Dict[str, Dict[str, Any]] = {}
    sources_summary: Dict[str, Any] = {}
    new_packages = 0
    total_raw = 0

    for source_id, source_cfg in cfg.sources.items():
        raw_records = load_records(source_cfg)
        total_raw += len(raw_records)
        stats = {
            "raw_records": len(raw_records),
            "canonical_records": 0,
            "errors": [],
            "evidence_packages": 0,
        }
        for record in raw_records:
            canonical, errors = _canonicalize(cfg, source_cfg, record)
            if errors:
                stats["errors"].append({"record": record, "errors": errors})
                continue
            dedup_key = _dedup_key(canonical, cfg.dedup_fields)
            evidence_info, created = _write_evidence(cfg, source_id, canonical, record, dedup_key)
            if created:
                stats["evidence_packages"] += 1
                new_packages += 1
            entry = canonical_index.setdefault(
                dedup_key,
                {
                    "record": canonical,
                    "supporting_sources": [],
                },
            )
            if _should_replace(entry["record"], canonical):
                entry["record"] = canonical
            entry["supporting_sources"].append(evidence_info)
            stats["canonical_records"] += 1
        sources_summary[source_id] = stats

    canonical_records = []
    for entry in canonical_index.values():
        record = dict(entry["record"])
        record["supporting_sources"] = entry["supporting_sources"]
        record["sources_count"] = len(entry["supporting_sources"])
        canonical_records.append(record)
    canonical_records.sort(key=lambda item: item.get("reported_at") or "", reverse=True)

    cfg.canonical_records_path.write_text(json.dumps(canonical_records, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = {
        "domain": cfg.domain,
        "started_at": started_at,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "sources_total": len(cfg.sources),
        "raw_records_total": total_raw,
        "canonical_records_total": len(canonical_records),
        "new_evidence_packages": new_packages,
        "sources": sources_summary,
    }
    cfg.summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"summary": summary, "canonical_records": canonical_records}


def _canonicalize(domain: DomainConfig, source: SourceConfig, record: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    canonical: Dict[str, Any] = {}
    errors: List[str] = []
    for field in domain.fields:
        path = field.sources.get(source.id)
        if not path:
            continue
        raw_value = _extract_path(record, path)
        value = _coerce_value(raw_value, field)
        if value is None and field.required:
            errors.append(f"{field.name}: missing (path {path})")
            continue
        if value is not None:
            canonical[field.name] = value
    missing_required = [field.name for field in domain.fields if field.required and field.name not in canonical]
    if missing_required:
        errors.append(f"missing required fields: {', '.join(missing_required)}")
    return canonical, errors


def _extract_path(data: Any, path: str) -> Any:
    current = data
    for part in path.split('.'):
        name, index = _split_index(part)
        if isinstance(current, dict):
            current = current.get(name)
        else:
            return None
        if index is not None:
            if isinstance(current, list) and 0 <= index < len(current):
                current = current[index]
            else:
                return None
    return current


def _split_index(part: str) -> Tuple[str, int | None]:
    if '[' in part and part.endswith(']'):
        name, idx = part[:-1].split('[', 1)
        try:
            return name, int(idx)
        except ValueError:
            return part, None
    return part, None


def _coerce_value(value: Any, field: FieldDefinition) -> Any:
    if value is None:
        return None
    target = field.type.lower()
    if target in {"string", "text"}:
        text = str(value).strip()
        return text or None
    if target in {"number", "float"}:
        try:
            return float(str(value).replace(',', '.'))
        except (TypeError, ValueError):
            return None
    if target in {"integer", "int"}:
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return None
    if target in {"datetime", "timestamp"}:
        text = str(value).strip()
        if not text:
            return None
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).isoformat()
        except ValueError:
            return text
    return value


def _dedup_key(record: Dict[str, Any], fields: List[str]) -> str:
    parts = []
    for field in fields:
        value = record.get(field)
        if isinstance(value, str):
            parts.append(value.strip().lower())
        else:
            parts.append(str(value).lower() if value is not None else "")
    return "|".join(parts)


def _write_evidence(
    cfg: DomainConfig,
    source_id: str,
    canonical: Dict[str, Any],
    raw_record: Dict[str, Any],
    dedup_key: str,
) -> Tuple[Dict[str, Any], bool]:
    reported_at = canonical.get("reported_at")
    timestamp = _parse_datetime(reported_at) or datetime.now(timezone.utc)
    day_path = timestamp.strftime("%Y/%m/%d")
    item_id = canonical.get("item_id") or hashlib.sha256(dedup_key.encode()).hexdigest()[:12]
    package_dir = cfg.evidence_root / source_id / day_path / _slugify(str(item_id))
    package_dir.mkdir(parents=True, exist_ok=True)

    raw_payload = {
        "source_id": source_id,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "record": raw_record,
    }
    raw_text = json.dumps(raw_payload, indent=2, ensure_ascii=False)
    raw_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    manifest_path = package_dir / "manifest.json"
    existing = _load_manifest(manifest_path)
    if existing and existing.get("hash_sha256") == raw_hash:
        return {
            "source_id": source_id,
            "item_id": canonical.get("item_id"),
            "manifest_path": str(manifest_path),
            "hash_sha256": raw_hash,
            "evidence_path": str(package_dir),
            "collected_at": existing.get("collected_at"),
        }, False

    (package_dir / "raw.json").write_text(raw_text, encoding="utf-8")
    (package_dir / "hash.txt").write_text(raw_hash + "\n", encoding="utf-8")
    (package_dir / "text.txt").write_text(_format_text_summary(canonical, source_id), encoding="utf-8")

    manifest = {
        "domain": cfg.domain,
        "source_id": source_id,
        "item_id": canonical.get("item_id"),
        "dedup_key": dedup_key,
        "reported_at": reported_at,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "hash_sha256": raw_hash,
        "canonical_fields": canonical,
        "files": {"raw": "raw.json", "text": "text.txt"},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "source_id": source_id,
        "item_id": canonical.get("item_id"),
        "manifest_path": str(manifest_path),
        "hash_sha256": raw_hash,
        "evidence_path": str(package_dir),
        "collected_at": manifest["collected_at"],
    }, True


def _format_text_summary(canonical: Dict[str, Any], source_id: str) -> str:
    price = canonical.get("price_brl")
    price_text = f"R$ {price:.2f}" if isinstance(price, (int, float)) else str(price)
    lines = [
        f"Fonte: {source_id}",
        f"Produto: {canonical.get('product_name', '')}",
        f"Categoria: {canonical.get('category', '')}",
        f"Região: {canonical.get('region', '')}",
        f"Unidade: {canonical.get('unit', '')}",
        f"Preço: {price_text}",
        f"Observado em: {canonical.get('reported_at', '')}",
        f"URL: {canonical.get('source_url', '')}",
        "",
        f"Notas: {canonical.get('notes', '')}",
    ]
    return "\n".join(lines)


def _load_manifest(path: Path) -> Dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _slugify(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", value)
    return safe or "item"


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _should_replace(current: Dict[str, Any], candidate: Dict[str, Any]) -> bool:
    cur_ts = _parse_datetime(current.get("reported_at"))
    new_ts = _parse_datetime(candidate.get("reported_at"))
    if cur_ts is None:
        return True
    if new_ts is None:
        return False
    return new_ts >= cur_ts
