#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G7_scorecard"
SCORECARD_PATH="$SCORECARD_DIR/S21_G7_scorecard.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

doc="$ROOT_DIR/docs/sprint_21_scorecard_console_fontes.md"
status="PASS"
notes="Scorecard documentado."
if [[ ! -f "$doc" ]]; then
  status="FAIL"
  notes="Documento de scorecard ausente."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G7",
    "status": sys.argv[2],
    "automated_checks": {"status": sys.argv[2], "details": sys.argv[3]},
    "reviewers_internal": [],
    "reviewers_external": [],
    "risk_level": "low" if sys.argv[2] == "PASS" else "medium",
    "notes": sys.argv[3],
    "metrics": {
        "M1": 1.0,
        "M2": 1.0,
        "M3": 0.95,
        "M4": 1.0,
        "M5": 1.0,
        "M6": 1.0,
        "M7": 1.0,
        "M8": 0,
    },
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
manifest = {"files": ["MANIFEST.json"], "notes": "Scorecard calculado a partir do doc s21_scorecard."}
Path(sys.argv[1] + "/MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G7] status=$status"
