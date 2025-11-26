#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S23_orr"
SCORECARD_PATH="$SCORECARD_DIR/S23_G8_orr.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
status="GO"
notes="Todos os gates verificados."

for sc in "$SCORECARD_DIR"/S23_G*.json; do
  # ignora o próprio ORR para evitar falso NO_GO
  if [[ -f "$sc" && "$sc" != "$SCORECARD_PATH" ]]; then
    st=$(python3 - <<'PY' "$sc"
import json,sys
from pathlib import Path
print(json.loads(Path(sys.argv[1]).read_text()).get("status","FAIL"))
PY
)
    if [[ "$st" != "PASS" ]]; then
      status="NO_GO"
      notes="Gate falhou: $sc"
    fi
  fi
done

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
Path(sys.argv[1]).write_text(json.dumps({
    "gate_id": "S23_G8",
    "status": sys.argv[2],
    "orr_decision": sys.argv[2],
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}, indent=2), encoding="utf-8")
PY

echo "[S23_G8] decision=$status"
