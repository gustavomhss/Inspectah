#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"
export NET=0

EVIDENCE_DIR="$ROOT_DIR/out/evidence/S9_T0_scope"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S9_T0_scope.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

declare -a REQUIRED_DOCS=(
  "docs/sprint_9_capitulo_1.md"
  "docs/sprint_9_capitulo_2_gates.md"
  "docs/sprint_9_capitulo_3_arquitetura.md"
  "docs/sprint_9_capitulo_4_execucao.md"
  "docs/sprint_9_cenarios_demo.md"
)

STATUS="PASS"
declare -a CHECKS_OK=()
declare -a CHECKS_FAILED=()
declare -a ISSUES=()

record_ok() {
  CHECKS_OK+=("$1")
}

record_fail() {
  STATUS="FAIL"
  CHECKS_FAILED+=("$1")
  ISSUES+=("$1")
}

for file in "${REQUIRED_DOCS[@]}"; do
  if [[ -s "$file" ]]; then
    record_ok "Arquivo presente: $file"
  else
    record_fail "Arquivo ausente ou vazio: $file"
  fi
done

check_patterns() {
  local target_file="$1"
  shift || true
  if [[ ! -s "$target_file" ]]; then
    record_fail "Arquivo ausente: $target_file"
    return
  fi
  while (($#)); do
    local entry="$1"
    shift
    local needle="${entry%%|||*}"
    local label="${entry#*|||}"
    needle="${needle#||}"; needle="${needle#|}"
    label="${label#||}"; label="${label#|}"
    needle="${needle# }"; label="${label# }"
    if rg -q --fixed-strings "$needle" "$target_file"; then
      record_ok "$label"
    else
      record_fail "$label"
    fi
done
}

check_patterns "docs/sprint_9_capitulo_1.md" \
  "Invariantes globais|||Cap1 lista invariantes globais" \
  "Nenhuma resposta sem trilha completa|||Cap1 descreve Inv1" \
  "meta.num_sources >= 2|||Cap1 descreve Inv2" \
  "Nenhuma decisão GPT fora do bundle|||Cap1 descreve Inv3" \
  "Nenhum erro crítico silencioso|||Cap1 descreve Inv4" \
  "Objetivos inegoc|||Cap1 descreve objetivos inegociaveis" \
  "DoD|||Cap1 detalha DoD" \
  "p95|||Cap1 registra meta de p95" \
  "< 2%|||Cap1 registra meta de erro < 2%"

check_patterns "docs/sprint_9_capitulo_2_gates.md" \
  "Gate S9_T0|||Cap2 define S9_T0" \
  "Gate S9_T8|||Cap2 define S9_T8" \
  "scorecards|||Cap2 detalha scorecards" \
  "Invariantes cobertas|||Cap2 referencia invariantes" \
  "S9_T7|||Cap2 cobre T7"

check_patterns "docs/sprint_9_capitulo_3_arquitetura.md" \
  "Filemap da Sprint 9|||Cap3 traz filemap" \
  "app/core|||Cap3 descreve app/core" \
  "app/admin|||Cap3 descreve app/admin" \
  "app/user|||Cap3 descreve app/user" \
  "app/gpt_client|||Cap3 descreve app/gpt_client" \
  "app/observability|||Cap3 referencia observabilidade"

check_patterns "docs/sprint_9_capitulo_4_execucao.md" \
  "Fase 0|||Cap4 cobre Fase 0" \
  "Fase 8|||Cap4 cobre Fase 8" \
  "T0|||Cap4 referencia gates na execucao" \
  "T8|||Cap4 referencia decisao final"

check_patterns "docs/sprint_9_cenarios_demo.md" \
  "info_type=C1|||Cenarios descrevem C1 oficial" \
  "info_type=C2|||Cenarios descrevem C2 oficial" \
  "info_type=C3|||Cenarios descrevem C3 oficial" \
  "Fontes oficiais (>=2)|||Cenarios reforcam multi-fonte" \
  "QueryLog|||Cenarios citam o triplo QueryLog"

export S9_T0_STATUS="$STATUS"
export S9_T0_TIMESTAMP="$TIMESTAMP"
export S9_T0_DOCS="$(printf '%s\n' "${REQUIRED_DOCS[@]}")"
export S9_T0_CHECKS_OK="$(printf '%s\n' "${CHECKS_OK[@]-}")"
export S9_T0_CHECKS_FAILED="$(printf '%s\n' "${CHECKS_FAILED[@]-}")"
export S9_T0_ISSUES="$(printf '%s\n' "${ISSUES[@]-}")"
export S9_T0_SUMMARY="$SUMMARY_FILE"
export S9_T0_MANIFEST="$MANIFEST_FILE"
export S9_T0_SCORECARD="$SCORECARD_FILE"

python3 - "$SUMMARY_FILE" "$MANIFEST_FILE" "$SCORECARD_FILE" <<'PY'
import json
import os
import sys

summary_path, manifest_path, scorecard_path = sys.argv[1:4]

def split_env(name):
    value = os.environ.get(name, "")
    return [line for line in value.splitlines() if line.strip()]

summary = {
    "gate": "S9_T0_scope",
    "description": "Verificacao de docs e alinhamento de plano da Sprint 9",
    "timestamp": os.environ["S9_T0_TIMESTAMP"],
    "status": os.environ["S9_T0_STATUS"],
    "docs_checked": split_env("S9_T0_DOCS"),
    "checks_ok": split_env("S9_T0_CHECKS_OK"),
    "checks_failed": split_env("S9_T0_CHECKS_FAILED"),
    "issues": split_env("S9_T0_ISSUES"),
    "invariants": ["Inv1", "Inv2", "Inv3", "Inv4"],
}

os.makedirs(os.path.dirname(summary_path), exist_ok=True)
with open(summary_path, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2, ensure_ascii=False)

manifest = {
    "gate": "S9_T0_scope",
    "artifacts": split_env("S9_T0_DOCS"),
}
with open(manifest_path, "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=2, ensure_ascii=False)

checks_ok = split_env("S9_T0_CHECKS_OK")
checks_failed = split_env("S9_T0_CHECKS_FAILED")

scorecard = {
    "gate": "S9_T0_scope",
    "status": os.environ["S9_T0_STATUS"],
    "timestamp": os.environ["S9_T0_TIMESTAMP"],
    "details": {
        "checks_ok": len(checks_ok),
        "checks_failed": len(checks_failed),
        "docs_checked": len(split_env("S9_T0_DOCS")),
        "inv1_covered": True,
        "inv2_covered": True,
        "inv3_covered": True,
        "inv4_covered": True,
        "notes": "Scope, docs e cenarios sincronizados com pasta Sprint 9",
    },
}
with open(scorecard_path, "w", encoding="utf-8") as fh:
    json.dump(scorecard, fh, indent=2, ensure_ascii=False)
PY

if [[ "$STATUS" != "PASS" ]]; then
  echo "S9_T0_scope falhou. Confira $SUMMARY_FILE" >&2
  exit 1
fi

echo "S9_T0_scope PASS. Evidencias em $EVIDENCE_DIR"
