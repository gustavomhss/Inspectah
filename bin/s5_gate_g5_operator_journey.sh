#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G5_operator_journey"
SCORECARD="$OUT_DIR/scorecard.json"
REPORT_MD="$OUT_DIR/report.md"
LOG_FILE="$OUT_DIR/sanity.log"
mkdir -p "$OUT_DIR"

status="PASS"
notes=()
metrics_ui=1
metrics_sanity=0

require_file() {
  local label="$1"
  local path="$2"
  if [[ ! -f "$path" ]]; then
    notes+=("Falta ${label}: ${path}")
    status="FAIL"
    metrics_ui=0
  fi
}

UI_FILES=(
  "$ROOT_DIR/inspectah/indexer/query_api.py"
  "$ROOT_DIR/inspectah/ui/admin_sources.py"
  "$ROOT_DIR/inspectah/ui/explore.py"
  "$ROOT_DIR/inspectah/ui/templates/admin_sources_header.txt"
  "$ROOT_DIR/inspectah/ui/templates/admin_source_detail.txt"
  "$ROOT_DIR/inspectah/ui/templates/explore_header.txt"
  "$ROOT_DIR/inspectah/ui/templates/explore_item_detail.txt"
  "$ROOT_DIR/docs/sprint_5/gates/G5_operator_journey_checklist.md"
  "$ROOT_DIR/docs/sprint_5/gates/G5_operator_scenario.md"
)

for file in "${UI_FILES[@]}"; do
  require_file "artefato G5" "$file"
done

run_sanity() {
  local tmp_dir
  tmp_dir=$(mktemp -d)
  local evidence_dir="$tmp_dir/evidence"
  local index_dir="$tmp_dir/index"
  mkdir -p "$evidence_dir" "$index_dir"
  if python3 - "$evidence_dir" "$index_dir" <<'PY' | tee "$LOG_FILE"
import json
import sys
from inspectah.pipeline.pipeline_fixtures import run_pipeline_with_fixtures

evidence_dir = sys.argv[1]
index_dir = sys.argv[2]
result = run_pipeline_with_fixtures(evidence_base=evidence_dir, index_base=index_dir)
summary = result["summary"]
print(json.dumps(summary))
if summary.get("items_total", 0) <= 0:
    raise SystemExit(1)
PY
  then
    metrics_sanity=1
  else
    notes+=("Sanity da pipeline com fixtures falhou — ver $LOG_FILE")
    status="FAIL"
  fi
  rm -rf "$tmp_dir"
}

run_sanity

cat <<EOFREP > "$REPORT_MD"
# G5 Operator Journey Report

- Preparado em: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
- Checklist: docs/sprint_5/gates/G5_operator_journey_checklist.md
- Cenário: docs/sprint_5/gates/G5_operator_scenario.md

## Instruções para o operador
1. Siga o checklist em ordem (UI Admin → pipeline → UI Explore).
2. Registre abaixo o tempo total da jornada e eventuais problemas.
3. Inclua prints ou descrições textuais, se necessário.

## Feedback do operador
- Tempo total: 
- Observações: 
EOFREP

notes_text="PASS"
if [[ ${#notes[@]} -gt 0 ]]; then
  notes_text=$(printf '%s; ' "${notes[@]}")
  notes_text=${notes_text::-2}
fi

cat <<JSON > "$SCORECARD"
{
  "gate_id": "G5",
  "status": "${status}",
  "checked_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "notes": "${notes_text}",
  "metrics": {
    "ui_files_present": ${metrics_ui},
    "sanity_pipeline_run": ${metrics_sanity}
  }
}
JSON

if [[ "$status" != "PASS" ]]; then
  echo "G5 Operator Journey -> FAIL"
  echo "Notas: ${notes_text}"
  exit 1
fi

echo "G5 Operator Journey -> PASS"
