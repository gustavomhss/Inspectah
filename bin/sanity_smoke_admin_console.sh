#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$ROOT_DIR/.venv"
EVIDENCE_PATH="$ROOT_DIR/out/evidence/admin_console_smoke.json"

if [[ ! -d "$VENV_PATH" ]]; then
  >&2 echo "[smoke] Virtualenv não encontrado em .venv"
  exit 2
fi

source "$VENV_PATH/bin/activate"
export PYTHONPATH="$ROOT_DIR"
export INSPECTAH_S23_DB_PATH="$ROOT_DIR/out/runtime/admin_console_smoke.sqlite"

python - <<'PY'
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

from fastapi.testclient import TestClient

# Preparar app e paths
ROOT = Path(__file__).resolve().parents[1]
FLOW_PATH = ROOT / "out/runtime/console_agents_flow.json"
EVIDENCE_PATH = ROOT / "out/evidence/admin_console_smoke.json"
DB_PATH = Path(os.environ["INSPECTAH_S23_DB_PATH"])

# Carrega app depois de configurar variáveis
from inspectah.api import app  # noqa: E402

if app is None:
  sys.exit("[smoke] inspectah.api não pôde ser carregado")

client = TestClient(app)

def check(method: Callable[..., Any], path: str, expected: int = 200, **kwargs):
  resp = method(path, **kwargs)
  if resp.status_code != expected:
    raise SystemExit(f"[smoke] {path} retornou {resp.status_code}, esperado {expected}")
  return resp.json()

# Backup de fluxo para restaurar depois
flow_backup = None
if FLOW_PATH.exists():
  flow_backup = FLOW_PATH.read_text(encoding="utf-8")

results: dict[str, Any] = {}

try:
  results["admin_health"] = check(client.get, "/admin/health")
  results["admin_cases"] = check(client.get, "/admin/cases")

  flow_payload = [{"agent_id": "smoke_agent"}]
  results["console_flow_before"] = check(client.get, "/api/console/agents/flow")
  results["console_flow_set"] = check(client.put, "/api/console/agents/flow", json=flow_payload)
  results["console_flow_after"] = check(client.get, "/api/console/agents/flow")

  agent_payload = {
      "name": "smoke_agent_console",
      "description": "agente de smoke do console",
      "instructions": "checagem mínima de console",
      "role": "debunker",
      "layer": "interpretation",
      "model_name": "gpt-4o-mini",
      "recommended_model_name": "gpt-4o-mini",
      "temperature": 0.2,
      "max_tokens": 4000,
      "top_p": 1.0,
      "status": "active",
      "kb_refs": [],
      "created_by": "smoke",
  }
  created_agent = check(client.post, "/api/console/agents", expected=201, json=agent_payload)
  agent_id = created_agent["id"]
  results["agent_created"] = created_agent
  results["agent_detail"] = check(client.get, f"/api/console/agents/{agent_id}")
  results["agent_versions_initial"] = check(client.get, f"/api/console/agents/{agent_id}/instructions")

  version_payload = {
      "changelog": "smoke v2",
      "instructions": "versao smoke v2",
      "created_by": "smoke",
      "model_name": "gpt-4o-mini",
      "temperature": 0.2,
      "max_tokens": 4000,
      "top_p": 1.0,
      "kb_snapshot": [],
  }
  results["agent_version_added"] = check(
      client.post, f"/api/console/agents/{agent_id}/instructions", expected=201, json=version_payload
  )
  results["agent_versions_final"] = check(client.get, f"/api/console/agents/{agent_id}/instructions")

  results["console_agents_list"] = check(client.get, "/api/console/agents")

  EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
  EVIDENCE_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
  print(f"[smoke] OK. Evidência em {EVIDENCE_PATH}")
finally:
  # Restaurar fluxo original
  if flow_backup is None:
    FLOW_PATH.unlink(missing_ok=True)
  else:
    FLOW_PATH.write_text(flow_backup, encoding="utf-8")
  # Limpar DB temporário
  if DB_PATH.exists():
    DB_PATH.unlink()
PY
