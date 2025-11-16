#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G3_pipeline_fixtures"
LOG_FILE="$OUT_DIR/pipeline_tests.log"
INVARIANTS_REPORT="$OUT_DIR/invariants_report.json"
mkdir -p "$OUT_DIR"

status="PASS"
notes=()

run_pipeline_tests() {
  pushd "$ROOT_DIR" >/dev/null
  local pytest_available
  pytest_available=$(python3 - <<'PY'
try:
    import pytest  # noqa: F401
except Exception:
    print("no")
else:
    print("yes")
PY
)
  if [[ "$pytest_available" == "yes" ]]; then
    cmd=(python3 -m pytest tests/pipeline/test_pipeline_fixtures.py)
  else
    cmd=(python3 "$ROOT_DIR/bin/s5_pytest_shim.py" tests/pipeline/test_pipeline_fixtures.py)
  fi
  if ! "${cmd[@]}" 2>&1 | tee "$LOG_FILE"; then
    notes+=("Testes de pipeline falharam — ver $LOG_FILE")
    status="FAIL"
  fi
  popd >/dev/null
}

run_invariants_checker() {
  if ! output=$(python3 "$ROOT_DIR/scripts/s5_invariants_pipeline.py"); then
    notes+=("Invariantes falharam")
    status="FAIL"
  fi
  echo "$output" > "$INVARIANTS_REPORT"
}

run_pipeline_tests
run_invariants_checker

if [[ "$status" != "PASS" ]]; then
  echo "s5_check_invariants: FAIL"
  for note in "${notes[@]}"; do
    echo "- $note"
  done
  exit 1
fi

echo "s5_check_invariants: PASS"
