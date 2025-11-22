#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T6_security_observability"
SCORECARD_PATH="$SCORECARD_DIR/S16_T6_security_observability.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_security_observability_checks import run_checks

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

result = run_checks(EVIDENCE_DIR)
raw_status = result.get("status", "WARN")
status = "PASS" if raw_status in {"PASS", "WARN"} else "FAIL"
decision = "GO_WITH_RESTRICTIONS" if raw_status == "WARN" else ("GO" if status == "PASS" else "NO_GO")
notes = []
if raw_status == "WARN":
    notes.append("Algumas consultas de observabilidade indisponíveis; verificar manifestos")
if status != "PASS":
    notes.append("Observabilidade insuficiente para incidentes")

scorecard = {
    "gate": "S16_T6_security_observability",
    "status": status,
    "decision": decision,
    "metrics": result.get("summary", {}),
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T6] Falhou; consulte evidências.")
PY

echo "[S16_T6] OK. Scorecard em $SCORECARD_PATH"
