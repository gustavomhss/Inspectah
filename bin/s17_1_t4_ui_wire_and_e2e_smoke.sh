#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T4_ui_wire_and_e2e_smoke"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T4_ui_wire_and_e2e_smoke.json"
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

resp = client.post("/api/consultation", json={"question": "Celebridade participou do reality show?"})
body = resp.json()
(evidence_dir / "ui_smoke_response.json").write_text(json.dumps(body, indent=2), encoding="utf-8")

required_fields = all(field in body for field in ("answer", "risk_level", "evidences"))
evidence_shape_ok = bool(body.get("evidences")) and all(
    isinstance(item, dict) and "description" in item for item in body.get("evidences", [])
)
status = "PASS" if resp.status_code == 200 and required_fields and evidence_shape_ok else "FAIL"
scorecard = {
    "gate": "S17_1_T4_ui_wire_and_e2e_smoke",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T4] Smoke E2E falhou.")
PY

echo "[S17_1_T4] OK. Scorecard em $SCORECARD_PATH"
