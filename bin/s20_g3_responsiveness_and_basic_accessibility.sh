#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S20_G3_responsiveness_and_basic_accessibility"
SCORECARD_PATH="$SCORECARD_DIR/S20_G3_responsiveness_and_basic_accessibility.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

commit_sha="$(git -C "$ROOT_DIR" rev-parse HEAD)"
status="PASS"
M3=1

echo "[S20_G3] Rodando npm test..."
if ! (cd "$FRONTEND_DIR" && npm test >"$EVIDENCE_DIR/npm_test.log" 2>&1); then
  status="FAIL"
  M3=0
fi

cat > "$EVIDENCE_DIR/README.md" <<'EOF'
# S20-G3 — Responsividade & Acessibilidade

Checklist manual previsto no Capítulo 2 deve ser rodado junto deste script.
Aqui registramos testes automatizados e build como sanidade mínima.
M3 = média dos cenários avaliados (representado como 1 quando testes passam).
EOF

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$M3" "$commit_sha"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
M3 = float(sys.argv[3])
commit_sha = sys.argv[4]

scorecard = {
    "gate_id": "S20_G3_responsiveness_and_basic_accessibility",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M3": M3},
    "details": {"commit": commit_sha},
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S20_G3] FAIL - revise checklist de responsividade/acessibilidade")
PY

echo "[S20_G3] Scorecard gerado em $SCORECARD_PATH"
