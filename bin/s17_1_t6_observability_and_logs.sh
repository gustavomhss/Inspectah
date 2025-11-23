#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T6_observability_and_logs"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T6_observability_and_logs.json"
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

resp = client.post("/api/consultation", json={"question": "Consulta de observabilidade em projeto público?"})
payload = resp.json()
(evidence_dir / "observability_payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

request_id_ok = bool(payload.get("request_id"))
risk_flags_ok = isinstance(payload.get("risk_flags"), list)
anchor_ok = isinstance(payload.get("notes"), str) and "anchor:" in payload.get("notes")
status = "PASS" if resp.status_code == 200 and request_id_ok and risk_flags_ok and anchor_ok else "FAIL"
scorecard = {
    "gate": "S17_1_T6_observability_and_logs",
    "status": status,
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T6] Observabilidade incompleta.")
PY

echo "[S17_1_T6] OK. Scorecard em $SCORECARD_PATH"
