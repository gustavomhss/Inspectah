#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${ROOT_DIR}/.venv/bin/python"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi
SCORECARD_DIR="$ROOT_DIR/out/scorecards"
EVIDENCE_DIR="$ROOT_DIR/out/evidence/S19_G1_contracts_and_data"
SCORECARD_PATH="$SCORECARD_DIR/S19_G1_contracts_and_data.json"

mkdir -p "$SCORECARD_DIR" "$EVIDENCE_DIR"

"$PYTHON_BIN" - <<'PY' "$SCORECARD_PATH" "$EVIDENCE_DIR"
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient
from inspectah.api import build_app

scorecard_path = Path(sys.argv[1])
evidence_dir = Path(sys.argv[2])

app = build_app()
if app is None:
    raise SystemExit("[S19_G1] FastAPI app não pôde ser construída")

client = TestClient(app)

cases = {
    "timeline": ["obra_publica:2025-123", "evento_climatico:inmet-2025-0901"],
    "xray": ["evento_climatico:inmet-2025-0901", "obra_publica:2025-123"],
}

checks = []
all_ok = True

for cid in cases["timeline"]:
    resp = client.get(f"/admin/cases/{cid}/timeline")
    payload = resp.json() if resp.content else {}
    (evidence_dir / f"timeline_{cid.replace(':', '_')}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    ok = resp.status_code == 200 and bool(payload.get("timeline", {}).get("events"))
    checks.append({"case_id": cid, "endpoint": "timeline", "status_code": resp.status_code, "ok": ok})
    all_ok = all_ok and ok

for cid in cases["xray"]:
    resp = client.get(f"/admin/cases/{cid}/xray")
    payload = resp.json() if resp.content else {}
    (evidence_dir / f"xray_{cid.replace(':', '_')}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    xray = payload.get("xray", {})
    ok = resp.status_code == 200 and all(section in xray for section in ["debunker", "committees", "anchors", "evidences"])
    checks.append({"case_id": cid, "endpoint": "xray", "status_code": resp.status_code, "ok": ok})
    all_ok = all_ok and ok

missing_resp = client.get("/admin/cases/nao-existe/timeline")
checks.append({"case_id": "nao-existe", "endpoint": "timeline", "status_code": missing_resp.status_code, "ok": missing_resp.status_code == 404})
all_ok = all_ok and missing_resp.status_code == 404

status = "PASS" if all_ok else "FAIL"
scorecard = {
    "gate_id": "S19_G1",
    "status": status,
    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "details": {"endpoints_checked": checks},
}

scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")
if status != "PASS":
    raise SystemExit("[S19_G1] Falhou algum contrato de timeline/xray")
PY

echo "[S19_G1] OK - scorecard em $SCORECARD_PATH"
