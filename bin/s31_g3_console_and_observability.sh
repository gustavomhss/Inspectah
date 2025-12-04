#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S31_G3_console"
API_LOG="$EVIDENCE_DIR/api_tests.log"
FRONT_LOG="$EVIDENCE_DIR/front_tests.log"
RUN_LOG="$EVIDENCE_DIR/run_now.json"
SCORECARD_PATH="$SCORECARD_DIR/S31_G3_console.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

echo "[S31_G3] Rodando testes de API (providers/perfis)..." | tee "$API_LOG"
cd "$ROOT_DIR"
PYTHONPATH=. poetry run true >/dev/null 2>&1 || true
PYTHONPATH=. pytest tests/api/test_providers_console.py -q | tee -a "$API_LOG"

echo "[S31_G3] Rodando testes de frontend do console de providers..." | tee "$FRONT_LOG"
cd "$ROOT_DIR/frontend/inspectah-ui"
npm test -- src/features/providers/__tests__/providersPage.test.tsx | tee -a "$FRONT_LOG"

echo "[S31_G3] Executando run-now em todos perfis para gerar métricas..." | tee -a "$RUN_LOG"
cd "$ROOT_DIR"
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

cd "$ROOT_DIR"
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
    "gate_id": "S31_G3",
    "status": status,
    "summary": "Console providers/perfis com testes de API/FE e run-now",
    "checks": [
        "pytest tests/api/test_providers_console.py",
        "npm test -- src/features/providers/__tests__/providersPage.test.tsx",
        "run_all providers/profiles (limit=2)",
    ],
    "issues_detected": [],
    "evidence_paths": [
        "out/evidence/S31_G3_console/api_tests.log",
        "out/evidence/S31_G3_console/front_tests.log",
        "out/evidence/S31_G3_console/run_now.json",
    ],
    "timestamp": timestamp,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
print(f"[S31_G3] Scorecard salvo em {scorecard_path}")
PY

if [[ "$STATUS" != "PASS" ]]; then
  exit 1
fi
