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
import time
from pathlib import Path

import yaml
from inspectah.sprint7.gate_utils import get_client, preserved_file, prepare_gate_paths, write_json

slug = "S7_G2_ui_sources_admin"
scorecard_path, evidence_dir = prepare_gate_paths(slug)

client = get_client()
index_resp = client.get("/admin/sources")
status = "PASS" if index_resp.status_code == 200 else "FAIL"
notes = []

source_id = "fonte_a"
source_path = Path("config") / "sources" / f"{source_id}.yaml"
timestamp = int(time.time())
new_note = f"Atualizado via UI test {timestamp}"

try:
    with preserved_file(source_path):
        payload = {
            "name": "Boletim RSS Sindicato SP",
            "description": "Fonte ajustada via UI",
            "transport_url": "https://dados.sindicato-sp.org/boletim/rss",
            "sample_file": "fixtures/sprint_6/fonte_a_rss.xml",
            "notes": f"{new_note}\nMonitorar sazonalidade",
            "enabled": "1",
        }
        resp = client.post(f"/admin/sources/{source_id}", data=payload)
        if resp.status_code != 200:
            status = "FAIL"
            notes.append(f"POST update returned {resp.status_code}")
        data = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        if new_note not in (data.get("notes") or []):
            status = "FAIL"
            notes.append("Note not persisted to fonte_a.yaml")
except FileNotFoundError:
    status = "FAIL"
    notes.append(f"{source_path} não encontrado")

temp_id = f"fonte_s7_temp_{timestamp}"
temp_path = Path("config") / "sources" / f"{temp_id}.yaml"
if temp_path.exists():
    temp_path.unlink()

create_payload = {
    "id": temp_id,
    "name": "Fonte Experimental",
    "description": "Criada automaticamente para validação da UI",
    "transport_url": "https://example.invalid",
    "sample_file": "fixtures/sprint_6/fonte_a_rss.xml",
    "notes": "Fonte temporária",
}
resp = client.post("/admin/sources/new", data=create_payload)
if resp.status_code != 200:
    status = "FAIL"
    notes.append(f"Falha ao criar nova fonte (status {resp.status_code})")
if not temp_path.exists():
    status = "FAIL"
    notes.append("Arquivo da nova fonte não foi criado.")
else:
    temp_path.unlink()

metrics = {"m3_admin_crud_success_rate": 1.0 if status == "PASS" else 0.0}
details = {
    "tested_source": source_id,
    "new_note": new_note,
    "created_source": temp_id,
    "notes": notes,
}
write_json(scorecard_path, {
    "gate": "S7_G2",
    "name": "ui_sources_admin",
    "status": status,
    "metrics": metrics,
    "details": details,
})
write_json(evidence_dir / "summary.json", details)

if status != "PASS":
    raise SystemExit("S7-G2 failed")
PY
