#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S29_G1_model_and_migrations"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S29_G1_model_and_migrations.json"
DB_PATH="$EVIDENCE_DIR/s29_g1_test.sqlite"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

TEST_LOG="$EVIDENCE_DIR/tests.log"
MIG_LOG="$EVIDENCE_DIR/migration.log"
COMPILE_LOG="$EVIDENCE_DIR/compile.log"

STATUS="PASS"

echo "[S29_G1] Compilando módulos de fluxo de agentes..." | tee "$COMPILE_LOG"
if ! (cd "$ROOT_DIR" && python3 -m compileall app/agents/flows >>"$COMPILE_LOG" 2>&1); then
  STATUS="FAIL"
fi

echo "[S29_G1] Aplicando migration em $DB_PATH" | tee "$MIG_LOG"
if ! (cd "$ROOT_DIR" && python3 - "$DB_PATH" >>"$MIG_LOG" 2>&1 <<'PY'); then STATUS="FAIL"; fi
import sys
import importlib
from pathlib import Path

db_path = Path(sys.argv[1])
mig = importlib.import_module("migrations.versions.0004_s29_agent_flows")
mig.apply_migration(db_path)
info = mig.verify_schema(db_path)
print(f"Migration applied at {db_path} | tables={info['tables']} index={info['step_index']}")
PY

echo "[S29_G1] Rodando testes de modelos..." | tee "$TEST_LOG"
if ! (cd "$ROOT_DIR" && PYTHONPATH=. pytest tests/agents/test_agent_flow_models.py -q >>"$TEST_LOG" 2>&1); then
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
    "gate_id": "S29_G1",
    "status": status,
    "timestamp": timestamp,
    "notes": "" if status == "PASS" else "Verifique logs em out/evidence/S29_G1_model_and_migrations",
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if status != "PASS":
    sys.exit(1)
PY

echo "[S29_G1] Scorecard gerado em $SCORECARD_PATH com status $STATUS"
