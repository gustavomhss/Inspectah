from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from .collector import collect_once
from .config import load_domain_config
from .query_engine import load_canonical_records


def snapshot_metrics(domain: str = "dominio_piloto") -> Dict[str, Any]:
    cfg = load_domain_config(domain)
    if not cfg.canonical_records_path.exists():
        collect_once(domain)
    records = load_canonical_records(domain)
    summary = json.loads(cfg.summary_path.read_text(encoding="utf-8")) if cfg.summary_path.exists() else {}
    metrics = {
        "domain": domain,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records_total": len(records),
        "sources_total": len(cfg.sources),
        "raw_records_total": summary.get("raw_records_total", 0),
        "categories": _count(records, "category"),
        "regions": _count(records, "region"),
        "latency_minutes_p50": _percentile(_latencies(records), 0.5),
        "latency_minutes_p95": _percentile(_latencies(records), 0.95),
    }
    snapshot_path = cfg.out_dir / f"metrics_snapshot_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.json"
    snapshot_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"metrics": metrics, "path": snapshot_path}


def _count(records: List[Dict[str, Any]], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for record in records:
        value = (record.get(field) or "").lower()
        if value:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _latencies(records: List[Dict[str, Any]]) -> List[float]:
    values: List[float] = []
    for record in records:
        reported = _parse_datetime(record.get("reported_at"))
        for entry in record.get("supporting_sources", []):
            collected = _parse_datetime(entry.get("collected_at"))
            if reported and collected and collected >= reported:
                values.append((collected - reported).total_seconds() / 60.0)
    return values


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _percentile(values: List[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    k = (len(ordered) - 1) * percentile
    f = int(k)
    c = min(len(ordered) - 1, f + 1)
    if f == c:
        return ordered[f]
    return ordered[f] * (c - k) + ordered[c] * (k - f)
