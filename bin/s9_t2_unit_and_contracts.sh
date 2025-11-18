#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"
export NET=0

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S9_T2_unit_and_contracts"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
SCORECARD_FILE="$SCORECARDS_DIR/S9_T2_unit_and_contracts.json"
PYTEST_LOG="$EVIDENCE_DIR/pytest.log"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"
STATUS="PASS"

if PYTHONPATH=. .venv/bin/python -m pytest tests/s9_t2_unit_contracts -q >"$PYTEST_LOG" 2>&1; then
  TEST_STATUS="PASS"
else
  TEST_STATUS="FAIL"
  STATUS="FAIL"
fi

python3 - "$SUMMARY_FILE" "$SCORECARD_FILE" "$PYTEST_LOG" "$STATUS" "$TIMESTAMP" <<'PY'
import json
import re
from pathlib import Path
import sys

summary_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
pytest_log = Path(sys.argv[3])
status = sys.argv[4]
timestamp = sys.argv[5]
log_text = pytest_log.read_text(encoding="utf-8")
match = re.search(r"(\d+) passed", log_text)
passed = int(match.group(1)) if match else 0
failed_match = re.search(r"(\d+) failed", log_text)
failed = int(failed_match.group(1)) if failed_match else 0

summary = {
    "gate": "S9_T2_unit_and_contracts",
    "status": status,
    "timestamp": timestamp,
    "pytest_log": str(pytest_log),
    "results": {"passed": passed, "failed": failed},
    "invariants": ["Inv1", "Inv2", "Inv4"],
}
summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate": "S9_T2_unit_and_contracts",
    "status": status,
    "timestamp": timestamp,
    "details": {"tests_passed": passed, "tests_failed": failed},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
PY

if [[ "$STATUS" != "PASS" ]]; then
  exit 1
fi

echo "S9_T2_unit_and_contracts PASS. Evidencias em $EVIDENCE_DIR"
