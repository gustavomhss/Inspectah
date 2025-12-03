#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S29_G0_scope_and_baseline"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S29_G0_scope_and_baseline.json"

if [[ -d "$ROOT_DIR/.venv" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

EXPECTED_DOCS=(
  "$ROOT_DIR/docs/sprint_29_macro.md"
  "$ROOT_DIR/docs/sprint_29_capitulo_1.md"
  "$ROOT_DIR/docs/sprint_29_capitulo_2.md"
  "$ROOT_DIR/docs/sprint_29_capitulo_3.md"
  "$ROOT_DIR/docs/sprint_29_capitulo_4.md"
  "$ROOT_DIR/docs/sprint_29_orr_summary.md"
)

EXPECTED_PATHS=(
  "$ROOT_DIR/app/agents/flows/models.py"
  "$ROOT_DIR/app/agents/flows/schemas.py"
  "$ROOT_DIR/app/agents/flows/validator.py"
  "$ROOT_DIR/app/agents/flows/service.py"
  "$ROOT_DIR/app/agents/flows/runtime_adapter.py"
  "$ROOT_DIR/app/api/admin_agent_flows_routes.py"
  "$ROOT_DIR/frontend/inspectah-ui/src/features/agent-flows"
  "$ROOT_DIR/out/evidence/S29_G0_scope_and_baseline"
  "$ROOT_DIR/out/evidence/S29_G1_model_and_migrations"
  "$ROOT_DIR/out/evidence/S29_G2_api_and_validator"
  "$ROOT_DIR/out/evidence/S29_G3_ui_and_frontend_quality"
  "$ROOT_DIR/out/evidence/S29_G4_runtime_and_observability"
  "$ROOT_DIR/out/evidence/S29_G5_orr_and_bundle"
  "$ROOT_DIR/out/bundles"
)

missing_docs=()
for doc in "${EXPECTED_DOCS[@]}"; do
  if [[ ! -f "$doc" ]]; then
    missing_docs+=("$doc")
  fi
done

missing_paths=()
for path in "${EXPECTED_PATHS[@]}"; do
  if [[ ! -e "$path" ]]; then
    missing_paths+=("$path")
  fi
done

{
  echo "[S29_G0] Docs check"
  for doc in "${EXPECTED_DOCS[@]}"; do
    if [[ -f "$doc" ]]; then
      echo "OK  $doc"
    else
      echo "MISS $doc"
    fi
  done
} > "$EVIDENCE_DIR/docs_check.txt"

{
  echo "[S29_G0] Filemap check"
  for path in "${EXPECTED_PATHS[@]}"; do
    if [[ -e "$path" ]]; then
      echo "OK  $path"
    else
      echo "MISS $path"
    fi
  done
} > "$EVIDENCE_DIR/filemap_check.txt"

STATUS="PASS"
if [[ ${#missing_docs[@]} -gt 0 || ${#missing_paths[@]} -gt 0 ]]; then
  STATUS="FAIL"
fi

python - <<'PY' "$SCORECARD_PATH" "$STATUS" "${missing_docs[@]}" -- "${missing_paths[@]}"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
args = sys.argv[3:]
missing_docs = []
missing_paths = []
collecting_paths = False
for item in args:
    if item == "--":
        collecting_paths = True
        continue
    if collecting_paths:
        missing_paths.append(item)
    else:
        missing_docs.append(item)

timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
scorecard = {
    "gate_id": "S29_G0",
    "status": status,
    "missing_docs": missing_docs,
    "missing_paths": missing_paths,
    "timestamp": timestamp,
    "notes": "" if status == "PASS" else "Verifique evidências em docs_check.txt e filemap_check.txt",
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

if status != "PASS":
    sys.exit(1)
PY

echo "[S29_G0] Scorecard gerado em $SCORECARD_PATH com status $STATUS"
