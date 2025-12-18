"""
Tests for BrowserPool manager.

S39 - Browser Pool Tests
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.scrapers.browser_pool import (
    BrowserInstance,
    BrowserPool,
    BrowserState,
    PoolConfig,
    PoolStats,
    get_browser_pool,
)
from app.ingestion.scrapers.playwright_base import BrowserType, StealthLevel


class TestBrowserState:
    """Tests for BrowserState enum."""

    def test_browser_states(self):
        """Test all browser states."""
        assert BrowserState.IDLE.value == "idle"
        assert BrowserState.BUSY.value == "busy"
        assert BrowserState.RECYCLING.value == "recycling"
        assert BrowserState.CLOSED.value == "closed"


class TestBrowserInstance:
    """Tests for BrowserInstance."""

    def test_default_instance(self):
        """Test default instance creation."""
        instance = BrowserInstance(
            id="browser-1",
            browser=MagicMock(),
            context=MagicMock(),
        )

        assert instance.id == "browser-1"
        assert instance.state == BrowserState.IDLE
        assert instance.pages_processed == 0
        assert instance.errors == 0
        assert instance.proxy is None

    def test_mark_busy(self):
        """Test marking instance as busy."""
        instance = BrowserInstance(
            id="browser-1",
            browser=MagicMock(),
            context=MagicMock(),
        )

        instance.mark_busy()

        assert instance.state == BrowserState.BUSY
        assert instance.last_used_at is not None

    def test_mark_idle(self):
        """Test marking instance as idle."""
        instance = BrowserInstance(
            id="browser-1",
            browser=MagicMock(),
            context=MagicMock(),
        )
        instance.mark_busy()

        instance.mark_idle()

        assert instance.state == BrowserState.IDLE
        assert instance.pages_processed == 1

    def test_mark_error(self):
        """Test marking instance error."""
        instance = BrowserInstance(
            id="browser-1",
            browser=MagicMock(),
            context=MagicMock(),
        )

        instance.mark_error()

        assert instance.errors == 1
        assert instance.state == BrowserState.IDLE

    def test_should_recycle_by_pages(self):
        """Test recycling threshold by pages."""
        instance = BrowserInstance(
            id="browser-1",
            browser=MagicMock(),
            context=MagicMock(),
        )
        instance.pages_processed = 100

        assert instance.should_recycle(max_pages=100, max_errors=5) is True
        assert instance.should_recycle(max_pages=101, max_errors=5) is False

    def test_should_recycle_by_errors(self):
        """Test recycling threshold by errors."""
        instance = BrowserInstance(
            id="browser-1",
            browser=MagicMock(),
            context=MagicMock(),
        )
        instance.errors = 5

        assert instance.should_recycle(max_pages=100, max_errors=5) is True
        assert instance.should_recycle(max_pages=100, max_errors=6) is False


class TestPoolConfig:
    """Tests for PoolConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = PoolConfig()

        assert config.min_instances == 1
        assert config.max_instances == 5
        assert config.max_pages_per_instance == 100
        assert config.max_errors_per_instance == 5
        assert config.idle_timeout_seconds == 300
        assert config.browser_type == BrowserType.CHROMIUM
        assert config.headless is True
        assert config.stealth_level == StealthLevel.STANDARD
        assert config.proxies == []
        assert config.proxy_rotation is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = PoolConfig(
            min_instances=2,
            max_instances=10,
            max_pages_per_instance=50,
            proxies=["proxy1", "proxy2"],
        )

        assert config.min_instances == 2
        assert config.max_instances == 10
        assert config.max_pages_per_instance == 50
        assert len(config.proxies) == 2


