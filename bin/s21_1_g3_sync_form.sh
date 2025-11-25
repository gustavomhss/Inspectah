#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_1_G3_sync_form"
SCORECARD_PATH="$SCORECARD_DIR/S21_1_G3_sync_form.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"
cd "$ROOT_DIR/frontend/inspectah-ui"
STATUS="PASS"; NOTES="lint/test/build"
if ! npm run lint >"$EVIDENCE_DIR/lint.log" 2>&1; then STATUS="FAIL"; NOTES="lint falhou"; fi
if [[ "$STATUS" == "PASS" ]] && ! npm test -- --watch=false >"$EVIDENCE_DIR/test.log" 2>&1; then STATUS="FAIL"; NOTES="test falhou"; fi
if [[ "$STATUS" == "PASS" ]] && ! npm run build >"$EVIDENCE_DIR/build.log" 2>&1; then STATUS="FAIL"; NOTES="build falhou"; fi
python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$NOTES"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
out={"gate_id":"S21_1_G3","status":sys.argv[2],"automated_checks":{"status":sys.argv[2],"details":sys.argv[3]},"reviewers_internal":[],"reviewers_external":[],"risk_level":"low" if sys.argv[2]=="PASS" else "high","notes":sys.argv[3],"ts_last_update":datetime.now(timezone.utc).isoformat().replace("+00:00","Z")}
Path(sys.argv[1]).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY
python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
ed=Path(sys.argv[1]); files=[p.name for p in ed.iterdir() if p.is_file()]
(ed/"MANIFEST.json").write_text(json.dumps({"files":sorted(files),"notes":"lint/test/build do frontend"}, indent=2), encoding="utf-8")
PY
echo "[S21_1_G3] status=$STATUS"
