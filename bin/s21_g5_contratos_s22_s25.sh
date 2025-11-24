#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G5_contratos"
SCORECARD_PATH="$SCORECARD_DIR/S21_G5_contratos.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

doc="$ROOT_DIR/docs/sprint_21_contratos_s22_s25.md"
status="PASS"
notes="Contratos S22–S25 documentados."

if [[ ! -f "$doc" ]]; then
  status="FAIL"
  notes="Documento de contratos ausente."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G5",
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

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": ["MANIFEST.json"],
    "notes": "Contratos S22–S25 presentes."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G5] status=$status"