class TestPoolStats:
    """Tests for PoolStats."""

    def test_default_stats(self):
        """Test default stats."""
        stats = PoolStats()

        assert stats.total_instances_created == 0
        assert stats.total_instances_recycled == 0
        assert stats.total_pages_processed == 0
        assert stats.total_errors == 0
        assert stats.current_active == 0
        assert stats.current_idle == 0
        assert stats.started_at is None

    def test_to_dict(self):
        """Test conversion to dict."""
        stats = PoolStats(
            total_instances_created=5,
            total_pages_processed=100,
            current_active=2,
            started_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )

        d = stats.to_dict()

        assert d["total_instances_created"] == 5
        assert d["total_pages_processed"] == 100
        assert d["current_active"] == 2
        assert d["started_at"] == "2024-01-01T12:00:00+00:00"

    def test_to_dict_no_started_at(self):
        """Test to_dict without started_at."""
        stats = PoolStats()

        d = stats.to_dict()

        assert d["started_at"] is None


class TestBrowserPool:
    """Tests for BrowserPool."""

    def test_pool_creation(self):
        """Test creating a pool."""
        pool = BrowserPool()

        assert pool.config is not None
        assert pool._instances == {}
        assert pool._initialized is False

    def test_pool_custom_config(self):
        """Test pool with custom config."""
        config = PoolConfig(max_instances=10)
        pool = BrowserPool(config)

        assert pool.config.max_instances == 10

    @pytest.mark.asyncio
    async def test_initialize_mock_mode(self):
        """Test initialization without Playwright (mock mode)."""
        pool = BrowserPool()

        await pool.initialize()

        assert pool._initialized is True
        assert pool.stats.started_at is not None

        await pool.close()

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialize when already initialized."""
        pool = BrowserPool()

        await pool.initialize()
        await pool.initialize()  # Should not reinitialize

        assert pool._initialized is True

        await pool.close()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing pool."""
        pool = BrowserPool()

        await pool.initialize()
        await pool.close()

        assert pool._initialized is False
        assert len(pool._instances) == 0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using pool as context manager."""
        async with BrowserPool() as pool:
            assert pool._initialized is True

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting pool stats."""
        pool = BrowserPool()
        await pool.initialize()

        stats = pool.get_stats()

        assert "total_instances_created" in stats
        assert "current_active" in stats
        assert "current_idle" in stats

        await pool.close()


