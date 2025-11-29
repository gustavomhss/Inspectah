#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_G4_console_and_agent_studio"
SCORECARD_PATH="$SCORECARD_DIR/S25_G4_console_and_agent_studio.json"
FRONT_DIR="$ROOT_DIR/frontend/inspectah-ui"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

BUILD_LOG="$EVIDENCE_DIR/frontend_build.log"
TEST_LOG="$EVIDENCE_DIR/frontend_test.log"

status="GO"
build_status="PASS"
test_status="PASS"

echo "[S25_G4] Instalando dependências do frontend..." | tee "$BUILD_LOG"
(cd "$FRONT_DIR" && npm ci >>"$BUILD_LOG" 2>&1)

echo "[S25_G4] Rodando testes do frontend..." | tee "$TEST_LOG"
set +e
(cd "$FRONT_DIR" && npm test >>"$TEST_LOG" 2>&1)
test_exit=$?
set -e
if [[ $test_exit -ne 0 ]]; then
  test_status="FAIL"
  status="NO_GO"
fi

echo "[S25_G4] Build do frontend..." | tee -a "$BUILD_LOG"
set +e
(cd "$FRONT_DIR" && npm run build >>"$BUILD_LOG" 2>&1)
build_exit=$?
set -e
if [[ $build_exit -ne 0 ]]; then
  build_status="FAIL"
  status="NO_GO"
fi

cat >"$SCORECARD_PATH" <<JSON
{
  "gate_id": "S25_G4",
  "gate_name": "console_and_agent_studio",
  "sprint": "S25",
  "status": "$status",
  "timestamp": "$ts",
  "commit_sha": "$git_commit",
  "inputs": {
    "branch": "$git_branch"
  },
  "metrics": {
    "frontend_tests": "$test_status",
    "frontend_build": "$build_status"
  },
  "human_code_score": {
    "applied": true,
    "score": 0.6,
    "notes": "Console/Agent Studio mínimos com build e testes."
  },
  "risks": [],
  "notes": "Evidências em $EVIDENCE_DIR"
}
JSON

if [[ "$status" != "GO" ]]; then
  echo "[S25_G4] NO_GO - confira $SCORECARD_PATH"
  exit 1
fi

echo "[S25_G4] GO - scorecard em $SCORECARD_PATH"
