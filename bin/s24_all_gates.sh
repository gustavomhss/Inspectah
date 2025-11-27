#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PYTHONPATH:-${ROOT_DIR}}"
export PYTHON_BIN="${PYTHON_BIN:-python}"
if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  export PYTHON_BIN="python3"
fi

"${ROOT_DIR}/bin/s24_g0_debunk_schema.sh"
"${ROOT_DIR}/bin/s24_g1_debunk_tests.sh"
"${ROOT_DIR}/bin/s24_g2_debunk_api_smoke.sh"
"${ROOT_DIR}/bin/s24_g3_human_loop_queue.sh"
"${ROOT_DIR}/bin/s24_g4_decision_quality.sh"
"${ROOT_DIR}/bin/s24_g5_observability.sh"
"${ROOT_DIR}/bin/s24_g6_demo_and_sanity.sh"
"${ROOT_DIR}/bin/s24_contracts_check.sh"
"${ROOT_DIR}/bin/s24_cases_check.sh"
"${ROOT_DIR}/bin/s24_cases_metrics.sh"
