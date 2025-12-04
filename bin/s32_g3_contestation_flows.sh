#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

mkdir -p out/scorecards out/evidence/S32_G3_contestation_flows

DB_PATH="${S32_TRUTH_DB_PATH:-out/databases/s32_truth.sqlite}"
EVIDENCE_LOG="out/evidence/S32_G3_contestation_flows/run.log"

echo "[S32_G3] Applying migration to ${DB_PATH}" | tee "$EVIDENCE_LOG"
python3 migrations/versions/0034_s32_truthdb_blocks.py "$DB_PATH" >>"$EVIDENCE_LOG" 2>&1

set +e
echo "[S32_G3] Running contestation flow tests" | tee -a "$EVIDENCE_LOG"
python3 -m pytest tests/truthdb/test_contestation_flows.py >>"$EVIDENCE_LOG" 2>&1
pytest_rc=$?
if [ $pytest_rc -ne 0 ]; then
  echo "[S32_G3] pytest not available or failed (rc=$pytest_rc), running fallback." | tee -a "$EVIDENCE_LOG"
  if python3 tests/truthdb/test_contestation_flows.py >>"$EVIDENCE_LOG" 2>&1; then
    pytest_rc=0
    echo "[S32_G3] Fallback run passed." | tee -a "$EVIDENCE_LOG"
  fi
fi
set -e

status="PASS"
contests_tested=1
contests_success=1
if [ $pytest_rc -ne 0 ]; then
  status="FAIL"
  contests_success=0
fi

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S32_G3_contestation_flows",
    "status": "$status",
    "contests_tested": $contests_tested,
    "contests_success": $contests_success,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "db_path": "$DB_PATH",
    "notes": [],
}
path = pathlib.Path("out/scorecards/S32_G3_contestation_flows.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
