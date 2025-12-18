"""
Tests for ProxyManager.

S39 - Proxy Manager Tests
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.scrapers.proxy_manager import (
    ProxyConfig,
    ProxyEntry,
    ProxyManager,
    ProxyManagerConfig,
    ProxyProtocol,
    ProxyStats,
    RotationStrategy,
    get_proxy_manager,
)


class TestProxyProtocol:
    """Tests for ProxyProtocol enum."""

    def test_protocols(self):
        """Test all protocols."""
        assert ProxyProtocol.HTTP.value == "http"
        assert ProxyProtocol.HTTPS.value == "https"
        assert ProxyProtocol.SOCKS5.value == "socks5"


class TestRotationStrategy:
    """Tests for RotationStrategy enum."""

    def test_strategies(self):
        """Test all strategies."""
        assert RotationStrategy.ROUND_ROBIN.value == "round_robin"
        assert RotationStrategy.RANDOM.value == "random"
        assert RotationStrategy.WEIGHTED.value == "weighted"
        assert RotationStrategy.LEAST_USED.value == "least_used"


class TestProxyConfig:
    """Tests for ProxyConfig."""

    def test_basic_config(self):
        """Test basic proxy config."""
        config = ProxyConfig(
            host="proxy.example.com",
            port=8080,
        )

        assert config.host == "proxy.example.com"
        assert config.port == 8080
        assert config.protocol == ProxyProtocol.HTTP
        assert config.username is None
        assert config.password is None

    def test_to_url_no_auth(self):
        """Test URL generation without auth."""
        config = ProxyConfig(
            host="proxy.example.com",
            port=8080,
        )

        assert config.to_url() == "http://proxy.example.com:8080"

    def test_to_url_with_auth(self):
        """Test URL generation with auth."""
        config = ProxyConfig(
            host="proxy.example.com",
            port=8080,
            username="user",
            password="pass",
        )

        assert config.to_url() == "http://user:pass@proxy.example.com:8080"

    def test_to_url_https(self):
        """Test HTTPS URL generation."""
        config = ProxyConfig(
            host="proxy.example.com",
            port=443,
            protocol=ProxyProtocol.HTTPS,
        )

        assert config.to_url() == "https://proxy.example.com:443"

    def test_to_url_socks5(self):
        """Test SOCKS5 URL generation."""
        config = ProxyConfig(
            host="proxy.example.com",
            port=1080,
            protocol=ProxyProtocol.SOCKS5,
        )

        assert config.to_url() == "socks5://proxy.example.com:1080"

    def test_from_url_simple(self):
        """Test parsing simple URL."""
        config = ProxyConfig.from_url("http://proxy.example.com:8080")

        assert config.host == "proxy.example.com"
        assert config.port == 8080
        assert config.protocol == ProxyProtocol.HTTP
        assert config.username is None

    def test_from_url_with_auth(self):
        """Test parsing URL with auth."""
        config = ProxyConfig.from_url("http://user:pass@proxy.example.com:8080")

        assert config.host == "proxy.example.com"
        assert config.port == 8080
        assert config.username == "user"
        assert config.password == "pass"

    def test_from_url_https(self):
        """Test parsing HTTPS URL."""
        config = ProxyConfig.from_url("https://proxy.example.com:443")

        assert config.protocol == ProxyProtocol.HTTPS
        assert config.port == 443

    def test_from_url_socks5(self):
        """Test parsing SOCKS5 URL."""
        config = ProxyConfig.from_url("socks5://proxy.example.com:1080")

        assert config.protocol == ProxyProtocol.SOCKS5
        assert config.port == 1080

    def test_from_url_no_port(self):
        """Test parsing URL without port."""
        config = ProxyConfig.from_url("http://proxy.example.com")

        assert config.host == "proxy.example.com"
        assert config.port == 80

    def test_from_url_https_no_port(self):
        """Test parsing HTTPS URL without port defaults to 443."""
        config = ProxyConfig.from_url("https://proxy.example.com")

        assert config.host == "proxy.example.com"
        assert config.port == 443
        assert config.protocol == ProxyProtocol.HTTPS

    def test_from_url_with_name(self):
        """Test parsing URL with name."""
        config = ProxyConfig.from_url("http://proxy.example.com:8080", name="my-proxy")

        assert config.name == "my-proxy"

    def test_from_url_password_with_special_chars(self):
        """Test parsing URL with special chars in password."""
        config = ProxyConfig.from_url("http://user:p@ss:word@proxy.example.com:8080")

        assert config.username == "user"
        # Everything after first : and before last @ is password
        assert config.host == "proxy.example.com"
        assert config.port == 8080


class TestProxyStats:
    """Tests for ProxyStats."""

    def test_default_stats(self):
        """Test default stats."""
        stats = ProxyStats()

        assert stats.requests_success == 0
        assert stats.requests_failed == 0
        assert stats.is_healthy is True
        assert stats.consecutive_failures == 0

    def test_record_success(self):
        """Test recording success."""
        stats = ProxyStats()

        stats.record_success(100.0)

        assert stats.requests_success == 1
        assert stats.total_response_time_ms == 100.0
        assert stats.last_used_at is not None
        assert stats.consecutive_failures == 0
        assert stats.is_healthy is True

    def test_record_failure(self):
        """Test recording failure."""
        stats = ProxyStats()

        stats.record_failure("Connection timeout")

        assert stats.requests_failed == 1
        assert stats.last_error == "Connection timeout"
        assert stats.consecutive_failures == 1

    def test_avg_response_time_no_requests(self):
        """Test avg response time with no requests."""
        stats = ProxyStats()

        assert stats.avg_response_time_ms() == 0.0

    def test_avg_response_time(self):
        """Test avg response time."""
        stats = ProxyStats()
        stats.record_success(100.0)
        stats.record_success(200.0)
        stats.record_success(300.0)

        assert stats.avg_response_time_ms() == 200.0

    def test_success_rate_no_requests(self):
        """Test success rate with no requests."""
        stats = ProxyStats()

        assert stats.success_rate() == 1.0

    def test_success_rate(self):
        """Test success rate."""
        stats = ProxyStats()
        stats.record_success(100.0)
        stats.record_success(100.0)
        stats.record_success(100.0)
        stats.record_failure("error")

        assert stats.success_rate() == 0.75

    def test_to_dict(self):
        """Test conversion to dict."""
        stats = ProxyStats()
        stats.record_success(100.0)
        stats.record_failure("error")

        d = stats.to_dict()

        assert d["requests_success"] == 1
        assert d["requests_failed"] == 1
        assert d["is_healthy"] is True
        assert "avg_response_time_ms" in d
        assert "success_rate" in d


class TestProxyManagerConfig:
    """Tests for ProxyManagerConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = ProxyManagerConfig()

        assert config.rotation_strategy == RotationStrategy.ROUND_ROBIN
        assert config.health_check_interval_seconds == 300
        assert config.health_check_timeout_seconds == 10
        assert config.blacklist_duration_seconds == 300
        assert config.max_consecutive_failures == 3
        assert config.auto_health_check is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.WEIGHTED,
            health_check_interval_seconds=60,
            max_consecutive_failures=5,
        )

        assert config.rotation_strategy == RotationStrategy.WEIGHTED
        assert config.health_check_interval_seconds == 60
        assert config.max_consecutive_failures == 5


