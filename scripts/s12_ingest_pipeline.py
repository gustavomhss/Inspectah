"""Sprint 12 ingestion pipeline implementation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from scripts.s12_case_service import CaseService
from scripts.s12_debunker_runner import evaluate_event
from scripts.s12_normalizers import evento_climatico, obra_publica
from scripts.s12_sources_registry import DEFAULT_REGISTRY, SourceConfig
from scripts.s12_timeline_service import TimelineService
from scripts.s12_truthdb_adapter import export_state, register_event_for_case, reset_state as reset_truthdb

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_EVENTS_DIR = ROOT_DIR / "out" / "evidence" / "S12_G1" / "raw_events"
EVIDENCE_DIR = ROOT_DIR / "out" / "evidence" / "S12_G2"


def load_raw_events(raw_dir: Path = RAW_EVENTS_DIR) -> List[Dict[str, object]]:
    events: List[Dict[str, object]] = []
    if not raw_dir.exists():
        return events
    for path in sorted(raw_dir.glob("raw_events_*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        events.extend(payload)
    return events


def load_normalized_events(evidence_dir: Path = EVIDENCE_DIR) -> List[Dict[str, object]]:
    normalized_path = evidence_dir / "normalized_events.json"
    if not normalized_path.exists():
        return []
    return json.loads(normalized_path.read_text(encoding="utf-8"))


def _normalize_event(raw_event: Dict[str, object]) -> Dict[str, object]:
    source_id = raw_event.get("source_id")
    if not source_id:
        raise ValueError("Evento bruto sem source_id não pode ser normalizado")
    source: SourceConfig = DEFAULT_REGISTRY.get(source_id)
    if source.dominio == "obra_publica":
        normalized = obra_publica.normalize_raw_event(raw_event, source)
    elif source.dominio == "evento_climatico":
        normalized = evento_climatico.normalize_alert_event(raw_event, source)
    else:
        raise ValueError(f"Domínio desconhecido para normalização: {source.dominio}")
    normalized.setdefault("case_key", f"{source.dominio}:{source.id_fonte}")
    normalized.setdefault("eligible", True)
    normalized.setdefault("captured_at", raw_event.get("fetched_at"))
    normalized.setdefault("dominio", source.dominio)
    normalized.setdefault("source_id", source.id_fonte)
    return normalized


def run_ingest_pipeline(
    *,
    mode: str = "test",
    raw_dir: Path = RAW_EVENTS_DIR,
    evidence_dir: Path = EVIDENCE_DIR,
) -> Dict[str, object]:
    """Execute the Sprint 12 ingestion pipeline."""

    evidence_dir.mkdir(parents=True, exist_ok=True)
    raw_events = load_raw_events(raw_dir)
    case_service = CaseService()
    timeline_service = TimelineService()
    reset_truthdb()

    normalized_events: List[Dict[str, object]] = []
    processed_ids: set[str] = set()
    eligible_total = 0
    eligible_with_decision = 0

    for raw_event in raw_events:
        normalized = _normalize_event(raw_event)
        event_id = normalized.get("id_evento")
        if not event_id or event_id in processed_ids:
            continue
        processed_ids.add(event_id)
        case = case_service.get_or_create_case(normalized)
        normalized["case_id"] = case.id_caso
        decision = evaluate_event(normalized, case_context=case.to_dict())
        if normalized.get("eligible", True):
            eligible_total += 1
            if decision.get("decision"):
                eligible_with_decision += 1
        normalized["debunker_decision"] = decision.get("decision")
        register_event_for_case(case.id_caso, normalized, decision)
        timeline_service.append_event(case.id_caso, normalized, decision)
        case_service.update_status_from_decision(case.id_caso, decision.get("decision", "incerto"))
        normalized_events.append(normalized)

    case_snapshot_path = evidence_dir / "cases_snapshot.json"
    timeline_snapshot_path = evidence_dir / "timelines_snapshot.json"
    normalized_path = evidence_dir / "normalized_events.json"
    truthdb_path = evidence_dir / "truthdb_snapshot.json"
    report_path = evidence_dir / "pipeline_report.json"

    normalized_path.write_text(_json_dumps(normalized_events), encoding="utf-8")
    case_service.export_snapshot(case_snapshot_path)
    timeline_service.export_snapshot(timeline_snapshot_path)
    export_state(truthdb_path)

    case_integrity = case_service.integrity_ratio(normalized_events)
    timeline_integrity, timeline_violations = timeline_service.integrity_ratio()
    debunker_coverage = 1.0 if eligible_total == 0 else eligible_with_decision / eligible_total

    summary = {
        "mode": mode,
        "raw_events": len(raw_events),
        "normalized_events": len(normalized_events),
        "cases": len(case_service.list_cases()),
        "case_integrity_ratio": round(case_integrity, 3),
        "timeline_integrity_ratio": round(timeline_integrity, 3),
        "timeline_violations": timeline_violations,
        "debunker_coverage": round(debunker_coverage, 3),
    }

    report_path.write_text(_json_dumps(summary), encoding="utf-8")
    return summary


def _json_dumps(payload: object) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)


if __name__ == "__main__":  # pragma: no cover - manual run helper
    print(_json_dumps(run_ingest_pipeline()))
