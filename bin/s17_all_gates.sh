#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  s17_t0_sanity.sh
  s17_t1_contracts_and_states.sh
  s17_t2_ux_and_accessibility.sh
  s17_t3_api_integration.sh
  s17_t4_golden_flows.sh
  s17_t5_performance_and_bundle.sh
  s17_t6_frontend_observability.sh
  s17_t7_ci_and_repro.sh
)

for gate in "${GATES[@]}"; do
  echo "[S17] -> $gate"
  bash "$ROOT_DIR/bin/$gate"
done

echo "[S17] -> s17_t8_go_no_go.sh"
bash "$ROOT_DIR/bin/s17_t8_go_no_go.sh"