class TestBrowserPoolWithMock:
    """Tests with mocked Playwright."""

    @pytest.fixture
    def mock_playwright(self):
        """Create mock Playwright objects."""
        mock_page = AsyncMock()
        mock_page.close = AsyncMock()

        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.add_init_script = AsyncMock()
        mock_context.close = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.firefox = mock_launcher
        mock_pw.webkit = mock_launcher
        mock_pw.stop = AsyncMock()

        return {
            "playwright": mock_pw,
            "browser": mock_browser,
            "context": mock_context,
            "page": mock_page,
            "launcher": mock_launcher,
        }

    @pytest.mark.asyncio
    async def test_acquire_and_release(self, mock_playwright):
        """Test acquiring and releasing instances."""
        config = PoolConfig(min_instances=1, max_instances=3)
        pool = BrowserPool(config)

        # Inject mock
        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create an instance manually
        instance = await pool._create_instance()
        assert instance is not None

        # Acquire
        acquired = await pool.acquire()
        assert acquired is not None
        assert acquired.state == BrowserState.BUSY
        assert pool.stats.current_active == 1

        # Release
        await pool.release(acquired)
        assert acquired.state == BrowserState.IDLE
        assert pool.stats.current_idle == 1
        assert pool.stats.total_pages_processed == 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_acquire_creates_new_instance(self, mock_playwright):
        """Test acquire creates new instance when needed."""
        config = PoolConfig(min_instances=0, max_instances=3)
        pool = BrowserPool(config)

        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        instance = await pool.acquire()

        assert instance is not None
        assert pool.stats.total_instances_created == 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_acquire_no_available_at_max(self, mock_playwright):
        """Test acquire returns None at max capacity."""
        config = PoolConfig(min_instances=1, max_instances=1)
        pool = BrowserPool(config)

        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create and acquire the only instance
        instance1 = await pool._create_instance()
        await pool.acquire()

        # Try to acquire another
        instance2 = await pool.acquire()

        assert instance2 is None

        await pool.close()

    @pytest.mark.asyncio
    async def test_release_with_error(self, mock_playwright):
        """Test releasing with error flag."""
        config = PoolConfig(min_instances=1)
        pool = BrowserPool(config)

        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        await pool._create_instance()
        instance = await pool.acquire()

        await pool.release(instance, error=True)

        assert instance.errors == 1
        assert pool.stats.total_errors == 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_release_unknown_instance(self, mock_playwright):
        """Test releasing unknown instance."""
        pool = BrowserPool()
        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True

        unknown = BrowserInstance(
            id="unknown",
            browser=MagicMock(),
            context=MagicMock(),
        )

        # Should not raise
        await pool.release(unknown)

        await pool.close()

    @pytest.mark.asyncio
    async def test_instance_recycling(self, mock_playwright):
        """Test instance recycling when threshold reached."""
        config = PoolConfig(
            min_instances=1,
            max_pages_per_instance=2,
        )
        pool = BrowserPool(config)

        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create instance
        await pool._create_instance()
        initial_count = pool.stats.total_instances_created

        # Use until recycle threshold
        for _ in range(3):
            instance = await pool.acquire()
            if instance:
                await pool.release(instance)

        # Should have recycled
        assert pool.stats.total_instances_recycled >= 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_cleanup_idle(self, mock_playwright):
        """Test cleanup of idle instances."""
        config = PoolConfig(
            min_instances=1,
            max_instances=3,
            idle_timeout_seconds=0,  # Immediate timeout
        )
        pool = BrowserPool(config)

        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create multiple instances
        for _ in range(3):
            instance = await pool._create_instance()
            if instance:
                instance.last_used_at = datetime.now(timezone.utc) - timedelta(hours=1)

        closed = await pool.cleanup_idle()

        # Should close down to min_instances
        assert closed == 2
        assert len(pool._instances) == 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_cleanup_idle_keeps_minimum(self, mock_playwright):
        """Test cleanup keeps minimum instances."""
        config = PoolConfig(
            min_instances=2,
            max_instances=5,
            idle_timeout_seconds=0,
        )
        pool = BrowserPool(config)

        pool._playwright = mock_playwright["playwright"]
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create instances at minimum
        for _ in range(2):
            instance = await pool._create_instance()
            if instance:
                instance.last_used_at = datetime.now(timezone.utc) - timedelta(hours=1)

        closed = await pool.cleanup_idle()

        assert closed == 0
        assert len(pool._instances) == 2

        await pool.close()


class TestBrowserPoolProxyRotation:
    """Tests for proxy rotation."""

    def test_get_next_proxy_no_proxies(self):
        """Test get_next_proxy with no proxies."""
        pool = BrowserPool()

        proxy = pool._get_next_proxy()

        assert proxy is None

    def test_get_next_proxy_rotation(self):
        """Test proxy rotation."""
        config = PoolConfig(
            proxies=["proxy1", "proxy2", "proxy3"],
            proxy_rotation=True,
        )
        pool = BrowserPool(config)

        proxies = [pool._get_next_proxy() for _ in range(6)]

        assert proxies == ["proxy1", "proxy2", "proxy3", "proxy1", "proxy2", "proxy3"]

    def test_get_next_proxy_random(self):
        """Test random proxy selection."""
        config = PoolConfig(
            proxies=["proxy1", "proxy2", "proxy3"],
            proxy_rotation=False,
        )
        pool = BrowserPool(config)

        # Just ensure it returns a valid proxy
        for _ in range(10):
            proxy = pool._get_next_proxy()
            assert proxy in config.proxies


class TestBrowserPoolEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_close_without_initialize(self):
        """Test closing without initializing."""
        pool = BrowserPool()

        # Should not raise
        await pool.close()

    @pytest.mark.asyncio
    async def test_acquire_without_playwright(self):
        """Test acquire without Playwright installed."""
        pool = BrowserPool()
        pool._initialized = True
        pool._playwright = None

        instance = await pool.acquire()

        assert instance is None

    @pytest.mark.asyncio
    async def test_close_instance_not_found(self):
        """Test closing non-existent instance."""
        pool = BrowserPool()
        pool._initialized = True

        # Should not raise
        await pool._close_instance("nonexistent")

    @pytest.mark.asyncio
    async def test_create_instance_failure(self):
        """Test instance creation failure."""
        pool = BrowserPool()

        mock_pw = MagicMock()
        mock_pw.chromium = MagicMock()
        mock_pw.chromium.launch = AsyncMock(side_effect=Exception("Launch failed"))

        pool._playwright = mock_pw
        pool._initialized = True

        instance = await pool._create_instance()

        assert instance is None

    @pytest.mark.asyncio
    async def test_recycle_instance(self):
        """Test recycling an instance."""
        pool = BrowserPool()

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create initial instance
        instance = await pool._create_instance()
        old_id = instance.id

        # Recycle
        new_instance = await pool._recycle_instance(old_id)

        assert new_instance is not None
        assert new_instance.id != old_id
        assert pool.stats.total_instances_recycled == 1

        await pool.close()


class TestGetBrowserPoolSingleton:
    """Tests for get_browser_pool singleton."""

    @pytest.mark.asyncio
    async def test_get_browser_pool(self):
        """Test get_browser_pool returns singleton."""
        import app.ingestion.scrapers.browser_pool as pool_module

        # Reset singleton
        pool_module._pool = None

        pool1 = await get_browser_pool()
        pool2 = await get_browser_pool()

        assert pool1 is pool2
        assert pool1._initialized is True

        # Cleanup
        await pool1.close()
        pool_module._pool = None

    @pytest.mark.asyncio
    async def test_get_browser_pool_with_config(self):
        """Test get_browser_pool with custom config."""
        import app.ingestion.scrapers.browser_pool as pool_module

        # Reset singleton
        pool_module._pool = None

        config = PoolConfig(max_instances=10)
        pool = await get_browser_pool(config)

        assert pool.config.max_instances == 10

        # Cleanup
        await pool.close()
        pool_module._pool = None


class TestBrowserInstanceTimestamps:
    """Tests for instance timestamps."""

    def test_created_at_set(self):
        """Test created_at is set automatically."""
        before = datetime.now(timezone.utc)

        instance = BrowserInstance(
            id="test",
            browser=MagicMock(),
            context=MagicMock(),
        )

        after = datetime.now(timezone.utc)

        assert before <= instance.created_at <= after

    def test_last_used_at_updated(self):
        """Test last_used_at is updated on mark_busy."""
        instance = BrowserInstance(
            id="test",
            browser=MagicMock(),
            context=MagicMock(),
        )

        assert instance.last_used_at is None

        before = datetime.now(timezone.utc)
        instance.mark_busy()
        after = datetime.now(timezone.utc)

        assert before <= instance.last_used_at <= after


class TestBrowserPoolStatsTracking:
    """Tests for stats tracking."""

    @pytest.mark.asyncio
    async def test_stats_after_multiple_operations(self):
        """Test stats after multiple operations."""
        pool = BrowserPool()

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create instances
        for _ in range(3):
            await pool._create_instance()

        assert pool.stats.total_instances_created == 3
        assert pool.stats.current_idle == 3

        # Acquire and release
        instance = await pool.acquire()
        assert pool.stats.current_active == 1
        assert pool.stats.current_idle == 2

        await pool.release(instance, error=True)
        assert pool.stats.current_active == 0
        assert pool.stats.current_idle == 3
        assert pool.stats.total_errors == 1

        await pool.close()


class TestPoolConfigBrowserTypes:
    """Tests for different browser type configurations."""

    @pytest.mark.asyncio
    async def test_firefox_pool(self):
        """Test pool with Firefox browser."""
        config = PoolConfig(browser_type=BrowserType.FIREFOX)
        pool = BrowserPool(config)

        await pool.initialize()
        assert pool._initialized is True
        await pool.close()

    @pytest.mark.asyncio
    async def test_webkit_pool(self):
        """Test pool with WebKit browser."""
        config = PoolConfig(browser_type=BrowserType.WEBKIT)
        pool = BrowserPool(config)

        await pool.initialize()
        assert pool._initialized is True
        await pool.close()


