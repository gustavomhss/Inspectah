#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T3_committees_flow"
SCORECARD_PATH="$SCORECARD_DIR/S15_T3_committees_flow.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s15_committees_flow import run_committees_flow

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
result = run_committees_flow(EVIDENCE_DIR)
metrics = result.get("metrics", {})
status = "PASS"
notes = []
if metrics.get("v1_rejected", 0) == 0:
    status = "FAIL"
    notes.append("Nenhum caso rejeitado em V1")
if metrics.get("v2_escalated", 0) == 0:
    status = "FAIL"
    notes.append("Nenhuma escalada detectada em V2")
if metrics.get("v3_blocked", 0) == 0:
    status = "FAIL"
    notes.append("Nenhuma incoerência global detectada")

summary_path = EVIDENCE_DIR / "summary.json"
summary_path.write_text(json.dumps({"cases": result.get("cases", []), "metrics": metrics}, indent=2, ensure_ascii=False), encoding="utf-8")

scorecard = {
    "gate": "S15_T3",
    "status": status,
    "metrics": metrics,
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T3] Falhou; consulte evidências.")
PY

echo "[S15_T3] OK. Scorecard em $SCORECARD_PATH"
