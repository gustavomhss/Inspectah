#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G1_models_and_invariants"
SCORECARD_PATH="$SCORECARD_DIR/S22_G1_models_and_invariants.json"
DOC_MODELOS="$ROOT_DIR/docs/sprint_22_g1_modelos_e_invariantes.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="Modelos e invariantes ok."
inv_defined=0
inv_tested=0
tests_pass_rate=0.0

if [[ ! -f "$DOC_MODELOS" ]]; then
  status="FAIL"
  notes="Doc de modelos/invariantes ausente."
else
  inv_defined=$(rg --no-heading -o "INV-[0-9]+" "$DOC_MODELOS" | wc -l | tr -d ' ' || echo "0")
fi

echo "[S22_G1] Aplicando migration SQL..." > "$EVIDENCE_DIR/migration.log"
if ! (cd "$ROOT_DIR" && .venv/bin/python -m scripts.db.migrate db/migrations/022_sprint22_ingestion.sql >> "$EVIDENCE_DIR/migration.log" 2>&1); then
  status="FAIL"
  notes="Falha ao aplicar migration de ingestão."
fi

echo "[S22_G1] Rodando testes de modelos e invariantes..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_models_and_invariants.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  inv_tested="$inv_defined"
  tests_pass_rate=1.0
else
  status="FAIL"
  notes="Falha nos testes de modelos/invariantes."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$inv_defined" "$inv_tested" "$tests_pass_rate"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G1",
    "status": sys.argv[2],
    "invariants_defined_count": int(sys.argv[4]),
    "invariants_tested_count": int(sys.argv[5]),
    "invariants_tests_pass_rate": float(sys.argv[6]),
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
    "notes": "Testes de modelos e invariantes."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G1] status=$status inv_defined=$inv_defined inv_tested=$inv_tested"
