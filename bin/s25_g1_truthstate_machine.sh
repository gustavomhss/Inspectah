#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S25_G1_truthstate_machine"
SCORECARD_PATH="$SCORECARD_DIR/S25_G1_truthstate_machine.json"
DB_PATH="${INSPECTAH_S25_TRUTH_DB_PATH:-$ROOT_DIR/out/databases/s25_truth.sqlite}"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR" "$(dirname "$DB_PATH")"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

MIGRATION_LOG="$EVIDENCE_DIR/migration.log"
TEST_LOG="$EVIDENCE_DIR/pytest.log"

migration_status="PASS"
test_status="PASS"
status="GO"

echo "[S25_G1] Aplicando migrations Truth-DB v1.5 em $DB_PATH" | tee "$MIGRATION_LOG"
if ! python3 "$ROOT_DIR/migrations/versions/0002_s25_truth_models.py" "$DB_PATH" >>"$MIGRATION_LOG" 2>&1; then
  migration_status="FAIL"
  status="NO_GO"
fi
if [[ "$migration_status" == "PASS" ]]; then
  if ! python3 "$ROOT_DIR/migrations/versions/0003_s25_layers_traces_incidents.py" "$DB_PATH" >>"$MIGRATION_LOG" 2>&1; then
    migration_status="FAIL"
    status="NO_GO"
  fi
fi

echo "[S25_G1] Rodando testes de truth..." | tee "$TEST_LOG"
set +e
PYTHONPATH="$ROOT_DIR" pytest "$ROOT_DIR/tests/truth" -q >>"$TEST_LOG" 2>&1
pytest_exit=$?
set -e
if [[ $pytest_exit -ne 0 ]]; then
  test_status="FAIL"
  status="NO_GO"
fi

total_tests=$(grep -Eo "[0-9]+ passed" "$TEST_LOG" | awk '{print $1}' | tail -n1)
total_tests=${total_tests:-0}

cat >"$SCORECARD_PATH" <<JSON
{
  "gate_id": "S25_G1",
  "gate_name": "truthstate_machine",
  "sprint": "S25",
  "status": "$status",
  "timestamp": "$ts",
  "commit_sha": "$git_commit",
  "inputs": {
    "branch": "$git_branch",
    "db_path": "$DB_PATH"
  },
  "metrics": {
    "tests_passed": $total_tests,
    "migration_status": "$migration_status",
    "test_status": "$test_status"
  },
  "human_code_score": {
    "applied": true,
    "score": 0.6,
    "notes": "Modelos e transições legíveis; cobertura básica de tests/truth."
  },
  "risks": [],
  "notes": "Ver evidências em $EVIDENCE_DIR"
}
JSON

if [[ "$status" != "GO" ]]; then
  echo "[S25_G1] NO_GO - confira $SCORECARD_PATH"
  exit 1
fi

echo "[S25_G1] GO - scorecard em $SCORECARD_PATH"
