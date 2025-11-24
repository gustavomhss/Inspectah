#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G6_cenarios_uso"
SCORECARD_PATH="$SCORECARD_DIR/S21_G6_cenarios_uso.json"
DB_PATH="$ROOT_DIR/out/databases/s21_sources.sqlite"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR" "$ROOT_DIR/out/databases"

doc="$ROOT_DIR/docs/sprint_21_cenarios_uso_fontes.md"
status="PASS"
notes="Cenários seedados e testados."

if [[ ! -f "$doc" ]]; then
  status="FAIL"
  notes="Documento de cenários ausente."
fi

echo "[S21_G6] Aplicando migrations de seeds..." > "$EVIDENCE_DIR/migration_seeds.log"
if ! python3 "$ROOT_DIR/migrations/versions/0002_s21_sources_schema.py" "$DB_PATH" >> "$EVIDENCE_DIR/migration_seeds.log" 2>&1; then
  status="FAIL"; notes="Falha migration 0002."
fi
if ! python3 "$ROOT_DIR/migrations/versions/0003_s21_sources_seed_examples.py" "$DB_PATH" >> "$EVIDENCE_DIR/migration_seeds.log" 2>&1; then
  status="FAIL"; notes="Falha migration 0003 seeds."
fi

echo "[S21_G6] Rodando teste de integração de healthcheck..." > "$EVIDENCE_DIR/tests.log"
if ! (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/sources -k "healthcheck_integration" -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  status="FAIL"
  notes="Teste de healthcheck/seed falhou."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G6",
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
    "notes": "Cenários e seeds verificados; teste de healthcheck executado."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G6] status=$status"
