#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T3_property"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T3_property.json"
LOG_FILE="$EVIDENCE_DIR/pytest.log"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

STATUS="PASS"
if ! (cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" -m pytest tests/s8_t3_property -q >"$LOG_FILE" 2>&1); then
  STATUS="FAIL"
fi

export STATUS TIMESTAMP ROOT_DIR LOG_FILE SUMMARY_FILE SCORECARD_FILE MANIFEST_FILE
python3 - <<'PY'
import json
import os
import re
from pathlib import Path

status = os.environ["STATUS"]
timestamp = os.environ["TIMESTAMP"]
log_file = Path(os.environ["LOG_FILE"])
summary_path = Path(os.environ["SUMMARY_FILE"])
manifest_path = Path(os.environ["MANIFEST_FILE"])
scorecard_path = Path(os.environ["SCORECARD_FILE"])

log_text = log_file.read_text() if log_file.exists() else ""
properties_checked = re.findall(r"::(test_[^ ]+)", log_text)

summary = {
    "gate": "S8_T3_property",
    "status": status,
    "timestamp": timestamp,
    "details": {
        "properties_checked": properties_checked,
        "log_file": str(log_file),
    },
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

manifest = {
    "gate": "S8_T3_property",
    "artifacts": [str(log_file), str(summary_path)],
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T3_property",
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

echo "S8_T3_property PASS. Evidências em $EVIDENCE_DIR"
