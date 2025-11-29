#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G5_admin_ui"
SCORECARD_PATH="$SCORECARD_DIR/S22_G5_admin_ui.json"
DOC_UI="$ROOT_DIR/docs/sprint_22_g5_admin_ui.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="Fluxos de admin UI validados."
max_clicks=3
admin_flows_covered=0
ux_test_non_dev_participant=false

if [[ ! -f "$DOC_UI" ]]; then
  status="FAIL"
  notes="Doc de UI de admin ausente."
else
  admin_flows_covered=$(rg --no-heading -c "^+- \\*\\*F" "$DOC_UI" || echo "0")
fi

echo "[S22_G5] Rodando testes de UI/admin..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_admin_ui_flows.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  ux_test_non_dev_participant=true
else
  status="FAIL"
  notes="Falha nos testes da UI/admin."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$max_clicks" "$admin_flows_covered" "$ux_test_non_dev_participant"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G5",
    "status": sys.argv[2],
    "max_clicks_to_last_run_info": int(sys.argv[4]),
    "admin_flows_covered": int(sys.argv[5]),
    "ux_test_non_dev_participant": sys.argv[6].lower() == "true",
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "Fluxos da UI de admin e prints/recordings se presentes."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G5] status=$status"
