#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T4_golden"
mkdir -p "$EVID_DIR"
python3 - <<'PY' "$ROOT" "$EVID_DIR"
import json
import sys
import importlib.util
from pathlib import Path
import sys
root = Path(sys.argv[1])
evid_dir = Path(sys.argv[2])
module_path = root / 'services/fts/fts.py'
spec = importlib.util.spec_from_file_location('fts', module_path)
fts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fts)  # type: ignore

docs = {}
for path in root.glob('tests/goldens/rss/*_expected.json'):
    data = json.loads(path.read_text())
    text = data['fields']['title'] + ' ' + data['fields'].get('description', '')
    docs[path.stem] = text
for path in root.glob('tests/goldens/api/*_expected.json'):
    data = json.loads(path.read_text())
    docs[path.stem] = data['fields']['title']

index = fts.build_index(docs)
fts.save_index(index)
queries = {term: fts.search(term) for term in ['alpha','beta','gamma','delta','zeta']}
(evid_dir / 'fts_smoke.json').write_text(json.dumps(queries, indent=2), encoding='utf-8')
(evid_dir / 'fts_index_dump.json').write_text(json.dumps({k: sorted(list(v)) for k, v in index.items()}, indent=2), encoding='utf-8')
PY
echo "FTS smoke completed. Outputs written to $EVID_DIR"
