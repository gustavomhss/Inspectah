#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S19_G8_go_no_go.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

"$PYTHON_BIN" - <<'PY' "$SCORECARD_DIR" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

required = [
    "S19_G0_scope.json",
    "S19_G1_contracts_and_data.json",
    "S19_G2_journeys_and_ux.json",
    "S19_G3_front_quality.json",
    "S19_G4_timeline_correctness.json",
    "S19_G5_xray_consistency_and_depth.json",
    "S19_G6_metrics_and_demo.json",
    "S19_G7_ci_and_observability.json",
]

failures = []
for name in required:
    path = scorecard_dir / name
    if not path.exists():
        failures.append(f"scorecard ausente: {name}")
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "PASS":
        failures.append(f"{name} em status {data.get('status')}")

metrics = {}
try:
    g6 = json.loads((scorecard_dir / "S19_G6_metrics_and_demo.json").read_text(encoding="utf-8"))
    metrics = g6.get("metrics", {})
except Exception:
    metrics = {}

threshold_ok = (
    metrics.get("M1", 0) <= 0.8
    and metrics.get("M2", 0) <= 0.8
    and metrics.get("M3", 0) >= 0.95
    and metrics.get("M4", 0) >= 1.0
    and metrics.get("M5", 0) >= 1.0
    and metrics.get("M6", 0) <= 2.0
)
if not threshold_ok:
    failures.append("métricas fora do threshold de M1..M6")

status = "PASS" if not failures else "FAIL"
decision = "GO" if status == "PASS" else "NO_GO"

scorecard = {
    "gate_id": "S19_G8",
    "status": status,
    "decision": decision,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": metrics,
    "details": {"failures": failures},
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G8] GO/NO-GO = NO_GO")
PY

echo "[S19_G8] OK - scorecard em $SCORECARD_PATH"
