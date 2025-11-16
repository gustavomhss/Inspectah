#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="$(command -v python3)"
fi

$PYTHON_BIN - <<'PY'
from __future__ import annotations

import re
import time
from pathlib import Path

import yaml
from inspectah.sprint7.gate_utils import get_client, preserved_file, prepare_gate_paths, write_json

slug = "S7_G6_ui_only_flows"
scorecard_path, evidence_dir = prepare_gate_paths(slug)

client = get_client()
status = "PASS"
notes = []

# Flow Admin
source_path = Path("config") / "sources" / "fonte_b.yaml"
admin_start = time.perf_counter()
with preserved_file(source_path):
    data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
    transport_url = data.get("transport", {}).get("url", "")
    payload = {
        "name": data.get("name", ""),
        "description": "Fluxo admin UI",
        "transport_url": transport_url,
        "sample_file": data.get("sample_file", ""),
        "notes": "Fluxo admin UI\nVerificar sincronismo",
        "enabled": "1",
    }
    resp = client.post("/admin/sources/fonte_b", data=payload)
    if resp.status_code != 200:
        status = "FAIL"
        notes.append("Falha ao atualizar fonte_b via UI.")
admin_elapsed = time.perf_counter() - admin_start

# Flow User
user_start = time.perf_counter()
query_resp = client.post("/query", data={"regiao": "Zona Norte"})
if query_resp.status_code != 200:
    status = "FAIL"
    notes.append("Consulta de usuário retornou erro.")
text = query_resp.text
link_match = re.search(r"href=['\"]([^'\"]+evidence/[^'\"]+)['\"]", text)
if not link_match:
    status = "FAIL"
    notes.append("Nenhum link de evidência encontrado.")
else:
    link = link_match.group(1)
    if link.startswith("http"):
        link = link.split("://", 1)[-1]
        link = link[link.find("/") :]
    ev_resp = client.get(link)
    if ev_resp.status_code != 200 or "Manifesto" not in ev_resp.text:
        status = "FAIL"
        notes.append("Falha ao abrir página de evidência.")
user_elapsed = time.perf_counter() - user_start

metrics = {
    "m1_end_to_end_boot_and_use_seconds": round(admin_elapsed + user_elapsed, 2),
    "m2_user_flow_seconds": round(user_elapsed, 2),
    "admin_flow_seconds": round(admin_elapsed, 2),
}

details = {
    "notes": notes,
    "terminal_required": False,
}
write_json(scorecard_path, {
    "gate": "S7_G6",
    "name": "ui_only_flows",
    "status": status,
    "metrics": metrics,
    "details": details,
})
write_json(evidence_dir / "summary.json", {**details, **metrics})

if status != "PASS":
    raise SystemExit("S7-G6 failed")
PY
