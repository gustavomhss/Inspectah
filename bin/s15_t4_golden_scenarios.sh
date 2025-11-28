#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_BASE="$ROOT_DIR/out/evidence"
SCORECARD_PATH="$SCORECARD_DIR/S15_T4_golden_scenarios.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_BASE"

python3 - <<'PY' "$EVIDENCE_BASE" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s15_golden_scenarios import run_golden_suite

EVIDENCE_BASE = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
summary = run_golden_suite(EVIDENCE_BASE)
status = "PASS"
notes = []
if summary.get("domains", 0) < 5:
    status = "FAIL"
    notes.append("Cobertura insuficiente de domínios")
if any(stats.get("high_risk", 0) == 0 for stats in summary.get("metrics", {}).values()):
    notes.append("Algum domínio não gerou casos de alto risco")

scorecard = {
    "gate": "S15_T4",
    "status": "FAIL" if "Cobertura insuficiente de domínios" in notes else status,
    "metrics": summary.get("metrics", {}),
    "notes": notes,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if scorecard["status"] != "PASS":
    raise SystemExit("[S15_T4] Falhou; verifique scorecard.")
PY

echo "[S15_T4] OK. Scorecard em $SCORECARD_PATH"
