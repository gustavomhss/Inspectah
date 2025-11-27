#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G6_demo_and_sanity"
DB_PATH="${INSPECTAH_S24_G6_DB_PATH:-${ROOT_DIR}/out/databases/s24_g6_demo.sqlite}"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}/logs" "${EVIDENCE_DIR}/reports" "$(dirname "${DB_PATH}")"

log_file="${EVIDENCE_DIR}/logs/demo.log"
status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

set +e
rm -f "${DB_PATH}"
export INSPECTAH_S24_DB_PATH="${DB_PATH}"
export DB_PATH_ENV="${DB_PATH}"
export EVIDENCE_DIR_ENV="${EVIDENCE_DIR}"
"${PYTHON_BIN}" - <<'PY' > "${log_file}" 2>&1
import json
from datetime import datetime
from pathlib import Path
import os

from app.debunk import service
from fastapi.testclient import TestClient

from app.debunk.models import (
    DebunkIssueTarget,
    DebunkRiskLevel,
    DebunkTaskType,
    DebunkTaskStatus,
    DebunkDecisionType,
    RecommendedTruthAction,
)
from app.debunk.repository import DebunkRepository
from inspectah.api import app

db_path = Path(os.environ["DB_PATH_ENV"])
evidence_dir = Path(os.environ["EVIDENCE_DIR_ENV"])
repo = DebunkRepository(db_path)
client = TestClient(app)

payload_issue = {
    "target_type": DebunkIssueTarget.CLAIM.value,
    "target_id": "claim-demo",
    "question": "Demo integrada S24",
    "reason": "Roteiro de demo",
    "risk_level": DebunkRiskLevel.MEDIUM.value,
    "priority": 3,
    "origin": "s24_demo",
    "opened_by": "demo_runner",
}

issue_resp = client.post("/api/debunk/issues", json=payload_issue)
issue_resp.raise_for_status()
issue = issue_resp.json()

task_resp = client.post(
    f"/api/debunk/issues/{issue['id']}/tasks",
    json={
        "task_type": DebunkTaskType.FACT_CHECK.value,
        "instructions": "Validar se a informação procede para demo",
        "assigned_to": "demo_human",
    },
)
task_resp.raise_for_status()
task = task_resp.json()

service.update_task_status(
    repo,
    task_id=task["id"],
    new_status=DebunkTaskStatus.DONE,
    result="Demo concluída",
    actor="demo_human",
)

decision_resp = client.post(
    f"/api/debunk/issues/{issue['id']}/decisions",
    json={
        "decision_type": DebunkDecisionType.CLAIM_BEM_SUPORTADO.value,
        "rationale": "Fluxo ponta a ponta executado sem falhas.",
        "recommended_truth_action": RecommendedTruthAction.MANTER_ESTADO_ATUAL.value,
        "created_by": "demo_runner",
        "confidence": 0.76,
        "evidence_refs": ["demo_evidence"],
    },
)
decision_resp.raise_for_status()

issue_after = client.get(f"/api/debunk/issues/{issue['id']}").json()

report = {
    "timestamp_utc": datetime.utcnow().isoformat() + "Z",
    "issue": issue_after,
    "task": task,
    "decision": decision_resp.json(),
}

(evidence_dir / "reports" / "demo_report.json").write_text(json.dumps(report, indent=2))
(evidence_dir / "run_metadata.json").write_text(json.dumps({"db_path": str(db_path), "timestamp_utc": report["timestamp_utc"]}, indent=2))
print(json.dumps(report, indent=2))
PY
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao executar demo integrada."
fi

gate_list=(S24_G0_debunk_schema S24_G1_debunk_tests S24_G2_debunk_api_smoke S24_G3_human_loop_queue S24_G4_decision_quality S24_G5_observability)
missing=()
for gate in "${gate_list[@]}"; do
  if [ ! -f "${SCORECARDS_DIR}/${gate}.json" ]; then
    missing+=("${gate}")
  fi
done

cat > "${SCORECARDS_DIR}/S24_G6_demo_and_sanity.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G6_demo_and_sanity",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": {
    "gates_prereq_missing": ${#missing[@]},
    "run_rc": ${rc}
  },
  "details": "${details}",
  "evidence": {
    "log": "out/evidence/S24_G6_demo_and_sanity/logs/demo.log",
    "report": "out/evidence/S24_G6_demo_and_sanity/reports/demo_report.json",
    "manifest": "out/evidence/S24_G6_demo_and_sanity/run_metadata.json"
  }
}
JSON

exit ${rc}
