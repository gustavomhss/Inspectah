from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from app.agents.models import AgentRole


@dataclass
class AgentFlowStep:
    id: Optional[str]
    flow_id: Optional[str]
    position: int
    agent_role: AgentRole | str
    params: Dict[str, object] = field(default_factory=dict)
    required: bool = True
    can_fail_soft: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentFlowConfig:
    id: Optional[str]
    domain_key: str
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    change_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    steps: List[AgentFlowStep] = field(default_factory=list)
