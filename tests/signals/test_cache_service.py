"""
S38: Tests for Signal Cache Service - 100% coverage
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.signals.cache_service import (
    CacheBackend,
    MemoryCacheBackend,
    RedisCacheBackend,
    SignalCacheService,
    CacheStats,
    InstrumentedCacheService,
)
from app.signals.signal_types import SignalScope, SignalType, SignalValue


class TestMemoryCacheBackend:
    """Tests for MemoryCacheBackend."""

    @pytest.fixture
    def backend(self):
        return MemoryCacheBackend()

    @pytest.mark.asyncio
    async def test_set_and_get(self, backend):
        await backend.set("key1", "value1", ttl=300)
        result = await backend.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, backend):
        result = await backend.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_expired(self, backend):
        await backend.set("key1", "value1", ttl=1)
        # Manually expire it
        backend._cache["key1"] = ("value1", datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=10))
        result = await backend.get("key1")
        assert result is None
        assert "key1" not in backend._cache

    @pytest.mark.asyncio
    async def test_delete_existing(self, backend):
        await backend.set("key1", "value1", ttl=300)
        result = await backend.delete("key1")
        assert result is True
        assert await backend.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, backend):
        result = await backend.delete("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_pattern(self, backend):
        await backend.set("signal:type1:scope1", "v1", ttl=300)
        await backend.set("signal:type1:scope2", "v2", ttl=300)
        await backend.set("other:key", "v3", ttl=300)

        deleted = await backend.delete_pattern("signal:type1:*")
        assert deleted == 2
        assert await backend.get("other:key") == "v3"

    @pytest.mark.asyncio
    async def test_exists_true(self, backend):
        await backend.set("key1", "value1", ttl=300)
        result = await backend.exists("key1")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, backend):
        result = await backend.exists("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_expired(self, backend):
        await backend.set("key1", "value1", ttl=1)
        backend._cache["key1"] = ("value1", datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=10))
        result = await backend.exists("key1")
        assert result is False


class TestRedisCacheBackend:
    """Tests for RedisCacheBackend with mocked Redis."""

    @pytest.fixture
    def mock_redis(self):
        redis = AsyncMock()
        return redis

    @pytest.fixture
    def backend(self, mock_redis):
        return RedisCacheBackend(mock_redis)

    @pytest.mark.asyncio
    async def test_get_success(self, backend, mock_redis):
        mock_redis.get.return_value = "value1"
        result = await backend.get("key1")
        assert result == "value1"
        mock_redis.get.assert_called_once_with("key1")

    @pytest.mark.asyncio
    async def test_get_error(self, backend, mock_redis):
        mock_redis.get.side_effect = Exception("Redis error")
        result = await backend.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_success(self, backend, mock_redis):
        mock_redis.setex.return_value = True
        result = await backend.set("key1", "value1", 300)
        assert result is True
        mock_redis.setex.assert_called_once_with("key1", 300, "value1")

    @pytest.mark.asyncio
    async def test_set_error(self, backend, mock_redis):
        mock_redis.setex.side_effect = Exception("Redis error")
        result = await backend.set("key1", "value1", 300)
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self, backend, mock_redis):
        mock_redis.delete.return_value = 1
        result = await backend.delete("key1")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, backend, mock_redis):
        mock_redis.delete.return_value = 0
        result = await backend.delete("key1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_error(self, backend, mock_redis):
        mock_redis.delete.side_effect = Exception("Redis error")
        result = await backend.delete("key1")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_pattern_success(self, backend, mock_redis):
        async def mock_scan_iter(match):
            for key in ["key1", "key2"]:
                yield key

        mock_redis.scan_iter = mock_scan_iter
        mock_redis.delete.return_value = 2

        result = await backend.delete_pattern("key*")
        assert result == 2

    @pytest.mark.asyncio
    async def test_delete_pattern_no_keys(self, backend, mock_redis):
        async def mock_scan_iter(match):
            return
            yield  # Empty generator

        mock_redis.scan_iter = mock_scan_iter
        result = await backend.delete_pattern("nonexistent*")
        assert result == 0

    @pytest.mark.asyncio
    async def test_delete_pattern_error(self, backend, mock_redis):
        async def mock_scan_iter(match):
            raise Exception("Redis error")
            yield

        mock_redis.scan_iter = mock_scan_iter
        result = await backend.delete_pattern("key*")
        assert result == 0

    @pytest.mark.asyncio
    async def test_exists_true(self, backend, mock_redis):
        mock_redis.exists.return_value = 1
        result = await backend.exists("key1")
        assert result is True

    @pytest.mark.asyncio
    async def test_exists_false(self, backend, mock_redis):
        mock_redis.exists.return_value = 0
        result = await backend.exists("key1")
        assert result is False

    @pytest.mark.asyncio
    async def test_exists_error(self, backend, mock_redis):
        mock_redis.exists.side_effect = Exception("Redis error")
        result = await backend.exists("key1")
        assert result is False


class TestSignalCacheService:
    """Tests for SignalCacheService."""

    @pytest.fixture
    def service(self):
        return SignalCacheService()

    @pytest.fixture
    def sample_signal(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return SignalValue(
            signal_type=SignalType.MENTIRAS_EM_CIRCULACAO,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.75,
            confidence=0.9,
            sample_size=100,
            calculated_at=now,
            expires_at=now + timedelta(hours=1),
            metadata={"test": True},
        )

    def test_full_key_without_prefix(self, service):
        result = service._full_key("mykey")
        assert result == "inspectah:signal:mykey"

    def test_full_key_with_prefix(self, service):
        result = service._full_key("inspectah:signal:mykey")
        assert result == "inspectah:signal:mykey"

    @pytest.mark.asyncio
    async def test_set_and_get(self, service, sample_signal):
        await service.set("test_signal", sample_signal, ttl=300)
        result = await service.get("test_signal")

        assert result is not None
        assert result.signal_type == sample_signal.signal_type
        assert result.value == sample_signal.value

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, service):
        result = await service.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_invalid_data(self, service):
        # Put invalid JSON directly
        await service.backend.set(
            service._full_key("bad_signal"),
            "not valid json",
            ttl=300
        )
        result = await service.get("bad_signal")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_serialization_error(self, service):
        # Create a signal that can't be serialized properly
        with patch.object(service, '_serialize', side_effect=TypeError("Serialize error")):
            result = await service.set("key", MagicMock(), ttl=300)
            assert result is False

    @pytest.mark.asyncio
    async def test_delete(self, service, sample_signal):
        await service.set("to_delete", sample_signal, ttl=300)
        result = await service.delete("to_delete")
        assert result is True
        assert await service.get("to_delete") is None

    @pytest.mark.asyncio
    async def test_invalidate_by_type(self, service, sample_signal):
        await service.set("signal:mentiras_em_circulacao:global:1", sample_signal, ttl=300)
        result = await service.invalidate_by_type(SignalType.MENTIRAS_EM_CIRCULACAO)
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_by_scope_with_id(self, service, sample_signal):
        await service.set("signal:test:entity:123", sample_signal, ttl=300)
        result = await service.invalidate_by_scope(SignalScope.ENTITY, "123")
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_by_scope_without_id(self, service, sample_signal):
        result = await service.invalidate_by_scope(SignalScope.GLOBAL)
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_invalidate_all(self, service, sample_signal):
        await service.set("key1", sample_signal, ttl=300)
        await service.set("key2", sample_signal, ttl=300)
        result = await service.invalidate_all()
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_get_many(self, service, sample_signal):
        await service.set("key1", sample_signal, ttl=300)
        await service.set("key2", sample_signal, ttl=300)

        results = await service.get_many(["key1", "key2", "key3"])
        assert results["key1"] is not None
        assert results["key2"] is not None
        assert results["key3"] is None

    @pytest.mark.asyncio
    async def test_set_many(self, service, sample_signal):
        signals = {
            "key1": sample_signal,
            "key2": sample_signal,
        }
        results = await service.set_many(signals, ttl=300)
        assert results["key1"] is True
        assert results["key2"] is True

    def test_serialize_deserialize(self, service, sample_signal):
        serialized = service._serialize(sample_signal)
        deserialized = service._deserialize(serialized)

        assert deserialized.signal_type == sample_signal.signal_type
        assert deserialized.scope == sample_signal.scope
        assert deserialized.value == sample_signal.value
        assert deserialized.confidence == sample_signal.confidence


class TestCacheStats:
    """Tests for CacheStats."""

    def test_initial_values(self):
        stats = CacheStats()
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.sets == 0
        assert stats.deletes == 0

    def test_hit_rate_zero_total(self):
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_hit_rate_calculation(self):
        stats = CacheStats()
        stats.hits = 80
        stats.misses = 20
        assert stats.hit_rate == 0.8

    def test_to_dict(self):
        stats = CacheStats()
        stats.hits = 10
        stats.misses = 5
        stats.sets = 15
        stats.deletes = 3

        result = stats.to_dict()
        assert result["hits"] == 10
        assert result["misses"] == 5
        assert result["sets"] == 15
        assert result["deletes"] == 3
        assert "hit_rate" in result


class TestInstrumentedCacheService:
    """Tests for InstrumentedCacheService."""

    @pytest.fixture
    def service(self):
        return InstrumentedCacheService()

    @pytest.fixture
    def sample_signal(self):
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        return SignalValue(
            signal_type=SignalType.MENTIRAS_EM_CIRCULACAO,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            value=0.75,
            confidence=0.9,
            sample_size=100,
            calculated_at=now,
            expires_at=now + timedelta(hours=1),
            metadata={},
        )

    @pytest.mark.asyncio
    async def test_get_hit_increments_stats(self, service, sample_signal):
        await service.set("key1", sample_signal, ttl=300)
        await service.get("key1")

        assert service.stats.hits == 1
        assert service.stats.misses == 0

    @pytest.mark.asyncio
    async def test_get_miss_increments_stats(self, service):
        await service.get("nonexistent")

        assert service.stats.hits == 0
        assert service.stats.misses == 1

    @pytest.mark.asyncio
    async def test_set_increments_stats(self, service, sample_signal):
        await service.set("key1", sample_signal, ttl=300)
        assert service.stats.sets == 1

    @pytest.mark.asyncio
    async def test_delete_increments_stats(self, service, sample_signal):
        await service.set("key1", sample_signal, ttl=300)
        await service.delete("key1")
        assert service.stats.deletes == 1

    @pytest.mark.asyncio
    async def test_delete_not_found_no_increment(self, service):
        await service.delete("nonexistent")
        assert service.stats.deletes == 0

    def test_get_stats(self, service):
        service.stats.hits = 10
        service.stats.misses = 5

        result = service.get_stats()
        assert result["hits"] == 10
        assert result["misses"] == 5
        assert "hit_rate" in result
