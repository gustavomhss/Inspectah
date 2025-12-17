"""
Sprint 40: NO-GO Signals for Claims.

Tasks: S40-BE-014, S40-BE-015, S40-BE-017
NO-GO signals block state transitions when detected.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class SignalType(str, Enum):
    """Types of NO-GO signals (S40-BE-014)."""

    INCONSISTENCY = "INCONSISTENCY"  # Contradictory evidence or claims
    SUSPICION = "SUSPICION"  # Suspicious patterns detected
    ABUSE = "ABUSE"  # Abuse/manipulation detected


class SignalSeverity(str, Enum):
    """Severity levels for signals."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NOGOSignal:
    """
    NO-GO Signal (S40-BE-014).

    NO-GO signals block state transitions and require resolution.
    """

    signal_id: str
    type: SignalType
    severity: SignalSeverity
    claim_id: str
    reason: str
    detected_at: datetime = field(default_factory=_utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        type: SignalType,
        severity: SignalSeverity,
        claim_id: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "NOGOSignal":
        """Create a new NO-GO signal."""
        return cls(
            signal_id=f"sig_{uuid4().hex[:12]}",
            type=type,
            severity=severity,
            claim_id=claim_id,
            reason=reason,
            metadata=metadata or {},
        )

    def resolve(self, resolved_by: str, reason: str) -> None:
        """Resolve this signal."""
        self.resolved = True
        self.resolved_at = _utcnow()
        self.resolved_by = resolved_by
        self.resolution_reason = reason

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "signal_id": self.signal_id,
            "type": self.type.value,
            "severity": self.severity.value,
            "claim_id": self.claim_id,
            "reason": self.reason,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_reason": self.resolution_reason,
            "metadata": self.metadata,
        }

    def is_blocking(self) -> bool:
        """Check if this signal blocks transitions."""
        if self.resolved:
            return False
        # All unresolved signals block
        return True


# INCONSISTENCY detection thresholds (S40-BE-017)
INCONSISTENCY_THRESHOLDS = {
    "contradiction_weight_threshold": 0.7,  # Edge weight above this is strong contradiction
    "evidence_conflict_ratio": 0.5,  # If >50% evidence conflicts, flag
    "temporal_conflict_days": 30,  # Claims within 30 days that contradict
}

# SUSPICION detection patterns
SUSPICION_PATTERNS = {
    "rapid_claim_threshold": 10,  # More than 10 claims/minute
    "duplicate_ratio_threshold": 0.8,  # 80% similar text
    "source_concentration_threshold": 0.9,  # 90% from single source
}

# ABUSE detection patterns
ABUSE_PATTERNS = {
    "repeated_false_claims_threshold": 3,  # 3+ retracted claims from same source
    "coordinated_action_threshold": 5,  # 5+ identical claims in short window
}


def detect_inconsistency(
    claim_id: str,
    evidence_trail: List[Dict[str, Any]],
    related_claims: Optional[List[Dict[str, Any]]] = None,
    contradiction_edges: Optional[List[Dict[str, Any]]] = None,
) -> Optional[NOGOSignal]:
    """
    Detect INCONSISTENCY signals (S40-BE-017).

    Checks for:
    - Conflicting evidence in the evidence trail
    - Strong contradictions with other claims
    - Temporal conflicts

    Args:
        claim_id: ID of the claim to check
        evidence_trail: List of evidence items
        related_claims: Optional list of related claims
        contradiction_edges: Optional list of contradiction edges

    Returns:
        NOGOSignal if inconsistency detected, None otherwise
    """
    # Check for evidence conflicts
    if evidence_trail:
        supports = sum(1 for e in evidence_trail if e.get("stance") == "supports")
        refutes = sum(1 for e in evidence_trail if e.get("stance") == "refutes")
        total = supports + refutes

        if total > 0:
            conflict_ratio = refutes / total
            if conflict_ratio >= INCONSISTENCY_THRESHOLDS["evidence_conflict_ratio"]:
                return NOGOSignal.create(
                    type=SignalType.INCONSISTENCY,
                    severity=SignalSeverity.HIGH if conflict_ratio >= 0.7 else SignalSeverity.MEDIUM,
                    claim_id=claim_id,
                    reason=f"Evidence conflict: {refutes}/{total} evidence items refute the claim",
                    metadata={"supports": supports, "refutes": refutes, "conflict_ratio": conflict_ratio},
                )

    # Check for strong contradictions
    if contradiction_edges:
        strong_contradictions = [
            e
            for e in contradiction_edges
            if (e.get("weight") or 0) >= INCONSISTENCY_THRESHOLDS["contradiction_weight_threshold"]
        ]
        if strong_contradictions:
            return NOGOSignal.create(
                type=SignalType.INCONSISTENCY,
                severity=SignalSeverity.HIGH,
                claim_id=claim_id,
                reason=f"Strong contradiction with {len(strong_contradictions)} other claims",
                metadata={"contradicting_claims": [e.get("target_id") for e in strong_contradictions]},
            )

    return None


def detect_suspicion(
    claim_id: str,
    source_claims: List[Dict[str, Any]],
    time_window_minutes: int = 10,
) -> Optional[NOGOSignal]:
    """
    Detect SUSPICION signals (S40-BE-014).

    Checks for:
    - Rapid claim submission
    - Duplicate claims
    - Source concentration

    Args:
        claim_id: ID of the claim to check
        source_claims: List of claims from the same source in time window
        time_window_minutes: Time window in minutes

    Returns:
        NOGOSignal if suspicion detected, None otherwise
    """
    claim_count = len(source_claims)

    # Check for rapid claims
    if claim_count > SUSPICION_PATTERNS["rapid_claim_threshold"]:
        return NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.MEDIUM,
            claim_id=claim_id,
            reason=f"Rapid claim submission: {claim_count} claims in {time_window_minutes} minutes",
            metadata={"claim_count": claim_count, "window_minutes": time_window_minutes},
        )

    return None


