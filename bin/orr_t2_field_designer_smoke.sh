#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T2_field_designer"
SCORECARD="$OUT/scorecards/T2_field_designer.json"
REPORT="$EVID_DIR/sources_report.json"
PYTHONPATH="src:${PYTHONPATH:-}"
export PYTHONPATH
SAMPLE_SIZE="${FIELD_DESIGNER_SAMPLE_SIZE:-5}"
rm -rf "$EVID_DIR"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
python3 -m field_designer.runner --all --sample-size "$SAMPLE_SIZE" --output "$REPORT" --evidence-dir "$EVID_DIR"
python3 - <<'PY' "$REPORT" "$SCORECARD"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
report_path, scorecard_path = sys.argv[1:3]
data = json.loads(Path(report_path).read_text(encoding='utf-8'))
sources = data.get('sources', {})
summary = data.get('summary', {})
sources_tested = summary.get('sources_tested', len(sources))
sources_passed = summary.get('sources_passed', sum(1 for d in sources.values() if d.get('ok')))
field_success = summary.get('field_resolution_success_test', 0.0)
status = 'PASS' if sources_passed >= 3 and field_success >= 0.95 else 'FAIL'
scorecard = {
    'gate': 'T2',
    'name': 'field_designer',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': {
        'sources_tested': sources_tested,
        'sources_passed': sources_passed,
        'field_resolution_success_test': field_success,
    },
    'thresholds': {
        'sources_passed_min': 3,
        'field_resolution_success_test': '>= 0.95',
    },
    'details': {
        'sources': sources,
    },
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if status != 'PASS':
    sys.stderr.write('T2 gate failed; inspect report for details\n')
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
echo "[T2] Field Designer smoke PASS"
