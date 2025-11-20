#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S12_G8"
SCORECARD_PATH="$SCORECARD_DIR/S12_G8_decision.json"
SUMMARY_PATH="$EVIDENCE_DIR/summary.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$ROOT_DIR" "$SCORECARD_PATH" "$SUMMARY_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
summary_path = Path(sys.argv[3])

scorecard_files = {
    "S12_G0": root / "out/scorecards/S12_G0_env_repo.json",
    "S12_G1": root / "out/scorecards/S12_G1_sources_scheduler.json",
    "S12_G2": root / "out/scorecards/S12_G2_ingest_pipeline.json",
    "S12_G3": root / "out/scorecards/S12_G3_debunker_coverage.json",
    "S12_G4": root / "out/scorecards/S12_G4_cases_timeline.json",
    "S12_G5": root / "out/scorecards/S12_G5_explorer_e2e.json",
    "S12_G6": root / "out/scorecards/S12_G6_feedback_flow.json",
    "S12_G7": root / "out/scorecards/S12_G7_observabilidade.json",
}

missing = [gate for gate, path in scorecard_files.items() if not path.exists()]
if missing:
    raise SystemExit(f"Scorecards ausentes: {missing}")

gate_statuses = {}
for gate, path in scorecard_files.items():
    gate_statuses[gate] = json.loads(path.read_text(encoding="utf-8"))

hard_required = ["S12_G0", "S12_G3", "S12_G4", "S12_G6"]
warn_allowed = {"S12_G1", "S12_G2", "S12_G5", "S12_G7"}

go_decision = True
reasons = []
for gate in hard_required:
    if gate_statuses[gate]["status"] != "PASS":
        go_decision = False
        reasons.append(f"{gate} = {gate_statuses[gate]['status']}")

for gate in warn_allowed:
    if gate_statuses[gate]["status"] == "FAIL":
        go_decision = False
        reasons.append(f"{gate} = FAIL (WARN não permitido)")

decision = "GO" if go_decision else "NO_GO"

scorecard = {
    "gate": "S12-G8",
    "status": "PASS",
    "decision": decision,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "gates": {gate: {"status": data["status"]} for gate, data in gate_statuses.items()},
    "reasons": reasons,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

summary_lines = [
    "# Sprint 12 – Decisão G8",
    f"- Decisão: **{decision}**",
    "- Status por gate:",
]
for gate in sorted(gate_statuses.keys()):
    summary_lines.append(f"  - {gate}: {gate_statuses[gate]['status']}")
if reasons:
    summary_lines.append("- Riscos / pendências:")
    summary_lines.extend([f"  - {reason}" for reason in reasons])
else:
    summary_lines.append("- Riscos / pendências: Nenhum bloqueador identificado.")
summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
PY

echo "S12-G8 concluído. Scorecard: $SCORECARD_PATH"
