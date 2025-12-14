"""
Guardian Models — S37

Data models for the Guardian validation system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.guardian.roles import GuardianRole


def _generate_id(prefix: str = "grd") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class DecisionStatus(str, Enum):
    """Status of a decision in the Guardian flow."""

    PENDING = "pending"
    VALIDATING = "validating"
    AWAITING_REVIEW = "awaiting_review"
    AWAITING_QUORUM = "awaiting_quorum"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


class VoteType(str, Enum):
    """Type of vote from a validator."""

    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"


@dataclass
class CommitteeMember:
    """A member of a validation committee."""

    id: str
    role: GuardianRole
    agent_id: Optional[str] = None  # For agent validators
    user_id: Optional[str] = None   # For human reviewers
    assigned_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        role: GuardianRole,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> "CommitteeMember":
        return cls(
            id=_generate_id("mem"),
            role=role,
            agent_id=agent_id,
            user_id=user_id,
        )


@dataclass
class Vote:
    """A vote from a committee member."""

    id: str
    member_id: str
    vote_type: VoteType
    reason: Optional[str] = None
    confidence: float = 1.0
    voted_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        member_id: str,
        vote_type: VoteType,
        reason: Optional[str] = None,
        confidence: float = 1.0,
    ) -> "Vote":
        return cls(
            id=_generate_id("vot"),
            member_id=member_id,
            vote_type=vote_type,
            reason=reason,
            confidence=confidence,
        )


@dataclass
class Committee:
    """A validation committee for a decision."""

    id: str
    decision_id: str
    members: List[CommitteeMember] = field(default_factory=list)
    votes: List[Vote] = field(default_factory=list)
    quorum_required: int = 1
    created_at: datetime = field(default_factory=_utcnow)

    @classmethod
    def create(
        cls,
        decision_id: str,
        quorum_required: int = 1,
    ) -> "Committee":
        return cls(
            id=_generate_id("com"),
            decision_id=decision_id,
            quorum_required=quorum_required,
        )

    def add_member(self, member: CommitteeMember) -> None:
        """Add a member to the committee."""
        self.members.append(member)

    def add_vote(self, vote: Vote) -> None:
        """Add a vote to the committee."""
        self.votes.append(vote)

    def get_proponent(self) -> Optional[CommitteeMember]:
        """Get the proponent member."""
        for m in self.members:
            if m.role == GuardianRole.PROPONENT:
                return m
        return None

    def get_validators(self) -> List[CommitteeMember]:
        """Get all validator members."""
        return [m for m in self.members if m.role == GuardianRole.VALIDATOR]

    def get_reviewer(self) -> Optional[CommitteeMember]:
        """Get the reviewer member."""
        for m in self.members:
            if m.role == GuardianRole.REVIEWER:
                return m
        return None

    def count_votes(self) -> Dict[VoteType, int]:
        """Count votes by type."""
        counts = {VoteType.APPROVE: 0, VoteType.REJECT: 0, VoteType.ABSTAIN: 0}
        for vote in self.votes:
            counts[vote.vote_type] = counts.get(vote.vote_type, 0) + 1
        return counts

    def has_quorum(self) -> bool:
        """Check if quorum has been reached."""
        return len(self.votes) >= self.quorum_required

    def get_decision(self) -> Optional[VoteType]:
        """Get the committee's decision based on votes."""
        if not self.has_quorum():
            return None
        counts = self.count_votes()
        if counts[VoteType.APPROVE] > counts[VoteType.REJECT]:
            return VoteType.APPROVE
        elif counts[VoteType.REJECT] > counts[VoteType.APPROVE]:
            return VoteType.REJECT
        return None  # Tie


