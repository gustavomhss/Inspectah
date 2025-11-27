#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G2_debunk_api_smoke"
SMOKE_DB="${ROOT_DIR}/out/databases/s24_debunk_smoke.sqlite"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}" "$(dirname "${SMOKE_DB}")"

started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)
status="GO"
details=""
log_file="${EVIDENCE_DIR}/api_smoke.log"

export INSPECTAH_S24_DB_PATH="${SMOKE_DB}"

set +e
"${PYTHON_BIN}" - <<'PY' >"${log_file}" 2>&1
import json
import os
import sys
from fastapi.testclient import TestClient

os.environ.setdefault("PYTHONPATH", ".")

from inspectah.api import build_app  # noqa: E402

app = build_app()
if app is None:
    print("FastAPI não disponível.")
    sys.exit(1)

client = TestClient(app)

create_issue = client.post(
    "/api/debunk/issues",
    json={
        "target_type": "CLAIM",
        "target_id": "smoke-claim",
        "question": "O claim smoke é válido?",
        "reason": "smoke-test",
        "risk_level": "MEDIUM",
        "priority": 5,
        "origin": "smoke",
        "opened_by": "smoke-tester",
    },
)
if create_issue.status_code != 201:
    print(f"create_issue failed: {create_issue.status_code} {create_issue.text}")
    sys.exit(1)
issue_id = create_issue.json()["id"]

create_task = client.post(
    f"/api/debunk/issues/{issue_id}/tasks",
    json={
        "task_type": "FACT_CHECK",
        "instructions": "Verificar evidências mínimas",
        "assigned_to": "smoke-tester",
    },
)
if create_task.status_code != 201:
    print(f"create_task failed: {create_task.status_code} {create_task.text}")
    sys.exit(1)

decision = client.post(
    f"/api/debunk/issues/{issue_id}/decisions",
    json={
        "decision_type": "CLAIM_PLAUSIVEL_MAS_INCOMPLETO",
        "rationale": "smoke decision",
        "recommended_truth_action": "MANTER_ESTADO_ATUAL",
        "created_by": "smoke-tester",
        "confidence": 0.5,
        "evidence_refs": ["evidence://smoke"],
    },
)
if decision.status_code != 201:
    print(f"decision failed: {decision.status_code} {decision.text}")
    sys.exit(1)

overview = client.get(f"/api/debunk/issues/{issue_id}")
if overview.status_code != 200:
    print(f"overview failed: {overview.status_code} {overview.text}")
    sys.exit(1)

data = overview.json()
print(json.dumps({"issue": issue_id, "decisions": len(data.get('decisions', []))}))
sys.exit(0)
PY
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Fluxo API smoke falhou (ver log)."
fi

cat > "${SCORECARDS_DIR}/S24_G2_debunk_api_smoke.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G2_debunk_api_smoke",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": {
    "exit_code": ${rc},
    "db_path": "$(basename "${SMOKE_DB}")"
  },
  "details": "${details}"
}
JSON

exit ${rc}
