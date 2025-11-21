"""Debunker coverage checks for Sprint 13 pilots."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from scripts.s12_debunker_runner import evaluate_event
from scripts.s13_pilots_registry import list_pilots
from scripts.s13_timeline_checks import collect_pilot_timelines

DEFAULT_EVIDENCE_DIR = Path("out/evidence/S13_G3")


def _normalize_event(pilot_id: str, domain: str, case_key: str, event: Dict[str, object]) -> Dict[str, object]:
    return {
        "id_evento": event.get("id_evento"),
        "case_id": case_key,
        "case_key": case_key,
        "dominio": domain,
        "titulo": event.get("titulo"),
        "resumo": event.get("resumo"),
        "tipo_evento": event.get("tipo_evento"),
        "event_timestamp": event.get("timestamp"),
        "source_id": event.get("fonte"),
        "metadata": {
            "pilot_id": pilot_id,
            "status_debunker_original": event.get("status_debunker"),
        },
        "payload": {
            "rationale_original": event.get("rationale", ""),
        },
    }


def run_debunker_checks(evidence_dir: Optional[Path] = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or DEFAULT_EVIDENCE_DIR
    evidence_dir.mkdir(parents=True, exist_ok=True)
    decisions_path = evidence_dir / "debunker_decisions.json"
    decisions_by_domain_dir = evidence_dir / "decisions_by_domain"
    decisions_by_domain_dir.mkdir(parents=True, exist_ok=True)

    pilot_timelines = collect_pilot_timelines()
    pilots_meta = {pilot["id"]: pilot for pilot in list_pilots()}

    decisions: List[Dict[str, object]] = []
    coverage_total = 0
    events_total = 0
    per_domain: Dict[str, Dict[str, float]] = {}
    domain_decisions: Dict[str, List[Dict[str, object]]] = {}

    for pilot_id, timeline in pilot_timelines.items():
        pilot_info = pilots_meta.get(pilot_id, {"dominio": timeline.domain})
        domain = pilot_info.get("dominio", timeline.domain)
        domain_stats = per_domain.setdefault(domain, {"events": 0, "with_rationale": 0})
        bucket = domain_decisions.setdefault(domain, [])
        for event in timeline.events:
            normalized = _normalize_event(pilot_id, domain, timeline.case_key, event)
            decision = evaluate_event(normalized, case_context={"source": timeline.source, "pilot_id": pilot_id})
            has_rationale = bool(decision.get("rationale"))
            decisions.append(decision)
            bucket.append(decision)
            events_total += 1
            coverage_total += 1 if has_rationale else 0
            domain_stats["events"] += 1
            domain_stats["with_rationale"] += 1 if has_rationale else 0

    coverage = 1.0 if events_total == 0 else coverage_total / events_total
    per_domain_metrics = {
        domain: {
            "coverage": (stats["with_rationale"] / stats["events"]) if stats["events"] else 1.0,
            "events": stats["events"],
        }
        for domain, stats in per_domain.items()
    }

    decisions_path.write_text(json.dumps(decisions, indent=2, ensure_ascii=False), encoding="utf-8")
    for domain, entries in domain_decisions.items():
        (decisions_by_domain_dir / f"{domain}.json").write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return {
        "metrics": {
            "debunker_explanation_coverage": round(coverage, 3),
            "events_total": events_total,
            "decisions_per_domain": per_domain_metrics,
        },
        "decisions_path": str(decisions_path),
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


__all__ = ["run_debunker_checks"]
