#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
DOMAIN="${1:-dominio_piloto}"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

SCORECARD="$REPO_ROOT/out/scorecards/S6_G1_sources_registry.json"
EVIDENCE_DIR="$REPO_ROOT/out/evidence/S6_G1_sources_registry"
mkdir -p "$(dirname "$SCORECARD")" "$EVIDENCE_DIR"

OUTPUT_JSON="$EVIDENCE_DIR/sources_validation.json"
if ! "$REPO_ROOT/bin/inspectah_sources_validate.sh" "$DOMAIN" | tee "$OUTPUT_JSON"; then
  status="FAIL"
else
  status=$("$PYTHON_BIN" - "$OUTPUT_JSON" <<'PY'
import json, sys
with open(sys.argv[1], encoding='utf-8') as handle:
    data = json.load(handle)
print(data.get('status', 'FAIL'))
PY
)
fi

"$PYTHON_BIN" - "$SCORECARD" "$status" "$OUTPUT_JSON" <<'PY'
import json, sys
scorecard_path, status, output_json = sys.argv[1:4]
try:
    data = json.load(open(output_json, encoding='utf-8'))
except FileNotFoundError:
    data = {"sources": {}}
missing = [name for name, entry in data.get('sources', {}).items() if not entry.get('exists')]
json.dump({
    "gate": "S6_G1",
    "name": "sources_registry",
    "status": status,
    "details": {
        "sources_total": len(data.get('sources', {})),
        "missing_sources": missing,
    },
}, open(scorecard_path, "w", encoding="utf-8"), indent=2)
PY

if [[ "$status" != "PASS" ]]; then
  exit 1
fi
