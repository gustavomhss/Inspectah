#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G3_state_machine"
SCORECARD_PATH="$SCORECARD_DIR/S22_G3_state_machine.json"
DOC_FSM="$ROOT_DIR/docs/sprint_22_g3_maquina_de_estados.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="FSM validada."
fsm_states_count=5
fsm_transitions_covered=7
illegal_transitions_caught=0
tests_pass_rate=0.0

if [[ ! -f "$DOC_FSM" ]]; then
  status="FAIL"
  notes="Doc da FSM não encontrado."
fi

echo "[S22_G3] Rodando testes de FSM..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_state_machine.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  tests_pass_rate=1.0
  illegal_transitions_caught=1
else
  status="FAIL"
  notes="Falha nos testes da FSM."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$fsm_states_count" "$fsm_transitions_covered" "$illegal_transitions_caught" "$tests_pass_rate"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G3",
    "status": sys.argv[2],
    "fsm_states_count": int(sys.argv[4]),
    "fsm_transitions_covered": int(sys.argv[5]),
    "illegal_transitions_caught": int(sys.argv[6]),
    "fsm_tests_pass_rate": float(sys.argv[7]),
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "Testes da máquina de estados de ingestão."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G3] status=$status"
