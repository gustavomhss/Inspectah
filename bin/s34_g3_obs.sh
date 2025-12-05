#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S34_G3_observabilidade_multifluxo"
SCORECARD="out/scorecards/S34_G3_obs.json"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards

echo "[S34_G3] Validando observabilidade: métricas/alerts/painel/UI" | tee "$LOG"

set +e
pytest tests/flows/test_slos_queries.py tests/flows/test_flow_alerts.py 2>&1 | tee -a "$LOG"
rc_py=${PIPESTATUS[0]}

(
  cd frontend/inspectah-ui
  npm test -- src/features/flows/__tests__/cockpit_slo_ui.spec.tsx
) 2>&1 | tee -a "$LOG"
rc_ui=${PIPESTATUS[0]}
set -e

status="PASS"
[[ $rc_py -ne 0 || $rc_ui -ne 0 ]] && status="FAIL"

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S34_G3_obs",
    "status": "$status",
    "pytest_rc": $rc_py,
    "ui_rc": $rc_ui,
    "checks": ["metrics_counters", "alerts_files", "dashboard_present", "ops_panel_slo_status"],
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
pathlib.Path("$SCORECARD").write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
