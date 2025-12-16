"""
Tests for LLM Fallback Handler.

S39 - Fallback Strategy Tests
"""
import time
from unittest.mock import MagicMock, patch

import pytest

from app.llm.fallback import (
    FallbackReason,
    FallbackStrategy,
    FallbackResult,
    FallbackConfig,
    FallbackStats,
    FallbackHandler,
    ResponseCache,
    CachedResponse,
    get_fallback_handler,
    reset_fallback_handler,
)


class TestFallbackEnums:
    """Tests for fallback enums."""

    def test_fallback_reason_values(self):
        """Test FallbackReason enum values."""
        assert FallbackReason.CIRCUIT_OPEN.value == "circuit_open"
        assert FallbackReason.QUOTA_EXCEEDED.value == "quota_exceeded"
        assert FallbackReason.TIMEOUT.value == "timeout"
        assert FallbackReason.RATE_LIMITED.value == "rate_limited"
        assert FallbackReason.API_ERROR.value == "api_error"
        assert FallbackReason.MODEL_UNAVAILABLE.value == "model_unavailable"
        assert FallbackReason.VALIDATION_ERROR.value == "validation_error"

    def test_fallback_strategy_values(self):
        """Test FallbackStrategy enum values."""
        assert FallbackStrategy.MODEL_DOWNGRADE.value == "model_downgrade"
        assert FallbackStrategy.CACHED_RESPONSE.value == "cached_response"
        assert FallbackStrategy.DEGRADED_RESPONSE.value == "degraded_response"
        assert FallbackStrategy.RETRY_LATER.value == "retry_later"
        assert FallbackStrategy.FAIL_FAST.value == "fail_fast"


class TestFallbackResult:
    """Tests for FallbackResult dataclass."""

    def test_create_result(self):
        """Test creating fallback result."""
        result = FallbackResult(
            success=True,
            strategy_used=FallbackStrategy.MODEL_DOWNGRADE,
            reason=FallbackReason.CIRCUIT_OPEN,
            response="Fallback response",
            original_model="gpt-4",
            fallback_model="gpt-3.5-turbo",
        )

        assert result.success
        assert result.strategy_used == FallbackStrategy.MODEL_DOWNGRADE
        assert result.response == "Fallback response"
        assert result.fallback_model == "gpt-3.5-turbo"

    def test_to_dict(self):
        """Test converting result to dict."""
        result = FallbackResult(
            success=True,
            strategy_used=FallbackStrategy.CACHED_RESPONSE,
            reason=FallbackReason.QUOTA_EXCEEDED,
            response="Cached response",
            original_model="gpt-4",
            from_cache=True,
            latency_ms=5.0,
        )

        d = result.to_dict()

        assert d["success"] is True
        assert d["strategy_used"] == "cached_response"
        assert d["reason"] == "quota_exceeded"
        assert d["from_cache"] is True
        assert d["latency_ms"] == 5.0


class TestCachedResponse:
    """Tests for CachedResponse dataclass."""

    def test_create_cached_response(self):
        """Test creating cached response."""
        cached = CachedResponse(
            cache_key="abc123",
            prompt_hash="def456",
            model="gpt-4",
            response="Cached content",
            created_at=time.time(),
            ttl_seconds=3600,
        )

        assert cached.cache_key == "abc123"
        assert cached.response == "Cached content"
        assert not cached.is_expired

    def test_is_expired(self):
        """Test expiration check."""
        cached = CachedResponse(
            cache_key="abc123",
            prompt_hash="def456",
            model="gpt-4",
            response="Cached content",
            created_at=time.time() - 7200,  # 2 hours ago
            ttl_seconds=3600,  # 1 hour TTL
        )

        assert cached.is_expired


