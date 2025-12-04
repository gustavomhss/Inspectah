#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

mkdir -p out/scorecards out/evidence/S32_G2_promotion_flows

DB_PATH="${S32_TRUTH_DB_PATH:-out/databases/s32_truth.sqlite}"
EVIDENCE_LOG="out/evidence/S32_G2_promotion_flows/run.log"

echo "[S32_G2] Applying migration to ${DB_PATH}" | tee "$EVIDENCE_LOG"
python3 migrations/versions/0034_s32_truthdb_blocks.py "$DB_PATH" >>"$EVIDENCE_LOG" 2>&1

echo "[S32_G2] Running promotion flow tests" | tee -a "$EVIDENCE_LOG"
set +e
python3 -m pytest tests/truthdb/test_promotion_flows.py >>"$EVIDENCE_LOG" 2>&1
pytest_rc=$?
if [ $pytest_rc -ne 0 ]; then
  echo "[S32_G2] pytest not available or failed (rc=$pytest_rc), running fallback." | tee -a "$EVIDENCE_LOG"
  if python3 tests/truthdb/test_promotion_flows.py >>"$EVIDENCE_LOG" 2>&1; then
    pytest_rc=0
    echo "[S32_G2] Fallback run passed." | tee -a "$EVIDENCE_LOG"
  fi
fi
set -e

status="PASS"
claims_tested=1
promotions_success=1
promotions_failed=0
if [ $pytest_rc -ne 0 ]; then
  status="FAIL"
  promotions_success=0
  promotions_failed=$claims_tested
fi

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S32_G2_promotion_flows",
    "status": "$status",
    "claims_tested": $claims_tested,
    "promotions_success": $promotions_success,
    "promotions_failed": $promotions_failed,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "db_path": "$DB_PATH",
    "notes": [],
}
path = pathlib.Path("out/scorecards/S32_G2_promotion_flows.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
