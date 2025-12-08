#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF3_G2"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF3_G2.log"
API_URL="${API_URL:-http://127.0.0.1:8000}"

mkdir -p "$EVIDENCE_DIR/screenshots" "$LOG_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF3_G2][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

BUILD_LOG="$EVIDENCE_DIR/build_test.log"
API_SMOKE="$EVIDENCE_DIR/api_smoke.log"
METRICS_OUT="$EVIDENCE_DIR/ingest_metrics.txt"
UI_STATES="$EVIDENCE_DIR/ui_states.png"

log "[SF3_G2] npm ci + build/test + Playwright"
(cd "$FRONTEND_DIR" && npm ci) >>"$BUILD_LOG" 2>&1
(cd "$FRONTEND_DIR" && npm run build) >>"$BUILD_LOG" 2>&1
(cd "$FRONTEND_DIR" && npm run test) >>"$BUILD_LOG" 2>&1
(cd "$FRONTEND_DIR" && npx playwright test) >>"$BUILD_LOG" 2>&1
log "[SF3_G2] build/test/playwright concluídos; logs em $BUILD_LOG"

ADMIN_TOKEN=$(ROLE=admin ACTOR=admin-user AUD=inspectah-api ISS=inspectah-idp "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/sf3_jwt_gen.py")

log "[SF3_G2] Smoke API admin/ingest"
{
  echo "== GET /admin/sources (role=admin) =="
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/admin/sources"
  echo -e "\n\n== POST /admin/ingestion/newsdata_br/run (role=admin) =="
  curl -s -w "\nstatus:%{http_code}\n" -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -X POST "$API_URL/admin/ingestion/newsdata_br/run" -d '{"trigger_origin":"sf3"}'
  echo -e "\n\n== GET /admin/ingestion/newsdata_br/runs (role=admin) =="
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/admin/ingestion/newsdata_br/runs"
  echo -e "\n\n== GET /api/providers/profiles (role=admin) =="
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/api/providers/profiles"
  echo -e "\n\n== GET /api/console/agents (role=admin) =="
  curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/api/console/agents"
} >"$API_SMOKE"

log "[SF3_G2] Capturando screenshot UI (estado atual)"
(cd "$FRONTEND_DIR" && node -e "import { chromium } from 'playwright'; (async () => { const browser = await chromium.launch({headless:true}); const context = await browser.newContext({ extraHTTPHeaders: {'Authorization':'Bearer $ADMIN_TOKEN'} }); const page = await context.newPage(); await page.goto('$API_URL', { waitUntil: 'domcontentloaded' }); await page.screenshot({ path: '$UI_STATES', fullPage: true }); await browser.close(); })();") >>"$BUILD_LOG" 2>&1 || fail "Falha ao capturar screenshot UI"

log "[SF3_G2] Coletando métricas de ingest/admin/truth"
curl -s "$API_URL/metrics" >"$METRICS_OUT" || fail "Não foi possível obter /metrics"
grep -Eq "ingest_requests_total|truth_promotion|auth_requests_total" "$METRICS_OUT" || fail "Métricas esperadas ausentes em /metrics"

log "[SF3_G2] Evidências em $EVIDENCE_DIR"