class TestPoolCloseInstanceStates:
    """Tests for closing instances in different states."""

    @pytest.mark.asyncio
    async def test_close_idle_instance(self):
        """Test closing an idle instance."""
        pool = BrowserPool()

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        instance = await pool._create_instance()
        assert pool.stats.current_idle == 1

        await pool._close_instance(instance.id)

        assert pool.stats.current_idle == 0
        assert instance.id not in pool._instances

        await pool.close()

    @pytest.mark.asyncio
    async def test_close_busy_instance(self):
        """Test closing a busy instance."""
        pool = BrowserPool()

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_browser)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        await pool._create_instance()
        instance = await pool.acquire()

        assert pool.stats.current_active == 1

        await pool._close_instance(instance.id)

        assert pool.stats.current_active == 0

        await pool.close()

    @pytest.mark.asyncio
    async def test_close_instance_exception(self):
        """Test closing instance with exception."""
        pool = BrowserPool()

        mock_context = AsyncMock()
        mock_context.close = AsyncMock(side_effect=Exception("Close failed"))

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()

        instance = BrowserInstance(
            id="test",
            browser=mock_browser,
            context=mock_context,
            state=BrowserState.IDLE,
        )
        pool._instances["test"] = instance
        pool._initialized = True
        pool.stats.current_idle = 1

        # Should not raise
        await pool._close_instance("test")

        assert "test" not in pool._instances


class TestBrowserPoolAcquireEdgeCases:
    """Additional acquire tests for coverage."""

    @pytest.mark.asyncio
    async def test_acquire_creates_if_below_max(self):
        """Test acquire creates new instance if below max."""
        config = PoolConfig(min_instances=0, max_instances=3)
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # No instances yet, acquire should create one
        instance = await pool.acquire()

        assert instance is not None
        assert pool.stats.total_instances_created == 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_acquire_with_proxy(self):
        """Test acquire with proxy rotation."""
        config = PoolConfig(
            proxies=["proxy1:8080", "proxy2:8080"],
            proxy_rotation=True,
        )
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        instance1 = await pool._create_instance()
        instance2 = await pool._create_instance()

        assert instance1.proxy == "proxy1:8080"
        assert instance2.proxy == "proxy2:8080"

        await pool.close()

    @pytest.mark.asyncio
    async def test_cleanup_idle_no_instances_to_close(self):
        """Test cleanup_idle with no eligible instances."""
        config = PoolConfig(
            min_instances=2,
            idle_timeout_seconds=3600,  # Long timeout
        )
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create instances and set recent last_used_at
        for _ in range(3):
            instance = await pool._create_instance()
            if instance:
                instance.last_used_at = datetime.now(timezone.utc)

        closed = await pool.cleanup_idle()

        # Should close only 1 (3 - min_instances of 2)
        assert closed <= 1

        await pool.close()

    @pytest.mark.asyncio
    async def test_cleanup_idle_no_last_used(self):
        """Test cleanup_idle when instance has no last_used_at."""
        config = PoolConfig(
            min_instances=0,
            idle_timeout_seconds=0,
        )
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.close = AsyncMock()
        mock_context.add_init_script = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create instance without setting last_used_at
        instance = await pool._create_instance()
        assert instance.last_used_at is None

        closed = await pool.cleanup_idle()

        # Should not close because last_used_at is None
        assert closed == 0

        await pool.close()


class TestBrowserPoolStealthLevel:
    """Tests for stealth level in pool config."""

    @pytest.mark.asyncio
    async def test_pool_with_stealth_none(self):
        """Test pool with no stealth."""
        config = PoolConfig(stealth_level=StealthLevel.NONE)
        pool = BrowserPool(config)

        await pool.initialize()
        assert pool._initialized is True
        await pool.close()

    @pytest.mark.asyncio
    async def test_pool_stealth_level(self):
        """Test pool inherits stealth level."""
        config = PoolConfig(stealth_level=StealthLevel.AGGRESSIVE)
        pool = BrowserPool(config)

        assert pool.config.stealth_level == StealthLevel.AGGRESSIVE


