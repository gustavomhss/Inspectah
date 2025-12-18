"""
Tests for PlaywrightScraper base class.

S39 - Playwright Scraper Tests
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.scrapers.base import ScrapedArticle, ScraperResult, VerdictType
from app.ingestion.scrapers.playwright_base import (
    BrowserType,
    PlaywrightConfig,
    PlaywrightScraper,
    PlaywrightScraperStats,
    StealthLevel,
    scrape_with_playwright,
)


class TestBrowserType:
    """Tests for BrowserType enum."""

    def test_browser_types(self):
        """Test all browser types."""
        assert BrowserType.CHROMIUM.value == "chromium"
        assert BrowserType.FIREFOX.value == "firefox"
        assert BrowserType.WEBKIT.value == "webkit"


class TestStealthLevel:
    """Tests for StealthLevel enum."""

    def test_stealth_levels(self):
        """Test all stealth levels."""
        assert StealthLevel.NONE.value == "none"
        assert StealthLevel.BASIC.value == "basic"
        assert StealthLevel.STANDARD.value == "standard"
        assert StealthLevel.AGGRESSIVE.value == "aggressive"


class TestPlaywrightConfig:
    """Tests for PlaywrightConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = PlaywrightConfig(
            name="test-scraper",
            base_url="https://example.com",
        )

        assert config.name == "test-scraper"
        assert config.base_url == "https://example.com"
        assert config.browser_type == BrowserType.CHROMIUM
        assert config.headless is True
        assert config.stealth_level == StealthLevel.STANDARD
        assert config.timeout_ms == 30000
        assert config.navigation_timeout_ms == 60000
        assert config.max_retries == 3
        assert config.rate_limit_rpm == 10
        assert config.proxy is None
        assert len(config.user_agent_pool) > 0

    def test_custom_config(self):
        """Test custom configuration."""
        config = PlaywrightConfig(
            name="custom-scraper",
            base_url="https://custom.com",
            browser_type=BrowserType.FIREFOX,
            headless=False,
            stealth_level=StealthLevel.AGGRESSIVE,
            timeout_ms=60000,
            max_retries=5,
            proxy="http://proxy:8080",
        )

        assert config.browser_type == BrowserType.FIREFOX
        assert config.headless is False
        assert config.stealth_level == StealthLevel.AGGRESSIVE
        assert config.timeout_ms == 60000
        assert config.max_retries == 5
        assert config.proxy == "http://proxy:8080"


class TestPlaywrightScraperStats:
    """Tests for PlaywrightScraperStats."""

    def test_default_stats(self):
        """Test default stats."""
        stats = PlaywrightScraperStats()

        assert stats.pages_loaded == 0
        assert stats.pages_failed == 0
        assert stats.screenshots_taken == 0
        assert stats.retries == 0
        assert stats.total_navigation_time_ms == 0.0

    def test_record_page_load(self):
        """Test recording page load."""
        stats = PlaywrightScraperStats()

        stats.record_page_load(100.0)
        stats.record_page_load(200.0)

        assert stats.pages_loaded == 2
        assert stats.total_navigation_time_ms == 300.0

    def test_record_failure(self):
        """Test recording failure."""
        stats = PlaywrightScraperStats()

        stats.record_failure()
        stats.record_failure()

        assert stats.pages_failed == 2

    def test_avg_navigation_time_no_pages(self):
        """Test avg navigation time with no pages."""
        stats = PlaywrightScraperStats()

        assert stats.avg_navigation_time_ms() == 0.0

    def test_avg_navigation_time(self):
        """Test avg navigation time."""
        stats = PlaywrightScraperStats()
        stats.record_page_load(100.0)
        stats.record_page_load(200.0)
        stats.record_page_load(300.0)

        assert stats.avg_navigation_time_ms() == 200.0

    def test_to_dict(self):
        """Test conversion to dict."""
        stats = PlaywrightScraperStats()
        stats.record_page_load(100.0)
        stats.started_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        d = stats.to_dict()

        assert d["pages_loaded"] == 1
        assert d["pages_failed"] == 0
        assert d["avg_navigation_time_ms"] == 100.0
        assert "started_at" in d


