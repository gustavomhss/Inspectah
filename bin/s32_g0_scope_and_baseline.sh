#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

mkdir -p out/scorecards out/evidence/S32_G0_scope_and_baseline out/bundles

expected_docs=(
  "docs/sprint_32_capitulo_1_contexto.md"
  "docs/sprint_32_capitulo_2_gates_e_metricas.md"
  "docs/sprint_32_capitulo_3_arquitetura_e_filemap.md"
  "docs/sprint_32_capitulo_4_execucao_e_evidencias.md"
  "docs/sprint_32_capitulo_5_orr_operacao_pos_sprint.md"
  "docs/sprint_32_capitulo_6_learnings_e_anti_gaps.md"
  "docs/sprint_32_capitulo_7_tasks.md"
)

expected_scripts=(
  "bin/s32_g0_scope_and_baseline.sh"
  "bin/s32_g1_models_and_invariants.sh"
  "bin/s32_g2_promotion_flows.sh"
  "bin/s32_g3_contestation_flows.sh"
  "bin/s32_g4_orr_and_bundle.sh"
)

missing_docs=()
for f in "${expected_docs[@]}"; do
  [[ -f "$f" ]] || missing_docs+=("$f")
done

missing_scripts=()
for f in "${expected_scripts[@]}"; do
  [[ -f "$f" ]] || missing_scripts+=("$f")
done

missing=(${missing_docs[@]:-} ${missing_scripts[@]:-})
docs_ok=true
scripts_ok=true
if ((${#missing_docs[@]} > 0)); then docs_ok=false; fi
if ((${#missing_scripts[@]} > 0)); then scripts_ok=false; fi
status="PASS"
[[ "$docs_ok" == "true" && "$scripts_ok" == "true" ]] || status="FAIL"

export STATUS="$status"
export DOCS_OK="$docs_ok"
export SCRIPTS_OK="$scripts_ok"
export MISSING=$(printf '%s\n' "${missing[@]:-}")
scorecard_path="out/scorecards/S32_G0_scope_and_baseline.json"

python3 - <<'PY'
import datetime
import json
import os
import pathlib

missing_raw = os.environ.get("MISSING", "")
missing = [m for m in missing_raw.split("\n") if m]
scorecard = {
    "gate": "S32_G0_scope_and_baseline",
    "status": os.environ["STATUS"],
    "docs_present": os.environ["DOCS_OK"].lower() == "true",
    "scripts_present": os.environ["SCRIPTS_OK"].lower() == "true",
    "missing": missing,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S32_G0_scope_and_baseline.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY

exit 0
