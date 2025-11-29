#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T2_unit_contracts"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T2_unit_contracts.json"
LOG_FILE="$EVIDENCE_DIR/pytest.log"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

STATUS="PASS"
if ! (cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR" pytest tests/s8_t2_unit_contracts -q >"$LOG_FILE" 2>&1); then
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

log_text = ""
if log_file.exists():
    log_text = log_file.read_text()

match = re.search(r"(\d+) passed.*?(\d+) failed", log_text)
if match:
    passed = int(match.group(1))
    failed = int(match.group(2))
else:
    passed = log_text.count("PASSED")
    failed = log_text.count("FAILED")

summary = {
    "gate": "S8_T2_unit_contracts",
    "status": status,
    "timestamp": timestamp,
    "details": {
        "tests_passed": passed,
        "tests_failed": failed,
        "log_file": str(log_file),
    },
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

manifest = {
    "gate": "S8_T2_unit_contracts",
    "artifacts": [str(log_file), str(summary_path)],
}
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T2_unit_contracts",
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

echo "S8_T2_unit_contracts PASS. Evidências em $EVIDENCE_DIR"
