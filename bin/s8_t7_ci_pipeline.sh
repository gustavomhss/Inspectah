#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T7_ci"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T7_ci.json"
LOG_FILE="$EVIDENCE_DIR/ci.log"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
export ROOT_DIR EVIDENCE_DIR SCORECARDS_DIR SUMMARY_FILE SCORECARD_FILE LOG_FILE TIMESTAMP

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

STATUS="PASS"
if ! (cd "$ROOT_DIR" && PYTHONPATH="$ROOT_DIR" bin/s8_ci.sh >"$LOG_FILE" 2>&1); then
  STATUS="FAIL"
fi
export STATUS

python3 - <<'PY'
import json
import os
from pathlib import Path

summary = {
    "gate": "S8_T7_ci",
    "status": os.environ["STATUS"],
    "timestamp": os.environ["TIMESTAMP"],
    "details": {
        "log_file": os.environ["LOG_FILE"],
    },
}
Path(os.environ["SUMMARY_FILE"]).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T7_ci",
    "status": os.environ["STATUS"],
    "timestamp": os.environ["TIMESTAMP"],
    "outputs": {"summary_file": os.environ["SUMMARY_FILE"]},
}
Path(os.environ["SCORECARD_FILE"]).write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY

if [[ "$STATUS" != "PASS" ]]; then
  cat "$LOG_FILE"
  exit 1
fi

echo "S8_T7_ci PASS. Evidências em $EVIDENCE_DIR"
