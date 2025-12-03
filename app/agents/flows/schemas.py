from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.agents.models import AgentRole


class AgentFlowStepBase(BaseModel):
    position: int = Field(..., ge=1)
    agent_role: AgentRole | str
    params: Dict[str, object] = Field(default_factory=dict)
    required: bool = True
    can_fail_soft: bool = False


class AgentFlowStepIn(AgentFlowStepBase):
    pass


class AgentFlowStepOut(AgentFlowStepBase):
    id: str
    flow_id: str
    created_at: datetime
    updated_at: datetime


class AgentFlowConfigBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    domain_key: str = Field(..., min_length=1)
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    change_reason: Optional[str] = None


class AgentFlowConfigIn(AgentFlowConfigBase):
    steps: List[AgentFlowStepIn]
    created_by: Optional[str] = Field(default=None, alias="actor")
    updated_by: Optional[str] = None


class AgentFlowConfigOut(AgentFlowConfigBase):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    steps: List[AgentFlowStepOut] = Field(default_factory=list)
