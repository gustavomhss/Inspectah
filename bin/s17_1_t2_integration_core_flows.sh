#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T2_integration_core_flows"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T2_integration_core_flows.json"
PYTHON_BIN="${PYTHON_BIN:-python3}"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN="$ROOT_DIR/.venv/bin/python"
fi

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

PYTHONPATH="$ROOT_DIR" "$PYTHON_BIN" - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from inspectah.api import build_app


evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])
client = TestClient(build_app())
questions = [
    "Qual o risco político desta eleição?",
    "O campeonato terminou com o time X campeão?",
    "Previsão de chuva forte hoje?",
]
results = []
allowed_levels = {"low", "medium", "high", "unknown"}
for q in questions:
    resp = client.post("/api/consultation", json={"question": q})
    results.append({"question": q, "status": resp.status_code, "body": resp.json()})

(evidence_dir / "integration_flows.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
all_ok = all(r["status"] == 200 for r in results)
risks_ok = all(str(r["body"].get("risk_level")).lower() in allowed_levels for r in results if r["status"] == 200)
evidence_ok = all(isinstance(r["body"].get("evidences"), list) for r in results if r["status"] == 200)
status = "PASS" if all_ok and risks_ok and evidence_ok else "FAIL"
scorecard = {
    "gate": "S17_1_T2_integration_core_flows",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T2] Fluxos integrados falharam.")
PY

echo "[S17_1_T2] OK. Scorecard em $SCORECARD_PATH"
