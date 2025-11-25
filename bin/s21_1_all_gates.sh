#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  "$ROOT_DIR/bin/s21_1_g0_contexto.sh"
  "$ROOT_DIR/bin/s21_1_g1_ux_widget.sh"
  "$ROOT_DIR/bin/s21_1_g2_agent_mode.sh"
  "$ROOT_DIR/bin/s21_1_g3_sync_form.sh"
  "$ROOT_DIR/bin/s21_1_g4_files.sh"
  "$ROOT_DIR/bin/s21_1_g5_safety.sh"
  "$ROOT_DIR/bin/s21_1_g6_cenarios.sh"
  "$ROOT_DIR/bin/s21_1_g7_scorecard.sh"
)
for gate in "${GATES[@]}"; do
  echo "== Running ${gate} =="
  bash "$gate"
done
echo "S21.1 gates concluídos"
