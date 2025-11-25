#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G1_ux_widget"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G1_ux_widget.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
files=(
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/components/CopilotoWidget.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/components/CopilotoChatPanel.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/hooks/useCopilotoAgent.ts"
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/pages/AdminSourceFormPage.tsx"
)
missing=()
for f in "${files[@]}"; do
  [[ -f "$f" ]] || missing+=("$f")
done
status="PASS"; notes="Widget e painel presentes."
if [[ ${#missing[@]} -gt 0 ]]; then
  status="FAIL"; notes="Arquivos ausentes: ${missing[*]}"
fi
python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G1","status":sys.argv[2],"automated_checks":{"status":sys.argv[2],"details":sys.argv[3]},"reviewers_internal":[],"reviewers_external":[],"risk_level":"low" if sys.argv[2]=="PASS" else "high","notes":sys.argv[3],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); ed.mkdir(parents=True, exist_ok=True)
manifest={"files": sorted([p.name for p in ed.iterdir() if p.is_file()]), "notes": "Verificação de UX do widget."}
(ed/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_1_G1] status=$status"
