#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T5_bench"
SCORECARD="$OUT_DIR/scorecards/T5_bench.json"
mkdir -p "$EVID_DIR" "$OUT_DIR/scorecards"

python3 "$ROOT/scripts/bench_runner.py" --raw "$EVID_DIR/bench_raw.json" --series "$EVID_DIR/series_latency.json"
python3 - <<'PY' "$EVID_DIR" "$SCORECARD"
import json, sys
from pathlib import Path
root, scorecard_path = Path(sys.argv[1]), Path(sys.argv[2])
raw = json.loads((root / 'bench_raw.json').read_text())
summary = {}
passed = True
for scenario, ops in raw.items():
    for op, stats in ops.items():
        if stats['p95'] > 200 or stats['p99'] > 400:
            passed = False
        summary.setdefault(scenario, {})[op] = {'p95': stats['p95'], 'p99': stats['p99']}
(root / 'bench_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
scorecard = {
    'gate': 'T5',
    'version': '1.0',
    'passed': passed,
    'failures': [] if passed else ['latency-slo-failed'],
    'notes': 'Bench completed'
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if not passed:
    raise SystemExit('T5 SLO failed')
PY

echo "T5 gate passed."
