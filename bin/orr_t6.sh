#!/usr/bin/env bash
set -euo pipefail
OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi
EVID_DIR="$OUT/evidence/T6_ci"
SCORECARD="$OUT/scorecards/T6_ci.json"
mkdir -p "$EVID_DIR" "$OUT/scorecards"
START=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
python3 - <<'PY2' "$EVID_DIR/summary.json"
import json
import sys
from pathlib import Path
summary_path = Path(sys.argv[1])
scorecards = [
    Path('out/scorecards/T0_spec.json'),
    Path('out/scorecards/T1_structure.json'),
    Path('out/scorecards/T2_unit.json'),
    Path('out/scorecards/T3_contract.json'),
    Path('out/scorecards/T4_golden.json'),
    Path('out/scorecards/T5_metrics.json'),
    Path('out/scorecards/D8_ci.json'),
]
results = []
for path in scorecards:
    if not path.exists():
        raise SystemExit(f"missing scorecard {path}")
    data = json.loads(path.read_text())
    passed = bool(data.get('passed'))
    results.append({"path": path.as_posix(), "passed": passed})
    if not passed:
        raise SystemExit(f"gate failed: {path}")
summary_path.write_text(json.dumps({"gates": results}, indent=2), encoding='utf-8')
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
    'gate': 'T6_ci',
    'version': '1.0',
    'started_at': started,
    'finished_at': finished,
    'passed': True,
    'failures': [],
    'metrics': {},
    'artifacts': artifacts,
    'notes': 'aggregate readiness',
}
Path(scorecard_path).write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
PY4
