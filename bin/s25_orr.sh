#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_ORR"
SCORECARD_PATH="$SCORECARD_DIR/S25_ORR_summary.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"

gates=($(ls "$SCORECARD_DIR"/S25_G*.json 2>/dev/null || true))
total=${#gates[@]}
fail=0
details=()

for card in "${gates[@]}"; do
  status=$(python3 - <<'PY' "$card"
import json, sys
data=json.load(open(sys.argv[1]))
print(data.get("status","NO_GO"))
PY
)
  details+=("$(basename "$card"):$status")
  if [[ "$status" != "GO" ]]; then
    fail=$((fail+1))
  fi
done

overall="GO"
if [[ $fail -gt 0 ]]; then
  overall="GO_WITH_RISKS"
fi

cat >"$SCORECARD_PATH" <<JSON
{
  "gate_id": "S25_G8",
  "gate_name": "orr_summary",
  "sprint": "S25",
  "status": "$overall",
  "timestamp": "$ts",
  "commit_sha": "$git_commit",
  "metrics": {
    "gates_total": $total,
    "gates_with_risk": $fail
  },
  "gates": ${details[@]+"\"${details[*]}\""},
  "risks": [],
  "notes": "Detalhes em $EVIDENCE_DIR/orr.log"
}
JSON

{
  echo "S25 ORR - $ts"
  echo "Total de gates: $total, com risco: $fail"
  printf '%s\n' "${details[@]}"
} >"$EVIDENCE_DIR/orr.log"

echo "[S25_G8] ORR gerado em $SCORECARD_PATH"
