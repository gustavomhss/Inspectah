#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G7_go_no_go"
SCORECARD_PATH="$SCORECARDS_DIR/S20_G7_go_no_go.json"

mkdir -p "$SCORECARDS_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"

declare -A paths=(
  ["S20_G0"]="$SCORECARDS_DIR/S20_G0_scope_and_baseline.json"
  ["S20_G1"]="$SCORECARDS_DIR/S20_G1_frontend_build_and_sanity.json"
  ["S20_G2"]="$SCORECARDS_DIR/S20_G2_ux_and_navigation.json"
  ["S20_G3"]="$SCORECARDS_DIR/S20_G3_responsiveness_and_basic_accessibility.json"
  ["S20_G4"]="$SCORECARDS_DIR/S20_G4_auth_and_protected_routes.json"
  ["S20_G5"]="$SCORECARDS_DIR/S20_G5_frontend_observability.json"
  ["S20_G6"]="$SCORECARDS_DIR/S20_G6_demo_internal_use_and_truth_states.json"
)

missing=()
declare -A statuses
declare -A metrics

for gate in "${!paths[@]}"; do
  path="${paths[$gate]}"
  if [[ -f "$path" ]]; then
    status=$(jq -r '.status // .decision // "MISSING"' "$path")
    statuses["$gate"]="$status"
    m=$(jq -r '.metrics // {}' "$path")
    metrics["$gate"]="$m"
  else
    statuses["$gate"]="MISSING"
    missing+=("$gate")
  fi
done

all_pass=true
for gate in "${!statuses[@]}"; do
  if [[ "${statuses[$gate]}" != "PASS" ]]; then
    all_pass=false
  fi
done

decision="NO_GO"
if $all_pass; then
  decision="GO"
fi

summary=$(cat <<EOF
{
  "gates": {
    "S20_G0": "${statuses[S20_G0]}",
    "S20_G1": "${statuses[S20_G1]}",
    "S20_G2": "${statuses[S20_G2]}",
    "S20_G3": "${statuses[S20_G3]}",
    "S20_G4": "${statuses[S20_G4]}",
    "S20_G5": "${statuses[S20_G5]}",
    "S20_G6": "${statuses[S20_G6]}"
  }
}
EOF
)

python3 - <<'PY' "$SCORECARD_PATH" "$decision" "$summary" "$commit_sha" "${paths[S20_G1]}" "${paths[S20_G2]}" "${paths[S20_G3]}" "${paths[S20_G4]}" "${paths[S20_G5]}" "${paths[S20_G6]}"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
decision = sys.argv[2]
summary = json.loads(sys.argv[3])
commit_sha = sys.argv[4]
g1 = Path(sys.argv[5])
g2 = Path(sys.argv[6])
g3 = Path(sys.argv[7])
g4 = Path(sys.argv[8])
g5 = Path(sys.argv[9])
g6 = Path(sys.argv[10])

def metric(path, key):
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return (data.get("metrics") or {}).get(key)
    except Exception:
        return None

scorecard = {
    "gate_id": "S20_G7_go_no_go",
    "decision": decision,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "gates": summary["gates"],
    "metrics": {
        "M1": metric(g1, "M1"),
        "M2": metric(g2, "M2"),
        "M3": metric(g3, "M3"),
        "M4": metric(g4, "M4"),
        "M5": metric(g5, "M5"),
        "M6": metric(g6, "M6"),
        "M7": metric(g6, "M7"),
    },
    "details": {
        "commit": commit_sha
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

echo "$summary" > "$EVIDENCE_DIR/summary.json"
cat > "$EVIDENCE_DIR/MANIFEST.json" <<EOF
{
  "scorecards": [
    "out/scorecards/S20_G0_scope_and_baseline.json",
    "out/scorecards/S20_G1_frontend_build_and_sanity.json",
    "out/scorecards/S20_G2_ux_and_navigation.json",
    "out/scorecards/S20_G3_responsiveness_and_basic_accessibility.json",
    "out/scorecards/S20_G4_auth_and_protected_routes.json",
    "out/scorecards/S20_G5_frontend_observability.json",
    "out/scorecards/S20_G6_demo_internal_use_and_truth_states.json"
  ]
}
EOF

if [[ "$decision" != "GO" ]]; then
  echo "[S20_G7] NO_GO - verifique scorecards anteriores."
  exit 1
fi

echo "[S20_G7] GO - scorecard em $SCORECARD_PATH"
