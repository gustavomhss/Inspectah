"""
Tests for NO-GO Signals functionality.

Tasks: S40-BE-014, S40-BE-015, S40-BE-017
"""

from datetime import datetime, timezone

import pytest

from app.claims.signals import (
    ABUSE_PATTERNS,
    INCONSISTENCY_THRESHOLDS,
    SUSPICION_PATTERNS,
    NOGOSignal,
    SignalRepository,
    SignalSeverity,
    SignalType,
    check_nogo_signals,
    detect_abuse,
    detect_inconsistency,
    detect_suspicion,
    get_signal_repository,
)


class TestSignalType:
    """Tests for SignalType enum."""

    def test_signal_types_defined(self):
        """Test all signal types are defined."""
        assert SignalType.INCONSISTENCY == "INCONSISTENCY"
        assert SignalType.SUSPICION == "SUSPICION"
        assert SignalType.ABUSE == "ABUSE"

    def test_signal_type_values(self):
        """Test signal type string values."""
        assert SignalType.INCONSISTENCY.value == "INCONSISTENCY"
        assert SignalType.SUSPICION.value == "SUSPICION"
        assert SignalType.ABUSE.value == "ABUSE"


class TestSignalSeverity:
    """Tests for SignalSeverity enum."""

    def test_severity_levels_defined(self):
        """Test all severity levels are defined."""
        assert SignalSeverity.LOW == "low"
        assert SignalSeverity.MEDIUM == "medium"
        assert SignalSeverity.HIGH == "high"
        assert SignalSeverity.CRITICAL == "critical"

    def test_severity_values(self):
        """Test severity string values."""
        assert SignalSeverity.LOW.value == "low"
        assert SignalSeverity.MEDIUM.value == "medium"
        assert SignalSeverity.HIGH.value == "high"
        assert SignalSeverity.CRITICAL.value == "critical"


class TestNOGOSignal:
    """Tests for NOGOSignal dataclass."""

    def test_create_signal(self):
        """Test creating a signal via factory method."""
        signal = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-001",
            reason="Test inconsistency",
        )

        assert signal.type == SignalType.INCONSISTENCY
        assert signal.severity == SignalSeverity.HIGH
        assert signal.claim_id == "claim-001"
        assert signal.reason == "Test inconsistency"
        assert signal.signal_id.startswith("sig_")
        assert not signal.resolved
        assert signal.resolved_at is None
        assert signal.resolved_by is None

    def test_create_signal_with_metadata(self):
        """Test creating a signal with metadata."""
        metadata = {"source_id": "src-1", "count": 5}
        signal = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.CRITICAL,
            claim_id="claim-002",
            reason="Test abuse",
            metadata=metadata,
        )

        assert signal.metadata == metadata
        assert signal.metadata["source_id"] == "src-1"

    def test_signal_is_blocking_unresolved(self):
        """Test that unresolved signals are blocking."""
        signal = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.MEDIUM,
            claim_id="claim-003",
            reason="Test suspicion",
        )

        assert signal.is_blocking() is True

    def test_signal_is_blocking_resolved(self):
        """Test that resolved signals are not blocking."""
        signal = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.MEDIUM,
            claim_id="claim-004",
            reason="Test suspicion",
        )
        signal.resolve("admin", "False positive")

        assert signal.is_blocking() is False

    def test_resolve_signal(self):
        """Test resolving a signal."""
        signal = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-005",
            reason="Test resolve",
        )

        signal.resolve("moderator", "Verified as correct")

        assert signal.resolved is True
        assert signal.resolved_by == "moderator"
        assert signal.resolution_reason == "Verified as correct"
        assert signal.resolved_at is not None
        assert isinstance(signal.resolved_at, datetime)

    def test_signal_to_dict(self):
        """Test converting signal to dict."""
        signal = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.CRITICAL,
            claim_id="claim-006",
            reason="Test dict conversion",
            metadata={"key": "value"},
        )

        signal_dict = signal.to_dict()

        assert signal_dict["signal_id"] == signal.signal_id
        assert signal_dict["type"] == "ABUSE"
        assert signal_dict["severity"] == "critical"
        assert signal_dict["claim_id"] == "claim-006"
        assert signal_dict["reason"] == "Test dict conversion"
        assert signal_dict["resolved"] is False
        assert signal_dict["resolved_at"] is None
        assert signal_dict["metadata"]["key"] == "value"
        assert "detected_at" in signal_dict

    def test_signal_to_dict_resolved(self):
        """Test converting resolved signal to dict."""
        signal = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.LOW,
            claim_id="claim-007",
            reason="Test",
        )
        signal.resolve("admin", "OK")

        signal_dict = signal.to_dict()

        assert signal_dict["resolved"] is True
        assert signal_dict["resolved_by"] == "admin"
        assert signal_dict["resolution_reason"] == "OK"
        assert signal_dict["resolved_at"] is not None


