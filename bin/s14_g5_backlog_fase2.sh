#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S14] Rode a partir da raiz do repo (faltou .git)."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S14_G5"
SCORECARD_PATH="$SCORECARD_DIR/S14_G5_backlog_fase2.json"
REPORT_PATH="$EVIDENCE_DIR/backlog_fase2_report.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"
python3 -m scripts.s14_backlog_fase2

if [[ ! -f "$REPORT_PATH" ]]; then
  >&2 echo "[S14_G5] Report não encontrado em $REPORT_PATH"
  exit 1
fi

python3 - <<'PY' "$REPORT_PATH" "$SCORECARD_PATH"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

report_path = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
report = json.loads(report_path.read_text(encoding="utf-8"))

metrics = report.get("metrics", {})
issues = report.get("issues", []) or []
coverage = float(metrics.get("coverage_ratio", 0.0))
total_items = metrics.get("total_items", 0)

status = report.get("status", "FAIL")
reasons = list(issues)

if total_items == 0 or coverage < 0.5:
    status = "FAIL"
    if "backlog vazio" not in reasons:
        reasons.append("backlog vazio ou coverage < 0.5")

scorecard = {
    "gate": "S14_G5",
    "status": status,
    "total_items": total_items,
    "coverage_ratio": coverage,
    "issues": reasons,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False), encoding="utf-8")
if status == "FAIL":
    raise SystemExit("S14_G5 falhou; consulte scorecard.")
PY

echo "[S14_G5] Status registrado em $SCORECARD_PATH"
