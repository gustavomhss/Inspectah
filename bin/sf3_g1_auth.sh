#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF3_G1"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF3_G1.log"
API_URL="${API_URL:-http://127.0.0.1:8000}"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF3_G1][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

HTTP_LOG="$EVIDENCE_DIR/auth_http.log"
NEG_LOG="$EVIDENCE_DIR/auth_negative_tests.log"
METRICS_OUT="$EVIDENCE_DIR/auth_metrics.txt"

log "[SF3_G1] Smoke auth/RBAC em $API_URL"

ADMIN_TOKEN=$(ROLE=admin ACTOR=admin-user AUD=inspectah-api ISS=inspectah-idp "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/sf3_jwt_gen.py")
VIEWER_TOKEN=$(ROLE=viewer ACTOR=test-user AUD=inspectah-api ISS=inspectah-idp "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/sf3_jwt_gen.py")

curl_check() {
  local desc="$1"; shift
  local expected="$1"; shift
  local status
  status=$(curl -s -o /tmp/sf3_tmp_response.json -w "%{http_code}" "$@")
  echo "== $desc ==" >>"$HTTP_LOG"
  echo "Request: $*" >>"$HTTP_LOG"
  echo "Status: $status" >>"$HTTP_LOG"
  cat /tmp/sf3_tmp_response.json >>"$HTTP_LOG"
  echo -e "\n" >>"$HTTP_LOG"
  if [ "$status" != "$expected" ]; then
    fail "$desc retornou $status, esperado $expected"
  fi
}

# 401 sem headers
curl_check "Sem token deve ser 401" "401" \
  -X GET "$API_URL/api/console/agents"

# 403 role errada
curl_check "Role errada deve ser 403" "403" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -X GET "$API_URL/api/console/agents"

# 200 role correta
curl_check "Role admin deve ser 200" "200" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -X GET "$API_URL/api/console/agents"

# Negativos adicionais
echo "== Negativos ==" >"$NEG_LOG"
status=$(curl -s -o /tmp/sf3_tmp_response.json -w "%{http_code}" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -X POST "$API_URL/admin/ingestion/foo/run" \
  -H "Content-Type: application/json" -d '{"trigger_origin":"sf3"}')
echo "POST /admin/ingestion/foo/run (admin) -> $status" >>"$NEG_LOG"
status=$(curl -s -o /tmp/sf3_tmp_response.json -w "%{http_code}" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -X POST "$API_URL/admin/ingestion/foo/run" \
  -H "Content-Type: application/json" -d '{"trigger_origin":"sf3"}')
echo "POST /admin/ingestion/foo/run (viewer) -> $status" >>"$NEG_LOG"
if [ "$status" = "200" ]; then
  fail "Rota protegida aceitou role inválida"
fi

# Métricas
curl -s "$API_URL/metrics" >"$METRICS_OUT" || fail "Não foi possível obter /metrics"
grep -q "auth_requests_total" "$METRICS_OUT" || fail "Métrica auth_requests_total ausente"

log "[SF3_G1] Evidências em $EVIDENCE_DIR"
