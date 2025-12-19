"""
Guardian Committee Management — S37

Responsible for selecting and managing validation committees.
Implements risk-based committee sizing and member selection logic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from app.guardian.models import Committee, CommitteeMember, Vote
from app.guardian.roles import GuardianRole

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class RiskLevel(str, Enum):
    """Risk level for committee sizing."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Risk-based committee sizing rules
COMMITTEE_SIZE_RULES = {
    RiskLevel.LOW: 3,
    RiskLevel.MEDIUM: 5,
    RiskLevel.HIGH: 7,
}


@dataclass
class CommitteeConfig:
    """Configuration for creating a committee."""

    domain: str
    risk_level: RiskLevel
    quorum_required: int
    require_proponent: bool = True
    require_reviewer: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class MemberPool:
    """Pool of available agents for committee selection."""

    validators: List[str] = field(default_factory=list)
    reviewers: List[str] = field(default_factory=list)
    arbiters: List[str] = field(default_factory=list)

    def has_validators(self, count: int) -> bool:
        """Check if pool has enough validators."""
        return len(self.validators) >= count

    def has_reviewers(self, count: int) -> bool:
        """Check if pool has enough reviewers."""
        return len(self.reviewers) >= count

    def has_arbiters(self, count: int) -> bool:
        """Check if pool has enough arbiters."""
        return len(self.arbiters) >= count


class CommitteeSelector:
    """
    Selects committee members based on domain, risk level, and availability.

    Selection Strategy:
    - LOW risk: 3 validators
    - MEDIUM risk: 5 validators
    - HIGH risk: 7 validators

    Members are selected from a pool of available agents.
    """

    def __init__(self, member_pool: Optional[MemberPool] = None):
        """
        Initialize the committee selector.

        Args:
            member_pool: Pool of available agents. If None, uses default pool.
        """
        self.member_pool = member_pool or self._create_default_pool()

    def _create_default_pool(self) -> MemberPool:
        """Create a default member pool for testing."""
        return MemberPool(
            validators=[
                "validator_001",
                "validator_002",
                "validator_003",
                "validator_004",
                "validator_005",
                "validator_006",
                "validator_007",
            ],
            reviewers=["reviewer_001", "reviewer_002"],
            arbiters=["arbiter_001"],
        )

    def select_members(
        self,
        domain: str,
        risk_level: RiskLevel,
        size: Optional[int] = None,
    ) -> List[str]:
        """
        Select committee members based on risk level.

        Args:
            domain: Policy domain (e.g., "politics", "health")
            risk_level: Risk level determining committee size
            size: Optional override for committee size

        Returns:
            List of agent IDs selected for the committee

        Raises:
            ValueError: If not enough agents available
        """
        # Determine required size
        required_size = size if size is not None else COMMITTEE_SIZE_RULES[risk_level]

        # Check availability
        if not self.member_pool.has_validators(required_size):
            raise ValueError(
                f"Insufficient validators: need {required_size}, "
                f"have {len(self.member_pool.validators)}"
            )

        # Select validators (simple round-robin for now)
        selected = self.member_pool.validators[:required_size]

        logger.info(
            f"Selected {len(selected)} validators for domain={domain}, "
            f"risk_level={risk_level.value}"
        )

        return selected

    def get_committee_size(self, risk_level: RiskLevel) -> int:
        """
        Get the required committee size for a risk level.

        Args:
            risk_level: Risk level

        Returns:
            Number of committee members required
        """
        return COMMITTEE_SIZE_RULES[risk_level]


