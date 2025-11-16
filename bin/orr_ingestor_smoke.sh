#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ORR_OUTDIR:-$ROOT/out}"
EVID_DIR="$OUT_DIR/evidence/T3_property"
mkdir -p "$EVID_DIR"
python3 "$ROOT/services/ingestor/ingestor.py"
python3 - <<'PY' "$EVID_DIR"
import json, sys, time
from pathlib import Path
root = Path(sys.argv[1])
series = json.loads((root / 'series_ingest.json').read_text())
report = {
    'ingestor_cycle_completed': True,
    'metrics': series,
    'timestamp': time.time()
}
(root / 'ingestor_smoke.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
PY
echo "Ingestor smoke completed. Evidence written to $EVID_DIR"
