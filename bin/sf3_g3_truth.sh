#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF3_G3"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF3_G3.log"
API_URL="${API_URL:-http://127.0.0.1:8000}"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF3_G3][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

FLOW_LOG="$EVIDENCE_DIR/truth_flow.log"
NEG_LOG="$EVIDENCE_DIR/truth_negative_tests.log"
METRICS_OUT="$EVIDENCE_DIR/truth_metrics.txt"

log "[SF3_G3] Exercitando state machine truth/promotion"

TRUTH_TOKEN=$(ROLE=truth_admin ACTOR=truth-admin AUD=inspectah-api ISS=inspectah-idp "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/sf3_jwt_gen.py")

# Caminho válido
curl -s -H "Authorization: Bearer $TRUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$API_URL/api/truth/promotion" \
  -d '{"claim_id":"c-123","current_state":"PENDING","target_state":"UNDER_REVIEW","justification":"ok","hash_manifest":"abcd","claim_type":"news"}' \
  | tee "$FLOW_LOG"

# Caminho inválido
status=$(curl -s -o "$NEG_LOG" -w "%{http_code}" \
  -H "Authorization: Bearer $TRUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -X POST "$API_URL/api/truth/promotion/invalid" \
  -d '{"claim_id":"c-123","current_state":"PENDING","target_state":"forbidden"}')
echo "status:$status" >>"$NEG_LOG"
if [ "$status" = "200" ]; then
  fail "Transição inválida não falhou"
fi

curl -s "$API_URL/metrics" >"$METRICS_OUT" || fail "Não foi possível obter /metrics"
grep -q "truth_promotion_transitions_total" "$METRICS_OUT" || fail "Métrica truth_promotion_transitions_total ausente"
grep -q "truth_promotion_failures_total" "$METRICS_OUT" || fail "Métrica truth_promotion_failures_total ausente"

log "[SF3_G3] Evidências em $EVIDENCE_DIR"
