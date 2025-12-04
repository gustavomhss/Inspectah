#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/evidence/S30_G4_flow_observability"
SCORECARD="$ROOT_DIR/out/scorecards/S30_G4_flow_observability.json"

mkdir -p "$LOG_DIR"
STATUS="PASS"
REASONS=()

echo "[s30-g4] Executando fluxo para coletar métricas/logs" | tee "$LOG_DIR/g4.log"

python3 - <<'PY' 2>"$LOG_DIR/g4_error.log"
import json
import logging
from pathlib import Path
from app.flows.dispatcher import dispatch_file
from app.flows import instrumentation

LOG_FILE = Path("out/evidence/S30_G4_flow_observability/g4_flow_logs.jsonl")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

class JsonHandler(logging.Handler):
    def emit(self, record):
        data = record.__dict__.copy()
        for k in list(data.keys()):
            if k.startswith("_") or k in ("msg", "args"):
                data.pop(k, None)
        data["message"] = record.getMessage()
        with LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(data) + "\n")

handler = JsonHandler()
logger = logging.getLogger("flows.instrumentation")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

exec_ids = dispatch_file("tests/data/s30_e2e_news_sample.jsonl")
metrics_bytes = instrumentation.generate_latest() if hasattr(instrumentation, "generate_latest") else b""
metrics_text = metrics_bytes.decode("utf-8") if isinstance(metrics_bytes, (bytes, bytearray)) else str(metrics_bytes)
Path("out/evidence/S30_G4_flow_observability/g4_prometheus_scrape.txt").write_text(metrics_text)
Path("out/evidence/S30_G4_flow_observability/g4_exec_ids.json").write_text(json.dumps(exec_ids, indent=2))
PY

if [ -f "$LOG_DIR/g4_error.log" ] && [ -s "$LOG_DIR/g4_error.log" ]; then
  STATUS="FAIL"
  REASONS+=("Erros ao coletar métricas/logs, veja g4_error.log")
fi

REASONS_JSON=$(printf '%s\n' "${REASONS[@]:-}" | python3 -c "import sys,json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")

echo "{ \"gate\": \"S30_G4_flow_observability\", \"status\": \"${STATUS}\", \"reasons\": ${REASONS_JSON} }" > "$SCORECARD"
echo "[s30-g4] status=$STATUS scorecard=$SCORECARD"
exit 0
