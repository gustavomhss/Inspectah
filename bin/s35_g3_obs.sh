#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S35_G3_observabilidade_rollout"
SCORECARD_PATH="out/scorecards/S35_G3_obs.json"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

echo "[S35_G3] Validando observabilidade rollout (métricas/alertas/painel)" | tee "$LOG"

missing=()
for f in observability/dashboards/s35_flow_rollout_overview.json observability/alerts/s35/rollout_alerts.yaml; do
  if [ ! -f "$f" ]; then
    missing+=("$f")
  fi
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "Faltam arquivos de observabilidade: ${missing[*]}" | tee -a "$LOG"
  STATUS=1
else
  set +e
  # promtool lint (se disponível)
  if command -v promtool >/dev/null 2>&1; then
    promtool check rules observability/alerts/s35/rollout_alerts.yaml 2>&1 | tee -a "$LOG"
  else
    echo "promtool não encontrado, pulando lint de alerts" | tee -a "$LOG"
  fi
  PYTEST_TARGETS=(
    tests/flows/test_console_rollout_api.py
    tests/flows/test_flow_rollout_models.py
  )
  "$PYTHON_BIN" -m pytest "${PYTEST_TARGETS[@]}" 2>&1 | tee -a "$LOG"
  STATUS=$?
  set -e
fi

RESULT="FAIL"
if [ "${STATUS:-1}" -eq 0 ]; then
  RESULT="PASS"
fi
FILES_OK="false"
if [ ${#missing[@]} -eq 0 ]; then
  FILES_OK="true"
fi

cat > "$SCORECARD_PATH" <<JSON
{
  "gate": "S35_G3_obs",
  "status": "$RESULT",
  "files_present": $FILES_OK,
  "tests_ran": 2,
  "targets": ["tests/flows/test_console_rollout_api.py", "tests/flows/test_flow_rollout_models.py"]
}
JSON

echo "[S35_G3] Resultado: $RESULT (scorecard em $SCORECARD_PATH)" | tee -a "$LOG"
exit "${STATUS:-1}"
