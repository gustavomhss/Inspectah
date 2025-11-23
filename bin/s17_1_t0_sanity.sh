#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S17_1_T0_sanity"
SCORECARD_PATH="$SCORECARD_DIR/S17_1_T0_sanity.json"
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
openapi = client.get("/openapi.json")
paths = openapi.json().get("paths", {})
route_exists = "/api/consultation" in paths
status = "PASS" if openapi.status_code == 200 and route_exists else "FAIL"
(evidence_dir / "openapi.json").write_text(json.dumps(openapi.json(), indent=2), encoding="utf-8")
scorecard = {
    "gate": "S17_1_T0_sanity",
    "status": status,
    "routes": list(paths.keys()),
    "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S17_1_T0] Falhou: rota /api/consultation ausente.")
PY

echo "[S17_1_T0] OK. Scorecard em $SCORECARD_PATH"
