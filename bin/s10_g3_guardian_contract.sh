#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G3"
SCORECARD="$SCORECARD_DIR/S10_G3_guardian_contract.json"
LOG_FILE="$EVIDENCE_DIR/tests.log"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
git_commit="$(git -C "$ROOT_DIR" rev-parse HEAD)"
git_branch="$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD)"

status="PASS"
test_status="PASS"
valid_ratio_status="PASS"
invalid_ratio_status="PASS"

set +e
python3 "$ROOT_DIR/bin/s5_pytest_shim.py" \
  "$ROOT_DIR/tests/truthdb/test_actions_contract.py" \
  >"$LOG_FILE" 2>&1
shim_exit=$?
set -e
if [[ $shim_exit -ne 0 ]]; then
  test_status="FAIL"
  status="FAIL"
fi

python3 - <<'PY' "$EVIDENCE_DIR/contract_sli.json"
import json
import sys
from inspectah.truthdb import actions_contract

valid_cases = [
    ("criar_bloco_tema", {
        "id_bloco": "obra_1",
        "titulo": "Obra piloto",
        "descricao_curta": "desc",
        "dominio": "obras_publicas",
        "referencias_iniciais": ["fonte"],
    }),
    ("criar_fato_registravel", {
        "id_bloco": "obra_1",
        "id_fato": "obra_1_fato",
        "resumo_fato": "Prazo",
        "descricao_detalhada": "det",
        "estado_inicial": "planejado",
        "evidencias": ["fonte"],
        "relatorio_simples": "rel",
    }),
]

invalid_cases = [
    ("criar_bloco_tema", {"id_bloco": "obra"}),
    ("criar_versao_fato", {
        "id_fato": "obra_1_fato",
        "versao_id": "v1",
        "numero_versao": 1,
        "descricao": "desc",
        "estado": "estado_invalido",
        "evidencias": [],
        "hash_conteudo": "",
    }),
]

valid_hits = sum(
    1 for name, payload in valid_cases
    if actions_contract.validate_action_payload(name, payload).is_valid
)
invalid_hits = sum(
    1 for name, payload in invalid_cases
    if not actions_contract.validate_action_payload(name, payload).is_valid
)

summary = {
    "ratio_valid_actions_accepted": valid_hits / len(valid_cases),
    "ratio_invalid_actions_rejected": invalid_hits / len(invalid_cases),
    "samples": {
        "valid": valid_cases,
        "invalid": invalid_cases,
    },
}
with open(sys.argv[1], "w", encoding="utf-8") as fp:
    json.dump(summary, fp, indent=2)
PY

read_values=$(python3 - <<'PY' "$EVIDENCE_DIR/contract_sli.json"
import json, sys
from pathlib import Path
summary = json.loads(Path(sys.argv[1]).read_text())
print(summary["ratio_valid_actions_accepted"])
print(summary["ratio_invalid_actions_rejected"])
PY
)
valid_ratio=$(echo "$read_values" | sed -n '1p')
invalid_ratio=$(echo "$read_values" | sed -n '2p')

if [[ "$valid_ratio" != "1.0" && "$valid_ratio" != "1" ]]; then
  valid_ratio_status="FAIL"
  status="FAIL"
fi
if [[ "$invalid_ratio" != "1.0" && "$invalid_ratio" != "1" ]]; then
  invalid_ratio_status="FAIL"
  status="FAIL"
fi

cat >"$SCORECARD" <<JSON
{
  "gate_id": "S10_G3",
  "name": "Guardião action contract",
  "status": "$status",
  "slis": {
    "ratio_valid_actions_accepted": $valid_ratio,
    "ratio_invalid_actions_rejected": $invalid_ratio
  },
  "checks": [
    {
      "id": "contract-tests",
      "description": "Rodar tests/truthdb/test_actions_contract.py via shim",
      "status": "$test_status",
      "details": "Logs em tests.log"
    },
    {
      "id": "valid-actions",
      "description": "Medir ratio_valid_actions_accepted",
      "status": "$valid_ratio_status",
      "details": "valor=$valid_ratio"
    },
    {
      "id": "invalid-actions",
      "description": "Medir ratio_invalid_actions_rejected",
      "status": "$invalid_ratio_status",
      "details": "valor=$invalid_ratio"
    }
  ],
  "meta": {
    "ts": "$ts",
    "git_commit": "$git_commit",
    "branch": "$git_branch"
  }
}
JSON

if [[ "$status" == "FAIL" ]]; then
  exit 1
fi
exit 0
