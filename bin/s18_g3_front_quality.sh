#!/usr/bin/env bash
set -euo pipefail

echo "[S18_G3] Iniciando gate de qualidade do frontend..."

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend/inspectah-ui"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G3_front_quality"
SCORECARD_PATH="$SCORECARD_DIR/S18_G3_front_quality.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

if [[ ! -d "$FRONTEND_DIR" ]]; then
  echo "[S18_G3] Diretório do frontend não encontrado em $FRONTEND_DIR" >&2
  exit 2
fi

set +e
echo "[S18_G3] Rodando npm ci..."
(cd "$FRONTEND_DIR" && rm -rf node_modules && npm ci --prefer-offline --no-fund --no-audit) > "$EVIDENCE_DIR/npm_ci.log" 2>&1
INSTALL_STATUS=$?
echo "[S18_G3] Rodando npm run lint..."
(cd "$FRONTEND_DIR" && npm run lint) > "$EVIDENCE_DIR/lint.log" 2>&1
LINT_STATUS=$?
echo "[S18_G3] Rodando npm run test (modo não interativo, suite admin)..."
(cd "$FRONTEND_DIR" && NODE_OPTIONS="--max-old-space-size=4096" npm run test -- \
  src/__tests__/admin/AdminPages.test.tsx \
  src/__tests__/admin/AdminAgentsPages.test.tsx \
  src/__tests__/admin/AdminAgentsFlowPage.test.tsx \
  --watch=false --fileParallelism=false --max-workers=50%) > "$EVIDENCE_DIR/test.log" 2>&1
TEST_STATUS=$?
echo "[S18_G3] Rodando npm run build..."
(cd "$FRONTEND_DIR" && npm run build) > "$EVIDENCE_DIR/build.log" 2>&1
BUILD_STATUS=$?
set -e

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR" "$INSTALL_STATUS" "$LINT_STATUS" "$TEST_STATUS" "$BUILD_STATUS"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
install_status, lint_status, test_status, build_status = map(int, sys.argv[3:])

commands = [
    {"name": "npm ci", "exit_code": install_status, "log": str(evidence_dir / "npm_ci.log")},
    {"name": "npm run lint", "exit_code": lint_status, "log": str(evidence_dir / "lint.log")},
    {"name": "npm run test -- --watch=false", "exit_code": test_status, "log": str(evidence_dir / "test.log")},
    {"name": "npm run build", "exit_code": build_status, "log": str(evidence_dir / "build.log")},
]

status = "PASS" if all(cmd["exit_code"] == 0 for cmd in commands) else "FAIL"
scorecard = {
    "gate_id": "S18_G3",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {
        "commands": commands,
        "note": "Qualidade do frontend (lint/test/build) incluindo rotas de admin.",
    },
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S18_G3] Falhou; veja logs em evidence.")
PY

echo "[S18_G3] OK - scorecard em $SCORECARD_PATH"
echo "[S18_G3] Gate de qualidade do frontend concluído com sucesso."
