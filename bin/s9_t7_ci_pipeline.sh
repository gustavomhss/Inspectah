#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"

OUT_DIR="$ROOT/out/evidence/S9_T7_ci_pipeline"
SCORECARD="$ROOT/out/scorecards/S9_T7_ci_pipeline.json"
SUMMARY="$OUT_DIR/summary.json"
LOG_FILE="$OUT_DIR/ci.log"
START_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
START_TIME="$(date +%s)"

mkdir -p "$OUT_DIR" "$(dirname "$SCORECARD")"

CI_STATUS="PASS"
if ! bin/s9_ci.sh >"$LOG_FILE" 2>&1; then
  CI_STATUS="FAIL"
fi

END_TIME="$(date +%s)"
DURATION=$((END_TIME - START_TIME))

export ROOT SUMMARY SCORECARD LOG_FILE CI_STATUS DURATION START_TS

python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ.get("ROOT", Path.cwd()))
summary_path = Path(os.environ["SUMMARY"])
scorecard_path = Path(os.environ["SCORECARD"])
log_file = Path(os.environ["LOG_FILE"])
ci_status = os.environ["CI_STATUS"]
duration = int(os.environ.get("DURATION", "0"))
timestamp = os.environ["START_TS"]

gates = {
    "S9_T1_static_quality": root / "out" / "scorecards" / "S9_T1_static_quality.json",
    "S9_T2_unit_and_contracts": root / "out" / "scorecards" / "S9_T2_unit_and_contracts.json",
    "S9_T3_property_and_edge_cases": root / "out" / "scorecards" / "S9_T3_property_and_edge_cases.json",
    "S9_T4_golden_flows": root / "out" / "scorecards" / "S9_T4_golden_flows.json",
    "S9_T5_perf_and_limits": root / "out" / "scorecards" / "S9_T5_perf_and_limits.json",
    "S9_T6_logs_and_evidence": root / "out" / "scorecards" / "S9_T6_logs_and_evidence.json",
}

gate_status = {}
all_pass = ci_status == "PASS"
missing = []
for name, path in gates.items():
    if not path.exists():
        gate_status[name] = "MISSING"
        all_pass = False
        missing.append(str(path))
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    status = data.get("status") or data.get("Status")
    if status is None:
        status = "UNKNOWN"
    gate_status[name] = status
    if status != "PASS":
        all_pass = False

final_status = "PASS" if all_pass else "FAIL"

summary = {
    "gate": "S9_T7_ci_pipeline",
    "timestamp": timestamp,
    "duration_seconds": duration,
    "ci_status": ci_status,
    "gates_checked": gate_status,
    "missing_scorecards": missing,
    "log_file": str(log_file.relative_to(root)),
    "status": final_status,
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate": "S9_T7_ci_pipeline",
    "status": final_status,
    "gates": gate_status,
    "summary_path": str(summary_path.relative_to(root)),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY

if [[ "$CI_STATUS" != "PASS" ]]; then
  cat "$LOG_FILE"
  exit 1
fi

PIPELINE_STATUS="$(python3 - <<'PY'
import json, os
from pathlib import Path
scorecard = json.loads(Path(os.environ["SCORECARD"]).read_text(encoding="utf-8"))
print(scorecard["status"])
PY
)"
if [[ "$PIPELINE_STATUS" != "PASS" ]]; then
  exit 1
fi
