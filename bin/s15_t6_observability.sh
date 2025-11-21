#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T6_observability"
SCORECARD_PATH="$SCORECARD_DIR/S15_T6_observability.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s15_observability import build_observability_report

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
result = build_observability_report(EVIDENCE_DIR)
metrics = result.get("metrics", {})
status = "PASS"
notes = []
if metrics.get("claims_analyzed", 0) == 0:
    status = "FAIL"
    notes.append("Nenhum claim analisado pelo Debunker")
if metrics.get("anchors_registered", 0) == 0:
    status = "FAIL"
    notes.append("Nenhuma âncora registrada para observabilidade")

scorecard = {
    "gate": "S15_T6",
    "status": status,
    "metrics": metrics,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T6] Falhou; verifique consultas.")
PY

echo "[S15_T6] OK. Scorecard em $SCORECARD_PATH"
