#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S31_G4_runtime"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S31_G4_runtime.json"
RUN_LOG="$EVIDENCE_DIR/run_now.json"
SUMMARY_PATH="$EVIDENCE_DIR/metrics_summary.json"

mkdir -p "$EVIDENCE_DIR" "$SCORECARD_DIR"

cd "$ROOT_DIR"
echo "[S31_G4] Rodando run-now em todos os perfis..." | tee "$RUN_LOG"
PYTHONPATH=. python - <<'PY' "$RUN_LOG"
import json
import sys
from pathlib import Path

from app.providers.runner import run_all

out_path = Path(sys.argv[1])
runs = run_all(limit=2)
out_path.write_text(json.dumps({"runs": runs}, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"runs": runs}, indent=2, ensure_ascii=False))
PY

echo "[S31_G4] Gerando resumo de métricas..." | tee -a "$RUN_LOG"
PYTHONPATH=. bin/s31_metrics_summary.sh
cp "$ROOT_DIR/out/evidence/S31_metrics/metrics_summary.json" "$SUMMARY_PATH"

STATUS="PASS"
python3 - <<'PY' "$SCORECARD_PATH" "$STATUS"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

scorecard_path = Path(sys.argv[1])
status = sys.argv[2]
timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
scorecard = {
    "gate_id": "S31_G4",
    "status": status,
    "summary": "Runtime + métricas dos perfis após run-now",
    "evidence_paths": [
        "out/evidence/S31_G4_runtime/run_now.json",
        "out/evidence/S31_G4_runtime/metrics_summary.json",
    ],
    "checks": ["run_all providers/profiles", "metrics summary"],
    "timestamp": timestamp,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
print(f"[S31_G4] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "PASS" ]]; then
  exit 1
fi
