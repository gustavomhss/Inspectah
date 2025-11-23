#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T1_contracts_and_states"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T1_contracts_and_states.json"
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
app = build_app()
client = TestClient(app)
openapi = client.get("/openapi.json").json()
components = openapi.get("components", {}).get("schemas", {})
paths = openapi.get("paths", {})
contract = paths.get("/api/consultation", {}).get("post", {})
def _resolve(schema: dict) -> dict:
    if "$ref" in schema:
        ref = schema["$ref"]
        name = ref.split("/")[-1]
        return components.get(name, schema)
    return schema

request_schema = _resolve(
    contract.get("requestBody", {})
    .get("content", {})
    .get("application/json", {})
    .get("schema", {})
)
response_schema = _resolve(
    contract.get("responses", {})
    .get("200", {})
    .get("content", {})
    .get("application/json", {})
    .get("schema", {})
)
req_fields = set(request_schema.get("properties", {}).keys())
resp_fields = set(response_schema.get("properties", {}).keys())
requirements = {
    "question_in_request": "question" in req_fields,
    "answer_in_response": "answer" in resp_fields,
    "risk_level_in_response": "risk_level" in resp_fields,
    "evidences_in_response": "evidences" in resp_fields,
}
(evidence_dir / "contract_snapshot.json").write_text(json.dumps(contract, indent=2), encoding="utf-8")
status = "PASS" if all(requirements.values()) else "FAIL"
scorecard = {
    "gate": "S17_1_T1_contracts_and_states",
    "status": status,
    "requirements": requirements,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T1] Contrato divergente do esperado.")
PY

echo "[S17_1_T1] OK. Scorecard em $SCORECARD_PATH"
