"""Guardian Module — S37.

Validation system for claim decisions.
"""

from app.guardian.flow import (
    FlowContext,
    FlowEvent,
    FlowState,
    FlowTransition,
    GuardianFlow,
    TERMINAL_STATES,
    TRANSITIONS,
)
from app.guardian.models import (
    Committee,
    CommitteeMember,
    Decision,
    DecisionBlock,
    DecisionStatus,
    Vote,
    VoteType,
)
from app.guardian.roles import (
    GuardianRole,
    RoleCapability,
    ROLE_CAPABILITIES,
    can_role_perform,
    get_min_validators,
    get_required_roles,
    get_role_capabilities,
)
from app.guardian.service import (
    GuardianService,
    get_guardian_service,
)
from app.guardian.human_review import (
    ReviewItem,
    ReviewPriority,
    ReviewQueue,
    ReviewStatus,
    ReviewSubmission,
    ReviewerInfo,
    get_review_queue,
)
from app.guardian.committee import (
    CommitteeConfig,
    CommitteeManager,
    CommitteeSelector,
    MemberPool,
    RiskLevel,
    create_manager,
    create_selector,
)
from app.guardian.schemas import (
    CommitteeDetails,
    OrchestrateRequest,
    OrchestrateResponse,
    ThresholdConfigSchema,
    VoteResponse,
)

__all__ = [
    # Roles
    "GuardianRole",
    "RoleCapability",
    "ROLE_CAPABILITIES",
    "can_role_perform",
    "get_min_validators",
    "get_required_roles",
    "get_role_capabilities",
    # Models
    "CommitteeMember",
    "Vote",
    "VoteType",
    "Committee",
    "Decision",
    "DecisionStatus",
    "DecisionBlock",
    # Flow
    "FlowState",
    "FlowEvent",
    "FlowTransition",
    "FlowContext",
    "GuardianFlow",
    "TRANSITIONS",
    "TERMINAL_STATES",
    # Service
    "GuardianService",
    "get_guardian_service",
    # Human Review
    "ReviewItem",
    "ReviewPriority",
    "ReviewQueue",
    "ReviewStatus",
    "ReviewSubmission",
    "ReviewerInfo",
    "get_review_queue",
    # Committee
    "CommitteeConfig",
    "CommitteeManager",
    "CommitteeSelector",
    "MemberPool",
    "RiskLevel",
    "create_manager",
    "create_selector",
    # Schemas
    "CommitteeDetails",
    "OrchestrateRequest",
    "OrchestrateResponse",
    "ThresholdConfigSchema",
    "VoteResponse",
]
