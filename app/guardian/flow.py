"""
Guardian Flow — S37

State machine for the Guardian validation flow.
Flow: submission → policy → E40.5 → quorum → DecisionBlock
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from app.guardian.models import (
    Committee,
    CommitteeMember,
    Decision,
    DecisionBlock,
    DecisionStatus,
    Vote,
    VoteType,
)
from app.guardian.roles import GuardianRole
from app.truth.policy_dsl import PolicyAction, PolicyExecutionResult
from app.truth.policy_engine import PolicyEngine

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class FlowState(str, Enum):
    """States in the Guardian validation flow."""

    INIT = "init"
    POLICY_CHECK = "policy_check"
    INVARIANT_CHECK = "invariant_check"
    AUTO_APPROVE = "auto_approve"
    AWAITING_REVIEW = "awaiting_review"
    AWAITING_QUORUM = "awaiting_quorum"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    FAILED = "failed"


class FlowEvent(str, Enum):
    """Events that trigger state transitions."""

    START = "start"
    POLICY_PASSED = "policy_passed"
    POLICY_REQUIRES_REVIEW = "policy_requires_review"
    POLICY_REQUIRES_QUORUM = "policy_requires_quorum"
    INVARIANTS_PASSED = "invariants_passed"
    INVARIANTS_FAILED = "invariants_failed"
    REVIEW_APPROVED = "review_approved"
    REVIEW_REJECTED = "review_rejected"
    QUORUM_REACHED = "quorum_reached"
    QUORUM_APPROVED = "quorum_approved"
    QUORUM_REJECTED = "quorum_rejected"
    QUORUM_TIE = "quorum_tie"
    TIMEOUT = "timeout"
    ESCALATE = "escalate"
    ERROR = "error"


@dataclass
class FlowTransition:
    """A state transition record."""

    from_state: FlowState
    to_state: FlowState
    event: FlowEvent
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowContext:
    """Context for a Guardian flow execution."""

    decision: Decision
    committee: Optional[Committee] = None
    policy_result: Optional[PolicyExecutionResult] = None
    invariants: Optional[Dict[str, bool]] = None
    current_state: FlowState = FlowState.INIT
    transitions: List[FlowTransition] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    error: Optional[str] = None

    def elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        return int((time.time() - self.start_time) * 1000)

    def add_transition(
        self,
        to_state: FlowState,
        event: FlowEvent,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a state transition."""
        transition = FlowTransition(
            from_state=self.current_state,
            to_state=to_state,
            event=event,
            metadata=metadata or {},
        )
        self.transitions.append(transition)
        self.current_state = to_state


