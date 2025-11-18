#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G7"
SCORECARD="$SCORECARD_DIR/S10_G7_audit_and_future.json"
LOG_FILE="$EVIDENCE_DIR/tests.log"
REPORT_FILE="$EVIDENCE_DIR/audit_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR" "$EVIDENCE_DIR/exports"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

status="PASS"
test_status="PASS"
audit_status="PASS"
future_status="PASS"

set +e
python3 "$ROOT_DIR/bin/s5_pytest_shim.py" \
  "$ROOT_DIR/tests/truthdb/test_exports.py" \
  >"$LOG_FILE" 2>&1
shim_exit=$?
set -e
if [[ $shim_exit -ne 0 ]]; then
  test_status="FAIL"
  status="FAIL"
fi

python3 "$ROOT_DIR/scripts/truthdb_export_demo.py" >"$EVIDENCE_DIR/exports.log" 2>&1

readarray -t SUMMARY_VALUES < <(python3 - <<'PY' "$REPORT_FILE"
import json
import sys
from pathlib import Path
from inspectah.pipelines import s10_domain_a_obras, s10_domain_b_precos
from inspectah.truthdb.engine import TruthDBEngine
from inspectah.truthdb import exports

engine = TruthDBEngine()
s10_domain_a_obras.build_domain_a_truthdb(engine=engine)
s10_domain_b_precos.build_domain_b_truthdb(engine=engine)

fact_ids = ["obra_123_prazo", "preco_media_sp_julho"]
fact_exports = exports.export_facts(engine.truthdb, fact_ids)
metrics = exports.build_export_metrics(fact_exports)

report = {
    "fact_exports": fact_exports,
    "metrics": metrics,
}
with open(sys.argv[1], "w", encoding="utf-8") as fp:
    json.dump(report, fp, indent=2)

print(metrics["audit_trace_completeness"])
print(metrics["future_ready_completeness"])
PY
)

audit_ratio="${SUMMARY_VALUES[0]}"
future_ratio="${SUMMARY_VALUES[1]}"

if python3 - <<PY
value=float("$audit_ratio")
exit(0 if value >= 1.0 else 1)
PY
then true
else
  audit_status="FAIL"
  status="FAIL"
fi

future_check=$(python3 - <<PY
value=float("$future_ratio")
if value >= 0.95:
    print("PASS")
elif value >= 0.90:
    print("WARN")
else:
    print("FAIL")
PY
)
future_status="$future_check"
if [[ "$future_status" == "FAIL" ]]; then
  status="FAIL"
elif [[ "$future_status" == "WARN" && "$status" != "FAIL" ]]; then
  status="WARN"
fi

cat >"$SCORECARD" <<JSON
{
  "gate_id": "S10_G7",
  "name": "Audit & exports readiness",
  "status": "$status",
  "slis": {
    "audit_trace_completeness": $audit_ratio,
    "future_ready_completeness": $future_ratio
  },
  "checks": [
    {
      "id": "exports-tests",
      "description": "Rodar tests/truthdb/test_exports.py via shim",
      "status": "$test_status",
      "details": "Logs em tests.log"
    },
    {
      "id": "audit-trace",
      "description": "audit_trace_completeness",
      "status": "$audit_status",
      "details": "valor=$audit_ratio"
    },
    {
      "id": "future-ready",
      "description": "future_ready_completeness",
      "status": "$future_status",
      "details": "valor=$future_ratio"
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
