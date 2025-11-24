#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S21_G2_modelo_dados"
SCORECARD_PATH="$SCORECARD_DIR/S21_G2_modelo_dados.json"
DB_PATH="$ROOT_DIR/out/databases/s21_sources.sqlite"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR" "$ROOT_DIR/out/databases"

doc_model="$ROOT_DIR/docs/sprint_21_modelo_dados_fontes.md"
doc_ciclo="$ROOT_DIR/docs/sprint_21_ciclo_vida_fontes.md"

status="PASS"
notes="Modelo e ciclo de vida ok."

if [[ ! -f "$doc_model" || ! -f "$doc_ciclo" ]]; then
  status="FAIL"
  notes="Docs de modelo/ciclo ausentes."
fi

echo "[S21_G2] Aplicando migration de schema..." > "$EVIDENCE_DIR/migration.log"
if ! python3 "$ROOT_DIR/migrations/versions/0002_s21_sources_schema.py" "$DB_PATH" >> "$EVIDENCE_DIR/migration.log" 2>&1; then
  status="FAIL"
  notes="Falha ao aplicar migration 0002."
fi

echo "[S21_G2] Rodando testes de domínio/serviço..." > "$EVIDENCE_DIR/tests.log"
if ! (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/sources -k "domain or service" -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  status="FAIL"
  notes="Testes de domínio/serviço falharam."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes"
import json, sys
from datetime import datetime, timezone
from pathlib import Path
scorecard = {
    "gate_id": "S21_G2",
    "status": sys.argv[2],
    "automated_checks": {"status": sys.argv[2], "details": sys.argv[3]},
    "reviewers_internal": [],
    "reviewers_external": [],
    "risk_level": "low" if sys.argv[2] == "PASS" else "high",
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
    "notes": "Migration 0002 + testes de domínio/serviço."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S21_G2] status=$status"