# State transition table
TRANSITIONS: Dict[FlowState, Dict[FlowEvent, FlowState]] = {
    FlowState.INIT: {
        FlowEvent.START: FlowState.POLICY_CHECK,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.POLICY_CHECK: {
        FlowEvent.POLICY_PASSED: FlowState.INVARIANT_CHECK,
        FlowEvent.POLICY_REQUIRES_REVIEW: FlowState.AWAITING_REVIEW,
        FlowEvent.POLICY_REQUIRES_QUORUM: FlowState.AWAITING_QUORUM,
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.INVARIANT_CHECK: {
        FlowEvent.INVARIANTS_PASSED: FlowState.AUTO_APPROVE,
        FlowEvent.INVARIANTS_FAILED: FlowState.AWAITING_REVIEW,
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.AUTO_APPROVE: {
        FlowEvent.POLICY_PASSED: FlowState.COMPLETED,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.AWAITING_REVIEW: {
        FlowEvent.REVIEW_APPROVED: FlowState.COMPLETED,
        FlowEvent.REVIEW_REJECTED: FlowState.COMPLETED,
        FlowEvent.ESCALATE: FlowState.ESCALATED,
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.AWAITING_QUORUM: {
        FlowEvent.QUORUM_APPROVED: FlowState.COMPLETED,
        FlowEvent.QUORUM_REJECTED: FlowState.COMPLETED,
        FlowEvent.QUORUM_TIE: FlowState.ESCALATED,
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.ESCALATED: {
        FlowEvent.REVIEW_APPROVED: FlowState.COMPLETED,
        FlowEvent.REVIEW_REJECTED: FlowState.COMPLETED,
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
}

# Terminal states
TERMINAL_STATES = {
    FlowState.COMPLETED,
    FlowState.TIMED_OUT,
    FlowState.FAILED,
}


def can_transition(current: FlowState, event: FlowEvent) -> bool:
    """Check if a transition is valid."""
    return event in TRANSITIONS.get(current, {})


def get_next_state(current: FlowState, event: FlowEvent) -> Optional[FlowState]:
    """Get the next state for a transition."""
    return TRANSITIONS.get(current, {}).get(event)


class GuardianFlow:
    """
    Guardian validation flow executor.

    Implements the state machine for claim validation decisions.
    SLA: Decision latency ≤20s (P95)
    """

    DEFAULT_TIMEOUT_SECONDS = 20

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.policy_engine = policy_engine or PolicyEngine()
        self.timeout_seconds = timeout_seconds
        self._on_state_change: Optional[Callable[[FlowContext], None]] = None

    def set_state_change_callback(
        self, callback: Callable[[FlowContext], None]
    ) -> None:
        """Set callback for state changes."""
        self._on_state_change = callback

    def _notify_state_change(self, ctx: FlowContext) -> None:
        """Notify state change callback."""
        if self._on_state_change:
            try:
                self._on_state_change(ctx)
            except Exception as e:
                logger.warning(f"State change callback error: {e}")

    def _check_timeout(self, ctx: FlowContext) -> bool:
        """Check if flow has exceeded timeout."""
        elapsed = ctx.elapsed_ms()
        timeout_ms = self.timeout_seconds * 1000
        if elapsed > timeout_ms:
            logger.warning(
                f"Decision {ctx.decision.id} timed out after {elapsed}ms"
            )
            return True
        return False

    def _transition(
        self,
        ctx: FlowContext,
        event: FlowEvent,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Execute a state transition."""
        if not can_transition(ctx.current_state, event):
            logger.error(
                f"Invalid transition: {ctx.current_state} + {event}"
            )
            return False

        next_state = get_next_state(ctx.current_state, event)
        if next_state is None:
            return False

        ctx.add_transition(next_state, event, metadata)
        self._notify_state_change(ctx)

        logger.debug(
            f"Decision {ctx.decision.id}: "
            f"{ctx.transitions[-1].from_state.value} → {next_state.value} "
            f"({event.value})"
        )
        return True

    async def execute(
        self,
        decision: Decision,
        claim_context: Dict[str, Any],
    ) -> FlowContext:
        """
        Execute the validation flow for a decision.

        Args:
            decision: The decision to process
            claim_context: Context dict with claim data for policy evaluation

        Returns:
            FlowContext with final state and results
        """
        ctx = FlowContext(decision=decision)

        try:
            # Start flow
            self._transition(ctx, FlowEvent.START)

            # Step 1: Policy check
            await self._execute_policy_check(ctx, claim_context)
            if ctx.current_state in TERMINAL_STATES:
                return ctx

            # Step 2: Invariant check (if policy passed)
            if ctx.current_state == FlowState.INVARIANT_CHECK:
                await self._execute_invariant_check(ctx, claim_context)
                if ctx.current_state in TERMINAL_STATES:
                    return ctx

            # Step 3: Auto-approve if applicable
            if ctx.current_state == FlowState.AUTO_APPROVE:
                await self._execute_auto_approve(ctx)
                return ctx

            # For review/quorum states, we return context for async handling
            return ctx

        except Exception as e:
            logger.exception(f"Flow execution error: {e}")
            ctx.error = str(e)
            self._transition(ctx, FlowEvent.ERROR, {"error": str(e)})
            return ctx

    async def _execute_policy_check(
        self,
        ctx: FlowContext,
        claim_context: Dict[str, Any],
    ) -> None:
        """Execute policy check step."""
        if self._check_timeout(ctx):
            self._transition(ctx, FlowEvent.TIMEOUT)
            return

        decision = ctx.decision

        try:
            result = self.policy_engine.execute(
                domain=decision.domain,
                gate=decision.gate,
                context=claim_context,
                policy_name=decision.policy_name,
            )
            ctx.policy_result = result

            # Determine next step based on policy action
            action = result.final_action
            if action == PolicyAction.AUTO_APPROVE:
                self._transition(
                    ctx,
                    FlowEvent.POLICY_PASSED,
                    {"action": action.value},
                )
            elif action == PolicyAction.HUMAN_REVIEW:
                self._transition(
                    ctx,
                    FlowEvent.POLICY_REQUIRES_REVIEW,
                    {"action": action.value},
                )
            elif action == PolicyAction.COMMITTEE_QUORUM:
                quorum = result.final_action_params.get("quorum", 3)
                self._transition(
                    ctx,
                    FlowEvent.POLICY_REQUIRES_QUORUM,
                    {"action": action.value, "quorum": quorum},
                )
                # Create committee
                ctx.committee = Committee.create(
                    decision_id=decision.id,
                    quorum_required=quorum,
                )
            else:
                # Default to human review for unknown actions
                self._transition(
                    ctx,
                    FlowEvent.POLICY_REQUIRES_REVIEW,
                    {"action": action.value if action else "unknown"},
                )

        except ValueError as e:
            # No policy found - default to human review
            logger.warning(f"No policy found for {decision.domain}:{decision.gate}")
            self._transition(
                ctx,
                FlowEvent.POLICY_REQUIRES_REVIEW,
                {"reason": "no_policy", "error": str(e)},
            )

    async def _execute_invariant_check(
        self,
        ctx: FlowContext,
        claim_context: Dict[str, Any],
    ) -> None:
        """Execute E40.5 invariant check step."""
        if self._check_timeout(ctx):
            self._transition(ctx, FlowEvent.TIMEOUT)
            return

        invariants = self.policy_engine.check_e40_5_invariants(
            {**claim_context, "gate": ctx.decision.gate}
        )
        ctx.invariants = invariants

        all_pass = all(invariants.values())
        failed = [k for k, v in invariants.items() if not v]

        if all_pass:
            self._transition(
                ctx,
                FlowEvent.INVARIANTS_PASSED,
                {"invariants": invariants},
            )
        else:
            logger.warning(
                f"Decision {ctx.decision.id} failed invariants: {failed}"
            )
            self._transition(
                ctx,
                FlowEvent.INVARIANTS_FAILED,
                {"invariants": invariants, "failed": failed},
            )

    async def _execute_auto_approve(self, ctx: FlowContext) -> None:
        """Execute auto-approve step."""
        decision = ctx.decision
        decision.complete(
            status=DecisionStatus.APPROVED,
            final_state="verified",
            reason="auto_approved_by_policy",
        )
        self._transition(
            ctx,
            FlowEvent.POLICY_PASSED,
            {"final_state": "verified"},
        )

    async def process_review_decision(
        self,
        ctx: FlowContext,
        approved: bool,
        reviewer_id: str,
        reason: Optional[str] = None,
    ) -> FlowContext:
        """
        Process a human review decision.

        Args:
            ctx: Flow context
            approved: Whether the review approved the decision
            reviewer_id: ID of the reviewer
            reason: Optional reason for the decision

        Returns:
            Updated FlowContext
        """
        if ctx.current_state not in (FlowState.AWAITING_REVIEW, FlowState.ESCALATED):
            logger.error(f"Cannot process review in state {ctx.current_state}")
            return ctx

        if self._check_timeout(ctx):
            self._transition(ctx, FlowEvent.TIMEOUT)
            return ctx

        decision = ctx.decision
        if approved:
            decision.complete(
                status=DecisionStatus.APPROVED,
                final_state=decision.proposed_state,
                reason=reason or "approved_by_reviewer",
            )
            self._transition(
                ctx,
                FlowEvent.REVIEW_APPROVED,
                {"reviewer_id": reviewer_id, "reason": reason},
            )
        else:
            decision.complete(
                status=DecisionStatus.REJECTED,
                final_state="rejected",
                reason=reason or "rejected_by_reviewer",
            )
            self._transition(
                ctx,
                FlowEvent.REVIEW_REJECTED,
                {"reviewer_id": reviewer_id, "reason": reason},
            )

        return ctx

    async def process_vote(
        self,
        ctx: FlowContext,
        vote: Vote,
    ) -> FlowContext:
        """
        Process a committee vote.

        Args:
            ctx: Flow context
            vote: The vote to process

        Returns:
            Updated FlowContext
        """
        if ctx.current_state != FlowState.AWAITING_QUORUM:
            logger.error(f"Cannot process vote in state {ctx.current_state}")
            return ctx

        if self._check_timeout(ctx):
            self._transition(ctx, FlowEvent.TIMEOUT)
            return ctx

        if ctx.committee is None:
            logger.error("No committee for quorum decision")
            return ctx

        ctx.committee.add_vote(vote)

        # Check if quorum reached
        if ctx.committee.has_quorum():
            committee_decision = ctx.committee.get_decision()
            decision = ctx.decision

            if committee_decision == VoteType.APPROVE:
                decision.complete(
                    status=DecisionStatus.APPROVED,
                    final_state=decision.proposed_state,
                    reason="approved_by_committee",
                )
                self._transition(
                    ctx,
                    FlowEvent.QUORUM_APPROVED,
                    {"vote_counts": ctx.committee.count_votes()},
                )
            elif committee_decision == VoteType.REJECT:
                decision.complete(
                    status=DecisionStatus.REJECTED,
                    final_state="rejected",
                    reason="rejected_by_committee",
                )
                self._transition(
                    ctx,
                    FlowEvent.QUORUM_REJECTED,
                    {"vote_counts": ctx.committee.count_votes()},
                )
            else:
                # Tie - escalate
                decision.status = DecisionStatus.ESCALATED
                self._transition(
                    ctx,
                    FlowEvent.QUORUM_TIE,
                    {"vote_counts": ctx.committee.count_votes()},
                )

        return ctx

    def create_decision_block(self, ctx: FlowContext) -> Optional[DecisionBlock]:
        """
        Create a DecisionBlock from a completed flow.

        Args:
            ctx: Flow context

        Returns:
            DecisionBlock or None if flow not completed
        """
        if ctx.current_state not in TERMINAL_STATES:
            return None

        invariants = ctx.invariants or {}
        policy_version = None
        if ctx.policy_result:
            policy_version = ctx.policy_result.policy_version

        return DecisionBlock.create(
            decision=ctx.decision,
            committee=ctx.committee,
            policy_version=policy_version,
            invariants={k: v for k, v in invariants.items()},
            evidence_refs=ctx.decision.context.get("evidence_refs", []),
            latency_ms=ctx.elapsed_ms(),
        )
