#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G5_frontend_observability"
SCORECARD_PATH="$SCORECARD_DIR/S20_G5_frontend_observability.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
status="PASS"
M5=1

echo "[S20_G5] Rodando npm test..."
if ! (cd "$FRONTEND_DIR" && npm test >"$EVIDENCE_DIR/npm_test.log" 2>&1); then
  status="FAIL"
fi

echo "[S20_G5] Rodando npm run build..."
if ! (cd "$FRONTEND_DIR" && npm run build >"$EVIDENCE_DIR/npm_build.log" 2>&1); then
  status="FAIL"
fi

python3 - <<'PY' "$ROOT_DIR/frontend/inspectah-ui/src" "$EVIDENCE_DIR/events_coverage.json"
import json, sys
from pathlib import Path

src_root = Path(sys.argv[1])
out_path = Path(sys.argv[2])

expected_events = [
    "consult.query_submitted",
    "consult.query_success",
    "consult.query_error",
    "admin.page_open",
    "admin.action_error",
    "cases.timeline_load",
    "cases.timeline_success",
    "cases.timeline_error",
    "cases.xray_load",
    "cases.xray_success",
    "cases.xray_error",
    "navigation",
    "ui_error",
]

def search(token: str) -> bool:
    for path in src_root.rglob("*.ts*"):
        if token in path.read_text(encoding="utf-8"):
            return True
    return False

coverage = {}
hits = 0
for event in expected_events:
    found = search(event)
    coverage[event] = found
    if found:
        hits += 1

M5 = hits / len(expected_events) if expected_events else 1.0
out_path.write_text(json.dumps({"coverage": coverage, "M5": M5}, indent=2), encoding="utf-8")
print(M5)
PY

M5=$(jq -r '.M5' "$EVIDENCE_DIR/events_coverage.json")
if (( $(echo "$M5 < 0.8" | bc -l) )); then
  status="FAIL"
fi

cat > "$EVIDENCE_DIR/README.md" <<'EOF'
# S20-G5 — Observabilidade de Frontend

Fluxos validados:
- npm test (inclui consultas, admin, timeline/xray com logs via MSW)
- npm run build
- Verificação de cobertura de eventos críticos (consult/admin/cases/navigation/ui_error)

M5 = eventos instrumentados / eventos planejados.
EOF

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$M5" "$commit_sha"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
M5 = float(sys.argv[3])
commit_sha = sys.argv[4]

scorecard = {
    "gate_id": "S20_G5_frontend_observability",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M5": M5},
    "details": {
        "commit": commit_sha,
        "notes": "Cobertura avaliada via scan estático de eventos críticos + testes/build.",
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G5] FAIL - revise logs e instrumentação")
PY

echo "[S20_G5] Scorecard gerado em $SCORECARD_PATH"
