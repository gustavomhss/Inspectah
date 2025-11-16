#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G1_schema_contracts"
LOG_FILE="$OUT_DIR/tests.log"
SCORECARD="$OUT_DIR/scorecard.json"
CONTRACTS_FILE="$ROOT_DIR/docs/sprint_5/s5_contracts_overview.md"

mkdir -p "$OUT_DIR"

now_iso="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
status="PASS"
notes=()

declare -a TESTS=(
  "tests/test_schema_item.py"
  "tests/test_schema_claim.py"
  "tests/test_equivalence_key.py"
)

run_tests() {
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
    test_cmd=(python3 -m pytest "${TESTS[@]}")
  else
    test_cmd=(python3 "$ROOT_DIR/bin/s5_pytest_shim.py" "${TESTS[@]}")
  fi
  if ! "${test_cmd[@]}" 2>&1 | tee "$LOG_FILE"; then
    notes+=("Testes falharam — ver $LOG_FILE")
    status="FAIL"
  fi
  popd >/dev/null
}

check_schema_enum() {
  local schema_file="$1"
  local json_path="$2"
  shift 2
  local expected=("$@")
  local result
  result=$(python3 - "$schema_file" "$json_path" "${expected[@]}" <<'PY'
import json
import sys
from pathlib import Path

schema = Path(sys.argv[1])
path = sys.argv[2]
expected = sys.argv[3:]

data = json.loads(schema.read_text())
node = data
for part in path.split('.'):
    if part not in node:
        print(f"missing:{path}")
        sys.exit(1)
    node = node[part]
if not isinstance(node, list):
    print("path_is_not_list")
    sys.exit(2)
missing = [v for v in expected if v not in node]
if missing:
    print("missing_values:" + ",".join(missing))
    sys.exit(3)
print("ok")
PY
  ) || true
  if [[ "$result" != "ok" ]]; then
    notes+=("Enum inconsistente em ${schema_file} ${json_path}: ${result}")
    status="FAIL"
  fi
}

require_file() {
  local label="$1"
  local path="$2"
  if [[ ! -f "$path" ]]; then
    notes+=("Falta ${label}: ${path}")
    status="FAIL"
  fi
}

SCHEMA_ITEM="$ROOT_DIR/schemas/inspectah_item_v0_1.json"
SCHEMA_CLAIM="$ROOT_DIR/schemas/inspectah_claim_v0_1.json"

require_file "Schema Item" "$SCHEMA_ITEM"
require_file "Schema Claim" "$SCHEMA_CLAIM"
require_file "Contracts overview" "$CONTRACTS_FILE"

check_schema_enum "$SCHEMA_ITEM" "properties.state.enum" "S0" "S1" "S2" "S3" "S4"
check_schema_enum "$SCHEMA_CLAIM" "properties.claim_type.enum" \
  "resultado_binario" "resultado_numerico" "estado_evento" "data_evento" "classificacao"
check_schema_enum "$SCHEMA_CLAIM" "properties.polarity.enum" \
  "afirma_que_e_verdade" "afirma_que_e_falso" "informa_sem_julgar" "indeterminado"
check_schema_enum "$SCHEMA_CLAIM" "properties.local_verdict.enum" \
  "segundo_esta_fonte_este_e_o_valor" \
  "segundo_esta_fonte_isto_ocorreu" \
  "segundo_esta_fonte_isto_nao_ocorreu" \
  "segundo_esta_fonte_ainda_esta_pendente" \
  "nao_ha_veredito_claro"

run_tests

tests_run=$(python3 - "$LOG_FILE" <<'PY'
import re
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text() if Path(sys.argv[1]).exists() else ""
match = re.search(r"collected (\d+) items", text)
if not match:
    match = re.search(r"Ran (\d+) tests?", text)
print(match.group(1) if match else "0")
PY
)

notes_text="PASS"
if [[ ${#notes[@]} -gt 0 ]]; then
  notes_text=$(printf '%s; ' "${notes[@]}")
  notes_text=${notes_text::-2}
fi

cat <<JSON > "$SCORECARD"
{
  "gate_id": "G1",
  "status": "${status}",
  "checked_at": "${now_iso}",
  "notes": "${notes_text}",
  "metrics": {"tests_run": ${tests_run}}
}
JSON

if [[ "$status" == "PASS" ]]; then
  echo "G1 Schema & Contracts -> PASS (${tests_run} testes)"
else
  echo "G1 Schema & Contracts -> FAIL"
  echo "Notas: ${notes_text}"
  exit 1
fi
