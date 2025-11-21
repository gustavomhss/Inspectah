#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G4"
SCORECARD_PATH="$SCORECARD_DIR/S14_G4_migrations_and_cleanup.json"
REPORT_PATH="$EVIDENCE_DIR/migrations_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"
python3 -m scripts.s14_migrations_and_cleanup

if [[ ! -f "$REPORT_PATH" ]]; then
  >&2 echo "[S14_G4] Report não encontrado em $REPORT_PATH"
  exit 1
fi

python3 - <<'PY' "$REPORT_PATH" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))

status_report = report.get("status", "FAIL")
missing = report.get("metrics", {}).get("missing_required_count", 0)

status = "PASS"
reasons = []
if status_report != "PASS":
    status = "FAIL"
    reasons.append("Relatório marca status FAIL")
if missing > 0:
    status = "FAIL"
    reasons.append(f"{missing} caminhos obrigatórios ausentes")

scorecard = {
    "gate": "S14_G4",
    "status": status,
    "missing_required_count": missing,
    "cleanup_candidates_count": report.get("metrics", {}).get("cleanup_candidates_count", 0),
    "reasons": reasons,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status == "FAIL":
    raise SystemExit("S14_G4 falhou; consulte scorecard.")
PY

echo "[S14_G4] Status registrado em $SCORECARD_PATH"
