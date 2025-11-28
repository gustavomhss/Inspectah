#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_G5_threatmodel_signals_and_metrics"
SCORECARD_PATH="$SCORECARD_DIR/S25_G5_threatmodel_signals_and_metrics.json"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

THRESHOLD_LOG="$EVIDENCE_DIR/thresholds.log"
TEST_LOG="$EVIDENCE_DIR/pytest.log"

status="GO"
schema_status="PASS"
test_status="PASS"

echo "[S25_G5] Validando thresholds de threatmodel..." | tee "$THRESHOLD_LOG"
if ! python3 - <<'PY' >"$THRESHOLD_LOG" 2>&1
from pathlib import Path
from app.threatmodel.service import load_thresholds

load_thresholds(Path("configs/threatmodel/thresholds.yaml"))
print("thresholds ok")
PY
then
  schema_status="FAIL"
  status="NO_GO"
fi

echo "[S25_G5] Rodando testes de threatmodel..." | tee "$TEST_LOG"
set +e
PYTHONPATH="$ROOT_DIR" pytest "$ROOT_DIR/tests/threatmodel" -q >>"$TEST_LOG" 2>&1
pytest_exit=$?
set -e
if [[ $pytest_exit -ne 0 ]]; then
  test_status="FAIL"
  status="NO_GO"
fi

tests_passed=$(grep -Eo "[0-9]+ passed" "$TEST_LOG" | awk '{print $1}' | tail -n1)
tests_passed=${tests_passed:-0}

cat >"$SCORECARD_PATH" <<JSON
{
  "gate_id": "S25_G5",
  "gate_name": "threatmodel_signals_and_metrics",
  "sprint": "S25",
  "status": "$status",
  "timestamp": "$ts",
  "commit_sha": "$git_commit",
  "inputs": {
    "branch": "$git_branch"
  },
  "metrics": {
    "tests_passed": $tests_passed,
    "thresholds_valid": "$schema_status",
    "test_status": "$test_status"
  },
  "human_code_score": {
    "applied": true,
    "score": 0.6,
    "notes": "Computações e thresholds simples, testados."
  },
  "risks": [],
  "notes": "Evidências em $EVIDENCE_DIR"
}
JSON

if [[ "$status" != "GO" ]]; then
  echo "[S25_G5] NO_GO - confira $SCORECARD_PATH"
  exit 1
fi

echo "[S25_G5] GO - scorecard em $SCORECARD_PATH"
