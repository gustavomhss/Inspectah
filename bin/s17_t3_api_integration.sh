#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T3_api_integration"
SCORECARD_PATH="$SCORECARD_DIR/S17_T3_api_integration.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

set +e
(cd "$FRONTEND_DIR" && npm run test -- src/__tests__/ConsultationPage.test.tsx) > "$EVIDENCE_DIR/api_tests.log" 2>&1
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

scenarios = [
    "sucesso com dados",
    "risco alto",
    "risco desconhecido",
    "erro 4xx",
    "erro 5xx",
    "falha de rede",
]
status = "PASS" if test_status == 0 else "FAIL"
scorecard = {
    "gate": "S17_T3_api_integration",
    "status": status,
    "details": {
        "objective": "Cobrir integração UI↔API de consulta com cenários de sucesso e erro",
        "tests_log": str(evidence_dir / "api_tests.log"),
        "scenarios": scenarios,
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T3] Falhou; verifique api_tests.log")
PY

echo "[S17_T3] OK. Scorecard em $SCORECARD_PATH"
