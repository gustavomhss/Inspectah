#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S21_G8_go_no_go.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

scorecards=(
  "S21_G0_contexto.json"
  "S21_G1_ontologia.json"
  "S21_G2_modelo_dados.json"
  "S21_G3_fluxos_admin.json"
  "S21_G4_ganchos_debunker.json"
  "S21_G5_contratos.json"
  "S21_G6_cenarios_uso.json"
  "S21_G7_scorecard.json"
)

missing=()
statuses=()
decision="GO"
notes="Todos os gates PASS."
for sc in "${scorecards[@]}"; do
  path="$SCORECARD_DIR/$sc"
  if [[ ! -f "$path" ]]; then
    missing+=("$sc")
    decision="NO_GO"
    continue
  fi
  status="$(python3 - <<'PY' "$path"
import json, sys
from pathlib import Path
data=json.loads(Path(sys.argv[1]).read_text())
print(data.get("status","UNKNOWN"))
PY
)"
  statuses+=("$sc:$status")
  if [[ "$status" != "PASS" && "$status" != "PASS_WITH_RISKS" ]]; then
    decision="NO_GO"
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  notes="Scorecards faltando: ${missing[*]}"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$decision" "$notes" "${statuses[@]}"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
statuses = sys.argv[3:]
decision = sys.argv[2]
notes = sys.argv[3] if len(sys.argv) > 3 else ""
scorecard = {
    "gate_id": "S21_G8",
    "status": "PASS" if decision == "GO" else "FAIL",
    "decision": decision,
    "gates": statuses,
    "risk_level": "low" if decision == "GO" else "high",
    "notes": notes,
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR" "${scorecards[@]}"
import json, sys
from pathlib import Path
manifest = {"files": ["MANIFEST.json"], "inputs": sys.argv[2:]}
Path(sys.argv[1] + "/MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G8] decision=$decision"
if [[ "$decision" != "GO" ]]; then
  exit 1
fi
