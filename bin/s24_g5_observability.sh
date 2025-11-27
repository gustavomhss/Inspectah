#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G5_observability"
DB_PATH="${INSPECTAH_S24_G5_DB_PATH:-${ROOT_DIR}/out/databases/s24_g5_observability.sqlite}"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}/logs" "${EVIDENCE_DIR}/metrics" "$(dirname "${DB_PATH}")"

log_file="${EVIDENCE_DIR}/logs/observability.log"
status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

set +e
rm -f "${DB_PATH}"
export DB_PATH_ENV="${DB_PATH}"
export EVIDENCE_DIR_ENV="${EVIDENCE_DIR}"
"${PYTHON_BIN}" - <<'PY' > "${log_file}" 2>&1
import json
from datetime import datetime
from pathlib import Path
import os

from app.debunk import service
from app.debunk.models import (
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTaskStatus,
    DebunkTaskType,
    DebunkDecisionType,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository

db_path = Path(os.environ["DB_PATH_ENV"])
evidence_dir = Path(os.environ["EVIDENCE_DIR_ENV"])
repo = DebunkRepository(db_path)

issue = service.open_issue(
    repo,
    target_type=DebunkIssueTarget.CLAIM,
    target_id="claim-observability",
    question="Verificar observabilidade de decisão",
    reason="gate_g5",
    risk_level=DebunkRiskLevel.CRITICAL,
    priority=9,
    origin="s24_g5",
    opened_by="gate_runner",
)

task = service.add_task(
    repo,
    issue_id=issue.id,
    task_type=DebunkTaskType.FACT_CHECK,
    instructions="Revisar fonte oficial e registrar observações",
    assigned_to="human_reviewer",
)
service.update_task_status(repo, task_id=task.id, new_status=DebunkTaskStatus.NEEDS_HUMAN_REVIEW, result=None, actor="human_reviewer")
service.update_task_status(repo, task_id=task.id, new_status=DebunkTaskStatus.DONE, result="Fonte confirma o claim", actor="human_reviewer")
service.move_issue_status(repo, issue_id=issue.id, new_status=DebunkIssueStatus.READY_FOR_DECISION, actor="gate_runner")
service.record_decision(
    repo,
    issue_id=issue.id,
    decision_type=DebunkDecisionType.CLAIM_BEM_SUPORTADO,
    rationale="Fluxo observável com eventos e logs.",
    recommended_truth_action=RecommendedTruthAction.MANTER_ESTADO_ATUAL,
    created_by="gate_runner",
    confidence=0.78,
    evidence_refs=["observability_run"],
)

events = repo.list_events(issue.id)
event_types = [e.event_type for e in events]
event_counts = {k: event_types.count(k) for k in set(event_types)}

checks = {
    "has_issue_opened": "ISSUE_OPENED" in event_types,
    "has_task_events": any(t in event_types for t in ("TASK_CREATED", "TASK_STATUS_CHANGED")),
    "has_decision": "DECISION_RECORDED" in event_types,
}

metrics = {
    "event_count": len(events),
    "event_types": event_counts,
    "checks_ok": checks,
}

audit_gap = 0
if not all(checks.values()):
    audit_gap = 1

metrics["audit_gaps"] = audit_gap
metrics["issue_id"] = issue.id

(evidence_dir / "metrics" / "observability_metrics.json").write_text(json.dumps(metrics, indent=2))
(evidence_dir / "run_metadata.json").write_text(
    json.dumps(
        {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "db_path": str(db_path),
            "issue_id": issue.id,
        },
        indent=2,
    )
)
print(json.dumps({"events": event_types, "metrics": metrics}, indent=2))
PY
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao validar observabilidade e regressões básicas."
else
  export EVIDENCE_DIR_ENV="${EVIDENCE_DIR}"
  audit_gaps=$("${PYTHON_BIN}" - <<'PY'
import json
from pathlib import Path
import os
data = json.loads(Path(os.environ["EVIDENCE_DIR_ENV"]).joinpath("metrics/observability_metrics.json").read_text())
print(data.get("audit_gaps", 0))
PY
)
  if [ "${audit_gaps}" != "0" ]; then
    status="WARN"
    details="Fluxo auditável com ressalvas; verificar métricas."
  fi
fi

cat > "${SCORECARDS_DIR}/S24_G5_observability.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G5_observability",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": $(cat "${EVIDENCE_DIR}/metrics/observability_metrics.json"),
  "details": "${details}",
  "evidence": {
    "log": "out/evidence/S24_G5_observability/logs/observability.log",
    "metrics": "out/evidence/S24_G5_observability/metrics/observability_metrics.json",
    "manifest": "out/evidence/S24_G5_observability/run_metadata.json"
  }
}
JSON

exit ${rc}
