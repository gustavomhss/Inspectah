#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T4_evidence_vault"
SCORECARD="$OUT/scorecards/T4_evidence_vault.json"
REPORT="$EVID_DIR/evidence_report.json"
rm -rf "$EVID_DIR"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
TMP_DB="$(mktemp "${TMPDIR:-/tmp}/inspectah_t4_XXXXXX.db")"
trap 'rm -f "$TMP_DB"' EXIT
export INSPECTAH_DB_PATH="$TMP_DB"
PYTHONPATH="src:${PYTHONPATH:-}"
export PYTHONPATH
python3 -m evidence_vault.audit_runner --config-dir "configs/sources" --db-path "$TMP_DB" --report "$REPORT" --evidence-dir "$EVID_DIR"
python3 - <<'PY' "$REPORT" "$SCORECARD"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
report_path, scorecard_path = sys.argv[1:3]
data = json.loads(Path(report_path).read_text(encoding='utf-8'))
metrics = data.get('metrics', {})
completeness = float(metrics.get('evidence_completeness', 0.0))
hash_rate = float(metrics.get('evidence_hash_valid_rate', 0.0))
orphan = int(metrics.get('orphan_evidence', 0))
status = 'PASS'
if completeness < 0.99 or hash_rate < 0.99 or orphan != 0:
    status = 'FAIL'
scorecard = {
    'gate': 'T4',
    'name': 'evidence_vault',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': {
        'evidence_completeness': completeness,
        'evidence_hash_valid_rate': hash_rate,
        'orphan_evidence': orphan,
    },
    'thresholds': {
        'evidence_completeness': '>= 0.99',
        'evidence_hash_valid_rate': '>= 0.99',
        'orphan_evidence': '== 0',
    },
    'details': data.get('details', {}),
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if status != 'PASS':
    sys.stderr.write('T4 evidence vault failed\n')
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
echo "[T4] Evidence vault PASS"
