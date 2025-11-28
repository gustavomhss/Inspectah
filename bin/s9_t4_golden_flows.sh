#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"
export INSPECTAH_DATA_DIR="${INSPECTAH_DATA_DIR:-$ROOT/out/evidence}"

PYTHON_BIN="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

OUT_DIR="$ROOT/out/evidence/S9_T4_golden_flows"
SCORECARD="$ROOT/out/scorecards/S9_T4_golden_flows.json"
SUMMARY="$OUT_DIR/summary.json"
MANIFEST="$OUT_DIR/MANIFEST.json"
LOG_FILE="$OUT_DIR/pytest.log"

mkdir -p "$OUT_DIR" "$(dirname "$SCORECARD")"

RESULT="PASS"
DETAILS=""
if ! "$PYTHON_BIN" -m pytest tests/s9_t4_golden_flows -q >"$LOG_FILE" 2>&1; then
  RESULT="FAIL"
  DETAILS="pytest retornou falha nos golden flows"
else
  DETAILS="pytest executado com sucesso nos golden flows"
fi

cat > "$SUMMARY" <<JSON
{
  "gate": "S9_T4_golden_flows",
  "command": "${PYTHON_BIN} -m pytest tests/s9_t4_golden_flows -q",
  "details": "$DETAILS",
  "timestamp": "$(date -Iseconds)",
  "status": "$RESULT",
  "log_file": "$LOG_FILE"
}
JSON

cat > "$MANIFEST" <<JSON
{
  "artifacts": [
    "$LOG_FILE",
    "tests/goldens/s9_preco_medio.json",
    "tests/goldens/s9_comparacao_simples.json",
    "tests/goldens/s9_checagem_factual.json"
  ]
}
JSON

cat > "$SCORECARD" <<JSON
{
  "gate": "S9_T4",
  "name": "Golden flows C1-C3",
  "status": "$RESULT",
  "summary_path": "out/evidence/S9_T4_golden_flows/summary.json"
}
JSON

if [[ "$RESULT" != "PASS" ]]; then
  exit 1
fi
