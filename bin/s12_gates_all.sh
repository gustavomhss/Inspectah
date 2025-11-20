#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  "s12_g0_env_repo.sh"
  "s12_g1_sources_scheduler.sh"
  "s12_g2_ingest_pipeline.sh"
  "s12_g3_debunker_coverage.sh"
  "s12_g4_cases_timeline.sh"
  "s12_g5_explorer_e2e.sh"
  "s12_g6_feedback_flow.sh"
  "s12_g7_observabilidade.sh"
)

echo "[S12] Rodando gates G0…G7"
for script in "${GATES[@]}"; do
  echo "[S12] -> ${script}"
  bash "$ROOT_DIR/bin/${script}"
done
echo "[S12] Gates G0…G7 concluídos com sucesso."