class CommitteeManager:
    """
    Manages committee lifecycle: creation, member assignment, and vote recording.

    Responsibilities:
    - Create committees with appropriate members
    - Assign roles to committee members
    - Record and track votes
    - Calculate quorum and decisions
    """

    def __init__(self, selector: Optional[CommitteeSelector] = None):
        """
        Initialize the committee manager.

        Args:
            selector: CommitteeSelector instance. If None, creates default.
        """
        self.selector = selector or CommitteeSelector()

        # In-memory storage (replace with repository in production)
        self._committees: Dict[str, Committee] = {}
        self._votes_by_committee: Dict[str, List[Vote]] = {}

    def create_committee(
        self,
        decision_id: str,
        config: CommitteeConfig,
        proponent_agent_id: Optional[str] = None,
    ) -> Committee:
        """
        Create a committee with selected members.

        Args:
            decision_id: ID of the decision this committee will validate
            config: Configuration for committee creation
            proponent_agent_id: Optional agent ID for the proponent

        Returns:
            Created Committee instance
        """
        # Create base committee
        committee = Committee.create(
            decision_id=decision_id,
            quorum_required=config.quorum_required,
        )

        # Add proponent if required
        if config.require_proponent:
            proponent = CommitteeMember.create(
                role=GuardianRole.PROPONENT,
                agent_id=proponent_agent_id,
            )
            committee.add_member(proponent)

        # Select and add validators
        validator_size = self.selector.get_committee_size(config.risk_level)
        validator_ids = self.selector.select_members(
            domain=config.domain,
            risk_level=config.risk_level,
            size=validator_size,
        )

        for validator_id in validator_ids:
            validator = CommitteeMember.create(
                role=GuardianRole.VALIDATOR,
                agent_id=validator_id,
            )
            committee.add_member(validator)

        # Add reviewer if required
        if config.require_reviewer and self.selector.member_pool.has_reviewers(1):
            reviewer_id = self.selector.member_pool.reviewers[0]
            reviewer = CommitteeMember.create(
                role=GuardianRole.REVIEWER,
                agent_id=reviewer_id,
            )
            committee.add_member(reviewer)

        # Store committee
        self._committees[committee.id] = committee
        self._votes_by_committee[committee.id] = []

        logger.info(
            f"Created committee {committee.id} for decision {decision_id} "
            f"with {len(committee.members)} members"
        )

        return committee

    def get_committee(self, committee_id: str) -> Optional[Committee]:
        """
        Get a committee by ID.

        Args:
            committee_id: Committee ID

        Returns:
            Committee instance or None if not found
        """
        return self._committees.get(committee_id)

    def record_votes(self, committee_id: str, votes: List[Vote]) -> None:
        """
        Record votes for a committee.

        Args:
            committee_id: Committee ID
            votes: List of votes to record

        Raises:
            ValueError: If committee not found
        """
        committee = self._committees.get(committee_id)
        if not committee:
            raise ValueError(f"Committee {committee_id} not found")

        # Add votes to committee
        for vote in votes:
            committee.add_vote(vote)
            self._votes_by_committee[committee_id].append(vote)

        logger.info(
            f"Recorded {len(votes)} votes for committee {committee_id}. "
            f"Total votes: {len(committee.votes)}"
        )

    def record_vote(
        self,
        committee_id: str,
        member_id: str,
        vote: Vote,
    ) -> None:
        """
        Record a single vote for a committee.

        Args:
            committee_id: Committee ID
            member_id: Member ID casting the vote
            vote: Vote to record

        Raises:
            ValueError: If committee not found or member not in committee
        """
        committee = self._committees.get(committee_id)
        if not committee:
            raise ValueError(f"Committee {committee_id} not found")

        # Verify member exists in committee
        member_ids = {m.id for m in committee.members}
        if member_id not in member_ids:
            raise ValueError(
                f"Member {member_id} not found in committee {committee_id}"
            )

        # Add vote
        committee.add_vote(vote)
        self._votes_by_committee[committee_id].append(vote)

        logger.debug(
            f"Recorded vote {vote.id} from member {member_id} "
            f"for committee {committee_id}"
        )

    def get_votes(self, committee_id: str) -> List[Vote]:
        """
        Get all votes for a committee.

        Args:
            committee_id: Committee ID

        Returns:
            List of votes
        """
        return self._votes_by_committee.get(committee_id, [])

    def has_quorum(self, committee_id: str) -> bool:
        """
        Check if a committee has reached quorum.

        Args:
            committee_id: Committee ID

        Returns:
            True if quorum reached, False otherwise

        Raises:
            ValueError: If committee not found
        """
        committee = self._committees.get(committee_id)
        if not committee:
            raise ValueError(f"Committee {committee_id} not found")

        return committee.has_quorum()

    def get_decision(self, committee_id: str) -> Optional[str]:
        """
        Get the committee's decision based on votes.

        Args:
            committee_id: Committee ID

        Returns:
            Decision string ("approve", "reject", or None if no decision)

        Raises:
            ValueError: If committee not found
        """
        committee = self._committees.get(committee_id)
        if not committee:
            raise ValueError(f"Committee {committee_id} not found")

        decision = committee.get_decision()
        return decision.value if decision else None

    def clear(self) -> None:
        """Clear all committees and votes (for testing)."""
        self._committees.clear()
        self._votes_by_committee.clear()


# Factory functions for convenience
def create_selector(member_pool: Optional[MemberPool] = None) -> CommitteeSelector:
    """
    Create a CommitteeSelector instance.

    Args:
        member_pool: Optional member pool

    Returns:
        CommitteeSelector instance
    """
    return CommitteeSelector(member_pool=member_pool)


def create_manager(selector: Optional[CommitteeSelector] = None) -> CommitteeManager:
    """
    Create a CommitteeManager instance.

    Args:
        selector: Optional selector instance

    Returns:
        CommitteeManager instance
    """
    return CommitteeManager(selector=selector)
