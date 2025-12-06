#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

EVIDENCE_DIR="out/evidence/S35_ORR"
SCORECARD_PATH="out/scorecards/S35_G5_orr.json"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR" out/scorecards

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi

echo "[S35_G5] ORR agregando G0–G4 + metrics_summary + bundle" | tee "$LOG"

# Verifica artefatos principais
missing=()
for f in \
  out/scorecards/S35_G0_scope.json \
  out/scorecards/S35_G1_model.json \
  out/scorecards/S35_G2_console.json \
  out/scorecards/S35_G3_obs.json \
  out/scorecards/S35_G4_pilotos.json \
  out/scorecards/S35_metrics_summary.json \
  out/bundles/inspectah_s35_evidence_bundle.zip \
  out/evidence/S35_G4_pilotos_rollout/rollout_timeline.json \
  out/evidence/S35_G4_pilotos_rollout/console_screenshots/flows.png \
  out/evidence/S35_G4_pilotos_rollout/console_screenshots/flow_detail.png
do
  [ -f "$f" ] || missing+=("$f")
done

STATUS="PASS"
if [ ${#missing[@]} -gt 0 ]; then
  STATUS="FAIL"
  echo "[S35_G5] Arquivos faltando: ${missing[*]}" | tee -a "$LOG"
fi

# Check bundle integrity
if [ "$STATUS" = "PASS" ]; then
  if ! unzip -t out/bundles/inspectah_s35_evidence_bundle.zip >/dev/null; then
    STATUS="FAIL"
    echo "[S35_G5] unzip -t falhou" | tee -a "$LOG"
  fi
fi

# Resumo de métricas dos scorecards
$PYTHON_BIN - <<'PY' 2>&1 | tee -a "$LOG"
import json
from pathlib import Path

scorecards = {}
for name in [
    "S35_G0_scope.json",
    "S35_G1_model.json",
    "S35_G2_console.json",
    "S35_G3_obs.json",
    "S35_G4_pilotos.json",
    "S35_metrics_summary.json",
]:
    path = Path("out/scorecards") / name
    scorecards[name] = json.loads(path.read_text()) if path.exists() else {"status": "MISSING"}
print("[S35_G5] Scorecards:", json.dumps(scorecards, indent=2))
PY

cat > "$SCORECARD_PATH" <<JSON
{
  "gate": "S35_G5_orr",
  "status": "$STATUS",
  "bundle": "out/bundles/inspectah_s35_evidence_bundle.zip",
  "missing": ${#missing[@]},
  "notes": "ORR agregando scorecards/evidências; ver run.log para detalhes."
}
JSON

echo "[S35_G5] Resultado: $STATUS (scorecard em $SCORECARD_PATH)" | tee -a "$LOG"
exit 0
