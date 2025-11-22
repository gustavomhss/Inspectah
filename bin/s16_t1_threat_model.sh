#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S16_T1_threat_model"
SCORECARD_PATH="$SCORECARD_DIR/S16_T1_threat_model.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s16_threat_model_checks import run_checks

EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])

result = run_checks(Path("docs/sprint_16_threat_model.md"), EVIDENCE_DIR)
status = "PASS" if result.get("status") == "PASS" else "FAIL"
notes = []
if result.get("missing_sections"):
    notes.append(f"Seções faltantes: {', '.join(result['missing_sections'])}")
if result.get("references_missing"):
    notes.append(f"Referências quebradas: {', '.join(result['references_missing'])}")

scorecard = {
    "gate": "S16_T1_threat_model",
    "status": status,
    "decision": "GO" if status == "PASS" else "NO_GO",
    "metrics": {
        "line_count": result.get("line_count", 0),
        "missing_sections": result.get("missing_sections", []),
        "references_missing": result.get("references_missing", []),
    },
    "evidence_paths": [str(EVIDENCE_DIR)],
    "notes": notes,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S16_T1] Falhou; consulte evidências.")
PY

echo "[S16_T1] OK. Scorecard em $SCORECARD_PATH"
