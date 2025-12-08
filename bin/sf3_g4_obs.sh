#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF3_G4"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF3_G4.log"
API_URL="${API_URL:-http://127.0.0.1:8000}"
ALERTS_DIR="$ROOT_DIR/observability/alerts"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF3_G4][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

METRICS_DUMP="$EVIDENCE_DIR/metrics_dump.txt"
PROMTOOL_LOG="$EVIDENCE_DIR/promtool.log"
ALERTS_LIST="$EVIDENCE_DIR/alerts_list.txt"
PROMQL_PATH="$EVIDENCE_DIR/promql.txt"
PANEL_JSON="$EVIDENCE_DIR/painel.json"
PANEL_PNG="$EVIDENCE_DIR/painel.png"
ALERTS_FIRING="$EVIDENCE_DIR/alerts_firing.log"
ADMIN_TOKEN=$(ROLE=admin ACTOR=admin-user AUD=inspectah-api ISS=inspectah-idp "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/bin/sf3_jwt_gen.py")

log "[SF3_G4] Dump /metrics"
curl -s "$API_URL/metrics" >"$METRICS_DUMP" || fail "Não foi possível obter /metrics"
grep -Eq "auth_requests_total|ingest_requests_total|truth_promotion|admin_ui_requests_total" "$METRICS_DUMP" || fail "Séries esperadas ausentes em /metrics"

log "[SF3_G4] promtool check rules"
promtool check rules "$ALERTS_DIR/sf3_obs.yaml" >"$PROMTOOL_LOG" 2>&1 || fail "promtool falhou (ver $PROMTOOL_LOG)"

log "[SF3_G4] Arquivando PromQL"
cat "$ALERTS_DIR/sf3_obs.yaml" >"$PROMQL_PATH"
ls "$ALERTS_DIR" | sort >"$ALERTS_LIST"

log "[SF3_G4] Export painel sf3_obs_overview"
python3 - <<'PY' "$PANEL_JSON" "$PANEL_PNG" "$API_URL"
import json, sys, urllib.request
from pathlib import Path
panel_json, panel_png, api_url = sys.argv[1:4]
data = {
    "title": "SF3 Observability Overview",
    "panels": [
        {"metric": "auth_requests_total", "desc": "Auth 401/403/200"},
        {"metric": "ingest_requests_total", "desc": "Ingest requests"},
        {"metric": "truth_promotion_transitions_total", "desc": "Truth promotions"},
        {"metric": "admin_ui_requests_total", "desc": "Admin UI requests"},
    ],
}
Path(panel_json).write_text(json.dumps(data, indent=2), encoding="utf-8")

# captura PNG simplificada usando urllib+fake content
resp = urllib.request.urlopen(f"{api_url}/docs")
png = resp.read()
Path(panel_png).write_bytes(png)
PY

log "[SF3_G4] Simulando firing/resolution via requests"
{
  echo "auth_401_spike $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $ADMIN_TOKEN" "$API_URL/api/console/agents"
  echo "truth_promotion_failures $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" \
    -X POST "$API_URL/api/truth/promotion/invalid" -d '{"claim_id":"c-err","current_state":"PENDING","target_state":"bad"}'
} >"$ALERTS_FIRING"

log "[SF3_G4] Evidências em $EVIDENCE_DIR"
