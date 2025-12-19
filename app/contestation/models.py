"""
Contestation Models — S41

Models for the contestation module, implementing dispute cases and acordaos.
Based on the MAC (Máquina Adiabática de Consenso) conceptual guide.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def _generate_id(prefix: str = "disp") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid4().hex[:12]}"


class DisputeStatus(str, Enum):
    """Status of a dispute case in the FSM."""

    DRAFT = "draft"  # Initial state, not yet filed
    FILED = "filed"  # Formally submitted
    UNDER_TRIAGE = "under_triage"  # Being evaluated for admissibility
    INSTRUCTION = "instruction"  # Evidence gathering phase
    READY_FOR_DECISION = "ready_for_decision"  # All evidence collected
    DECIDED = "decided"  # Acordao issued
    CLOSED = "closed"  # Final state, no more actions
    REJECTED = "rejected"  # Dismissed without decision


class AcordaoOutcome(str, Enum):
    """Possible outcomes of an acordao (final decision)."""

    UPHELD = "upheld"  # Original decision maintained
    OVERTURNED = "overturned"  # Original decision reversed
    MODIFIED = "modified"  # Original decision partially changed
    REMANDED = "remanded"  # Sent back for re-evaluation


class AppealType(str, Enum):
    """Types of appeals that can be filed."""

    FACTUAL = "factual"  # Dispute about facts
    PROCEDURAL = "procedural"  # Dispute about process
    ETHICAL = "ethical"  # Dispute about ethical implications
    TECHNICAL = "technical"  # Dispute about technical analysis


class EvidenceType(str, Enum):
    """Types of evidence that can be submitted."""

    DOCUMENT = "document"  # Text documents
    SOURCE = "source"  # New sources
    EXPERT = "expert"  # Expert testimony
    PRECEDENT = "precedent"  # Previous similar cases
    ANALYSIS = "analysis"  # Re-analysis of existing evidence


@dataclass
class EvidenceRef:
    """Reference to evidence in a dispute case."""

    id: str = field(default_factory=lambda: _generate_id("evd"))
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    url: Optional[str] = None
    content_hash: Optional[str] = None
    description: str = ""
    submitted_at: datetime = field(default_factory=_utcnow)
    submitted_by: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "evidence_type": self.evidence_type.value,
            "url": self.url,
            "content_hash": self.content_hash,
            "description": self.description,
            "submitted_at": self.submitted_at.isoformat(),
            "submitted_by": self.submitted_by,
            "metadata": self.metadata,
        }


@dataclass
class DisputeGround:
    """A ground for disputing a decision."""

    id: str = field(default_factory=lambda: _generate_id("gnd"))
    ground_type: AppealType = AppealType.FACTUAL
    description: str = ""
    supporting_evidence: List[str] = field(default_factory=list)  # Evidence IDs
    weight: float = 1.0  # Importance weight (0.0 to 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "ground_type": self.ground_type.value,
            "description": self.description,
            "supporting_evidence": self.supporting_evidence,
            "weight": self.weight,
        }


@dataclass
class DisputeCaseModel:
    """
    Model representing a dispute case.

    A dispute case goes through an FSM from DRAFT to CLOSED,
    accumulating evidence and grounds until a final decision (Acordao).
    """

    id: str = field(default_factory=lambda: _generate_id("case"))
    claim_id: str = ""
    original_decision_id: str = ""
    status: DisputeStatus = DisputeStatus.DRAFT
    petitioner_id: str = ""
    petitioner_name: Optional[str] = None
    grounds: List[DisputeGround] = field(default_factory=list)
    evidence: List[EvidenceRef] = field(default_factory=list)
    acordao_id: Optional[str] = None
    priority: int = 0  # Higher = more urgent
    domain: Optional[str] = None
    risk_level: Optional[str] = None
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)
    filed_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_ground(self, ground: DisputeGround) -> None:
        """Add a ground for the dispute."""
        self.grounds.append(ground)
        self.updated_at = _utcnow()

    def add_evidence(self, evidence: EvidenceRef) -> None:
        """Add evidence to the dispute."""
        self.evidence.append(evidence)
        self.updated_at = _utcnow()

    def file(self) -> None:
        """File the dispute case (transition from DRAFT to FILED)."""
        if self.status != DisputeStatus.DRAFT:
            raise ValueError(f"Cannot file case in status {self.status.value}")
        if not self.grounds:
            raise ValueError("Cannot file case without grounds")
        self.status = DisputeStatus.FILED
        self.filed_at = _utcnow()
        self.updated_at = _utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "original_decision_id": self.original_decision_id,
            "status": self.status.value,
            "petitioner_id": self.petitioner_id,
            "petitioner_name": self.petitioner_name,
            "grounds": [g.to_dict() for g in self.grounds],
            "evidence": [e.to_dict() for e in self.evidence],
            "acordao_id": self.acordao_id,
            "priority": self.priority,
            "domain": self.domain,
            "risk_level": self.risk_level,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "filed_at": self.filed_at.isoformat() if self.filed_at else None,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "metadata": self.metadata,
        }


@dataclass
class VoteRecord:
    """Record of a vote in the acordao process."""

    voter_id: str = ""
    voter_role: str = ""  # e.g., "arbiter", "validator"
    vote: str = ""  # e.g., "uphold", "overturn", "modify"
    confidence: float = 0.0
    reasoning: str = ""
    timestamp: datetime = field(default_factory=_utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "voter_id": self.voter_id,
            "voter_role": self.voter_role,
            "vote": self.vote,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class TensorEticoResult:
    """Result of the ethical tensor calculation."""

    social_impact: float = 0.0  # -1.0 to 1.0
    individual_impact: float = 0.0  # -1.0 to 1.0
    precedent_weight: float = 0.0  # 0.0 to 1.0
    urgency_factor: float = 0.0  # 0.0 to 1.0
    overall_score: float = 0.0  # Composite score
    calculation_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "social_impact": self.social_impact,
            "individual_impact": self.individual_impact,
            "precedent_weight": self.precedent_weight,
            "urgency_factor": self.urgency_factor,
            "overall_score": self.overall_score,
            "calculation_metadata": self.calculation_metadata,
        }


@dataclass
class AcordaoModel:
    """
    Model representing an Acordao (final decision in a dispute).

    The Acordao is the result of the MAC (Máquina Adiabática de Consenso)
    process and represents the authoritative resolution of a dispute.
    """

    id: str = field(default_factory=lambda: _generate_id("acrd"))
    dispute_case_id: str = ""
    outcome: AcordaoOutcome = AcordaoOutcome.UPHELD
    original_decision_id: str = ""
    new_decision_id: Optional[str] = None  # If overturned/modified
    votes: List[VoteRecord] = field(default_factory=list)
    delta_crenca: float = 0.0  # Change in belief (Δcrença from MAC)
    lambda_factor: float = 0.0  # Confidence factor (λ-factor from MAC)
    tensor_etico: Optional[TensorEticoResult] = None
    reasoning: str = ""
    summary: str = ""
    precedents_cited: List[str] = field(default_factory=list)
    dissenting_opinions: List[str] = field(default_factory=list)
    issued_at: datetime = field(default_factory=_utcnow)
    issued_by: str = ""  # Committee or arbiter ID
    finalized: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_vote(self, vote: VoteRecord) -> None:
        """Add a vote to the acordao."""
        self.votes.append(vote)

    def calculate_consensus(self) -> float:
        """
        Calculate consensus level from votes.

        Returns a value between 0.0 (no consensus) and 1.0 (full consensus).
        """
        if not self.votes:
            return 0.0

        # Count votes by outcome
        vote_counts: Dict[str, int] = {}
        for vote in self.votes:
            vote_counts[vote.vote] = vote_counts.get(vote.vote, 0) + 1

        # Consensus is the percentage of the most common vote
        max_count = max(vote_counts.values())
        return max_count / len(self.votes)

    def finalize(self) -> None:
        """Finalize the acordao (no more changes allowed)."""
        if self.finalized:
            raise ValueError("Acordao already finalized")
        if not self.votes:
            raise ValueError("Cannot finalize acordao without votes")
        self.finalized = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "dispute_case_id": self.dispute_case_id,
            "outcome": self.outcome.value,
            "original_decision_id": self.original_decision_id,
            "new_decision_id": self.new_decision_id,
            "votes": [v.to_dict() for v in self.votes],
            "delta_crenca": self.delta_crenca,
            "lambda_factor": self.lambda_factor,
            "tensor_etico": self.tensor_etico.to_dict() if self.tensor_etico else None,
            "reasoning": self.reasoning,
            "summary": self.summary,
            "precedents_cited": self.precedents_cited,
            "dissenting_opinions": self.dissenting_opinions,
            "issued_at": self.issued_at.isoformat(),
            "issued_by": self.issued_by,
            "finalized": self.finalized,
            "metadata": self.metadata,
        }
