#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S23_G1_modelo_dados"
SCORECARD_PATH="$SCORECARD_DIR/S23_G1_modelo_dados.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
status="PASS"
notes="Testes de agentes executados."

LOGFILE="$EVIDENCE_DIR/tests.log"
echo "[S23_G1] pytest tests/agents/test_s23_agents_api.py" > "$LOGFILE"
if ! (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/agents/test_s23_agents_api.py -q >> "$LOGFILE" 2>&1); then
  status="FAIL"
  notes="Falha nos testes de domínio/API de agentes"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
    "gate_id": "S23_G1",
    "status": sys.argv[2],
    "notes": sys.argv[3],
    "tests": ["tests/agents/test_s23_agents_api.py"],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}, indent=2), encoding="utf-8")
PY

echo "[S23_G1] status=$status"
