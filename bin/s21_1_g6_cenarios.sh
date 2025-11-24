#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G6_cenarios"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G6_cenarios.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
logs=("cenario_1_noticias.log" "cenario_2_esportes.log" "cenario_3_clima.log" "cenario_4_fofoca.log")
missing=()
for f in "${logs[@]}"; do
  [[ -f "$EVIDENCE_DIR/$f" ]] || missing+=("$f")
done
STATUS="PASS"; NOTES="Cenários registrados"
if [[ ${#missing[@]} -gt 0 ]]; then
  STATUS="FAIL"; NOTES="Logs ausentes: ${missing[*]}"
fi
python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$NOTES"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G6","status":sys.argv[2],"automated_checks":{"status":sys.argv[2],"details":sys.argv[3]},"reviewers_internal":[],"reviewers_external":[],"risk_level":"low" if sys.argv[2]=="PASS" else "high","notes":sys.argv[3],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); files=[p.name for p in ed.iterdir() if p.is_file()]
(ed/"MANIFEST.json").write_text(json.dumps({"files":sorted(files),"notes":"Cenários rodados com o Copiloto"}, indent=2), encoding="utf-8")
PY
echo "[S21_1_G6] status=$STATUS"
