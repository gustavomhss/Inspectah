#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

mkdir -p out/scorecards out/evidence/S32_G4_orr_and_bundle out/bundles

EVIDENCE_LOG="out/evidence/S32_G4_orr_and_bundle/run.log"
BUNDLE_PATH="out/bundles/inspectah_s32_evidence_bundle.zip"

echo "[S32_G4] Verificando scorecards G0-G3" | tee "$EVIDENCE_LOG"

missing=()
for sc in out/scorecards/S32_G0_scope_and_baseline.json out/scorecards/S32_G1_models_and_invariants.json out/scorecards/S32_G2_promotion_flows.json out/scorecards/S32_G3_contestation_flows.json; do
  if [[ ! -f "$sc" ]]; then
    missing+=("$sc")
  fi
done

status="PASS"
if ((${#missing[@]} > 0)); then
  status="FAIL"
fi

echo "[S32_G4] Montando bundle" | tee -a "$EVIDENCE_LOG"
set +e
zip -r "$BUNDLE_PATH" out/scorecards out/evidence  >>"$EVIDENCE_LOG" 2>&1
zip_rc=$?
set -e

bundle_integrity_ok="false"
if [ $zip_rc -eq 0 ]; then
  if unzip -t "$BUNDLE_PATH" >>"$EVIDENCE_LOG" 2>&1; then
    bundle_integrity_ok="true"
  else
    status="FAIL"
  fi
else
  status="FAIL"
fi

export MISSING_LIST=$(IFS=,; echo "${missing[*]:-}")
export BUNDLE_OK=$bundle_integrity_ok
export STATUS=$status
export BUNDLE_PATH_VAL=$BUNDLE_PATH

python3 - <<PY
import datetime
import json
import pathlib
import os

missing_env = os.environ.get("MISSING_LIST", "")
missing_list = [m for m in missing_env.split(",") if m]
bundle_ok = os.environ.get("BUNDLE_OK", "false") == "true"

scorecard = {
    "gate": "S32_G4_orr_and_bundle",
    "status": os.environ.get("STATUS", "FAIL"),
    "missing_scorecards": missing_list,
    "bundle_path": os.environ.get("BUNDLE_PATH_VAL", "out/bundles/inspectah_s32_evidence_bundle.zip"),
    "bundle_integrity_ok": bundle_ok,
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
}
path = pathlib.Path("out/scorecards/S32_G4_orr_and_bundle.json")
path.write_text(json.dumps(scorecard, indent=2))
print(json.dumps(scorecard, indent=2))
PY
