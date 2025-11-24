#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G3_fluxos_admin"
SCORECARD_PATH="$SCORECARD_DIR/S21_G3_fluxos_admin.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

doc="$ROOT_DIR/docs/sprint_21_fluxos_admin_fontes.md"
status="PASS"
notes="Fluxos admin verificados."

if [[ ! -f "$doc" ]]; then
  status="FAIL"
  notes="Documento de fluxos admin ausente."
fi

echo "[S21_G3] Rodando testes de rotas/API..." > "$EVIDENCE_DIR/tests.log"
if ! (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/sources -k "routes" -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  status="FAIL"
  notes="Testes de rotas falharam."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G3",
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
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "Fluxos admin: testes de rotas/API."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G3] status=$status"
