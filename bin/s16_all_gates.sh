#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GATES=(
  "s16_t0_sanity.sh"
  "s16_t1_threat_model.sh"
  "s16_t2_attack_scenarios.sh"
  "s16_t3_debunker_and_committees_under_attack.sh"
  "s16_t4_anchors_and_anti_canetada.sh"
  "s16_t5_stress_and_degradation.sh"
  "s16_t6_security_observability.sh"
  "s16_t7_ci_and_repro.sh"
  "s16_t8_go_no_go.sh"
)

echo "[S16] Rodando gates T0…T8"
for gate in "${GATES[@]}"; do
  echo "[S16] -> ${gate}"
  bash "$ROOT_DIR/bin/${gate}"
done

echo "[S16] Gates T0…T8 finalizados."