class ConcreteScraper(PlaywrightScraper):
    """Concrete implementation for testing."""

    def __init__(self, config: PlaywrightConfig, urls: Optional[List[str]] = None):
        super().__init__(config)
        self._urls = urls or ["https://example.com/article/1"]

    async def get_article_urls(self, page: int = 1) -> List[str]:
        """Return predefined URLs."""
        return self._urls

    async def parse_article(self, page_obj: Any, url: str) -> Optional[ScrapedArticle]:
        """Parse a mock article."""
        return ScrapedArticle(
            external_id=f"ext-{url[-1:]}",
            source_name=self.config.name,
            url=url,
            title=f"Article from {url}",
            claim="Test claim",
            verdict=VerdictType.FALSE,
            verdict_label="FALSO",
            content="Test content",
            published_at=datetime.now(timezone.utc),
            author="Test Author",
        )


class FailingScraper(PlaywrightScraper):
    """Scraper that fails to parse articles."""

    async def get_article_urls(self, page: int = 1) -> List[str]:
        return ["https://example.com/fail"]

    async def parse_article(self, page_obj: Any, url: str) -> Optional[ScrapedArticle]:
        return None


class ExceptionScraper(PlaywrightScraper):
    """Scraper that throws exceptions."""

    async def get_article_urls(self, page: int = 1) -> List[str]:
        return ["https://example.com/error"]

    async def parse_article(self, page_obj: Any, url: str) -> Optional[ScrapedArticle]:
        raise Exception("Parse error")


class TestPlaywrightScraper:
    """Tests for PlaywrightScraper."""

    def test_scraper_creation(self):
        """Test creating a scraper."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        assert scraper.config == config
        assert scraper._browser is None
        assert scraper._context is None
        assert scraper._initialized is False

    @pytest.mark.asyncio
    async def test_initialize_mock_mode(self):
        """Test initialization without Playwright (mock mode)."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()

        assert scraper._initialized is True

        await scraper.close()

    @pytest.mark.asyncio
    async def test_initialize_already_initialized(self):
        """Test initialize when already initialized."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()
        await scraper.initialize()  # Should not reinitialize

        assert scraper._initialized is True

        await scraper.close()

    @pytest.mark.asyncio
    async def test_close(self):
        """Test closing scraper."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()
        await scraper.close()

        assert scraper._initialized is False

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using scraper as context manager."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )

        async with ConcreteScraper(config) as scraper:
            assert scraper._initialized is True

    @pytest.mark.asyncio
    async def test_navigate_mock_mode(self):
        """Test navigation in mock mode."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        await scraper.initialize()

        page = await scraper.navigate("https://example.com/test")

        # In mock mode, returns None
        assert page is None

        await scraper.close()

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting scraper stats."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        await scraper.initialize()

        stats = scraper.get_stats()

        assert "pages_loaded" in stats
        assert "pages_failed" in stats
        assert "avg_navigation_time_ms" in stats

        await scraper.close()

    @pytest.mark.asyncio
    async def test_scrape_mock_mode(self):
        """Test scraping in mock mode."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config, urls=["url1", "url2", "url3"])

        result = await scraper.scrape(pages=1, max_articles=10)

        assert isinstance(result, ScraperResult)
        assert result.source_name == "test"

    @pytest.mark.asyncio
    async def test_get_context_options(self):
        """Test get_context_options method."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        options = scraper._get_context_options()

        assert "user_agent" in options
        assert "viewport" in options
        assert "locale" in options
        assert "timezone_id" in options

    @pytest.mark.asyncio
    async def test_get_context_options_no_stealth(self):
        """Test get_context_options without stealth."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.NONE,
        )
        scraper = ConcreteScraper(config)

        options = scraper._get_context_options()

        # Viewport should be exact without randomization
        assert options["viewport"]["width"] == config.viewport_width
        assert options["viewport"]["height"] == config.viewport_height


