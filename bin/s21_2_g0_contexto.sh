#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_2_G0_contexto"
SCORECARD_PATH="$SCORECARD_DIR/S21_2_G0_contexto.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

tests_sources_pass=false
tests_agents_pass=false
s21_pass=false
s21_1_pass=false
cap1_exists=false

if PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest tests/sources -q >"$EVIDENCE_DIR/tests_sources.log" 2>&1; then
  tests_sources_pass=true
fi
if PYTHONPATH=. "$ROOT_DIR/.venv/bin/python" -m pytest tests/agents -q >"$EVIDENCE_DIR/tests_agents.log" 2>&1; then
  tests_agents_pass=true
fi
if bash "$ROOT_DIR/bin/s21_all_gates.sh" >"$EVIDENCE_DIR/s21_gates.log" 2>&1; then
  s21_pass=true
fi
if bash "$ROOT_DIR/bin/s21_1_all_gates.sh" >"$EVIDENCE_DIR/s21_1_gates.log" 2>&1; then
  s21_1_pass=true
fi

[[ -f "$ROOT_DIR/docs/sprint_21_2_capitulo_1.md" ]] && cap1_exists=true

status="PASS"
if [[ "$tests_sources_pass" != true || "$tests_agents_pass" != true || "$s21_pass" != true || "$s21_1_pass" != true || "$cap1_exists" != true ]]; then
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$tests_sources_pass" "$tests_agents_pass" "$s21_pass" "$s21_1_pass" "$cap1_exists"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
path, status, ts, ta, g21, g211, cap1 = sys.argv[1:]
out = {
    "gate_id": "S21_2_G0_contexto",
    "status": status,
    "tests_sources_pass": ts == "True",
    "tests_agents_pass": ta == "True",
    "s21_all_gates_pass": g21 == "True",
    "s21_1_all_gates_pass": g211 == "True",
    "cap1_exists": cap1 == "True",
    "notes": "Base S21/S21.1 verificada para S21.2",
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
files = [p.name for p in root.iterdir() if p.is_file()]
manifest = {"files": sorted(files), "notes": "Sanidade S21/S21.1 + docs S21.2 Cap1"}
(root/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_2_G0] status=$status"
