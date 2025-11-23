#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G2_journeys_and_ux"
SCORECARD_PATH="$SCORECARD_DIR/S19_G2_journeys_and_ux.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

set +e
(cd "$FRONTEND_DIR" && npm run test -- --watch=false src/__tests__/admin/AdminTimelineXRay.test.tsx) > "$EVIDENCE_DIR/test.log" 2>&1
TEST_STATUS=$?
set -e

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$TEST_STATUS"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
test_status = int(sys.argv[3])

status = "PASS" if test_status == 0 else "FAIL"
scorecard = {
    "gate_id": "S19_G2",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {
        "tests": [
            {
                "name": "AdminTimelineXRay.test.tsx",
                "exit_code": test_status,
                "log": str(evidence_dir / "test.log"),
            }
        ]
    },
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G2] Falhou jornada de timeline/raio-x")
PY

echo "[S19_G2] OK - scorecard em $SCORECARD_PATH"
