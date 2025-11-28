#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )/.." && pwd)"
if [[ ! -d "$ROOT_DIR/.git" ]]; then
  >&2 echo "[S13][G4] Script precisa rodar a partir da raiz do repo."
  exit 2
fi

SCORECARD_DIR="$ROOT_DIR/out/scorecards"
SCORECARD_PATH="$SCORECARD_DIR/S13_G4_explorer_multi_dominio.json"
mkdir -p "$SCORECARD_DIR"

export PYTHONPATH="$ROOT_DIR"

python3 - <<'PY' "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.s13_explorer_scenarios import run_explorer_scenarios

scorecard_path = Path(sys.argv[1])
report = run_explorer_scenarios()
success_rate = report["explorer_success_rate"]
domain_rates = report["per_domain_success_rate"]
if success_rate >= 0.95:
    status = "PASS"
elif success_rate >= 0.90:
    status = "WARN"
else:
    status = "FAIL"
if any(rate == 0 for rate in domain_rates.values()):
    status = "FAIL"

data = {
    "gate": "S13_G4",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {
        "explorer_success_rate": success_rate,
        "per_domain_success_rate": domain_rates,
    },
    "scenarios": report["scenarios"],
}
scorecard_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

if status == "FAIL":
    raise SystemExit("S13-G4 falhou. Consulte out/evidence/S13_G4/queries/ para detalhes.")
PY

printf '[S13][G4] Explorer multi-domínio avaliado. Scorecard em %s\n' "$SCORECARD_PATH"
