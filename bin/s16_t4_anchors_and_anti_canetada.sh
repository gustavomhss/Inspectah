#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T4_anchors_and_anti_canetada"
SCORECARD_PATH="$SCORECARD_DIR/S16_T4_anchors_and_anti_canetada.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_anchors_and_anti_canetada_tests import run_tests

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

result = run_tests(EVIDENCE_DIR)
status = result.get("status", "FAIL")
notes = result.get("notes", [])
decision = "GO" if status == "PASS" else "NO_GO"
if result.get("anchor_failures", 0) > 0 and status == "PASS":
    decision = "GO_WITH_RESTRICTIONS"
    notes.append("Falhas de chain detectadas; ver comportamento em produção")

scorecard = {
    "gate": "S16_T4_anchors_and_anti_canetada",
    "status": status,
    "decision": decision,
    "metrics": {
        "anchor_failures": result.get("anchor_failures", 0),
        "override_events_recorded": result.get("override_events_recorded", 0),
    },
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T4] Falhou; consulte evidências.")
PY

echo "[S16_T4] OK. Scorecard em $SCORECARD_PATH"
