#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/out/s5_gates/G3_pipeline_fixtures"
PIPELINE_SUMMARY="$OUT_DIR/pipeline_summary.json"
PIPELINE_ITEMS="$OUT_DIR/pipeline_items.json"
GOLDEN_DIFF="$OUT_DIR/golden_diff.json"
LOG_DIR="$OUT_DIR"
mkdir -p "$OUT_DIR"

status="PASS"
notes=()

golden_path="$ROOT_DIR/tests/golden/s5_pipeline/expected_items_summary.json"

require_file() {
  local label="$1"
  local path="$2"
  if [[ ! -f "$path" ]]; then
    notes+=("Falta ${label}: ${path}")
    status="FAIL"
  fi
}

require_file "Sources registry" "$ROOT_DIR/inspectah/config/sources_registry.yaml"
require_file "Pipeline module" "$ROOT_DIR/inspectah/pipeline/pipeline_fixtures.py"
require_file "Golden summary" "$golden_path"
require_file "Fixtures RSS" "$ROOT_DIR/fixtures/s5/rss_feed.xml"
require_file "Fixtures API" "$ROOT_DIR/fixtures/s5/api_feed.json"
require_file "Fixtures HTML" "$ROOT_DIR/fixtures/s5/html_page.html"
require_file "Evidence builder" "$ROOT_DIR/inspectah/evidence/builder.py"
require_file "Normalizer" "$ROOT_DIR/inspectah/normalizer/normalizer.py"
require_file "Indexer" "$ROOT_DIR/inspectah/indexer/indexer.py"
require_file "Pipeline tests" "$ROOT_DIR/tests/pipeline/test_pipeline_fixtures.py"

run_pipeline() {
  local tmp_dir
  tmp_dir=$(mktemp -d)
  local evidence_dir="$tmp_dir/evidence"
  local index_dir="$tmp_dir/index"
  mkdir -p "$evidence_dir" "$index_dir"
  if ! python3 - <<PY2
import json
from pathlib import Path
from inspectah.pipeline.pipeline_fixtures import run_pipeline_with_fixtures

result = run_pipeline_with_fixtures(
    evidence_base="$evidence_dir",
    index_base="$index_dir",
    summary_path="$PIPELINE_SUMMARY",
)
Path("$PIPELINE_ITEMS").write_text(json.dumps(result["items"], indent=2))
PY2
  then
    notes+=("Falha ao executar pipeline com fixtures")
    status="FAIL"
  fi
  rm -rf "$tmp_dir"
}

compare_golden() {
  if [[ ! -f "$PIPELINE_SUMMARY" ]]; then
    notes+=("Resumo da pipeline ausente")
    status="FAIL"
    return
  fi
  if ! python3 - <<PY3
import json
from pathlib import Path
summary = json.loads(Path("$PIPELINE_SUMMARY").read_text())
golden = json.loads(Path("$golden_path").read_text())
diff = {
    "items_total_delta": summary["items_total"] - golden["items_total"],
    "bundles_total_delta": summary["bundles_total"] - golden.get("bundles_total", 0),
    "items_by_state_match": summary["items_by_state"] == golden["items_by_state"],
    "items_by_source_match": summary["items_by_source"] == golden["items_by_source"],
    "summary": summary,
    "golden": golden,
}
Path("$GOLDEN_DIFF").write_text(json.dumps(diff, indent=2))
if diff["items_total_delta"] != 0 or diff["bundles_total_delta"] != 0 or not diff["items_by_state_match"] or not diff["items_by_source_match"]:
    raise SystemExit(1)
PY3
  then
    notes+=("Diferenças encontradas no golden data")
    status="FAIL"
  fi
}

run_tests_and_invariants() {
  if ! "$ROOT_DIR/bin/s5_check_invariants.sh"; then
    notes+=("s5_check_invariants falhou")
    status="FAIL"
  fi
}

extract_tests_run() {
  python3 - "$LOG_DIR/pipeline_tests.log" <<'PY4'
import re
import sys
from pathlib import Path
text = Path(sys.argv[1]).read_text() if Path(sys.argv[1]).exists() else ""
match = re.search(r"collected (\d+) items", text)
if not match:
    match = re.search(r"Ran (\d+) tests?", text)
print(match.group(1) if match else "0")
PY4
}

run_pipeline
compare_golden
run_tests_and_invariants

tests_run=$(extract_tests_run)
summary_json="{}"
if [[ -f "$PIPELINE_SUMMARY" ]]; then
  summary_json=$(cat "$PIPELINE_SUMMARY")
fi

metrics_json=$(python3 - <<PY5
import json
from pathlib import Path
summary = {}
try:
    summary = json.loads(Path("$PIPELINE_SUMMARY").read_text())
except Exception:
    summary = {}
metrics = {
    "tests_run": int("$tests_run" or 0),
    "items_total": summary.get("items_total", 0),
    "bundles_total": summary.get("bundles_total", 0),
    "items_by_state": summary.get("items_by_state", {}),
}
print(json.dumps(metrics))
PY5
)

notes_text="PASS"
if [[ ${#notes[@]} -gt 0 ]]; then
  notes_text=$(printf '%s; ' "${notes[@]}")
  notes_text=${notes_text::-2}
fi

cat <<JSON > "$OUT_DIR/scorecard.json"
{
  "gate_id": "G3",
  "status": "${status}",
  "checked_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "notes": "${notes_text}",
  "metrics": ${metrics_json}
}
JSON

if [[ "$status" != "PASS" ]]; then
  echo "G3 Pipeline Fixtures -> FAIL"
  echo "Notas: ${notes_text}"
  exit 1
fi

echo "G3 Pipeline Fixtures -> PASS"
