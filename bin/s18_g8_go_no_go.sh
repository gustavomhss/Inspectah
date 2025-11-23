#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S18_G8_go_no_go.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$ROOT_DIR" "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])

required = [
    "S18_G0_scope.json",
    "S18_G1_arch_front_and_api.json",
    "S18_G2_journeys_and_ux.json",
    "S18_G3_front_quality.json",
    "S18_G4_ui_vs_backend.json",
    "S18_G5_health_mapping.json",
    "S18_G6_metrics_and_demo.json",
    "S18_G7_ci_and_observability.json",
]

scorecards = {}
failures = []
metrics = {}
for name in required:
    path = root / "out" / "scorecards" / name
    if not path.exists():
        failures.append(f"{name} ausente")
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    scorecards[name] = data
    if data.get("status") != "PASS":
        failures.append(f"{name} status={data.get('status')}")
    for key, value in data.get("metrics", {}).items():
        metrics[key] = value

decision = "GO" if not failures else "NO_GO"
scorecard = {
    "gate_id": "S18_G8",
    "status": "PASS" if decision == "GO" else "FAIL",
    "decision": decision,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": metrics,
    "details": {"failures": failures},
}

summary = {
    "evaluated": required,
    "decision": decision,
    "failures": failures,
    "metrics": metrics,
}
evidence_dir.joinpath("summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if decision != "GO":
    raise SystemExit(f"[S18_G8] NO_GO: {failures}")
PY

echo "[S18_G8] OK - scorecard em $SCORECARD_PATH"
