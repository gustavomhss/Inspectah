"""
S39 - Streaming Models

Dataclasses for Kafka message payloads.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SignalType(Enum):
    """Types of signals."""

    LIES_IN_CIRCULATION = "lies_in_circulation"
    BATTLEGROUND = "battleground"
    SILENCE_RADAR = "silence_radar"
    FRAGILITY = "fragility"
    CLAIM_CREATED = "claim_created"
    CLAIM_UPDATED = "claim_updated"
    EVIDENCE_ADDED = "evidence_added"
    VERDICT_CHANGED = "verdict_changed"


class SignalPriority(Enum):
    """Signal processing priority."""

    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class RawSignal:
    """
    Raw signal to be published to Kafka.

    This is the input format for signal processing.
    """

    claim_id: str
    signal_type: SignalType
    value: float
    domain: str = "default"
    components: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "signal_type": self.signal_type.value,
            "value": self.value,
            "domain": self.domain,
            "components": self.components,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RawSignal:
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid4())),
            claim_id=data["claim_id"],
            signal_type=SignalType(data["signal_type"]),
            value=data["value"],
            domain=data.get("domain", "default"),
            components=data.get("components", {}),
            metadata=data.get("metadata", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
        )

    @classmethod
    def from_json(cls, json_str: str) -> RawSignal:
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class ComputedSignal:
    """
    Computed/derived signal after processing.

    This is the output format after signal computation.
    """

    id: str
    claim_id: str
    signal_type: SignalType
    value: float
    confidence: float
    domain: str
    source_signals: List[str] = field(default_factory=list)
    reasoning: str = ""
    components: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    computed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "claim_id": self.claim_id,
            "signal_type": self.signal_type.value,
            "value": self.value,
            "confidence": self.confidence,
            "domain": self.domain,
            "source_signals": self.source_signals,
            "reasoning": self.reasoning,
            "components": self.components,
            "metadata": self.metadata,
            "computed_at": self.computed_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "version": self.version,
        }

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ComputedSignal:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            claim_id=data["claim_id"],
            signal_type=SignalType(data["signal_type"]),
            value=data["value"],
            confidence=data.get("confidence", 1.0),
            domain=data.get("domain", "default"),
            source_signals=data.get("source_signals", []),
            reasoning=data.get("reasoning", ""),
            components=data.get("components", {}),
            metadata=data.get("metadata", {}),
            computed_at=datetime.fromisoformat(data["computed_at"]) if "computed_at" in data else datetime.now(timezone.utc),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            version=data.get("version", 1),
        )

    @classmethod
    def from_json(cls, json_str: str) -> ComputedSignal:
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))


@dataclass
class SignalBatch:
    """
    Batch of signals for efficient publishing.
    """

    signals: List[RawSignal] = field(default_factory=list)
    priority: SignalPriority = SignalPriority.NORMAL
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    batch_id: str = field(default_factory=lambda: str(uuid4()))

    def add(self, signal: RawSignal) -> None:
        """Add signal to batch."""
        self.signals.append(signal)

    def __len__(self) -> int:
        return len(self.signals)

    def __iter__(self):
        return iter(self.signals)


@dataclass
class SignalEnvelope:
    """
    Message envelope for Kafka messages.

    Contains metadata for routing and processing.
    """

    topic: str
    key: str
    payload: Dict[str, Any]
    headers: Dict[str, str] = field(default_factory=dict)
    partition: Optional[int] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_kafka_message(self) -> Dict[str, Any]:
        """Convert to Kafka message format."""
        return {
            "topic": self.topic,
            "key": self.key.encode("utf-8"),
            "value": json.dumps(self.payload).encode("utf-8"),
            "headers": [(k, v.encode("utf-8")) for k, v in self.headers.items()],
            "partition": self.partition,
            "timestamp_ms": int(self.timestamp.timestamp() * 1000),
        }


# Topic constants
class Topics:
    """Kafka topic names."""

    SIGNALS_RAW = "signals.raw"
    SIGNALS_COMPUTED = "signals.computed"
    SIGNALS_DLQ = "signals.dlq"
    CLAIMS_EVENTS = "claims.events"
    EVIDENCE_EVENTS = "evidence.events"
