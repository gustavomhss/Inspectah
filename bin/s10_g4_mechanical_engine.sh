#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S10_G4"
SCORECARD="$SCORECARD_DIR/S10_G4_mechanical_engine.json"
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
  "$ROOT_DIR/tests/truthdb/test_engine.py" \
  >"$LOG_FILE" 2>&1
shim_exit=$?
set -e
if [[ $shim_exit -ne 0 ]]; then
  test_status="FAIL"
  status="FAIL"
fi

python3 - <<'PY' "$EVIDENCE_DIR/engine_sli.json"
import json
import sys
from inspectah.truthdb.engine import TruthDBEngine

def bloco_payload():
    return {
        "id_bloco": "obra_1",
        "titulo": "Obra piloto",
        "descricao_curta": "desc",
        "dominio": "obras_publicas",
        "referencias_iniciais": ["fonte"],
    }

def fato_payload():
    return {
        "id_bloco": "obra_1",
        "id_fato": "obra_1_fato",
        "resumo_fato": "Prazo oficial",
        "descricao_detalhada": "detalhe",
        "estado_inicial": "planejado",
        "evidencias": ["fonte"],
        "relatorio_simples": "relatorio",
    }

def versao_payload():
    return {
        "id_fato": "obra_1_fato",
        "versao_id": "v1",
        "numero_versao": 1,
        "descricao": "Versão inicial",
        "estado": "planejado",
        "evidencias": ["fonte"],
        "hash_conteudo": "hash_v1",
    }

def update_payload():
    return {
        "id_fato": "obra_1_fato",
        "estado_anterior": "planejado",
        "estado_novo": "confirmado",
        "justificativa": "Evidencias atualizadas",
        "relatorio_simples": "Resumo",
    }

engine = TruthDBEngine()
valid_sequence = [
    ("criar_bloco_tema", bloco_payload()),
    ("criar_fato_registravel", fato_payload()),
    ("criar_versao_fato", versao_payload()),
    ("atualizar_estado_fato", update_payload()),
]
valid_hits = sum(1 for name, payload in valid_sequence if engine.apply(name, payload).accepted)

def invalid_missing_block():
    eng = TruthDBEngine()
    payload = fato_payload()
    payload["id_bloco"] = "bloco_inexistente"
    return eng.apply("criar_fato_registravel", payload).accepted

def invalid_transition():
    eng = TruthDBEngine()
    eng.apply("criar_bloco_tema", bloco_payload())
    eng.apply("criar_fato_registravel", fato_payload())
    bad_payload = update_payload()
    bad_payload["estado_novo"] = "planejado"
    return eng.apply("atualizar_estado_fato", bad_payload).accepted

invalid_cases = [invalid_missing_block, invalid_transition]
invalid_hits = sum(1 for fn in invalid_cases if not fn())

metrics = {
    "ratio_valid_actions_accepted": valid_hits / len(valid_sequence),
    "ratio_invalid_actions_rejected": invalid_hits / len(invalid_cases),
}
path = sys.argv[1]
with open(path, "w", encoding="utf-8") as fp:
    json.dump(metrics, fp, indent=2)
PY

read_values=$(python3 - <<'PY' "$EVIDENCE_DIR/engine_sli.json"
import json, sys
from pathlib import Path
data = json.loads(Path(sys.argv[1]).read_text())
print(data["ratio_valid_actions_accepted"])
print(data["ratio_invalid_actions_rejected"])
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
  "gate_id": "S10_G4",
  "name": "Mechanical Truth-DB engine",
  "status": "$status",
  "slis": {
    "ratio_valid_actions_accepted": $valid_ratio,
    "ratio_invalid_actions_rejected": $invalid_ratio
  },
  "checks": [
    {
      "id": "engine-tests",
      "description": "Rodar tests/truthdb/test_engine.py via shim",
      "status": "$test_status",
      "details": "Logs em tests.log"
    },
    {
      "id": "engine-valid-ratio",
      "description": "Medir ratio_valid_actions_accepted",
      "status": "$valid_ratio_status",
      "details": "valor=$valid_ratio"
    },
    {
      "id": "engine-invalid-ratio",
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
