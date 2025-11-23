#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G7_ci_and_observability"
SCORECARD_PATH="$SCORECARD_DIR/S19_G7_ci_and_observability.json"
WORKFLOW_PATH="$ROOT_DIR/.github/workflows/_s19_timeline_xray.yml"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$WORKFLOW_PATH" "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

workflow_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])

exists = workflow_path.exists()
content = workflow_path.read_text(encoding="utf-8") if exists else ""
checks = {
    "workflow_exists": exists,
    "runs_g3": "s19_g3_front_quality.sh" in content,
    "runs_g4_or_g5": ("s19_g4_timeline_correctness.sh" in content) or ("s19_g5_xray_consistency_and_depth.sh" in content),
}
status = "PASS" if all(checks.values()) else "FAIL"

(scorecard_path.parent).mkdir(parents=True, exist_ok=True)
workflow_copy = evidence_dir / "workflow_preview.yml"
if exists:
    workflow_copy.write_text(content, encoding="utf-8")

scorecard = {
    "gate_id": "S19_G7",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": checks,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G7] Workflow de CI da S19 ausente ou incompleto")
PY

echo "[S19_G7] OK - scorecard em $SCORECARD_PATH"
