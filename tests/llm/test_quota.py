"""
Tests for LLM Quota Manager.

S39 - Quota Management Tests
"""
import time
from unittest.mock import patch

import pytest

from app.llm.quota import (
    QuotaScope,
    QuotaType,
    QuotaExceededError,
    QuotaLimit,
    QuotaUsage,
    QuotaStats,
    QuotaManager,
    get_quota_manager,
    reset_quota_manager,
)


class TestQuotaEnums:
    """Tests for quota enums."""

    def test_quota_scope_values(self):
        """Test QuotaScope enum values."""
        assert QuotaScope.GLOBAL.value == "global"
        assert QuotaScope.MODEL.value == "model"
        assert QuotaScope.USER.value == "user"
        assert QuotaScope.AGENT.value == "agent"

    def test_quota_type_values(self):
        """Test QuotaType enum values."""
        assert QuotaType.TOKENS.value == "tokens"
        assert QuotaType.INPUT_TOKENS.value == "input_tokens"
        assert QuotaType.OUTPUT_TOKENS.value == "output_tokens"
        assert QuotaType.REQUESTS.value == "requests"


class TestQuotaLimit:
    """Tests for QuotaLimit dataclass."""

    def test_create_limit(self):
        """Test creating quota limit."""
        limit = QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            window_seconds=3600,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        )

        assert limit.quota_type == QuotaType.TOKENS
        assert limit.limit == 100000
        assert limit.window_seconds == 3600
        assert limit.scope == QuotaScope.MODEL
        assert limit.scope_id == "gpt-4"

    def test_default_values(self):
        """Test default values."""
        limit = QuotaLimit(
            quota_type=QuotaType.REQUESTS,
            limit=1000,
        )

        assert limit.window_seconds == 3600
        assert limit.scope == QuotaScope.GLOBAL
        assert limit.scope_id is None


class TestQuotaUsage:
    """Tests for QuotaUsage dataclass."""

    def test_create_usage(self):
        """Test creating quota usage."""
        now = time.time()
        usage = QuotaUsage(
            quota_type=QuotaType.TOKENS,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
            window_start=now,
            window_seconds=3600,
            limit=100000,
            used=50000,
        )

        assert usage.remaining == 50000
        assert not usage.is_exceeded

    def test_remaining_at_limit(self):
        """Test remaining when at limit."""
        usage = QuotaUsage(
            quota_type=QuotaType.TOKENS,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
            window_start=time.time(),
            window_seconds=3600,
            limit=1000,
            used=1000,
        )

        assert usage.remaining == 0
        assert usage.is_exceeded

    def test_remaining_over_limit(self):
        """Test remaining when over limit."""
        usage = QuotaUsage(
            quota_type=QuotaType.TOKENS,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
            window_start=time.time(),
            window_seconds=3600,
            limit=1000,
            used=1500,
        )

        assert usage.remaining == 0
        assert usage.is_exceeded

    def test_to_dict(self):
        """Test converting usage to dict."""
        usage = QuotaUsage(
            quota_type=QuotaType.TOKENS,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
            window_start=time.time(),
            window_seconds=3600,
            limit=100000,
            used=25000,
        )

        d = usage.to_dict()

        assert d["quota_type"] == "tokens"
        assert d["scope"] == "model"
        assert d["scope_id"] == "gpt-4"
        assert d["limit"] == 100000
        assert d["used"] == 25000
        assert d["remaining"] == 75000
        assert d["utilization_percent"] == 25.0


class TestQuotaExceededError:
    """Tests for QuotaExceededError."""

    def test_error_creation(self):
        """Test creating error."""
        error = QuotaExceededError(
            message="Quota exceeded",
            quota_type=QuotaType.TOKENS,
            current=100000,
            limit=100000,
        )

        assert str(error) == "Quota exceeded"
        assert error.quota_type == QuotaType.TOKENS
        assert error.current == 100000
        assert error.limit == 100000

    def test_error_with_reset_at(self):
        """Test error with reset time."""
        from datetime import datetime, timezone

        reset = datetime.now(timezone.utc)
        error = QuotaExceededError(
            message="Quota exceeded",
            quota_type=QuotaType.REQUESTS,
            current=100,
            limit=100,
            reset_at=reset,
        )

        assert error.reset_at == reset