class TestProxyManager:
    """Tests for ProxyManager."""

    def test_manager_creation(self):
        """Test creating manager."""
        manager = ProxyManager()

        assert manager.config is not None
        assert len(manager._proxies) == 0

    def test_manager_custom_config(self):
        """Test manager with custom config."""
        config = ProxyManagerConfig(rotation_strategy=RotationStrategy.RANDOM)
        manager = ProxyManager(config)

        assert manager.config.rotation_strategy == RotationStrategy.RANDOM

    def test_add_proxy(self):
        """Test adding proxy."""
        manager = ProxyManager()
        config = ProxyConfig(host="proxy.example.com", port=8080)

        manager.add_proxy(config)

        assert len(manager._proxies) == 1

    def test_add_proxy_duplicate(self):
        """Test adding duplicate proxy."""
        manager = ProxyManager()
        config = ProxyConfig(host="proxy.example.com", port=8080)

        manager.add_proxy(config)
        manager.add_proxy(config)  # Duplicate

        assert len(manager._proxies) == 1

    def test_add_proxies_from_urls(self):
        """Test adding proxies from URLs."""
        manager = ProxyManager()

        manager.add_proxies_from_urls([
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
        ])

        assert len(manager._proxies) == 2

    def test_remove_proxy(self):
        """Test removing proxy."""
        manager = ProxyManager()
        config = ProxyConfig(host="proxy.example.com", port=8080)
        manager.add_proxy(config)

        manager.remove_proxy(config.to_url())

        assert len(manager._proxies) == 0

    def test_remove_nonexistent_proxy(self):
        """Test removing nonexistent proxy."""
        manager = ProxyManager()

        # Should not raise
        manager.remove_proxy("http://nonexistent:8080")


