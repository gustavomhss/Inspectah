#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S26_G2_sources_console_flows"
SCORECARD_PATH="$SCORECARD_DIR/S26_G2_sources_console_flows.json"
LOG_PATH="$EVIDENCE_DIR/g2_sources_console_flows.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

EXPECTED_FILES=(
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/pages/SourceEditPage.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/components/SourcesTable.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/components/SourceForm.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/components/SourceStatusBadge.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/api/sourcesApi.ts"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/sources/types/Source.ts"
)

missing=()
for file in "${EXPECTED_FILES[@]}"; do
  if [[ ! -f "$file" ]]; then
    missing+=("$file")
  fi
done

flows_total=4
flows_passed=0
flows_blocking_failures=0
ui_regression_detected=false

if [[ ${#missing[@]} -gt 0 ]]; then
  flows_blocking_failures=${#missing[@]}
  {
    echo "[S26_G2] Arquivos faltantes:"
    printf '%s\n' "${missing[@]}"
  } | tee "$LOG_PATH"
else
  if [[ ! -d "$ROOT_DIR/frontend/inspectah-ui/node_modules" ]]; then
    flows_blocking_failures=1
    echo "[S26_G2] Dependências de frontend ausentes. Rode npm ci em frontend/inspectah-ui." | tee "$LOG_PATH"
  else
    echo "[S26_G2] Executando testes de fluxos do Console de Fontes v2 (vitest)..." | tee "$LOG_PATH"
    if (cd "$ROOT_DIR/frontend/inspectah-ui" && npm run test -- src/features/sources/__tests__/sourcesPages.test.tsx >>"$LOG_PATH" 2>&1); then
      flows_passed=$flows_total
    else
      flows_blocking_failures=1
    fi
  fi
fi

STATUS="GO"
if [[ $flows_blocking_failures -ne 0 || $flows_passed -ne $flows_total || "$ui_regression_detected" != "false" ]]; then
  STATUS="NO_GO"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$flows_total" "$flows_passed" "$flows_blocking_failures" "$ui_regression_detected"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
flows_total = int(sys.argv[3])
flows_passed = int(sys.argv[4])
flows_blocking_failures = int(sys.argv[5])
ui_regression_detected = sys.argv[6].lower() == "true"

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

scorecard = {
    "gate": "S26_G2_sources_console_flows",
    "timestamp": timestamp,
    "status": status,
    "metrics": {
        "flows_total": flows_total,
        "flows_passed": flows_passed,
        "flows_blocking_failures": flows_blocking_failures,
        "ui_regression_detected": ui_regression_detected,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2))
print(f"[S26_G2] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "GO" ]]; then
  exit 1
fi
