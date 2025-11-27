#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_contracts_check"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}"

log_file="${EVIDENCE_DIR}/contracts_check.log"
status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

set +e
"${PYTHON_BIN}" -m pytest tests/integration/test_s23_s24_s25_contracts.py > "${log_file}" 2>&1
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha nos contratos S23→S24→S25"
fi

cat > "${SCORECARDS_DIR}/S24_contracts_check.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_contracts_check",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": {
    "exit_code": ${rc}
  },
  "details": "${details}",
  "evidence": {
    "log": "out/evidence/S24_contracts_check/contracts_check.log"
  }
}
JSON

exit ${rc}
