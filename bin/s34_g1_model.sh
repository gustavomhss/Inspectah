#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

DB_PATH="${S34_FLOWS_DB_PATH:-out/databases/s34_flows.sqlite}"
EVIDENCE_DIR="out/evidence/S34_G1_model_and_policies_multifluxo"
LOG="$EVIDENCE_DIR/run.log"
SCORECARD="out/scorecards/S34_G1_model.json"

mkdir -p "$EVIDENCE_DIR" out/scorecards

echo "[S34_G1] Applying migration to ${DB_PATH}" | tee "$LOG"

set +e
python3 - <<'PY' 2>&1 | tee -a "$LOG"
import importlib
from pathlib import Path

mig = importlib.import_module("migrations.versions.0034_s34_flow_multidomain_ops")
mig.apply_migration(Path("$DB_PATH"))
info = mig.verify_schema(Path("$DB_PATH"))
print({"status": "applied", "flow_cols": info["flow_flows"]})
PY
migration_rc=$?

echo "[S34_G1] Running pytest for invariants/policies/limits" | tee -a "$LOG"
pytest -q tests/flows/test_flow_models_and_policies.py tests/flows/test_flow_limits.py 2>&1 | tee -a "$LOG"
pytest_rc=${PIPESTATUS[0]}
set -e

status="PASS"
[[ $migration_rc -ne 0 || $pytest_rc -ne 0 ]] && status="FAIL"

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S34_G1_model",
    "status": "$status",
    "migration_rc": $migration_rc,
    "pytest_rc": $pytest_rc,
    "db_path": "$DB_PATH",
    "checked": [
        "migration_0034_applied",
        "flow_version_id_required",
        "limits_percentual_teste",
        "rollback_limits",
        "domain_policies_present",
    ],
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
pathlib.Path("$SCORECARD").write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
