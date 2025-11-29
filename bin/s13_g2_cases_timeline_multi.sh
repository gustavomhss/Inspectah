#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G2] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S13_G2"
SCORECARD_PATH="$SCORECARD_DIR/S13_G2_cases_timeline_multi.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s13_timeline_checks import run_timeline_checks

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])

report = run_timeline_checks(evidence_dir=evidence_dir)
metrics = report["metrics"]
ratio = metrics["pilot_timeline_integrity_ratio"]
violations = metrics["timelines_with_issues"]
status = "PASS" if ratio >= 0.95 and violations == 0 else ("WARN" if ratio >= 0.8 else "FAIL")

payload = {
    "gate": "S13_G2",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": metrics,
}
scorecard_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

if status == "FAIL":
    raise SystemExit("S13-G2 falhou. Consulte out/evidence/S13_G2/timelines_report.json")
PY

printf '[S13][G2] Timelines multi-domínio avaliadas. Scorecard em %s\n' "$SCORECARD_PATH"
