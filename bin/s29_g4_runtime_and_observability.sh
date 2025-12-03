#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S29_G4_runtime_and_observability"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S29_G4_runtime_and_observability.json"

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

COMPILE_LOG="$EVIDENCE_DIR/compile.log"
TEST_LOG="$EVIDENCE_DIR/runtime_tests.log"

STATUS="PASS"

echo "[S29_G4] Compilando runtime de fluxo..." | tee "$COMPILE_LOG"
if ! (cd "$ROOT_DIR" && python3 -m compileall app/agents/flows inspectah/ingest/pipeline.py >>"$COMPILE_LOG" 2>&1); then
  STATUS="FAIL"
fi

echo "[S29_G4] Executando testes de runtime/ingest..." | tee "$TEST_LOG"
if ! (cd "$ROOT_DIR" && PYTHONPATH=. ./.venv/bin/pytest tests/agents/test_agent_flow_runtime.py tests/unit/test_ingest_pipeline.py -q >>"$TEST_LOG" 2>&1); then
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
    "gate_id": "S29_G4",
    "status": status,
    "timestamp": timestamp,
    "notes": "" if status == "PASS" else "Verifique evidências em out/evidence/S29_G4_runtime_and_observability",
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if status != "PASS":
    sys.exit(1)
PY

echo "[S29_G4] Scorecard gerado em $SCORECARD_PATH com status $STATUS"
