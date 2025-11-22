#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T7_ci_and_repro"
SCORECARD_PATH="$SCORECARD_DIR/S17_T7_ci_and_repro.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

set +e
(cd "$FRONTEND_DIR" && npm run lint && npm run test && npm run build) > "$EVIDENCE_DIR/ci_bundle.log" 2>&1
PIPELINE_STATUS=$?
set -e

WORKFLOW_MAIN=("$ROOT_DIR/.ci/sprint_17_gates.yml")
WORKFLOW_NIGHTLY=("$ROOT_DIR/.ci/sprint_17_nightly.yml")

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$PIPELINE_STATUS" "${WORKFLOW_MAIN[@]}" "${WORKFLOW_NIGHTLY[@]}"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
pipeline_status = int(sys.argv[3])
workflow_main = Path(sys.argv[4])
workflow_nightly = Path(sys.argv[5])

workflows_present = workflow_main.exists() and workflow_nightly.exists()
status = "PASS" if pipeline_status == 0 and workflows_present else "FAIL"
scorecard = {
    "gate": "S17_T7_ci_and_repro",
    "status": status,
    "details": {
        "objective": "Garantir checks reprodutíveis e workflows de CI definidos",
        "local_pipeline_log": str(evidence_dir / "ci_bundle.log"),
        "workflows_present": workflows_present,
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T7] Falhou; veja ci_bundle.log ou workflows da pasta .ci")
PY

echo "[S17_T7] OK. Scorecard em $SCORECARD_PATH"
