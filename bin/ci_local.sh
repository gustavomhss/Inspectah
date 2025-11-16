#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/out/evidence/T7_ci"
REPORT="$OUT/ci_full_report.json"
SCORECARD="$ROOT/out/scorecards/T7_ci_full.json"
mkdir -p "$OUT" "$ROOT/out/scorecards"
SCRIPTS=(".ci/lint.sh" ".ci/tests.sh" ".ci/bench.sh" ".ci/release_check.sh")
STATUS=()
FAIL=0
for script in "${SCRIPTS[@]}"; do
  name="$(basename "$script")"
  set +e
  bash "$ROOT/$script"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then
    STATUS+=("$name:passed")
  else
    STATUS+=("$name:failed")
    FAIL=1
  fi
done
python3 - <<'PY' "$OUT" "$REPORT" "$SCORECARD" "${STATUS[@]}"
import json, sys
from pathlib import Path
out_dir = Path(sys.argv[1])
report_path = Path(sys.argv[2])
scorecard_path = Path(sys.argv[3])
statuses = sys.argv[4:]
entries = []
passed = True
for item in statuses:
    name, status = item.split(':')
    ok = status == 'passed'
    entries.append({'script': name, 'status': status})
    if not ok:
        passed = False
report = {'stages': entries, 'passed': passed}
report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
scorecard = {
    'gate': 'T7_CI',
    'version': '1.0',
    'passed': passed,
    'failures': [entry['script'] for entry in entries if entry['status'] != 'passed'],
    'notes': 'CI local executado'
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding='utf-8')
if not passed:
    sys.exit(1)
PY
if [ "$FAIL" -ne 0 ]; then
  exit 1
fi
