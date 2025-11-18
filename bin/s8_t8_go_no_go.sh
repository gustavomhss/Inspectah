#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T8_go_no_go"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T8_go_no_go.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
export ROOT_DIR EVIDENCE_DIR SCORECARDS_DIR SUMMARY_FILE SCORECARD_FILE TIMESTAMP

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["ROOT_DIR"])
scorecards_dir = root / "out" / "scorecards"
ordered = [
    "S8_T0_scope.json",
    "S8_T1_static.json",
    "S8_T2_unit_contracts.json",
    "S8_T3_property.json",
    "S8_T4_golden_flows.json",
    "S8_T5_perf.json",
    "S8_T6_logs_and_evidence.json",
    "S8_T7_ci.json",
]
statuses = {}
for filename in ordered:
    path = scorecards_dir / filename
    if not path.exists():
        statuses[filename] = "MISSING"
        continue
    data = json.loads(path.read_text())
    statuses[filename] = data.get("status", "UNKNOWN")

decision = "GO" if all(status == "PASS" for status in statuses.values()) else "NO_GO"
summary = {
    "gate": "S8_T8_go_no_go",
    "status": "PASS" if decision == "GO" else "FAIL",
    "timestamp": os.environ["TIMESTAMP"],
    "decision": decision,
    "gates": statuses,
}
Path(os.environ["SUMMARY_FILE"]).write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate_id": "S8_T8_go_no_go",
    "status": summary["status"],
    "timestamp": os.environ["TIMESTAMP"],
    "decision": decision,
    "outputs": {"summary_file": os.environ["SUMMARY_FILE"]},
}
Path(os.environ["SCORECARD_FILE"]).write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")

if decision != "GO":
    raise SystemExit(1)
PY

echo "S8_T8_go_no_go script avaliou scorecards."
