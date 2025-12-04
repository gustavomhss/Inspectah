from __future__ import annotations

import random
from typing import Dict, Optional

from app.flows.models import Flow, FlowState
from app.flows.service import FlowService


class RoutingDecision:
    def __init__(self, flow: Flow, motivo: str):
        self.flow = flow
        self.motivo = motivo


def select_flow_for_event(evento: Dict, service: Optional[FlowService] = None) -> RoutingDecision:
    """
    Seleciona fluxo para o evento de ingestão (tipo_entrada = noticia_texto).
    Regra simples: fluxo ativo recebe 100%; se houver um em_teste com percentual_teste > 0,
    usa aleatoriedade simples para enviar parte do tráfego.
    """
    service = service or FlowService()
    tipo = evento.get("tipo_entrada")
    flows = [f for f in service.list_flows() if f.tipo_entrada == tipo]
    ativos = [f for f in flows if f.estado == FlowState.ATIVO]
    testes = [f for f in flows if f.estado == FlowState.EM_TESTE and f.percentual_teste > 0]
    if ativos:
        ativo = ativos[0]
        if testes:
            test_flow = testes[0]
            if random.randint(1, 100) <= test_flow.percentual_teste:
                return RoutingDecision(test_flow, "fluxo_em_teste_percentual")
        return RoutingDecision(ativo, "fluxo_ativo")
    if testes:
        return RoutingDecision(testes[0], "fallback_em_teste_sem_ativo")
    raise ValueError("Nenhum fluxo ativo para tipo_entrada")
