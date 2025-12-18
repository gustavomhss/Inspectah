"""
S40-BE-026: Truth Twin and Decision Inspector DTOs.

Response schemas for P4 Exposure endpoints with full provenance support.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _safe_list(value: Any, default: Optional[List] = None) -> List:
    """Safely convert value to list with defensive copy."""
    if value is None:
        return list(default) if default else []
    if isinstance(value, list):
        return list(value)  # Defensive copy
    return []


def _safe_dict(value: Any, default: Optional[Dict] = None) -> Dict:
    """Safely convert value to dict with defensive copy."""
    if value is None:
        return dict(default) if default else {}
    if isinstance(value, dict):
        return copy.copy(value)  # Shallow defensive copy
    return {}


def _safe_str(value: Any, default: str = "") -> str:
    """Safely convert value to string."""
    if value is None:
        return default
    return str(value)


@dataclass
class ProvenanceInfo:
    """Provenance information for audit trail."""

    source: str
    timestamp: str
    policy_version: Optional[str] = None
    policy_name: Optional[str] = None
    actor: Optional[str] = None
    evidence_refs: List[str] = field(default_factory=list)
    references: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Ensure evidence_refs is always a list."""
        if self.evidence_refs is None:
            self.evidence_refs = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "timestamp": self.timestamp,
            "policy_version": self.policy_version,
            "policy_name": self.policy_name,
            "actor": self.actor,
            "evidence_refs": list(self.evidence_refs),  # Defensive copy
            "references": copy.copy(self.references) if self.references else None,
        }


@dataclass
class StateTransitionInfo:
    """State transition information."""

    from_state: str
    to_state: str
    reason: str
    timestamp: str
    decision_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "decision_id": self.decision_id,
        }


@dataclass
class DecisionBlockSummary:
    """Summary of a decision block for timeline display."""

    id: str
    decision_id: str
    gate: str
    decision_type: str
    initial_state: str
    final_state: str
    created_at: str
    latency_ms: Optional[int] = None
    policy_name: Optional[str] = None
    policy_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "gate": self.gate,
            "decision_type": self.decision_type,
            "initial_state": self.initial_state,
            "final_state": self.final_state,
            "created_at": self.created_at,
            "latency_ms": self.latency_ms,
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
        }


@dataclass
class TruthTwinResponse:
    """
    Response for GET /api/truth/{claim_id}/twin (S40-BE-023).

    Provides a complete view of a claim's truth status with full provenance.
    """

    claim_id: str
    domain: str
    current_state: str
    created_at: str
    updated_at: str
    # Claim content (S40 - displayed to user)
    slug: Optional[str] = None
    headline: Optional[str] = None
    claim_text: Optional[str] = None  # Full claim text for display
    # Timeline of decisions
    decision_timeline: List[DecisionBlockSummary] = field(default_factory=list)
    # Full provenance
    provenance: Optional[ProvenanceInfo] = None
    # State transitions history
    state_history: List[StateTransitionInfo] = field(default_factory=list)
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Experience references (similar claims)
    experience_refs: List[str] = field(default_factory=list)
    # Last decision details
    last_decision_id: Optional[str] = None

    def __post_init__(self):
        """Ensure list and dict fields are never None."""
        if self.decision_timeline is None:
            self.decision_timeline = []
        if self.state_history is None:
            self.state_history = []
        if self.metadata is None:
            self.metadata = {}
        if self.experience_refs is None:
            self.experience_refs = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "slug": self.slug,
            "headline": self.headline,
            "claim_text": self.claim_text,
            "domain": self.domain,
            "current_state": self.current_state,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "decision_timeline": [d.to_dict() for d in self.decision_timeline],
            "provenance": self.provenance.to_dict() if self.provenance else None,
            "state_history": [s.to_dict() for s in self.state_history],
            "metadata": _safe_dict(self.metadata),  # Defensive copy
            "experience_refs": list(self.experience_refs),  # Defensive copy
            "last_decision_id": self.last_decision_id,
        }

    def has_valid_provenance(self) -> bool:
        """Check if response has valid provenance (required for P4)."""
        return self.provenance is not None and bool(self.provenance.source)

    def get_decision_count(self) -> int:
        """Get total number of decisions in timeline."""
        return len(self.decision_timeline)

    def get_last_decision(self) -> Optional[DecisionBlockSummary]:
        """Get the most recent decision from timeline."""
        if not self.decision_timeline:
            return None
        return self.decision_timeline[-1]