class TestBrowserPoolReleaseEdgeCases:
    """Edge cases for release method."""

    @pytest.mark.asyncio
    async def test_release_unknown_instance_id(self):
        """Test releasing instance with unknown ID."""
        pool = BrowserPool()
        pool._initialized = True

        mock_instance = BrowserInstance(
            id="unknown-id",
            browser=MagicMock(),
            context=MagicMock(),
        )

        # Should not raise even though ID not in _instances
        await pool.release(mock_instance)


class TestBrowserPoolCreateInstanceEdgeCases:
    """Edge cases for _create_instance method."""

    @pytest.mark.asyncio
    async def test_create_instance_with_proxy(self):
        """Test creating instance with proxy."""
        config = PoolConfig(proxies=["http://proxy:8080"])
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.add_init_script = AsyncMock()
        mock_context.close = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        instance = await pool._create_instance()

        assert instance is not None
        assert instance.proxy == "http://proxy:8080"

        # Verify proxy was passed to launch
        mock_launcher.launch.assert_called_once()
        call_kwargs = mock_launcher.launch.call_args[1]
        assert "proxy" in call_kwargs
        assert call_kwargs["proxy"]["server"] == "http://proxy:8080"

        await pool.close()

    @pytest.mark.asyncio
    async def test_create_instance_with_stealth(self):
        """Test creating instance with stealth settings."""
        config = PoolConfig(stealth_level=StealthLevel.STANDARD)
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.add_init_script = AsyncMock()
        mock_context.close = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        instance = await pool._create_instance()

        assert instance is not None
        # Stealth script should have been added
        mock_context.add_init_script.assert_called()

        await pool.close()


class TestBrowserPoolCloseEdgeCases:
    """Edge cases for close method."""

    @pytest.mark.asyncio
    async def test_close_empty_pool(self):
        """Test closing empty pool."""
        pool = BrowserPool()
        pool._initialized = True

        # Should not raise
        await pool.close()

        assert pool._initialized is False

    @pytest.mark.asyncio
    async def test_close_with_multiple_instances(self):
        """Test closing pool with multiple instances."""
        pool = BrowserPool()

        mock_context = AsyncMock()
        mock_context.add_init_script = AsyncMock()
        mock_context.close = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create multiple instances
        for _ in range(3):
            await pool._create_instance()

        assert len(pool._instances) == 3

        await pool.close()

        assert len(pool._instances) == 0
        assert pool._initialized is False


class TestBrowserPoolAcquireMoreCases:
    """More acquire edge cases."""

    @pytest.mark.asyncio
    async def test_acquire_all_busy_at_max(self):
        """Test acquire when all instances are busy at max capacity."""
        config = PoolConfig(min_instances=1, max_instances=1)
        pool = BrowserPool(config)

        mock_context = AsyncMock()
        mock_context.add_init_script = AsyncMock()
        mock_context.close = AsyncMock()

        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_launcher = AsyncMock()
        mock_launcher.launch = AsyncMock(return_value=mock_browser)

        mock_pw = MagicMock()
        mock_pw.chromium = mock_launcher
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Create one instance
        await pool._create_instance()

        # Acquire it
        instance1 = await pool.acquire()
        assert instance1 is not None
        assert instance1.state == BrowserState.BUSY

        # Try to acquire another - should return None
        instance2 = await pool.acquire()
        assert instance2 is None

        await pool.close()

    @pytest.mark.asyncio
    async def test_acquire_create_fails(self):
        """Test acquire when creating new instance fails."""
        config = PoolConfig(min_instances=0, max_instances=5)
        pool = BrowserPool(config)

        mock_pw = MagicMock()
        mock_pw.chromium = MagicMock()
        mock_pw.chromium.launch = AsyncMock(side_effect=Exception("Launch failed"))
        mock_pw.stop = AsyncMock()

        pool._playwright = mock_pw
        pool._initialized = True
        pool.stats.started_at = datetime.now(timezone.utc)

        # Acquire should try to create but fail
        instance = await pool.acquire()

        assert instance is None

        await pool.close()
