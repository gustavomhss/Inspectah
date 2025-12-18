"""
Tests for app/ingestion/rate_limiter.py

Covers:
- TokenBucketRateLimiter configuration
- Token acquisition (blocking and non-blocking)
- Token refill mechanics
- Wait time calculations
- Stats retrieval
- Reset, enable, disable functionality
- Singleton getter
"""
from __future__ import annotations

import time
import threading
from unittest.mock import patch

import pytest

from app.ingestion.rate_limiter import (
    TokenBucketRateLimiter,
    RateLimitConfig,
    RateLimitState,
    RateLimitStrategy,
    get_rate_limiter,
)


class TestTokenBucketRateLimiter:
    """Test suite for TokenBucketRateLimiter."""

    def test_configure_source(self):
        """Test configuring rate limit for a source."""
        limiter = TokenBucketRateLimiter()

        limiter.configure(
            source_id="test_source",
            requests_per_minute=30,
            burst_size=10,
        )

        assert "test_source" in limiter._configs
        assert "test_source" in limiter._states

        config = limiter._configs["test_source"]
        assert config.source_id == "test_source"
        assert config.requests_per_minute == 30
        assert config.burst_size == 10
        assert config.enabled is True

        state = limiter._states["test_source"]
        assert state.source_id == "test_source"
        assert state.tokens == 10.0  # Starts with burst_size tokens

    def test_acquire_no_config(self):
        """Test acquiring tokens for unconfigured source allows request."""
        limiter = TokenBucketRateLimiter()

        # No config = no limit
        result = limiter.acquire("unconfigured_source")
        assert result is True

    def test_acquire_disabled_source(self):
        """Test acquiring tokens for disabled source allows request."""
        limiter = TokenBucketRateLimiter()
        limiter.configure("test_source", requests_per_minute=10)
        limiter.disable("test_source")

        result = limiter.acquire("test_source")
        assert result is True

    def test_acquire_success(self):
        """Test successful token acquisition."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=5,
        )

        # Should succeed - we have 5 tokens
        result = limiter.acquire("test_source", tokens=1.0)
        assert result is True

        state = limiter._states["test_source"]
        assert state.tokens == 4.0
        assert state.requests_this_window == 1

    def test_acquire_multiple_tokens(self):
        """Test acquiring multiple tokens at once."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=10,
        )

        result = limiter.acquire("test_source", tokens=3.0)
        assert result is True

        state = limiter._states["test_source"]
        assert state.tokens == 7.0

    def test_acquire_insufficient_tokens_nonblocking(self):
        """Test acquiring tokens when insufficient (non-blocking)."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=5,
        )

        # Exhaust tokens
        for _ in range(5):
            limiter.acquire("test_source", tokens=1.0)

        # Should fail - no tokens left
        result = limiter.acquire("test_source", tokens=1.0, block=False)
        assert result is False

        state = limiter._states["test_source"]
        assert state.tokens < 1.0

    def test_acquire_blocking_waits_for_tokens(self):
        """Test that blocking acquire waits for token refill."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,  # 1 token per second
            burst_size=2,
        )

        # Consume all tokens
        limiter.acquire("test_source", tokens=2.0)

        start_time = time.time()
        # Block and wait for tokens (should get ~1 token after 1 second)
        result = limiter.acquire("test_source", tokens=1.0, block=True, timeout=3.0)
        elapsed = time.time() - start_time

        assert result is True
        # Should have waited approximately 1 second for token refill
        assert 0.5 < elapsed < 2.0  # Allow some variance

    def test_acquire_blocking_timeout(self):
        """Test that blocking acquire respects timeout."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=6,  # 0.1 tokens per second (very slow)
            burst_size=1,
        )

        # Consume all tokens
        limiter.acquire("test_source", tokens=1.0)

        start_time = time.time()
        # Try to acquire 5 tokens with short timeout (impossible)
        result = limiter.acquire("test_source", tokens=5.0, block=True, timeout=0.5)
        elapsed = time.time() - start_time

        assert result is False
        # Should timeout around 0.5 seconds
        assert 0.4 < elapsed < 1.0

    def test_refill_tokens_over_time(self):
        """Test that tokens are refilled over time."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,  # 1 token per second
            burst_size=5,
        )

        # Consume all tokens
        for _ in range(5):
            limiter.acquire("test_source", tokens=1.0)

        state = limiter._states["test_source"]
        assert state.tokens < 1.0

        # Wait for refill
        time.sleep(1.1)  # Wait ~1 second

        # Manually trigger refill
        limiter._refill_tokens("test_source")

        state = limiter._states["test_source"]
        # Should have refilled ~1 token
        assert state.tokens >= 0.9
        assert state.tokens <= 1.5

    def test_refill_respects_burst_size_cap(self):
        """Test that refill doesn't exceed burst_size."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=120,  # 2 tokens per second
            burst_size=5,
        )

        # Wait to accumulate tokens
        time.sleep(10.0)  # Would refill 20 tokens if uncapped

        limiter._refill_tokens("test_source")

        state = limiter._states["test_source"]
        # Should be capped at burst_size
        assert state.tokens == 5.0

    def test_refill_no_config(self):
        """Test refill with no config is no-op."""
        limiter = TokenBucketRateLimiter()

        # Should not raise
        limiter._refill_tokens("nonexistent")

    def test_get_wait_time_no_wait_needed(self):
        """Test get_wait_time when tokens are available."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=5,
        )

        wait_time = limiter.get_wait_time("test_source", tokens=3.0)
        assert wait_time == 0.0

    def test_get_wait_time_calculation(self):
        """Test wait time calculation when tokens are needed."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,  # 1 token per second
            burst_size=5,
        )

        # Consume all tokens
        for _ in range(5):
            limiter.acquire("test_source", tokens=1.0)

        # Need 3 tokens, refill rate is 1/sec, so should wait ~3 seconds
        wait_time = limiter.get_wait_time("test_source", tokens=3.0)
        assert 2.5 < wait_time < 3.5

    def test_get_wait_time_no_config(self):
        """Test get_wait_time for unconfigured source."""
        limiter = TokenBucketRateLimiter()

        wait_time = limiter.get_wait_time("nonexistent")
        assert wait_time == 0.0

    def test_get_stats_success(self):
        """Test retrieving stats for a configured source."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=30,
            burst_size=10,
        )

        limiter.acquire("test_source", tokens=3.0)

        stats = limiter.get_stats("test_source")

        assert stats is not None
        assert stats["source_id"] == "test_source"
        # Allow small variance due to token refill during test
        assert 6.9 < stats["tokens_available"] < 7.1
        assert stats["burst_size"] == 10
        assert stats["requests_per_minute"] == 30
        assert stats["requests_this_window"] == 1
        assert stats["enabled"] is True

    def test_get_stats_no_config(self):
        """Test get_stats for unconfigured source."""
        limiter = TokenBucketRateLimiter()

        stats = limiter.get_stats("nonexistent")
        assert stats is None

    def test_reset_source(self):
        """Test resetting a source restores initial tokens."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=10,
        )

        # Consume some tokens
        for _ in range(5):
            limiter.acquire("test_source", tokens=1.0)

        state = limiter._states["test_source"]
        # Allow small variance due to token refill
        assert 4.9 < state.tokens < 5.1
        assert state.requests_this_window == 5

        # Reset
        limiter.reset("test_source")

        state = limiter._states["test_source"]
        assert state.tokens == 10.0  # Restored to burst_size
        assert state.requests_this_window == 0

    def test_reset_nonexistent_source(self):
        """Test reset on nonexistent source is no-op."""
        limiter = TokenBucketRateLimiter()

        # Should not raise
        limiter.reset("nonexistent")

    def test_enable_disable_source(self):
        """Test enabling and disabling rate limiting."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=10,
            burst_size=5,
        )

        assert limiter._configs["test_source"].enabled is True

        # Disable
        limiter.disable("test_source")
        assert limiter._configs["test_source"].enabled is False

        # Acquire should succeed even with no tokens when disabled
        for _ in range(10):
            result = limiter.acquire("test_source")
            assert result is True

        # Re-enable
        limiter.enable("test_source")
        assert limiter._configs["test_source"].enabled is True

    def test_enable_disable_nonexistent(self):
        """Test enable/disable on nonexistent source is no-op."""
        limiter = TokenBucketRateLimiter()

        # Should not raise
        limiter.disable("nonexistent")
        limiter.enable("nonexistent")

    def test_thread_safety(self):
        """Test that limiter is thread-safe."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=600,  # High rate
            burst_size=100,
        )

        results = []

        def acquire_tokens():
            for _ in range(10):
                result = limiter.acquire("test_source", tokens=1.0)
                results.append(result)

        # Run 5 threads concurrently
        threads = [threading.Thread(target=acquire_tokens) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have acquired 50 tokens total (5 threads * 10 each)
        successes = sum(1 for r in results if r)
        assert successes == 50

        state = limiter._states["test_source"]
        # Allow small variance due to token refill during thread execution
        assert 49.5 < state.tokens < 50.5  # 100 - 50 = ~50
        assert state.requests_this_window == 50

    def test_refill_rate_accuracy(self):
        """Test that refill rate is accurate."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=120,  # 2 tokens per second
            burst_size=10,
        )

        # Consume all tokens
        for _ in range(10):
            limiter.acquire("test_source", tokens=1.0)

        # Wait for 0.5 seconds (should refill ~1 token)
        time.sleep(0.5)

        limiter._refill_tokens("test_source")

        state = limiter._states["test_source"]
        # Should have ~1 token (0.5s * 2 tokens/s)
        assert 0.8 < state.tokens < 1.5

    def test_consecutive_acquires(self):
        """Test multiple consecutive acquires."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=3,
        )

        # Should succeed 3 times
        assert limiter.acquire("test_source") is True
        assert limiter.acquire("test_source") is True
        assert limiter.acquire("test_source") is True

        # Should fail on 4th
        assert limiter.acquire("test_source", block=False) is False

    def test_partial_token_consumption(self):
        """Test consuming fractional tokens."""
        limiter = TokenBucketRateLimiter()
        limiter.configure(
            source_id="test_source",
            requests_per_minute=60,
            burst_size=10,
        )

        result = limiter.acquire("test_source", tokens=2.5)
        assert result is True

        state = limiter._states["test_source"]
        assert state.tokens == 7.5


def test_get_rate_limiter_singleton():
    """Test singleton getter returns same instance."""
    limiter1 = get_rate_limiter()
    limiter2 = get_rate_limiter()

    assert limiter1 is limiter2


def test_rate_limit_config_defaults():
    """Test RateLimitConfig default values."""
    config = RateLimitConfig(source_id="test")

    assert config.requests_per_minute == 10
    assert config.burst_size == 5
    assert config.strategy == RateLimitStrategy.TOKEN_BUCKET
    assert config.enabled is True


def test_rate_limit_strategy_enum():
    """Test RateLimitStrategy enum values."""
    assert RateLimitStrategy.TOKEN_BUCKET.value == "token_bucket"
    assert RateLimitStrategy.SLIDING_WINDOW.value == "sliding_window"
    assert RateLimitStrategy.FIXED_WINDOW.value == "fixed_window"


def test_concurrent_refills():
    """Test that concurrent refills don't cause issues."""
    limiter = TokenBucketRateLimiter()
    limiter.configure(
        source_id="test_source",
        requests_per_minute=60,
        burst_size=10,
    )

    def refill_repeatedly():
        for _ in range(100):
            limiter._refill_tokens("test_source")

    threads = [threading.Thread(target=refill_repeatedly) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should still be capped at burst_size
    state = limiter._states["test_source"]
    assert state.tokens <= 10.0


def test_acquire_with_wait_time_calculation():
    """Test wait time calculation during blocking acquire."""
    limiter = TokenBucketRateLimiter()
    limiter.configure(
        source_id="test_source",
        requests_per_minute=60,  # 1 token/sec
        burst_size=1,
    )

    # Consume token
    limiter.acquire("test_source")

    # Calculate wait time before blocking acquire
    wait_before = limiter.get_wait_time("test_source", tokens=1.0)
    assert wait_before > 0.5

    # Now actually acquire (should wait)
    start = time.time()
    result = limiter.acquire("test_source", block=True, timeout=2.0)
    elapsed = time.time() - start

    assert result is True
    assert elapsed > 0.5
    assert elapsed < 2.0


def test_high_rate_refill():
    """Test refill at very high request rates."""
    limiter = TokenBucketRateLimiter()
    limiter.configure(
        source_id="test_source",
        requests_per_minute=6000,  # 100 tokens/sec
        burst_size=50,
    )

    # Consume all
    for _ in range(50):
        limiter.acquire("test_source")

    # Wait briefly
    time.sleep(0.1)  # Should refill ~10 tokens

    limiter._refill_tokens("test_source")

    state = limiter._states["test_source"]
    # Should have refilled approximately 10 tokens (0.1s * 100/s)
    assert 8 < state.tokens < 12


def test_zero_tokens_after_consumption():
    """Test state when all tokens are consumed."""
    limiter = TokenBucketRateLimiter()
    limiter.configure(
        source_id="test_source",
        requests_per_minute=60,
        burst_size=3,
    )

    # Consume all
    for _ in range(3):
        limiter.acquire("test_source")

    state = limiter._states["test_source"]
    # Allow very small variance due to token refill
    assert state.tokens < 0.01

    # Next acquire should fail
    assert limiter.acquire("test_source", block=False) is False


def test_requests_this_window_counter():
    """Test that requests_this_window counter increments correctly."""
    limiter = TokenBucketRateLimiter()
    limiter.configure(
        source_id="test_source",
        requests_per_minute=60,
        burst_size=10,
    )

    for i in range(5):
        limiter.acquire("test_source")
        state = limiter._states["test_source"]
        assert state.requests_this_window == i + 1
