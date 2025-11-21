#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

GATES=(
  "s14_g0_env_repo.sh"
  "s14_g1_truth_kernel.sh"
  "s14_g2_debunker_consistency.sh"
  "s14_g3_explorer_contracts.sh"
  "s14_g4_migrations_and_cleanup.sh"
  "s14_g5_backlog_fase2.sh"
  "s14_g6_metrics_snapshot.sh"
  "s14_g7_observabilidade.sh"
)

echo "[S14] Rodando gates G0…G7"
for script in "${GATES[@]}"; do
  echo "[S14] -> ${script}"
  bash "$ROOT_DIR/bin/${script}"
done
echo "[S14] Gates G0…G7 finalizados."
