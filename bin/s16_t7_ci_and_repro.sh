#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T7_ci_and_repro"
SCORECARD_PATH="$SCORECARD_DIR/S16_T7_ci_and_repro.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_ci_and_repro_checks import run_checks

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

result = run_checks(EVIDENCE_DIR)
status = result.get("status", "FAIL")
notes = result.get("notes", [])
decision = "GO" if status == "PASS" else "NO_GO"

scorecard = {
    "gate": "S16_T7_ci_and_repro",
    "status": status,
    "decision": decision,
    "metrics": {
        "workflows_present": {
            "gates": bool(result.get("workflows", {}).get("gates", {}).get("exists")),
            "nightly": bool(result.get("workflows", {}).get("nightly", {}).get("exists")),
        },
        "local_scorecards": result.get("local_scorecards", []),
    },
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T7] Falhou; consulte evidências.")
PY

echo "[S16_T7] OK. Scorecard em $SCORECARD_PATH"
