#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S35_G1_model_rollout"
SCORECARD_PATH="out/scorecards/S35_G1_model.json"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

echo "[S35_G1] Rodando migração 0036 + pytest (rollout/limits/catalog) com ${PYTHON_BIN}" | tee "$LOG"

"$PYTHON_BIN" - <<'PY' 2>&1 | tee -a "$LOG"
import importlib

mig = importlib.import_module("migrations.versions.0036_s35_flow_governance_advanced")
mig.apply_migration()
info = mig.verify_schema()
print(f"[S35_G1] migration applied at {mig.DEFAULT_DB_PATH} cols={ {k: len(v) for k,v in info.items()} }")
PY

set +e
PYTEST_TARGETS=(
  tests/flows/test_flow_models_and_policies.py
  tests/flows/test_flow_limits.py
  tests/flows/test_flow_rollout_models.py
)

"$PYTHON_BIN" -m pytest "${PYTEST_TARGETS[@]}" 2>&1 | tee -a "$LOG"
STATUS=$?
set -e

if [ "$STATUS" -eq 0 ]; then
  RESULT="PASS"
else
  RESULT="FAIL"
fi

cat > "$SCORECARD_PATH" <<JSON
{
  "gate": "S35_G1_model",
  "status": "$RESULT",
  "tests_ran": ${#PYTEST_TARGETS[@]},
  "targets": ["tests/flows/test_flow_models_and_policies.py", "tests/flows/test_flow_limits.py", "tests/flows/test_flow_rollout_models.py"]
}
JSON

echo "[S35_G1] Resultado: $RESULT (scorecard em $SCORECARD_PATH)" | tee -a "$LOG"
exit "$STATUS"
