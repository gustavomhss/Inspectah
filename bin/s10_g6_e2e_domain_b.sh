#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G6"
SCORECARD="$SCORECARD_DIR/S10_G6_e2e_domain_B.json"
LOG_FILE="$EVIDENCE_DIR/tests.log"
REPORT_FILE="$EVIDENCE_DIR/domain_b_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

status="PASS"
test_status="PASS"
valid_ratio_status="PASS"
invalid_ratio_status="PASS"
audit_status="PASS"
scenario_status="PASS"

set +e
python3 "$ROOT_DIR/bin/s5_pytest_shim.py" \
  "$ROOT_DIR/tests/pipelines/test_s10_domain_b_precos.py" \
  >"$LOG_FILE" 2>&1
shim_exit=$?
set -e
if [[ $shim_exit -ne 0 ]]; then
  test_status="FAIL"
  status="FAIL"
fi

readarray -t SUMMARY_VALUES < <(python3 - <<'PY' "$REPORT_FILE"
import json
import sys
from inspectah.pipelines import s10_domain_b_precos as pipeline

report = pipeline.run_demo_report()
with open(sys.argv[1], "w", encoding="utf-8") as fp:
    json.dump(report, fp, indent=2)
summary = report["summary"]
print(summary["ratio_valid_actions_accepted"])
print(summary["ratio_invalid_actions_rejected"])
print(summary["audit_trace_completeness"])
print(summary["e2e_scenario_success_rate"])
PY
)

valid_ratio="${SUMMARY_VALUES[0]}"
invalid_ratio="${SUMMARY_VALUES[1]}"
audit_ratio="${SUMMARY_VALUES[2]}"
scenario_ratio="${SUMMARY_VALUES[3]}"

if python3 - <<PY
value=float("$valid_ratio")
exit(0 if value >= 1.0 else 1)
PY
then true
else
  valid_ratio_status="FAIL"
  status="FAIL"
fi

if python3 - <<PY
value=float("$invalid_ratio")
exit(0 if value >= 1.0 else 1)
PY
then true
else
  invalid_ratio_status="FAIL"
  status="FAIL"
fi

if python3 - <<PY
value=float("$audit_ratio")
exit(0 if value >= 1.0 else 1)
PY
then true
else
  audit_status="FAIL"
  status="FAIL"
fi

scenario_check=$(python3 - <<PY
value=float("$scenario_ratio")
if value >= 0.95:
    print("PASS")
elif value >= 0.90:
    print("WARN")
else:
    print("FAIL")
PY
)

scenario_status="$scenario_check"
if [[ "$scenario_status" == "FAIL" ]]; then
  status="FAIL"
elif [[ "$scenario_status" == "WARN" && "$status" != "FAIL" ]]; then
  status="WARN"
fi

cat >"$SCORECARD" <<JSON
{
  "gate_id": "S10_G6",
  "name": "Domain B E2E pipeline",
  "status": "$status",
  "slis": {
    "ratio_valid_actions_accepted": $valid_ratio,
    "ratio_invalid_actions_rejected": $invalid_ratio,
    "audit_trace_completeness": $audit_ratio,
    "e2e_scenario_success_rate": $scenario_ratio
  },
  "checks": [
    {
      "id": "domain-b-tests",
      "description": "Rodar tests/pipelines/test_s10_domain_b_precos.py via shim",
      "status": "$test_status",
      "details": "Logs em tests.log"
    },
    {
      "id": "valid-actions",
      "description": "ratio_valid_actions_accepted",
      "status": "$valid_ratio_status",
      "details": "valor=$valid_ratio"
    },
    {
      "id": "invalid-actions",
      "description": "ratio_invalid_actions_rejected",
      "status": "$invalid_ratio_status",
      "details": "valor=$invalid_ratio"
    },
    {
      "id": "audit-trace",
      "description": "audit_trace_completeness",
      "status": "$audit_status",
      "details": "valor=$audit_ratio"
    },
    {
      "id": "scenario-success",
      "description": "e2e_scenario_success_rate",
      "status": "$scenario_status",
      "details": "valor=$scenario_ratio"
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
