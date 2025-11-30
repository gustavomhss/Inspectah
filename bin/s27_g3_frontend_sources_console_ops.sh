#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S27_G3_frontend_sources_console_ops"
SCORECARD_PATH="$SCORECARD_DIR/S27_G3_frontend_sources_console_ops.json"
LOG_PATH="$EVIDENCE_DIR/g3_frontend_sources_console_ops.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

STATUS="GO"

set +e
cd "$ROOT_DIR/frontend/inspectah-ui"
npm run lint -- --max-warnings=0 src/features/sources 2>&1 | tee "$LOG_PATH"
LINT_EXIT=${PIPESTATUS[0]}
npm test -- src/features/sources/__tests__/sourcesPages.test.tsx 2>&1 | tee -a "$LOG_PATH"
TEST_EXIT=${PIPESTATUS[0]}
set -e

if [[ $LINT_EXIT -ne 0 || $TEST_EXIT -ne 0 ]]; then
  STATUS="NO_GO"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S27_G3_frontend_sources_console_ops",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "lint_passed": status == "GO",
        "tests_passed": status == "GO",
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S27_G3] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
