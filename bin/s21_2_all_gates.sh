#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

gates=(
  s21_2_g0_contexto.sh
  s21_2_g1_ontologia.sh
  s21_2_g2_fluxos_fsm.sh
  s21_2_g3_backend_api.sh
  s21_2_g4_frontend_ux.sh
  s21_2_g5_agent_tools.sh
  s21_2_g6_safety.sh
  s21_2_g7_scorecard_experiencia.sh
)

for gate in "${gates[@]}"; do
  echo "== Running $ROOT_DIR/bin/$gate =="
  if ! bash "$ROOT_DIR/bin/$gate"; then
    echo "Gate $gate falhou."
    exit 1
  fi
done
echo "S21.2 gates concluídos"
