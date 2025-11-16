#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T3_pipeline_invariants"
SCORECARD="$OUT/scorecards/T3_pipeline_invariants.json"
REPORT="$EVID_DIR/pipeline_report.json"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
TMP_DB="$(mktemp "${TMPDIR:-/tmp}/inspectah_t3_XXXXXX.db")"
trap 'rm -f "$TMP_DB"' EXIT
PYTHONPATH="src:${PYTHONPATH:-}"
export PYTHONPATH
python3 -m watchers.pipeline_runner --config-dir "configs/sources" --db-path "$TMP_DB" --report "$REPORT"
python3 - <<'PY' "$REPORT" "$SCORECARD"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
report_path, scorecard_path = sys.argv[1:3]
data = json.loads(Path(report_path).read_text(encoding='utf-8'))
metrics = data.get('metrics', {})
dedup = int(metrics.get('dedup_violations', 0))
immutability = int(metrics.get('immutability_violations', 0))
lineage = int(metrics.get('lineage_violations', 0))
status = 'PASS'
if dedup != 0 or immutability != 0 or lineage != 0:
    status = 'FAIL'
scorecard = {
    'gate': 'T3',
    'name': 'pipeline_invariants',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': {
        'dedup_violations': dedup,
        'immutability_violations': immutability,
        'lineage_violations': lineage,
    },
    'thresholds': {
        'dedup_violations': '== 0',
        'immutability_violations': '== 0',
        'lineage_violations': '== 0',
    },
    'details': data.get('details', {}),
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if status != 'PASS':
    sys.stderr.write('T3 pipeline invariants failed\n')
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
echo "[T3] Pipeline invariants PASS"
