#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T7_ci_and_repro"
SCORECARD_PATH="$SCORECARD_DIR/S15_T7_ci_and_repro.json"
WORKFLOW="$ROOT_DIR/.ci/sprint_15_gates.yml"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$WORKFLOW" "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

workflow = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])

scripts = [
    "bin/s15_t0_sanity.sh",
    "bin/s15_t1_contracts_and_states.sh",
    "bin/s15_t2_debunker_offline.sh",
    "bin/s15_t3_committees_flow.sh",
    "bin/s15_t4_golden_scenarios.sh",
    "bin/s15_t5_performance_and_cost.sh",
    "bin/s15_t6_observability.sh",
    "bin/s15_all_gates.sh",
]
missing_scripts = [script for script in scripts if not Path(script).exists()]
workflow_exists = workflow.exists()
scorecards_present = [path for path in Path("out/scorecards").glob("S15_*.json")]
status = "PASS"
notes = []
if missing_scripts:
    status = "FAIL"
    notes.append(f"Scripts faltando: {', '.join(missing_scripts)}")
if not workflow_exists:
    status = "FAIL"
    notes.append("Workflow sprint_15_gates.yml ausente")
if len(scorecards_present) < 5:
    notes.append("Scorecards S15 ainda não gerados; rode s15_all_gates.sh")

report = {
    "gate": "S15_T7",
    "status": status,
    "notes": notes,
    "workflow_present": workflow_exists,
    "scorecards_contados": len(scorecards_present),
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
(evidence_dir / "ci_check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
scorecard_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T7] Falhou; verifique notas no scorecard.")
PY

echo "[S15_T7] OK. Scorecard em $SCORECARD_PATH"
