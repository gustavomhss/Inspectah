#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G3_human_loop"
DB_PATH="${ROOT_DIR}/out/databases/s24_g3_queue.sqlite"
mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}" "$(dirname "${DB_PATH}")"

started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)
status="GO"
details=""
log_file="${EVIDENCE_DIR}/human_loop.log"

set +e
"${PYTHON_BIN}" - <<'PY' >"${log_file}" 2>&1
import json
from pathlib import Path
from app.debunk import service
from app.debunk.models import DebunkIssueTarget, DebunkRiskLevel, DebunkTaskType, DebunkTaskStatus, DebunkIssueStatus
from app.debunk.repository import DebunkRepository

db_path = Path("${DB_PATH}")
if db_path.exists():
    db_path.unlink()
repo = DebunkRepository(db_path=db_path)

issue_critical = service.open_issue(
    repo,
    target_type=DebunkIssueTarget.CLAIM,
    target_id="case-critical",
    question="Claim crítico precisa de revisão?",
    reason="Alto impacto",
    risk_level=DebunkRiskLevel.CRITICAL,
    priority=10,
    origin="s24_g3",
    opened_by="queue-tester",
)
issue_low = service.open_issue(
    repo,
    target_type=DebunkIssueTarget.TRUTH_RECORD,
    target_id="case-low",
    question="Check leve",
    reason="Ruído baixo",
    risk_level=DebunkRiskLevel.LOW,
    priority=3,
    origin="s24_g3",
    opened_by="queue-tester",
)

service.add_task(
    repo,
    issue_id=issue_critical.id,
    task_type=DebunkTaskType.FACT_CHECK,
    instructions="Validar fontes oficiais",
    assigned_to="analyst-1",
)
service.add_task(
    repo,
    issue_id=issue_low.id,
    task_type=DebunkTaskType.SOURCE_COMPARE,
    instructions="Checar divergência leve",
    assigned_to="analyst-2",
)

service.update_task_status(
    repo,
    task_id=repo.list_tasks(issue_critical.id)[0].id,
    new_status=DebunkTaskStatus.DONE,
    result="Fonte oficial confirma",
    actor="analyst-1",
)

queue = repo.queue_snapshot()
metrics = {
    "queue_size": len(queue),
    "high_risk_in_queue": sum(1 for _, i in queue if i.risk_level in {DebunkRiskLevel.CRITICAL, DebunkRiskLevel.HIGH}),
    "issues_by_status": {},
}
for issue in repo.list_issues():
    metrics["issues_by_status"].setdefault(issue.status.value, 0)
    metrics["issues_by_status"][issue.status.value] += 1

print(json.dumps(metrics, ensure_ascii=False, indent=2))
PY
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

metrics=$(tail -n +1 "${log_file}" | tail -n 20 | tr -d '\n' | sed 's/"/\\"/g')
if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao simular fila humano-no-loop."
fi

cat > "${SCORECARDS_DIR}/S24_G3_human_loop.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G3_human_loop",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": {},
  "details": "${details}"
}
JSON

exit ${rc}
