#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G4_auth_and_protected_routes"
SCORECARD_PATH="$SCORECARD_DIR/S20_G4_auth_and_protected_routes.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
status="PASS"
M4=1

echo "[S20_G4] Rodando npm test..."
if ! (cd "$FRONTEND_DIR" && npm test >"$EVIDENCE_DIR/npm_test.log" 2>&1); then
  status="FAIL"
  M4=0
fi

echo "[S20_G4] Rodando npm run build..."
if ! (cd "$FRONTEND_DIR" && npm run build >"$EVIDENCE_DIR/npm_build.log" 2>&1); then
  status="FAIL"
  M4=0
fi

cat > "$EVIDENCE_DIR/README.md" <<'EOF'
# S20-G4 — Auth & rotas protegidas

Cenários validados:
- npm test (inclui testes de AuthGuard/login simulados)
- npm run build

M4 = proporção de cenários de auth corretos sobre o total (aqui, test + build). Score PASS somente se ambos ok.
EOF

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$M4" "$commit_sha"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
M4 = float(sys.argv[3])
commit_sha = sys.argv[4]

scorecard = {
    "gate_id": "S20_G4_auth_and_protected_routes",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M4": M4},
    "details": {
        "commit": commit_sha,
        "notes": "M4 = 1 quando testes e build passam, indicando rotas protegidas e fluxo de login/logout funcional nos testes automatizados."
    },
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G4] FAIL - veja logs em evidence para detalhes")
PY

echo "[S20_G4] Scorecard gerado em $SCORECARD_PATH"
