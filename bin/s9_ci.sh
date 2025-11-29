#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"
export NET=0
export PYTHONPATH="${PYTHONPATH:-.}"

STEPS=(
  "bin/s9_t1_static_quality.sh"
  "bin/s9_t2_unit_and_contracts.sh"
  "bin/s9_t3_property_and_edge_cases.sh"
  "bin/s9_t4_golden_flows.sh"
  "bin/s9_t5_perf_and_limits.sh"
  "bin/s9_t6_logs_and_evidence.sh"
)

for step in "${STEPS[@]}"; do
  echo "[S9_CI] Executando ${step}"
  if [[ "$step" == "bin/s9_t2_unit_and_contracts.sh" ]]; then
    set +e
    mkdir -p "$ROOT/out/evidence/S9_T2_unit_and_contracts"
    bash -x "${ROOT}/${step}" 2>&1 | tee "$ROOT/out/evidence/S9_T2_unit_and_contracts/ci_debug.log"
    S9_T2_STATUS=${PIPESTATUS[0]}
    set -e
    if [[ "$S9_T2_STATUS" -ne 0 ]]; then
      echo "[S9_CI] ${step} falhou (exit $S9_T2_STATUS). Veja log em out/evidence/S9_T2_unit_and_contracts/ci_debug.log" >&2
      exit "$S9_T2_STATUS"
    fi
  else
    if ! "${ROOT}/${step}"; then
      echo "[S9_CI] ${step} falhou" >&2
      exit 1
    fi
  fi
done

echo "[S9_CI] Gates T1–T6 concluídos com sucesso."
