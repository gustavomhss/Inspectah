#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T2_ux_and_accessibility"
SCORECARD_PATH="$SCORECARD_DIR/S17_T2_ux_and_accessibility.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

set +e
(cd "$FRONTEND_DIR" && npm run test -- src/__tests__/ResultContainer.test.tsx src/__tests__/ConsultationPage.test.tsx) > "$EVIDENCE_DIR/tests.log" 2>&1
TEST_STATUS=$?
set -e

cat > "$EVIDENCE_DIR/checklist.md" <<'CHECK'
# S17 T2 — UX e Acessibilidade Básica
- [x] Formulário com label e descrição clara
- [x] Input desativa durante envio
- [x] Estado vazio amigável comunica como usar
- [x] Estado de erro sem jargão técnico
- [x] Badges de risco com contraste e texto explícito
- [x] Suporte a teclado (Enter no formulário)
CHECK

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$TEST_STATUS"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
test_status = int(sys.argv[3])

status = "PASS" if test_status == 0 else "FAIL"
scorecard = {
    "gate": "S17_T2_ux_and_accessibility",
    "status": status,
    "details": {
        "objective": "Validar UX mínima, estados vazios e acessibilidade básica",
        "tests_log": str(evidence_dir / "tests.log"),
        "checklist": str(evidence_dir / "checklist.md"),
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T2] Falhou; revise checklist e testes.")
PY

echo "[S17_T2] OK. Scorecard em $SCORECARD_PATH"
