"""Consolidated observability snapshot for Sprint 13."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
SCORECARD_DIR = BASE_DIR / "out" / "scorecards"
EVIDENCE_DIR = BASE_DIR / "out" / "evidence" / "S13_G7"
SNAPSHOT_PATH = EVIDENCE_DIR / "metrics_snapshot.json"
RISKS_PATH = EVIDENCE_DIR / "risks_and_debts.md"

SCORECARDS: Dict[str, str] = {
    "S13_G0": "S13_G0_env_repo.json",
    "S13_G1": "S13_G1_pilotos_multi_dominio.json",
    "S13_G2": "S13_G2_cases_timeline_multi.json",
    "S13_G3": "S13_G3_debunker_multi_dominio.json",
    "S13_G4": "S13_G4_explorer_multi_dominio.json",
    "S13_G5": "S13_G5_narrativas_multi_dominio.json",
    "S13_G6": "S13_G6_feedback_multi_dominio.json",
}

PRIMARY_SLO: Dict[str, Tuple[str, float, float]] = {
    "S13_G1": ("domain_pilot_coverage", 1.0, 0.95),
    "S13_G2": ("pilot_timeline_integrity_ratio", 0.95, 0.90),
    "S13_G3": ("debunker_explanation_coverage", 0.95, 0.90),
    "S13_G4": ("explorer_success_rate", 0.95, 0.90),
    "S13_G5": ("narrative_completeness_ratio", 1.0, 0.95),
    "S13_G6": ("feedback_delivery_ratio", 0.95, 0.90),
}


def _load_scorecard(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Scorecard não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_metrics_snapshot() -> Dict[str, object]:
    slis: Dict[str, Dict[str, object]] = {}
    warnings = []
    criticals = []

    for gate_id, filename in SCORECARDS.items():
        data = _load_scorecard(SCORECARD_DIR / filename)
        slis[gate_id] = {
            "status": data.get("status"),
            "metrics": data.get("metrics", {}),
        }
        if gate_id in PRIMARY_SLO:
            metric_name, slo, warn_threshold = PRIMARY_SLO[gate_id]
            metric_value = slis[gate_id]["metrics"].get(metric_name)
            if isinstance(metric_value, (int, float)):
                if metric_value < warn_threshold:
                    criticals.append(f"{gate_id} {metric_name}={metric_value} < {warn_threshold}")
                elif metric_value < slo:
                    warnings.append(f"{gate_id} {metric_name}={metric_value} < {slo}")

    if criticals:
        global_health = "CRITICAL"
    elif warnings:
        global_health = "WARN"
    else:
        global_health = "OK"

    notes = warnings + criticals
    snapshot = {
        "slis": slis,
        "global_health": global_health,
        "notes": notes,
    }
    return snapshot


def _write_evidence(snapshot: Dict[str, object]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# Sprint 13 Observabilidade",
        f"Global health: {snapshot['global_health']}",
        "",
        "## Principais SLIs",
    ]
    for gate_id, payload in snapshot["slis"].items():
        metrics = payload.get("metrics", {})
        metric_summary = ", ".join(f"{k}={v}" for k, v in metrics.items() if isinstance(v, (int, float)))
        lines.append(f"- {gate_id}: status={payload.get('status')} {metric_summary}")
    lines.append("")
    lines.append("## Riscos & débitos")
    if snapshot["notes"]:
        lines.extend(f"- {note}" for note in snapshot["notes"])
    else:
        lines.append("- Sem riscos adicionais além da dependência em fixtures locais para os pilotos atuais.")
    RISKS_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:  # pragma: no cover
    snapshot = build_metrics_snapshot()
    _write_evidence(snapshot)
    print(json.dumps({"global_health": snapshot["global_health"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
