#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S15_T0] Rode o script a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S15_T0_sanity"
SCORECARD_PATH="$SCORECARD_DIR/S15_T0_sanity.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from inspectah.truthdb.state_machine import StateMachine


EVIDENCE_DIR = Path(sys.argv[1])
SCORECARD_PATH = Path(sys.argv[2])
sm = StateMachine()
coverage = [attempt._asdict() if hasattr(attempt, "_asdict") else {
    "origin": attempt.origin.value,
    "target": attempt.target.value,
    "allowed": attempt.allowed,
} for attempt in sm.coverage_suite()]
invalid_ratio = sm.invalid_transition_rejection_ratio()

(EVIDENCE_DIR / "state_machine_coverage.json").write_text(
    json.dumps({"coverage": coverage, "invalid_rejection_ratio": invalid_ratio}, indent=2),
    encoding="utf-8",
)
status = "PASS" if invalid_ratio >= 0.95 else "FAIL"
scorecard = {
    "gate": "S15_T0",
    "status": status,
    "invalid_transition_rejection_ratio": invalid_ratio,
    "notes": [] if status == "PASS" else ["State machine rejeitou menos de 95% das transições inválidas"],
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
SCORECARD_PATH.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S15_T0] Falhou: verifique scorecard.")
PY

echo "[S15_T0] OK. Scorecard em $SCORECARD_PATH"
