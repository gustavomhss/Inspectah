#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S26_G3_frontend_quality"
SCORECARD_PATH="$SCORECARD_DIR/S26_G3_frontend_quality.json"
LOG_PATH="$EVIDENCE_DIR/g3_frontend_quality.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

lint_errors_count=0
frontend_tests_total=1
frontend_tests_passed=0
build_succeeded=false

if [[ ! -d "$ROOT_DIR/frontend/inspectah-ui/node_modules" ]]; then
  lint_errors_count=1
  echo "[S26_G3] Dependências de frontend ausentes. Rode npm ci em frontend/inspectah-ui." | tee "$LOG_PATH"
else
  echo "[S26_G3] Rodando lint completo..." | tee "$LOG_PATH"
  if ! (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run lint >>"$LOG_PATH" 2>&1); then
    lint_errors_count=1
  fi

  echo "[S26_G3] Rodando vitest (modo headless)..." | tee -a "$LOG_PATH"
  if (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run test >>"$LOG_PATH" 2>&1); then
    frontend_tests_passed=$frontend_tests_total
  fi

  echo "[S26_G3] Rodando build do frontend..." | tee -a "$LOG_PATH"
  if (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run build -- --outDir /tmp/s26-frontend-build --emptyOutDir=false --sourcemap=false >>"$LOG_PATH" 2>&1); then
    build_succeeded=true
  fi
fi

STATUS="GO"
if [[ $lint_errors_count -ne 0 || $frontend_tests_total -ne $frontend_tests_passed || "$build_succeeded" != "true" ]]; then
  STATUS="NO_GO"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$lint_errors_count" "$frontend_tests_total" "$frontend_tests_passed" "$build_succeeded"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
lint_errors_count = int(sys.argv[3])
frontend_tests_total = int(sys.argv[4])
frontend_tests_passed = int(sys.argv[5])
build_succeeded = sys.argv[6].lower() == "true"

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S26_G3_frontend_quality",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "lint_errors_count": lint_errors_count,
        "frontend_tests_total": frontend_tests_total,
        "frontend_tests_passed": frontend_tests_passed,
        "build_succeeded": build_succeeded,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S26_G3] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
