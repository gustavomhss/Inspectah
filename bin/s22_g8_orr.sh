#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_ROOT="$ROOT_DIR/out/evidence"
EVIDENCE_DIR="$EVIDENCE_ROOT/S22_orr"
SCORECARD_PATH="$SCORECARD_DIR/S22_G8_orr.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$ROOT_DIR" "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
evidence_dir = Path(sys.argv[3])

gate_ids = [
    "S22_G0_grounding",
    "S22_G1_models_and_invariants",
    "S22_G2_service_contracts",
    "S22_G3_state_machine",
    "S22_G4_persistence",
    "S22_G5_admin_ui",
    "S22_G6_observability",
    "S22_G7_e2e_scenarios",
]

scorecards = []
missing = []
failed = []
for gate in gate_ids:
    path = root / "out" / "scorecards" / f"{gate}.json"
    if not path.exists():
        missing.append(gate)
        continue
    data = json.loads(path.read_text())
    scorecards.append(data)
    if data.get("status") != "PASS":
        failed.append(gate)

gates_total = len(gate_ids)
gates_passed = gates_total - len(failed) - len(missing)
status = "PASS" if gates_passed == gates_total else "FAIL"
decision = "GO" if status == "PASS" else "NO_GO"
missing_evidence_count = len(missing)

aggregate = {
    "gate_id": "S22_G8",
    "status": status,
    "gates_total": gates_total,
    "gates_passed": gates_passed,
    "missing_evidence_count": missing_evidence_count,
    "failed_gates": failed,
    "missing_gates": missing,
    "orr_decision": decision,
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")

manifest = {
    "scorecards": gate_ids,
    "evidence_dirs": sorted([p.name for p in (root / "out" / "evidence").iterdir() if p.is_dir() and p.name.startswith("S22_")]),
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G8] status written to $SCORECARD_PATH"
