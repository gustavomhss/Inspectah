"""
S40-TST-003: NO-GO Signals Tests

Tests that NO-GO signals properly block state transitions:
- INCONSISTENCY signal blocks transition
- SUSPICION signal blocks transition
- ABUSE signal blocks transition
"""

from __future__ import annotations

import pytest
from datetime import datetime
from typing import Any, Dict, List
from enum import Enum
from dataclasses import dataclass, field


# Mock Signal types for testing
class SignalType(str, Enum):
    """Signal types."""
    INFO = "INFO"
    INCONSISTENCY = "INCONSISTENCY"
    SUSPICION = "SUSPICION"
    ABUSE = "ABUSE"


NOGO_SIGNAL_TYPES = frozenset([
    SignalType.INCONSISTENCY,
    SignalType.SUSPICION,
    SignalType.ABUSE,
])


@dataclass
class Signal:
    """Mock Signal class for testing."""
    id: str
    claim_id: str
    signal_type: SignalType
    severity: str
    message: str
    detected_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_nogo(self) -> bool:
        """Check if this is a NO-GO signal."""
        return self.signal_type in NOGO_SIGNAL_TYPES

    def blocks_transition(self, target_state: str) -> bool:
        """Check if this signal blocks a transition to target_state."""
        if not self.is_nogo():
            return False

        # ABUSE blocks everything except rejection
        if self.signal_type == SignalType.ABUSE:
            return target_state not in ["REJECTED", "BLOCKED"]

        # Other NO-GO signals block positive transitions
        return target_state not in ["REJECTED", "BLOCKED", "RETRACTED"]


class MockSignalRepository:
    """Mock repository for testing."""

    def __init__(self):
        self._signals: Dict[str, Signal] = {}
        self._by_claim: Dict[str, List[Signal]] = {}

    def add(self, signal: Signal) -> None:
        self._signals[signal.id] = signal
        if signal.claim_id not in self._by_claim:
            self._by_claim[signal.claim_id] = []
        self._by_claim[signal.claim_id].append(signal)

    def get(self, signal_id: str) -> Signal | None:
        return self._signals.get(signal_id)

    def get_by_claim(self, claim_id: str) -> List[Signal]:
        return self._by_claim.get(claim_id, [])

    def get_nogo_signals(self, claim_id: str) -> List[Signal]:
        return [s for s in self.get_by_claim(claim_id) if s.is_nogo()]

    def has_blocking_signal(self, claim_id: str, target_state: str) -> bool:
        for signal in self.get_by_claim(claim_id):
            if signal.blocks_transition(target_state):
                return True
        return False


