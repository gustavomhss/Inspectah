"""
Tests for Streaming Models.

S39 - Signal Models Tests
"""

import json
from datetime import datetime, timezone

import pytest

from app.streaming.models import (
    ComputedSignal,
    RawSignal,
    SignalBatch,
    SignalEnvelope,
    SignalPriority,
    SignalType,
    Topics,
)


class TestSignalType:
    """Tests for SignalType enum."""

    def test_signal_types_exist(self):
        """Test all signal types exist."""
        assert SignalType.LIES_IN_CIRCULATION.value == "lies_in_circulation"
        assert SignalType.BATTLEGROUND.value == "battleground"
        assert SignalType.SILENCE_RADAR.value == "silence_radar"
        assert SignalType.FRAGILITY.value == "fragility"
        assert SignalType.CLAIM_CREATED.value == "claim_created"
        assert SignalType.CLAIM_UPDATED.value == "claim_updated"
        assert SignalType.EVIDENCE_ADDED.value == "evidence_added"
        assert SignalType.VERDICT_CHANGED.value == "verdict_changed"


class TestSignalPriority:
    """Tests for SignalPriority enum."""

    def test_priority_values(self):
        """Test priority values."""
        assert SignalPriority.LOW.value == 0
        assert SignalPriority.NORMAL.value == 1
        assert SignalPriority.HIGH.value == 2
        assert SignalPriority.CRITICAL.value == 3


class TestRawSignal:
    """Tests for RawSignal dataclass."""

    def test_creation_minimal(self):
        """Test creating signal with minimal fields."""
        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.85,
        )

        assert signal.claim_id == "claim-123"
        assert signal.signal_type == SignalType.LIES_IN_CIRCULATION
        assert signal.value == 0.85
        assert signal.domain == "default"
        assert signal.components == {}
        assert signal.metadata == {}
        assert signal.id is not None
        assert signal.timestamp is not None

    def test_creation_full(self):
        """Test creating signal with all fields."""
        now = datetime.now(timezone.utc)
        signal = RawSignal(
            id="signal-456",
            claim_id="claim-123",
            signal_type=SignalType.BATTLEGROUND,
            value=0.75,
            domain="politica",
            components={"factor_a": 0.8, "factor_b": 0.7},
            metadata={"source": "test"},
            timestamp=now,
        )

        assert signal.id == "signal-456"
        assert signal.domain == "politica"
        assert signal.components["factor_a"] == 0.8
        assert signal.metadata["source"] == "test"
        assert signal.timestamp == now

    def test_to_dict(self):
        """Test conversion to dictionary."""
        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        d = signal.to_dict()

        assert d["claim_id"] == "claim-123"
        assert d["signal_type"] == "fragility"
        assert d["value"] == 0.5
        assert "timestamp" in d
        assert "id" in d

    def test_to_json(self):
        """Test JSON serialization."""
        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.SILENCE_RADAR,
            value=0.9,
        )

        json_str = signal.to_json()
        parsed = json.loads(json_str)

        assert parsed["claim_id"] == "claim-123"
        assert parsed["signal_type"] == "silence_radar"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "id": "signal-789",
            "claim_id": "claim-456",
            "signal_type": "battleground",
            "value": 0.65,
            "domain": "economia",
            "timestamp": "2024-01-01T12:00:00+00:00",
        }

        signal = RawSignal.from_dict(data)

        assert signal.id == "signal-789"
        assert signal.claim_id == "claim-456"
        assert signal.signal_type == SignalType.BATTLEGROUND
        assert signal.value == 0.65
        assert signal.domain == "economia"

    def test_from_json(self):
        """Test deserialization from JSON."""
        json_str = json.dumps({
            "claim_id": "claim-test",
            "signal_type": "fragility",
            "value": 0.33,
            "timestamp": "2024-01-01T00:00:00+00:00",
        })

        signal = RawSignal.from_json(json_str)

        assert signal.claim_id == "claim-test"
        assert signal.signal_type == SignalType.FRAGILITY
        assert signal.value == 0.33

    def test_roundtrip(self):
        """Test serialization roundtrip."""
        original = RawSignal(
            claim_id="claim-roundtrip",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.99,
            domain="saude",
            components={"x": 1, "y": 2},
            metadata={"test": True},
        )

        restored = RawSignal.from_json(original.to_json())

        assert restored.claim_id == original.claim_id
        assert restored.signal_type == original.signal_type
        assert restored.value == original.value
        assert restored.domain == original.domain
        assert restored.components == original.components
        assert restored.metadata == original.metadata


