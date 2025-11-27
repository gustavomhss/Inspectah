#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-${ROOT_DIR}/.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"

SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_G0_debunk_schema"
DB_PATH="${INSPECTAH_S24_DB_PATH:-${ROOT_DIR}/out/databases/s24_debunk.sqlite}"
MIGRATION_PATH="${ROOT_DIR}/db/migrations/025_sprint24_debunk.sql"

mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}" "$(dirname "${DB_PATH}")"

log_file="${EVIDENCE_DIR}/migration.log"
status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

set +e
rm -f "${DB_PATH}"
"${PYTHON_BIN}" -m scripts.db.migrate "${MIGRATION_PATH}" "${DB_PATH}" >"${log_file}" 2>&1
rc=$?
set -e

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Falha ao aplicar migration debunk."
fi

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
db_size=0
if [ -f "${DB_PATH}" ]; then
  db_size=$(stat -f%z "${DB_PATH}" 2>/dev/null || stat -c%s "${DB_PATH}")
fi
duration=$((end_ts - start_ts))

cat > "${SCORECARDS_DIR}/S24_G0_debunk_schema.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_G0_debunk_schema",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "metrics": {
    "db_path": "$(basename "${DB_PATH}")",
    "db_size_bytes": ${db_size},
    "migration_rc": ${rc}
  },
  "details": "${details}"
}
JSON

exit ${rc}
