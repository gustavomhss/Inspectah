#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G5_metrics_obs.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G5_metrics_obs"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

OUTPUT_JSON="$EVIDENCE_DIR/metrics_snapshot.json"
if ! "$REPO_ROOT/bin/inspectah_metrics_snapshot.sh" "$DOMAIN" | tee "$OUTPUT_JSON"; then
  status="FAIL"
else
  status="PASS"
fi

"$PYTHON_BIN" - <<'PY' "$SCORECARD" "$status" "$OUTPUT_JSON"
import json, sys
scorecard_path, status, output_json = sys.argv[1:4]
try:
    data = json.load(open(output_json, encoding='utf-8'))
except FileNotFoundError:
    data = {"metrics": {}}
metrics = data.get('metrics', data)
json.dump({
    "gate": "S6_G5",
    "name": "metrics_observability",
    "status": status,
    "details": {
        "records_total": metrics.get('records_total'),
        "latency_minutes_p95": metrics.get('latency_minutes_p95'),
    },
}, open(scorecard_path, "w", encoding="utf-8"), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
