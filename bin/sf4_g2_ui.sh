#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF4_G2"
PLAYWRIGHT_EVIDENCE="$EVIDENCE_DIR/playwright"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF4_G2.log"
RUN_LOG="$EVIDENCE_DIR/sf4_g2_ui.log"
UI_URL="${UI_URL:-http://127.0.0.1:3000}"
API_URL="${API_URL:-http://127.0.0.1:8000}"

mkdir -p "$EVIDENCE_DIR" "$PLAYWRIGHT_EVIDENCE" "$LOG_DIR"
: >"$RUN_LOG"

log() { echo "$@" | tee -a "$LOG_PATH" "$RUN_LOG"; }
fail() { echo "[SF4_G2][FAIL] $*" | tee -a "$LOG_PATH" "$RUN_LOG"; exit 1; }

if [[ ! -d "$FRONTEND_DIR" ]]; then
  fail "Frontend não encontrado em $FRONTEND_DIR"
fi

log "[SF4_G2] npm ci/test/build em $FRONTEND_DIR"
(
  cd "$FRONTEND_DIR"
  npm ci
  npm test
  npm run build
) 2>&1 | tee -a "$RUN_LOG"

log "[SF4_G2] Playwright smoke API+UI (sem mocks/snapshots)"
PLAYWRIGHT_REPORT="$PLAYWRIGHT_EVIDENCE/report.json"
node - <<'NODE' "$PLAYWRIGHT_EVIDENCE" "$PLAYWRIGHT_REPORT" "$ROOT_DIR" "$API_URL" "$UI_URL"
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const playwright = require(path.join(process.argv[4], 'frontend', 'inspectah-ui', 'node_modules', 'playwright'));

const evidenceDir = process.argv[2];
const reportPath = process.argv[3];
const root = process.argv[4];
const apiUrl = process.argv[5] || 'http://127.0.0.1:8000';
const uiUrl = process.argv[6] || 'http://127.0.0.1:3000';
const reqId = `sf4-${new Date().toISOString().replace(/[:.]/g, '-')}`;

function genToken(role, actor) {
  return execSync(`ROLE=${role} ACTOR=${actor} AUD=inspectah-api ISS=inspectah-idp ${root}/.venv/bin/python ${root}/bin/sf3_jwt_gen.py`, { encoding: 'utf-8' }).trim();
}

const adminToken = genToken('admin', 'admin-user');
const viewerToken = genToken('viewer', 'viewer-user');

async function run() {
  const api = await playwright.request.newContext();
  const scenarios = [
    { name: 'auth_401', expected: 401, headers: {}, url: `${apiUrl}/api/console/agents`, method: 'GET' },
    { name: 'auth_403', expected: 403, headers: { Authorization: `Bearer ${viewerToken}` }, url: `${apiUrl}/api/console/agents`, method: 'GET' },
    { name: 'auth_200', expected: 200, headers: { Authorization: `Bearer ${adminToken}` }, url: `${apiUrl}/api/console/agents`, method: 'GET' },
    { name: 'ingest_error', expected: null, headers: { Authorization: `Bearer ${adminToken}` }, url: `${apiUrl}/admin/ingestion/foo/run`, method: 'POST', body: { trigger_origin: 'sf4_g2' } },
  ];

  const results = [];
  for (const sc of scenarios) {
    const resp = await api.fetch(sc.url, { method: sc.method, headers: { ...sc.headers, 'x-request-id': reqId }, data: sc.body ? JSON.stringify(sc.body) : undefined });
    const status = resp.status();
    const ok = sc.expected ? status === sc.expected : status >= 400;
    results.push({ name: sc.name, status, ok });
    if (!ok) {
      throw new Error(`Scenario ${sc.name} expected ${sc.expected ?? '>=400'} got ${status}`);
    }
  }

  let uiError = null;
  try {
    const browser = await playwright.chromium.launch({ headless: true });
    const context = await browser.newContext({ extraHTTPHeaders: { Authorization: `Bearer ${adminToken}`, 'x-request-id': reqId } });
    const page = await context.newPage();
    await page.goto(uiUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.screenshot({ path: path.join(evidenceDir, `ui_happy_${reqId}.png`), fullPage: true });
    await page.goto(`${uiUrl}/admin/sources`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.screenshot({ path: path.join(evidenceDir, `ui_admin_sources_${reqId}.png`), fullPage: true });
    await browser.close();
  } catch (err) {
    uiError = err.message || String(err);
  }

  fs.writeFileSync(reportPath, JSON.stringify({ reqId, api: results, ui_error: uiError }, null, 2));
  if (uiError) {
    throw new Error(`UI smoke failed: ${uiError}`);
  }
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
NODE

log "[SF4_G2] Concluído; evidências em $EVIDENCE_DIR e $PLAYWRIGHT_EVIDENCE"

log "[SF4_G2] Concluído; evidências em $EVIDENCE_DIR e $PLAYWRIGHT_EVIDENCE"
