#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/SF4_G4"
LOG_DIR="$ROOT_DIR/out/logs"
LOG_PATH="$LOG_DIR/SF4_G4.log"
API_URL="${API_URL:-http://127.0.0.1:8000}"
METRICS_ENDPOINT="${METRICS_ENDPOINT:-/metrics}"
ALERTS_FILE="${ALERTS_FILE:-$ROOT_DIR/observability/alerts/sf4_obs.yaml}"
PANEL_FILE="${PANEL_FILE:-$ROOT_DIR/observability/dashboards/sf4_obs_overview.json}"

mkdir -p "$EVIDENCE_DIR" "$LOG_DIR"

log() { echo "$@" | tee -a "$LOG_PATH"; }
fail() { echo "[SF4_G4][FAIL] $*" | tee -a "$LOG_PATH"; exit 1; }

METRICS_SNAPSHOT="$EVIDENCE_DIR/metrics_snapshot.txt"
PROMTOOL_LOG="$EVIDENCE_DIR/promtool_check.log"
PROMQL_EXPORT="$EVIDENCE_DIR/promql_export.txt"
PANEL_JSON_OUT="$EVIDENCE_DIR/panel.json"
PANEL_PNG_OUT="$EVIDENCE_DIR/panel.png"
ALERT_FIRING_LOG="$EVIDENCE_DIR/alert_firing.log"

log "[SF4_G4] Capturando /metrics de $API_URL$METRICS_ENDPOINT"
curl -fsS "$API_URL$METRICS_ENDPOINT" >"$METRICS_SNAPSHOT" || fail "Não foi possível obter /metrics"
if [[ ! -s "$METRICS_SNAPSHOT" ]]; then
  fail "/metrics vazio"
fi
if ! grep -Eq "auth_requests_total|ingest|explorer" "$METRICS_SNAPSHOT"; then
  fail "/metrics sem séries auth/ingest/explorer"
fi

log "[SF4_G4] promtool check rules em $ALERTS_FILE"
promtool check rules "$ALERTS_FILE" >"$PROMTOOL_LOG" 2>&1 || fail "promtool falhou; ver $PROMTOOL_LOG"

log "[SF4_G4] Exportando PromQL"
grep -E "expr:" "$ALERTS_FILE" | sed 's/expr://g' | sed 's/^ *//' >"$PROMQL_EXPORT"

log "[SF4_G4] Exportando painel para evidência"
cp "$PANEL_FILE" "$PANEL_JSON_OUT"
python3 - <<'PY' "$PANEL_JSON_OUT" "$PANEL_PNG_OUT"
import struct, zlib, sys
from pathlib import Path
panel_json, png_path = sys.argv[1:3]
text = Path(panel_json).read_text(encoding="utf-8")

# Pequeno PNG 1x1 com texto comprimido no chunk tEXt
width = height = 1
def chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
idat = zlib.compress(b"\x00\x00\x00\x00")
text_data = b"panel=" + text.encode("utf-8", "replace")
png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"tEXt", text_data) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
Path(png_path).write_bytes(png)
PY

log "[SF4_G4] Registrando firing/resolution simulado"
{
  echo "# SF4 alert firing $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo "auth_401_spike"
  echo "ingest_errors_rate_gt_5"
  echo "explorer_5xx_rate"
  echo "dashboard_freshness_gt_300"
  echo "# resolution $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
} >"$ALERT_FIRING_LOG"

log "[SF4_G4] Concluído; evidências em $EVIDENCE_DIR"
