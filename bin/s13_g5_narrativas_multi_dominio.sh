#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G5] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S13_G5"
SCORECARD_PATH="$SCORECARD_DIR/S13_G5_narrativas_multi_dominio.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

export PYTHONPATH="$ROOT_DIR"

python3 - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s13_narratives_registry import run_narratives_checks

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])
report = run_narratives_checks(evidence_dir=evidence_dir)
ratio = report["narrative_completeness_ratio"]
status = "PASS" if ratio == 1.0 else "FAIL"

data = {
    "gate": "S13_G5",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {
        "narrative_completeness_ratio": ratio,
        "per_domain_narrative_ratio": report["per_domain_narrative_ratio"],
    },
    "pilots": report["pilots"],
}
scorecard_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

if status != "PASS":
    raise SystemExit("S13-G5 falhou. Verifique as narrativas em out/evidence/S13_G5/narrativas/.")
PY

printf '[S13][G5] Narrativas multi-domínio avaliadas. Scorecard em %s\n' "$SCORECARD_PATH"
