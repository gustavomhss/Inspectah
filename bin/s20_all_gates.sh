#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GATES=(
  "bin/s20_g0_scope_and_baseline.sh"
  "bin/s20_g1_frontend_build_and_sanity.sh"
  "bin/s20_g2_ux_and_navigation.sh"
  "bin/s20_g3_responsiveness_and_basic_accessibility.sh"
  "bin/s20_g4_auth_and_protected_routes.sh"
  "bin/s20_g5_frontend_observability.sh"
  "bin/s20_g6_demo_internal_use_and_truth_states.sh"
  "bin/s20_g7_go_no_go.sh"
)

for gate in "${GATES[@]}"; do
  echo "[S20_ALL] Executando $gate"
  if ! (cd "$ROOT_DIR" && $gate); then
    echo "[S20_ALL] Falha em $gate"
    exit 1
  fi
done

echo "[S20_ALL] Todos os gates executados com sucesso."
