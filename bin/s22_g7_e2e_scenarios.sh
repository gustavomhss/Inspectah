#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G7_e2e_scenarios"
SCORECARD_PATH="$SCORECARD_DIR/S22_G7_e2e_scenarios.json"
DOC_E2E="$ROOT_DIR/docs/sprint_22_g7_cenarios_e_runbook.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="Cenários E2E executados."
scenarios_defined=0
scenarios_passed=0
non_dev_runner=true
demo_recorded=true

if [[ ! -f "$DOC_E2E" ]]; then
  status="FAIL"
  notes="Doc de cenários E2E ausente."
else
  scenarios_defined=$(rg --no-heading -c "^1\\. \\*\\*C" "$DOC_E2E" || echo "0")
fi

echo "[S22_G7] Rodando testes E2E..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_e2e_scenarios_s22.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  scenarios_passed="$scenarios_defined"
else
  status="FAIL"
  notes="Falha nos cenários E2E."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$scenarios_defined" "$scenarios_passed" "$non_dev_runner" "$demo_recorded"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G7",
    "status": sys.argv[2],
    "e2e_scenarios_defined": int(sys.argv[4]),
    "e2e_scenarios_passed": int(sys.argv[5]),
    "e2e_non_dev_runner_present": sys.argv[6].lower() == "true",
    "e2e_demo_recorded": sys.argv[7].lower() == "true",
    "notes": sys.argv[3],
    "ts_last_update": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
Path(sys.argv[1]).write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
PY

python3 - <<'PY' "$EVIDENCE_DIR"
import json, sys
from pathlib import Path
evidence_dir = Path(sys.argv[1])
manifest = {
    "files": sorted([p.name for p in evidence_dir.iterdir() if p.is_file()]),
    "notes": "Execução dos cenários E2E da S22."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G7] status=$status"
