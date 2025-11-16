#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

REPO_ROOT="$REPO_ROOT" "$PYTHON_BIN" - <<'PY'
from __future__ import annotations

import json
import os
import time
from pathlib import Path

from inspectah.sprint7.gate_utils import get_client

slug = "S7_G1_ui_boot_health"
repo_root = Path(os.environ["REPO_ROOT"])
scorecard_path = repo_root / "out" / "scorecards" / f"{slug}.json"
evidence_dir = repo_root / "out" / "evidence" / slug
scorecard_path.parent.mkdir(parents=True, exist_ok=True)
evidence_dir.mkdir(parents=True, exist_ok=True)

start = time.perf_counter()
client = get_client()
resp = client.get("/health")
elapsed = time.perf_counter() - start

status = "PASS" if resp.status_code == 200 and resp.json().get("status") == "ok" else "FAIL"
details = {
    "status_code": resp.status_code,
    "payload": resp.json(),
    "boot_seconds": round(elapsed, 2),
}
scorecard = {
    "gate": "S7_G1",
    "name": "ui_boot_health",
    "status": status,
    "metrics": {"m1_boot_seconds": details["boot_seconds"]},
    "details": details,
}
scorecard_path.write_text(json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(evidence_dir / "summary.json").write_text(json.dumps(details, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if status != "PASS":
    raise SystemExit("S7-G1 failed")
PY
