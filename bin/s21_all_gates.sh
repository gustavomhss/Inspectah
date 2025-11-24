#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

gates=(
  "bin/s21_g0_contexto.sh"
  "bin/s21_g1_ontologia_fontes.sh"
  "bin/s21_g2_modelo_dados.sh"
  "bin/s21_g3_fluxos_admin.sh"
  "bin/s21_g4_ganchos_debunker.sh"
  "bin/s21_g5_contratos_s22_s25.sh"
  "bin/s21_g6_cenarios_uso.sh"
  "bin/s21_g7_scorecard.sh"
)

for gate in "${gates[@]}"; do
  echo "[S21_ALL] Rodando $gate"
  if ! bash "$ROOT_DIR/$gate"; then
    echo "[S21_ALL] Falha em $gate"
    exit 1
  fi
done

echo "[S21_ALL] Gates G0-G7 concluídos."