def detect_abuse(
    claim_id: str,
    source_id: str,
    retracted_claims_count: int,
    coordinated_claims: Optional[List[Dict[str, Any]]] = None,
) -> Optional[NOGOSignal]:
    """
    Detect ABUSE signals (S40-BE-014).

    Checks for:
    - Repeated false claims from same source
    - Coordinated posting patterns

    Args:
        claim_id: ID of the claim to check
        source_id: ID of the source
        retracted_claims_count: Number of retracted claims from this source
        coordinated_claims: Optional list of coordinated claims

    Returns:
        NOGOSignal if abuse detected, None otherwise
    """
    # Check for repeated false claims
    if retracted_claims_count >= ABUSE_PATTERNS["repeated_false_claims_threshold"]:
        return NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.HIGH,
            claim_id=claim_id,
            reason=f"Source has {retracted_claims_count} previously retracted claims",
            metadata={"source_id": source_id, "retracted_count": retracted_claims_count},
        )

    # Check for coordinated actions
    if coordinated_claims and len(coordinated_claims) >= ABUSE_PATTERNS["coordinated_action_threshold"]:
        return NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.CRITICAL,
            claim_id=claim_id,
            reason=f"Coordinated action detected: {len(coordinated_claims)} identical claims",
            metadata={"coordinated_claim_ids": [c.get("claim_id") for c in coordinated_claims]},
        )

    return None


class SignalRepository:
    """Repository for NO-GO signals (S40-BE-014)."""

    def __init__(self) -> None:
        self._signals: Dict[str, NOGOSignal] = {}
        self._by_claim: Dict[str, List[str]] = {}

    def add(self, signal: NOGOSignal) -> NOGOSignal:
        """Add a signal to the repository."""
        self._signals[signal.signal_id] = signal
        if signal.claim_id not in self._by_claim:
            self._by_claim[signal.claim_id] = []
        self._by_claim[signal.claim_id].append(signal.signal_id)
        logger.info(f"Added signal {signal.signal_id} for claim {signal.claim_id}")
        return signal

    def get(self, signal_id: str) -> Optional[NOGOSignal]:
        """Get a signal by ID."""
        return self._signals.get(signal_id)

    def get_by_claim(self, claim_id: str, include_resolved: bool = False) -> List[NOGOSignal]:
        """Get all signals for a claim."""
        signal_ids = self._by_claim.get(claim_id, [])
        signals = [self._signals[sid] for sid in signal_ids if sid in self._signals]
        if not include_resolved:
            signals = [s for s in signals if not s.resolved]
        return signals

    def get_blocking_signals(self, claim_id: str) -> List[NOGOSignal]:
        """Get all blocking signals for a claim."""
        return [s for s in self.get_by_claim(claim_id) if s.is_blocking()]

    def has_blocking_signals(self, claim_id: str) -> bool:
        """Check if a claim has any blocking signals."""
        return len(self.get_blocking_signals(claim_id)) > 0

    def resolve(self, signal_id: str, resolved_by: str, reason: str) -> bool:
        """Resolve a signal."""
        signal = self._signals.get(signal_id)
        if signal:
            signal.resolve(resolved_by, reason)
            logger.info(f"Resolved signal {signal_id} by {resolved_by}")
            return True
        return False

    def count(self, claim_id: Optional[str] = None) -> int:
        """Count signals."""
        if claim_id:
            return len(self._by_claim.get(claim_id, []))
        return len(self._signals)


# Singleton instance
_signal_repository: Optional[SignalRepository] = None


def get_signal_repository() -> SignalRepository:
    """Get the default signal repository."""
    global _signal_repository
    if _signal_repository is None:
        _signal_repository = SignalRepository()
    return _signal_repository


def check_nogo_signals(
    claim_id: str,
    evidence_trail: Optional[List[Dict[str, Any]]] = None,
    contradiction_edges: Optional[List[Dict[str, Any]]] = None,
    source_claims: Optional[List[Dict[str, Any]]] = None,
    source_id: Optional[str] = None,
    retracted_count: int = 0,
) -> List[NOGOSignal]:
    """
    Check for all NO-GO signals on a claim (S40-BE-014, S40-BE-017).

    Args:
        claim_id: ID of the claim to check
        evidence_trail: Evidence items
        contradiction_edges: Contradiction edges
        source_claims: Claims from same source
        source_id: Source ID
        retracted_count: Number of retracted claims from source

    Returns:
        List of detected NOGOSignal objects
    """
    signals: List[NOGOSignal] = []

    # Check for INCONSISTENCY
    inconsistency = detect_inconsistency(
        claim_id=claim_id,
        evidence_trail=evidence_trail or [],
        contradiction_edges=contradiction_edges,
    )
    if inconsistency:
        signals.append(inconsistency)

    # Check for SUSPICION
    if source_claims:
        suspicion = detect_suspicion(
            claim_id=claim_id,
            source_claims=source_claims,
        )
        if suspicion:
            signals.append(suspicion)

    # Check for ABUSE
    if source_id:
        abuse = detect_abuse(
            claim_id=claim_id,
            source_id=source_id,
            retracted_claims_count=retracted_count,
        )
        if abuse:
            signals.append(abuse)

    return signals
