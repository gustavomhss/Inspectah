#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARDS_DIR="${ROOT_DIR}/out/scorecards"
EVIDENCE_DIR="${ROOT_DIR}/out/evidence/S24_ORR"
mkdir -p "${SCORECARDS_DIR}" "${EVIDENCE_DIR}"

log_file="${EVIDENCE_DIR}/orr.log"

status="GO"
details=""
started_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
start_ts=$(date +%s)

finished_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
end_ts=$(date +%s)
duration=$((end_ts - start_ts))

read_status() {
  local file="$1"
  if [ -f "${file}" ]; then
    jq -r '.status // .gate_status // "UNKNOWN"' "${file}"
  else
    echo "MISSING"
  fi
}

primary_gates=(
  S24_G0_debunk_schema
  S24_G1_debunk_tests
  S24_G2_debunk_api_smoke
  S24_G3_human_loop_queue
  S24_G4_decision_quality
  S24_G5_observability
  S24_G6_demo_and_sanity
)
auxiliary_gates=(
  S24_contracts_check
  S24_cases_check
  S24_cases_metrics
)

declare -A gate_status
rc=0
primary_missing=0
primary_no_go=0
aux_missing=0
aux_no_go=0

{
  echo "S24 ORR Summary (${started_at} UTC)"
  echo "Primary gates:"
  for gate in "${primary_gates[@]}"; do
    status_value="$(read_status "${SCORECARDS_DIR}/${gate}.json")"
    gate_status["${gate}"]="${status_value}"
    echo "- ${gate}: ${status_value}"
    if [ "${status_value}" != "GO" ]; then
      primary_no_go=$((primary_no_go + 1))
      rc=1
    fi
    if [ "${status_value}" = "MISSING" ]; then
      primary_missing=$((primary_missing + 1))
    fi
  done
  echo "Auxiliary checks:"
  for gate in "${auxiliary_gates[@]}"; do
    status_value="$(read_status "${SCORECARDS_DIR}/${gate}.json")"
    gate_status["${gate}"]="${status_value}"
    echo "- ${gate}: ${status_value}"
    if [ "${status_value}" != "GO" ]; then
      aux_no_go=$((aux_no_go + 1))
    fi
    if [ "${status_value}" = "MISSING" ]; then
      aux_missing=$((aux_missing + 1))
    fi
  done
} > "${log_file}"

if [ ${rc} -ne 0 ]; then
  status="NO_GO"
  details="Algum gate primário falhou ou está ausente. Veja out/evidence/S24_ORR/orr.log"
elif [ ${aux_no_go} -gt 0 ]; then
  status="GO"
  details="Gates primários OK, mas há checagens auxiliares não-GO."
fi

cat > "${SCORECARDS_DIR}/S24_ORR.json" <<JSON
{
  "sprint": "S24",
  "gate": "S24_ORR",
  "status": "${status}",
  "started_at": "${started_at}",
  "finished_at": "${finished_at}",
  "duration_seconds": ${duration},
  "details": "${details}",
  "metrics": {
    "primary_total": ${#primary_gates[@]},
    "primary_go": $(( ${#primary_gates[@]} - primary_no_go )),
    "primary_no_go": ${primary_no_go},
    "primary_missing": ${primary_missing},
    "auxiliary_total": ${#auxiliary_gates[@]},
    "auxiliary_non_go": ${aux_no_go},
    "auxiliary_missing": ${aux_missing}
  },
  "gates": {
    "primary": {
      "S24_G0_debunk_schema": "${gate_status[S24_G0_debunk_schema]}",
      "S24_G1_debunk_tests": "${gate_status[S24_G1_debunk_tests]}",
      "S24_G2_debunk_api_smoke": "${gate_status[S24_G2_debunk_api_smoke]}",
      "S24_G3_human_loop_queue": "${gate_status[S24_G3_human_loop_queue]}",
      "S24_G4_decision_quality": "${gate_status[S24_G4_decision_quality]}",
      "S24_G5_observability": "${gate_status[S24_G5_observability]}",
      "S24_G6_demo_and_sanity": "${gate_status[S24_G6_demo_and_sanity]}"
    },
    "auxiliary": {
      "S24_contracts_check": "${gate_status[S24_contracts_check]}",
      "S24_cases_check": "${gate_status[S24_cases_check]}",
      "S24_cases_metrics": "${gate_status[S24_cases_metrics]}"
    }
  },
  "evidence": {
    "log": "out/evidence/S24_ORR/orr.log"
  }
}
JSON

exit ${rc}
