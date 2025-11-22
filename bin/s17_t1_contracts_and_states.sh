#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T1_contracts_and_states"
SCORECARD_PATH="$SCORECARD_DIR/S17_T1_contracts_and_states.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

set +e
(cd "$FRONTEND_DIR" && npm run test -- src/__tests__/ResultContainer.test.tsx src/__tests__/ConsultationPage.test.tsx) > "$EVIDENCE_DIR/tests.log" 2>&1
TEST_STATUS=$?
set -e

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$FRONTEND_DIR" "$TEST_STATUS"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
frontend_dir = Path(sys.argv[3])
test_status = int(sys.argv[4])

types_path = frontend_dir / "src" / "types" / "inspectah.ts"
has_types = types_path.exists() and "ConsultationStatus" in types_path.read_text(encoding="utf-8")

status = "PASS" if test_status == 0 and has_types else "FAIL"
scorecard = {
    "gate": "S17_T1_contracts_and_states",
    "status": status,
    "details": {
        "objective": "Garantir máquina de estados explícita e contratos UI↔API",
        "tests_log": str(evidence_dir / "tests.log"),
        "types_present": has_types,
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T1] Falhou; consulte evidências e contratos.")
PY

echo "[S17_T1] OK. Scorecard em $SCORECARD_PATH"
