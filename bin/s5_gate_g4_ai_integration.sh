#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G4_ai_integration"
LOG_FILE="$OUT_DIR/tests.log"
SMOKE_LOG="$OUT_DIR/smoke.log"
SCORECARD="$OUT_DIR/scorecard.json"
mkdir -p "$OUT_DIR"

status="PASS"
notes=()
smoke_status="NOT_RUN"

declare -a REQUIRED_FILES=(
  "$ROOT_DIR/inspectah/config/ai_gpt_4_1mini.json"
  "$ROOT_DIR/inspectah/normalizer/client_ai.py"
  "$ROOT_DIR/inspectah/normalizer/normalizer.py"
  "$ROOT_DIR/tests/components/test_normalizer_stub.py"
  "$ROOT_DIR/tests/components/test_normalizer_ai_mode.py"
)

require_files() {
  for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
      notes+=("Arquivo obrigatório ausente: $file")
      status="FAIL"
    fi
  done
}

run_tests() {
  pushd "$ROOT_DIR" >/dev/null
  mapfile -t TEST_FILES < <(find tests/components -name 'test_normalizer*_*.py' -o -name 'test_normalizer*.py' | sort)
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
    cmd=(python3 -m pytest tests/components/test_normalizer*.py)
  else
    cmd=(python3 "$ROOT_DIR/bin/s5_pytest_shim.py" tests/components/test_normalizer_stub.py tests/components/test_normalizer_ai_mode.py)
  fi
  if ! "${cmd[@]}" 2>&1 | tee "$LOG_FILE"; then
    notes+=("Testes de normalizer falharam — ver $LOG_FILE")
    status="FAIL"
  fi
  popd >/dev/null
}

run_smoke() {
  if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    notes+=("OPENAI_API_KEY ausente — smoke real não executado")
    return
  fi
  if ! command -v python3 >/dev/null; then
    notes+=("python3 não disponível para rodar o smoke")
    status="FAIL"
    return
  fi
  if ! python3 "$ROOT_DIR/scripts/s5_ai_smoke_gpt4mini.py" 2>&1 | tee "$SMOKE_LOG"; then
    notes+=("Smoke GPT-4.1 mini falhou — ver $SMOKE_LOG")
    status="FAIL"
    smoke_status="FAIL"
  else
    smoke_status="PASS"
  fi
}

extract_tests_run() {
  python3 - "$LOG_FILE" <<'PY'
import re
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text() if Path(sys.argv[1]).exists() else ""
match = re.search(r"collected (\d+) items", text)
if not match:
    match = re.search(r"Ran (\d+) tests?", text)
print(match.group(1) if match else "0")
PY
}

require_files
run_tests
run_smoke

tests_run=$(extract_tests_run)
metrics_json=$(python3 - <<PY
import json
print(json.dumps({
    "tests_run": int("$tests_run" or 0),
    "smoke_status": "$smoke_status"
}))
PY
)

notes_text="PASS"
if [[ ${#notes[@]} -gt 0 ]]; then
  notes_text=$(printf '%s; ' "${notes[@]}")
  notes_text=${notes_text::-2}
fi

cat <<JSON > "$SCORECARD"
{
  "gate_id": "G4",
  "status": "${status}",
  "checked_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "notes": "${notes_text}",
  "metrics": ${metrics_json}
}
JSON

if [[ "$status" != "PASS" ]]; then
  echo "G4 AI Integration -> FAIL"
  echo "Notas: ${notes_text}"
  exit 1
fi

echo "G4 AI Integration -> PASS"
