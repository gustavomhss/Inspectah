#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T4_golden"
mkdir -p "$OUT"
python3 - <<'PY' "$ROOT" "$OUT"
import json
import sys
import re
from pathlib import Path

def normalize(text: str) -> list[str]:
    tokens = re.sub(r'[^a-z0-9]+', ' ', text.lower()).split()
    return [tok for tok in tokens if tok]

def build_index(cases: dict[str, str]) -> dict[str, set[str]]:
    index: dict[str, set[str]] = {}
    for item_id, text in cases.items():
        for token in set(normalize(text)):
            index.setdefault(token, set()).add(item_id)
    return index

def search(index: dict[str, set[str]], query: str) -> list[str]:
    tokens = normalize(query)
    if not tokens:
        return []
    matches = index.get(tokens[0], set()).copy()
    for token in tokens[1:]:
        matches &= index.get(token, set())
    return sorted(matches)

root = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
cases: dict[str, str] = {}
for path in root.glob('tests/goldens/rss/*_expected.json'):
    data = json.loads(path.read_text())
    text = data['fields']['title'] + ' ' + data['fields'].get('description', '')
    cases[path.stem] = text
for path in root.glob('tests/goldens/api/*_expected.json'):
    data = json.loads(path.read_text())
    cases[path.stem] = data['fields']['title']

index = build_index(cases)
queries = {term: search(index, term) for term in ['alpha','beta','gamma','delta','zeta']}
(out_dir / 'fts_smoke.json').write_text(json.dumps(queries, indent=2), encoding='utf-8')
(out_dir / 'fts_index_dump.json').write_text(json.dumps({k: sorted(list(v)) for k, v in index.items()}, indent=2), encoding='utf-8')
PY
echo "FTS smoke completed."
