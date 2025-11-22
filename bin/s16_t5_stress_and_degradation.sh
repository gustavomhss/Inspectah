#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T5_stress_and_degradation"
SCORECARD_PATH="$SCORECARD_DIR/S16_T5_stress_and_degradation.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_stress_and_degradation import run_stress

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

result = run_stress(EVIDENCE_DIR)
status = result.get("status", "FAIL")
notes = result.get("details", {}).get("notes", [])

scorecard = {
    "gate": "S16_T5_stress_and_degradation",
    "status": status,
    "decision": "GO" if status == "PASS" else "GO_WITH_RESTRICTIONS",
    "metrics": result.get("metrics", {}),
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T5] Falhou; consulte evidências.")
PY

echo "[S16_T5] OK. Scorecard em $SCORECARD_PATH"
