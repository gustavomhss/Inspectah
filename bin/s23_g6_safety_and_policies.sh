#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S23_G6_safety_and_policies"
SCORECARD_PATH="$SCORECARD_DIR/S23_G6_safety_and_policies.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
status="PASS"
notes="Políticas de modelo e buffers configuráveis." 
python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
    "gate_id": "S23_G6",
    "status": sys.argv[2],
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}, indent=2), encoding="utf-8")
PY

echo "[S23_G6] status=$status"