class TestComputedSignal:
    """Tests for ComputedSignal dataclass."""

    def test_creation_minimal(self):
        """Test creating computed signal with minimal fields."""
        signal = ComputedSignal(
            id="computed-123",
            claim_id="claim-456",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.85,
            confidence=0.9,
            domain="default",
        )

        assert signal.id == "computed-123"
        assert signal.claim_id == "claim-456"
        assert signal.value == 0.85
        assert signal.confidence == 0.9
        assert signal.version == 1
        assert signal.source_signals == []

    def test_creation_full(self):
        """Test creating computed signal with all fields."""
        now = datetime.now(timezone.utc)
        signal = ComputedSignal(
            id="computed-456",
            claim_id="claim-789",
            signal_type=SignalType.BATTLEGROUND,
            value=0.75,
            confidence=0.95,
            domain="politica",
            source_signals=["raw-1", "raw-2"],
            reasoning="High engagement detected",
            components={"engagement": 0.8},
            metadata={"version": "v2"},
            computed_at=now,
            expires_at=now,
            version=2,
        )

        assert signal.source_signals == ["raw-1", "raw-2"]
        assert signal.reasoning == "High engagement detected"
        assert signal.version == 2

    def test_to_dict(self):
        """Test conversion to dictionary."""
        signal = ComputedSignal(
            id="computed-test",
            claim_id="claim-test",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
            confidence=0.8,
            domain="default",
        )

        d = signal.to_dict()

        assert d["id"] == "computed-test"
        assert d["signal_type"] == "fragility"
        assert d["confidence"] == 0.8

    def test_to_json(self):
        """Test JSON serialization."""
        signal = ComputedSignal(
            id="computed-json",
            claim_id="claim-json",
            signal_type=SignalType.SILENCE_RADAR,
            value=0.9,
            confidence=0.85,
            domain="economia",
        )

        json_str = signal.to_json()
        parsed = json.loads(json_str)

        assert parsed["id"] == "computed-json"
        assert parsed["confidence"] == 0.85

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "id": "computed-from-dict",
            "claim_id": "claim-456",
            "signal_type": "battleground",
            "value": 0.65,
            "confidence": 0.9,
            "domain": "economia",
            "computed_at": "2024-01-01T12:00:00+00:00",
        }

        signal = ComputedSignal.from_dict(data)

        assert signal.id == "computed-from-dict"
        assert signal.confidence == 0.9

    def test_from_json(self):
        """Test deserialization from JSON."""
        json_str = json.dumps({
            "id": "computed-json-test",
            "claim_id": "claim-test",
            "signal_type": "fragility",
            "value": 0.33,
            "confidence": 0.77,
            "domain": "default",
            "computed_at": "2024-01-01T00:00:00+00:00",
        })

        signal = ComputedSignal.from_json(json_str)

        assert signal.id == "computed-json-test"
        assert signal.confidence == 0.77

    def test_with_expires_at(self):
        """Test signal with expiration."""
        now = datetime.now(timezone.utc)
        signal = ComputedSignal(
            id="computed-expires",
            claim_id="claim-test",
            signal_type=SignalType.LIES_IN_CIRCULATION,
            value=0.5,
            confidence=0.8,
            domain="default",
            expires_at=now,
        )

        d = signal.to_dict()
        assert d["expires_at"] is not None

        restored = ComputedSignal.from_dict(d)
        assert restored.expires_at is not None


class TestSignalBatch:
    """Tests for SignalBatch dataclass."""

    def test_creation_empty(self):
        """Test creating empty batch."""
        batch = SignalBatch()

        assert len(batch) == 0
        assert batch.priority == SignalPriority.NORMAL
        assert batch.batch_id is not None

    def test_add_signal(self):
        """Test adding signals to batch."""
        batch = SignalBatch()
        signal = RawSignal(
            claim_id="claim-123",
            signal_type=SignalType.FRAGILITY,
            value=0.5,
        )

        batch.add(signal)

        assert len(batch) == 1
        assert batch.signals[0] == signal

    def test_iteration(self):
        """Test iterating over batch."""
        batch = SignalBatch()
        for i in range(3):
            batch.add(RawSignal(
                claim_id=f"claim-{i}",
                signal_type=SignalType.BATTLEGROUND,
                value=i * 0.1,
            ))

        count = 0
        for signal in batch:
            count += 1

        assert count == 3

    def test_with_priority(self):
        """Test batch with custom priority."""
        batch = SignalBatch(priority=SignalPriority.HIGH)

        assert batch.priority == SignalPriority.HIGH


class TestSignalEnvelope:
    """Tests for SignalEnvelope dataclass."""

    def test_creation(self):
        """Test creating envelope."""
        envelope = SignalEnvelope(
            topic="signals.raw",
            key="claim-123",
            payload={"test": "data"},
        )

        assert envelope.topic == "signals.raw"
        assert envelope.key == "claim-123"
        assert envelope.payload == {"test": "data"}
        assert envelope.partition is None

    def test_with_headers(self):
        """Test envelope with headers."""
        envelope = SignalEnvelope(
            topic="signals.raw",
            key="claim-123",
            payload={"test": "data"},
            headers={"signal_type": "fragility", "domain": "default"},
        )

        assert envelope.headers["signal_type"] == "fragility"

    def test_with_partition(self):
        """Test envelope with specific partition."""
        envelope = SignalEnvelope(
            topic="signals.raw",
            key="claim-123",
            payload={"test": "data"},
            partition=2,
        )

        assert envelope.partition == 2

    def test_to_kafka_message(self):
        """Test conversion to Kafka message format."""
        envelope = SignalEnvelope(
            topic="signals.raw",
            key="claim-123",
            payload={"test": "data"},
            headers={"type": "test"},
        )

        msg = envelope.to_kafka_message()

        assert msg["topic"] == "signals.raw"
        assert msg["key"] == b"claim-123"
        assert b"test" in msg["value"]
        assert ("type", b"test") in msg["headers"]


class TestTopics:
    """Tests for Topics constants."""

    def test_topic_names(self):
        """Test topic names."""
        assert Topics.SIGNALS_RAW == "signals.raw"
        assert Topics.SIGNALS_COMPUTED == "signals.computed"
        assert Topics.SIGNALS_DLQ == "signals.dlq"
        assert Topics.CLAIMS_EVENTS == "claims.events"
        assert Topics.EVIDENCE_EVENTS == "evidence.events"
