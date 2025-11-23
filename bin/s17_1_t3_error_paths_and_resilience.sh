#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T3_error_paths_and_resilience"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T3_error_paths_and_resilience.json"
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

invalid_payload = client.post("/api/consultation", json={})
unknown_domain = client.post("/api/consultation", json={"question": "???"})

records = {
    "invalid_payload": {"status": invalid_payload.status_code, "body": invalid_payload.json()},
    "unknown_domain": {"status": unknown_domain.status_code, "body": unknown_domain.json()},
}
(evidence_dir / "error_cases.json").write_text(json.dumps(records, indent=2), encoding="utf-8")

status_codes_ok = invalid_payload.status_code in {400, 422} and unknown_domain.status_code == 200
unknown_is_unknown = str(unknown_domain.json().get("risk_level")).lower() == "unknown"
status = "PASS" if status_codes_ok else "FAIL"
if status == "PASS" and not unknown_is_unknown:
    status = "FAIL"
scorecard = {
    "gate": "S17_1_T3_error_paths_and_resilience",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T3] Erros não tratados corretamente.")
PY

echo "[S17_1_T3] OK. Scorecard em $SCORECARD_PATH"
