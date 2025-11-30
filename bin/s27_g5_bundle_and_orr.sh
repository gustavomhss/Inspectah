#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S27_G5_bundle_and_orr"
SCORECARD_PATH="$SCORECARD_DIR/S27_G5_bundle_and_orr.json"
LOG_PATH="$EVIDENCE_DIR/g5_bundle_and_orr.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

STATUS="GO"

set +e
cd "$ROOT_DIR"
bash bin/s27_bundle.sh 2>&1 | tee "$LOG_PATH"
BUNDLE_EXIT=${PIPESTATUS[0]}
set -e

if [[ $BUNDLE_EXIT -ne 0 || ! -f "$ROOT_DIR/out/bundles/inspectah_s27_evidence_bundle.zip" ]]; then
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
    "gate": "S27_G5_bundle_and_orr",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "bundle_exists": (status == "GO"),
    },
    "evidence": {
        "bundle_path": "out/bundles/inspectah_s27_evidence_bundle.zip"
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S27_G5] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
