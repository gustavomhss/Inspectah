#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S26_G1_design_system_static"
SCORECARD_PATH="$SCORECARD_DIR/S26_G1_design_system_static.json"
LOG_PATH="$EVIDENCE_DIR/g1_design_system_static.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

lint_errors_count=0
ts_compile_errors_count=0
ds_component_tests_total=0
ds_component_tests_passed=0
orphan_admin_components_found=0

if [[ ! -d "$ROOT_DIR/frontend/inspectah-ui/node_modules" ]]; then
  lint_errors_count=1
  ts_compile_errors_count=1
  echo "[S26_G1] Dependências de frontend ausentes. Rode npm ci em frontend/inspectah-ui." | tee "$LOG_PATH"
else
  echo "[S26_G1] Rodando lint para ui/admin..." | tee "$LOG_PATH"
  if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run lint -- --max-warnings=0 src/ui/admin >>"$LOG_PATH" 2>&1); then
    lint_errors_count=1
  fi

  echo "[S26_G1] Rodando build (tsc) focado em ui/admin..." | tee -a "$LOG_PATH"
  if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run build -- --outDir /tmp/s26-admin-build --emptyOutDir=false --sourcemap=false >>"$LOG_PATH" 2>&1); then
    ts_compile_errors_count=1
  fi
fi

STATUS="GO"
if [[ $lint_errors_count -ne 0 || $ts_compile_errors_count -ne 0 || $ds_component_tests_total -ne $ds_component_tests_passed || $orphan_admin_components_found -ne 0 ]]; then
  STATUS="NO_GO"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$ts_compile_errors_count" "$lint_errors_count" "$ds_component_tests_total" "$ds_component_tests_passed" "$orphan_admin_components_found"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
ts_compile_errors_count = int(sys.argv[3])
lint_errors_count = int(sys.argv[4])
ds_component_tests_total = int(sys.argv[5])
ds_component_tests_passed = int(sys.argv[6])
orphan_admin_components_found = int(sys.argv[7])

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S26_G1_design_system_static",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "ts_compile_errors_count": ts_compile_errors_count,
        "lint_errors_count": lint_errors_count,
        "ds_component_tests_total": ds_component_tests_total,
        "ds_component_tests_passed": ds_component_tests_passed,
        "orphan_admin_components_found": orphan_admin_components_found,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S26_G1] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