@dataclass
class Decision:
    """A decision being processed by the Guardian."""

    id: str
    claim_id: str
    domain: str
    gate: str
    proposed_state: str
    status: DecisionStatus = DecisionStatus.PENDING
    claim_summary: Optional[str] = None  # Human-readable: "O que está sendo decidido?"
    evidence_summary: Optional[List[str]] = None  # Evidências que ancoram a claim
    context: Dict[str, Any] = field(default_factory=dict)
    policy_name: Optional[str] = None
    committee_id: Optional[str] = None
    final_state: Optional[str] = None
    final_reason: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    completed_at: Optional[datetime] = None
    timeout_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        claim_id: str,
        domain: str,
        gate: str,
        proposed_state: str,
        context: Optional[Dict[str, Any]] = None,
        policy_name: Optional[str] = None,
        claim_summary: Optional[str] = None,
        evidence_summary: Optional[List[str]] = None,
        timeout_seconds: int = 20,
    ) -> "Decision":
        now = _utcnow()
        from datetime import timedelta
        timeout = now + timedelta(seconds=timeout_seconds)
        return cls(
            id=_generate_id("dec"),
            claim_id=claim_id,
            domain=domain,
            gate=gate,
            proposed_state=proposed_state,
            claim_summary=claim_summary,
            evidence_summary=evidence_summary,
            context=context or {},
            policy_name=policy_name,
            timeout_at=timeout,
        )

    def is_terminal(self) -> bool:
        """Check if decision is in a terminal state."""
        return self.status in (
            DecisionStatus.APPROVED,
            DecisionStatus.REJECTED,
            DecisionStatus.ESCALATED,
            DecisionStatus.TIMED_OUT,
            DecisionStatus.CANCELLED,
        )

    def is_timed_out(self) -> bool:
        """Check if decision has timed out."""
        if self.timeout_at is None:
            return False
        return _utcnow() > self.timeout_at

    def complete(
        self,
        status: DecisionStatus,
        final_state: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Complete the decision."""
        self.status = status
        self.final_state = final_state
        self.final_reason = reason
        self.completed_at = _utcnow()
        self.updated_at = _utcnow()


@dataclass
class DecisionBlock:
    """
    Final output of a Guardian decision.

    Contains all references and evidence for audit trail.
    """

    id: str
    decision_id: str
    claim_id: str
    domain: str
    gate: str
    initial_state: str
    final_state: str
    decision_type: str  # auto_approve, human_review, committee, escalated
    policy_name: Optional[str]
    policy_version: Optional[str]
    committee_summary: Optional[Dict[str, Any]]
    invariants_checked: Dict[str, bool]
    evidence_refs: List[str]
    created_at: datetime = field(default_factory=_utcnow)
    latency_ms: Optional[int] = None

    @classmethod
    def create(
        cls,
        decision: Decision,
        committee: Optional[Committee],
        policy_version: Optional[str],
        invariants: Dict[str, bool],
        evidence_refs: Optional[List[str]] = None,
        latency_ms: Optional[int] = None,
    ) -> "DecisionBlock":
        committee_summary = None
        if committee:
            committee_summary = {
                "committee_id": committee.id,
                "member_count": len(committee.members),
                "vote_counts": {k.value: v for k, v in committee.count_votes().items()},
                "quorum_required": committee.quorum_required,
                "quorum_reached": committee.has_quorum(),
            }

        return cls(
            id=_generate_id("blk"),
            decision_id=decision.id,
            claim_id=decision.claim_id,
            domain=decision.domain,
            gate=decision.gate,
            initial_state=decision.proposed_state,
            final_state=decision.final_state or decision.proposed_state,
            decision_type=decision.status.value,
            policy_name=decision.policy_name,
            policy_version=policy_version,
            committee_summary=committee_summary,
            invariants_checked=invariants,
            evidence_refs=evidence_refs or [],
            latency_ms=latency_ms,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "claim_id": self.claim_id,
            "domain": self.domain,
            "gate": self.gate,
            "initial_state": self.initial_state,
            "final_state": self.final_state,
            "decision_type": self.decision_type,
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
            "committee_summary": self.committee_summary,
            "invariants_checked": self.invariants_checked,
            "evidence_refs": self.evidence_refs,
            "created_at": self.created_at.isoformat(),
            "latency_ms": self.latency_ms,
        }
