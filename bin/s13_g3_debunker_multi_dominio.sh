#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G3] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S13_G3"
SCORECARD_PATH="$SCORECARD_DIR/S13_G3_debunker_multi_dominio.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s13_debunker_checks import run_debunker_checks

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])

report = run_debunker_checks(evidence_dir=evidence_dir)
metrics = report["metrics"]
coverage = metrics["debunker_explanation_coverage"]
status = "PASS" if coverage >= 0.95 else ("WARN" if coverage >= 0.8 else "FAIL")

data = {
    "gate": "S13_G3",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": metrics,
}
scorecard_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

if status == "FAIL":
    raise SystemExit("S13-G3 falhou. Consulte out/evidence/S13_G3/debunker_decisions.json")
PY

printf '[S13][G3] Debunker multi-domínio avaliado. Scorecard em %s\n' "$SCORECARD_PATH"
