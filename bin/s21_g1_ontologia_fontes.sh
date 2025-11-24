#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G1_ontologia"
SCORECARD_PATH="$SCORECARD_DIR/S21_G1_ontologia.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

doc="$ROOT_DIR/docs/sprint_21_ontologia_fontes.md"
status="PASS"
notes="Ontologia presente e sem TODO."
if [[ ! -f "$doc" ]]; then
  status="FAIL"
  notes="Ontologia ausente."
fi
todo_hits="$(rg --no-heading --line-number -w 'TODO|FIXME' "$doc" || true)"
if [[ -n "$todo_hits" ]]; then
  status="FAIL"
  notes="TODO/FIXME encontrados."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G1",
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

python3 - <<'PY' "$EVIDENCE_DIR" "$doc"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": ["MANIFEST.json"],
    "notes": f"Ontologia: {Path(sys.argv[2]).name}",
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G1] status=$status"
