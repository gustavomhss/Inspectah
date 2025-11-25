#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G8_go_no_go.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
scorecards=(
  "$SCORECARD_DIR/S21_1_G0_contexto.json"
  "$SCORECARD_DIR/S21_1_G1_ux_widget.json"
  "$SCORECARD_DIR/S21_1_G2_agent_mode.json"
  "$SCORECARD_DIR/S21_1_G3_sync_form.json"
  "$SCORECARD_DIR/S21_1_G4_files.json"
  "$SCORECARD_DIR/S21_1_G5_safety.json"
  "$SCORECARD_DIR/S21_1_G6_cenarios.json"
  "$SCORECARD_DIR/S21_1_G7_scorecard.json"
)
missing=()
statuses=()
for sc in "${scorecards[@]}"; do
  [[ -f "$sc" ]] || missing+=("$sc")
  if [[ -f "$sc" ]]; then
    statuses+=("$(python3 -c "import json;import sys;print(json.load(open('$sc'))['status'])" 2>/dev/null || echo "FAIL")")
  fi

done
status="PASS"; decision="GO"; notes="Todos os gates anteriores em PASS"
if [[ ${#missing[@]} -gt 0 ]]; then
  status="FAIL"; decision="NO_GO"; notes="Scorecards ausentes: ${missing[*]}"
fi
for st in "${statuses[@]}"; do
  if [[ "$st" != "PASS" ]]; then
    status="FAIL"; decision="NO_GO"; notes="Gate com falha"; break
  fi

done
python3 - <<'PY' "$SCORECARD_PATH" "$status" "$decision" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G8","status":sys.argv[2],"decision":sys.argv[3],"notes":sys.argv[4],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR" "${scorecards[@]}"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); ed.mkdir(parents=True, exist_ok=True)
refs=sys.argv[2:]
manifest={"files": [p.name for p in ed.iterdir() if p.is_file()], "referenced_scorecards": [Path(r).name for r in refs]}
(ed/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_1_G8] decision=$decision status=$status"
