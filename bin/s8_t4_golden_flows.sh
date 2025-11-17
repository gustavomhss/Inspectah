#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T4_golden_flows"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T4_golden_flows.json"
LOG_FILE="$EVIDENCE_DIR/pytest.log"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
export ROOT_DIR EVIDENCE_DIR SCORECARDS_DIR SUMMARY_FILE MANIFEST_FILE SCORECARD_FILE LOG_FILE TIMESTAMP

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

STATUS="PASS"
if ! (cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" -m pytest tests/s8_t4_golden_flows -q >"$LOG_FILE" 2>&1); then
  STATUS="FAIL"
fi
export STATUS

python3 - <<'PY'
import json
import os
from pathlib import Path

summary_path = Path(os.environ["SUMMARY_FILE"])
manifest_path = Path(os.environ["MANIFEST_FILE"])
scorecard_path = Path(os.environ["SCORECARD_FILE"])
log_file = Path(os.environ["LOG_FILE"])
status = os.environ["STATUS"]
timestamp = os.environ["TIMESTAMP"]

summary = {
    "gate": "S8_T4_golden_flows",
    "status": status,
    "timestamp": timestamp,
    "details": {
        "log_file": str(log_file),
    },
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

manifest = {
    "gate": "S8_T4_golden_flows",
    "artifacts": [str(log_file)] + [f"tests/goldens/{name}.json" for name in ["s8_preco_medio", "s8_comparacao_simples", "s8_checagem_factual"]],
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T4_golden_flows",
    "status": status,
    "timestamp": timestamp,
    "outputs": {"summary_file": str(summary_path)},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY

if [[ "$STATUS" != "PASS" ]]; then
  cat "$LOG_FILE"
  exit 1
fi

echo "S8_T4_golden_flows PASS. Evidências em $EVIDENCE_DIR"
