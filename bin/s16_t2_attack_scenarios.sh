#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T2_attack_scenarios"
SCORECARD_PATH="$SCORECARD_DIR/S16_T2_attack_scenarios.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_attack_scenarios import list_scenarios, run_scenarios

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

available = list_scenarios()
manifest = run_scenarios(evidence_dir=EVIDENCE_DIR, smoke=False)
counter = Counter(res.get("status", "unknown") for res in manifest.get("results", []))

dangerous = counter.get("dangerous", 0)
errors = counter.get("error", 0)
status = "PASS" if dangerous == 0 and errors == 0 else "FAIL"
notes = []
if dangerous:
    notes.append(f"{dangerous} cenários marcados como perigosos")
if errors:
    notes.append(f"{errors} cenários falharam estruturalmente")

scorecard = {
    "gate": "S16_T2_attack_scenarios",
    "status": status,
    "decision": "GO" if status == "PASS" else "NO_GO",
    "metrics": {
        "total": manifest.get("total", 0),
        "dangerous": dangerous,
        "errors": errors,
        "statuses": counter,
    },
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "available_scenarios": [s["id"] for s in available],
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T2] Falhou; consulte evidências.")
PY

echo "[S16_T2] OK. Scorecard em $SCORECARD_PATH"