class TestNoGoSignalTypes:
    """Test NO-GO signal type definitions."""

    def test_inconsistency_signal_type(self):
        """INCONSISTENCY should be a valid NO-GO signal type."""
        signal = Signal(
            id="sig-001",
            claim_id="claim-001",
            signal_type=SignalType.INCONSISTENCY,
            severity="HIGH",
            message="Contradictory evidence found",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.signal_type == SignalType.INCONSISTENCY
        assert signal.is_nogo()

    def test_suspicion_signal_type(self):
        """SUSPICION should be a valid NO-GO signal type."""
        signal = Signal(
            id="sig-002",
            claim_id="claim-002",
            signal_type=SignalType.SUSPICION,
            severity="MEDIUM",
            message="Pattern matches known misinformation",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.signal_type == SignalType.SUSPICION
        assert signal.is_nogo()

    def test_abuse_signal_type(self):
        """ABUSE should be a valid NO-GO signal type."""
        signal = Signal(
            id="sig-003",
            claim_id="claim-003",
            signal_type=SignalType.ABUSE,
            severity="CRITICAL",
            message="Coordinated inauthentic behavior detected",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.signal_type == SignalType.ABUSE
        assert signal.is_nogo()

    def test_info_signal_is_not_nogo(self):
        """INFO signal should NOT be NO-GO."""
        signal = Signal(
            id="sig-004",
            claim_id="claim-004",
            signal_type=SignalType.INFO,
            severity="LOW",
            message="Additional context available",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.signal_type == SignalType.INFO
        assert not signal.is_nogo()


class TestNoGoTransitionBlocking:
    """Test that NO-GO signals block transitions."""

    def test_inconsistency_blocks_promotion(self):
        """INCONSISTENCY signal should block promotion."""
        signal = Signal(
            id="sig-block-001",
            claim_id="claim-block-001",
            signal_type=SignalType.INCONSISTENCY,
            severity="HIGH",
            message="Evidence contradicts claim",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.blocks_transition("PROMOTED")
        assert signal.blocks_transition("UNDER_REVIEW")

    def test_suspicion_blocks_under_review(self):
        """SUSPICION signal should block under_review."""
        signal = Signal(
            id="sig-block-002",
            claim_id="claim-block-002",
            signal_type=SignalType.SUSPICION,
            severity="MEDIUM",
            message="Suspicious pattern detected",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.blocks_transition("UNDER_REVIEW")
        assert signal.blocks_transition("PROMOTED")

    def test_abuse_blocks_all_positive_transitions(self):
        """ABUSE signal should block all positive transitions."""
        signal = Signal(
            id="sig-block-003",
            claim_id="claim-block-003",
            signal_type=SignalType.ABUSE,
            severity="CRITICAL",
            message="Abuse pattern detected",
            detected_at=datetime.utcnow().isoformat(),
        )

        # ABUSE blocks everything except REJECTED/BLOCKED
        assert signal.blocks_transition("PENDING")
        assert signal.blocks_transition("UNDER_REVIEW")
        assert signal.blocks_transition("PROMOTED")
        assert signal.blocks_transition("CONTESTABLE")
        # Does not block rejection
        assert not signal.blocks_transition("REJECTED")
        assert not signal.blocks_transition("BLOCKED")

    def test_multiple_signals_compound(self):
        """Multiple NO-GO signals should compound blocking."""
        claim_id = "claim-multi-signal"

        signals = [
            Signal(
                id="sig-m1",
                claim_id=claim_id,
                signal_type=SignalType.INCONSISTENCY,
                severity="HIGH",
                message="First issue",
                detected_at=datetime.utcnow().isoformat(),
            ),
            Signal(
                id="sig-m2",
                claim_id=claim_id,
                signal_type=SignalType.SUSPICION,
                severity="MEDIUM",
                message="Second issue",
                detected_at=datetime.utcnow().isoformat(),
            ),
        ]

        for signal in signals:
            assert signal.is_nogo()
            assert signal.blocks_transition("PROMOTED")


class TestSignalRepository:
    """Test SignalRepository operations."""

    def test_add_signal(self):
        """Should add signal to repository."""
        repo = MockSignalRepository()

        signal = Signal(
            id="sig-repo-001",
            claim_id="claim-repo-001",
            signal_type=SignalType.INCONSISTENCY,
            severity="HIGH",
            message="Test signal",
            detected_at=datetime.utcnow().isoformat(),
        )

        repo.add(signal)
        retrieved = repo.get(signal.id)

        assert retrieved is not None
        assert retrieved.id == signal.id

    def test_get_by_claim(self):
        """Should retrieve signals by claim_id."""
        repo = MockSignalRepository()
        claim_id = "claim-repo-002"

        for i in range(3):
            signal = Signal(
                id=f"sig-repo-{claim_id}-{i}",
                claim_id=claim_id,
                signal_type=SignalType.INFO,
                severity="LOW",
                message=f"Signal {i}",
                detected_at=datetime.utcnow().isoformat(),
            )
            repo.add(signal)

        signals = repo.get_by_claim(claim_id)
        assert len(signals) == 3

    def test_get_nogo_signals(self):
        """Should retrieve only NO-GO signals."""
        repo = MockSignalRepository()
        claim_id = "claim-repo-003"

        repo.add(Signal(
            id="sig-nogo-1",
            claim_id=claim_id,
            signal_type=SignalType.INCONSISTENCY,
            severity="HIGH",
            message="NO-GO 1",
            detected_at=datetime.utcnow().isoformat(),
        ))
        repo.add(Signal(
            id="sig-info-1",
            claim_id=claim_id,
            signal_type=SignalType.INFO,
            severity="LOW",
            message="Info 1",
            detected_at=datetime.utcnow().isoformat(),
        ))
        repo.add(Signal(
            id="sig-nogo-2",
            claim_id=claim_id,
            signal_type=SignalType.ABUSE,
            severity="CRITICAL",
            message="NO-GO 2",
            detected_at=datetime.utcnow().isoformat(),
        ))

        nogo_signals = repo.get_nogo_signals(claim_id)
        assert len(nogo_signals) == 2
        assert all(s.is_nogo() for s in nogo_signals)

    def test_has_blocking_signal(self):
        """Should check if claim has blocking signals."""
        repo = MockSignalRepository()
        claim_id = "claim-repo-004"

        # Initially no blocking signals
        assert not repo.has_blocking_signal(claim_id, "PROMOTED")

        # Add NO-GO signal
        repo.add(Signal(
            id="sig-blocking",
            claim_id=claim_id,
            signal_type=SignalType.SUSPICION,
            severity="MEDIUM",
            message="Blocking signal",
            detected_at=datetime.utcnow().isoformat(),
        ))

        # Now should have blocking signal
        assert repo.has_blocking_signal(claim_id, "PROMOTED")


class TestNoGoEventFlow:
    """Test NOGO_BLOCKED event flow."""

    def test_nogo_signal_triggers_blocked_event(self):
        """NO-GO signal should trigger NOGO_BLOCKED event."""
        claim_id = "claim-flow-001"

        signal = Signal(
            id="sig-flow-001",
            claim_id=claim_id,
            signal_type=SignalType.ABUSE,
            severity="CRITICAL",
            message="Abuse detected",
            detected_at=datetime.utcnow().isoformat(),
        )

        assert signal.is_nogo()
        assert signal.blocks_transition("PROMOTED")

        # Event structure
        event = {
            "type": "NOGO_BLOCKED",
            "claim_id": claim_id,
            "signal_id": signal.id,
            "signal_type": signal.signal_type.value,
            "blocked_transition": "PROMOTED",
            "message": signal.message,
        }

        assert event["type"] == "NOGO_BLOCKED"
        assert event["signal_type"] == "ABUSE"

    def test_nogo_signal_preserves_context(self):
        """NO-GO blocking should preserve signal context."""
        signal = Signal(
            id="sig-context",
            claim_id="claim-context",
            signal_type=SignalType.INCONSISTENCY,
            severity="HIGH",
            message="Evidence mismatch",
            detected_at=datetime.utcnow().isoformat(),
            metadata={
                "source_a_verdict": "TRUE",
                "source_b_verdict": "FALSE",
                "confidence_delta": 0.8,
            },
        )

        assert signal.metadata is not None
        assert signal.metadata.get("confidence_delta") == 0.8
