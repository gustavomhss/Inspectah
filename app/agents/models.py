from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional


class AgentLayer(str, Enum):
    INTERPRETATION = "interpretation"
    CLASSIFICATION = "classification"
    DEBUNK = "debunk"


class AgentRole(str, Enum):
    INTERPRETER = "interpreter"
    CLASSIFIER = "classifier"
    ANALYST = "analyst"
    DEBUNKER = "debunker"
    DECISION_MAKER = "decision_maker"
    MEDIATOR = "mediator"
    LIBRARIAN = "librarian"


class AgentStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DEPRECATED = "deprecated"


class AgentRunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    CANCELLED = "CANCELLED"


class FlowLayerType(str, Enum):
    INTERPRETATION = "interpretation_layer"
    CLASSIFICATION = "classification_layer"
    INTERMEDIATE = "intermediate_layer"
    DECISION_MAKER = "decision_maker_layer"
    LIBRARIAN = "librarian_layer"


@dataclass
class AgentKBRef:
    id: str
    kind: str
    label: str
    path_or_uri: str


@dataclass
class AgentProfile:
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
    kb_refs: List[AgentKBRef] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None
    last_modified_by: Optional[str] = None

    def to_version_snapshot(self, version_number: int, changelog: str, author: str) -> "AgentInstructionVersion":
        return AgentInstructionVersion(
            id=f"agver_{self.id}_{version_number}",
            agent_id=self.id,
            version_number=version_number,
            instructions=self.instructions,
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            kb_snapshot=self.kb_refs.copy(),
            changelog=changelog,
            created_by=author,
        )


@dataclass
class AgentInstructionVersion:
    id: str
    agent_id: str
    version_number: int
    instructions: str
    model_name: Optional[str]
    temperature: float
    max_tokens: int
    top_p: float
    kb_snapshot: List[AgentKBRef]
    changelog: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None


@dataclass
class CommitteePolicy:
    required_agreement_ratio: float = 0.67
    max_disagreement_tolerance: float = 0.34
    resolve_ties_strategy: str = "favor_cautious"


@dataclass
class AgentCommittee:
    id: str
    name: str
    description: str
    layer: AgentLayer
    primary_agents: List[str]
    mediator_agent: str
    policy: CommitteePolicy
    status: AgentStatus = AgentStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ModelUpgradePolicy:
    global_default_model: str = "gpt-plus-latest"
    auto_upgrade_enabled: bool = True
    adoption_delay_days: int = 15
    allowed_models: List[str] = field(default_factory=list)
    last_upgrade_at: Optional[datetime] = None
    next_upgrade_at: Optional[datetime] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def effective_model_for(self, agent: AgentProfile, now: Optional[datetime] = None) -> str:
        if agent.model_name:
            return agent.model_name
        now = now or datetime.now(timezone.utc)
        if not self.auto_upgrade_enabled:
            return agent.recommended_model_name or self.global_default_model
        if self.next_upgrade_at and now < self.next_upgrade_at:
            return agent.recommended_model_name or self.global_default_model
        return self.global_default_model

    def schedule_next_upgrade(self, new_model: str) -> None:
        self.global_default_model = new_model
        self.last_upgrade_at = datetime.now(timezone.utc)
        self.next_upgrade_at = self.last_upgrade_at + timedelta(days=self.adoption_delay_days)
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class AgentFlowLayer:
    id: str
    name: str
    description: str
    layer_type: FlowLayerType
    layer_index: int
    agent_ids: List[str]
    mediator_agent_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentRun:
    id: str
    committee_id: str
    input_ref: Optional[str]
    payload_snapshot: Dict[str, object]
    result_bundle_ref: Optional[str]
    status: AgentRunStatus
    error: Optional[str]
    started_at: datetime
    finished_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, *, id: str, committee_id: str, input_ref: Optional[str], payload_snapshot: Dict[str, object]) -> "AgentRun":
        now = datetime.now(timezone.utc)
        return cls(
            id=id,
            committee_id=committee_id,
            input_ref=input_ref,
            payload_snapshot=payload_snapshot,
            result_bundle_ref=None,
            status=AgentRunStatus.RUNNING,
            error=None,
            started_at=now,
            finished_at=None,
            created_at=now,
        )
