#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

bash "$ROOT_DIR/bin/s19_g0_scope.sh"
bash "$ROOT_DIR/bin/s19_g1_contracts_and_data.sh"
bash "$ROOT_DIR/bin/s19_g2_journeys_and_ux.sh"
bash "$ROOT_DIR/bin/s19_g3_front_quality.sh"
bash "$ROOT_DIR/bin/s19_g4_timeline_correctness.sh"
bash "$ROOT_DIR/bin/s19_g5_xray_consistency_and_depth.sh"
bash "$ROOT_DIR/bin/s19_g6_metrics_and_demo.sh"
bash "$ROOT_DIR/bin/s19_g7_ci_and_observability.sh"

echo "[S19_ALL] Gates S19_G0..S19_G7 executados"