@dataclass
class DecisionInspectResponse:
    """
    Response for GET /api/truth/decision/{decision_id}/inspect (S40-BE-024).

    Provides complete details of a specific decision with full provenance.
    """

    decision_id: str
    block_id: str
    claim_id: str
    domain: str
    gate: str
    decision_type: str
    # States
    initial_state: str
    final_state: str
    # Policy info
    policy_name: Optional[str] = None
    policy_version: Optional[str] = None
    # Committee details
    committee_summary: Dict[str, Any] = field(default_factory=dict)
    # Invariants
    invariants_checked: Dict[str, Any] = field(default_factory=dict)
    # Evidence
    evidence_refs: List[str] = field(default_factory=list)
    # S40 references (guias, pilares, e40_5)
    references: Optional[Dict[str, Any]] = None
    # State transition details
    state_transition: Optional[Dict[str, Any]] = None
    # Experience references
    experience_refs: List[str] = field(default_factory=list)
    # Timestamps
    created_at: str = ""
    latency_ms: Optional[int] = None
    # Full provenance
    provenance: Optional[ProvenanceInfo] = None

    def __post_init__(self):
        """Ensure list and dict fields are never None."""
        if self.committee_summary is None:
            self.committee_summary = {}
        if self.invariants_checked is None:
            self.invariants_checked = {}
        if self.evidence_refs is None:
            self.evidence_refs = []
        if self.experience_refs is None:
            self.experience_refs = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "block_id": self.block_id,
            "claim_id": self.claim_id,
            "domain": self.domain,
            "gate": self.gate,
            "decision_type": self.decision_type,
            "initial_state": self.initial_state,
            "final_state": self.final_state,
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
            "committee_summary": _safe_dict(self.committee_summary),  # Defensive copy
            "invariants_checked": _safe_dict(self.invariants_checked),  # Defensive copy
            "evidence_refs": list(self.evidence_refs),  # Defensive copy
            "references": copy.copy(self.references) if self.references else None,
            "state_transition": copy.copy(self.state_transition) if self.state_transition else None,
            "experience_refs": list(self.experience_refs),  # Defensive copy
            "created_at": self.created_at,
            "latency_ms": self.latency_ms,
            "provenance": self.provenance.to_dict() if self.provenance else None,
        }

    def has_valid_provenance(self) -> bool:
        """Check if response has valid provenance (required for P4)."""
        return self.provenance is not None and bool(self.provenance.source)

    def is_state_changed(self) -> bool:
        """Check if this decision changed the claim state."""
        return self.initial_state != self.final_state

    def get_invariant_violations(self) -> List[str]:
        """Get list of invariants that were violated (False)."""
        return [
            name for name, passed in self.invariants_checked.items()
            if passed is False
        ]


