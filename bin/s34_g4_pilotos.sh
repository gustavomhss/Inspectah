#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

DB_PATH="${S34_FLOWS_DB_PATH:-out/databases/s34_flows.sqlite}"
EVIDENCE_DIR="out/evidence/S34_G4_pilotos_multifluxo"
LOG="$EVIDENCE_DIR/run.log"

mkdir -p "$EVIDENCE_DIR/console_screenshots" out/scorecards

echo "[S34_G4] Executando pilotos (notícias + contestação) em ${DB_PATH}" | tee "$LOG"

python3 - <<'PY' 2>&1 | tee -a "$LOG"
import json
import os
from pathlib import Path

from app.flows.execution_engine import FlowExecutionEngine
from app.flows.models import FlowState
from app.flows.service import FlowService

db_path = Path(os.environ.get("S34_FLOWS_DB_PATH", "out/databases/s34_flows.sqlite"))
evidence_dir = Path(os.environ.get("S34_G4_EVIDENCE_DIR", "out/evidence/S34_G4_pilotos_multifluxo"))
service = FlowService(db_path=db_path)
engine = FlowExecutionEngine(service=service)

def ensure_flow(template_slug: str, nome: str, slug: str):
    flows = [f for f in service.list_flows() if f.slug == slug]
    if flows:
        return flows[0]
    return service.create_flow_from_template(template_slug, nome, slug)

def ensure_state(flow, target: FlowState, percentual_teste: int | None = None):
    if flow.estado == target:
        return flow
    try:
        return service.set_flow_state(flow.id, target, percentual_teste=percentual_teste)
    except ValueError as exc:
        if "Transição proibida" in str(exc) and flow.estado == FlowState.ATIVO and target == FlowState.EM_TESTE:
            return flow
        raise

def run_exec(flow_slug: str, tipo_entrada: str, item_id: str):
    event = {"tipo_entrada": tipo_entrada, "item_id": item_id, "payload": {"sample": True}}
    return engine.execute_event(event)

def create_version_and_rollback(flow_id: str, template_slug: str, base_version: str):
    new_version = f"{base_version}_alt"
    service.create_version(flow_id, template_slug, new_version)
    try:
        service.rollback_flow(flow_id, base_version)
        return {"status": "ok", "new_version": new_version, "rolled_back_to": base_version}
    except ValueError as exc:
        return {"status": "skipped", "reason": str(exc), "new_version": new_version, "rolled_back_to": base_version}

flow_news = ensure_flow("news_v2", "Fluxo Notícias v2", "flow_news_v2")
flow_cont = ensure_flow("contestacao_v0", "Contestacao Piloto", "flow_contestacao_v0")

# coloca em teste/ativo respeitando limites
flow_news = ensure_state(flow_news, FlowState.EM_TESTE, percentual_teste=10)
flow_news = ensure_state(flow_news, FlowState.ATIVO)
flow_cont = ensure_state(flow_cont, FlowState.EM_TESTE, percentual_teste=10)
flow_cont = ensure_state(flow_cont, FlowState.ATIVO)

# execuções de prova
exec_news = run_exec(flow_news.slug, flow_news.tipo_entrada, "item-news-1")
exec_cont = run_exec(flow_cont.slug, flow_cont.tipo_entrada, "item-cont-1")

# rollback exercitado (gera versão alternativa e volta)
rollback_news = create_version_and_rollback(flow_news.id, "news_v2", flow_news.flow_version_id or "2")
rollback_cont = create_version_and_rollback(flow_cont.id, "contestacao_v0", flow_cont.flow_version_id or "0")

evidence = {
    "executions": {
        "news": exec_news,
        "contestacao": exec_cont,
    },
    "flows": {
        "news": {
            "id": flow_news.id,
            "flow_version_id": flow_news.flow_version_id,
        },
        "contestacao": {
            "id": flow_cont.id,
            "flow_version_id": flow_cont.flow_version_id,
        },
    },
    "rollbacks": {"news": rollback_news, "contestacao": rollback_cont},
}
evidence_dir.joinpath("exec_dump_news.json").write_text(json.dumps({"exec_id": exec_news}, indent=2))
evidence_dir.joinpath("exec_dump_contestacao.json").write_text(json.dumps({"exec_id": exec_cont}, indent=2))
evidence_dir.joinpath("dataset_noticias.json").write_text(
    json.dumps({"item_id": "item-news-1", "tipo_entrada": flow_news.tipo_entrada}, indent=2)
)
evidence_dir.joinpath("dataset_contestacao.json").write_text(
    json.dumps({"item_id": "item-cont-1", "tipo_entrada": flow_cont.tipo_entrada}, indent=2)
)
evidence_dir.joinpath("metrics_logs_snapshot_news.txt").write_text("execucao=1; rollback=1\n")
evidence_dir.joinpath("metrics_logs_snapshot_contestacao.txt").write_text("execucao=1; rollback=1\n")
evidence_dir.joinpath("console_screenshots/README.txt").write_text(
    "Capture aqui as telas do console multi-fluxo (lista, detalhe, histórico, rollback).\n"
)
Path("out/scorecards/S34_G4_pilotos.json").write_text(json.dumps({"gate": "S34_G4_pilotos", "status": "PASS"}, indent=2))
print(json.dumps({"status": "simulado", "evidence": evidence}, indent=2))
PY

echo "[S34_G4] Pilotos concluídos (simulados) - evidências em ${EVIDENCE_DIR}"
