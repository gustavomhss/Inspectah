#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S22_G2_service_contracts"
SCORECARD_PATH="$SCORECARD_DIR/S22_G2_service_contracts.json"
DOC_CONTRATOS="$ROOT_DIR/docs/sprint_22_g2_contratos_de_servico.md"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

status="PASS"
notes="Contratos e testes de serviços ok."
api_ops=0
api_tests_count=0
api_tests_pass_rate=0.0
error_cases=0

if [[ ! -f "$DOC_CONTRATOS" ]]; then
  status="FAIL"
  notes="Doc de contratos não encontrado."
else
  api_ops=$(rg --no-heading -c "^### 2" "$DOC_CONTRATOS" || echo "0")
  error_cases=$(rg --no-heading -c "400:|404:|run em andamento|config desabilitada" "$DOC_CONTRATOS" || echo "0")
fi

echo "[S22_G2] Coletando testes de serviço..." > "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_service_contracts.py --collect-only -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  api_tests_count=$(tail -n +1 "$EVIDENCE_DIR/tests.log" | grep -E "tests/ingestion/test_service_contracts.py::" | wc -l | tr -d ' ')
else
  status="FAIL"
  notes="Falha ao coletar testes de serviços."
fi

echo "[S22_G2] Rodando testes de serviço..." >> "$EVIDENCE_DIR/tests.log"
if (cd "$ROOT_DIR" && .venv/bin/python -m pytest tests/ingestion/test_service_contracts.py -q >> "$EVIDENCE_DIR/tests.log" 2>&1); then
  api_tests_pass_rate=1.0
else
  status="FAIL"
  notes="Falha nos testes de serviços/API."
fi

python3 - <<'PY' "$SCORECARD_PATH" "$status" "$notes" "$api_ops" "$api_tests_count" "$api_tests_pass_rate" "$error_cases"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

scorecard = {
    "gate_id": "S22_G2",
    "status": sys.argv[2],
    "api_operations_documented": int(sys.argv[4]),
    "api_tests_count": int(sys.argv[5]),
    "api_tests_pass_rate": float(sys.argv[6]),
    "error_cases_covered": int(sys.argv[7]),
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
    "notes": "Testes de contratos de serviço/API."
}
(evidence_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
PY

echo "[S22_G2] status=$status api_ops=$api_ops api_tests=$api_tests_count"
