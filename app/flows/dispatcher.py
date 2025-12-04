from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Dict

from app.flows.execution_engine import FlowExecutionEngine
from app.flows.service import FlowService, FlowState


def _ensure_flow_active(service: FlowService) -> None:
    flows = service.list_flows()
    active = [f for f in flows if f.tipo_entrada == "noticia_texto" and f.estado == FlowState.ATIVO]
    if active:
        return
    flow = service.create_flow_from_template("fluxo_noticias_geral_v1", "Fluxo Noticias E2E", "fluxo_noticias_e2e", {})
    service.set_flow_state(flow.id, FlowState.EM_TESTE, percentual_teste=0)
    service.set_flow_state(flow.id, FlowState.ATIVO)


def _load_events(path: Path) -> List[Dict]:
    events: List[Dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(json.loads(line))
    return events


def dispatch_events(events: Iterable[Dict]) -> List[str]:
    service = FlowService()
    _ensure_flow_active(service)
    engine = FlowExecutionEngine(service=service)
    exec_ids: List[str] = []
    for evt in events:
        exec_id = engine.execute_event(evt)
        exec_ids.append(exec_id)
    return exec_ids


def dispatch_file(path: str) -> List[str]:
    file_path = Path(path)
    events = _load_events(file_path)
    return dispatch_events(events)