class TestResponseCache:
    """Tests for ResponseCache."""

    @pytest.fixture
    def cache(self):
        """Create fresh cache."""
        return ResponseCache(max_size=10, default_ttl=3600)

    def test_create_cache(self, cache):
        """Test creating cache."""
        assert cache.size() == 0

    def test_put_and_get(self, cache):
        """Test putting and getting from cache."""
        cache.put("What is AI?", "gpt-4", "AI is...")

        cached = cache.get("What is AI?", "gpt-4")

        assert cached is not None
        assert cached.response == "AI is..."

    def test_get_miss(self, cache):
        """Test cache miss."""
        cached = cache.get("Unknown prompt", "gpt-4")
        assert cached is None

    def test_get_different_model(self, cache):
        """Test cache miss for different model."""
        cache.put("What is AI?", "gpt-4", "AI is...")

        cached = cache.get("What is AI?", "gpt-3.5-turbo")
        assert cached is None

    def test_get_expired(self, cache):
        """Test getting expired entry returns None."""
        # Create cache with very short TTL
        short_cache = ResponseCache(max_size=10, default_ttl=1)

        start_time = time.time()
        with patch('time.time', return_value=start_time):
            short_cache.put("prompt", "model", "response")

        # Simulate time passing past TTL
        with patch('time.time', return_value=start_time + 1.5):
            cached = short_cache.get("prompt", "model")
            assert cached is None

    def test_hit_count(self, cache):
        """Test hit count increments."""
        cache.put("prompt", "model", "response")

        cache.get("prompt", "model")
        cache.get("prompt", "model")
        cached = cache.get("prompt", "model")

        assert cached.hit_count == 3

    def test_invalidate(self, cache):
        """Test invalidating cache entry."""
        key = cache.put("prompt", "model", "response")

        result = cache.invalidate(key)

        assert result is True
        assert cache.get("prompt", "model") is None

    def test_invalidate_nonexistent(self, cache):
        """Test invalidating nonexistent entry."""
        result = cache.invalidate("nonexistent")
        assert result is False

    def test_clear(self, cache):
        """Test clearing cache."""
        cache.put("prompt1", "model", "response1")
        cache.put("prompt2", "model", "response2")

        count = cache.clear()

        assert count == 2
        assert cache.size() == 0

    def test_lru_eviction(self, cache):
        """Test LRU eviction when at capacity."""
        small_cache = ResponseCache(max_size=3)

        small_cache.put("prompt1", "model", "response1")
        small_cache.put("prompt2", "model", "response2")
        small_cache.put("prompt3", "model", "response3")

        # Access prompt1 to make it recently used
        small_cache.get("prompt1", "model")

        # Add new entry, should evict prompt2 (least recently used)
        small_cache.put("prompt4", "model", "response4")

        assert small_cache.get("prompt1", "model") is not None
        assert small_cache.get("prompt2", "model") is None
        assert small_cache.get("prompt3", "model") is not None
        assert small_cache.get("prompt4", "model") is not None

    def test_cleanup_expired(self, cache):
        """Test cleaning up expired entries."""
        short_cache = ResponseCache(max_size=10, default_ttl=1)

        start_time = time.time()
        with patch('time.time', return_value=start_time):
            short_cache.put("prompt1", "model", "response1")
            short_cache.put("prompt2", "model", "response2", ttl=3600)  # Long TTL

        # Simulate time passing past short TTL but not long TTL
        with patch('time.time', return_value=start_time + 1.5):
            count = short_cache.cleanup_expired()

            assert count == 1
            assert short_cache.get("prompt2", "model") is not None


