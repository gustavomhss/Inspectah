#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G0_contexto"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G0_contexto.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
docs=(
  "$ROOT_DIR/docs/sprint_21_1_capitulo_1.md"
  "$ROOT_DIR/docs/sprint_21_1_capitulo_2_gates.md"
  "$ROOT_DIR/docs/sprint_21_1_capitulo_3_filemap.md"
  "$ROOT_DIR/docs/sprint_21_1_capitulo_4_execucao.md"
)
missing=()
for doc in "${docs[@]}"; do
  [[ -f "$doc" ]] || missing+=("$doc")
done
status="PASS"; notes="Contexto da S21.1 materializado."
if [[ ${#missing[@]} -gt 0 ]]; then
  status="FAIL"; notes="Docs ausentes: ${missing[*]}"
fi
python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out = {
    "gate_id": "S21_1_G0",
    "status": sys.argv[2],
    "automated_checks": {"status": sys.argv[2], "details": sys.argv[3]},
    "reviewers_internal": [],
    "reviewers_external": [],
    "risk_level": "low" if sys.argv[2]=="PASS" else "high",
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); ed.mkdir(parents=True, exist_ok=True)
manifest={"files": sorted([p.name for p in ed.iterdir() if p.is_file()]), "notes": "Capítulos 21.1 verificados."}
(ed/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_1_G0] status=$status"
