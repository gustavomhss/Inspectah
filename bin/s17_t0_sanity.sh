#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_T0_sanity"
SCORECARD_PATH="$SCORECARD_DIR/S17_T0_sanity.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

if [[ ! -d "$FRONTEND_DIR" ]]; then
  >&2 echo "[S17_T0] Projeto de frontend não encontrado em $FRONTEND_DIR"
  exit 2
fi

set +e
(cd "$FRONTEND_DIR" && npm ci --prefer-offline) > "$EVIDENCE_DIR/npm_ci.log" 2>&1
INSTALL_STATUS=$?
(cd "$FRONTEND_DIR" && npm run lint) > "$EVIDENCE_DIR/lint.log" 2>&1
LINT_STATUS=$?
(cd "$FRONTEND_DIR" && npm run test) > "$EVIDENCE_DIR/test.log" 2>&1
TEST_STATUS=$?
(cd "$FRONTEND_DIR" && npm run build) > "$EVIDENCE_DIR/build.log" 2>&1
BUILD_STATUS=$?
set -e

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$INSTALL_STATUS" "$LINT_STATUS" "$TEST_STATUS" "$BUILD_STATUS"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
install_status, lint_status, test_status, build_status = map(int, sys.argv[3:])

commands = [
    {"name": "npm ci", "exit_code": install_status, "log": str(evidence_dir / "npm_ci.log")},
    {"name": "npm run lint", "exit_code": lint_status, "log": str(evidence_dir / "lint.log")},
    {"name": "npm run test", "exit_code": test_status, "log": str(evidence_dir / "test.log")},
    {"name": "npm run build", "exit_code": build_status, "log": str(evidence_dir / "build.log")},
]

status = "PASS" if all(cmd["exit_code"] == 0 for cmd in commands) else "FAIL"
scorecard = {
    "gate": "S17_T0_sanity",
    "status": status,
    "details": {
        "objective": "Sanidade do projeto de frontend da Sprint 17",
        "commands": commands,
    },
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "evidence": [str(evidence_dir)],
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_T0] Falhou; consulte evidências e scorecard.")
PY

echo "[S17_T0] OK. Scorecard em $SCORECARD_PATH"
