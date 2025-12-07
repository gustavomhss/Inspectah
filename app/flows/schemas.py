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
    domain: str = "generic"
    flow_version_id: Optional[str] = None
    active_version_id: Optional[str] = None
    test_version_id: Optional[str] = None
    rollout_mode: Optional[str] = None
    rollout_state: Optional[str] = None
    catalog_hash: Optional[str] = None
    catalog_signature: Optional[str] = None
    rollout_started_at: Optional[datetime] = None
    rollout_criteria: Dict = Field(default_factory=dict)
    flow_ops_profile_id: Optional[str] = None
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
    flow_version_id: Optional[str] = None
    mode: Optional[str] = None
    operation_id: Optional[str] = None
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


class FlowTemplateRead(BaseModel):
    id: str
    slug: str
    versao: str
    tipo_entrada: str
    ativo: bool
    estrutura: Dict = Field(default_factory=dict)
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class FlowTemplateWrite(BaseModel):
    slug: str
    version: str
    domain: str
    entry_type: str
    description: Optional[str] = None
    limits: Optional[Dict] = None
    policies: Optional[List[Dict]] = None
    steps: List[Dict]
    metadata: Dict = Field(default_factory=dict)
    id: Optional[str] = None


class FlowVersionRead(BaseModel):
    id: str
    flow_id: str
    version_id: str
    template_slug: str
    estado: str
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class FlowOperationRead(BaseModel):
    id: str
    flow_id: str
    flow_version_id: Optional[str] = None
    operacao: str
    payload: Dict = Field(default_factory=dict)
    resultado: str
    mode: Optional[str] = None
    actor: Optional[str] = None
    catalog_hash: Optional[str] = None
    operation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FlowReprocessCriteria(BaseModel):
    item_ids: List[str] = Field(default_factory=list)
    max_items: Optional[int] = None
    janela_horas: Optional[int] = None


class FlowReprocessRequest(BaseModel):
    criteria: FlowReprocessCriteria
    motivo: Optional[str] = None


class FlowRolloutRequest(BaseModel):
    flow_version_id: Optional[str] = None
    mode: str
    test_percentual: int
    criteria: Dict = Field(default_factory=dict)
    actor: str
    operation_id: str
    catalog_hash: str


class FlowRolloutStatus(BaseModel):
    flow_id: str
    flow_version_id: Optional[str] = None
    active_version_id: Optional[str] = None
    test_version_id: Optional[str] = None
    rollout_mode: Optional[str] = None
    rollout_state: Optional[str] = None
    operation_id: Optional[str] = None
    catalog_hash: Optional[str] = None
    catalog_signature: Optional[str] = None
    rollout_started_at: Optional[datetime] = None
    rollout_criteria: Dict = Field(default_factory=dict)
    alerts: List[str] = Field(default_factory=list)
    policy_violations: List[str] = Field(default_factory=list)
    slo_status: List[Dict] = Field(default_factory=list)


class FlowCatalogEntry(BaseModel):
    flow_id: str
    domain: Optional[str] = None
    version: Optional[str] = None
    flow_version_id: Optional[str] = None
    template_ref: Optional[str] = None
    policies: Dict = Field(default_factory=dict)
    rollout_defaults: Dict = Field(default_factory=dict)
    hash: Optional[str] = None
    signature: Optional[str] = None
