#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G4_decision_quality"
DB_PATH="${INSPECTAH_S24_G4_DB_PATH:-${ROOT_DIR}/out/databases/s24_g4_quality.sqlite}"
GOLDEN_PATH="${ROOT_DIR}/goldens/s24_decision_golden.json"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}/logs" "${EVIDENCE_DIR}/metrics" "$(dirname "${DB_PATH}")"

log_file="${EVIDENCE_DIR}/logs/decision_quality.log"
status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

set +e
rm -f "${DB_PATH}"
export DB_PATH_ENV="${DB_PATH}"
export EVIDENCE_DIR_ENV="${EVIDENCE_DIR}"
export GOLDEN_PATH_ENV="${GOLDEN_PATH}"
"${PYTHON_BIN}" - <<'PY' > "${log_file}" 2>&1
import json
from datetime import datetime
from pathlib import Path
import os

from app.debunk import service
from app.debunk.models import (
    DebunkDecisionType,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository

db_path = Path(os.environ["DB_PATH_ENV"])
golden_path = Path(os.environ["GOLDEN_PATH_ENV"])
evidence_dir = Path(os.environ["EVIDENCE_DIR_ENV"])
repo = DebunkRepository(db_path)

golden_cases = json.loads(golden_path.read_text())

agree = 0
severe_errors = 0
uncertainty_flags = 0

executed_cases = []

for case in golden_cases:
    issue = service.open_issue(
        repo,
        target_type=DebunkIssueTarget.CLAIM,
        target_id=case["target_id"],
        question=f"Validar {case['case_id']}",
        reason="benchmark_golden",
        risk_level=DebunkRiskLevel.HIGH,
        priority=5,
        origin="s24_g4_benchmark",
        opened_by="gate_runner",
        metadata={"case_id": case["case_id"]},
    )
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.TRIAGED, actor="gate_runner")
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.IN_REVIEW, actor="gate_runner")
    service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.READY_FOR_DECISION, actor="gate_runner")
    decision = service.record_decision(
        repo,
        issue_id=issue.id,
        decision_type=DebunkDecisionType[case["expected_decision_type"]],
        rationale=case["rationale"],
        recommended_truth_action=RecommendedTruthAction[case["expected_action"]],
        created_by="gate_runner",
        confidence=case["confidence"],
        evidence_refs=case["evidence_refs"],
        residual_uncertainties=[] if case["confidence"] >= 0.5 else ["confidence_below_majority"],
    )
    decision_ok = decision.recommended_truth_action.value == case["expected_action"]
    agree += 1 if decision_ok else 0
    if decision.confidence is not None and decision.confidence < 0.35:
        severe_errors += 1
    if decision.confidence is not None and decision.confidence < 0.5:
        uncertainty_flags += 1
    executed_cases.append({"case_id": case["case_id"], "decision": decision.recommended_truth_action.value, "confidence": decision.confidence})

sample_count = len(golden_cases)
agreement_rate = agree / sample_count if sample_count else 0.0
metrics = {
    "sample_count": sample_count,
    "agreement_rate": round(agreement_rate, 3),
    "severe_misjudgement_count": severe_errors,
    "uncertainty_flag_rate": round(uncertainty_flags / sample_count, 3) if sample_count else 0.0,
    "cases": executed_cases,
}

summary = {
    "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    "db_path": str(db_path),
    "metrics": metrics,
    "golden_path": str(golden_path),
}

(evidence_dir / "metrics" / "decision_quality.json").write_text(json.dumps(metrics, indent=2))
(evidence_dir / "run_metadata.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
PY
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao avaliar qualidade de decisão."
fi

cat > "${SCORECARDS_DIR}/S24_G4_decision_quality.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G4_decision_quality",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": $(cat "${EVIDENCE_DIR}/metrics/decision_quality.json"),
  "details": "${details}",
  "evidence": {
    "log": "out/evidence/S24_G4_decision_quality/logs/decision_quality.log",
    "metrics": "out/evidence/S24_G4_decision_quality/metrics/decision_quality.json",
    "manifest": "out/evidence/S24_G4_decision_quality/run_metadata.json",
    "golden": "goldens/s24_decision_golden.json"
  }
}
JSON

exit ${rc}