class TestSignalRepository:
    """Tests for SignalRepository."""

    def test_create_repository(self):
        """Test creating a repository."""
        repo = SignalRepository()

        assert repo.count() == 0

    def test_add_signal(self):
        """Test adding a signal."""
        repo = SignalRepository()
        signal = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-001",
            reason="Test",
        )

        result = repo.add(signal)

        assert result == signal
        assert repo.count() == 1

    def test_get_signal(self):
        """Test getting a signal by ID."""
        repo = SignalRepository()
        signal = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.CRITICAL,
            claim_id="claim-002",
            reason="Test",
        )
        repo.add(signal)

        retrieved = repo.get(signal.signal_id)

        assert retrieved is not None
        assert retrieved.signal_id == signal.signal_id

    def test_get_nonexistent_signal(self):
        """Test getting a nonexistent signal."""
        repo = SignalRepository()

        result = repo.get("nonexistent-id")

        assert result is None

    def test_get_by_claim(self):
        """Test getting signals by claim ID."""
        repo = SignalRepository()
        signal1 = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-100",
            reason="Signal 1",
        )
        signal2 = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.MEDIUM,
            claim_id="claim-100",
            reason="Signal 2",
        )
        signal3 = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.LOW,
            claim_id="claim-200",
            reason="Signal 3",
        )
        repo.add(signal1)
        repo.add(signal2)
        repo.add(signal3)

        signals = repo.get_by_claim("claim-100")

        assert len(signals) == 2
        signal_ids = {s.signal_id for s in signals}
        assert signal1.signal_id in signal_ids
        assert signal2.signal_id in signal_ids

    def test_get_by_claim_include_resolved(self):
        """Test getting signals including resolved ones."""
        repo = SignalRepository()
        signal1 = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-300",
            reason="Active",
        )
        signal2 = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.LOW,
            claim_id="claim-300",
            reason="Resolved",
        )
        signal2.resolve("admin", "OK")
        repo.add(signal1)
        repo.add(signal2)

        # Without resolved
        active_signals = repo.get_by_claim("claim-300", include_resolved=False)
        assert len(active_signals) == 1

        # With resolved
        all_signals = repo.get_by_claim("claim-300", include_resolved=True)
        assert len(all_signals) == 2

    def test_get_blocking_signals(self):
        """Test getting blocking signals."""
        repo = SignalRepository()
        signal1 = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-400",
            reason="Blocking",
        )
        signal2 = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.LOW,
            claim_id="claim-400",
            reason="Not blocking",
        )
        signal2.resolve("admin", "OK")
        repo.add(signal1)
        repo.add(signal2)

        blocking = repo.get_blocking_signals("claim-400")

        assert len(blocking) == 1
        assert blocking[0].signal_id == signal1.signal_id

    def test_has_blocking_signals(self):
        """Test checking for blocking signals."""
        repo = SignalRepository()
        signal = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.CRITICAL,
            claim_id="claim-500",
            reason="Test",
        )
        repo.add(signal)

        assert repo.has_blocking_signals("claim-500") is True
        assert repo.has_blocking_signals("claim-999") is False

    def test_resolve_signal_in_repo(self):
        """Test resolving a signal via repository."""
        repo = SignalRepository()
        signal = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-600",
            reason="To resolve",
        )
        repo.add(signal)

        result = repo.resolve(signal.signal_id, "moderator", "Verified")

        assert result is True
        assert signal.resolved is True
        assert not repo.has_blocking_signals("claim-600")

    def test_resolve_nonexistent_signal(self):
        """Test resolving a nonexistent signal."""
        repo = SignalRepository()

        result = repo.resolve("nonexistent-id", "admin", "Test")

        assert result is False

    def test_count_all(self):
        """Test counting all signals."""
        repo = SignalRepository()
        for i in range(5):
            signal = NOGOSignal.create(
                type=SignalType.SUSPICION,
                severity=SignalSeverity.LOW,
                claim_id=f"claim-{i}",
                reason=f"Signal {i}",
            )
            repo.add(signal)

        assert repo.count() == 5

    def test_count_by_claim(self):
        """Test counting signals by claim."""
        repo = SignalRepository()
        for i in range(3):
            signal = NOGOSignal.create(
                type=SignalType.SUSPICION,
                severity=SignalSeverity.LOW,
                claim_id="claim-target",
                reason=f"Signal {i}",
            )
            repo.add(signal)
        signal_other = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.HIGH,
            claim_id="claim-other",
            reason="Other",
        )
        repo.add(signal_other)

        assert repo.count("claim-target") == 3
        assert repo.count("claim-other") == 1
        assert repo.count("claim-none") == 0


