"""
Guardian API Schemas — S37

Pydantic schemas for Guardian API endpoints.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SubmitDecisionRequest(BaseModel):
    """Request to submit a decision for validation."""

    claim_id: str = Field(..., description="ID of the claim being decided")
    claim_summary: Optional[str] = Field(
        None,
        description="Human-readable summary of what the claim states (e.g., 'Lula é culpado', 'Vai chover amanhã')",
    )
    evidence_summary: Optional[List[str]] = Field(
        default=None,
        description="List of evidence summaries supporting the claim (e.g., ['Acórdão TRF4 processo 123', 'Reportagem Folha 2018-01-24'])",
    )
    domain: str = Field(..., description="Policy domain (e.g., 'politics', 'health')")
    gate: str = Field(..., description="Gate identifier (G1, G7, etc.)")
    proposed_state: str = Field(..., description="Proposed state (e.g., 'verified')")
    context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Context for policy evaluation",
    )
    policy_name: Optional[str] = Field(
        None,
        description="Optional specific policy to use",
    )


class DecisionResponse(BaseModel):
    """Response for a decision."""

    id: str
    claim_id: str
    claim_summary: Optional[str] = None  # Human-readable description of what is being decided
    evidence_summary: Optional[List[str]] = None  # Evidence summaries anchoring the claim
    domain: str
    gate: str
    proposed_state: str
    status: str
    policy_name: Optional[str]
    committee_id: Optional[str]
    final_state: Optional[str]
    final_reason: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]


class FlowContextResponse(BaseModel):
    """Response with flow execution context."""

    decision: DecisionResponse
    current_state: str
    transitions: List[Dict[str, Any]]
    elapsed_ms: int
    policy_result: Optional[Dict[str, Any]]
    invariants: Optional[Dict[str, bool]]
    error: Optional[str]


class SubmitReviewRequest(BaseModel):
    """Request to submit a human review."""

    reviewer_id: str = Field(..., description="ID of the reviewer")
    approved: bool = Field(..., description="Whether to approve the decision")
    reason: Optional[str] = Field(None, description="Reason for the decision")


class SubmitVoteRequest(BaseModel):
    """Request to submit a committee vote."""

    member_id: str = Field(..., description="ID of the voting member")
    vote_type: str = Field(..., description="Vote type: approve, reject, abstain")
    reason: Optional[str] = Field(None, description="Reason for the vote")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Vote confidence")


class AddReviewerRequest(BaseModel):
    """Request to add a reviewer to a decision."""

    user_id: str = Field(..., description="ID of the reviewer user")


class AddValidatorRequest(BaseModel):
    """Request to add a validator to a committee."""

    agent_id: str = Field(..., description="ID of the validator agent")


class CommitteeResponse(BaseModel):
    """Response for a committee."""

    id: str
    decision_id: str
    member_count: int
    vote_count: int
    quorum_required: int
    has_quorum: bool
    vote_counts: Dict[str, int]


class DecisionBlockResponse(BaseModel):
    """Response for a decision block."""

    id: str
    decision_id: str
    claim_id: str
    domain: str
    gate: str
    initial_state: str
    final_state: str
    decision_type: str
    policy_name: Optional[str]
    policy_version: Optional[str]
    committee_summary: Optional[Dict[str, Any]]
    invariants_checked: Dict[str, bool]
    evidence_refs: List[str]
    created_at: datetime
    latency_ms: Optional[int]


class ReviewQueueItemResponse(BaseModel):
    """Response for a review queue item."""

    id: str
    decision_id: str
    claim_id: str
    domain: str
    gate: str
    proposed_state: str
    priority: str
    status: str
    reason: Optional[str]
    context_summary: Dict[str, Any]
    assigned_to: Optional[str]
    assigned_at: Optional[datetime]
    created_at: datetime
    expires_at: Optional[datetime]


class ReviewQueueStatsResponse(BaseModel):
    """Response for review queue statistics."""

    total_items: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    by_domain: Dict[str, int]
    total_reviewers: int
    total_submissions: int


class GuardianMetricsResponse(BaseModel):
    """Response for Guardian service metrics."""

    decisions_submitted: int
    decisions_approved: int
    decisions_rejected: int
    decisions_timed_out: int
    avg_latency_ms: float
    pending_decisions: int
    awaiting_review: int
    awaiting_quorum: int


class PolicyListResponse(BaseModel):
    """Response for policy list."""

    name: str
    domain: str
    gate: str
    version: str
    requirements: int
    rules: int


class PolicyRequirementResponse(BaseModel):
    """A REQUIRE condition in a policy."""

    field: str
    operator: str
    value: Any
    modifier: Optional[str] = None


class PolicyRuleResponse(BaseModel):
    """An ON...THEN rule in a policy."""

    condition_field: str
    condition_operator: str
    condition_value: Any
    action: str
    action_params: Dict[str, Any] = {}


class PolicyDetailResponse(BaseModel):
    """Full policy details including requirements and rules."""

    name: str
    domain: str
    gate: str
    version: str
    requirements: List[PolicyRequirementResponse]
    rules: List[PolicyRuleResponse]
    metadata: Dict[str, Any] = {}
