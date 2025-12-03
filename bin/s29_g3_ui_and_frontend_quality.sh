#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S29_G3_ui_and_frontend_quality"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S29_G3_ui_and_frontend_quality.json"

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

LINT_LOG="$EVIDENCE_DIR/lint.log"
TEST_LOG="$EVIDENCE_DIR/test.log"
BUILD_LOG="$EVIDENCE_DIR/build.log"

STATUS="PASS"

echo "[S29_G3] Lint frontend" | tee "$LINT_LOG"
if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run lint >>"$LINT_LOG" 2>&1); then
  STATUS="FAIL"
fi

echo "[S29_G3] Test frontend" | tee "$TEST_LOG"
if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm test >>"$TEST_LOG" 2>&1); then
  STATUS="FAIL"
fi

echo "[S29_G3] Build frontend" | tee "$BUILD_LOG"
if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run build >>"$BUILD_LOG" 2>&1); then
  STATUS="FAIL"
fi

python3 - "$SCORECARD_PATH" "$STATUS" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate_id": "S29_G3",
    "status": status,
    "timestamp": timestamp,
    "notes": "" if status == "PASS" else "Verifique logs em out/evidence/S29_G3_ui_and_frontend_quality",
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if status != "PASS":
    sys.exit(1)
PY

echo "[S29_G3] Scorecard gerado em $SCORECARD_PATH com status $STATUS"
