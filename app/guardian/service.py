"""
Guardian Service — S37

Main service for the Guardian validation system.
Orchestrates decision flows, committee management, and audit logging.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.guardian.flow import (
    FlowContext,
    FlowState,
    GuardianFlow,
    TERMINAL_STATES,
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
from app.guardian.roles import GuardianRole, get_min_validators
from app.truth.policy_engine import PolicyEngine, get_policy_engine

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class GuardianService:
    """
    Main Guardian service for claim validation.

    Responsibilities:
    - Submit decisions for validation
    - Manage validation committees
    - Track decision lifecycle
    - Generate audit blocks

    SLA: Decision latency ≤20s (P95)
    """

    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        timeout_seconds: int = 20,
    ):
        self.policy_engine = policy_engine or get_policy_engine()
        self.timeout_seconds = timeout_seconds
        self.flow = GuardianFlow(
            policy_engine=self.policy_engine,
            timeout_seconds=timeout_seconds,
        )

        # In-memory stores (replace with repository in production)
        self._decisions: Dict[str, Decision] = {}
        self._committees: Dict[str, Committee] = {}
        self._blocks: Dict[str, DecisionBlock] = {}
        self._flow_contexts: Dict[str, FlowContext] = {}

        # Metrics
        self._metrics = {
            "decisions_submitted": 0,
            "decisions_approved": 0,
            "decisions_rejected": 0,
            "decisions_timed_out": 0,
            "avg_latency_ms": 0.0,
        }

    async def submit_decision(
        self,
        claim_id: str,
        domain: str,
        gate: str,
        proposed_state: str,
        context: Dict[str, Any],
        policy_name: Optional[str] = None,
        claim_summary: Optional[str] = None,
        evidence_summary: Optional[List[str]] = None,
        proponent_agent_id: Optional[str] = None,
    ) -> Decision:
        """
        Submit a new decision for validation.

        Args:
            claim_id: ID of the claim being decided
            domain: Policy domain (e.g., "politics", "health")
            gate: Gate identifier (G1, G7, etc.)
            proposed_state: The state being proposed (e.g., "verified")
            context: Context dict with claim data for policy evaluation
            policy_name: Optional specific policy to use
            claim_summary: Human-readable summary of what the claim states
            evidence_summary: List of evidence summaries supporting the claim
            proponent_agent_id: ID of the agent proposing the decision

        Returns:
            The created Decision
        """
        decision = Decision.create(
            claim_id=claim_id,
            domain=domain,
            gate=gate,
            proposed_state=proposed_state,
            context=context,
            policy_name=policy_name,
            claim_summary=claim_summary,
            evidence_summary=evidence_summary,
            timeout_seconds=self.timeout_seconds,
        )

        # Store decision
        self._decisions[decision.id] = decision
        self._metrics["decisions_submitted"] += 1

        logger.info(
            f"Decision submitted: {decision.id} "
            f"(claim={claim_id}, domain={domain}, gate={gate})"
        )

        return decision

    async def process_decision(
        self,
        decision_id: str,
    ) -> FlowContext:
        """
        Process a submitted decision through the validation flow.

        Args:
            decision_id: ID of the decision to process

        Returns:
            FlowContext with processing results
        """
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        if decision.is_terminal():
            raise ValueError(f"Decision already completed: {decision_id}")

        # Update status
        decision.status = DecisionStatus.VALIDATING
        decision.updated_at = _utcnow()

        # Execute flow
        ctx = await self.flow.execute(decision, decision.context)

        # Store context for async operations
        self._flow_contexts[decision_id] = ctx

        # Store committee if created
        if ctx.committee:
            self._committees[ctx.committee.id] = ctx.committee
            decision.committee_id = ctx.committee.id

        # Update decision status based on flow state
        self._update_decision_from_flow(decision, ctx)

        # If terminal, create block
        if ctx.current_state in TERMINAL_STATES:
            await self._finalize_decision(decision, ctx)

        return ctx

    async def submit_and_process(
        self,
        claim_id: str,
        domain: str,
        gate: str,
        proposed_state: str,
        context: Dict[str, Any],
        policy_name: Optional[str] = None,
        claim_summary: Optional[str] = None,
        evidence_summary: Optional[List[str]] = None,
    ) -> FlowContext:
        """
        Submit and immediately process a decision.

        Convenience method that combines submit_decision and process_decision.

        Returns:
            FlowContext with processing results
        """
        decision = await self.submit_decision(
            claim_id=claim_id,
            domain=domain,
            gate=gate,
            proposed_state=proposed_state,
            context=context,
            policy_name=policy_name,
            claim_summary=claim_summary,
            evidence_summary=evidence_summary,
        )
        return await self.process_decision(decision.id)

    def _update_decision_from_flow(
        self,
        decision: Decision,
        ctx: FlowContext,
    ) -> None:
        """Update decision status from flow state."""
        state_to_status = {
            FlowState.AWAITING_REVIEW: DecisionStatus.AWAITING_REVIEW,
            FlowState.AWAITING_QUORUM: DecisionStatus.AWAITING_QUORUM,
            FlowState.ESCALATED: DecisionStatus.ESCALATED,
            FlowState.COMPLETED: None,  # Set by flow
            FlowState.TIMED_OUT: DecisionStatus.TIMED_OUT,
            FlowState.FAILED: DecisionStatus.CANCELLED,
        }

        new_status = state_to_status.get(ctx.current_state)
        if new_status:
            decision.status = new_status
            decision.updated_at = _utcnow()

    async def _finalize_decision(
        self,
        decision: Decision,
        ctx: FlowContext,
    ) -> None:
        """Finalize a completed decision and create audit block."""
        # Create decision block
        block = self.flow.create_decision_block(ctx)
        if block:
            self._blocks[block.id] = block
            logger.info(
                f"Decision block created: {block.id} "
                f"(decision={decision.id}, final_state={block.final_state})"
            )

        # Update metrics
        latency = ctx.elapsed_ms()
        self._update_metrics(decision, latency)

        logger.info(
            f"Decision finalized: {decision.id} "
            f"(status={decision.status.value}, latency={latency}ms)"
        )

    def _update_metrics(self, decision: Decision, latency_ms: int) -> None:
        """Update service metrics."""
        if decision.status == DecisionStatus.APPROVED:
            self._metrics["decisions_approved"] += 1
        elif decision.status == DecisionStatus.REJECTED:
            self._metrics["decisions_rejected"] += 1
        elif decision.status == DecisionStatus.TIMED_OUT:
            self._metrics["decisions_timed_out"] += 1

        # Update average latency (simple moving average)
        total = self._metrics["decisions_approved"] + self._metrics["decisions_rejected"]
        if total > 0:
            current_avg = self._metrics["avg_latency_ms"]
            self._metrics["avg_latency_ms"] = (
                (current_avg * (total - 1) + latency_ms) / total
            )

    async def add_reviewer(
        self,
        decision_id: str,
        user_id: str,
    ) -> CommitteeMember:
        """
        Add a human reviewer to a decision awaiting review.

        Args:
            decision_id: Decision ID
            user_id: ID of the reviewing user

        Returns:
            The created CommitteeMember
        """
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        if decision.status != DecisionStatus.AWAITING_REVIEW:
            raise ValueError(f"Decision not awaiting review: {decision_id}")

        ctx = self._flow_contexts.get(decision_id)
        if not ctx:
            raise ValueError(f"No flow context for decision: {decision_id}")

        # Create committee if not exists
        if not ctx.committee:
            ctx.committee = Committee.create(
                decision_id=decision_id,
                quorum_required=1,
            )
            self._committees[ctx.committee.id] = ctx.committee
            decision.committee_id = ctx.committee.id

        # Add reviewer
        member = CommitteeMember.create(
            role=GuardianRole.REVIEWER,
            user_id=user_id,
        )
        ctx.committee.add_member(member)

        logger.info(
            f"Reviewer added to decision {decision_id}: {user_id}"
        )

        return member

    async def submit_review(
        self,
        decision_id: str,
        reviewer_id: str,
        approved: bool,
        reason: Optional[str] = None,
    ) -> FlowContext:
        """
        Submit a human review decision.

        Args:
            decision_id: Decision ID
            reviewer_id: ID of the reviewer
            approved: Whether to approve
            reason: Optional reason

        Returns:
            Updated FlowContext
        """
        ctx = self._flow_contexts.get(decision_id)
        if not ctx:
            raise ValueError(f"No flow context for decision: {decision_id}")

        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        # Process review
        ctx = await self.flow.process_review_decision(
            ctx=ctx,
            approved=approved,
            reviewer_id=reviewer_id,
            reason=reason,
        )

        # Finalize if terminal
        if ctx.current_state in TERMINAL_STATES:
            await self._finalize_decision(decision, ctx)

        return ctx

    async def add_validator(
        self,
        decision_id: str,
        agent_id: str,
    ) -> CommitteeMember:
        """
        Add a validator agent to a committee decision.

        Args:
            decision_id: Decision ID
            agent_id: ID of the validator agent

        Returns:
            The created CommitteeMember
        """
        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        if decision.status != DecisionStatus.AWAITING_QUORUM:
            raise ValueError(f"Decision not awaiting quorum: {decision_id}")

        ctx = self._flow_contexts.get(decision_id)
        if not ctx or not ctx.committee:
            raise ValueError(f"No committee for decision: {decision_id}")

        # Add validator
        member = CommitteeMember.create(
            role=GuardianRole.VALIDATOR,
            agent_id=agent_id,
        )
        ctx.committee.add_member(member)

        logger.info(
            f"Validator added to decision {decision_id}: {agent_id}"
        )

        return member

    async def submit_vote(
        self,
        decision_id: str,
        member_id: str,
        vote_type: VoteType,
        reason: Optional[str] = None,
        confidence: float = 1.0,
    ) -> FlowContext:
        """
        Submit a committee vote.

        Args:
            decision_id: Decision ID
            member_id: ID of the voting member
            vote_type: Type of vote
            reason: Optional reason
            confidence: Vote confidence (0.0-1.0)

        Returns:
            Updated FlowContext
        """
        ctx = self._flow_contexts.get(decision_id)
        if not ctx:
            raise ValueError(f"No flow context for decision: {decision_id}")

        decision = self._decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision not found: {decision_id}")

        # Create vote
        vote = Vote.create(
            member_id=member_id,
            vote_type=vote_type,
            reason=reason,
            confidence=confidence,
        )

        # Process vote
        ctx = await self.flow.process_vote(ctx, vote)

        # Finalize if terminal
        if ctx.current_state in TERMINAL_STATES:
            await self._finalize_decision(decision, ctx)

        return ctx

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get a decision by ID."""
        return self._decisions.get(decision_id)

    def get_committee(self, committee_id: str) -> Optional[Committee]:
        """Get a committee by ID."""
        return self._committees.get(committee_id)

    def get_block(self, block_id: str) -> Optional[DecisionBlock]:
        """Get a decision block by ID."""
        return self._blocks.get(block_id)

    def get_decision_block(self, decision_id: str) -> Optional[DecisionBlock]:
        """Get the block for a decision."""
        for block in self._blocks.values():
            if block.decision_id == decision_id:
                return block
        return None

    def list_pending_decisions(self) -> List[Decision]:
        """List all pending/non-terminal decisions."""
        return [
            d for d in self._decisions.values()
            if not d.is_terminal()
        ]

    def list_awaiting_review(self) -> List[Decision]:
        """List decisions awaiting human review."""
        return [
            d for d in self._decisions.values()
            if d.status == DecisionStatus.AWAITING_REVIEW
        ]

    def list_awaiting_quorum(self) -> List[Decision]:
        """List decisions awaiting committee quorum."""
        return [
            d for d in self._decisions.values()
            if d.status == DecisionStatus.AWAITING_QUORUM
        ]

    def list_all_decisions(self) -> List[Decision]:
        """List all decisions (pending and completed)."""
        return list(self._decisions.values())

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            **self._metrics,
            "pending_decisions": len(self.list_pending_decisions()),
            "awaiting_review": len(self.list_awaiting_review()),
            "awaiting_quorum": len(self.list_awaiting_quorum()),
        }

    async def check_timeouts(self) -> List[Decision]:
        """
        Check for timed out decisions and update their status.

        Returns:
            List of decisions that timed out
        """
        timed_out = []
        for decision in self.list_pending_decisions():
            if decision.is_timed_out():
                decision.complete(
                    status=DecisionStatus.TIMED_OUT,
                    reason="timeout_exceeded",
                )
                timed_out.append(decision)
                self._metrics["decisions_timed_out"] += 1

                logger.warning(
                    f"Decision timed out: {decision.id}"
                )

        return timed_out


# Singleton instance
_service: Optional[GuardianService] = None


def get_guardian_service() -> GuardianService:
    """Get or create the default Guardian service instance."""
    global _service
    if _service is None:
        _service = GuardianService()
    return _service
