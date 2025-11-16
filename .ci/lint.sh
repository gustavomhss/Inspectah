#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T7_ci"
REPORT="$OUT/lint_report.json"
mkdir -p "$OUT"
python3 - <<'PY' "$ROOT" "$REPORT"
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
report_path = Path(sys.argv[2])
checks = []
required_files = [root / 'README.md', root / 'Makefile', root / 'docs/dashboards/alarms.json']
missing = [str(path) for path in required_files if not path.exists()]
checks.append({'name': 'required_files', 'missing': missing})
dashboards_dir = root / 'docs/dashboards'
dash_results = []
for dash in sorted(dashboards_dir.glob('*.json')):
    try:
        json.loads(dash.read_text())
        dash_results.append({'file': str(dash), 'valid': True})
    except json.JSONDecodeError as exc:
        dash_results.append({'file': str(dash), 'valid': False, 'error': str(exc)})
checks.append({'name': 'dashboards', 'results': dash_results})
passed = not missing and all(entry.get('valid', True) for entry in dash_results)
report_path.write_text(json.dumps({'passed': passed, 'checks': checks}, indent=2), encoding='utf-8')
if not passed:
    sys.exit(1)
PY
