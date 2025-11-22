#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T4_golden_flows"
SCORECARD_PATH="$SCORECARD_DIR/S17_T4_golden_flows.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

cat > "$EVIDENCE_DIR/cases.md" <<'CASES'
# Casos canônicos de consulta (S17)
1. Pergunta consolidada com risco baixo e evidência robusta
2. Pergunta com risco alto (conflito/alerta)
3. Pergunta com risco incerto ou dados insuficientes
CASES

set +e
(cd "$FRONTEND_DIR" && npm run test -- src/__tests__/ConsultationPage.test.tsx) > "$EVIDENCE_DIR/golden_tests.log" 2>&1
TEST_STATUS=$?
set -e

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
    "gate": "S17_T4_golden_flows",
    "status": status,
    "details": {
        "objective": "Garantir flows canônicos de consulta com respostas e risco",
        "cases_doc": str(evidence_dir / "cases.md"),
        "tests_log": str(evidence_dir / "golden_tests.log"),
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T4] Falhou; revisar golden_tests.log")
PY

echo "[S17_T4] OK. Scorecard em $SCORECARD_PATH"
