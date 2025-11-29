#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S15_T8_go_no_go.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$SCORECARD_DIR" "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_dir = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
scorecard_path = Path(sys.argv[3])

required = [
    "S15_T0_sanity.json",
    "S15_T1_contracts_and_states.json",
    "S15_T2_debunker_offline.json",
    "S15_T3_committees_flow.json",
    "S15_T4_golden_scenarios.json",
    "S15_T5_performance_and_cost.json",
    "S15_T6_observability.json",
    "S15_T7_ci_and_repro.json",
]
results = {}
missing = []
for name in required:
    path = scorecard_dir / name
    if not path.exists():
        missing.append(name)
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    results[name] = data.get("status")

status = "GO"
notes = []
if missing:
    status = "NO_GO"
    notes.append(f"Scorecards faltando: {', '.join(missing)}")
if any(value != "PASS" for value in results.values()):
    status = "NO_GO"
    failures = [k for k, v in results.items() if v != "PASS"]
    notes.append(f"Gates com falha: {', '.join(failures)}")

manifest = {
    "scores": results,
    "missing": missing,
}

(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
summary = {
    "gate": "S15_T8",
    "decision": status,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
if status != "GO":
    raise SystemExit("[S15_T8] NO_GO; veja evidências")
PY

echo "[S15_T8] OK. Scorecard em $SCORECARD_PATH"
