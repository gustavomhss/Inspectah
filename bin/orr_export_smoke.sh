#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T4_golden"
mkdir -p "$EVID_DIR"
INPUTS=("$ROOT"/tests/goldens/rss/*_expected.json "$ROOT"/tests/goldens/api/*_expected.json)
python3 "$ROOT/scripts/exporter.py" --inputs "${INPUTS[@]}" --json-out "$EVID_DIR/export.json" --csv-out "$EVID_DIR/export.csv"
python3 - <<'PY' "$EVID_DIR"
import json, csv, sys
from pathlib import Path
root = Path(sys.argv[1])
data = json.loads((root / 'export.json').read_text())
rows = sum(1 for _ in (root / 'export.csv').open()) - 1
(root / 'export_smoke.json').write_text(json.dumps({"json_items": len(data), "csv_rows": rows}, indent=2), encoding='utf-8')
PY
echo "Export smoke completed. Files at $EVID_DIR"
