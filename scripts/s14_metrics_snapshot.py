"""
Sprint 14 metrics snapshot (G6/G7 input).

Lê scorecards S14_G0…S14_G5 e consolida SLIs/SLOs em um snapshot único.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_G6 = ROOT_DIR / "out" / "evidence" / "S14_G6"
EVIDENCE_G7 = ROOT_DIR / "out" / "evidence" / "S14_G7"
METRICS_PATH = EVIDENCE_G6 / "metrics_snapshot.json"
RISKS_PATH = EVIDENCE_G6 / "risks_and_debts.md"

GATES = [
    "S14_G0_env_repo",
    "S14_G1_truth_kernel",
    "S14_G2_debunker_consistency",
    "S14_G3_explorer_contracts",
    "S14_G4_migrations_and_cleanup",
    "S14_G5_backlog_fase2",
]


def _load_scorecard(name: str) -> Dict[str, Any]:
    scorecard_path = ROOT_DIR / "out" / "scorecards" / f"{name}.json"
    if not scorecard_path.exists():
        return {"status": "MISSING", "path": str(scorecard_path)}
    try:
        return json.loads(scorecard_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "INVALID", "path": str(scorecard_path)}


def _health_from_status(status: str) -> float:
    if status == "PASS":
        return 1.0
    if status == "WARN":
        return 0.7
    return 0.0


def _compute_global(health_by_gate: Dict[str, float]) -> str:
    if any(value == 0.0 for value in health_by_gate.values()):
        return "CRITICAL"
    avg = sum(health_by_gate.values()) / len(health_by_gate) if health_by_gate else 0.0
    if avg >= 0.95:
        return "OK"
    if avg >= 0.9:
        return "WARN"
    return "CRITICAL"


def _render_risks(global_health: str, health_by_gate: Dict[str, float], statuses: Dict[str, str]) -> None:
    lines = ["# Sprint 14 – Riscos e Débitos", ""]
    lines.append(f"- Saúde global: {global_health}")
    for gate, status in statuses.items():
        if status in {"WARN", "FAIL", "MISSING", "INVALID"}:
            lines.append(f"- {gate}: {status}")
    if len(lines) == 2:
        lines.append("- Nenhum risco relevante detectado.")
    RISKS_PATH.write_text("\n".join(lines), encoding="utf-8")


def run() -> None:
    EVIDENCE_G6.mkdir(parents=True, exist_ok=True)
    EVIDENCE_G7.mkdir(parents=True, exist_ok=True)

    statuses: Dict[str, str] = {}
    health_by_gate: Dict[str, float] = {}

    for gate in GATES:
        card = _load_scorecard(gate)
        status = card.get("status", "MISSING")
        statuses[gate] = status
        health_by_gate[gate] = _health_from_status(status)

    global_health = _compute_global(health_by_gate)
    metrics = {
        "health_by_gate": health_by_gate,
        "status_by_gate": statuses,
        "global_health": global_health,
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    _render_risks(global_health, health_by_gate, statuses)

    # Copiar snapshot para G7 como referência principal
    (EVIDENCE_G7 / "metrics_snapshot.json").write_text(METRICS_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    (EVIDENCE_G7 / "risks_and_debts.md").write_text(RISKS_PATH.read_text(encoding="utf-8"), encoding="utf-8")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
