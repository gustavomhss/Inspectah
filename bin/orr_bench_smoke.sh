#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T5_bench"
mkdir -p "$EVID_DIR"
python3 "$ROOT/scripts/bench_runner.py" --raw "$EVID_DIR/bench_raw.json" --series "$EVID_DIR/series_latency.json"
python3 - <<'PY' "$EVID_DIR"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
raw = json.loads((root / 'bench_raw.json').read_text())
smoke = {scenario: stats['api_create']['p95'] for scenario, stats in raw.items()}
(root / 'bench_smoke.json').write_text(json.dumps(smoke, indent=2), encoding='utf-8')
PY
echo "Bench smoke completed."
