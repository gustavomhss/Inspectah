#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T2_debunker_offline"
SCORECARD_PATH="$SCORECARD_DIR/S15_T2_debunker_offline.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s15_debunker_offline import run_debunker_suite

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
result = run_debunker_suite(EVIDENCE_DIR)
metrics = result.get("metrics", {})
status = "PASS"
notes = []
if metrics.get("risk_accuracy", 0.0) < 0.6:
    status = "FAIL"
    notes.append("Acurácia de risco abaixo do mínimo")
if metrics.get("recommendation_accuracy", 0.0) < 0.6:
    status = "FAIL"
    notes.append("Acurácia de recomendação abaixo do mínimo")

scorecard = {
    "gate": "S15_T2",
    "status": status,
    "metrics": metrics,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T2] Falhou; verifique evidências.")
PY

echo "[S15_T2] OK. Scorecard em $SCORECARD_PATH"
