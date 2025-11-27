#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  PYTHON_BIN="python3"
fi
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G1_debunk_tests"
mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}"

started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)
log_file="${EVIDENCE_DIR}/pytest.log"

set +e
"${PYTHON_BIN}" -m pytest tests/debunk/test_debunk_service.py >"${log_file}" 2>&1
rc=$?
set -e

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

tests_run=$(grep -Eo "[0-9]+ passed" "${log_file}" | head -n1 | awk '{print $1}')
if [ -z "${tests_run}" ]; then
  tests_run=0
fi

status="GO"
details=""
if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao rodar pytest para Debunker v0."
fi

cat > "${SCORECARDS_DIR}/S24_G1_debunk_tests.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G1_debunk_tests",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": {
    "tests_run": ${tests_run},
    "exit_code": ${rc}
  },
  "details": "${details}"
}
JSON

exit ${rc}
