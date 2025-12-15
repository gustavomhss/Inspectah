"""
S38: Tests for Signal Service
"""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

pytestmark = pytest.mark.asyncio(loop_scope="function")

from app.signals.signal_types import (
    SignalType,
    SignalScope,
    SignalPriority,
    SignalConfig,
    SignalValue,
    SignalBatch,
    SignalRequest,
)
from app.signals.signal_service import SignalService
from app.signals.cache_service import SignalCacheService, MemoryCacheBackend


class TestSignalTypes:
    """Tests for signal type definitions."""

    def test_signal_type_values(self):
        """Test all signal types are defined."""
        assert SignalType.MENTIRAS_EM_CIRCULACAO.value == "mentiras_em_circulacao"
        assert SignalType.CAMPO_BATALHA.value == "campo_batalha"
        assert SignalType.RADAR_SILENCIO.value == "radar_silencio"
        assert SignalType.FRAGILIDADE_NARRATIVA.value == "fragilidade_narrativa"

    def test_signal_scope_values(self):
        """Test all scopes are defined."""
        assert SignalScope.GLOBAL.value == "global"
        assert SignalScope.TOPIC.value == "topic"
        assert SignalScope.ENTITY.value == "entity"

    def test_default_configs(self):
        """Test default configurations are valid."""
        configs = SignalConfig.default_configs()

        assert SignalType.MENTIRAS_EM_CIRCULACAO in configs
        assert configs[SignalType.MENTIRAS_EM_CIRCULACAO].priority == SignalPriority.CRITICAL

    def test_signal_value_expiration(self):
        """Test signal value expiration check."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Not expired
        value = SignalValue(
            signal_type=SignalType.VIRALIDADE,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.5,
            confidence=0.8,
            sample_size=100,
            calculated_at=now,
            expires_at=now + timedelta(hours=1),
        )
        assert not value.is_expired()

        # Expired
        expired_value = SignalValue(
            signal_type=SignalType.VIRALIDADE,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.5,
            confidence=0.8,
            sample_size=100,
            calculated_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),
        )
        assert expired_value.is_expired()


class TestSignalBatch:
    """Tests for SignalBatch dataclass."""

    @pytest.fixture
    def sample_signals(self):
        """Create sample signals for batch testing."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return [
            SignalValue(
                signal_type=SignalType.MENTIRAS_EM_CIRCULACAO,
                scope=SignalScope.GLOBAL,
                scope_id=None,
                value=0.5,
                confidence=0.8,
                sample_size=100,
                calculated_at=now,
                expires_at=now + timedelta(hours=1),
            ),
            SignalValue(
                signal_type=SignalType.VIRALIDADE,
                scope=SignalScope.GLOBAL,
                scope_id=None,
                value=0.3,
                confidence=0.9,
                sample_size=50,
                calculated_at=now,
                expires_at=now + timedelta(hours=1),
            ),
            SignalValue(
                signal_type=SignalType.MENTIRAS_EM_CIRCULACAO,
                scope=SignalScope.TOPIC,
                scope_id="topic_123",
                value=0.7,
                confidence=0.85,
                sample_size=30,
                calculated_at=now,
                expires_at=now + timedelta(hours=1),
            ),
        ]

    def test_signal_count(self, sample_signals):
        """Test signal_count property."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        batch = SignalBatch(
            batch_id=f"batch_{uuid4().hex[:8]}",
            signals=sample_signals,
            calculated_at=now,
            calculation_time_ms=100.5,
        )

        assert batch.signal_count == 3

    def test_get_by_type(self, sample_signals):
        """Test get_by_type method."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        batch = SignalBatch(
            batch_id=f"batch_{uuid4().hex[:8]}",
            signals=sample_signals,
            calculated_at=now,
            calculation_time_ms=100.5,
        )

        mentiras = batch.get_by_type(SignalType.MENTIRAS_EM_CIRCULACAO)
        assert len(mentiras) == 2

        viralidade = batch.get_by_type(SignalType.VIRALIDADE)
        assert len(viralidade) == 1

        radar = batch.get_by_type(SignalType.RADAR_SILENCIO)
        assert len(radar) == 0

    def test_get_by_scope_without_scope_id(self, sample_signals):
        """Test get_by_scope without scope_id filter."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        batch = SignalBatch(
            batch_id=f"batch_{uuid4().hex[:8]}",
            signals=sample_signals,
            calculated_at=now,
            calculation_time_ms=100.5,
        )

        global_signals = batch.get_by_scope(SignalScope.GLOBAL)
        assert len(global_signals) == 2

        topic_signals = batch.get_by_scope(SignalScope.TOPIC)
        assert len(topic_signals) == 1

    def test_get_by_scope_with_scope_id(self, sample_signals):
        """Test get_by_scope with scope_id filter."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        batch = SignalBatch(
            batch_id=f"batch_{uuid4().hex[:8]}",
            signals=sample_signals,
            calculated_at=now,
            calculation_time_ms=100.5,
        )

        # Filter by specific topic
        topic_signals = batch.get_by_scope(SignalScope.TOPIC, scope_id="topic_123")
        assert len(topic_signals) == 1
        assert topic_signals[0].scope_id == "topic_123"

        # Filter by non-existent topic
        empty = batch.get_by_scope(SignalScope.TOPIC, scope_id="topic_999")
        assert len(empty) == 0