class TestDetectInconsistency:
    """Tests for detect_inconsistency function."""

    def test_no_inconsistency_empty_evidence(self):
        """Test no inconsistency with empty evidence."""
        result = detect_inconsistency(
            claim_id="claim-001",
            evidence_trail=[],
        )

        assert result is None

    def test_no_inconsistency_all_supports(self):
        """Test no inconsistency when all evidence supports."""
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "supports"},
            {"evidence_id": "e3", "stance": "supports"},
        ]

        result = detect_inconsistency(
            claim_id="claim-002",
            evidence_trail=evidence,
        )

        assert result is None

    def test_inconsistency_high_refute_ratio(self):
        """Test inconsistency detected with high refute ratio."""
        # 60% refutes - above the 50% threshold
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "supports"},
            {"evidence_id": "e3", "stance": "refutes"},
            {"evidence_id": "e4", "stance": "refutes"},
            {"evidence_id": "e5", "stance": "refutes"},
        ]

        result = detect_inconsistency(
            claim_id="claim-003",
            evidence_trail=evidence,
        )

        assert result is not None
        assert result.type == SignalType.INCONSISTENCY
        assert result.claim_id == "claim-003"
        assert "conflict" in result.reason.lower()

    def test_inconsistency_severity_high(self):
        """Test inconsistency has high severity for very high conflict ratio."""
        # 80% refutes - should be HIGH severity
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "refutes"},
            {"evidence_id": "e3", "stance": "refutes"},
            {"evidence_id": "e4", "stance": "refutes"},
            {"evidence_id": "e5", "stance": "refutes"},
        ]

        result = detect_inconsistency(
            claim_id="claim-004",
            evidence_trail=evidence,
        )

        assert result is not None
        assert result.severity == SignalSeverity.HIGH

    def test_inconsistency_severity_medium(self):
        """Test inconsistency has medium severity for moderate conflict ratio."""
        # 50% refutes - should be MEDIUM severity (between 0.5 and 0.7)
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "refutes"},
        ]

        result = detect_inconsistency(
            claim_id="claim-005",
            evidence_trail=evidence,
        )

        assert result is not None
        assert result.severity == SignalSeverity.MEDIUM

    def test_inconsistency_strong_contradiction_edges(self):
        """Test inconsistency from strong contradiction edges."""
        edges = [
            {"target_id": "other-claim-1", "weight": 0.8},
            {"target_id": "other-claim-2", "weight": 0.9},
        ]

        result = detect_inconsistency(
            claim_id="claim-006",
            evidence_trail=[],
            contradiction_edges=edges,
        )

        assert result is not None
        assert result.type == SignalType.INCONSISTENCY
        assert result.severity == SignalSeverity.HIGH
        assert "contradiction" in result.reason.lower()
        assert result.metadata["contradicting_claims"] == ["other-claim-1", "other-claim-2"]

    def test_no_inconsistency_weak_contradiction_edges(self):
        """Test no inconsistency from weak contradiction edges."""
        edges = [
            {"target_id": "other-claim-1", "weight": 0.3},
            {"target_id": "other-claim-2", "weight": 0.5},
        ]

        result = detect_inconsistency(
            claim_id="claim-007",
            evidence_trail=[],
            contradiction_edges=edges,
        )

        assert result is None

    def test_inconsistency_metadata_included(self):
        """Test inconsistency includes metadata."""
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "refutes"},
            {"evidence_id": "e3", "stance": "refutes"},
        ]

        result = detect_inconsistency(
            claim_id="claim-008",
            evidence_trail=evidence,
        )

        assert result is not None
        assert "supports" in result.metadata
        assert "refutes" in result.metadata
        assert "conflict_ratio" in result.metadata


