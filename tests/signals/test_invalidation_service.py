"""
S38: Tests for Cache Invalidation Service - 100% coverage
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.signals.invalidation_service import (
    EventType,
    InvalidationEvent,
    InvalidationStrategy,
    TypeBasedStrategy,
    ScopeBasedStrategy,
    CacheInvalidationService,
    SignalEventHandler,
    EVENT_SIGNAL_MAPPING,
)
from app.signals.cache_service import SignalCacheService, MemoryCacheBackend
from app.signals.signal_types import SignalScope, SignalType


class TestEventType:
    """Tests for EventType enum."""

    def test_event_type_values(self):
        assert EventType.CLAIM_CREATED.value == "claim_created"
        assert EventType.CLAIM_UPDATED.value == "claim_updated"
        assert EventType.CLAIM_VERDICT_CHANGED.value == "claim_verdict_changed"
        assert EventType.CLAIM_DELETED.value == "claim_deleted"
        assert EventType.SOURCE_HEALTH_CHANGED.value == "source_health_changed"
        assert EventType.SOURCE_INGESTION_COMPLETE.value == "source_ingestion_complete"
        assert EventType.ENTITY_MERGED.value == "entity_merged"
        assert EventType.RELATION_CREATED.value == "relation_created"
        assert EventType.RELATION_DELETED.value == "relation_deleted"
        assert EventType.POLICY_UPDATED.value == "policy_updated"
        assert EventType.MANUAL_INVALIDATION.value == "manual_invalidation"


class TestInvalidationEvent:
    """Tests for InvalidationEvent dataclass."""

    def test_create_event(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            scope_id="claim_001",
        )

        assert event.event_type == EventType.CLAIM_CREATED
        assert event.scope == SignalScope.CLAIM
        assert event.scope_id == "claim_001"

    def test_create_event_with_affected_types(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            affected_types=[SignalType.MENTIRAS_EM_CIRCULACAO],
        )

        assert len(event.affected_types) == 1

    def test_create_event_metadata_default(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
        )

        # __post_init__ should set metadata to {}
        assert event.metadata == {}

    def test_create_event_with_metadata(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            metadata={"key": "value"},
        )

        assert event.metadata["key"] == "value"


class TestEventSignalMapping:
    """Tests for EVENT_SIGNAL_MAPPING."""

    def test_claim_created_mapping(self):
        signals = EVENT_SIGNAL_MAPPING[EventType.CLAIM_CREATED]
        assert SignalType.MENTIRAS_EM_CIRCULACAO in signals
        assert SignalType.VIRALIDADE in signals
        assert SignalType.CAMPO_BATALHA in signals

    def test_policy_updated_invalidates_all(self):
        signals = EVENT_SIGNAL_MAPPING[EventType.POLICY_UPDATED]
        assert len(signals) == len(SignalType)

    def test_manual_invalidation_invalidates_all(self):
        signals = EVENT_SIGNAL_MAPPING[EventType.MANUAL_INVALIDATION]
        assert len(signals) == len(SignalType)


class TestTypeBasedStrategy:
    """Tests for TypeBasedStrategy."""

    @pytest.fixture
    def strategy(self):
        return TypeBasedStrategy()

    @pytest.fixture
    def cache(self):
        return SignalCacheService()

    def test_get_keys_with_scope_id(self, strategy, cache):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            scope_id="claim_123",
        )

        keys = strategy.get_keys_to_invalidate(event, cache)
        assert len(keys) > 0
        assert all("claim_123" in k for k in keys)

    def test_get_keys_without_scope_id(self, strategy, cache):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.GLOBAL,
        )

        keys = strategy.get_keys_to_invalidate(event, cache)
        assert len(keys) > 0
        assert all("*" in k for k in keys)

    def test_get_keys_with_explicit_affected_types(self, strategy, cache):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            scope_id="claim_123",
            affected_types=[SignalType.MENTIRAS_EM_CIRCULACAO],
        )

        keys = strategy.get_keys_to_invalidate(event, cache)
        assert len(keys) == 1


class TestScopeBasedStrategy:
    """Tests for ScopeBasedStrategy."""

    @pytest.fixture
    def strategy(self):
        return ScopeBasedStrategy()

    @pytest.fixture
    def cache(self):
        return SignalCacheService()

    def test_get_keys_with_scope_id(self, strategy, cache):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.ENTITY,
            scope_id="entity_123",
        )

        keys = strategy.get_keys_to_invalidate(event, cache)
        assert len(keys) == 1
        assert "entity_123" in keys[0]

    def test_get_keys_without_scope_id(self, strategy, cache):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.GLOBAL,
        )

        keys = strategy.get_keys_to_invalidate(event, cache)
        assert len(keys) == 1
        assert "*" in keys[0]


class TestCacheInvalidationService:
    """Tests for CacheInvalidationService."""

    @pytest.fixture
    def cache(self):
        return SignalCacheService()

    @pytest.fixture
    def service(self, cache):
        return CacheInvalidationService(cache)

    @pytest.mark.asyncio
    async def test_process_event(self, service):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            scope_id="claim_001",
        )

        result = await service.process_event(event)
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_register_and_run_handler(self, service):
        handler_called = []

        def my_handler(event):
            handler_called.append(event)

        service.register_handler(EventType.CLAIM_CREATED, my_handler)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
        )

        await service.process_event(event)
        assert len(handler_called) == 1

    @pytest.mark.asyncio
    async def test_run_async_handler(self, service):
        handler_called = []

        async def async_handler(event):
            handler_called.append(event)

        service.register_handler(EventType.CLAIM_CREATED, async_handler)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
        )

        await service.process_event(event)
        assert len(handler_called) == 1

    @pytest.mark.asyncio
    async def test_handler_error_caught(self, service):
        def failing_handler(event):
            raise Exception("Handler error")

        service.register_handler(EventType.CLAIM_CREATED, failing_handler)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
        )

        # Should not raise
        await service.process_event(event)

    @pytest.mark.asyncio
    async def test_invalidate_pattern_based(self, service):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.MANUAL_INVALIDATION,
            timestamp=now,
            scope=SignalScope.GLOBAL,
        )

        # With patterns (wildcard)
        result = await service._invalidate(event)
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_exact_key(self, service, cache):
        # Use scope-based strategy to get exact keys
        service.strategy = ScopeBasedStrategy()

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
            scope_id="claim_exact",
            affected_types=[SignalType.MENTIRAS_EM_CIRCULACAO],
        )

        # This will try exact key deletion
        result = await service._invalidate(event)
        assert isinstance(result, int)

    def test_log_event(self, service):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        event = InvalidationEvent(
            event_type=EventType.CLAIM_CREATED,
            timestamp=now,
            scope=SignalScope.CLAIM,
        )

        service._log_event(event)
        assert len(service._event_log) == 1

    def test_log_event_max_size(self, service):
        service._max_log_size = 5

        for i in range(10):
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            event = InvalidationEvent(
                event_type=EventType.CLAIM_CREATED,
                timestamp=now,
                scope=SignalScope.CLAIM,
            )
            service._log_event(event)

        assert len(service._event_log) == 5

    @pytest.mark.asyncio
    async def test_invalidate_for_claim(self, service):
        result = await service.invalidate_for_claim("claim_001")
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_for_claim_with_topic(self, service):
        result = await service.invalidate_for_claim("claim_001", topic_id="topic_001")
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_for_source(self, service):
        result = await service.invalidate_for_source("source_001")
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_all(self, service):
        result = await service.invalidate_all()
        assert isinstance(result, int)

    def test_get_recent_events(self, service):
        for i in range(5):
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            event = InvalidationEvent(
                event_type=EventType.CLAIM_CREATED,
                timestamp=now,
                scope=SignalScope.CLAIM,
                scope_id=f"claim_{i}",
            )
            service._log_event(event)

        recent = service.get_recent_events(limit=3)
        assert len(recent) == 3
        assert "event_type" in recent[0]
        assert "timestamp" in recent[0]
        assert "scope" in recent[0]

    def test_custom_strategy(self, cache):
        custom_strategy = ScopeBasedStrategy()
        service = CacheInvalidationService(cache, strategy=custom_strategy)
        assert service.strategy is custom_strategy


class TestSignalEventHandler:
    """Tests for SignalEventHandler."""

    @pytest.fixture
    def cache(self):
        return SignalCacheService()

    @pytest.fixture
    def invalidation_service(self, cache):
        return CacheInvalidationService(cache)

    @pytest.fixture
    def handler(self, invalidation_service):
        return SignalEventHandler(invalidation_service)

    @pytest.mark.asyncio
    async def test_on_claim_created(self, handler):
        await handler.on_claim_created(
            claim_id="claim_001",
            verdict="false",
            topic_id="topic_001",
        )
        # Should not raise

    @pytest.mark.asyncio
    async def test_on_claim_created_minimal(self, handler):
        await handler.on_claim_created(claim_id="claim_001")
        # Should not raise

    @pytest.mark.asyncio
    async def test_on_claim_verdict_changed(self, handler):
        await handler.on_claim_verdict_changed(
            claim_id="claim_001",
            old_verdict="unknown",
            new_verdict="false",
        )
        # Should not raise

    @pytest.mark.asyncio
    async def test_on_source_ingestion_complete(self, handler):
        await handler.on_source_ingestion_complete(
            source_id="source_001",
            documents_count=100,
        )
        # Should not raise

    @pytest.mark.asyncio
    async def test_on_relation_created(self, handler):
        await handler.on_relation_created(
            source_claim_id="claim_001",
            target_claim_id="claim_002",
            relation_type="contradicts",
        )
        # Should not raise