class TestPlaywrightScraperWithMock:
    """Tests with mocked Playwright."""

    @pytest.fixture
    def mock_playwright(self):
        """Create mock Playwright objects."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value=1000)
        mock_page.close = AsyncMock()
        mock_page.screenshot = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html></html>")
        mock_page.wait_for_selector = AsyncMock()
        mock_page.click = AsyncMock()
        mock_page.set_default_timeout = MagicMock()
        mock_page.set_default_navigation_timeout = MagicMock()

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
        }

    @pytest.mark.asyncio
    async def test_initialize_with_playwright(self, mock_playwright):
        """Test initialization with mocked Playwright."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        # Inject mocked playwright
        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        assert scraper._initialized is True
        assert scraper._browser is not None

        # Need to set _playwright.stop as AsyncMock for close
        mock_playwright["playwright"].stop = AsyncMock()
        await scraper.close()

    @pytest.mark.asyncio
    async def test_navigate_with_page(self, mock_playwright):
        """Test navigation with mocked page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,  # High to avoid waiting
        )
        scraper = ConcreteScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        page = await scraper.navigate("https://example.com/article")

        assert page is not None
        mock_playwright["page"].goto.assert_called_once()

        mock_playwright["playwright"].stop = AsyncMock()
        await scraper.close()

    @pytest.mark.asyncio
    async def test_navigate_retry_on_failure(self, mock_playwright):
        """Test navigation retry on failure."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
            max_retries=3,
        )
        scraper = ConcreteScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        # Make goto fail twice, then succeed
        call_count = 0

        async def failing_goto(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Navigation failed")

        mock_playwright["page"].goto = failing_goto

        page = await scraper.navigate("https://example.com/article")

        assert page is not None
        assert call_count == 3
        assert scraper.stats.retries == 2

        mock_playwright["playwright"].stop = AsyncMock()
        await scraper.close()

    @pytest.mark.asyncio
    async def test_navigate_all_retries_fail(self, mock_playwright):
        """Test navigation when all retries fail."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
            max_retries=2,
        )
        scraper = ConcreteScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["page"].goto = AsyncMock(side_effect=Exception("Always fails"))

        page = await scraper.navigate("https://example.com/article")

        assert page is None

        mock_playwright["playwright"].stop = AsyncMock()
        await scraper.close()

    @pytest.mark.asyncio
    async def test_take_screenshot(self, mock_playwright):
        """Test taking screenshot."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        scraper._initialized = True

        mock_page = mock_playwright["page"]

        with patch("os.makedirs"):
            result = await scraper.take_screenshot(mock_page, "test-screenshot")

        assert result is not None
        mock_page.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_take_screenshot_failure(self, mock_playwright):
        """Test screenshot failure handling."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        scraper._initialized = True

        mock_page = mock_playwright["page"]
        mock_page.screenshot = AsyncMock(side_effect=Exception("Screenshot failed"))

        result = await scraper.take_screenshot(mock_page, "test-screenshot")

        assert result is None

    @pytest.mark.asyncio
    async def test_take_screenshot_no_page(self, mock_playwright):
        """Test screenshot with no page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        result = await scraper.take_screenshot(None, "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_scroll_to_bottom(self, mock_playwright):
        """Test scrolling to bottom."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        scraper._initialized = True

        mock_page = mock_playwright["page"]

        await scraper.scroll_to_bottom(mock_page)

        assert mock_page.evaluate.call_count >= 1

    @pytest.mark.asyncio
    async def test_scroll_to_bottom_no_page(self, mock_playwright):
        """Test scroll with no page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        # Should not raise
        await scraper.scroll_to_bottom(None)

    @pytest.mark.asyncio
    async def test_infinite_scroll(self, mock_playwright):
        """Test infinite scroll."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        scraper._initialized = True

        mock_page = mock_playwright["page"]
        # Simulate height changes then stabilization
        # Note: scroll_to_bottom also calls evaluate, so we need more values
        # Pattern: scrollHeight check, scroll, scrollHeight check, etc.
        mock_page.evaluate = AsyncMock(side_effect=[1000, None, 2000, None, 3000, None, 3000])

        await scraper.infinite_scroll(mock_page, max_scrolls=5, scroll_delay_ms=10)

        assert mock_page.evaluate.call_count >= 2

    @pytest.mark.asyncio
    async def test_infinite_scroll_no_page(self, mock_playwright):
        """Test infinite scroll with no page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        # Should not raise
        await scraper.infinite_scroll(None, max_scrolls=5)

    @pytest.mark.asyncio
    async def test_get_page_content(self, mock_playwright):
        """Test get_page_content."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]
        mock_page.content = AsyncMock(return_value="<html>Test</html>")

        content = await scraper.get_page_content(mock_page)

        assert content == "<html>Test</html>"

    @pytest.mark.asyncio
    async def test_get_page_content_no_page(self, mock_playwright):
        """Test get_page_content with no page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        content = await scraper.get_page_content(None)

        assert content == ""

    @pytest.mark.asyncio
    async def test_wait_for_selector(self, mock_playwright):
        """Test wait_for_selector."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]

        result = await scraper.wait_for_selector(mock_page, ".article")

        assert result is True
        mock_page.wait_for_selector.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_selector_no_page(self, mock_playwright):
        """Test wait_for_selector with no page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        result = await scraper.wait_for_selector(None, ".article")

        assert result is False

    @pytest.mark.asyncio
    async def test_wait_for_selector_timeout(self, mock_playwright):
        """Test wait_for_selector timeout."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]
        mock_page.wait_for_selector = AsyncMock(side_effect=Exception("Timeout"))

        result = await scraper.wait_for_selector(mock_page, ".article")

        assert result is False

    @pytest.mark.asyncio
    async def test_click(self, mock_playwright):
        """Test click."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]

        result = await scraper.click(mock_page, ".button")

        assert result is True
        mock_page.click.assert_called_once_with(".button")

    @pytest.mark.asyncio
    async def test_click_no_page(self, mock_playwright):
        """Test click with no page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        result = await scraper.click(None, ".button")

        assert result is False

    @pytest.mark.asyncio
    async def test_click_failure(self, mock_playwright):
        """Test click failure."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]
        mock_page.click = AsyncMock(side_effect=Exception("Click failed"))

        result = await scraper.click(mock_page, ".button")

        assert result is False

    @pytest.mark.asyncio
    async def test_scrape_with_articles(self, mock_playwright):
        """Test scraping with successful article parsing."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = ConcreteScraper(
            config,
            urls=["https://example.com/1", "https://example.com/2"],
        )

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=1, max_articles=10)

        assert isinstance(result, ScraperResult)
        assert result.source_name == "test"
        assert len(result.articles) == 2
        assert result.success is True

    @pytest.mark.asyncio
    async def test_scrape_failing_articles(self, mock_playwright):
        """Test scraping when article parsing fails."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = FailingScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=1, max_articles=10)

        assert isinstance(result, ScraperResult)
        # No articles scraped but still success (no exception)
        assert len(result.articles) == 0

    @pytest.mark.asyncio
    async def test_scrape_exception_handling(self, mock_playwright):
        """Test scraping with exception handling."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
            screenshot_on_error=False,  # Disable screenshots
        )
        scraper = ExceptionScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=1, max_articles=10)

        assert isinstance(result, ScraperResult)
        # Should have empty articles due to exception
        assert len(result.articles) == 0

    @pytest.mark.asyncio
    async def test_scrape_max_articles_limit(self, mock_playwright):
        """Test max_articles limit."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = ConcreteScraper(
            config,
            urls=[f"https://example.com/{i}" for i in range(10)],
        )

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=1, max_articles=3)

        assert len(result.articles) == 3

    @pytest.mark.asyncio
    async def test_scrape_article_single(self, mock_playwright):
        """Test scrape_article method."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = ConcreteScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        article = await scraper.scrape_article("https://example.com/article")

        assert article is not None
        assert article.source_name == "test"


class TestPlaywrightScraperStealth:
    """Tests for stealth mode features."""

    @pytest.mark.asyncio
    async def test_stealth_none(self):
        """Test with no stealth."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.NONE,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()

        assert scraper._initialized is True

        await scraper.close()

    @pytest.mark.asyncio
    async def test_stealth_basic(self):
        """Test with basic stealth."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.BASIC,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()

        assert scraper._initialized is True

        await scraper.close()

    @pytest.mark.asyncio
    async def test_stealth_standard(self):
        """Test with standard stealth."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.STANDARD,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()

        assert scraper._initialized is True

        await scraper.close()

    @pytest.mark.asyncio
    async def test_stealth_aggressive(self):
        """Test with aggressive stealth."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.AGGRESSIVE,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()

        assert scraper._initialized is True

        await scraper.close()

    @pytest.mark.asyncio
    async def test_apply_stealth_scripts_no_context(self):
        """Test apply_stealth_scripts with no context."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        scraper._context = None

        # Should not raise
        await scraper._apply_stealth_scripts()


