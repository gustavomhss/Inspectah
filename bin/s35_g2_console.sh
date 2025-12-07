#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S35_G2_console_rollout"
SCORECARD_PATH="out/scorecards/S35_G2_console.json"
LOG="$EVIDENCE_DIR/run.log"
OUT_LOG="out/logs/SF1_bin_s35_g2_console.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards out/logs

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

echo "[S35_G2] Rodando testes de console/API rollout com ${PYTHON_BIN}" | tee "$LOG" "$OUT_LOG"

PYTEST_TARGETS=(
  tests/flows/test_console_rollout_api.py
  tests/flows/test_flow_rollout_models.py
)
if "$PYTHON_BIN" -m pytest "${PYTEST_TARGETS[@]}" 2>&1 | tee -a "$LOG" "$OUT_LOG"; then
  STATUS=0
else
  STATUS=${PIPESTATUS[0]:-1}
fi

RESULT="FAIL"
if [ "$STATUS" -eq 0 ]; then
  RESULT="PASS"
fi

cat > "$SCORECARD_PATH" <<JSON
{
  "gate": "S35_G2_console",
  "status": "$RESULT",
  "tests_ran": ${#PYTEST_TARGETS[@]},
  "targets": ["tests/flows/test_console_rollout_api.py", "tests/flows/test_flow_rollout_models.py"]
}
JSON

echo "[S35_G2] Resultado: $RESULT (scorecard em $SCORECARD_PATH)" | tee -a "$LOG" "$OUT_LOG"
exit "$STATUS"
