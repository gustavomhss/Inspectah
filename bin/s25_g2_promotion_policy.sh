#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_G2_promotion_policy"
SCORECARD_PATH="$SCORECARD_DIR/S25_G2_promotion_policy.json"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

SCHEMA_LOG="$EVIDENCE_DIR/policy_schema.log"
TEST_LOG="$EVIDENCE_DIR/pytest.log"

status="GO"
schema_status="PASS"
test_status="PASS"

echo "[S25_G2] Validando policies em configs/promotion_policies..." | tee "$SCHEMA_LOG"
if ! python3 -m app.policies.schema >>"$SCHEMA_LOG" 2>&1; then
  schema_status="FAIL"
  status="NO_GO"
fi

echo "[S25_G2] Rodando testes de policies..." | tee "$TEST_LOG"
set +e
PYTHONPATH="$ROOT_DIR" pytest "$ROOT_DIR/tests/policies" -q >>"$TEST_LOG" 2>&1
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
  "gate_id": "S25_G2",
  "gate_name": "promotion_policy",
  "sprint": "S25",
  "status": "$status",
  "timestamp": "$ts",
  "commit_sha": "$git_commit",
  "inputs": {
    "branch": "$git_branch"
  },
  "metrics": {
    "tests_passed": $tests_passed,
    "schema_status": "$schema_status",
    "test_status": "$test_status"
  },
  "human_code_score": {
    "applied": true,
    "score": 0.6,
    "notes": "Engine e configs declarativas simples validadas por testes."
  },
  "risks": [],
  "notes": "Evidências em $EVIDENCE_DIR"
}
JSON

if [[ "$status" != "GO" ]]; then
  echo "[S25_G2] NO_GO - confira $SCORECARD_PATH"
  exit 1
fi

echo "[S25_G2] GO - scorecard em $SCORECARD_PATH"
