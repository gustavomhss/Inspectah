#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S18_G5_health_mapping"
SCORECARD_PATH="$SCORECARD_DIR/S18_G5_health_mapping.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

python3 - <<'PY' "$EVIDENCE_DIR" "$SCORECARD_PATH"
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from inspectah.api import build_app

evidence_dir = Path(sys.argv[1])
scorecard_path = Path(sys.argv[2])

app = build_app()
if app is None:
    raise SystemExit("[S18_G5] Não foi possível construir o app FastAPI.")

client = TestClient(app)

start = time.perf_counter()
resp = client.get("/admin/health")
elapsed = time.perf_counter() - start
payload = resp.json() if resp.status_code == 200 else {}

backend_snapshot = {"status_code": resp.status_code, "payload": payload, "elapsed_seconds": elapsed}
(evidence_dir / "backend_health_snapshots.json").write_text(json.dumps(backend_snapshot, indent=2), encoding="utf-8")

status = "PASS" if resp.status_code == 200 else "FAIL"
details = {"elapsed_seconds": elapsed}
m1 = elapsed

scorecard = {
    "gate_id": "S18_G5",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "metrics": {"M1": m1},
    "details": details,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit(f"[S18_G5] FAIL: status_code={resp.status_code}")
PY

echo "[S18_G5] OK - scorecard em $SCORECARD_PATH"
