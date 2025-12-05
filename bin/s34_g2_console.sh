#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S34_G2_console_multifluxo"
SCORECARD="out/scorecards/S34_G2_console.json"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards

echo "[S34_G2] Rodando testes de console/API multi-fluxo (frontend)" | tee "$LOG"

set +e
(cd frontend/inspectah-ui && npm test -- src/features/flows/__tests__/flows_console.spec.tsx) 2>&1 | tee -a "$LOG"
rc_tests=${PIPESTATUS[0]}
set -e

status="PASS"
[[ $rc_tests -ne 0 ]] && status="FAIL"

python3 - <<PY
import datetime
import json
import pathlib

scorecard = {
    "gate": "S34_G2_console",
    "status": "$status",
    "tests_rc": $rc_tests,
    "tests": ["frontend flows_console.spec.tsx"],
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
pathlib.Path("$SCORECARD").write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
