#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S29_G2_api_and_validator"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S29_G2_api_and_validator.json"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

COMPILE_LOG="$EVIDENCE_DIR/compile.log"
TEST_LOG="$EVIDENCE_DIR/tests.log"

STATUS="PASS"

echo "[S29_G2] Compilando módulos de fluxo e API..." | tee "$COMPILE_LOG"
if ! (cd "$ROOT_DIR" && python3 -m compileall app/agents/flows app/api/admin_agent_flows_routes.py >>"$COMPILE_LOG" 2>&1); then
  STATUS="FAIL"
fi

echo "[S29_G2] Executando testes de validator/API..." | tee "$TEST_LOG"
if ! (cd "$ROOT_DIR" && PYTHONPATH=. pytest tests/agents/test_agent_flow_validator.py tests/api/test_admin_agent_flows.py -q >>"$TEST_LOG" 2>&1); then
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
    "gate_id": "S29_G2",
    "status": status,
    "timestamp": timestamp,
    "notes": "" if status == "PASS" else "Verifique logs em out/evidence/S29_G2_api_and_validator/tests.log",
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if status != "PASS":
    sys.exit(1)
PY

echo "[S29_G2] Scorecard gerado em $SCORECARD_PATH com status $STATUS"
