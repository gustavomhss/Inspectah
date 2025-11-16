#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T7_ci"
RAW="$OUT/bench_ci_raw.json"
SERIES="$OUT/bench_ci_series.json"
REPORT="$OUT/bench_ci_report.json"
mkdir -p "$OUT"
python3 "$ROOT/scripts/bench_runner.py" --raw "$RAW" --series "$SERIES"
python3 - <<'PY' "$RAW" "$REPORT"
from pathlib import Path
import json, sys
raw_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
raw = json.loads(raw_path.read_text())
passed = True
violations = []
for scenario, ops in raw.items():
    for op, stats in ops.items():
        if stats['p95'] > 200 or stats['p99'] > 400:
            passed = False
            violations.append({'scenario': scenario, 'operation': op, 'p95': stats['p95'], 'p99': stats['p99']})
report = {'passed': passed, 'violations': violations}
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
if not passed:
    sys.exit(1)
PY
