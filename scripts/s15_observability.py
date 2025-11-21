"""Consultas de observabilidade para Debunker, comitês, âncoras e anti-canetada."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def _read_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def build_observability_report(evidence_dir: Path | None = None) -> Dict[str, object]:
    evidence_dir = evidence_dir or Path("out/evidence/S15_T6_observability")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    audit_log = _read_json(Path("out/evidence/S15_T1_contracts_and_states/override_log.json"))
    anchors_snapshot = _read_json(Path("out/evidence/S15_T1_contracts_and_states/anchors/registry_snapshot.json"))
    debunker_summary = _read_json(Path("out/evidence/S15_T2_debunker_offline/summary.json"))
    committee_summary = _read_json(Path("out/evidence/S15_T3_committees_flow/summary.json"))

    report = {
        "override_events": len(audit_log) if isinstance(audit_log, list) else len(audit_log.get("events", audit_log) if isinstance(audit_log, dict) else []),
        "anchors_registered": len(anchors_snapshot.get("anchors", {})) if isinstance(anchors_snapshot, dict) else 0,
        "claims_analyzed": debunker_summary.get("total_claims", 0),
        "committee_cases": committee_summary.get("total", 0),
    }

    queries = {
        "last_override": audit_log[-1] if isinstance(audit_log, list) and audit_log else None,
        "latest_anchor_ids": list(anchors_snapshot.get("anchors", {}).keys()) if isinstance(anchors_snapshot, dict) else [],
    }

    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "observability_report.json").write_text(
        json.dumps({"metrics": report, "queries": queries}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return {"metrics": report, "queries": queries}


__all__ = ["build_observability_report"]
