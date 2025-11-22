#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T3_debunker_and_committees"
SCORECARD_PATH="$SCORECARD_DIR/S16_T3_debunker_and_committees_under_attack.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_debunker_and_committees_under_attack import run_suite

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

result = run_suite(EVIDENCE_DIR)
metrics = result.get("metrics", {})
dangerous = metrics.get("dangerous", 0)
status = "PASS" if dangerous == 0 else "FAIL"
notes = []
if dangerous:
    notes.append("Cenários perigosos passaram sem detecção")
if metrics.get("unknown", 0) > 0:
    notes.append("Cenários com status desconhecido encontrados")

scorecard = {
    "gate": "S16_T3_debunker_and_committees_under_attack",
    "status": status,
    "decision": "GO" if status == "PASS" else "NO_GO",
    "metrics": metrics,
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T3] Falhou; consulte evidências.")
PY

echo "[S16_T3] OK. Scorecard em $SCORECARD_PATH"
