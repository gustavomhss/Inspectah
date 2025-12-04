from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.flows.models import (
    FlowExecutionStatus,
    FlowState,
    FlowStepExecutionStatus,
    FlowStepType,
)


class FlowStepRead(BaseModel):
    id: str
    flow_id: str
    ordem: int
    tipo_etapa: FlowStepType
    agent_role: str
    agent_binding: Optional[str] = None
    config: Dict = Field(default_factory=dict)
    flags: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class FlowListItem(BaseModel):
    id: str
    nome: str
    slug: str
    tipo_entrada: str
    estado: FlowState
    template_origem_id: Optional[str] = None
    percentual_teste: int = 0
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class FlowRead(FlowListItem):
    steps: List[FlowStepRead] = Field(default_factory=list)


class FlowCreateFromTemplateRequest(BaseModel):
    template_slug: str
    nome: str
    slug: str
    bindings: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict = Field(default_factory=dict)
    percentual_teste: int = 0


class FlowCreateFromTemplateResponse(FlowRead):
    pass


class FlowUpdateStateRequest(BaseModel):
    novo_estado: FlowState
    percentual_teste: Optional[int] = None


class FlowReplaceAgentRequest(BaseModel):
    step_id: str
    agent_binding: str


class FlowExecutionRead(BaseModel):
    id: str
    flow_id: str
    item_id: str
    tipo_entrada: str
    status: FlowExecutionStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    erro_resumo: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class FlowStepExecutionRead(BaseModel):
    id: str
    flow_execution_id: str
    step_id: str
    status: FlowStepExecutionStatus
    started_at: datetime
    finished_at: Optional[datetime] = None
    output_resumo: Optional[str] = None
    erro_resumo: Optional[str] = None
    raw_ref: Optional[str] = None


class FlowExecutionDetailRead(FlowExecutionRead):
    steps: List[FlowStepExecutionRead] = Field(default_factory=list)


class FlowReprocessCriteria(BaseModel):
    item_ids: List[str] = Field(default_factory=list)
    max_items: Optional[int] = None
    janela_horas: Optional[int] = None


class FlowReprocessRequest(BaseModel):
    criteria: FlowReprocessCriteria
    motivo: Optional[str] = None
