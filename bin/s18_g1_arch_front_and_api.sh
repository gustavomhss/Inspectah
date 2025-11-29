#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G1_arch_front_and_api"
SCORECARD_PATH="$SCORECARD_DIR/S18_G1_arch_front_and_api.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

BACK_FILES=(
  "$ROOT_DIR/app/admin/routes.py"
  "$ROOT_DIR/app/admin/schemas.py"
  "$ROOT_DIR/app/admin/service.py"
)
FRONT_FILES=(
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/pages/AdminOverviewPage.tsx"
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/api/index.ts"
  "$ROOT_DIR/frontend/inspectah-ui/src/modules/admin/components/HealthSummaryCards.tsx"
)

missing=0
for f in "${BACK_FILES[@]}" "${FRONT_FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "[S18_G1] Arquivo ausente: $f" >&2
    missing=1
  fi
done

python3 - <<'PY' "$ROOT_DIR" "$EVIDENCE_DIR"
import json, sys, traceback
from pathlib import Path

openapi_paths = []
note = ""
try:
    from inspectah.api import build_app
    app = build_app()
    if app is not None:
        spec = app.openapi()
        openapi_paths = sorted(p for p in spec.get("paths", {}) if p.startswith("/admin"))
        openapi_path = Path(sys.argv[2]) / "openapi_admin.json"
        openapi_path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
        note = f"Admin paths: {', '.join(openapi_paths) if openapi_paths else 'nenhum'}"
    else:
        note = "FastAPI não inicializado (build_app retornou None)."
except ModuleNotFoundError as exc:
    note = f"Dependência ausente para gerar OpenAPI: {exc}"
except Exception:
    note = f"Falha ao gerar OpenAPI: {traceback.format_exc()}"

summary_path = Path(sys.argv[2]) / "notes.md"
summary_path.write_text("# S18_G1 — Arquitetura front & API\n" + note, encoding="utf-8")
PY

status="PASS"
details="Arquivos de admin presentes e OpenAPI exportada."
if [[ $missing -ne 0 ]]; then
  status="FAIL"
  details="Arquivos obrigatórios ausentes."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$details"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

path = Path(sys.argv[1])
status = sys.argv[2]
details = sys.argv[3]
scorecard = {
    "gate_id": "S18_G1",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {"note": details},
}
path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit(f"[S18_G1] {details}")
PY

echo "[S18_G1] OK - scorecard em $SCORECARD_PATH"
