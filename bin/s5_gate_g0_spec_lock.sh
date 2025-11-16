#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G0_spec_lock"
SCORECARD="$OUT_DIR/scorecard.json"
CHECKLIST="$ROOT_DIR/docs/sprint_5/gates/G0_spec_lock_checklist.md"

mkdir -p "$OUT_DIR"

now_iso="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
status="PASS"
notes=()

require_file() {
  local label="$1"
  local path="$2"
  if [[ ! -f "$path" ]]; then
    notes+=("Falta ${label}: ${path}")
    status="FAIL"
  fi
}

# Capítulo 1 v6 precisa existir
require_file "Capítulo 1" "$ROOT_DIR/docs/sprint_5/s5_capitulo_1_core_v6.md"
require_file "Capítulo 2" "$ROOT_DIR/docs/sprint_5/s5_capitulo_2_gates_v2.md"
require_file "Capítulo 3" "$ROOT_DIR/docs/sprint_5/s5_capitulo_3_filemap_plano_v2.md"
require_file "Capítulo 4" "$ROOT_DIR/docs/sprint_5/s5_capitulo_4_execucao_codex_v2.md"

# check drafts/wip
if [[ -d "$ROOT_DIR/docs/sprint_5" ]]; then
  mapfile -t drafts < <(find "$ROOT_DIR/docs/sprint_5" -maxdepth 1 -type f \( -name '*_draft*' -o -name '*_wip*' \)) || true
  if [[ ${#drafts[@]} -gt 0 ]]; then
    notes+=("Encontrados arquivos draft/wip: ${drafts[*]}")
    status="FAIL"
  fi
fi

# Consistência básica com schemas: estados e enums
EXPECTED_STATES=("S0" "S1" "S2" "S3" "S4")
EXPECTED_CLAIM_TYPES=("resultado_binario" "resultado_numerico" "estado_evento" "data_evento" "classificacao")
EXPECTED_POLARITY=("afirma_que_e_verdade" "afirma_que_e_falso" "informa_sem_julgar" "indeterminado")
EXPECTED_VERDICT=("segundo_esta_fonte_este_e_o_valor" "segundo_esta_fonte_isto_ocorreu" "segundo_esta_fonte_isto_nao_ocorreu" "segundo_esta_fonte_ainda_esta_pendente" "nao_ha_veredito_claro")

SCHEMA_ITEM="$ROOT_DIR/schemas/inspectah_item_v0_1.json"
SCHEMA_CLAIM="$ROOT_DIR/schemas/inspectah_claim_v0_1.json"

check_schema_enum() {
  local schema_file="$1"
  local json_path="$2"
  shift 2
  local expected=("$@")
  if [[ ! -f "$schema_file" ]]; then
    notes+=("Schema ausente: ${schema_file}")
    status="FAIL"
    return
  fi
  local check_result
  if ! check_result=$(python3 - "$schema_file" "$json_path" "${expected[@]}" <<'PY'
import json
import sys
from pathlib import Path

schema_file = Path(sys.argv[1])
json_path = sys.argv[2]
expected = sys.argv[3:]

data = json.loads(schema_file.read_text())
node = data
for part in json_path.split('.'):
    if part not in node:
        print(f"missing:{json_path}")
        sys.exit(1)
    node = node[part]

if not isinstance(node, list):
    print("path_is_not_list")
    sys.exit(2)
missing = [value for value in expected if value not in node]
if missing:
    print("missing_values:" + ",".join(missing))
    sys.exit(3)
print("ok")
PY
); then
    notes+=("Falha ao ler schema ${schema_file}: ${check_result}")
    status="FAIL"
  else
    if [[ "$check_result" != "ok" ]]; then
      notes+=("Inconsistência ${schema_file} ${json_path}: ${check_result}")
      status="FAIL"
    fi
  fi
}

check_schema_enum "$SCHEMA_ITEM" "properties.state.enum" "${EXPECTED_STATES[@]}"
check_schema_enum "$SCHEMA_CLAIM" "properties.claim_type.enum" "${EXPECTED_CLAIM_TYPES[@]}"
check_schema_enum "$SCHEMA_CLAIM" "properties.polarity.enum" "${EXPECTED_POLARITY[@]}"
check_schema_enum "$SCHEMA_CLAIM" "properties.local_verdict.enum" "${EXPECTED_VERDICT[@]}"

metrics_json=$(python3 - <<'PY'
from datetime import datetime
print('{"checked_fields":4}')
PY
)

notes_text="PASS"
if [[ ${#notes[@]} -gt 0 ]]; then
  notes_text=$(printf '%s; ' "${notes[@]}")
  notes_text=${notes_text::-2}
fi

cat <<JSON > "$SCORECARD"
{
  "gate_id": "G0",
  "status": "${status}",
  "checked_at": "${now_iso}",
  "notes": "${notes_text}",
  "metrics": ${metrics_json}
}
JSON

echo "G0 Spec Lock -> ${status}"
if [[ "$status" != "PASS" ]]; then
  echo "Notas: ${notes_text}"
  exit 1
fi

exit 0
