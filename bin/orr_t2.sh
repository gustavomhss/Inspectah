#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T2_unit"
SCORECARD="$OUT_DIR/scorecards/T2_unit.json"
mkdir -p "$EVID_DIR" "$OUT_DIR/scorecards"
FIELDS="$ROOT/tests/fixtures/unit/field_designer/example_fields.json"
PAYLOAD="$ROOT/tests/fixtures/unit/field_designer/example_payload.json"
OUTPUT="$EVID_DIR/field_designer_dryrun.json"
python3 "$ROOT/scripts/field_designer_validate.py" --fields "$FIELDS" --payload "$PAYLOAD" --out "$OUTPUT"
if ! jq -e . "$OUTPUT" >/dev/null; then
  printf '{"gate":"T2","version":"1.0","passed":false,"failures":["invalid-output"],"notes":"dry-run invalid"}' > "$SCORECARD"
  exit 1
fi
python3 - "$OUTPUT" "$EVID_DIR/MANIFEST.json" <<'PY'
import hashlib, json, os, sys
out, manifest = sys.argv[1:3]
files = []
for path in [out]:
    with open(path, 'rb') as fh:
        data = fh.read()
    files.append({
        'path': os.path.relpath(path, os.path.dirname(os.path.dirname(out))),
        'sha256': hashlib.sha256(data).hexdigest(),
        'bytes': len(data)
    })
with open(manifest, 'w', encoding='utf-8') as fh:
    json.dump({'files': files}, fh, indent=2)
PY
python3 - "$SCORECARD" <<'PY'
import datetime, json, sys
with open(sys.argv[1], 'w', encoding='utf-8') as fh:
    json.dump({
        'gate': 'T2',
        'version': '1.0',
        'started_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'finished_at': datetime.datetime.utcnow().isoformat() + 'Z',
        'passed': True,
        'failures': [],
        'metrics': {},
        'artifacts': [
            {'path': 'out/evidence/T2_unit/field_designer_dryrun.json'},
            {'path': 'out/evidence/T2_unit/MANIFEST.json'}
        ],
        'notes': 'field designer dry-run ok'
    }, fh, indent=2)
PY
echo "T2 passed. Field designer dry-run generated at $OUTPUT"
