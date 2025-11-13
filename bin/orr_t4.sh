#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EVID_DIR="$ROOT/out/evidence/T4_golden"
SCORECARD="$ROOT/out/scorecards/T4_golden.json"
mkdir -p "$EVID_DIR" "$ROOT/out/scorecards"
"$ROOT/bin/orr_fts_smoke.sh"
"$ROOT/bin/orr_export_smoke.sh"
python3 "$ROOT/scripts/t4_validator.py" "$EVID_DIR/validator_report.json"
python3 "$ROOT/scripts/t4_reporter.py" "$EVID_DIR" "$SCORECARD"
echo "T4 gate passed."
