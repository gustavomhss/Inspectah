#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

$PYTHON_BIN - <<'PY'
from __future__ import annotations

import json
import re

from inspectah.sprint7.gate_utils import get_client, prepare_gate_paths, write_json

slug = "S7_G5_ui_evidence_trace"
scorecard_path, evidence_dir = prepare_gate_paths(slug)

client = get_client()
resp = client.post("/query", data={"categoria": "proteinas"})
if resp.status_code != 200:
    write_json(scorecard_path, {"gate": "S7_G5", "status": "FAIL", "details": {"error": "query failed"}})
    raise SystemExit("S7-G5 failed")

links = re.findall(r"href=['\"]([^'\"]+evidence/[^'\"]+)['\"]", resp.text)
unique_links = []
seen = set()
for link in links:
    if link.startswith("http"):
        link = link.split("://", 1)[-1]
        link = link[link.find("/") :]
    if link not in seen:
        seen.add(link)
        unique_links.append(link)
    if len(unique_links) >= 2:
        break

successes = 0
cases = []
for link in unique_links:
    ev_resp = client.get(link)
    has_manifest = "Manifesto" in ev_resp.text
    if ev_resp.status_code == 200 and has_manifest:
        successes += 1
    cases.append({"link": link, "status": ev_resp.status_code, "manifest": has_manifest})

ratio = successes / len(unique_links) if unique_links else 0
metrics = {
    "m6_max_clicks_to_evidence": 2,
    "m6_evidence_found_ratio": round(ratio, 2),
}
status = "PASS" if ratio == 1.0 and unique_links else "FAIL"

details = {"cases": cases}
write_json(scorecard_path, {
    "gate": "S7_G5",
    "name": "ui_evidence_trace",
    "status": status,
    "metrics": metrics,
    "details": details,
})
write_json(evidence_dir / "summary.json", details)

if status != "PASS":
    raise SystemExit("S7-G5 failed")
PY
