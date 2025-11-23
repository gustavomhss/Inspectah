#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T8_go_no_go"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T8_go_no_go.json"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" - <<'PY' "$SCORECARD_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from glob import glob

scorecard_dir = Path(sys.argv[1])
output = Path(sys.argv[2])

scorecards = {}
for path in glob(str(scorecard_dir / "S17_1_T*_*.json")):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    scorecards[Path(path).name] = data.get("status")

all_pass = all(status == "PASS" for status in scorecards.values()) and len(scorecards) >= 8
decision = "GO" if all_pass else "NO_GO"

payload = {
    "gate": "S17_1_T8_go_no_go",
    "status": "PASS" if decision == "GO" else "FAIL",
    "decision": decision,
    "scorecards": scorecards,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

if decision != "GO":
    raise SystemExit("[S17_1_T8] GO/NO_GO: condições não atendidas.")
PY

echo "[S17_1_T8] OK. Scorecard em $SCORECARD_PATH"
