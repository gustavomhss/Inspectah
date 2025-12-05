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

LOG="out/evidence/S33_G2_cockpit/run.log"
mkdir -p out/scorecards out/evidence/S33_G2_cockpit

echo "[S33_G2] Running cockpit API tests" | tee "$LOG"
set +e
"$PYTHON_BIN" -m pytest tests/ops/test_cockpit_api.py >>"$LOG" 2>&1
rc=$?
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
    "gate": "S33_G2_cockpit",
    "status": "$status",
    "tests_rc": $rc,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S33_G2_cockpit.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
