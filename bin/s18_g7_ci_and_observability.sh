#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G7_ci_and_observability"
SCORECARD_PATH="$SCORECARD_DIR/S18_G7_ci_and_observability.json"
WORKFLOW_PATH="$ROOT_DIR/.github/workflows/_s18_admin_front.yml"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
details="Workflow verificado."

if [[ ! -f "$WORKFLOW_PATH" ]]; then
  status="FAIL"
  details="Workflow _s18_admin_front.yml não encontrado."
else
  cp "$WORKFLOW_PATH" "$EVIDENCE_DIR/workflow.yml"
  if ! rg -q "s18_g3_front_quality" "$WORKFLOW_PATH"; then
    status="FAIL"
    details="Workflow não executa s18_g3_front_quality.sh"
  fi
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$details"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
status = sys.argv[2]
details = sys.argv[3]
scorecard = {
    "gate_id": "S18_G7",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {"note": details},
}
path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit(f"[S18_G7] {details}")
PY

echo "[S18_G7] OK - scorecard em $SCORECARD_PATH"
