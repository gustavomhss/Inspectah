#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

SCRIPTS=(
  "bin/s8_t1_static_quality.sh"
  "bin/s8_t2_unit_and_contracts.sh"
  "bin/s8_t3_property_and_edge_cases.sh"
  "bin/s8_t4_golden_flows.sh"
  "bin/s8_t5_perf_and_limits.sh"
  "bin/s8_t6_logs_and_evidence.sh"
)

export PYTHONPATH="$ROOT_DIR"
for script in "${SCRIPTS[@]}"; do
  PYTHONPATH="$ROOT_DIR" "$script"
done
