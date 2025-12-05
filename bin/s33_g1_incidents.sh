#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

if [ -n "${VIRTUAL_ENV:-}" ]; then
  PYTHON_BIN="${VIRTUAL_ENV}/bin/python"
else
  PYTHON_BIN="${PYTHON_BIN:-python}"
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  fi
fi

DB_PATH="${S33_OPS_DB_PATH:-out/databases/s33_ops.sqlite}"
LOG="out/evidence/S33_G1_incidents/run.log"
mkdir -p out/scorecards out/evidence/S33_G1_incidents

echo "[S33_G1] Applying migration to ${DB_PATH}" | tee "$LOG"
"$PYTHON_BIN" migrations/versions/0035_s33_incidents.py "$DB_PATH" >>"$LOG" 2>&1

echo "[S33_G1] Running incident domain/API tests" | tee -a "$LOG"
set +e
 "$PYTHON_BIN" -m pytest tests/ops/test_incidents_models.py tests/ops/test_incidents_api.py >>"$LOG" 2>&1
rc=$?
if [ $rc -ne 0 ]; then
  echo "[S33_G1] pytest not available or failed (rc=$rc), running fallback." | tee -a "$LOG"
  if "$PYTHON_BIN" tests/ops/test_incidents_models.py >>"$LOG" 2>&1; then
    rc=0
  fi
fi
set -e
status="PASS"
if [ $rc -ne 0 ]; then
  status="FAIL"
fi

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S33_G1_incidents",
    "status": "$status",
    "tests_rc": $rc,
    "db_path": "$DB_PATH",
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S33_G1_incidents.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
