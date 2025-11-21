#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T5_performance_and_cost"
SCORECARD_PATH="$SCORECARD_DIR/S15_T5_performance_and_cost.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s15_performance_cost import measure_performance

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
result = measure_performance(EVIDENCE_DIR)
metrics = result.get("metrics", {})
status = "PASS"
notes = []
if metrics.get("throughput_claims_per_sec", 0) < 1:
    status = "FAIL"
    notes.append("Throughput do Debunker abaixo do alvo mínimo (1 claim/s)")

scorecard = {
    "gate": "S15_T5",
    "status": status,
    "metrics": metrics,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T5] Falhou; confira evidências.")
PY

echo "[S15_T5] OK. Scorecard em $SCORECARD_PATH"
