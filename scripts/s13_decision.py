"""Apply Sprint 13 GO/NO-GO decision rules."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parents[1]
SCORECARD_DIR = BASE_DIR / "out" / "scorecards"
EVIDENCE_DIR = BASE_DIR / "out" / "evidence" / "S13_G8"
DECISION_PATH = SCORECARD_DIR / "S13_G8_decision.json"
SUMMARY_PATH = EVIDENCE_DIR / "summary.md"

GATE_FILES: Dict[str, str] = {
    "S13_G0": "S13_G0_env_repo.json",
    "S13_G1": "S13_G1_pilotos_multi_dominio.json",
    "S13_G2": "S13_G2_cases_timeline_multi.json",
    "S13_G3": "S13_G3_debunker_multi_dominio.json",
    "S13_G4": "S13_G4_explorer_multi_dominio.json",
    "S13_G5": "S13_G5_narrativas_multi_dominio.json",
    "S13_G6": "S13_G6_feedback_multi_dominio.json",
    "S13_G7": "S13_G7_observabilidade.json",
}


def _load_scorecard(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"Scorecard não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def compute_decision() -> Dict[str, object]:
    gates: Dict[str, Dict[str, object]] = {}
    reasons = []
    missing = []

    for gate_id, filename in GATE_FILES.items():
        scorecard_path = SCORECARD_DIR / filename
        if not scorecard_path.exists():
            missing.append(gate_id)
            gates[gate_id] = {"status": "MISSING"}
            continue
        data = _load_scorecard(scorecard_path)
        gates[gate_id] = {
            "status": data.get("status", "UNKNOWN"),
            "metrics": data.get("metrics"),
        }

    decision = "GO"
    status = "PASS"

    if missing:
        decision = "NO_GO"
        status = "FAIL"
        reasons.append(f"Scorecards ausentes: {', '.join(missing)}")

    for gate_id, payload in gates.items():
        gate_status = payload.get("status")
        if gate_status not in {"PASS", "WARN"}:
            decision = "NO_GO"
            status = "FAIL"
            reasons.append(f"{gate_id} com status {gate_status}")

    if decision == "GO" and not reasons:
        reasons = []

    return {
        "gate": "S13_G8",
        "status": status,
        "decision": decision,
        "gates": gates,
        "reasons": reasons,
    }


def _write_artifacts(payload: Dict[str, object]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.parent.mkdir(parents=True, exist_ok=True)
    DECISION_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Sprint 13 — Decisão G8",
        f"Decision: **{payload['decision']}**",
        f"Gate status: {payload['status']}",
        "",
        "## Gate summary",
    ]
    for gate_id, info in payload["gates"].items():
        lines.append(f"- {gate_id}: {info.get('status')}")
    lines.append("")
    lines.append("## Motivos / riscos")
    if payload["reasons"]:
        lines.extend(f"- {reason}" for reason in payload["reasons"])
    else:
        lines.append("- Todos os gates hard em PASS; sem riscos adicionais além da dependência em fixtures locais.")
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:  # pragma: no cover
    payload = compute_decision()
    _write_artifacts(payload)
    print(json.dumps({"decision": payload["decision"], "status": payload["status"]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