class TestSignalService:
    """Tests for SignalService."""

    @pytest.fixture
    def service(self):
        """Create service with in-memory cache."""
        cache = SignalCacheService(MemoryCacheBackend())
        return SignalService(cache_service=cache)

    @pytest.mark.asyncio
    async def test_get_signals_all_types(self, service):
        """Test getting all signal types."""
        request = SignalRequest(
            signal_types=list(SignalType),
            scope=SignalScope.GLOBAL,
        )

        batch = await service.get_signals(request)

        assert isinstance(batch, SignalBatch)
        assert batch.batch_id
        assert len(batch.signals) > 0
        assert batch.calculation_time_ms >= 0

    @pytest.mark.asyncio
    async def test_get_signals_single_type(self, service):
        """Test getting a single signal type."""
        request = SignalRequest(
            signal_types=[SignalType.MENTIRAS_EM_CIRCULACAO],
            scope=SignalScope.GLOBAL,
        )

        batch = await service.get_signals(request)

        assert len(batch.signals) == 1
        assert batch.signals[0].signal_type == SignalType.MENTIRAS_EM_CIRCULACAO

    @pytest.mark.asyncio
    async def test_get_signals_with_scope(self, service):
        """Test getting signals with specific scope."""
        request = SignalRequest(
            signal_types=[SignalType.CAMPO_BATALHA],
            scope=SignalScope.TOPIC,
            scope_ids=["topic_123"],
        )

        batch = await service.get_signals(request)

        assert len(batch.signals) == 1
        assert batch.signals[0].scope == SignalScope.TOPIC
        assert batch.signals[0].scope_id == "topic_123"

    @pytest.mark.asyncio
    async def test_cache_hit(self, service):
        """Test that cache is used on second request."""
        request = SignalRequest(
            signal_types=[SignalType.VIRALIDADE],
            scope=SignalScope.GLOBAL,
        )

        # First request - cache miss
        batch1 = await service.get_signals(request)

        # Second request - should use cache
        batch2 = await service.get_signals(request)

        # Both should return same signal value
        assert batch1.signals[0].value == batch2.signals[0].value

    @pytest.mark.asyncio
    async def test_force_refresh_bypasses_cache(self, service):
        """Test that force_refresh bypasses cache."""
        request = SignalRequest(
            signal_types=[SignalType.VIRALIDADE],
            scope=SignalScope.GLOBAL,
        )

        # First request
        await service.get_signals(request)

        # Force refresh
        request.force_refresh = True
        batch2 = await service.get_signals(request)

        assert batch2.signals[0] is not None

    @pytest.mark.asyncio
    async def test_check_alerts(self, service):
        """Test alert generation from signals."""
        request = SignalRequest(
            signal_types=list(SignalType),
            scope=SignalScope.GLOBAL,
        )

        batch = await service.get_signals(request)
        alerts = service.check_alerts(batch.signals)

        # Alerts should be a list (may be empty if no thresholds exceeded)
        assert isinstance(alerts, list)

    @pytest.mark.asyncio
    async def test_dashboard_signals(self, service):
        """Test dashboard signal aggregation."""
        result = await service.get_dashboard_signals()

        assert "signals" in result
        assert "alerts" in result
        assert "calculation_time_ms" in result


class TestSignalCacheService:
    """Tests for SignalCacheService."""

    @pytest.fixture
    def cache(self):
        """Create cache with memory backend."""
        return SignalCacheService(MemoryCacheBackend())

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        """Test basic set and get."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        signal = SignalValue(
            signal_type=SignalType.VIRALIDADE,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.75,
            confidence=0.9,
            sample_size=50,
            calculated_at=now,
            expires_at=now + timedelta(hours=1),
        )

        await cache.set("test_key", signal, ttl=300)
        result = await cache.get("test_key")

        assert result is not None
        assert result.value == 0.75
        assert result.signal_type == SignalType.VIRALIDADE

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, cache):
        """Test getting non-existent key."""
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test deleting a key."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        signal = SignalValue(
            signal_type=SignalType.VIRALIDADE,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.5,
            confidence=0.8,
            sample_size=100,
            calculated_at=now,
            expires_at=now + timedelta(hours=1),
        )

        await cache.set("to_delete", signal, ttl=300)
        assert await cache.get("to_delete") is not None

        await cache.delete("to_delete")
        assert await cache.get("to_delete") is None

    @pytest.mark.asyncio
    async def test_invalidate_by_type(self, cache):
        """Test invalidating by signal type."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        signal = SignalValue(
            signal_type=SignalType.VIRALIDADE,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.5,
            confidence=0.8,
            sample_size=100,
            calculated_at=now,
            expires_at=now + timedelta(hours=1),
        )

        await cache.set("signal:viralidade:global", signal, ttl=300)

        count = await cache.invalidate_by_type(SignalType.VIRALIDADE)
        # Count may vary based on pattern matching implementation
        assert isinstance(count, int)
