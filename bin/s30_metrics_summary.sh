#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
OUTPUT="$SCORECARDS_DIR/S30_metrics_summary.json"

mkdir -p "$SCORECARDS_DIR"

STATUS="PASS"
REASONS=()

for gate in G0 G1 G2 G3 G4 G5; do
  FILE="$SCORECARDS_DIR/S30_${gate}_*.json"
  if ! ls $FILE >/dev/null 2>&1; then
    STATUS="FAIL"
    REASONS+=("Scorecard do gate ${gate} ausente")
  fi
done

REASONS_JSON=$(printf '%s\n' "${REASONS[@]:-}" | python3 -c "import sys,json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")

cat > "$OUTPUT" <<JSON
{
  "sprint": "S30",
  "status": "$STATUS",
  "reasons": $REASONS_JSON
}
JSON

echo "[s30-metrics-summary] status=$STATUS output=$OUTPUT"
