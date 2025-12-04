#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/evidence/S30_G2_flow_console_ops"
SCORECARD="$ROOT_DIR/out/scorecards/S30_G2_flow_console_ops.json"

mkdir -p "$LOG_DIR"
STATUS="PASS"
REASONS=()

echo "[s30-g2] Checando arquivos de API/Frontend de fluxos" | tee "$LOG_DIR/g2.log"

FILES=(
  "app/api/flow_console_routes.py"
  "app/flows/schemas.py"
  "frontend/inspectah-ui/src/features/flows/FlowsListPage.tsx"
  "frontend/inspectah-ui/src/features/flows/FlowDetailPage.tsx"
  "frontend/inspectah-ui/src/features/flows/__tests__/flows_console.spec.tsx"
)

for f in "${FILES[@]}"; do
  if [ ! -f "$ROOT_DIR/$f" ]; then
    STATUS="FAIL"
    REASONS+=("Arquivo ausente: $f")
  fi
done

REASONS_JSON=$(printf '%s\n' "${REASONS[@]:-}" | python3 -c "import sys,json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")

cat > "$SCORECARD" <<JSON
{
  "gate": "S30_G2_flow_console_ops",
  "status": "$STATUS",
  "reasons": $REASONS_JSON
}
JSON

echo "[s30-g2] status=$STATUS scorecard=$SCORECARD"
