#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T6_observability"
SCORECARD="$OUT/scorecards/T6_observability.json"
SNAPSHOT="$EVID_DIR/metrics_snapshot.json"
rm -rf "$EVID_DIR"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
PYTHONPATH="src:${PYTHONPATH:-}"
export PYTHONPATH
python3 -m observability.metrics --output "$SNAPSHOT"
python3 - <<'PY' "$SNAPSHOT" "$SCORECARD"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
snapshot_path, scorecard_path = sys.argv[1:3]
metrics = json.loads(Path(snapshot_path).read_text(encoding='utf-8'))
required_keys = [
    'inspectah_sources_configured_total',
    'inspectah_field_resolution_success',
    'inspectah_dedup_violations_total',
    'inspectah_evidence_completeness_ratio',
    'inspectah_detection_latency_p95_ms',
    'inspectah_confidence_coverage_ratio'
]
missing = [key for key in required_keys if key not in metrics]
invalid = []
violations = 0
for key, value in metrics.items():
    if isinstance(value, (int, float)):
        if key.endswith('ratio') or key.endswith('rate') or key.endswith('success'):
            if not (0.0 <= value <= 1.0):
                invalid.append((key, value))
        if key.endswith('violations_total') or key.endswith('orphan_evidence_total'):
            if value != 0:
                violations += int(value)
        if 'latency' in key and value < 0:
            invalid.append((key, value))
status = 'PASS'
if missing or invalid or violations:
    status = 'FAIL'
scorecard = {
    'gate': 'T6',
    'name': 'observability',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': {
        'metrics_present_ratio': (len(required_keys) - len(missing)) / len(required_keys),
        'invalid_values_count': len(invalid),
        'violations_from_metrics': violations,
    },
    'thresholds': {
        'metrics_present_ratio': '== 1.0',
        'invalid_values_count': '== 0',
        'violations_from_metrics': '== 0'
    },
    'details': {
        'missing_keys': missing,
        'invalid_values': invalid,
        'snapshot_path': snapshot_path,
    }
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if status != 'PASS':
    sys.stderr.write('T6 observability gate failed\n')
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
echo "[T6] Observability gate PASS"
