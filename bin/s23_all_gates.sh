#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  s23_g0_contexto.sh
  s23_g1_modelo_dados_e_ontologia.sh
  s23_g2_service_contracts.sh
  s23_g3_frontend_console.sh
  s23_g4_integration_stubs.sh
  s23_g5_observabilidade.sh
  s23_g6_safety_and_policies.sh
  s23_g7_scorecard.sh
)
for gate in "${GATES[@]}"; do
  echo "[S23] executando $gate"
  bash "$ROOT_DIR/bin/$gate"
done
