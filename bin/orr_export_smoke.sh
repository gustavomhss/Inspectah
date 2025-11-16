#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T4_golden"
mkdir -p "$OUT"
python3 - <<'PY' "$ROOT" "$OUT"
import csv
import json
import sys
from pathlib import Path
root = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
items = []
for expected_path in sorted(root.glob('tests/goldens/rss/*_expected.json')):
    data = json.loads(expected_path.read_text())
    items.append({
        'item_id': data['item_id'],
        'source_id': data['source_id'],
        'title': data['fields'].get('title', ''),
        'event_time': data['event_time']
    })
for expected_path in sorted(root.glob('tests/goldens/api/*_expected.json')):
    data = json.loads(expected_path.read_text())
    items.append({
        'item_id': data['item_id'],
        'source_id': data['source_id'],
        'title': data['fields'].get('title', ''),
        'event_time': data['event_time']
    })
items.sort(key=lambda item: (item['source_id'], item['event_time'], item['item_id']))
(out_dir / 'export_smoke.json').write_text(json.dumps({'rows': items, 'count': len(items)}, indent=2), encoding='utf-8')
with (out_dir / 'export_smoke.csv').open('w', newline='', encoding='utf-8') as fh:
    writer = csv.DictWriter(fh, fieldnames=['item_id','source_id','title','event_time'])
    writer.writeheader()
    for row in items:
        writer.writerow(row)
PY
echo "Export smoke completed."
