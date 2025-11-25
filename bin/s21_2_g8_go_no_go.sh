#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_2_G8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S21_2_G8_go_no_go.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

all_pass=true
for g in S21_2_G0_contexto S21_2_G1_ontologia S21_2_G2_fluxos S21_2_G3_backend S21_2_G4_frontend S21_2_G5_agent S21_2_G6_safety S21_2_G7_scorecard; do
  card="$SCORECARD_DIR/${g}.json"
  if [[ ! -f "$card" ]]; then
    all_pass=false
    continue
  fi
  status=$(python3 - <<'PY' "$card"
import json,sys
data=json.load(open(sys.argv[1]))
print(data.get("status","FAIL"))
PY
)
  if [[ "$status" != "PASS" ]]; then
    all_pass=false
  fi
done

decision="GO"
status="PASS"
if [[ "$all_pass" != true ]]; then
  decision="NO_GO"
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$decision" "$all_pass" "$status"
import json, sys
from datetime import datetime, timezone
path, decision, all_pass, status = sys.argv[1:]
out = {
    "gate_id": "S21_2_G8_go_no_go",
    "status": status,
    "decision": decision,
    "all_gates_pass": all_pass == "True",
    "reason": "Todos os gates S21.2 em PASS." if decision=="GO" else "Algum gate falhou.",
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}
from pathlib import Path
Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1]); cards = Path(sys.argv[2])
manifest = {"scorecards": [p.name for p in cards.glob("S21_2_G*.json")]}
(root/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_2_G8] decision=$decision status=$status"
