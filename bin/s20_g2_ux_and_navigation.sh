#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G2_ux_and_navigation"
SCORECARD_PATH="$SCORECARD_DIR/S20_G2_ux_and_navigation.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
status="PASS"
M2=1

echo "[S20_G2] Rodando npm test..."
if ! (cd "$FRONTEND_DIR" && npm test >"$EVIDENCE_DIR/npm_test.log" 2>&1); then
  status="FAIL"
  M2=0
fi

cat > "$EVIDENCE_DIR/README.md" <<'EOF'
# S20-G2 — UX & Navegação

Cenários cobertos via suíte de testes existente (consulta, admin, timeline/raio-X) garantindo navegação protegida.
M2 = cenários ok / cenários totais (aqui representado pelos testes passando).
EOF

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$M2" "$commit_sha"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
M2 = float(sys.argv[3])
commit_sha = sys.argv[4]

scorecard = {
    "gate_id": "S20_G2_ux_and_navigation",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M2": M2},
    "details": {"commit": commit_sha},
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G2] FAIL - veja evidências para detalhes")
PY

echo "[S20_G2] Scorecard gerado em $SCORECARD_PATH"
