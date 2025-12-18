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
    # S40: New states for E40.5 enforcement
    BLOCKED = "blocked"  # S40-BE-005: E40.5 check failed, transition blocked
    DEGRADED = "degraded"  # S40-BE-029: Running in degraded mode


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
    # S40: New events for E40.5 enforcement
    E40_5_BLOCKED = "e40_5_blocked"  # S40-BE-005: Critical invariant violated
    NOGO_BLOCKED = "nogo_blocked"  # S40-BE-015: NO-GO signal blocks transition
    ENTER_DEGRADED = "enter_degraded"  # S40-BE-029: Enter degraded mode
    EXIT_DEGRADED = "exit_degraded"  # S40-BE-029: Exit degraded mode
    UNBLOCK = "unblock"  # After blocked issue is resolved


@dataclass
class FlowTransition:
    """A state transition record."""

    from_state: FlowState
    to_state: FlowState
    event: FlowEvent
    timestamp: datetime = field(default_factory=_utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class E40_5CheckResult:
    """Result of E40.5 invariant check (S40-BE-005)."""

    status: str  # PASS, FAIL, SKIP, TIMEOUT, DEGRADED
    invariants_checked: List[str] = field(default_factory=list)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    checked_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def from_invariants(cls, invariants: Dict[str, bool]) -> "E40_5CheckResult":
        """Create from invariants dict."""
        checked = list(invariants.keys())
        failed = [k for k, v in invariants.items() if not v]
        status = "PASS" if not failed else "FAIL"
        violations = [{"invariant": k, "passed": False} for k in failed]
        return cls(
            status=status,
            invariants_checked=checked,
            violations=violations,
        )


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
    # S40: E40.5 enforcement (S40-BE-005)
    e40_5_result: Optional[E40_5CheckResult] = None
    e40_5_required: bool = True  # Default: E40.5 is mandatory
    blocked_reason: Optional[str] = None
    # S40: Degraded mode (S40-BE-029)
    degraded_mode: bool = False
    degraded_reason: Optional[str] = None
    # S40-BE-015: NO-GO signal references
    signal_refs: List[str] = field(default_factory=list)
    nogo_blocked: bool = False

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

    def is_e40_5_passed(self) -> bool:
        """Check if E40.5 passed (S40-BE-005)."""
        if not self.e40_5_required:
            return True
        if self.e40_5_result is None:
            return False
        return self.e40_5_result.status in ("PASS", "SKIP")

    def is_blocked(self) -> bool:
        """Check if flow is blocked due to E40.5 failure."""
        return self.current_state == FlowState.BLOCKED

    def enter_degraded_mode(self, reason: str) -> None:
        """Enter degraded mode (S40-BE-029)."""
        self.degraded_mode = True
        self.degraded_reason = reason

    def exit_degraded_mode(self) -> None:
        """Exit degraded mode (S40-BE-029)."""
        self.degraded_mode = False
        self.degraded_reason = None

    def has_nogo_signals(self) -> bool:
        """Check if there are active NO-GO signals (S40-BE-015)."""
        return self.nogo_blocked or len(self.signal_refs) > 0

    def add_nogo_signal(self, signal_id: str) -> None:
        """Add a NO-GO signal reference (S40-BE-015)."""
        if signal_id not in self.signal_refs:
            self.signal_refs.append(signal_id)

    def clear_nogo_signals(self) -> None:
        """Clear NO-GO signals after resolution (S40-BE-015)."""
        self.signal_refs = []
        self.nogo_blocked = False


# State transition table
TRANSITIONS: Dict[FlowState, Dict[FlowEvent, FlowState]] = {
    FlowState.INIT: {
        FlowEvent.START: FlowState.POLICY_CHECK,
        FlowEvent.ERROR: FlowState.FAILED,
        FlowEvent.ENTER_DEGRADED: FlowState.DEGRADED,  # S40-BE-029
    },
    FlowState.POLICY_CHECK: {
        FlowEvent.POLICY_PASSED: FlowState.INVARIANT_CHECK,
        FlowEvent.POLICY_REQUIRES_REVIEW: FlowState.AWAITING_REVIEW,
        FlowEvent.POLICY_REQUIRES_QUORUM: FlowState.AWAITING_QUORUM,
        FlowEvent.NOGO_BLOCKED: FlowState.BLOCKED,  # S40-BE-015: NO-GO signal blocks
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
        FlowEvent.ENTER_DEGRADED: FlowState.DEGRADED,  # S40-BE-029
    },
    FlowState.INVARIANT_CHECK: {
        FlowEvent.INVARIANTS_PASSED: FlowState.AUTO_APPROVE,
        FlowEvent.INVARIANTS_FAILED: FlowState.AWAITING_REVIEW,
        FlowEvent.E40_5_BLOCKED: FlowState.BLOCKED,  # S40-BE-005: Block on critical failure
        FlowEvent.NOGO_BLOCKED: FlowState.BLOCKED,  # S40-BE-015: NO-GO signal blocks
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.AUTO_APPROVE: {
        FlowEvent.POLICY_PASSED: FlowState.COMPLETED,
        FlowEvent.E40_5_BLOCKED: FlowState.BLOCKED,  # S40-BE-005: Block before completion
        FlowEvent.NOGO_BLOCKED: FlowState.BLOCKED,  # S40-BE-015: NO-GO signal blocks
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.AWAITING_REVIEW: {
        FlowEvent.REVIEW_APPROVED: FlowState.COMPLETED,
        FlowEvent.REVIEW_REJECTED: FlowState.COMPLETED,
        FlowEvent.ESCALATE: FlowState.ESCALATED,
        FlowEvent.E40_5_BLOCKED: FlowState.BLOCKED,  # S40-BE-005
        FlowEvent.NOGO_BLOCKED: FlowState.BLOCKED,  # S40-BE-015: NO-GO signal blocks
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.AWAITING_QUORUM: {
        FlowEvent.QUORUM_APPROVED: FlowState.COMPLETED,
        FlowEvent.QUORUM_REJECTED: FlowState.COMPLETED,
        FlowEvent.QUORUM_TIE: FlowState.ESCALATED,
        FlowEvent.E40_5_BLOCKED: FlowState.BLOCKED,  # S40-BE-005
        FlowEvent.NOGO_BLOCKED: FlowState.BLOCKED,  # S40-BE-015: NO-GO signal blocks
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    FlowState.ESCALATED: {
        FlowEvent.REVIEW_APPROVED: FlowState.COMPLETED,
        FlowEvent.REVIEW_REJECTED: FlowState.COMPLETED,
        FlowEvent.E40_5_BLOCKED: FlowState.BLOCKED,  # S40-BE-005
        FlowEvent.NOGO_BLOCKED: FlowState.BLOCKED,  # S40-BE-015: NO-GO signal blocks
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    # S40-BE-005: Blocked state - only manual unblock or error
    FlowState.BLOCKED: {
        FlowEvent.UNBLOCK: FlowState.AWAITING_REVIEW,  # Resume after unblock
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
    # S40-BE-029: Degraded mode - can continue with limitations
    FlowState.DEGRADED: {
        FlowEvent.START: FlowState.POLICY_CHECK,  # Continue in degraded mode
        FlowEvent.EXIT_DEGRADED: FlowState.INIT,  # Return to normal
        FlowEvent.TIMEOUT: FlowState.TIMED_OUT,
        FlowEvent.ERROR: FlowState.FAILED,
    },
}

# Terminal states
TERMINAL_STATES = {
    FlowState.COMPLETED,
    FlowState.TIMED_OUT,
    FlowState.FAILED,
    FlowState.BLOCKED,  # S40-BE-005: Blocked is terminal until unblocked
}

# Critical invariants that cause BLOCKED state (S40-BE-005)
CRITICAL_INVARIANTS = {
    "evidence_exists",  # INV-E40.5-01: Must have evidence
    "non_contradiction",  # Cannot have strong contradictions
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
        """
        Execute E40.5 invariant check step (S40-BE-005).

        Critical invariants that fail will cause BLOCKED state.
        Non-critical failures go to AWAITING_REVIEW.
        """
        if self._check_timeout(ctx):
            self._transition(ctx, FlowEvent.TIMEOUT)
            return

        invariants = self.policy_engine.check_e40_5_invariants(
            {**claim_context, "gate": ctx.decision.gate}
        )
        ctx.invariants = invariants

        # S40-BE-005: Create structured E40.5 result
        ctx.e40_5_result = E40_5CheckResult.from_invariants(invariants)

        all_pass = all(invariants.values())
        failed = [k for k, v in invariants.items() if not v]

        # S40-BE-005: Check for critical invariant failures
        critical_failures = [f for f in failed if f in CRITICAL_INVARIANTS]

        if all_pass:
            self._transition(
                ctx,
                FlowEvent.INVARIANTS_PASSED,
                {"invariants": invariants, "e40_5_status": "PASS"},
            )
        elif critical_failures:
            # S40-BE-005: Block on critical invariant failure
            ctx.blocked_reason = f"Critical invariant(s) failed: {critical_failures}"
            logger.error(
                f"Decision {ctx.decision.id} BLOCKED - critical invariants: {critical_failures}"
            )
            self._transition(
                ctx,
                FlowEvent.E40_5_BLOCKED,
                {
                    "invariants": invariants,
                    "failed": failed,
                    "critical_failures": critical_failures,
                    "e40_5_status": "BLOCKED",
                },
            )
        else:
            # Non-critical failures go to review
            logger.warning(
                f"Decision {ctx.decision.id} failed non-critical invariants: {failed}"
            )
            self._transition(
                ctx,
                FlowEvent.INVARIANTS_FAILED,
                {"invariants": invariants, "failed": failed, "e40_5_status": "FAIL"},
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

    async def unblock_decision(
        self,
        ctx: FlowContext,
        resolver_id: str,
        reason: str,
    ) -> FlowContext:
        """
        Unblock a blocked decision (S40-BE-005).

        Args:
            ctx: Flow context
            resolver_id: ID of the user/system resolving the block
            reason: Reason for unblocking

        Returns:
            Updated FlowContext
        """
        if ctx.current_state != FlowState.BLOCKED:
            logger.error(f"Cannot unblock decision in state {ctx.current_state}")
            return ctx

        logger.info(
            f"Decision {ctx.decision.id} unblocked by {resolver_id}: {reason}"
        )

        ctx.blocked_reason = None
        self._transition(
            ctx,
            FlowEvent.UNBLOCK,
            {"resolver_id": resolver_id, "reason": reason},
        )

        return ctx

    def enter_degraded_mode(
        self,
        ctx: FlowContext,
        reason: str,
    ) -> FlowContext:
        """
        Enter degraded mode (S40-BE-029).

        In degraded mode, certain checks may be skipped or relaxed
        to maintain availability during system issues.

        Args:
            ctx: Flow context
            reason: Reason for entering degraded mode

        Returns:
            Updated FlowContext
        """
        if ctx.current_state not in (FlowState.INIT, FlowState.POLICY_CHECK):
            logger.error(f"Cannot enter degraded mode in state {ctx.current_state}")
            return ctx

        logger.warning(f"Decision {ctx.decision.id} entering degraded mode: {reason}")

        ctx.enter_degraded_mode(reason)
        ctx.e40_5_required = False  # Relax E40.5 requirement in degraded mode

        self._transition(
            ctx,
            FlowEvent.ENTER_DEGRADED,
            {"reason": reason},
        )

        return ctx

    def exit_degraded_mode(self, ctx: FlowContext) -> FlowContext:
        """
        Exit degraded mode (S40-BE-029).

        Args:
            ctx: Flow context

        Returns:
            Updated FlowContext
        """
        if ctx.current_state != FlowState.DEGRADED:
            logger.error(f"Cannot exit degraded mode in state {ctx.current_state}")
            return ctx

        logger.info(f"Decision {ctx.decision.id} exiting degraded mode")

        ctx.exit_degraded_mode()
        ctx.e40_5_required = True  # Restore E40.5 requirement

        self._transition(ctx, FlowEvent.EXIT_DEGRADED, {})

        return ctx

    def check_nogo_signals(
        self,
        ctx: FlowContext,
        claim_id: str,
        evidence_trail: Optional[List[Dict[str, Any]]] = None,
        source_id: Optional[str] = None,
        retracted_count: int = 0,
    ) -> FlowContext:
        """
        Check for NO-GO signals and block if any are active (S40-BE-015).

        Args:
            ctx: Flow context
            claim_id: ID of the claim to check
            evidence_trail: Evidence items for the claim
            source_id: Source ID (for abuse detection)
            retracted_count: Number of retracted claims from source

        Returns:
            Updated FlowContext (may be BLOCKED if signals detected)
        """
        from app.claims.signals import check_nogo_signals, get_signal_repository

        # Get active signals
        signals = check_nogo_signals(
            claim_id=claim_id,
            evidence_trail=evidence_trail or [],
            source_id=source_id,
            retracted_count=retracted_count,
        )

        if not signals:
            return ctx

        # Add signals to repository and context
        repo = get_signal_repository()
        for signal in signals:
            repo.add(signal)
            ctx.add_nogo_signal(signal.signal_id)

        # Block transition
        ctx.nogo_blocked = True
        signal_types = [s.type.value for s in signals]
        ctx.blocked_reason = f"NO-GO signals detected: {', '.join(signal_types)}"

        logger.warning(
            f"Decision {ctx.decision.id} BLOCKED by NO-GO signals: {signal_types}"
        )

        self._transition(
            ctx,
            FlowEvent.NOGO_BLOCKED,
            {
                "signal_ids": ctx.signal_refs,
                "signal_types": signal_types,
                "nogo_status": "BLOCKED",
            },
        )

        return ctx

    def clear_nogo_block(
        self,
        ctx: FlowContext,
        resolver_id: str,
        reason: str,
    ) -> FlowContext:
        """
        Clear NO-GO block after signals are resolved (S40-BE-015).

        Args:
            ctx: Flow context
            resolver_id: ID of the resolver
            reason: Reason for clearing

        Returns:
            Updated FlowContext
        """
        if not ctx.nogo_blocked and not ctx.signal_refs:
            logger.warning(f"No NO-GO block to clear for decision {ctx.decision.id}")
            return ctx

        from app.claims.signals import get_signal_repository

        # Resolve all signals
        repo = get_signal_repository()
        for signal_id in ctx.signal_refs:
            repo.resolve(signal_id, resolver_id, reason)

        # Clear context
        ctx.clear_nogo_signals()
        ctx.blocked_reason = None

        logger.info(
            f"Decision {ctx.decision.id} NO-GO block cleared by {resolver_id}: {reason}"
        )

        # If still in blocked state, unblock
        if ctx.current_state == FlowState.BLOCKED:
            self._transition(
                ctx,
                FlowEvent.UNBLOCK,
                {"resolver_id": resolver_id, "reason": reason, "nogo_cleared": True},
            )

        return ctx
