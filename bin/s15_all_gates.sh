#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  "s15_t0_sanity.sh"
  "s15_t1_contracts_and_states.sh"
  "s15_t2_debunker_offline.sh"
  "s15_t3_committees_flow.sh"
  "s15_t4_golden_scenarios.sh"
  "s15_t5_performance_and_cost.sh"
  "s15_t6_observability.sh"
  "s15_t7_ci_and_repro.sh"
  "s15_t8_go_no_go.sh"
)

echo "[S15] Rodando gates T0…T8"
for gate in "${GATES[@]}"; do
  echo "[S15] -> ${gate}"
  bash "$ROOT_DIR/bin/${gate}"
done

echo "[S15] Gates T0…T8 finalizados."
