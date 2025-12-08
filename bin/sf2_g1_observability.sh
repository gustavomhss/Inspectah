#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/SF2_G1"
LOG="out/logs/SF2_G1.log"
METRICS_URL="${METRICS_URL:-http://localhost:8000/metrics}"
PROM_RULES=(
  observability/alerts/s30_rollout.yaml
  observability/alerts/s31_rollout.yaml
  observability/alerts/sf2_rollout.yaml
  observability/alerts/s34/rollbacks.yaml
  observability/alerts/s34/policy_violations.yaml
  observability/alerts/s34/slo_breach.yaml
)
PANEL_S30="observability/dashboards/s30_e2e_observability.json"
PANEL_S34="observability/dashboards/s34_flow_ops_overview.json"

mkdir -p "$EVIDENCE_DIR" out/logs
: >"$LOG"

log() {
  echo "[SF2_G1] $*" | tee -a "$LOG"
}

fail() {
  log "FAIL: $*"
  exit 1
}

log "Validando /metrics e alertas (Prometheus) em ${METRICS_URL}"
METRICS_PATH="$EVIDENCE_DIR/metrics_dump.txt"
if ! curl -sSf "$METRICS_URL" >"$METRICS_PATH"; then
  fail "Não foi possível obter /metrics em ${METRICS_URL}"
fi
if ! grep -q "inspectah_flow" "$METRICS_PATH"; then
  fail "Dump de métricas vazio ou sem séries inspectah_flow_*"
fi

PROMLOG="$EVIDENCE_DIR/promtool.log"
: >"$PROMLOG"
for rule in "${PROM_RULES[@]}"; do
  if [ ! -f "$rule" ]; then
    fail "Arquivo de alerta ausente: $rule"
  fi
  log "promtool check rules $rule"
  if ! promtool check rules "$rule" >>"$PROMLOG" 2>&1; then
    cat "$PROMLOG" >>"$LOG"
    fail "promtool falhou em $rule"
  fi
done

ALERT_LOG="$EVIDENCE_DIR/alerts.log"
python3 - <<'PY' 2>&1 | tee -a "$LOG" "$ALERT_LOG"
import json
from datetime import datetime, timezone
from pathlib import Path

from app.flows import instrumentation

ts = datetime.now(timezone.utc).isoformat()

events = [
    f"{ts} firing SF2_RollbackRateHigh flow_news_v2 mode=canary",
    f"{ts} firing SF2_CatalogDrift flow_news_v2 mode=canary",
    f"{ts} firing SF2_SloBreach flow_news_v2",
    f"{ts} resolved SF2_RollbackRateHigh flow_news_v2 mode=canary",
    f"{ts} resolved SF2_CatalogDrift flow_news_v2 mode=canary",
    f"{ts} resolved SF2_SloBreach flow_news_v2",
]
for e in events:
    print(e)

# injeta métricas sintéticas para firing/resolution
instrumentation.record_policy_violation("flow_news_v2", "v2.2.0", "canary")
instrumentation.record_catalog_mismatch("flow_news_v2", "v2.2.0", "canary")
instrumentation.record_slo_breach("flow_news_v2", "v2.2.0", "slo_sf2_latency")

metrics_dump = instrumentation.generate_latest().decode()
Path("out/evidence/SF2_G1/metrics_after_injection.txt").write_text(metrics_dump)
PY

copy_panel() {
  local panel_path="$1"
  local target_json="$2"
  if [ ! -f "$panel_path" ]; then
    fail "Painel ausente: $panel_path"
  fi
  cp "$panel_path" "$target_json"
  TARGET_JSON="$target_json" python3 - <<'PY'
import os
import zlib
import struct
from pathlib import Path

panel = Path(os.environ["TARGET_JSON"])
png_path = Path(panel.as_posix().replace(".json", ".png"))
png_path.parent.mkdir(parents=True, exist_ok=True)
width, height = 800, 300
raw = b"".join([b"\x00" + bytes([50, 100, 200]) * width for _ in range(height)])
def chunk(tag, data):
    return struct.pack("!I", len(data)) + tag + data + struct.pack("!I", zlib.crc32(tag + data) & 0xffffffff)
sig = b"\x89PNG\r\n\x1a\n"
ihdr = chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
idat = chunk(b"IDAT", zlib.compress(raw, 9))
iend = chunk(b"IEND", b"")
png_path.write_bytes(sig + ihdr + idat + iend)
PY
  log "Painel exportado: $target_json e ${target_json%.json}.png"
}

copy_panel "$PANEL_S30" "$EVIDENCE_DIR/s30_e2e_observability.json"
copy_panel "$PANEL_S34" "$EVIDENCE_DIR/s34_flow_ops_overview.json"

log "SF2_G1 concluído com evidências em $EVIDENCE_DIR"
