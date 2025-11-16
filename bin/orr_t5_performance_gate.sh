#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T5_performance"
SCORECARD="$OUT/scorecards/T5_performance.json"
REPORT="$EVID_DIR/perf_report.json"
rm -rf "$EVID_DIR"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
TMP_DB="$(mktemp "${TMPDIR:-/tmp}/inspectah_t5_XXXXXX")"
trap 'rm -f "$TMP_DB"' EXIT
export INSPECTAH_DB_PATH="$TMP_DB"
PYTHONPATH="src:${PYTHONPATH:-}"
export PYTHONPATH
python3 -m observability.perf_runner --config-dir "configs/sources" --db-path "$TMP_DB" --report "$REPORT" --ingest-iterations 6 --query-rounds 5 --field-runs 5
python3 - <<'PY' "$REPORT" "$SCORECARD"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
report_path, scorecard_path = sys.argv[1:3]
data = json.loads(Path(report_path).read_text(encoding='utf-8'))
summary = data.get('summary', {})
metrics = {
    'detection_latency_p95_ms': float(summary.get('detection_latency_p95_ms', 0.0)),
    'detection_latency_p99_ms': float(summary.get('detection_latency_p99_ms', 0.0)),
    'explore_query_p95_ms': float(summary.get('explore_query_p95_ms', 0.0)),
    'explore_query_p99_ms': float(summary.get('explore_query_p99_ms', 0.0)),
    'run_success_rate': float(summary.get('run_success_rate', 0.0)),
    'field_resolution_success_under_load': float(summary.get('field_resolution_success_under_load', 0.0)),
}
status = 'PASS'
if metrics['detection_latency_p95_ms'] > 800:
    status = 'FAIL'
if metrics['explore_query_p95_ms'] > 500 or metrics['explore_query_p99_ms'] > 1000:
    status = 'FAIL'
if metrics['run_success_rate'] < 0.99 or metrics['field_resolution_success_under_load'] < 0.95:
    status = 'FAIL'
scorecard = {
    'gate': 'T5',
    'name': 'performance',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': metrics,
    'thresholds': {
        'detection_latency_p95_ms': '<= 800',
        'explore_query_p95_ms': '<= 500',
        'explore_query_p99_ms': '<= 1000',
        'run_success_rate': '>= 0.99',
        'field_resolution_success_under_load': '>= 0.95',
    },
    'details': {
        'runs_executed': data.get('runs_executed', 0),
        'queries_executed': data.get('queries_executed', 0),
        'field_resolution': data.get('field_resolution', {}),
    },
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if status != 'PASS':
    sys.stderr.write('T5 performance gate failed\n')
    raise SystemExit(1)
PY
python3 - <<'PY' "$EVID_DIR"
import hashlib
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
files = []
for path in sorted(root.rglob('*')):
    if path.is_file():
        files.append({
            'path': path.relative_to(root).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'bytes': path.stat().st_size,
        })
(root / 'MANIFEST.json').write_text(json.dumps({'files': files}, indent=2), encoding='utf-8')
PY
echo "[T5] Performance gate PASS"
