#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S17_T8_go_no_go.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$SCORECARD_PATH" "$SCORECARD_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

targets = [
    "S17_T0_sanity",
    "S17_T1_contracts_and_states",
    "S17_T2_ux_and_accessibility",
    "S17_T3_api_integration",
    "S17_T4_golden_flows",
    "S17_T5_performance_and_bundle",
    "S17_T6_frontend_observability",
    "S17_T7_ci_and_repro",
]

scorecard_path = Path(sys.argv[1])
scorecard_dir = Path(sys.argv[2])

results = {}
missing = []
for gate in targets:
    path = scorecard_dir / f"{gate}.json"
    if not path.exists():
        missing.append(gate)
        continue
    try:
        results[gate] = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        results[gate] = {"status": "FAIL", "notes": "scorecard inválido"}

all_pass = all((res.get("status") == "PASS") for res in results.values()) and not missing
decision = "GO" if all_pass else "GO_WITH_RESTRICTIONS" if not missing else "NO_GO"
notes = []
if missing:
    notes.append(f"Scorecards ausentes: {', '.join(missing)}")
for gate, res in results.items():
    if res.get("status") != "PASS":
        notes.append(f"{gate} status={res.get('status')}")

scorecard = {
    "gate": "S17_T8_go_no_go",
    "status": "PASS" if all_pass else "FAIL",
    "decision": decision,
    "commit_sha": "TBD",
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "inputs": {
        "evaluated_gates": targets,
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if scorecard["status"] != "PASS":
    raise SystemExit("[S17_T8] Decisão ainda não é GO; verifique scorecards anteriores.")
PY

echo "[S17_T8] Scorecard agregado em $SCORECARD_PATH"
