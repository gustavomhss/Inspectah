#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

LOG="out/evidence/S33_G5_orr/run.log"
mkdir -p out/scorecards out/evidence/S33_G5_orr

missing=()
for sc in out/scorecards/S33_G0_scope_and_baseline.json out/scorecards/S33_G1_incidents.json out/scorecards/S33_G2_cockpit.json out/scorecards/S33_G3_slos.json out/scorecards/S33_G4_runbooks.json; do
  [[ -f "$sc" ]] || missing+=("$sc")
done

status="PASS"
if ((${#missing[@]} > 0)); then
  status="FAIL"
fi

echo "[S33_G5] ORR checklist (simulado)" | tee "$LOG"
if [ "$status" = "PASS" ]; then
  echo "Gates anteriores presentes; rodar sessão ORR manual" >>"$LOG"
else
  echo "Faltam scorecards: ${missing[*]:-}" >>"$LOG"
fi

python3 - <<PY
import datetime
import json
import pathlib
import os

missing_env = os.environ.get("S33_G5_MISSING", "")
missing_list = [m for m in missing_env.split(",") if m]
scorecard = {
    "gate": "S33_G5_orr",
    "status": os.environ.get("STATUS", "$status"),
    "missing_scorecards": missing_list,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S33_G5_orr.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
