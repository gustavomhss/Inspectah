from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.agents.models import (
    AgentLayer,
    AgentRole,
    AgentStatus,
    AgentRunStatus,
    AgentFlowLayer,
    FlowLayerType,
)


class AgentKBRefSchema(BaseModel):
    id: str
    kind: str
    label: str
    path_or_uri: str


class AgentProfileCreate(BaseModel):
    name: str
    description: str = ""
    instructions: str = ""
    role: AgentRole
    layer: AgentLayer
    model_name: Optional[str] = None
    recommended_model_name: Optional[str] = None
    temperature: float = 0.2
    max_tokens: int = 4000
    top_p: float = 1.0
    status: AgentStatus = AgentStatus.ACTIVE
    kb_refs: List[AgentKBRefSchema] = Field(default_factory=list)
    created_by: Optional[str] = None


class AgentProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructions: Optional[str] = None
    role: Optional[AgentRole] = None
    layer: Optional[AgentLayer] = None
    model_name: Optional[str] = None
    recommended_model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    status: Optional[AgentStatus] = None
    kb_refs: Optional[List[AgentKBRefSchema]] = None
    last_modified_by: Optional[str] = None


class AgentProfileRead(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    name: str
    description: str
    instructions: str
    role: AgentRole
    layer: AgentLayer
    model_name: Optional[str]
    recommended_model_name: Optional[str]
    temperature: float
    max_tokens: int
    top_p: float
    status: AgentStatus
    kb_refs: List[AgentKBRefSchema]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    last_modified_by: Optional[str]


class AgentInstructionVersionCreate(BaseModel):
    changelog: str = "Atualização de instruções"
    instructions: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    kb_snapshot: Optional[List[AgentKBRefSchema]] = None
    created_by: Optional[str] = None


class AgentInstructionVersionRead(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    agent_id: str
    version_number: int
    instructions: Optional[str]
    model_name: Optional[str]
    temperature: Optional[float]
    max_tokens: Optional[int]
    top_p: Optional[float]
    kb_snapshot: List[AgentKBRefSchema]
    changelog: str
    created_at: datetime
    created_by: Optional[str]


class CommitteePolicySchema(BaseModel):
    required_agreement_ratio: float = 0.67
    max_disagreement_tolerance: float = 0.34
    resolve_ties_strategy: str = "favor_cautious"


class AgentCommitteeCreate(BaseModel):
    name: str
    description: str = ""
    layer: AgentLayer
    primary_agents: List[str]
    mediator_agent: str
    policy: CommitteePolicySchema = Field(default_factory=CommitteePolicySchema)
    status: AgentStatus = AgentStatus.ACTIVE


class AgentCommitteeRead(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    name: str
    description: str
    layer: AgentLayer
    primary_agents: List[str]
    mediator_agent: str
    policy: CommitteePolicySchema
    status: AgentStatus
    created_at: datetime
    updated_at: datetime


class ModelUpgradePolicySchema(BaseModel):
    global_default_model: str = "gpt-plus-latest"
    auto_upgrade_enabled: bool = True
    adoption_delay_days: int = 15
    allowed_models: List[str] = Field(default_factory=list)
    last_upgrade_at: Optional[datetime] = None
    next_upgrade_at: Optional[datetime] = None
    updated_at: datetime


class AgentRunRead(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    committee_id: str
    input_ref: Optional[str] = None
    payload_snapshot: dict
    result_bundle_ref: Optional[str] = None
    status: AgentRunStatus
    error: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
    created_at: datetime


class CommitteeRunRequest(BaseModel):
    input_ref: Optional[str] = None
    payload: dict = Field(default_factory=dict)


class ModelCatalogSchema(BaseModel):
    available_models: List[str]
    default_model: Optional[str] = None


class AgentFlowLayerCreate(BaseModel):
    id: Optional[str] = None
    name: str
    description: str = ""
    layer_type: FlowLayerType
    layer_index: int
    agent_ids: List[str]
    mediator_agent_id: str


class AgentFlowLayerRead(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: str
    name: str
    description: str
    layer_type: FlowLayerType
    layer_index: int
    agent_ids: List[str]
    mediator_agent_id: str
    created_at: datetime
    updated_at: datetime