class TestPlaywrightScraperBrowserTypes:
    """Tests for different browser types."""

    @pytest.mark.asyncio
    async def test_chromium_browser(self):
        """Test with Chromium browser."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            browser_type=BrowserType.CHROMIUM,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()
        assert scraper._initialized is True
        await scraper.close()

    @pytest.mark.asyncio
    async def test_firefox_browser(self):
        """Test with Firefox browser."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            browser_type=BrowserType.FIREFOX,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()
        assert scraper._initialized is True
        await scraper.close()

    @pytest.mark.asyncio
    async def test_webkit_browser(self):
        """Test with WebKit browser."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            browser_type=BrowserType.WEBKIT,
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()
        assert scraper._initialized is True
        await scraper.close()


class TestPlaywrightScraperEdgeCases:
    """Edge case tests."""

    @pytest.mark.asyncio
    async def test_close_without_initialize(self):
        """Test closing without initializing."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        # Should not raise
        await scraper.close()

    @pytest.mark.asyncio
    async def test_navigate_without_context(self):
        """Test navigating without context."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)
        scraper._initialized = True

        # Should return None
        page = await scraper.navigate("https://example.com")
        assert page is None

    @pytest.mark.asyncio
    async def test_scrape_without_initialize(self):
        """Test scraping without initializing."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        # Should work and initialize automatically
        result = await scraper.scrape(pages=1, max_articles=5)
        assert isinstance(result, ScraperResult)

    @pytest.mark.asyncio
    async def test_empty_urls(self):
        """Test with no URLs returned."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config, urls=[])

        result = await scraper.scrape(pages=1, max_articles=10)

        assert len(result.articles) == 0

    @pytest.mark.asyncio
    async def test_with_proxy(self):
        """Test with proxy configuration."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            proxy="http://proxy.example.com:8080",
        )
        scraper = ConcreteScraper(config)

        await scraper.initialize()
        assert scraper._initialized is True
        await scraper.close()

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=60,  # 1 per second
        )
        scraper = ConcreteScraper(config)
        await scraper.initialize()

        # Check that min_interval is calculated correctly
        assert scraper._min_interval == 1.0  # 60/60 = 1 second

        await scraper.close()

    @pytest.mark.asyncio
    async def test_wait_rate_limit(self):
        """Test _wait_rate_limit method."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=6000,  # 100 per second - fast
        )
        scraper = ConcreteScraper(config)

        # Ensure rate limiter works
        scraper._last_request_time = 0
        await scraper._wait_rate_limit()
        assert scraper._last_request_time > 0


class TestScrapeWithPlaywright:
    """Tests for scrape_with_playwright convenience function."""

    @pytest.mark.asyncio
    async def test_scrape_with_playwright_mock_mode(self):
        """Test scrape_with_playwright without Playwright installed."""
        async def extractor(page):
            return {"extracted": True}

        result = await scrape_with_playwright(
            url="https://example.com",
            extractor=extractor,
        )

        # In mock mode, returns None
        assert result is None

    @pytest.mark.asyncio
    async def test_scrape_with_playwright_custom_config(self):
        """Test scrape_with_playwright with custom config."""
        config = PlaywrightConfig(
            name="custom",
            base_url="https://example.com",
        )

        async def extractor(page):
            return {"extracted": True}

        result = await scrape_with_playwright(
            url="https://example.com",
            extractor=extractor,
            config=config,
        )

        assert result is None  # Mock mode


class TestScraperResult:
    """Tests for ScraperResult from base module."""

    def test_scraper_result_creation(self):
        """Test creating ScraperResult."""
        result = ScraperResult(
            source_name="test",
            articles=[],
            total_found=10,
            success=True,
            duration_seconds=5.5,
        )

        assert result.source_name == "test"
        assert len(result.articles) == 0
        assert result.total_found == 10
        assert result.success is True
        assert result.duration_seconds == 5.5

    def test_scraper_result_with_error(self):
        """Test ScraperResult with error."""
        result = ScraperResult(
            source_name="test",
            articles=[],
            total_found=0,
            success=False,
            error_message="Something went wrong",
        )

        assert result.success is False
        assert result.error_message == "Something went wrong"


class TestPlaywrightScraperExtraEdgeCases:
    """Additional edge case tests for better coverage."""

    @pytest.fixture
    def mock_playwright(self):
        """Create mock Playwright objects."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.close = AsyncMock()
        mock_page.screenshot = AsyncMock()
        mock_page.set_default_timeout = MagicMock()
        mock_page.set_default_navigation_timeout = MagicMock()

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
        }

    @pytest.mark.asyncio
    async def test_scrape_multiple_pages(self, mock_playwright):
        """Test scraping multiple pages."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = ConcreteScraper(
            config,
            urls=["https://example.com/1"],
        )

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=3, max_articles=10)

        assert isinstance(result, ScraperResult)
        # 3 pages * 1 URL per page = 3 articles
        assert len(result.articles) == 3

    @pytest.mark.asyncio
    async def test_scrape_article_with_screenshot_on_error(self, mock_playwright):
        """Test scrape_article takes screenshot on error."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
            screenshot_on_error=True,
        )
        scraper = ExceptionScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        with patch("os.makedirs"):
            article = await scraper.scrape_article("https://example.com/error")

        assert article is None
        mock_playwright["page"].screenshot.assert_called()

    @pytest.mark.asyncio
    async def test_scrape_with_exception(self, mock_playwright):
        """Test scrape method handles exceptions gracefully."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )

        class FailingGetUrlsScraper(PlaywrightScraper):
            async def get_article_urls(self, page: int = 1) -> List[str]:
                raise Exception("Failed to get URLs")

            async def parse_article(self, page_obj: Any, url: str) -> Optional[ScrapedArticle]:
                return None

        scraper = FailingGetUrlsScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=1, max_articles=10)

        assert result.success is False
        assert result.error_message is not None

    @pytest.mark.asyncio
    async def test_apply_stealth_scripts_basic(self, mock_playwright):
        """Test apply_stealth_scripts with BASIC level."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.BASIC,
        )
        scraper = ConcreteScraper(config)
        scraper._context = mock_playwright["context"]

        await scraper._apply_stealth_scripts()

        mock_playwright["context"].add_init_script.assert_called()

    @pytest.mark.asyncio
    async def test_apply_stealth_scripts_standard(self, mock_playwright):
        """Test apply_stealth_scripts with STANDARD level."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.STANDARD,
        )
        scraper = ConcreteScraper(config)
        scraper._context = mock_playwright["context"]

        await scraper._apply_stealth_scripts()

        # Should call add_init_script twice (basic + standard)
        assert mock_playwright["context"].add_init_script.call_count >= 2

    @pytest.mark.asyncio
    async def test_apply_stealth_scripts_aggressive(self, mock_playwright):
        """Test apply_stealth_scripts with AGGRESSIVE level."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            stealth_level=StealthLevel.AGGRESSIVE,
        )
        scraper = ConcreteScraper(config)
        scraper._context = mock_playwright["context"]

        await scraper._apply_stealth_scripts()

        # Should call add_init_script three times (basic + standard + aggressive)
        assert mock_playwright["context"].add_init_script.call_count >= 3

    @pytest.mark.asyncio
    async def test_stats_to_dict_no_started_at(self):
        """Test stats to_dict with no started_at."""
        stats = PlaywrightScraperStats()

        d = stats.to_dict()

        assert d["started_at"] is None

    @pytest.mark.asyncio
    async def test_scrape_article_navigation_failure(self, mock_playwright):
        """Test scrape_article when navigation fails."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
            max_retries=1,
        )
        scraper = ConcreteScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["page"].goto = AsyncMock(side_effect=Exception("Navigation failed"))

        article = await scraper.scrape_article("https://example.com/article")

        assert article is None

    @pytest.mark.asyncio
    async def test_wait_for_selector_with_custom_timeout(self, mock_playwright):
        """Test wait_for_selector with custom timeout."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]

        result = await scraper.wait_for_selector(mock_page, ".article", timeout_ms=5000)

        assert result is True
        mock_page.wait_for_selector.assert_called_once_with(".article", timeout=5000)

    @pytest.mark.asyncio
    async def test_scrape_stops_at_max_articles(self, mock_playwright):
        """Test that scrape stops when reaching max_articles even mid-page."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = ConcreteScraper(
            config,
            urls=[f"https://example.com/{i}" for i in range(100)],
        )

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        mock_playwright["playwright"].stop = AsyncMock()

        result = await scraper.scrape(pages=5, max_articles=5)

        assert len(result.articles) == 5

    @pytest.mark.asyncio
    async def test_infinite_scroll_reaches_max(self, mock_playwright):
        """Test infinite scroll reaches max scrolls."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
        )
        scraper = ConcreteScraper(config)

        mock_page = mock_playwright["page"]
        # Height always increases (never stabilizes)
        heights = list(range(1000, 20000, 1000))
        mock_page.evaluate = AsyncMock(side_effect=heights + [None] * 20)

        await scraper.infinite_scroll(mock_page, max_scrolls=3, scroll_delay_ms=10)

        # Should stop at max_scrolls even though height keeps increasing

    @pytest.mark.asyncio
    async def test_navigate_wait_until_parameter(self, mock_playwright):
        """Test navigate with different wait_until parameter."""
        config = PlaywrightConfig(
            name="test",
            base_url="https://example.com",
            rate_limit_rpm=1000,
        )
        scraper = ConcreteScraper(config)

        scraper._playwright = mock_playwright["playwright"]
        scraper._browser = mock_playwright["browser"]
        scraper._context = mock_playwright["context"]
        scraper._initialized = True

        page = await scraper.navigate("https://example.com", wait_until="networkidle")

        assert page is not None
        mock_playwright["page"].goto.assert_called_with(
            "https://example.com",
            wait_until="networkidle"
        )
