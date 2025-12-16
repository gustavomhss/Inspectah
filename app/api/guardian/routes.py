"""
Guardian API Routes — S37

REST API endpoints for the Guardian validation system.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)

from app.api.guardian.schemas import (
    AddReviewerRequest,
    AddValidatorRequest,
    CommitteeResponse,
    DecisionBlockResponse,
    DecisionResponse,
    FlowContextResponse,
    GuardianMetricsResponse,
    PolicyDetailResponse,
    PolicyListResponse,
    PolicyRequirementResponse,
    PolicyRuleResponse,
    ReviewQueueItemResponse,
    ReviewQueueStatsResponse,
    SubmitDecisionRequest,
    SubmitReviewRequest,
    SubmitVoteRequest,
)
from app.guardian import (
    Decision,
    DecisionStatus,
    FlowContext,
    GuardianService,
    VoteType,
    get_guardian_service,
)
from app.guardian.human_review import (
    ReviewPriority,
    ReviewQueue,
    ReviewStatus,
    get_review_queue,
)
from app.truth.policy_engine import get_policy_engine

router = APIRouter(prefix="/api/guardian", tags=["guardian"])


def get_service() -> GuardianService:
    return get_guardian_service()


def get_queue() -> ReviewQueue:
    return get_review_queue()


def _decision_to_response(decision: Decision) -> DecisionResponse:
    return DecisionResponse(
        id=decision.id,
        claim_id=decision.claim_id,
        claim_summary=decision.claim_summary,
        evidence_summary=decision.evidence_summary,
        domain=decision.domain,
        gate=decision.gate,
        proposed_state=decision.proposed_state,
        status=decision.status.value,
        policy_name=decision.policy_name,
        committee_id=decision.committee_id,
        final_state=decision.final_state,
        final_reason=decision.final_reason,
        created_at=decision.created_at,
        updated_at=decision.updated_at,
        completed_at=decision.completed_at,
    )


def _flow_context_to_response(ctx: FlowContext) -> FlowContextResponse:
    policy_result = None
    if ctx.policy_result:
        policy_result = {
            "policy_name": ctx.policy_result.policy_name,
            "final_action": ctx.policy_result.final_action.value if ctx.policy_result.final_action else None,
            "all_requirements_met": ctx.policy_result.all_requirements_met,
        }

    return FlowContextResponse(
        decision=_decision_to_response(ctx.decision),
        current_state=ctx.current_state.value,
        transitions=[
            {
                "from_state": t.from_state.value,
                "to_state": t.to_state.value,
                "event": t.event.value,
                "timestamp": t.timestamp.isoformat(),
                "metadata": t.metadata,
            }
            for t in ctx.transitions
        ],
        elapsed_ms=ctx.elapsed_ms(),
        policy_result=policy_result,
        invariants=ctx.invariants,
        error=ctx.error,
    )


# Decision endpoints


@router.post("/decisions", response_model=FlowContextResponse)
async def submit_decision(
    request: SubmitDecisionRequest,
    service: GuardianService = Depends(get_service),
):
    """
    Submit a new decision for validation.

    The decision will be processed through the Guardian flow:
    - Policy evaluation
    - E40.5 invariant checks
    - Auto-approve, human review, or committee quorum
    """
    ctx = await service.submit_and_process(
        claim_id=request.claim_id,
        domain=request.domain,
        gate=request.gate,
        proposed_state=request.proposed_state,
        context=request.context,
        policy_name=request.policy_name,
        claim_summary=request.claim_summary,
        evidence_summary=request.evidence_summary,
    )
    return _flow_context_to_response(ctx)


@router.get("/decisions", response_model=List[DecisionResponse])
async def list_decisions(
    status_filter: Optional[str] = None,
    service: GuardianService = Depends(get_service),
):
    """List all decisions, optionally filtered by status."""
    all_decisions = service.list_all_decisions()

    if status_filter:
        all_decisions = [d for d in all_decisions if d.status.value == status_filter]

    return [_decision_to_response(d) for d in all_decisions]


@router.get("/decisions/awaiting-review", response_model=List[DecisionResponse])
async def list_awaiting_review(
    service: GuardianService = Depends(get_service),
):
    """List decisions awaiting human review."""
    return [_decision_to_response(d) for d in service.list_awaiting_review()]


@router.get("/decisions/awaiting-quorum", response_model=List[DecisionResponse])
async def list_awaiting_quorum(
    service: GuardianService = Depends(get_service),
):
    """List decisions awaiting committee quorum."""
    return [_decision_to_response(d) for d in service.list_awaiting_quorum()]


@router.get("/decisions/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: str,
    service: GuardianService = Depends(get_service),
):
    """Get a specific decision by ID."""
    decision = service.get_decision(decision_id)
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision not found: {decision_id}",
        )
    return _decision_to_response(decision)


@router.get("/decisions/{decision_id}/block", response_model=DecisionBlockResponse)
async def get_decision_block(
    decision_id: str,
    service: GuardianService = Depends(get_service),
):
    """Get the decision block for a completed decision."""
    block = service.get_decision_block(decision_id)
    if not block:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision block not found for: {decision_id}",
        )
    return DecisionBlockResponse(
        id=block.id,
        decision_id=block.decision_id,
        claim_id=block.claim_id,
        domain=block.domain,
        gate=block.gate,
        initial_state=block.initial_state,
        final_state=block.final_state,
        decision_type=block.decision_type,
        policy_name=block.policy_name,
        policy_version=block.policy_version,
        committee_summary=block.committee_summary,
        invariants_checked=block.invariants_checked,
        evidence_refs=block.evidence_refs,
        created_at=block.created_at,
        latency_ms=block.latency_ms,
    )


# Review endpoints


@router.post("/decisions/{decision_id}/reviewer")
async def add_reviewer(
    decision_id: str,
    request: AddReviewerRequest,
    service: GuardianService = Depends(get_service),
):
    """Add a human reviewer to a decision awaiting review."""
    try:
        member = await service.add_reviewer(decision_id, request.user_id)
        return {"member_id": member.id, "user_id": member.user_id}
    except ValueError as e:
        logger.warning("add_reviewer error for decision %s: %s", decision_id, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": "Cannot add reviewer to decision"},
        )


@router.post("/decisions/{decision_id}/review", response_model=FlowContextResponse)
async def submit_review(
    decision_id: str,
    request: SubmitReviewRequest,
    service: GuardianService = Depends(get_service),
):
    """Submit a human review decision."""
    try:
        ctx = await service.submit_review(
            decision_id=decision_id,
            reviewer_id=request.reviewer_id,
            approved=request.approved,
            reason=request.reason,
        )
        return _flow_context_to_response(ctx)
    except ValueError as e:
        logger.warning("submit_review error for decision %s: %s", decision_id, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": "Cannot submit review"},
        )


# Committee/Vote endpoints


@router.post("/decisions/{decision_id}/validator")
async def add_validator(
    decision_id: str,
    request: AddValidatorRequest,
    service: GuardianService = Depends(get_service),
):
    """Add a validator to a committee decision."""
    try:
        member = await service.add_validator(decision_id, request.agent_id)
        return {"member_id": member.id, "agent_id": member.agent_id}
    except ValueError as e:
        logger.warning("add_validator error for decision %s: %s", decision_id, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": "Cannot add validator to decision"},
        )


@router.post("/decisions/{decision_id}/vote", response_model=FlowContextResponse)
async def submit_vote(
    decision_id: str,
    request: SubmitVoteRequest,
    service: GuardianService = Depends(get_service),
):
    """Submit a committee vote."""
    try:
        vote_type = VoteType(request.vote_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid vote type: {request.vote_type}",
        )

    try:
        ctx = await service.submit_vote(
            decision_id=decision_id,
            member_id=request.member_id,
            vote_type=vote_type,
            reason=request.reason,
            confidence=request.confidence,
        )
        return _flow_context_to_response(ctx)
    except ValueError as e:
        logger.warning("submit_vote error for decision %s: %s", decision_id, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "validation_error", "message": "Cannot submit vote"},
        )


@router.get("/decisions/{decision_id}/committee", response_model=CommitteeResponse)
async def get_committee(
    decision_id: str,
    service: GuardianService = Depends(get_service),
):
    """Get the committee for a decision."""
    decision = service.get_decision(decision_id)
    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision not found: {decision_id}",
        )

    if not decision.committee_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No committee for decision: {decision_id}",
        )

    committee = service.get_committee(decision.committee_id)
    if not committee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Committee not found: {decision.committee_id}",
        )

    return CommitteeResponse(
        id=committee.id,
        decision_id=committee.decision_id,
        member_count=len(committee.members),
        vote_count=len(committee.votes),
        quorum_required=committee.quorum_required,
        has_quorum=committee.has_quorum(),
        vote_counts={k.value: v for k, v in committee.count_votes().items()},
    )


# Review Queue endpoints


@router.get("/review-queue", response_model=List[ReviewQueueItemResponse])
async def list_review_queue(
    status_filter: Optional[str] = None,
    domain: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    queue: ReviewQueue = Depends(get_queue),
):
    """List items in the review queue."""
    status_enum = ReviewStatus(status_filter) if status_filter else None
    priority_enum = ReviewPriority(priority) if priority else None

    items = queue.get_queue(
        status=status_enum,
        domain=domain,
        priority=priority_enum,
        assigned_to=assigned_to,
    )

    return [
        ReviewQueueItemResponse(
            id=item.id,
            decision_id=item.decision_id,
            claim_id=item.claim_id,
            domain=item.domain,
            gate=item.gate,
            proposed_state=item.proposed_state,
            priority=item.priority.value,
            status=item.status.value,
            reason=item.reason,
            context_summary=item.context_summary,
            assigned_to=item.assigned_to,
            assigned_at=item.assigned_at,
            created_at=item.created_at,
            expires_at=item.expires_at,
        )
        for item in items
    ]


@router.get("/review-queue/stats", response_model=ReviewQueueStatsResponse)
async def get_review_queue_stats(
    queue: ReviewQueue = Depends(get_queue),
):
    """Get review queue statistics."""
    stats = queue.get_stats()
    return ReviewQueueStatsResponse(**stats)


# Metrics and Policies endpoints


@router.get("/metrics", response_model=GuardianMetricsResponse)
async def get_metrics(
    service: GuardianService = Depends(get_service),
):
    """Get Guardian service metrics."""
    metrics = service.get_metrics()
    return GuardianMetricsResponse(**metrics)


@router.get("/policies", response_model=List[PolicyListResponse])
async def list_policies():
    """List all available policies."""
    engine = get_policy_engine()
    policies = engine.list_policies()
    return [PolicyListResponse(**p) for p in policies]


@router.get("/policies/{policy_name}", response_model=PolicyDetailResponse)
async def get_policy_details(policy_name: str):
    """Get full details of a specific policy including requirements and rules."""
    engine = get_policy_engine()
    policy = engine.get_policy_by_name(policy_name)
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy not found: {policy_name}",
        )

    policy_dict = policy.to_dict()
    return PolicyDetailResponse(
        name=policy_dict["name"],
        domain=policy_dict["domain"],
        gate=policy_dict["gate"],
        version=policy_dict["version"],
        requirements=[
            PolicyRequirementResponse(**r) for r in policy_dict["requirements"]
        ],
        rules=[PolicyRuleResponse(**r) for r in policy_dict["rules"]],
        metadata=policy_dict.get("metadata", {}),
    )


@router.post("/check-timeouts")
async def check_timeouts(
    service: GuardianService = Depends(get_service),
):
    """Check for and process timed out decisions."""
    timed_out = await service.check_timeouts()
    return {
        "timed_out_count": len(timed_out),
        "decision_ids": [d.id for d in timed_out],
    }