class TestQuotaManager:
    """Tests for QuotaManager."""

    @pytest.fixture
    def manager(self):
        """Create fresh quota manager."""
        return QuotaManager()

    def test_create_manager(self, manager):
        """Test creating manager."""
        assert manager is not None
        stats = manager.get_stats()
        assert stats.total_requests == 0

    def test_add_limit(self, manager):
        """Test adding quota limit."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            window_seconds=3600,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        # Should be able to consume
        assert manager.can_consume("gpt-4", QuotaType.TOKENS, 1000)

    def test_remove_limit(self, manager):
        """Test removing quota limit."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        result = manager.remove_limit(QuotaType.TOKENS, QuotaScope.MODEL, "gpt-4")
        assert result is True

    def test_remove_nonexistent_limit(self, manager):
        """Test removing nonexistent limit."""
        result = manager.remove_limit(QuotaType.TOKENS, QuotaScope.MODEL, "nonexistent")
        assert result is False

    def test_can_consume_no_limit(self, manager):
        """Test can_consume with no limit configured."""
        # No limit configured, should allow
        assert manager.can_consume("gpt-4", QuotaType.TOKENS, 1000000)

    def test_can_consume_within_limit(self, manager):
        """Test can_consume within limit."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        assert manager.can_consume("gpt-4", QuotaType.TOKENS, 50000)

    def test_can_consume_exceeds_limit(self, manager):
        """Test can_consume exceeding limit."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        assert not manager.can_consume("gpt-4", QuotaType.TOKENS, 150000)

    def test_consume_success(self, manager):
        """Test successful consumption."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        usage = manager.consume("gpt-4", QuotaType.TOKENS, 1000)

        assert usage.used == 1000
        assert usage.remaining == 99000

    def test_consume_multiple(self, manager):
        """Test multiple consumptions."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=10000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 3000)
        manager.consume("gpt-4", QuotaType.TOKENS, 2000)
        usage = manager.consume("gpt-4", QuotaType.TOKENS, 1000)

        assert usage.used == 6000
        assert usage.remaining == 4000

    def test_consume_exceeds_raises(self, manager):
        """Test consumption exceeding limit raises error."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=1000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        with pytest.raises(QuotaExceededError) as exc_info:
            manager.consume("gpt-4", QuotaType.TOKENS, 2000)

        assert exc_info.value.quota_type == QuotaType.TOKENS
        assert exc_info.value.limit == 1000

    def test_consume_exceeds_no_raise(self, manager):
        """Test consumption exceeding limit without raising."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=1000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        usage = manager.consume(
            "gpt-4",
            QuotaType.TOKENS,
            2000,
            raise_on_exceed=False,
        )

        # Should still track usage even when over
        assert usage.used == 2000

    def test_consume_no_limit_configured(self, manager):
        """Test consumption with no limit configured."""
        usage = manager.consume("gpt-4", QuotaType.TOKENS, 1000)

        # Should create temporary usage tracker
        assert usage.used == 1000
        assert usage.limit == 999999999

    def test_get_usage(self, manager):
        """Test getting current usage."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 5000)

        usage = manager.get_usage("gpt-4", QuotaType.TOKENS)

        assert usage is not None
        assert usage.used == 5000

    def test_get_usage_no_limit(self, manager):
        """Test getting usage with no limit configured."""
        usage = manager.get_usage("nonexistent", QuotaType.TOKENS)
        assert usage is None

    def test_get_all_usage(self, manager):
        """Test getting all usage."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.REQUESTS,
            limit=1000,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 1000)
        manager.consume("default", QuotaType.REQUESTS, 1, scope=QuotaScope.GLOBAL)

        all_usage = manager.get_all_usage()

        assert len(all_usage) == 2

    def test_reset_usage(self, manager):
        """Test resetting usage."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 50000)
        result = manager.reset_usage("gpt-4", QuotaType.TOKENS)

        assert result is True

        usage = manager.get_usage("gpt-4", QuotaType.TOKENS)
        assert usage.used == 0

    def test_reset_usage_not_found(self, manager):
        """Test resetting nonexistent usage."""
        result = manager.reset_usage("nonexistent", QuotaType.TOKENS)
        assert result is False

    def test_window_expiration(self, manager):
        """Test window expiration resets usage."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            window_seconds=1,  # 1 second window
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        start_time = time.time()
        with patch('time.time', return_value=start_time):
            manager.consume("gpt-4", QuotaType.TOKENS, 50000)

        # Simulate time passing past window
        with patch('time.time', return_value=start_time + 1.5):
            usage = manager.get_usage("gpt-4", QuotaType.TOKENS)

            # Usage should be reset
            assert usage.used == 0

    def test_get_stats(self, manager):
        """Test getting stats."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 1000)
        manager.consume("gpt-4", QuotaType.TOKENS, 2000)

        stats = manager.get_stats()

        assert stats.total_requests == 2
        assert stats.total_tokens == 3000
        assert stats.rejected_requests == 0

    def test_stats_rejected_requests(self, manager):
        """Test stats track rejected requests."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=1000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 500)

        with pytest.raises(QuotaExceededError):
            manager.consume("gpt-4", QuotaType.TOKENS, 1000)

        stats = manager.get_stats()
        assert stats.rejected_requests == 1

    def test_reserve(self, manager):
        """Test reservation check."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=1000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        assert manager.reserve("gpt-4", QuotaType.TOKENS, 500) is True
        assert manager.reserve("gpt-4", QuotaType.TOKENS, 2000) is False

    def test_to_dict(self, manager):
        """Test exporting to dict."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.TOKENS,
            limit=100000,
            scope=QuotaScope.MODEL,
            scope_id="gpt-4",
        ))

        manager.consume("gpt-4", QuotaType.TOKENS, 1000)

        data = manager.to_dict()

        assert "limits" in data
        assert "usage" in data
        assert "stats" in data
        assert len(data["limits"]) == 1

    def test_input_output_token_stats(self, manager):
        """Test input/output token stats tracking."""
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.INPUT_TOKENS,
            limit=100000,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
        ))
        manager.add_limit(QuotaLimit(
            quota_type=QuotaType.OUTPUT_TOKENS,
            limit=50000,
            scope=QuotaScope.GLOBAL,
            scope_id="default",
        ))

        manager.consume("default", QuotaType.INPUT_TOKENS, 1000, scope=QuotaScope.GLOBAL)
        manager.consume("default", QuotaType.OUTPUT_TOKENS, 500, scope=QuotaScope.GLOBAL)

        stats = manager.get_stats()
        assert stats.total_input_tokens == 1000
        assert stats.total_output_tokens == 500


class TestSingleton:
    """Tests for singleton functions."""

    def test_get_quota_manager(self):
        """Test getting singleton."""
        reset_quota_manager()
        manager1 = get_quota_manager()
        manager2 = get_quota_manager()

        assert manager1 is manager2

    def test_reset_quota_manager(self):
        """Test resetting singleton."""
        manager1 = get_quota_manager()
        reset_quota_manager()
        manager2 = get_quota_manager()

        assert manager1 is not manager2
