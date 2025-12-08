#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/SF2_G4"
LOG="out/logs/SF2_G4.log"

mkdir -p "$EVIDENCE_DIR" "$EVIDENCE_DIR/provider_screens" out/logs
: >"$LOG"

log() {
  echo "[SF2_G4] $*" | tee -a "$LOG"
}

fail() {
  log "FAIL: $*"
  exit 1
}

RBAC_NEG="$EVIDENCE_DIR/rbac_negative.log"
RBAC_POS="$EVIDENCE_DIR/rbac_positive.log"
TEST_LOG="$EVIDENCE_DIR/tests.log"
PLAYWRIGHT_LOG="$EVIDENCE_DIR/playwright.log"

log "RBAC negativo/positivo usando FlowService (actor ausente vs presente)"
python3 - <<'PY' >"$RBAC_NEG" 2>&1
from pathlib import Path
from app.flows.service import FlowService

db_path = Path("out/databases/sf2_g4.sqlite")
if db_path.exists():
    db_path.unlink()
svc = FlowService(db_path=db_path)
svc._flags_cache = {
    "s34_flow_multidomain_enabled": True,
    "s35_flow_rollout_enabled": True,
    "s35_flow_catalog_enforced": True,
    "s35_flow_logic_contract_enabled": True,
}
flow = svc.create_flow_from_template("news_v2", "Flow RBAC", "flow_news_v2")
base_version = flow.flow_version_id

neg_error = None
try:
    svc.start_rollout(flow.id, mode="canary", test_percentual=10, actor=None, operation_id="op_rbac_neg", request_catalog_hash=flow.catalog_hash or "")
except Exception as exc:  # expected
    neg_error = str(exc)

if not neg_error:
    raise SystemExit("Esperava erro sem actor, mas start_rollout passou")

svc.start_rollout(flow.id, mode="canary", test_percentual=10, actor="ops_user", operation_id="op_rbac_pos", request_catalog_hash=flow.catalog_hash or "")
svc.promote_rollout(flow.id, actor="ops_admin", operation_id="op_rbac_promote", request_catalog_hash=flow.catalog_hash or "")
svc.create_version(flow.id, "news_v2", "v2.2.1-rbac")
svc.rollback_rollout(flow.id, target_version_id=base_version, actor="ops_admin", operation_id="op_rbac_rollback", request_catalog_hash=flow.catalog_hash or "")

Path("out/evidence/SF2_G4/rbac_positive.log").write_text("start/promote/rollback ok\\n")
print(f"NEG_ERROR={neg_error}")
PY
if [ $? -ne 0 ]; then
  fail "RBAC via FlowService não confirmou 401/403 esperado"
fi

log "Rodando pytest/vitest com rc estrito"
PYTHON_BIN=".venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi
PYTEST_TARGETS=(tests/flows/test_console_rollout_api.py)
if ! "$PYTHON_BIN" -m pytest "${PYTEST_TARGETS[@]}" 2>&1 | tee -a "$TEST_LOG"; then
  fail "pytest falhou (console/rollout)"
fi

if [ -d "frontend/inspectah-ui" ]; then
  if ! npm --prefix frontend/inspectah-ui test 2>&1 | tee -a "$TEST_LOG"; then
    fail "npm test (frontend) falhou"
  fi
  if command -v npx >/dev/null 2>&1; then
    if ! (cd frontend/inspectah-ui && npx playwright test --config=playwright.config.ts) 2>&1 | tee -a "$PLAYWRIGHT_LOG"; then
      fail "Playwright falhou (capturar estados UI)"
    fi
  else
    fail "npx/playwright ausente; não é permitido passar sem execução"
  fi
else
  fail "frontend/inspectah-ui ausente"
fi

if ! ls "$EVIDENCE_DIR"/provider_screens/*.png >/dev/null 2>&1; then
  fail "Sem screenshots em $EVIDENCE_DIR/provider_screens (capture estados ops_only/derived/erros)"
fi

log "SF2_G4 concluído com evidências em $EVIDENCE_DIR"
