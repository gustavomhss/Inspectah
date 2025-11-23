#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  "s18_g0_scope.sh"
  "s18_g1_arch_front_and_api.sh"
  "s18_g2_journeys_and_ux.sh"
  "s18_g3_front_quality.sh"
  "s18_g4_ui_vs_backend.sh"
  "s18_g5_health_mapping.sh"
  "s18_g6_metrics_and_demo.sh"
  "s18_g7_ci_and_observability.sh"
)

for gate in "${GATES[@]}"; do
  echo "[S18_ALL] Executando $gate"
  if ! PYTHONPATH="$ROOT_DIR" bash "$ROOT_DIR/bin/$gate"; then
    echo "[S18_ALL] Falha em $gate" >&2
    exit 1
  fi
done

echo "[S18_ALL] Todos os gates G0…G7 executados com sucesso."
