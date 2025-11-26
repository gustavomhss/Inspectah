#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S23_G3_frontend_console"
SCORECARD_PATH="$SCORECARD_DIR/S23_G3_frontend_console.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
status="PASS"
notes="Vitest executado."
LOGFILE="$EVIDENCE_DIR/tests.log"

echo "[S23_G3] npm test (frontend)" > "$LOGFILE"
if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm test >> "$LOGFILE" 2>&1); then
  status="FAIL"
  notes="Falha nos testes de frontend (console de agentes)"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
    "gate_id": "S23_G3",
    "status": sys.argv[2],
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}, indent=2), encoding="utf-8")
PY

echo "[S23_G3] status=$status"