class TestDetectSuspicion:
    """Tests for detect_suspicion function."""

    def test_no_suspicion_low_claim_count(self):
        """Test no suspicion with low claim count."""
        source_claims = [{"claim_id": f"c{i}"} for i in range(5)]

        result = detect_suspicion(
            claim_id="claim-001",
            source_claims=source_claims,
        )

        assert result is None

    def test_suspicion_rapid_claims(self):
        """Test suspicion detected with rapid claim submission."""
        # More than 10 claims in 10 minutes
        source_claims = [{"claim_id": f"c{i}"} for i in range(15)]

        result = detect_suspicion(
            claim_id="claim-002",
            source_claims=source_claims,
        )

        assert result is not None
        assert result.type == SignalType.SUSPICION
        assert result.severity == SignalSeverity.MEDIUM
        assert "rapid" in result.reason.lower()
        assert result.metadata["claim_count"] == 15

    def test_suspicion_custom_time_window(self):
        """Test suspicion with custom time window."""
        source_claims = [{"claim_id": f"c{i}"} for i in range(12)]

        result = detect_suspicion(
            claim_id="claim-003",
            source_claims=source_claims,
            time_window_minutes=5,
        )

        assert result is not None
        assert result.metadata["window_minutes"] == 5


class TestDetectAbuse:
    """Tests for detect_abuse function."""

    def test_no_abuse_low_retracted_count(self):
        """Test no abuse with low retracted count."""
        result = detect_abuse(
            claim_id="claim-001",
            source_id="source-001",
            retracted_claims_count=1,
        )

        assert result is None

    def test_abuse_repeated_false_claims(self):
        """Test abuse detected with repeated false claims."""
        result = detect_abuse(
            claim_id="claim-002",
            source_id="source-002",
            retracted_claims_count=5,
        )

        assert result is not None
        assert result.type == SignalType.ABUSE
        assert result.severity == SignalSeverity.HIGH
        assert "retracted" in result.reason.lower()
        assert result.metadata["retracted_count"] == 5

    def test_abuse_coordinated_action(self):
        """Test abuse detected with coordinated action."""
        coordinated = [{"claim_id": f"coord-{i}"} for i in range(7)]

        result = detect_abuse(
            claim_id="claim-003",
            source_id="source-003",
            retracted_claims_count=0,
            coordinated_claims=coordinated,
        )

        assert result is not None
        assert result.type == SignalType.ABUSE
        assert result.severity == SignalSeverity.CRITICAL
        assert "coordinated" in result.reason.lower()

    def test_no_abuse_low_coordination(self):
        """Test no abuse with low coordination."""
        coordinated = [{"claim_id": f"coord-{i}"} for i in range(3)]

        result = detect_abuse(
            claim_id="claim-004",
            source_id="source-004",
            retracted_claims_count=0,
            coordinated_claims=coordinated,
        )

        assert result is None

    def test_abuse_priority_retracted_over_coordinated(self):
        """Test that retracted claims take priority over coordinated."""
        coordinated = [{"claim_id": f"coord-{i}"} for i in range(7)]

        result = detect_abuse(
            claim_id="claim-005",
            source_id="source-005",
            retracted_claims_count=5,
            coordinated_claims=coordinated,
        )

        # Should return the retracted claims signal (checked first)
        assert result is not None
        assert "retracted" in result.reason.lower()


