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
  if ! "$ROOT/${step}"; then
    echo "[S9_CI] ${step} falhou" >&2
    exit 1
  fi
done

echo "[S9_CI] Gates T1–T6 concluídos com sucesso."
