#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

RUNBOOKS=(
  "docs/s33/runbooks/s33_runbook_fonte_noticias_atraso.md"
  "docs/s33/runbooks/s33_runbook_latencia_pipeline_noticias.md"
)
EVIDENCE_DIR="out/evidence/S33_G4_incidents"
BUNDLE_PATH="out/bundles/inspectah_s33_incidents_bundle.zip"
LOG="out/evidence/S33_G4_incidents/run.log"
mkdir -p out/scorecards "$EVIDENCE_DIR" out/bundles

status="PASS"
errors=()

echo "[S33_G4] Checando runbooks e evidências" | tee "$LOG"
for f in "${RUNBOOKS[@]}"; do
  if [[ ! -f "$f" ]]; then
    status="FAIL"
    errors+=("$f ausente")
  fi
done

if [[ ! -d "$EVIDENCE_DIR" ]]; then
  status="FAIL"
  errors+=("evidence dir ausente")
fi

set +e
zip -r "$BUNDLE_PATH" docs/s33/runbooks "$EVIDENCE_DIR" >>"$LOG" 2>&1
zip_rc=$?
if [ $zip_rc -ne 0 ]; then
  status="FAIL"
  errors+=("zip falhou")
fi
set -e

export S33_G4_ERRORS=$(IFS=';;'; echo "${errors[*]:-}")
export RUNBOOKS_COUNT=${#RUNBOOKS[@]}
export STATUS=$status
export BUNDLE_PATH=$BUNDLE_PATH

python3 - <<PY
import datetime
import json
import pathlib
import os

errors_env = os.environ.get("S33_G4_ERRORS", "")
errors = [e for e in errors_env.split(";;") if e]

runbooks_count = int(os.environ.get("RUNBOOKS_COUNT", "0"))
scorecard = {
    "gate": "S33_G4_runbooks",
    "status": os.environ.get("STATUS", "$status"),
    "runbooks": runbooks_count,
    "bundle_path": os.environ.get("BUNDLE_PATH", "$BUNDLE_PATH"),
    "errors": errors,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S33_G4_runbooks.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
