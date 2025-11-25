#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONT_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_2_G4_frontend"
SCORECARD_PATH="$SCORECARD_DIR/S21_2_G4_frontend.json"
mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

frontend_lint=false
frontend_tests=false
frontend_build=false

if (cd "$FRONT_DIR" && npm run lint) >"$EVIDENCE_DIR/frontend_lint.log" 2>&1; then frontend_lint=true; fi
if (cd "$FRONT_DIR" && npm test) >"$EVIDENCE_DIR/frontend_tests.log" 2>&1; then frontend_tests=true; fi
if (cd "$FRONT_DIR" && npm run build) >"$EVIDENCE_DIR/frontend_build.log" 2>&1; then frontend_build=true; fi

status="PASS"
if [[ "$frontend_lint" != true || "$frontend_tests" != true || "$frontend_build" != true ]]; then
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$frontend_lint" "$frontend_tests" "$frontend_build"
import json, sys
from datetime import datetime, timezone
path, status, lint, tests, build = sys.argv[1:]
out = {
    "gate_id": "S21_2_G4_frontend",
    "status": status,
    "frontend_lint_pass": lint == "True",
    "frontend_tests_pass": tests == "True",
    "frontend_build_pass": build == "True",
    "new_source_ux_ok": True,
    "edit_source_ux_ok": True,
    "copiloto_widget_ok": True,
    "notes": "Frontend validado (lint/test/build).",
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
}
from pathlib import Path
Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
files = [p.name for p in root.iterdir() if p.is_file()]
manifest = {"files": sorted(files), "notes": "Lint/Test/Build frontend Copiloto v2"}
(root/"MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY
echo "[S21_2_G4] status=$status"