def build_truth_twin_response(
    record: Dict[str, Any],
    decision_blocks: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
) -> TruthTwinResponse:
    """
    Build a TruthTwinResponse from repository data.

    Args:
        record: TruthRecord or dict with claim info
        decision_blocks: List of DecisionBlock dicts
        events: List of state change events

    Returns:
        TruthTwinResponse with full provenance
    """
    # Ensure inputs are valid
    if record is None:
        record = {}
    if decision_blocks is None:
        decision_blocks = []
    if events is None:
        events = []

    # Build decision timeline
    timeline = []
    for block in decision_blocks:
        if not isinstance(block, dict):
            logger.warning(f"[build_truth_twin] Skipping invalid block: {type(block)}")
            continue
        summary = DecisionBlockSummary(
            id=_safe_str(block.get("id")),
            decision_id=_safe_str(block.get("decision_id")),
            gate=_safe_str(block.get("gate")),
            decision_type=_safe_str(block.get("decision_type")),
            initial_state=_safe_str(block.get("initial_state")),
            final_state=_safe_str(block.get("final_state")),
            created_at=_safe_str(block.get("created_at")),
            latency_ms=block.get("latency_ms"),
            policy_name=block.get("policy_name"),
            policy_version=block.get("policy_version"),
        )
        timeline.append(summary)

    # Build state history from events
    state_history = []
    for event in events:
        if not isinstance(event, dict):
            logger.warning(f"[build_truth_twin] Skipping invalid event: {type(event)}")
            continue
        transition = StateTransitionInfo(
            from_state=_safe_str(event.get("previous_state")),
            to_state=_safe_str(event.get("new_state")),
            reason=_safe_str(event.get("reason")),
            timestamp=_safe_str(event.get("created_at")),
            decision_id=event.get("decision_id"),
        )
        state_history.append(transition)

    # Get last decision for provenance and claim_text
    provenance = None
    last_exp_refs: List[str] = []
    claim_text = None

    # Try to get claim_text from metadata first
    metadata = _safe_dict(record.get("metadata"))
    if metadata.get("claim_text"):
        claim_text = metadata.get("claim_text")

    if decision_blocks:
        last_block = decision_blocks[-1]
        if isinstance(last_block, dict):
            provenance = ProvenanceInfo(
                source="decision_block",
                timestamp=_safe_str(last_block.get("created_at")),
                policy_version=last_block.get("policy_version"),
                policy_name=last_block.get("policy_name"),
                evidence_refs=_safe_list(last_block.get("evidence_refs")),
                references=last_block.get("references"),
            )
            last_exp_refs = _safe_list(last_block.get("experience_refs"))

            # Try to get claim_text from committee_summary.notes if not already set
            if not claim_text:
                committee = _safe_dict(last_block.get("committee_summary"))
                notes = committee.get("notes", "")
                if notes and notes.startswith("Verified: "):
                    claim_text = notes[10:]  # Remove "Verified: " prefix
                elif notes:
                    claim_text = notes

    # Fallback to headline or slug
    if not claim_text:
        claim_text = record.get("headline") or record.get("slug")

    return TruthTwinResponse(
        claim_id=_safe_str(record.get("claim_id")) or _safe_str(record.get("id")),
        slug=record.get("slug"),
        headline=record.get("headline"),
        claim_text=claim_text,
        domain=_safe_str(record.get("domain")),
        current_state=_safe_str(record.get("current_state")),
        created_at=_safe_str(record.get("created_at")),
        updated_at=_safe_str(record.get("updated_at")),
        decision_timeline=timeline,
        provenance=provenance,
        state_history=state_history,
        metadata=metadata,  # Already computed above
        experience_refs=last_exp_refs,
        last_decision_id=record.get("last_decision_id"),
    )


def build_decision_inspect_response(block: Dict[str, Any]) -> DecisionInspectResponse:
    """
    Build a DecisionInspectResponse from a DecisionBlock.

    Args:
        block: DecisionBlock dict from repository

    Returns:
        DecisionInspectResponse with full provenance

    Raises:
        ValueError: If block is None or not a dict
    """
    if block is None:
        raise ValueError("block cannot be None")
    if not isinstance(block, dict):
        raise ValueError(f"block must be a dict, got {type(block)}")

    provenance = ProvenanceInfo(
        source="decision_block",
        timestamp=_safe_str(block.get("created_at")),
        policy_version=block.get("policy_version"),
        policy_name=block.get("policy_name"),
        evidence_refs=_safe_list(block.get("evidence_refs")),
        references=block.get("references"),
    )

    return DecisionInspectResponse(
        decision_id=_safe_str(block.get("decision_id")),
        block_id=_safe_str(block.get("id")),
        claim_id=_safe_str(block.get("claim_id")),
        domain=_safe_str(block.get("domain")),
        gate=_safe_str(block.get("gate")),
        decision_type=_safe_str(block.get("decision_type")),
        initial_state=_safe_str(block.get("initial_state")),
        final_state=_safe_str(block.get("final_state")),
        policy_name=block.get("policy_name"),
        policy_version=block.get("policy_version"),
        committee_summary=_safe_dict(block.get("committee_summary")),
        invariants_checked=_safe_dict(block.get("invariants_checked")),
        evidence_refs=_safe_list(block.get("evidence_refs")),
        references=block.get("references"),
        state_transition=block.get("state_transition"),
        experience_refs=_safe_list(block.get("experience_refs")),
        created_at=_safe_str(block.get("created_at")),
        latency_ms=block.get("latency_ms"),
        provenance=provenance,
    )
