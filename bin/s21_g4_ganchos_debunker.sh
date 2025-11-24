#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G4_ganchos_debunker"
SCORECARD_PATH="$SCORECARD_DIR/S21_G4_ganchos_debunker.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

doc="$ROOT_DIR/docs/sprint_21_ganchos_debunker_fontes.md"
model="$ROOT_DIR/app/sources/models.py"
status="PASS"
notes="Ganchos documentados e presentes no modelo."

if [[ ! -f "$doc" || ! -f "$model" ]]; then
  status="FAIL"
  notes="Doc ou modelo ausente."
fi

rg_hits="$(rg "conflict_flags|has_open_contestation|conflict_with_sources" "$model" || true)"
if [[ -z "$rg_hits" ]]; then
  status="FAIL"
  notes="Campos de conflito/contestação não encontrados no modelo."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G4",
    "status": sys.argv[2],
    "automated_checks": {"status": sys.argv[2], "details": sys.argv[3]},
    "reviewers_internal": [],
    "reviewers_external": [],
    "risk_level": "low" if sys.argv[2] == "PASS" else "medium",
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR" "$rg_hits"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": ["MANIFEST.json", "hits.txt"],
    "notes": "Ganchos de Debunker (doc + campos no modelo)."
}
(evidence_dir / "hits.txt").write_text(sys.argv[2], encoding="utf-8")
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G4] status=$status"
