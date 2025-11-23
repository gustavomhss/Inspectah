#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G6_demo_internal_use_and_truth_states"
SCORECARD_PATH="$SCORECARD_DIR/S20_G6_demo_internal_use_and_truth_states.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
status="FAIL"
M6=0
M7=0

cat > "$EVIDENCE_DIR/README.md" <<'EOF'
# S20-G6 — Demo, uso interno & estados de verdade

Preencha este diretório com screenshots/notas da demo seguindo docs/sprint_20_demo_script.md.
M6 = fluidez da demo (0-1). M7 = exposição correta dos estados de verdade (0-1).
EOF

# Expect mandatory manual scores file
SCORES_FILE="$EVIDENCE_DIR/demo_scores.json"
if [[ -f "$SCORES_FILE" ]]; then
  M6=$(jq -r '.M6 // 0' "$SCORES_FILE")
  M7=$(jq -r '.M7 // 0' "$SCORES_FILE")
  if (( $(echo "$M6 >= 0.8" | bc -l) )) && (( $(echo "$M7 >= 0.9" | bc -l) )); then
    status="PASS"
  else
    status="FAIL"
  fi
else
  status="FAIL"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$M6" "$M7" "$commit_sha"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
M6 = float(sys.argv[3])
M7 = float(sys.argv[4])
commit_sha = sys.argv[5]

scorecard = {
    "gate_id": "S20_G6_demo_internal_use_and_truth_states",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M6": M6, "M7": M7},
    "details": {"commit": commit_sha},
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G6] FAIL - revise roteiro de demo e estados de verdade")
PY

echo "[S20_G6] Scorecard gerado em $SCORECARD_PATH"
