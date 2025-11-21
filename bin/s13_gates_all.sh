#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13] Não parece estar rodando a partir da raiz do repo (faltou .git)."
  exit 2
fi
GATES=(
  "s13_g0_env_repo.sh"
  "s13_g1_pilotos_multi_dominio.sh"
  "s13_g2_cases_timeline_multi.sh"
  "s13_g3_debunker_multi_dominio.sh"
  "s13_g4_explorer_multi_dominio.sh"
  "s13_g5_narrativas_multi_dominio.sh"
  "s13_g6_feedback_multi_dominio.sh"
  "s13_g7_observabilidade.sh"
)

printf '[S13] Rodando gates G0…G7\n'
for gate in "${GATES[@]}"; do
  printf '[S13] -> %s\n' "$gate"
  bash "$ROOT_DIR/bin/$gate"
  printf '[S13] %s PASS (placeholder)\n' "$gate"
done

printf '[S13] Gates G0…G7 finalizados.\n'
