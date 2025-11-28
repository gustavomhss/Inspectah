#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G4_explore_verify.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G4_explore_verify"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

QUERY_STDOUT="$EVIDENCE_DIR/query_stdout.json"
QUERY_META="$EVIDENCE_DIR/query_meta.json"
QUERY_RESULTS="$EVIDENCE_DIR/query_results.json"

status="PASS"
if ! "$REPO_ROOT/bin/inspectah_query.sh" "$DOMAIN" --format json --page 1 --page-size 5 --meta-output "$QUERY_META" --export-prefix "$EVIDENCE_DIR/query_export" > "$QUERY_STDOUT"; then
  status="FAIL"
fi

FIRST_ITEM=$("$PYTHON_BIN" - <<'PY' "$QUERY_STDOUT" "$QUERY_RESULTS"
import json, sys
from pathlib import Path
stdout_path, results_path = sys.argv[1:3]
content = Path(stdout_path).read_text(encoding='utf-8')
decoder = json.JSONDecoder()
try:
    items, idx = decoder.raw_decode(content)
except json.JSONDecodeError:
    items = []
Path(results_path).write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding='utf-8')
print(items[0]['item_id'] if items else '', end='')
PY)
if [[ -z "$FIRST_ITEM" ]]; then
  status="FAIL"
fi

EVIDENCE_OUTPUT="$EVIDENCE_DIR/evidence_lookup.json"
if [[ "$status" == "PASS" ]]; then
  if ! "$REPO_ROOT/bin/inspectah_show_evidence.sh" "$FIRST_ITEM" "$DOMAIN" > "$EVIDENCE_OUTPUT"; then
    status="FAIL"
  fi
fi

"$PYTHON_BIN" - <<'PY' "$SCORECARD" "$status" "$QUERY_RESULTS"
import json, sys
scorecard_path, status, results_path = sys.argv[1:4]
try:
    items = json.load(open(results_path, encoding='utf-8'))
except FileNotFoundError:
    items = []
json.dump({
    "gate": "S6_G4",
    "name": "explore_verify",
    "status": status,
    "details": {
        "items_returned": len(items),
        "sample_item_ids": [item.get('item_id') for item in items[:3]],
    },
}, open(scorecard_path, "w", encoding="utf-8"), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
