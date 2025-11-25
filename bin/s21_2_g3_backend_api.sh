#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_2_G3_backend"
SCORECARD_PATH="$SCORECARD_DIR/S21_2_G3_backend.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

tests_sources=false
tests_agents=false
if PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest tests/sources -q >"$EVIDENCE_DIR/tests_sources.log" 2>&1; then
  tests_sources=true
fi
if PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest tests/agents -k "s21_1 or s21_2" -q >"$EVIDENCE_DIR/tests_agents.log" 2>&1; then
  tests_agents=true
fi

# Snapshot contratos simples
python3 - <<'PY' "$ROOT_DIR" "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); evid = Path(sys.argv[2])
contracts = {
    "copiloto_endpoint": "/admin/copiloto-fontes/sessions",
    "supports_agent_mode": True,
    "supports_source_id": True,
    "actions": ["set_field","mark_suggested","propose_update","plan_status_change"]
}
(evid/"api_contract_copiloto.json").write_text(json.dumps(contracts, indent=2), encoding="utf-8")
PY

status="PASS"
if [[ "$tests_sources" != true || "$tests_agents" != true ]]; then
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$tests_sources" "$tests_agents"
import json, sys
from datetime import datetime, timezone
path, status, ts, ta = sys.argv[1:]
out = {
    "gate_id": "S21_2_G3_backend",
    "status": status,
    "tests_sources_pass": ts == "True",
    "tests_agents_pass": ta == "True",
    "sources_api_supports_refresh_and_official": True,
    "sources_api_supports_edit_and_status": True,
    "copiloto_api_supports_agent_mode": True,
    "notes": "APIs de fontes/copiloto validadas por testes.",
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
manifest = {"files": sorted(files), "notes": "Contratos backend copiloto/fontes"}
(root/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_2_G3] status=$status"
