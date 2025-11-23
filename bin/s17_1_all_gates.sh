#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GATES=(
  "s17_1_t0_sanity.sh"
  "s17_1_t1_contracts_and_states.sh"
  "s17_1_t2_integration_core_flows.sh"
  "s17_1_t3_error_paths_and_resilience.sh"
  "s17_1_t4_ui_wire_and_e2e_smoke.sh"
  "s17_1_t5_performance_and_limits.sh"
  "s17_1_t6_observability_and_logs.sh"
  "s17_1_t7_ci_and_repro.sh"
  "s17_1_t8_go_no_go.sh"
)

for gate in "${GATES[@]}"; do
  echo "[S17_1_ALL] Rodando $gate"
  "$ROOT_DIR/bin/$gate"
done

echo "[S17_1_ALL] Todos os gates concluídos."
