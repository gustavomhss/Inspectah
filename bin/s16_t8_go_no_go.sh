#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S16_T8_go_no_go.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

required = [
    "S16_T0_sanity.json",
    "S16_T1_threat_model.json",
    "S16_T2_attack_scenarios.json",
    "S16_T3_debunker_and_committees_under_attack.json",
    "S16_T4_anchors_and_anti_canetada.json",
    "S16_T5_stress_and_degradation.json",
    "S16_T6_security_observability.json",
    "S16_T7_ci_and_repro.json",
]

scorecards = {}
missing = []
for name in required:
    path = Path("out/scorecards") / name
    if path.exists():
        scorecards[name] = json.loads(path.read_text(encoding="utf-8"))
    else:
        missing.append(name)

status = "PASS"
decision = "GO"
notes = []
if missing:
    status = "FAIL"
    decision = "NO_GO"
    notes.append(f"Scorecards ausentes: {', '.join(missing)}")

failures = [name for name, payload in scorecards.items() if payload.get("status") != "PASS"]
if failures:
    status = "PASS" if status == "PASS" else status
    decision = "NO_GO"
    notes.append(f"Gates com status != PASS: {', '.join(failures)}")

restrictions = [payload.get("decision") for payload in scorecards.values() if payload.get("decision") == "GO_WITH_RESTRICTIONS"]
if not failures and restrictions:
    decision = "GO_WITH_RESTRICTIONS"
if not failures and not restrictions and not missing:
    decision = "GO"

manifest = {
    "scorecards": list(scorecards.keys()),
    "missing": missing,
    "decision": decision,
}
(EVIDENCE_DIR / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

summary = {
    "gate": "S16_T8_go_no_go",
    "status": "PASS" if not missing else "FAIL",
    "decision": decision,
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence_paths": [str(EVIDENCE_DIR)],
}
SCORECARD_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
if summary["status"] != "PASS":
    raise SystemExit("[S16_T8] Falhou; consulte evidências.")
PY

echo "[S16_T8] OK. Scorecard em $SCORECARD_PATH"
