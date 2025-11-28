#!/usr/bin/env bash
set -euo pipefail

OUT="${ORR_OUTDIR:-out}"
if [[ "$OUT" != /* ]]; then
  OUT="$(pwd)/$OUT"
fi

SUMMARY_DIR="$OUT/evidence/T8_go_no_go"
SUMMARY_JSON="$SUMMARY_DIR/summary.json"
SCORECARD="$OUT/scorecards/T8_go_no_go.json"
T7_SCORECARD="out/scorecards/T7_orr_pipeline.json"
WRAP_DOC="docs/sprint_3_orr_summary.md"

rm -rf "$SUMMARY_DIR"
mkdir -p "$SUMMARY_DIR" "$OUT/scorecards"

if [[ ! -f "$T7_SCORECARD" ]]; then
  echo "Missing $T7_SCORECARD" >&2
  exit 1
fi
if [[ ! -f "$WRAP_DOC" ]]; then
  echo "Missing wrap doc $WRAP_DOC" >&2
  exit 1
fi

python3 - <<'PY' "$T7_SCORECARD" "$SUMMARY_JSON" "$WRAP_DOC"
import json
import sys
scorecard_path, summary_path, wrap_doc = sys.argv[1:4]
data = json.loads(Path(scorecard_path).read_text())
gates = data.get('details', {}).get('gates', [])
metrics = data.get('metrics', {})
summary = {
    'gates_total': metrics.get('gates_total', len(gates)),
    'gates_passed': metrics.get('gates_passed', sum(1 for gate in gates if gate.get('status') == 'PASS')),
    'gates_failed': metrics.get('gates_failed', sum(1 for gate in gates if gate.get('status') != 'PASS')),
    'gates': gates,
    't7_scorecard': scorecard_path,
    'wrap_doc': wrap_doc,
}
Path(summary_path).write_text(json.dumps(summary, indent=2), encoding='utf-8')
PY

python3 - <<'PY' "$SUMMARY_JSON" "$SCORECARD"
import hashlib
import json
import sys
from datetime import datetime, timezone
summary_path, scorecard_path = sys.argv[1:3]
summary = json.loads(open(summary_path).read())
failed = summary.get('gates_failed', 0) or 0
status = 'PASS' if failed == 0 else 'FAIL'
decision = 'GO' if failed == 0 else 'NO_GO'
scorecard = {
    'gate': 'T8',
    'name': 'go_no_go',
    'version': 'v1',
    'status': status,
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'metrics': {
        'gates_total': summary.get('gates_total'),
        'gates_passed': summary.get('gates_passed'),
        'gates_failed': summary.get('gates_failed'),
        'decision': decision,
    },
    'thresholds': {
        'gates_failed': '== 0',
    },
    'details': {
        't7_scorecard': summary.get('t7_scorecard'),
        'wrap_doc': summary.get('wrap_doc'),
        'gates': summary.get('gates', []),
    },
}
with open(scorecard_path, 'w', encoding='utf-8') as handle:
    json.dump(scorecard, handle, indent=2)
PY

python3 - <<'PY' "$SUMMARY_DIR"
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

if grep -q '"status": "FAIL"' "$SCORECARD"; then
  echo "[T8] Decision NO_GO"
  exit 1
fi

echo "[T8] Decision GO"
