#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S27_G2_backend_ingestion_ops"
SCORECARD_PATH="$SCORECARD_DIR/S27_G2_backend_ingestion_ops.json"
LOG_PATH="$EVIDENCE_DIR/g2_backend_ingestion_ops.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

STATUS="GO"

set +e
cd "$ROOT_DIR"
"$PYTHON_BIN" -m pytest tests/ingestion/test_service_contracts.py tests/ingestion/test_observability.py tests/ingestion/test_admin_ui_flows.py tests/sources/test_routes_admin.py 2>&1 | tee "$LOG_PATH"
EXIT_CODE=${PIPESTATUS[0]}
set -e

if [[ $EXIT_CODE -ne 0 ]]; then
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
    "gate": "S27_G2_backend_ingestion_ops",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "tests_passed": status == "GO",
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S27_G2] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