class TestProxyManagerAsync:
    """Async tests for ProxyManager."""

    @pytest.mark.asyncio
    async def test_start_stop(self):
        """Test start and stop."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()
        assert manager._running is True

        await manager.stop()
        assert manager._running is False

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using manager as context manager."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)

        async with manager:
            assert manager._running is True

    @pytest.mark.asyncio
    async def test_get_next_round_robin(self):
        """Test round-robin rotation."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_health_check=False,
        )
        manager = ProxyManager(config)
        manager.add_proxies_from_urls([
            "http://proxy1:8080",
            "http://proxy2:8080",
            "http://proxy3:8080",
        ])

        await manager.start()

        proxies = [await manager.get_next() for _ in range(6)]

        assert proxies[0] == "http://proxy1:8080"
        assert proxies[1] == "http://proxy2:8080"
        assert proxies[2] == "http://proxy3:8080"
        assert proxies[3] == "http://proxy1:8080"

        await manager.stop()

    @pytest.mark.asyncio
    async def test_get_next_random(self):
        """Test random rotation."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.RANDOM,
            auto_health_check=False,
        )
        manager = ProxyManager(config)
        manager.add_proxies_from_urls([
            "http://proxy1:8080",
            "http://proxy2:8080",
        ])

        await manager.start()

        proxy = await manager.get_next()
        assert proxy in ["http://proxy1:8080", "http://proxy2:8080"]

        await manager.stop()

    @pytest.mark.asyncio
    async def test_get_next_least_used(self):
        """Test least-used rotation."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.LEAST_USED,
            auto_health_check=False,
        )
        manager = ProxyManager(config)
        manager.add_proxies_from_urls([
            "http://proxy1:8080",
            "http://proxy2:8080",
        ])

        await manager.start()

        # Use proxy1 multiple times
        proxy1_url = "http://proxy1:8080"
        for _ in range(5):
            await manager.report_success(proxy1_url, 100.0)

        # Next should prefer proxy2 (less used)
        next_proxy = await manager.get_next()
        assert next_proxy == "http://proxy2:8080"

        await manager.stop()

    @pytest.mark.asyncio
    async def test_get_next_no_proxies(self):
        """Test get_next with no proxies."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)

        await manager.start()

        proxy = await manager.get_next()
        assert proxy is None

        await manager.stop()

    @pytest.mark.asyncio
    async def test_report_success(self):
        """Test reporting success."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        await manager.report_success("http://proxy.example.com:8080", 100.0)

        entry = manager._proxies["http://proxy.example.com:8080"]
        assert entry.stats.requests_success == 1

        await manager.stop()

    @pytest.mark.asyncio
    async def test_report_failure(self):
        """Test reporting failure."""
        config = ProxyManagerConfig(
            auto_health_check=False,
            max_consecutive_failures=3,
        )
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        await manager.report_failure("http://proxy.example.com:8080", "Timeout")

        entry = manager._proxies["http://proxy.example.com:8080"]
        assert entry.stats.requests_failed == 1
        assert entry.stats.consecutive_failures == 1

        await manager.stop()

    @pytest.mark.asyncio
    async def test_blacklist_after_failures(self):
        """Test blacklisting after consecutive failures."""
        config = ProxyManagerConfig(
            auto_health_check=False,
            max_consecutive_failures=2,
            blacklist_duration_seconds=60,
        )
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        # Report failures
        for _ in range(3):
            await manager.report_failure("http://proxy.example.com:8080", "Error")

        entry = manager._proxies["http://proxy.example.com:8080"]
        assert entry.stats.is_healthy is False
        assert entry.stats.blacklisted_until is not None

        # Should not be available
        proxy = await manager.get_next()
        assert proxy is None

        await manager.stop()

    @pytest.mark.asyncio
    async def test_blacklist_expires(self):
        """Test blacklist expiration."""
        config = ProxyManagerConfig(
            auto_health_check=False,
            max_consecutive_failures=1,
            blacklist_duration_seconds=1,
        )
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        # Blacklist the proxy
        await manager.report_failure("http://proxy.example.com:8080", "Error")

        entry = manager._proxies["http://proxy.example.com:8080"]
        assert entry.stats.is_healthy is False

        # Wait for blacklist to expire
        await asyncio.sleep(1.1)

        proxy = await manager.get_next()
        assert proxy == "http://proxy.example.com:8080"

        await manager.stop()

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting stats."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080, name="test"))

        await manager.start()
        await manager.report_success("http://proxy.example.com:8080", 100.0)

        stats = manager.get_stats()

        assert stats["total_proxies"] == 1
        assert stats["available_proxies"] == 1
        assert "test" in stats["proxies"]
        assert stats["proxies"]["test"]["requests_success"] == 1

        await manager.stop()


