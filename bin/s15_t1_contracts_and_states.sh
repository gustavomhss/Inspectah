#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T1_contracts_and_states"
SCORECARD_PATH="$SCORECARD_DIR/S15_T1_contracts_and_states.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s15_anchor_and_guard import run_anchor_and_guard_suite

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
metrics = run_anchor_and_guard_suite(EVIDENCE_DIR)
status = "PASS"
notes = []
if not metrics.get("override_blocked"):
    status = "FAIL"
    notes.append("Override sem trilha não foi bloqueado")
if metrics.get("anchors_total", 0) <= 0:
    status = "FAIL"
    notes.append("Nenhuma âncora registrada")

scorecard = {
    "gate": "S15_T1",
    "status": status,
    "metrics": metrics,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T1] Falhou: veja scorecard.")
PY

echo "[S15_T1] OK. Scorecard em $SCORECARD_PATH"
