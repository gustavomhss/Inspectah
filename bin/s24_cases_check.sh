#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_cases_check"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}"

log_file="${EVIDENCE_DIR}/cases_check.log"
status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

set +e
"${PYTHON_BIN}" -m scripts.s24_cases_check > "${log_file}" 2>&1
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao rodar validação de casos."
fi

metrics=$(cat "${log_file}" | tail -n +1)

cat > "${SCORECARDS_DIR}/S24_cases_check.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_cases_check",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": ${metrics},
  "details": "${details}",
  "evidence": {
    "log": "out/evidence/S24_cases_check/cases_check.log"
  }
}
JSON

exit ${rc}