class TestFallbackConfig:
    """Tests for FallbackConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = FallbackConfig()

        assert config.enabled is True
        assert FallbackStrategy.MODEL_DOWNGRADE in config.strategies
        assert config.cache_ttl_seconds == 3600
        assert "gpt-4" in config.model_fallback_chain

    def test_custom_config(self):
        """Test custom configuration."""
        config = FallbackConfig(
            enabled=False,
            strategies=[FallbackStrategy.CACHED_RESPONSE],
            cache_ttl_seconds=1800,
        )

        assert config.enabled is False
        assert len(config.strategies) == 1


class TestFallbackHandler:
    """Tests for FallbackHandler."""

    @pytest.fixture
    def handler(self):
        """Create fresh handler."""
        return FallbackHandler()

    def test_create_handler(self, handler):
        """Test creating handler."""
        assert handler is not None
        assert handler.config.enabled is True

    def test_configure(self, handler):
        """Test configuring handler."""
        new_config = FallbackConfig(enabled=False)
        handler.configure(new_config)

        assert handler.config.enabled is False

    def test_register_degraded_response(self, handler):
        """Test registering degraded response."""
        handler.register_degraded_response("default", lambda: "Default response")

        assert "default" in handler._degraded_responses

    def test_handle_fallback_disabled(self, handler):
        """Test fallback when disabled."""
        handler.configure(FallbackConfig(enabled=False))

        result = handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test prompt",
        )

        assert result.success is False
        assert result.strategy_used == FallbackStrategy.FAIL_FAST

    def test_handle_fallback_model_downgrade(self, handler):
        """Test model downgrade fallback."""
        def mock_call(model, prompt):
            if model == "gpt-3.5-turbo":
                return "Fallback response"
            raise Exception("Primary model failed")

        result = handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test prompt",
            call_fn=mock_call,
        )

        assert result.success is True
        assert result.strategy_used == FallbackStrategy.MODEL_DOWNGRADE
        assert result.fallback_model == "gpt-3.5-turbo"

    def test_handle_fallback_model_downgrade_fails(self, handler):
        """Test model downgrade when fallback also fails."""
        def mock_call(model, prompt):
            raise Exception("All models failed")

        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.MODEL_DOWNGRADE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test prompt",
            call_fn=mock_call,
        )

        assert result.success is False

    def test_handle_fallback_cached_response(self, handler):
        """Test cached response fallback."""
        # Pre-cache a response
        handler.cache_response("Test prompt", "gpt-4", "Cached response")

        result = handler.handle_fallback(
            reason=FallbackReason.QUOTA_EXCEEDED,
            model="gpt-4",
            prompt="Test prompt",
        )

        assert result.success is True
        assert result.strategy_used == FallbackStrategy.CACHED_RESPONSE
        assert result.from_cache is True
        assert result.response == "Cached response"

    def test_handle_fallback_cached_from_fallback_model(self, handler):
        """Test using cached response from fallback model."""
        # Cache for fallback model
        handler.cache_response("Test prompt", "gpt-3.5-turbo", "Fallback cached")

        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.CACHED_RESPONSE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test prompt",
        )

        assert result.success is True
        assert result.from_cache is True
        assert result.fallback_model == "gpt-3.5-turbo"

    def test_handle_fallback_degraded_response(self, handler):
        """Test degraded response fallback."""
        handler.register_degraded_response("test", lambda: "Degraded response")

        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.DEGRADED_RESPONSE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test prompt",
            degraded_key="test",
        )

        assert result.success is True
        assert result.strategy_used == FallbackStrategy.DEGRADED_RESPONSE
        assert result.response == "Degraded response"

    def test_handle_fallback_degraded_default(self, handler):
        """Test degraded response with default key."""
        handler.register_degraded_response("default", lambda: "Default degraded")

        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.DEGRADED_RESPONSE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.TIMEOUT,
            model="gpt-4",
            prompt="Test prompt",
        )

        assert result.success is True
        assert result.response == "Default degraded"

    def test_handle_fallback_all_fail(self, handler):
        """Test when all fallback strategies fail."""
        handler.configure(FallbackConfig(
            strategies=[
                FallbackStrategy.MODEL_DOWNGRADE,
                FallbackStrategy.CACHED_RESPONSE,
            ],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Unknown prompt",
        )

        assert result.success is False
        assert result.strategy_used == FallbackStrategy.FAIL_FAST

    def test_get_stats(self, handler):
        """Test getting stats."""
        handler.cache_response("Test", "gpt-4", "Response")
        handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test",
        )

        stats = handler.get_stats()

        assert stats.total_fallbacks == 1
        assert stats.cache_hits == 1

    def test_get_fallback_model(self, handler):
        """Test getting fallback model."""
        assert handler.get_fallback_model("gpt-4") == "gpt-3.5-turbo"
        assert handler.get_fallback_model("unknown") is None

    def test_cleanup_cache(self, handler):
        """Test cleaning up cache."""
        # Use short TTL
        handler.config.cache_ttl_seconds = 1
        handler.cache = ResponseCache(default_ttl=1)

        start_time = time.time()
        with patch('time.time', return_value=start_time):
            handler.cache_response("Test", "model", "Response")

        # Simulate time passing past TTL
        with patch('time.time', return_value=start_time + 1.5):
            count = handler.cleanup_cache()
            assert count == 1

    def test_stats_by_reason(self, handler):
        """Test stats track reasons."""
        handler.cache_response("Test1", "gpt-4", "R1")
        handler.cache_response("Test2", "gpt-4", "R2")

        handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test1",
        )
        handler.handle_fallback(
            reason=FallbackReason.QUOTA_EXCEEDED,
            model="gpt-4",
            prompt="Test2",
        )

        stats = handler.get_stats()

        assert stats.by_reason["circuit_open"] == 1
        assert stats.by_reason["quota_exceeded"] == 1

    def test_stats_by_strategy(self, handler):
        """Test stats track strategies."""
        handler.cache_response("Test1", "gpt-4", "R1")

        handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test1",
        )

        stats = handler.get_stats()

        assert stats.by_strategy.get("cached_response", 0) >= 1

    def test_model_downgrade_caches_response(self, handler):
        """Test model downgrade caches successful response."""
        def mock_call(model, prompt):
            return f"Response from {model}"

        handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test prompt",
            call_fn=mock_call,
        )

        # Should now be cached
        cached = handler.cache.get("Test prompt", "gpt-3.5-turbo")
        assert cached is not None


class TestFallbackCoverage:
    """Additional tests for full coverage."""

    def test_try_strategy_fail_fast(self):
        """Test FAIL_FAST strategy."""
        handler = FallbackHandler()
        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.FAIL_FAST],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test",
        )

        assert result.success is False
        assert result.strategy_used == FallbackStrategy.FAIL_FAST

    def test_try_strategy_retry_later(self):
        """Test RETRY_LATER strategy (not implemented, should fail)."""
        handler = FallbackHandler()
        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.RETRY_LATER],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.TIMEOUT,
            model="gpt-4",
            prompt="Test",
        )

        # RETRY_LATER not implemented, should fail
        assert result.success is False

    def test_model_downgrade_no_call_fn(self):
        """Test model downgrade without call function."""
        handler = FallbackHandler()
        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.MODEL_DOWNGRADE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test",
            call_fn=None,  # No call function
        )

        assert result.success is False

    def test_model_downgrade_no_fallback_model(self):
        """Test model downgrade when no fallback model configured."""
        handler = FallbackHandler()
        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.MODEL_DOWNGRADE],
            model_fallback_chain={},  # Empty chain
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test",
            call_fn=lambda m, p: "response",
        )

        assert result.success is False

    def test_degraded_response_error(self):
        """Test degraded response when generator fails."""
        handler = FallbackHandler()
        handler.register_degraded_response("error", lambda: 1/0)  # Will raise

        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.DEGRADED_RESPONSE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test",
            degraded_key="error",
        )

        assert result.success is False

    def test_degraded_response_no_generator(self):
        """Test degraded response when no generator registered."""
        handler = FallbackHandler()
        handler.configure(FallbackConfig(
            strategies=[FallbackStrategy.DEGRADED_RESPONSE],
        ))

        result = handler.handle_fallback(
            reason=FallbackReason.API_ERROR,
            model="gpt-4",
            prompt="Test",
            degraded_key="nonexistent",
        )

        assert result.success is False

    def test_cache_with_params(self):
        """Test cache with additional params."""
        cache = ResponseCache()

        cache.put("prompt", "model", "response1", params={"temp": 0.5})
        cache.put("prompt", "model", "response2", params={"temp": 0.7})

        cached1 = cache.get("prompt", "model", params={"temp": 0.5})
        cached2 = cache.get("prompt", "model", params={"temp": 0.7})

        assert cached1.response == "response1"
        assert cached2.response == "response2"

    def test_fallback_stats_model_downgrades(self):
        """Test stats track model downgrades."""
        handler = FallbackHandler()

        def mock_call(model, prompt):
            return f"Response from {model}"

        handler.handle_fallback(
            reason=FallbackReason.CIRCUIT_OPEN,
            model="gpt-4",
            prompt="Test",
            call_fn=mock_call,
        )

        stats = handler.get_stats()
        assert stats.model_downgrades == 1

    def test_cache_custom_ttl(self):
        """Test cache with custom TTL."""
        cache = ResponseCache(default_ttl=3600)

        start_time = time.time()
        with patch('time.time', return_value=start_time):
            cache.put("prompt", "model", "response", ttl=1)

        # Simulate time passing past custom TTL
        with patch('time.time', return_value=start_time + 1.5):
            cached = cache.get("prompt", "model")
            assert cached is None  # Should be expired


class TestSingleton:
    """Tests for singleton functions."""

    def test_get_fallback_handler(self):
        """Test getting singleton."""
        reset_fallback_handler()
        handler1 = get_fallback_handler()
        handler2 = get_fallback_handler()

        assert handler1 is handler2

    def test_reset_fallback_handler(self):
        """Test resetting singleton."""
        handler1 = get_fallback_handler()
        reset_fallback_handler()
        handler2 = get_fallback_handler()

        assert handler1 is not handler2
