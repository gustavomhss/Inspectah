#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/evidence/S30_G3_flow_operations_safety"
SCORECARD="$ROOT_DIR/out/scorecards/S30_G3_flow_operations_safety.json"

mkdir -p "$LOG_DIR"
STATUS="PASS"
REASONS=()

run_py() {
  python3 - "$@"
}

echo "[s30-g3] Validando operações seguras (transições + limites reprocesso)" | tee "$LOG_DIR/g3.log"

# Teste 1: transição proibida deve falhar
if ! run_py <<'PY' 2>"$LOG_DIR/transition_error.log"
from app.flows.service import FlowService, FlowState
svc = FlowService()
flow = svc.create_flow_from_template("fluxo_noticias_geral_v1", "Fluxo Teste", "fluxo_teste", {})
try:
    svc.set_flow_state(flow.id, FlowState.ATIVO)
    svc.set_flow_state(flow.id, FlowState.DRAFT)
    raise SystemExit(1)
except ValueError:
    raise SystemExit(0)
PY
then
  STATUS="FAIL"
  REASONS+=("Transição proibida não falhou conforme esperado")
fi

# Teste 2: reprocesso sem itens deve falhar
if ! run_py <<'PY' 2>"$LOG_DIR/reprocess_error.log"
from app.flows.service import FlowService
svc = FlowService()
flow = svc.create_flow_from_template("fluxo_noticias_geral_v1", "Fluxo Teste 2", "fluxo_teste_2", {})
try:
    svc.reprocess_items(flow.id, {"item_ids": []}, max_items=1)
    raise SystemExit(1)
except ValueError:
    raise SystemExit(0)
PY
then
  STATUS="FAIL"
  REASONS+=("Reprocesso sem itens não falhou")
fi

REASONS_JSON=$(printf '%s\n' "${REASONS[@]:-}" | python3 -c "import sys,json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")

echo "{ \"gate\": \"S30_G3_flow_operations_safety\", \"status\": \"${STATUS}\", \"reasons\": ${REASONS_JSON} }" > "$SCORECARD"

echo "[s30-g3] status=$STATUS scorecard=$SCORECARD"
exit 0
