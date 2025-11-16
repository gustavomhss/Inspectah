#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T7_ready"
SCORECARD="$OUT/scorecards/T7_ready.json"
INFO="$OUT/evidence/D8_latest_bundle.json"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
bin/orr_t6.sh
python3 - <<'PY2' "$INFO" "$EVID_DIR/summary.json"
import json
import sys
from pathlib import Path
info_path = Path(sys.argv[1])
summary_path = Path(sys.argv[2])
if not info_path.exists():
    raise SystemExit('missing D8 bundle info')
data = json.loads(info_path.read_text())
summary = {
    'bundle_zip': data.get('bundle_zip'),
    'bundle_sha256': data.get('bundle_sha256'),
    'bundle_dir': data.get('bundle_dir'),
    'notes': 'Ready for D8 demo'
}
summary_path.write_text(json.dumps(summary, indent=2), encoding='utf-8')
PY2
python3 - <<'PY3' "$EVID_DIR"
import hashlib
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
files = []
for path in sorted(root.rglob('*')):
    if path.is_file():
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        files.append({"path": rel, "sha256": digest, "bytes": path.stat().st_size})
(root / 'MANIFEST.json').write_text(json.dumps({"files": files}, indent=2), encoding='utf-8')
PY3
FINISH=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 - <<'PY4' "$SCORECARD" "$EVID_DIR" "$START" "$FINISH"
import hashlib
import json
import sys
from pathlib import Path
scorecard_path, evid_dir, started, finished = sys.argv[1:5]
summary = Path(evid_dir) / 'summary.json'
artifacts = []
if summary.exists():
    artifacts.append({
        'path': summary.as_posix(),
        'sha256': hashlib.sha256(summary.read_bytes()).hexdigest(),
        'bytes': summary.stat().st_size,
    })
scorecard = {
    'gate': 'T7_ready',
    'version': '1.0',
    'started_at': started,
    'finished_at': finished,
    'passed': True,
    'failures': [],
    'metrics': {},
    'artifacts': artifacts,
    'notes': 'Ready for demo',
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
PY4
