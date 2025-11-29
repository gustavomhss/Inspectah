#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT_DIR"

gates=(
  "bin/s10_g0_sanity.sh"
  "bin/s10_g1_truthdb_model.sh"
  "bin/s10_g2_state_machine.sh"
  "bin/s10_g3_guardian_contract.sh"
  "bin/s10_g4_mechanical_engine.sh"
  "bin/s10_g5_e2e_domain_a.sh"
  "bin/s10_g6_e2e_domain_b.sh"
  "bin/s10_g7_audit_and_future.sh"
  "bin/s10_g8_go_no_go.sh"
)

for gate in "${gates[@]}"; do
  echo "[Sprint10] Executando $gate"
  "$ROOT_DIR/$gate"
done

echo "[Sprint10] Todos os gates concluídos."
