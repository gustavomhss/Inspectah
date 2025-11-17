#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$ROOT_DIR/docs"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S8_T0_scope"
SCORECARDS_DIR="$ROOT_DIR/out/scorecards"
SUMMARY_FILE="$EVIDENCE_DIR/summary.json"
MANIFEST_FILE="$EVIDENCE_DIR/MANIFEST.json"
SCORECARD_FILE="$SCORECARDS_DIR/S8_T0_scope.json"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

mkdir -p "$EVIDENCE_DIR" "$SCORECARDS_DIR"

declare -a REQUIRED_DOCS=(
  "docs/sprint_8_capitulo_1.md"
  "docs/sprint_8_capitulo_2_gates.md"
  "docs/sprint_8_capitulo_3_arquitetura.md"
  "docs/sprint_8_capitulo_4_execucao.md"
  "docs/sprint_8_cenarios_demo.md"
)

declare -a REQUIRED_DIRS=(
  "app"
  "app/admin"
  "app/user"
  "app/core"
  "app/gpt_client"
  "tests"
  "tests/s8_t2_unit_contracts"
  "tests/s8_t3_property"
  "tests/s8_t4_golden_flows"
  "tests/fixtures"
  "tests/fixtures/s8_preco_medio"
  "tests/fixtures/s8_comparacao"
  "tests/fixtures/s8_checagem_factual"
  "tests/goldens"
  "bin"
  "out"
  "out/evidence"
  "out/scorecards"
)

STATUS="PASS"
declare -a ISSUES=()

for file in "${REQUIRED_DOCS[@]}"; do
  if [[ ! -s "$ROOT_DIR/$file" ]]; then
    STATUS="FAIL"
    ISSUES+=("Arquivo ausente ou vazio: $file")
  fi
done

for dir in "${REQUIRED_DIRS[@]}"; do
  if [[ ! -d "$ROOT_DIR/$dir" ]]; then
    STATUS="FAIL"
    ISSUES+=("Diretorio ausente: $dir")
  fi
done

export S8_T0_STATUS="$STATUS"
export S8_T0_TIMESTAMP="$TIMESTAMP"
export S8_T0_DOCS="$(printf '%s\n' "${REQUIRED_DOCS[@]}")"
export S8_T0_DIRS="$(printf '%s\n' "${REQUIRED_DIRS[@]}")"
export S8_T0_ISSUES="$(printf '%s\n' "${ISSUES[@]-}")"
export S8_T0_SUMMARY="$SUMMARY_FILE"
export S8_T0_SCORECARD="$SCORECARD_FILE"
export S8_T0_MANIFEST="$MANIFEST_FILE"
export ROOT_DIR

python3 - "$SUMMARY_FILE" "$MANIFEST_FILE" "$SCORECARD_FILE" <<'PY'
import json
import os
import sys

summary_path, manifest_path, scorecard_path = sys.argv[1:4]

def split_env(name):
    value = os.environ.get(name, "").strip()
    return [line for line in value.splitlines() if line]

data_common = {
    "gate": "S8_T0_scope",
    "status": os.environ["S8_T0_STATUS"],
    "timestamp": os.environ["S8_T0_TIMESTAMP"],
}

summary = dict(data_common)
summary.update(
    description="Verificacao de docs e esqueleto da Sprint 8",
    docs=split_env("S8_T0_DOCS"),
    dirs=split_env("S8_T0_DIRS"),
    issues=split_env("S8_T0_ISSUES"),
)

with open(summary_path, "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=2, ensure_ascii=False)

manifest = {
    "gate": "S8_T0_scope",
    "artifacts": split_env("S8_T0_DOCS"),
}
with open(manifest_path, "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, indent=2, ensure_ascii=False)

scorecard = dict(data_common)
scorecard.update(
    gate_id="S8_T0_scope",
    checks_total=len(split_env("S8_T0_DOCS")) + len(split_env("S8_T0_DIRS")),
    checks_failed=len(split_env("S8_T0_ISSUES")),
    summary_file=os.path.relpath(summary_path, os.environ.get("ROOT_DIR", summary_path)),
)
with open(scorecard_path, "w", encoding="utf-8") as fh:
    json.dump(scorecard, fh, indent=2, ensure_ascii=False)
PY

if [[ "$STATUS" != "PASS" ]]; then
  echo "S8_T0_scope falhou. Consulte $SUMMARY_FILE para detalhes." >&2
  exit 1
fi

echo "S8_T0_scope PASS. Evidencias em $EVIDENCE_DIR"
