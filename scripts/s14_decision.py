"""
Sprint 14 GO/NO_GO decision (G8).

Lê scorecards S14_G0…S14_G7 e aplica as regras de decisão:
- FAIL ou MISSING em qualquer gate crítico => NO_GO.
- WARN é aceito, mas registrado.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT_DIR = Path(__file__).resolve().parent.parent
SCORECARD_DIR = ROOT_DIR / "out" / "scorecards"
EVIDENCE_DIR = ROOT_DIR / "out" / "evidence" / "S14_G8"
DECISION_PATH = SCORECARD_DIR / "S14_G8_decision.json"
SUMMARY_PATH = EVIDENCE_DIR / "summary.md"

GATES = [
    "S14_G0_env_repo",
    "S14_G1_truth_kernel",
    "S14_G2_debunker_consistency",
    "S14_G3_explorer_contracts",
    "S14_G4_migrations_and_cleanup",
    "S14_G5_backlog_fase2",
    "S14_G6_metrics_snapshot",
    "S14_G7_observabilidade",
]

CRITICAL_GATES = set(GATES)  # todos são críticos aqui


def _load_scorecard(name: str) -> Dict[str, Any]:
    path = SCORECARD_DIR / f"{name}.json"
    if not path.exists():
        return {"status": "MISSING", "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"status": "INVALID", "path": str(path)}


def _decide(status_map: Dict[str, str]) -> str:
    for gate, status in status_map.items():
        if gate in CRITICAL_GATES and status not in {"PASS", "WARN"}:
            return "NO_GO"
    return "GO"


def _render_summary(decision: str, status_map: Dict[str, str]) -> None:
    lines = ["# Sprint 14 – Decisão", ""]
    lines.append(f"- Decisão: **{decision}**")
    lines.append("- Estados por gate:")
    for gate, status in status_map.items():
        lines.append(f"  - {gate}: {status}")
    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def run() -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    status_map: Dict[str, str] = {}
    for gate in GATES:
        card = _load_scorecard(gate)
        status_map[gate] = card.get("status", "MISSING")

    decision = _decide(status_map)
    status_gate = "PASS" if decision == "GO" else "FAIL"

    _render_summary(decision, status_map)

    payload = {
        "gate": "S14_G8",
        "status": status_gate,
        "decision": decision,
        "gates": status_map,
    }
    DECISION_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if status_gate == "FAIL":
        raise SystemExit("S14_G8 = NO_GO; consulte summary.md e scorecard.")


def main() -> None:
    run()


if __name__ == "__main__":
    main()
