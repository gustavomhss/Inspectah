#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G6] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S13_G6"
SCORECARD_PATH="$SCORECARD_DIR/S13_G6_feedback_multi_dominio.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s13_feedback_backlog import run_feedback_backlog

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
report = run_feedback_backlog(evidence_dir=evidence_dir)
ratio = report["feedback_delivery_ratio"]
status = "PASS"
if ratio < 0.95:
    status = "WARN" if ratio >= 0.90 else "FAIL"

payload = {
    "gate": "S13_G6",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {
        "feedback_delivery_ratio": ratio,
        "per_domain_feedback_ratio": report["per_domain_feedback_ratio"],
    },
    "scenarios": report["scenarios"],
}
scorecard_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

if status == "FAIL":
    raise SystemExit("S13-G6 falhou. Consulte out/evidence/S13_G6/*.json para detalhes.")
PY

printf '[S13][G6] Feedback multi-domínio avaliado. Scorecard em %s\n' "$SCORECARD_PATH"
