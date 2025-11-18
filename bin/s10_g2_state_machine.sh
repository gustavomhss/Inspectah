#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G2"
SCORECARD="$SCORECARD_DIR/S10_G2_state_machine.json"
LOG_FILE="$EVIDENCE_DIR/tests.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

status="PASS"
test_status="PASS"
ratio_status="PASS"
ratio_value="0.0"

set +e
python3 "$ROOT_DIR/bin/s5_pytest_shim.py" \
  "$ROOT_DIR/tests/truthdb/test_state_machine.py" \
  >"$LOG_FILE" 2>&1
shim_exit=$?
set -e
if [[ $shim_exit -ne 0 ]]; then
  test_status="FAIL"
  status="FAIL"
fi

ratio_value="$(python3 - <<'PY'
from inspectah.truthdb.state_machine import StateMachine
print(f"{StateMachine().invalid_transition_rejection_ratio():.4f}")
PY
)"

if [[ "$ratio_value" != "1.0000" ]]; then
  ratio_status="FAIL"
  status="FAIL"
fi

cat >"$SCORECARD" <<JSON
{
  "gate_id": "S10_G2",
  "name": "Fact state machine",
  "status": "$status",
  "slis": {
    "ratio_invalid_actions_rejected": $ratio_value
  },
  "checks": [
    {
      "id": "state-machine-tests",
      "description": "Rodar tests/truthdb/test_state_machine.py via shim",
      "status": "$test_status",
      "details": "Logs em tests.log"
    },
    {
      "id": "invalid-transition-ratio",
      "description": "Executar suite de cobertura de transições",
      "status": "$ratio_status",
      "details": "ratio_invalid_actions_rejected=$ratio_value"
    }
  ],
  "meta": {
    "ts": "$ts",
    "git_commit": "$git_commit",
    "branch": "$git_branch"
  }
}
JSON

if [[ "$status" == "FAIL" ]]; then
  exit 1
fi
exit 0