class TestProxyManagerHealthCheck:
    """Tests for health checking."""

    @pytest.mark.asyncio
    async def test_check_proxy_success(self):
        """Test successful health check."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)

            mock_client.return_value = mock_instance

            result = await manager.check_proxy("http://proxy.example.com:8080")

            assert result is True

    @pytest.mark.asyncio
    async def test_check_proxy_failure(self):
        """Test failed health check."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(side_effect=Exception("Connection failed"))
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)

            mock_client.return_value = mock_instance

            result = await manager.check_proxy("http://proxy.example.com:8080")

            assert result is False

    @pytest.mark.asyncio
    async def test_check_proxy_not_found(self):
        """Test checking nonexistent proxy."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)

        result = await manager.check_proxy("http://nonexistent:8080")

        assert result is False

    @pytest.mark.asyncio
    async def test_check_all_proxies(self):
        """Test checking all proxies."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxies_from_urls([
            "http://proxy1:8080",
            "http://proxy2:8080",
        ])

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)

            mock_client.return_value = mock_instance

            results = await manager.check_all_proxies()

            assert len(results) == 2
            assert all(results.values())


class TestProxyManagerWeightedRotation:
    """Tests for weighted rotation."""

    @pytest.mark.asyncio
    async def test_weighted_rotation_prefers_healthy(self):
        """Test weighted rotation prefers healthy proxies."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.WEIGHTED,
            auto_health_check=False,
        )
        manager = ProxyManager(config)
        manager.add_proxies_from_urls([
            "http://proxy1:8080",
            "http://proxy2:8080",
        ])

        await manager.start()

        # Make proxy1 have good stats
        for _ in range(10):
            await manager.report_success("http://proxy1:8080", 50.0)

        # Make proxy2 have bad stats
        for _ in range(8):
            await manager.report_failure("http://proxy2:8080", "Error")
        for _ in range(2):
            await manager.report_success("http://proxy2:8080", 500.0)

        # Get multiple proxies and count
        counts = {"http://proxy1:8080": 0, "http://proxy2:8080": 0}
        for _ in range(100):
            proxy = await manager.get_next()
            if proxy:
                counts[proxy] += 1

        # proxy1 should be selected more often
        assert counts["http://proxy1:8080"] > counts["http://proxy2:8080"]

        await manager.stop()


class TestProxyManagerDefaultStrategy:
    """Tests for default strategy fallback."""

    @pytest.mark.asyncio
    async def test_get_next_default_strategy(self):
        """Test get_next with unknown strategy falls back to round-robin."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.ROUND_ROBIN,
            auto_health_check=False,
        )
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        proxy = await manager.get_next()
        assert proxy is not None

        await manager.stop()


