from __future__ import annotations

from typing import Dict, Optional

from app.flows.service import FlowService
from app.flows.models import Flow


def start_rollout(
    service: FlowService,
    flow_id: str,
    mode: str,
    test_percentual: int,
    criteria: Optional[Dict] = None,
    actor: Optional[str] = None,
) -> Flow:
    """Wrapper de conveniência para iniciar rollout governado."""
    return service.start_rollout(flow_id, mode=mode, test_percentual=test_percentual, criteria=criteria or {}, actor=actor)


def promote_rollout(service: FlowService, flow_id: str, actor: Optional[str] = None) -> Flow:
    """Promove rollout ativo/teste para ativo governado."""
    return service.promote_rollout(flow_id, actor=actor)


def rollback_rollout(service: FlowService, flow_id: str, target_version_id: Optional[str] = None, actor: Optional[str] = None) -> Flow:
    """Rollback governado com auditoria e limites."""
    return service.rollback_rollout(flow_id, target_version_id=target_version_id, actor=actor)
