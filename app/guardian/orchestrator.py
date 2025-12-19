"""
Guardian Orchestrator — S41

Orchestrates committee decisions for the Guardian validation system.
Manages committee selection, agent execution, and vote aggregation.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.guardian.models import (
    Committee,
    CommitteeMember,
    Vote,
    VoteType,
)
from app.guardian.roles import GuardianRole

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Outcome(str, Enum):
    """Outcome of committee orchestration."""

    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    INCONCLUSIVE = "inconclusive"


class RiskLevel(str, Enum):
    """Risk level for committee selection."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ThresholdConfig:
    """
    Threshold configuration for vote aggregation.

    Defines the minimum percentage of votes required to reach a decision.
    """

    approve_threshold: float = 0.67  # 67% for approval
    reject_threshold: float = 0.51   # 51% for rejection
    min_votes: int = 1               # Minimum votes required

    def validate(self) -> None:
        """Validate threshold configuration."""
        if not 0.0 <= self.approve_threshold <= 1.0:
            raise ValueError("approve_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.reject_threshold <= 1.0:
            raise ValueError("reject_threshold must be between 0.0 and 1.0")
        if self.min_votes < 1:
            raise ValueError("min_votes must be at least 1")


@dataclass
class CommitteeSelector:
    """
    Selects appropriate committee configuration based on domain and risk.

    Uses domain-specific rules and risk levels to determine:
    - Number of validators required
    - Quorum requirements
    - Review requirements
    """

    # Default committee sizes by risk level
    _default_sizes: Dict[RiskLevel, int] = field(default_factory=lambda: {
        RiskLevel.LOW: 1,
        RiskLevel.MEDIUM: 3,
        RiskLevel.HIGH: 5,
        RiskLevel.CRITICAL: 7,
    })

    # Domain-specific overrides
    _domain_overrides: Dict[str, Dict[RiskLevel, int]] = field(default_factory=lambda: {
        "politics": {
            RiskLevel.LOW: 3,
            RiskLevel.MEDIUM: 5,
            RiskLevel.HIGH: 7,
            RiskLevel.CRITICAL: 9,
        },
        "health": {
            RiskLevel.LOW: 3,
            RiskLevel.MEDIUM: 5,
            RiskLevel.HIGH: 7,
            RiskLevel.CRITICAL: 9,
        },
    })

    def get_committee_size(self, domain: str, risk_level: RiskLevel) -> int:
        """
        Get required committee size for domain and risk level.

        Args:
            domain: Policy domain (e.g., "politics", "health")
            risk_level: Risk level assessment

        Returns:
            Number of validators required
        """
        # Check domain-specific override
        if domain in self._domain_overrides:
            return self._domain_overrides[domain].get(
                risk_level,
                self._default_sizes[risk_level]
            )

        # Use default
        return self._default_sizes.get(risk_level, 3)

    def get_quorum(self, committee_size: int) -> int:
        """
        Calculate quorum requirement for committee size.

        Args:
            committee_size: Number of committee members

        Returns:
            Minimum votes required for quorum
        """
        # Quorum is simple majority
        return (committee_size // 2) + 1


@dataclass
class OrchestrationResult:
    """
    Result of committee orchestration.

    Contains the final outcome, votes collected, and metadata about the process.
    """

    outcome: Outcome
    votes: List[Vote] = field(default_factory=list)
    committee: Optional[Committee] = None
    approve_count: int = 0
    reject_count: int = 0
    abstain_count: int = 0
    threshold_met: bool = False
    reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        outcome: Outcome,
        votes: List[Vote],
        committee: Optional[Committee] = None,
        threshold_met: bool = False,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "OrchestrationResult":
        """
        Create an OrchestrationResult with vote counts.

        Args:
            outcome: Final outcome
            votes: List of votes collected
            committee: Committee used
            threshold_met: Whether threshold was met
            reason: Reason for outcome
            metadata: Additional metadata

        Returns:
            OrchestrationResult instance
        """
        # Count votes by type
        approve_count = sum(1 for v in votes if v.vote_type == VoteType.APPROVE)
        reject_count = sum(1 for v in votes if v.vote_type == VoteType.REJECT)
        abstain_count = sum(1 for v in votes if v.vote_type == VoteType.ABSTAIN)

        return cls(
            outcome=outcome,
            votes=votes,
            committee=committee,
            approve_count=approve_count,
            reject_count=reject_count,
            abstain_count=abstain_count,
            threshold_met=threshold_met,
            reason=reason,
            metadata=metadata or {},
        )


class CommitteeOrchestrator:
    """
    Orchestrates committee-based decisions in the Guardian system.

    Responsibilities:
    - Select appropriate committee based on domain and risk
    - Execute agents in parallel to collect votes
    - Aggregate votes using threshold logic
    - Return final outcome with full audit trail
    """

    def __init__(
        self,
        selector: Optional[CommitteeSelector] = None,
        threshold_config: Optional[ThresholdConfig] = None,
    ):
        """
        Initialize committee orchestrator.

        Args:
            selector: Committee selector (uses default if None)
            threshold_config: Threshold configuration (uses default if None)
        """
        self.selector = selector or CommitteeSelector()
        self.threshold_config = threshold_config or ThresholdConfig()
        self.threshold_config.validate()

    def select_committee(
        self,
        domain: str,
        risk_level: RiskLevel,
        decision_id: str,
    ) -> Committee:
        """
        Select committee configuration for a decision.

        Args:
            domain: Policy domain (e.g., "politics", "health")
            risk_level: Risk level assessment
            decision_id: ID of the decision being made

        Returns:
            Committee instance configured for the decision
        """
        # Get committee size from selector
        committee_size = self.selector.get_committee_size(domain, risk_level)
        quorum = self.selector.get_quorum(committee_size)

        # Create committee
        committee = Committee.create(
            decision_id=decision_id,
            quorum_required=quorum,
        )

        # Add proponent (always present)
        proponent = CommitteeMember.create(
            role=GuardianRole.PROPONENT,
            agent_id=f"proponent_{decision_id}",
        )
        committee.add_member(proponent)

        # Add validators based on committee size
        for i in range(committee_size):
            validator = CommitteeMember.create(
                role=GuardianRole.VALIDATOR,
                agent_id=f"validator_{i}_{decision_id}",
            )
            committee.add_member(validator)

        logger.info(
            f"Committee selected: {committee_size} validators, "
            f"quorum={quorum} for {domain}:{risk_level.value}"
        )

        return committee

    async def execute_agents_parallel(
        self,
        committee: Committee,
        context: Dict[str, Any],
    ) -> List[Vote]:
        """
        Execute validator agents in parallel to collect votes.

        In a production system, this would invoke actual agent instances.
        For now, this is a mock implementation that simulates agent responses.

        Args:
            committee: Committee with members to execute
            context: Context dictionary with claim data for agents

        Returns:
            List of votes from validators
        """
        validators = committee.get_validators()

        if not validators:
            logger.warning(f"No validators in committee {committee.id}")
            return []

        # In production, this would be:
        # tasks = [self._execute_agent(v, context) for v in validators]
        # votes = await asyncio.gather(*tasks)
        # return [v for v in votes if v is not None]

        # Mock implementation: simulate agent execution
        votes = []
        for validator in validators:
            vote = await self._simulate_agent_vote(validator, context)
            if vote:
                votes.append(vote)
                committee.add_vote(vote)

        logger.info(
            f"Collected {len(votes)} votes from {len(validators)} validators"
        )

        return votes

    async def _simulate_agent_vote(
        self,
        member: CommitteeMember,
        context: Dict[str, Any],
    ) -> Optional[Vote]:
        """
        Simulate an agent vote (placeholder for actual agent execution).

        In production, this would:
        1. Load agent instance
        2. Provide claim context
        3. Execute agent reasoning
        4. Return structured vote

        Args:
            member: Committee member executing
            context: Context for voting decision

        Returns:
            Vote from the agent (or None if agent fails)
        """
        # Simulate some processing time
        await asyncio.sleep(0.1)

        # Mock logic: approve if context has "approved" flag
        # In reality, this would be complex agent reasoning
        should_approve = context.get("mock_approve", True)

        vote_type = VoteType.APPROVE if should_approve else VoteType.REJECT
        reason = "Mock agent vote (to be replaced with real agent)"

        return Vote.create(
            member_id=member.id,
            vote_type=vote_type,
            reason=reason,
            confidence=0.8,
        )

    def aggregate_votes(
        self,
        votes: List[Vote],
        threshold: Optional[ThresholdConfig] = None,
    ) -> Outcome:
        """
        Aggregate votes using threshold logic to determine outcome.

        Logic:
        - APPROVED: >= threshold of APPROVE votes
        - REJECTED: >= threshold of REJECT votes
        - NEEDS_REVIEW: Has votes but no threshold met
        - INCONCLUSIVE: No votes or exact tie

        Args:
            votes: List of votes to aggregate
            threshold: Threshold config (uses default if None)

        Returns:
            Final outcome
        """
        threshold = threshold or self.threshold_config

        if not votes:
            logger.warning("No votes to aggregate")
            return Outcome.INCONCLUSIVE

        # Count votes by type
        total_votes = len(votes)
        approve_count = sum(1 for v in votes if v.vote_type == VoteType.APPROVE)
        reject_count = sum(1 for v in votes if v.vote_type == VoteType.REJECT)
        abstain_count = sum(1 for v in votes if v.vote_type == VoteType.ABSTAIN)

        # Check minimum votes
        if total_votes < threshold.min_votes:
            logger.warning(
                f"Insufficient votes: {total_votes} < {threshold.min_votes}"
            )
            return Outcome.NEEDS_REVIEW

        # Calculate percentages (excluding abstentions for threshold calculation)
        active_votes = total_votes - abstain_count
        if active_votes == 0:
            logger.warning("All votes were abstentions")
            return Outcome.INCONCLUSIVE

        approve_pct = approve_count / active_votes
        reject_pct = reject_count / active_votes

        logger.debug(
            f"Vote counts: approve={approve_count} ({approve_pct:.2%}), "
            f"reject={reject_count} ({reject_pct:.2%}), "
            f"abstain={abstain_count}"
        )

        # Check for exact tie first
        if approve_count == reject_count and approve_count > 0:
            return Outcome.INCONCLUSIVE

        # Apply threshold logic
        if approve_pct >= threshold.approve_threshold:
            return Outcome.APPROVED
        elif reject_pct >= threshold.reject_threshold:
            return Outcome.REJECTED
        else:
            # Has votes but no threshold met
            return Outcome.NEEDS_REVIEW

    async def orchestrate(
        self,
        claim_id: str,
        domain: str,
        risk_level: RiskLevel,
        context: Dict[str, Any],
        decision_id: Optional[str] = None,
    ) -> OrchestrationResult:
        """
        Orchestrate a complete committee decision.

        This is the main entry point that:
        1. Selects appropriate committee
        2. Executes agents in parallel
        3. Aggregates votes
        4. Returns final outcome

        Args:
            claim_id: ID of claim being decided
            domain: Policy domain
            risk_level: Risk level assessment
            context: Context dict with claim data
            decision_id: Optional decision ID (generated if None)

        Returns:
            OrchestrationResult with outcome and full audit trail
        """
        decision_id = decision_id or f"dec_{claim_id[:12]}"

        logger.info(
            f"Starting orchestration for {claim_id} "
            f"({domain}:{risk_level.value})"
        )

        try:
            # Step 1: Select committee
            committee = self.select_committee(
                domain=domain,
                risk_level=risk_level,
                decision_id=decision_id,
            )

            # Step 2: Execute agents in parallel
            votes = await self.execute_agents_parallel(
                committee=committee,
                context=context,
            )

            # Step 3: Aggregate votes
            outcome = self.aggregate_votes(votes, self.threshold_config)

            # Step 4: Determine threshold status
            threshold_met = outcome in (Outcome.APPROVED, Outcome.REJECTED)

            # Step 5: Generate reason
            reason = self._generate_reason(outcome, votes)

            # Create result
            result = OrchestrationResult.create(
                outcome=outcome,
                votes=votes,
                committee=committee,
                threshold_met=threshold_met,
                reason=reason,
                metadata={
                    "claim_id": claim_id,
                    "domain": domain,
                    "risk_level": risk_level.value,
                    "committee_size": len(committee.members),
                    "quorum_required": committee.quorum_required,
                },
            )

            logger.info(
                f"Orchestration complete: {outcome.value} "
                f"(approve={result.approve_count}, reject={result.reject_count})"
            )

            return result

        except Exception as e:
            logger.exception(f"Orchestration failed: {e}")
            # Return inconclusive result on error
            return OrchestrationResult.create(
                outcome=Outcome.INCONCLUSIVE,
                votes=[],
                committee=None,
                threshold_met=False,
                reason=f"Orchestration error: {str(e)}",
                metadata={
                    "claim_id": claim_id,
                    "domain": domain,
                    "error": str(e),
                },
            )

    def _generate_reason(self, outcome: Outcome, votes: List[Vote]) -> str:
        """
        Generate human-readable reason for outcome.

        Args:
            outcome: Final outcome
            votes: List of votes

        Returns:
            Reason string
        """
        vote_counts = {
            VoteType.APPROVE: sum(1 for v in votes if v.vote_type == VoteType.APPROVE),
            VoteType.REJECT: sum(1 for v in votes if v.vote_type == VoteType.REJECT),
            VoteType.ABSTAIN: sum(1 for v in votes if v.vote_type == VoteType.ABSTAIN),
        }

        if outcome == Outcome.APPROVED:
            return (
                f"Committee approved with {vote_counts[VoteType.APPROVE]} votes "
                f"(threshold met)"
            )
        elif outcome == Outcome.REJECTED:
            return (
                f"Committee rejected with {vote_counts[VoteType.REJECT]} votes "
                f"(threshold met)"
            )
        elif outcome == Outcome.NEEDS_REVIEW:
            return (
                f"Committee decision unclear - needs human review "
                f"(approve={vote_counts[VoteType.APPROVE]}, "
                f"reject={vote_counts[VoteType.REJECT]})"
            )
        else:  # INCONCLUSIVE
            if not votes:
                return "No votes collected"
            return (
                f"Inconclusive result - tie or insufficient votes "
                f"(approve={vote_counts[VoteType.APPROVE]}, "
                f"reject={vote_counts[VoteType.REJECT]})"
            )


def get_threshold(risk_level: RiskLevel) -> ThresholdConfig:
    """
    Get threshold configuration for a risk level.

    Higher risk levels require higher approval thresholds.

    Args:
        risk_level: Risk level

    Returns:
        ThresholdConfig instance
    """
    thresholds = {
        RiskLevel.LOW: ThresholdConfig(
            approve_threshold=0.51,  # Simple majority for low risk
            reject_threshold=0.51,
            min_votes=1,
        ),
        RiskLevel.MEDIUM: ThresholdConfig(
            approve_threshold=0.67,  # 2/3 majority for medium risk
            reject_threshold=0.51,
            min_votes=3,
        ),
        RiskLevel.HIGH: ThresholdConfig(
            approve_threshold=0.75,  # 3/4 majority for high risk
            reject_threshold=0.51,
            min_votes=5,
        ),
        RiskLevel.CRITICAL: ThresholdConfig(
            approve_threshold=0.80,  # 4/5 majority for critical risk
            reject_threshold=0.51,
            min_votes=7,
        ),
    }
    return thresholds.get(risk_level, ThresholdConfig())


# Singleton instance
_orchestrator: Optional[CommitteeOrchestrator] = None


def get_committee_orchestrator() -> CommitteeOrchestrator:
    """Get or create the default CommitteeOrchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CommitteeOrchestrator()
    return _orchestrator
