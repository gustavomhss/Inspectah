#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

gates=(
  "bin/s22_g0_grounding.sh"
  "bin/s22_g1_models_and_invariants.sh"
  "bin/s22_g2_service_contracts.sh"
  "bin/s22_g3_state_machine.sh"
  "bin/s22_g4_persistence.sh"
  "bin/s22_g5_admin_ui.sh"
  "bin/s22_g6_observability.sh"
  "bin/s22_g7_e2e_scenarios.sh"
)

for gate in "${gates[@]}"; do
  echo "[S22_ALL] Rodando $gate"
  if ! bash "$ROOT_DIR/$gate"; then
    echo "[S22_ALL] Falha em $gate"
    exit 1
  fi
done

echo "[S22_ALL] Gates G0-G7 concluídos."
