#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G7"
SCORECARD_PATH="$SCORECARD_DIR/S14_G7_observabilidade.json"
REPORT_PATH="$EVIDENCE_DIR/metrics_snapshot.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

# Reutiliza o snapshot gerado pelo s14_metrics_snapshot (também usado no G6)
export PYTHONPATH="$ROOT_DIR"
python3 -m scripts.s14_metrics_snapshot

if [[ ! -f "$REPORT_PATH" ]]; then
  >&2 echo "[S14_G7] Report não encontrado em $REPORT_PATH"
  exit 1
fi

python3 - <<'PY' "$REPORT_PATH" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))

global_health = report.get("global_health", "CRITICAL")
if global_health == "OK":
    status = "PASS"
elif global_health == "WARN":
    status = "WARN"
else:
    status = "FAIL"

scorecard = {
    "gate": "S14_G7",
    "status": status,
    "global_health": global_health,
    "health_by_gate": report.get("health_by_gate", {}),
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status == "FAIL":
    raise SystemExit("S14_G7 falhou; consulte scorecard.")
PY

echo "[S14_G7] Status registrado em $SCORECARD_PATH"
