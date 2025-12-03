#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S29_G5_orr_and_bundle"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S29_G5_orr_and_bundle.json"
BUNDLE_PATH="$ROOT_DIR/out/bundles/inspectah_s29_evidence_bundle.zip"

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR" "$ROOT_DIR/out/bundles"

SCORECARDS=(
  "$ROOT_DIR/out/scorecards/S29_G0_scope_and_baseline.json"
  "$ROOT_DIR/out/scorecards/S29_G1_model_and_migrations.json"
  "$ROOT_DIR/out/scorecards/S29_G2_api_and_validator.json"
  "$ROOT_DIR/out/scorecards/S29_G3_ui_and_frontend_quality.json"
  "$ROOT_DIR/out/scorecards/S29_G4_runtime_and_observability.json"
)

STATUS="PASS"
CHECK_LOG="$EVIDENCE_DIR/scorecards_check.log"

python3 - "$CHECK_LOG" "${SCORECARDS[@]}" > "$EVIDENCE_DIR/scorecards_status.txt" <<'PY'
import json
import sys
from pathlib import Path

log_path = Path(sys.argv[1])
scorecards = [Path(p) for p in sys.argv[2:]]
lines = []
status = "PASS"
for p in scorecards:
    if not p.exists():
        lines.append(f"MISSING {p}")
        status = "FAIL"
        continue
    data = json.loads(p.read_text())
    st = data.get("status")
    lines.append(f"{p.name} status={st}")
    if st != "PASS":
        status = "FAIL"

log_path.write_text("\n".join(lines), encoding="utf-8")
print(status)
PY

SCORECARD_STATUS=$(tail -n 1 "$EVIDENCE_DIR/scorecards_status.txt")
if [[ "$SCORECARD_STATUS" != "PASS" ]]; then
  STATUS="FAIL"
fi

# ORR doc check
ORR_LOG="$EVIDENCE_DIR/orr_doc_check.log"
if [[ ! -s "$ROOT_DIR/docs/sprint_29_orr_summary.md" ]]; then
  echo "ORR summary missing or empty" | tee "$ORR_LOG"
  STATUS="FAIL"
else
  echo "ORR summary present" | tee "$ORR_LOG"
fi

# Sanity minimal
SANITY_LOG="$EVIDENCE_DIR/orr_sanity.log"
SANITY_STATUS="PASS"
echo "[S29_G5] Sanity pytest (core)" | tee "$SANITY_LOG"
if ! (cd "$ROOT_DIR" && PYTHONPATH=. ./.venv/bin/pytest tests/unit/test_ingest_pipeline.py -q >>"$SANITY_LOG" 2>&1); then
  SANITY_STATUS="FAIL"
  STATUS="FAIL"
fi

# Bundle
BUNDLE_LOG="$EVIDENCE_DIR/orr_bundle.log"
if [[ "$STATUS" == "PASS" ]]; then
  echo "[S29_G5] Building evidence bundle" | tee "$BUNDLE_LOG"
  (cd "$ROOT_DIR" && zip -r "$BUNDLE_PATH" \
    docs/sprint_29_orr_summary.md \
    out/evidence/S29_G0_scope_and_baseline \
    out/evidence/S29_G1_model_and_migrations \
    out/evidence/S29_G2_api_and_validator \
    out/evidence/S29_G3_ui_and_frontend_quality \
    out/evidence/S29_G4_runtime_and_observability \
    out/scorecards/S29_G0_scope_and_baseline.json \
    out/scorecards/S29_G1_model_and_migrations.json \
    out/scorecards/S29_G2_api_and_validator.json \
    out/scorecards/S29_G3_ui_and_frontend_quality.json \
    out/scorecards/S29_G4_runtime_and_observability.json \
    out/scorecards/S29_G5_orr_and_bundle.json \
    >>"$BUNDLE_LOG" 2>&1) || STATUS="FAIL"
else
  echo "[S29_G5] Skipping bundle due to prior failures" | tee "$BUNDLE_LOG"
fi

python3 - <<'PY' "$SCORECARD_PATH" "$STATUS" "$BUNDLE_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
bundle_path = sys.argv[3]
timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
scorecard = {
    "gate_id": "S29_G5",
    "status": status,
    "timestamp": timestamp,
    "bundle_path": str(bundle_path),
    "notes": "" if status == "PASS" else "Cheque logs em out/evidence/S29_G5_orr_and_bundle",
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    sys.exit(1)
PY

echo "[S29_G5] Scorecard gerado em $SCORECARD_PATH com status $STATUS"
