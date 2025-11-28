#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G3_collect_evidence.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G3_collect_evidence"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

OUTPUT_JSON="$EVIDENCE_DIR/collect_summary.json"
if ! "$REPO_ROOT/bin/inspectah_collect_once.sh" "$DOMAIN" | tee "$OUTPUT_JSON"; then
  status="FAIL"
else
  status=$("$PYTHON_BIN" - <<'PY' "$OUTPUT_JSON"
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    data = json.load(handle)
errors = [name for name, entry in data.get('sources', {}).items() if entry.get('errors')]
if data.get('canonical_records_total', 0) <= 0 or errors:
    print('FAIL')
else:
    print('PASS')
PY)
fi

"$PYTHON_BIN" - <<'PY' "$SCORECARD" "$status" "$OUTPUT_JSON"
import json, sys
scorecard_path, status, output_json = sys.argv[1:4]
try:
    data = json.load(open(output_json, encoding='utf-8'))
except FileNotFoundError:
    data = {"sources": {}}
errors = [name for name, entry in data.get('sources', {}).items() if entry.get('errors')]
json.dump({
    "gate": "S6_G3",
    "name": "collect_evidence",
    "status": status,
    "details": {
        "canonical_records_total": data.get('canonical_records_total'),
        "new_evidence_packages": data.get('new_evidence_packages'),
        "sources_with_errors": errors,
    },
}, open(scorecard_path, "w", encoding="utf-8"), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
