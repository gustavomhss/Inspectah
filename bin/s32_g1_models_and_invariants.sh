#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

mkdir -p out/scorecards out/evidence/S32_G1_models_and_invariants

DB_PATH="${S32_TRUTH_DB_PATH:-out/databases/s32_truth.sqlite}"
EVIDENCE_LOG="out/evidence/S32_G1_models_and_invariants/run.log"

echo "[S32_G1] Applying migration to ${DB_PATH}" | tee "$EVIDENCE_LOG"

set +e
python3 migrations/versions/0034_s32_truthdb_blocks.py "$DB_PATH" >>"$EVIDENCE_LOG" 2>&1
migration_rc=$?
if [ $migration_rc -ne 0 ]; then
  echo "[S32_G1] Migration failed (rc=$migration_rc)" | tee -a "$EVIDENCE_LOG"
fi

echo "[S32_G1] Running invariants suite (python script)" | tee -a "$EVIDENCE_LOG"
python3 tests/truthdb/test_models_and_invariants.py >>"$EVIDENCE_LOG" 2>&1
tests_rc=$?
if [ $tests_rc -ne 0 ]; then
  echo "[S32_G1] Invariants suite failed (rc=$tests_rc)" | tee -a "$EVIDENCE_LOG"
fi
set -e

status="PASS"
[[ $migration_rc -ne 0 || $tests_rc -ne 0 ]] && status="FAIL"

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S32_G1_models_and_invariants",
    "status": "$status",
    "migration_rc": $migration_rc,
    "tests_rc": $tests_rc,
    "db_path": "$DB_PATH",
    "checked_invariants": [
        "no_orphan_fact_blocks",
        "no_orphan_evidence_blocks",
        "no_orphan_truth_states",
        "final_states_require_decision_block",
        "history_monotonic",
    ],
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S32_G1_models_and_invariants.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