class TestGetProxyManagerSingleton:
    """Tests for get_proxy_manager singleton."""

    @pytest.mark.asyncio
    async def test_get_proxy_manager(self):
        """Test get_proxy_manager returns singleton."""
        import app.ingestion.scrapers.proxy_manager as pm_module

        # Reset singleton
        pm_module._manager = None

        manager1 = await get_proxy_manager()
        manager2 = await get_proxy_manager()

        assert manager1 is manager2

        # Cleanup
        await manager1.stop()
        pm_module._manager = None

    @pytest.mark.asyncio
    async def test_get_proxy_manager_with_config(self):
        """Test get_proxy_manager with custom config."""
        import app.ingestion.scrapers.proxy_manager as pm_module

        # Reset singleton
        pm_module._manager = None

        config = ProxyManagerConfig(rotation_strategy=RotationStrategy.RANDOM)
        manager = await get_proxy_manager(config)

        assert manager.config.rotation_strategy == RotationStrategy.RANDOM

        # Cleanup
        await manager.stop()
        pm_module._manager = None


class TestProxyManagerEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_start_with_auto_health_check(self):
        """Test start with auto health check enabled."""
        config = ProxyManagerConfig(
            auto_health_check=True,
            health_check_interval_seconds=1000,  # Long interval
        )
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        assert manager._running is True
        assert manager._health_check_task is not None

        await manager.stop()

    @pytest.mark.asyncio
    async def test_start_already_running(self):
        """Test start when already running."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)

        await manager.start()
        await manager.start()  # Should not start again

        assert manager._running is True

        await manager.stop()

    @pytest.mark.asyncio
    async def test_report_success_unknown_proxy(self):
        """Test reporting success for unknown proxy."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)

        await manager.start()

        # Should not raise
        await manager.report_success("http://unknown:8080", 100.0)

        await manager.stop()

    @pytest.mark.asyncio
    async def test_report_failure_unknown_proxy(self):
        """Test reporting failure for unknown proxy."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)

        await manager.start()

        # Should not raise
        await manager.report_failure("http://unknown:8080", "Error")

        await manager.stop()

    @pytest.mark.asyncio
    async def test_check_proxy_http_error(self):
        """Test health check with non-200 response."""
        config = ProxyManagerConfig(auto_health_check=False)
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 503

            mock_instance = AsyncMock()
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)

            mock_client.return_value = mock_instance

            result = await manager.check_proxy("http://proxy.example.com:8080")

            assert result is False

    @pytest.mark.asyncio
    async def test_weighted_zero_weight(self):
        """Test weighted rotation with zero total weight."""
        config = ProxyManagerConfig(
            rotation_strategy=RotationStrategy.WEIGHTED,
            auto_health_check=False,
        )
        manager = ProxyManager(config)
        manager.add_proxy(ProxyConfig(host="proxy.example.com", port=8080))

        await manager.start()

        # Entry has default stats (no requests yet)
        proxy = await manager.get_next()
        assert proxy is not None

        await manager.stop()
