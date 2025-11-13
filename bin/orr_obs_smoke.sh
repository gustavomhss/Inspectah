#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/services/obs/metrics.py"
python3 "$ROOT/services/obs/logs.py"
python3 "$ROOT/services/obs/traces.py"
python3 - <<'PY' "$ROOT"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
obs_dir = root / 'out/evidence/T6_obs'
report = {
    'metrics_present': (obs_dir / 'metrics.json').exists(),
    'logs_present': (obs_dir / 'logs.json').exists(),
    'traces_present': (obs_dir / 'traces.json').exists()
}
(obs_dir / 'smoke.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
PY
echo "Observability smoke completed."
