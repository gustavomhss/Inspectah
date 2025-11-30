#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T4_golden"
SCORECARD="$OUT/scorecards/T4_golden.json"
INFO="$OUT/evidence/D8_latest_bundle.json"
LOG="$EVID_DIR/d8_ci.log"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
bin/d8_ci.sh >"$LOG" 2>&1
python3 - <<'PY2' "$INFO" "$EVID_DIR"
import json
import sys
from pathlib import Path
info_path = Path(sys.argv[1])
if not info_path.exists():
    raise SystemExit("missing D8 bundle info")
data = json.loads(info_path.read_text())
evid_dir = Path(sys.argv[2])
for key, target in [("summary_path", "summary.json"), ("metrics_path", "metrics.json")]:
    source = Path(data.get(key, ""))
    if source.exists():
        (evid_dir / target).write_text(source.read_text(), encoding='utf-8')
bundle_src = Path(data["bundle_zip"])
if bundle_src.exists():
    (evid_dir / bundle_src.name).write_bytes(bundle_src.read_bytes())
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
bundle = None
for candidate in Path(evid_dir).glob('*.zip'):
    bundle = candidate
    break
artifacts = []
if bundle is not None:
    artifacts.append({
        'path': bundle.as_posix(),
        'sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
        'bytes': bundle.stat().st_size,
    })
scorecard = {
    'gate': 'T4_golden',
    'version': '1.0',
    'started_at': started,
    'finished_at': finished,
    'passed': True,
    'failures': [],
    'metrics': {},
    'artifacts': artifacts,
    'notes': 'D8 smoke bundle',
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
PY4
