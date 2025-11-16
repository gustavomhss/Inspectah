#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G7_guard_automation.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G7_guard_automation"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

GUARD_LOG="$EVIDENCE_DIR/guard_run.log"
if "$REPO_ROOT/bin/inspectah_s6_guard.sh" | tee "$GUARD_LOG"; then
  status="PASS"
else
  status="FAIL"
fi

"$PYTHON_BIN" - "$SCORECARD" "$status" "$GUARD_LOG" <<'PY'
import json, sys
scorecard_path, status, guard_log = sys.argv[1:4]
json.dump({
    "gate": "S6_G7",
    "name": "guard_automation",
    "status": status,
    "details": {
        "guard_log": guard_log,
    },
}, open(scorecard_path, "w", encoding='utf-8'), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
