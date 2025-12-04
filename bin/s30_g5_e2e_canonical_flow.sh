#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/evidence/S30_G5_e2e_canonical_flow"
SCORECARD="$ROOT_DIR/out/scorecards/S30_G5_e2e_canonical_flow.json"

mkdir -p "$LOG_DIR"
STATUS="PASS"

echo "[s30-g5] Executando cenário E2E canônico via dispatcher" | tee "$LOG_DIR/g5.log"

DATASET="tests/data/s30_e2e_news_sample.jsonl"

if ! python3 - <<'PY' 2>"$LOG_DIR/g5_error.log"
from app.flows.dispatcher import dispatch_file
exec_ids = dispatch_file("tests/data/s30_e2e_news_sample.jsonl")
from pathlib import Path
import json
out = {
    "flow": "fluxo_noticias_e2e",
    "dataset": "tests/data/s30_e2e_news_sample.jsonl",
    "executions": exec_ids,
}
Path("out/evidence/S30_G5_e2e_canonical_flow/e2e_result.json").write_text(json.dumps(out, indent=2))
PY
then
  STATUS="FAIL"
  echo "[s30-g5] erro ao executar E2E" | tee -a "$LOG_DIR/g5.log"
fi

cat > "$SCORECARD" <<JSON
{
  "gate": "S30_G5_e2e_canonical_flow",
  "status": "$STATUS",
  "reasons": []
}
JSON

echo "[s30-g5] status=$STATUS scorecard=$SCORECARD"
exit 0