class TestCheckNOGOSignals:
    """Tests for check_nogo_signals function."""

    def test_no_signals_clean_claim(self):
        """Test no signals for clean claim."""
        signals = check_nogo_signals(
            claim_id="claim-001",
            evidence_trail=[{"evidence_id": "e1", "stance": "supports"}],
        )

        assert len(signals) == 0

    def test_detects_inconsistency(self):
        """Test detection of inconsistency signal."""
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "refutes"},
            {"evidence_id": "e3", "stance": "refutes"},
        ]

        signals = check_nogo_signals(
            claim_id="claim-002",
            evidence_trail=evidence,
        )

        assert len(signals) == 1
        assert signals[0].type == SignalType.INCONSISTENCY

    def test_detects_suspicion(self):
        """Test detection of suspicion signal."""
        source_claims = [{"claim_id": f"c{i}"} for i in range(15)]

        signals = check_nogo_signals(
            claim_id="claim-003",
            source_claims=source_claims,
        )

        assert len(signals) == 1
        assert signals[0].type == SignalType.SUSPICION

    def test_detects_abuse(self):
        """Test detection of abuse signal."""
        signals = check_nogo_signals(
            claim_id="claim-004",
            source_id="source-bad",
            retracted_count=5,
        )

        assert len(signals) == 1
        assert signals[0].type == SignalType.ABUSE

    def test_detects_multiple_signals(self):
        """Test detection of multiple signals."""
        evidence = [
            {"evidence_id": "e1", "stance": "supports"},
            {"evidence_id": "e2", "stance": "refutes"},
            {"evidence_id": "e3", "stance": "refutes"},
        ]
        source_claims = [{"claim_id": f"c{i}"} for i in range(15)]

        signals = check_nogo_signals(
            claim_id="claim-005",
            evidence_trail=evidence,
            source_claims=source_claims,
            source_id="source-abuser",
            retracted_count=5,
        )

        assert len(signals) == 3
        signal_types = {s.type for s in signals}
        assert SignalType.INCONSISTENCY in signal_types
        assert SignalType.SUSPICION in signal_types
        assert SignalType.ABUSE in signal_types

    def test_detects_contradiction_edges(self):
        """Test detection via contradiction edges."""
        edges = [{"target_id": "other-1", "weight": 0.9}]

        signals = check_nogo_signals(
            claim_id="claim-006",
            contradiction_edges=edges,
        )

        assert len(signals) == 1
        assert signals[0].type == SignalType.INCONSISTENCY


class TestGetSignalRepository:
    """Tests for get_signal_repository singleton."""

    def test_returns_repository(self):
        """Test that it returns a repository."""
        repo = get_signal_repository()

        assert repo is not None
        assert isinstance(repo, SignalRepository)

    def test_returns_same_instance(self):
        """Test that it returns the same instance (singleton)."""
        repo1 = get_signal_repository()
        repo2 = get_signal_repository()

        assert repo1 is repo2


class TestThresholds:
    """Tests for threshold configurations."""

    def test_inconsistency_thresholds_defined(self):
        """Test inconsistency thresholds are defined."""
        assert "contradiction_weight_threshold" in INCONSISTENCY_THRESHOLDS
        assert "evidence_conflict_ratio" in INCONSISTENCY_THRESHOLDS
        assert "temporal_conflict_days" in INCONSISTENCY_THRESHOLDS

    def test_suspicion_patterns_defined(self):
        """Test suspicion patterns are defined."""
        assert "rapid_claim_threshold" in SUSPICION_PATTERNS
        assert "duplicate_ratio_threshold" in SUSPICION_PATTERNS
        assert "source_concentration_threshold" in SUSPICION_PATTERNS

    def test_abuse_patterns_defined(self):
        """Test abuse patterns are defined."""
        assert "repeated_false_claims_threshold" in ABUSE_PATTERNS
        assert "coordinated_action_threshold" in ABUSE_PATTERNS

    def test_threshold_values_reasonable(self):
        """Test threshold values are reasonable."""
        assert 0 < INCONSISTENCY_THRESHOLDS["contradiction_weight_threshold"] <= 1
        assert 0 < INCONSISTENCY_THRESHOLDS["evidence_conflict_ratio"] <= 1
        assert INCONSISTENCY_THRESHOLDS["temporal_conflict_days"] > 0

        assert SUSPICION_PATTERNS["rapid_claim_threshold"] > 0
        assert 0 < SUSPICION_PATTERNS["duplicate_ratio_threshold"] <= 1
        assert 0 < SUSPICION_PATTERNS["source_concentration_threshold"] <= 1

        assert ABUSE_PATTERNS["repeated_false_claims_threshold"] > 0
        assert ABUSE_PATTERNS["coordinated_action_threshold"] > 0
