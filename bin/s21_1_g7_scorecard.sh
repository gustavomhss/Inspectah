#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G7_scorecard"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G7_scorecard.json"
DOC="$ROOT_DIR/docs/sprint_21_1_scorecard_copiloto_fontes.md"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
STATUS="PASS"; NOTES="Scorecard preenchido"
[[ -f "$DOC" ]] || { STATUS="FAIL"; NOTES="Doc de scorecard ausente"; }
python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$NOTES"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G7","status":sys.argv[2],"automated_checks":{"status":sys.argv[2],"details":sys.argv[3]},"reviewers_internal":[],"reviewers_external":[],"risk_level":"low" if sys.argv[2]=="PASS" else "high","notes":sys.argv[3],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR" "$DOC"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); doc=Path(sys.argv[2])
ed.mkdir(parents=True, exist_ok=True)
manifest={"files": [p.name for p in ed.iterdir() if p.is_file()], "notes": f"Scorecard doc: {doc.name}"}
(ed/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_1_G7] status=$STATUS"
