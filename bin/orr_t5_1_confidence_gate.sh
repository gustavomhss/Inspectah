#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T5_1_confidence"
SCORECARD="$OUT/scorecards/T5_1_confidence.json"
REPORT="$EVID_DIR/audit_report.json"
rm -rf "$EVID_DIR"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
TMP_DB="$(mktemp "${TMPDIR:-/tmp}/inspectah_t5_1_XXXXXX")"
trap 'rm -f "$TMP_DB"' EXIT
export INSPECTAH_DB_PATH="$TMP_DB"
PYTHONPATH="src:${PYTHONPATH:-}"
export PYTHONPATH
CALIB_DATA="$EVID_DIR/calibration_dataset.json"
python3 -m confidence_engine.audit_runner --config-dir "configs/sources" --db-path "$TMP_DB" --report "$REPORT" --calibration "$CALIB_DATA"
python3 - <<'PY' "$REPORT" "$SCORECARD"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
report_path, scorecard_path = sys.argv[1:3]
report = json.loads(Path(report_path).read_text(encoding='utf-8'))
coverage = float(report.get('coverage', 0.0))
monotonic = float(report.get('monotonicity_ok_rate', 0.0))
low_sat = float(report.get('score_saturation_low', 0.0))
high_sat = float(report.get('score_saturation_high', 0.0))
status = 'PASS'
if coverage < 0.95 or monotonic < 0.9 or low_sat > 0.5 or high_sat > 0.5:
    status = 'FAIL'
scorecard = {
    'gate': 'T5.1',
    'name': 'confidence_engine',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': {
        'coverage': coverage,
        'monotonicity_ok_rate': monotonic,
        'score_saturation_low': low_sat,
        'score_saturation_high': high_sat,
    },
    'thresholds': {
        'coverage': '>= 0.95',
        'monotonicity_ok_rate': '>= 0.90',
        'score_saturation_low': '<= 0.5',
        'score_saturation_high': '<= 0.5'
    },
    'details': report,
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if status != 'PASS':
    sys.stderr.write('T5.1 confidence engine failed\n')
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
echo "[T5.1] Confidence gate PASS"
