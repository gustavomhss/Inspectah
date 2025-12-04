#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT_DIR/out/evidence/S30_G1_flow_model_and_templates"
SCORECARD="$ROOT_DIR/out/scorecards/S30_G1_flow_model_and_templates.json"

mkdir -p "$LOG_DIR"
STATUS="PASS"
REASONS=()

echo "[s30-g1] Aplicando migrations e verificando template" | tee "$LOG_DIR/g1.log"

if ! python3 - <<'PY' 2>"$LOG_DIR/g1_errors.log"
import importlib
from app.flows.service import FlowService

flow_schema = importlib.import_module("migrations.versions.0030_s30_flow_model_v15")
tpl_seed = importlib.import_module("migrations.versions.0031_s30_flow_templates_seed")
db = flow_schema.DEFAULT_DB_PATH
flow_schema.apply_migration(db)
tpl_seed.apply_seed(db)
svc = FlowService(db_path=db)
templates = svc.list_templates()
assert any(t.slug == "fluxo_noticias_geral_v1" for t in templates)
print("[s30-g1] templates:", [t.slug for t in templates])
PY
then
  STATUS="FAIL"
  REASONS+=("Falha ao aplicar migrations/seed ou template ausente")
fi

REASONS_JSON=$(printf '%s\n' "${REASONS[@]:-}" | python3 -c "import sys,json; print(json.dumps([line.strip() for line in sys.stdin if line.strip()]))")

cat > "$SCORECARD" <<JSON
{
  "gate": "S30_G1_flow_model_and_templates",
  "status": "$STATUS",
  "reasons": $REASONS_JSON
}
JSON

echo "[s30-g1] status=$STATUS scorecard=$SCORECARD"
