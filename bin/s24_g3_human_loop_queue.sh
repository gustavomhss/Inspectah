#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G3_human_loop_queue"
DB_PATH="${INSPECTAH_S24_G3_DB_PATH:-${ROOT_DIR}/out/databases/s24_g3_queue.sqlite}"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}/logs" "${EVIDENCE_DIR}/metrics" "$(dirname "${DB_PATH}")"

log_file="${EVIDENCE_DIR}/logs/human_loop.log"
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
import statistics
from datetime import datetime, timedelta
from pathlib import Path
import os

from app.debunk.models import (
    DebunkIssue,
    DebunkIssueEvent,
    DebunkIssueStatus,
    DebunkIssueTarget,
    DebunkRiskLevel,
)
from app.debunk.repository import DebunkRepository, gen_id

db_path = Path(os.environ["DB_PATH_ENV"])
evidence_dir = Path(os.environ["EVIDENCE_DIR_ENV"])
repo = DebunkRepository(db_path)

now = datetime.utcnow()
issues = []

def add_issue(age_hours: int, status: DebunkIssueStatus, risk: DebunkRiskLevel, priority: int) -> DebunkIssue:
    created = now - timedelta(hours=age_hours)
    issue = DebunkIssue(
        id=gen_id("dbi"),
        target_type=DebunkIssueTarget.CLAIM,
        target_id=f"claim-{priority}",
        question="O claim procede?",
        reason="Simulação de fila humano-no-loop",
        risk_level=risk,
        priority=priority,
        status=status,
        origin="s24_g3_sim",
        opened_by="gate_runner",
        created_at=created,
        updated_at=created + timedelta(minutes=30),
        metadata={"age_hours": age_hours},
    )
    repo.create_issue(issue)
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="ISSUE_OPENED",
            payload={"risk": risk.value, "priority": priority},
            created_by="gate_runner",
            created_at=created,
        )
    )
    first_action_at = created + timedelta(hours=max(1, age_hours // 3))
    repo.append_event(
        DebunkIssueEvent(
            id=gen_id("dbev"),
            issue_id=issue.id,
            event_type="FIRST_ACTION",
            payload={"note": "primeira ação registrada"},
            created_by="sim_agent",
            created_at=first_action_at,
        )
    )
    issues.append((issue, first_action_at - created))
    return issue

add_issue(6, DebunkIssueStatus.OPEN, DebunkRiskLevel.HIGH, 5)
add_issue(12, DebunkIssueStatus.TRIAGED, DebunkRiskLevel.CRITICAL, 10)
add_issue(30, DebunkIssueStatus.IN_REVIEW, DebunkRiskLevel.MEDIUM, 4)
add_issue(52, DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE, DebunkRiskLevel.HIGH, 6)
add_issue(4, DebunkIssueStatus.READY_FOR_DECISION, DebunkRiskLevel.LOW, 2)

queued_statuses = {
    DebunkIssueStatus.OPEN,
    DebunkIssueStatus.TRIAGED,
    DebunkIssueStatus.IN_REVIEW,
    DebunkIssueStatus.PENDING_ADDITIONAL_EVIDENCE,
    DebunkIssueStatus.READY_FOR_DECISION,
}

queue = [issue for issue, _ in issues if issue.status in queued_statuses]
backlog_total = len(queue)
by_status = {}
for issue in queue:
    by_status[issue.status.value] = by_status.get(issue.status.value, 0) + 1

high_risk_backlog = sum(1 for issue in queue if issue.risk_level in {DebunkRiskLevel.HIGH, DebunkRiskLevel.CRITICAL})
stale_threshold = timedelta(hours=48)
stale_cases = [
    issue.id for issue, _ in issues if issue.status in queued_statuses and (now - issue.created_at) > stale_threshold
]

time_to_first_action = [delta.total_seconds() / 3600.0 for _, delta in issues]
p95 = statistics.quantiles(time_to_first_action, n=20)[-1] if len(time_to_first_action) >= 2 else time_to_first_action[0]

metrics = {
    "backlog_total": backlog_total,
    "by_status": by_status,
    "high_risk_backlog": high_risk_backlog,
    "stale_over_48h": len(stale_cases),
    "time_to_first_action_p95_hours": round(p95, 2),
    "sampled_issues": [issue.id for issue, _ in issues],
}

print(json.dumps({"metrics": metrics, "stale_cases": stale_cases, "db_path": str(db_path)}, indent=2, ensure_ascii=False))

(evidence_dir / "metrics" / "queue_metrics.json").write_text(json.dumps(metrics, indent=2))
(evidence_dir / "run_metadata.json").write_text(
    json.dumps(
        {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "db_path": str(db_path),
            "runner": "s24_g3_human_loop_queue",
        },
        indent=2,
    )
)
PY
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao coletar métricas da fila humano-no-loop."
fi

cat > "${SCORECARDS_DIR}/S24_G3_human_loop_queue.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G3_human_loop_queue",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": $(cat "${EVIDENCE_DIR}/metrics/queue_metrics.json"),
  "details": "${details}",
  "evidence": {
    "log": "out/evidence/S24_G3_human_loop_queue/logs/human_loop.log",
    "metrics": "out/evidence/S24_G3_human_loop_queue/metrics/queue_metrics.json",
    "manifest": "out/evidence/S24_G3_human_loop_queue/run_metadata.json"
  }
}
JSON

exit ${rc}
