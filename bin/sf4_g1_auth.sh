#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF4_G1"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF4_G1.log"
API_URL="${API_URL:-http://127.0.0.1:8000}"
AUTH_ENDPOINT="${AUTH_ENDPOINT:-/api/console/agents}"
METRICS_ENDPOINT="${METRICS_ENDPOINT:-/metrics}"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF4_G1][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

HTTP_LOG="$EVIDENCE_DIR/auth_http.log"
AUTH_METRICS="$EVIDENCE_DIR/auth_metrics.txt"
METRICS_DUMP="$EVIDENCE_DIR/metrics_dump.txt"
PROMQL_AUTH="$EVIDENCE_DIR/promql_auth.txt"

: >"$HTTP_LOG"
: >"$AUTH_METRICS"
: >"$PROMQL_AUTH"

gen_token() {
  local role="$1"
  local actor="$2"
  ROLE="$role" ACTOR="$actor" AUD=inspectah-api ISS=inspectah-idp "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/sf3_jwt_gen.py"
}

ADMIN_TOKEN="$(gen_token admin admin-user)"
VIEWER_TOKEN="$(gen_token viewer viewer-user)"

curl_check() {
  local desc="$1"; shift
  local expected="$1"; shift
  local status
  status=$(curl -s -o /tmp/sf4_g1_resp.json -w "%{http_code}" "$@")
  {
    echo "== $desc =="
    echo "Request: $*"
    echo "Status: $status"
    cat /tmp/sf4_g1_resp.json
    echo
  } >>"$HTTP_LOG"
  if [[ "$status" != "$expected" ]]; then
    fail "$desc retornou $status, esperado $expected"
  fi
}

log "[SF4_G1] Smoke auth/RBAC em $API_URL$AUTH_ENDPOINT"

# 401 sem token
curl_check "Sem token deve ser 401" "401" \
  -X GET "$API_URL$AUTH_ENDPOINT"

# 403 role errada
curl_check "Role errada deve ser 403" "403" \
  -H "Authorization: Bearer $VIEWER_TOKEN" \
  -X GET "$API_URL$AUTH_ENDPOINT"

# 200 role correta
curl_check "Role admin deve ser 200" "200" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -X GET "$API_URL$AUTH_ENDPOINT"

log "[SF4_G1] Capturando métricas em $API_URL$METRICS_ENDPOINT"
curl -fsS "$API_URL$METRICS_ENDPOINT" >"$METRICS_DUMP" || fail "Não foi possível obter /metrics"
if [[ ! -s "$METRICS_DUMP" ]]; then
  fail "/metrics vazio"
fi
grep -E "auth_requests_total" "$METRICS_DUMP" >"$AUTH_METRICS" || fail "Métrica auth_requests_total ausente em /metrics"

cat >"$PROMQL_AUTH" <<'EOF'
sum by (code) (rate(auth_requests_total[5m]))
sum by (role,code) (rate(auth_requests_total[5m]))
histogram_quantile(0.9, sum by (le) (rate(auth_latency_seconds_bucket[5m])))
EOF

log "[SF4_G1] Concluído; evidências em $EVIDENCE_DIR"
