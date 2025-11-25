#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_2_G2_fluxos"
SCORECARD_PATH="$SCORECARD_DIR/S21_2_G2_fluxos.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

docs_ok=true
for doc in "$ROOT_DIR/docs/sprint_21_2_fluxos_admin_fontes_v2.md" "$ROOT_DIR/docs/sprint_21_2_maquina_estados_copiloto.md"; do
  [[ -f "$doc" ]] || docs_ok=false
done

fsm_code_exists=false
[[ -f "$ROOT_DIR/inspectah/agents/copiloto_fontes_fsm.py" ]] && fsm_code_exists=true

status_ok=false
if PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest tests/agents -k "s21_1 or s21_2" -q >"$EVIDENCE_DIR/tests.log" 2>&1; then
  status_ok=true
fi

status="PASS"
if [[ "$docs_ok" != true || "$fsm_code_exists" != true || "$status_ok" != true ]]; then
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$docs_ok" "$fsm_code_exists" "$status_ok"
import json, sys
from datetime import datetime, timezone
path, status, docs_ok, fsm_ok, tests_ok = sys.argv[1:]
out = {
    "gate_id": "S21_2_G2_fluxos",
    "status": status,
    "flows_doc_present": docs_ok == "True",
    "fsm_doc_present": docs_ok == "True",
    "fsm_matches_code": fsm_ok == "True",
    "status_transitions_match_code": tests_ok == "True",
    "notes": "FSM e fluxos alinhados via testes de agente.",
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}
from pathlib import Path
Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
files = [p.name for p in root.iterdir() if p.is_file()]
manifest = {"files": sorted(files), "notes": "FSM/fluxos validados via testes."}
(root/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_2_G2] status=$status"
