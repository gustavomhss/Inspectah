"""
Tests for app/ingestion/scrapers/base.py

Comprehensive tests for the base scraper functionality.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import List, Optional
from unittest.mock import MagicMock, Mock, patch

import httpx
import pytest
from bs4 import BeautifulSoup

from app.ingestion.scrapers.base import (
    BaseScraper,
    ScrapedArticle,
    ScraperConfig,
    ScraperResult,
    VerdictType,
)


class TestVerdictType:
    """Test VerdictType enum."""

    def test_verdict_types_exist(self):
        """Test all verdict types are defined."""
        assert VerdictType.TRUE == "true"
        assert VerdictType.FALSE == "false"
        assert VerdictType.MISLEADING == "misleading"
        assert VerdictType.UNVERIFIABLE == "unverifiable"
        assert VerdictType.OUTDATED == "outdated"
        assert VerdictType.EXAGGERATED == "exaggerated"
        assert VerdictType.PARTIALLY_TRUE == "partially_true"
        assert VerdictType.UNKNOWN == "unknown"


class TestScraperConfig:
    """Test ScraperConfig dataclass."""

    def test_config_with_defaults(self):
        """Test config with default values."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        assert config.name == "test"
        assert config.base_url == "https://example.com"
        assert config.rate_limit_rpm == 2
        assert config.timeout_seconds == 30
        assert config.max_retries == 3
        assert len(config.user_agent_pool) == 5
        assert config.enabled is True

    def test_config_with_custom_values(self):
        """Test config with custom values."""
        config = ScraperConfig(
            name="custom",
            base_url="https://custom.com",
            rate_limit_rpm=10,
            timeout_seconds=60,
            max_retries=5,
            user_agent_pool=["CustomUA/1.0"],
            enabled=False,
        )
        assert config.name == "custom"
        assert config.rate_limit_rpm == 10
        assert config.timeout_seconds == 60
        assert config.max_retries == 5
        assert config.user_agent_pool == ["CustomUA/1.0"]
        assert config.enabled is False


class TestScrapedArticle:
    """Test ScrapedArticle dataclass."""

    def test_article_creation(self):
        """Test creating a scraped article."""
        article = ScrapedArticle(
            external_id="test_123",
            source_name="test_source",
            url="https://example.com/article",
            title="Test Article",
            claim="Test claim",
            verdict=VerdictType.FALSE,
            verdict_label="FALSO",
            content="Article content",
            published_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            author="Test Author",
            tags=["tag1", "tag2"],
            metadata={"key": "value"},
        )

        assert article.external_id == "test_123"
        assert article.source_name == "test_source"
        assert article.verdict == VerdictType.FALSE
        assert article.verdict_label == "FALSO"
        assert len(article.tags) == 2
        assert article.metadata["key"] == "value"
        assert article.scraped_at is not None

    def test_content_hash(self):
        """Test content hash generation."""
        article = ScrapedArticle(
            external_id="test_123",
            source_name="test_source",
            url="https://example.com/article",
            title="Test Article",
            claim="Test claim",
            verdict=VerdictType.FALSE,
            verdict_label="FALSO",
            content="Article content",
            published_at=None,
            author=None,
        )

        hash1 = article.content_hash()
        assert len(hash1) == 16
        assert isinstance(hash1, str)

        # Same article should produce same hash
        article2 = ScrapedArticle(
            external_id="different_id",
            source_name="different_source",
            url="https://example.com/article",
            title="Test Article",
            claim="Test claim",
            verdict=VerdictType.FALSE,
            verdict_label="DIFFERENT",
            content="Different content",
            published_at=None,
            author=None,
        )
        hash2 = article2.content_hash()
        assert hash1 == hash2  # Same URL, title, claim, verdict

    def test_article_with_defaults(self):
        """Test article with default values."""
        article = ScrapedArticle(
            external_id="test_123",
            source_name="test_source",
            url="https://example.com/article",
            title="Test Article",
            claim="Test claim",
            verdict=VerdictType.FALSE,
            verdict_label="FALSO",
            content="Article content",
            published_at=None,
            author=None,
        )

        assert article.tags == []
        assert article.metadata == {}
        assert article.scraped_at is not None


class TestScraperResult:
    """Test ScraperResult dataclass."""

    def test_result_success(self):
        """Test successful scraper result."""
        articles = [
            ScrapedArticle(
                external_id="test_1",
                source_name="test",
                url="https://example.com/1",
                title="Article 1",
                claim="Claim 1",
                verdict=VerdictType.FALSE,
                verdict_label="FALSO",
                content="Content 1",
                published_at=None,
                author=None,
            )
        ]

        result = ScraperResult(
            source_name="test_source",
            articles=articles,
            total_found=10,
            success=True,
            duration_seconds=5.0,
        )

        assert result.source_name == "test_source"
        assert len(result.articles) == 1
        assert result.total_found == 10
        assert result.success is True
        assert result.error_message is None
        assert result.duration_seconds == 5.0
        assert result.started_at is not None

    def test_result_failure(self):
        """Test failed scraper result."""
        result = ScraperResult(
            source_name="test_source",
            articles=[],
            total_found=0,
            success=False,
            error_message="Connection failed",
            duration_seconds=1.0,
        )

        assert result.success is False
        assert result.error_message == "Connection failed"


class ConcreteScraper(BaseScraper):
    """Concrete implementation for testing."""

    def __init__(self, config: ScraperConfig):
        super().__init__(config)
        self.article_urls_to_return = []
        self.parsed_articles = {}

    def get_article_urls(self, page: int = 1) -> List[str]:
        return self.article_urls_to_return

    def parse_article(self, url: str, html: str) -> Optional[ScrapedArticle]:
        return self.parsed_articles.get(url)


class TestBaseScraper:
    """Test BaseScraper abstract class."""

    def test_init(self):
        """Test scraper initialization."""
        config = ScraperConfig(name="test", base_url="https://example.com", rate_limit_rpm=6)
        scraper = ConcreteScraper(config)

        assert scraper.config == config
        assert scraper._min_interval == 10.0  # 60/6
        assert scraper._last_request_time == 0.0

    def test_get_headers(self):
        """Test header generation with random user agent."""
        config = ScraperConfig(
            name="test",
            base_url="https://example.com",
            user_agent_pool=["UA1", "UA2", "UA3"],
        )
        scraper = ConcreteScraper(config)

        headers = scraper._get_headers()

        assert "User-Agent" in headers
        assert headers["User-Agent"] in ["UA1", "UA2", "UA3"]
        assert headers["Accept"] == "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        assert headers["Accept-Language"] == "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        assert headers["DNT"] == "1"
        assert headers["Connection"] == "keep-alive"

    def test_wait_rate_limit(self):
        """Test rate limiting."""
        config = ScraperConfig(name="test", base_url="https://example.com", rate_limit_rpm=60)
        scraper = ConcreteScraper(config)

        # First request should not wait
        start = time.time()
        scraper._wait_rate_limit()
        elapsed = time.time() - start
        assert elapsed < 0.1

        # Second immediate request should wait
        start = time.time()
        scraper._wait_rate_limit()
        elapsed = time.time() - start
        assert elapsed >= 0.9  # Should wait ~1 second (60 req/min)

    def test_sleep_with_jitter(self):
        """Test sleep with jitter."""
        start = time.time()
        BaseScraper._sleep_with_jitter(0.1)
        elapsed = time.time() - start

        assert 0.1 <= elapsed <= 0.7  # 0.1 base + 0-0.5 jitter

    def test_parse_html(self):
        """Test HTML parsing."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        html = "<html><body><h1>Test</h1></body></html>"
        soup = scraper._parse_html(html)

        assert isinstance(soup, BeautifulSoup)
        assert soup.find("h1").text == "Test"

    @patch("httpx.get")
    def test_request_with_retry_success(self, mock_get):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html>Success</html>"
        mock_get.return_value = mock_response

        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result == "<html>Success</html>"
        assert mock_get.call_count == 1

    @patch("httpx.get")
    def test_request_with_retry_429(self, mock_get):
        """Test retry on 429 status."""
        # First two calls return 429, third returns 200
        mock_response_429 = Mock()
        mock_response_429.status_code = 429

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.text = "<html>Success</html>"

        mock_get.side_effect = [mock_response_429, mock_response_429, mock_response_200]

        config = ScraperConfig(name="test", base_url="https://example.com", max_retries=3)
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result == "<html>Success</html>"
        assert mock_get.call_count == 3

    @patch("httpx.get")
    def test_request_with_retry_403(self, mock_get):
        """Test handling of 403 blocked."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result is None
        assert mock_get.call_count == 1  # Should not retry 403

    @patch("httpx.get")
    def test_request_with_retry_404(self, mock_get):
        """Test handling of 404 not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result is None
        assert mock_get.call_count == 1

    @patch("httpx.get")
    def test_request_with_retry_http_error(self, mock_get):
        """Test retry on HTTP error."""
        # First two calls raise exception, third succeeds
        mock_get.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.TimeoutException("Timeout"),
            Mock(status_code=200, text="<html>Success</html>"),
        ]

        config = ScraperConfig(name="test", base_url="https://example.com", max_retries=3)
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result == "<html>Success</html>"
        assert mock_get.call_count == 3

    @patch("httpx.get")
    def test_request_with_retry_max_retries_exceeded(self, mock_get):
        """Test max retries exceeded."""
        mock_get.side_effect = httpx.ConnectError("Connection failed")

        config = ScraperConfig(name="test", base_url="https://example.com", max_retries=3)
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result is None
        assert mock_get.call_count == 3

    @patch("httpx.get")
    def test_request_with_retry_500(self, mock_get):
        """Test retry on 500 server error."""
        mock_response_500 = Mock()
        mock_response_500.status_code = 500

        mock_response_200 = Mock()
        mock_response_200.status_code = 200
        mock_response_200.text = "<html>Success</html>"

        mock_get.side_effect = [mock_response_500, mock_response_200]

        config = ScraperConfig(name="test", base_url="https://example.com", max_retries=3)
        scraper = ConcreteScraper(config)

        result = scraper._request_with_retry("https://example.com/test")

        assert result == "<html>Success</html>"
        assert mock_get.call_count == 2

    def test_scrape_article_success(self):
        """Test scraping single article successfully."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        article = ScrapedArticle(
            external_id="test_1",
            source_name="test",
            url="https://example.com/1",
            title="Test",
            claim="Test claim",
            verdict=VerdictType.FALSE,
            verdict_label="FALSO",
            content="Content",
            published_at=None,
            author=None,
        )
        scraper.parsed_articles["https://example.com/1"] = article

        with patch.object(scraper, "_request_with_retry", return_value="<html>Test</html>"):
            result = scraper.scrape_article("https://example.com/1")

        assert result == article

    def test_scrape_article_request_failed(self):
        """Test scraping article when request fails."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        with patch.object(scraper, "_request_with_retry", return_value=None):
            result = scraper.scrape_article("https://example.com/1")

        assert result is None

    def test_scrape_article_parse_error(self):
        """Test scraping article when parsing fails."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        def raise_error(url, html):
            raise ValueError("Parse error")

        scraper.parse_article = raise_error

        with patch.object(scraper, "_request_with_retry", return_value="<html>Test</html>"):
            result = scraper.scrape_article("https://example.com/1")

        assert result is None

    def test_scrape_success(self):
        """Test full scrape operation."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        scraper.article_urls_to_return = [
            "https://example.com/1",
            "https://example.com/2",
        ]

        article1 = ScrapedArticle(
            external_id="test_1",
            source_name="test",
            url="https://example.com/1",
            title="Test 1",
            claim="Claim 1",
            verdict=VerdictType.FALSE,
            verdict_label="FALSO",
            content="Content 1",
            published_at=None,
            author=None,
        )
        article2 = ScrapedArticle(
            external_id="test_2",
            source_name="test",
            url="https://example.com/2",
            title="Test 2",
            claim="Claim 2",
            verdict=VerdictType.TRUE,
            verdict_label="VERDADEIRO",
            content="Content 2",
            published_at=None,
            author=None,
        )

        scraper.parsed_articles["https://example.com/1"] = article1
        scraper.parsed_articles["https://example.com/2"] = article2

        with patch.object(scraper, "_request_with_retry", return_value="<html>Test</html>"):
            result = scraper.scrape(pages=1, max_articles=10)

        assert result.success is True
        assert len(result.articles) == 2
        assert result.total_found == 2
        assert result.error_message is None
        assert result.duration_seconds > 0

    def test_scrape_max_articles_limit(self):
        """Test scrape respects max_articles limit."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        scraper.article_urls_to_return = [
            f"https://example.com/{i}" for i in range(10)
        ]

        for i in range(10):
            scraper.parsed_articles[f"https://example.com/{i}"] = ScrapedArticle(
                external_id=f"test_{i}",
                source_name="test",
                url=f"https://example.com/{i}",
                title=f"Test {i}",
                claim=f"Claim {i}",
                verdict=VerdictType.FALSE,
                verdict_label="FALSO",
                content=f"Content {i}",
                published_at=None,
                author=None,
            )

        with patch.object(scraper, "_request_with_retry", return_value="<html>Test</html>"):
            result = scraper.scrape(pages=1, max_articles=3)

        assert result.success is True
        assert len(result.articles) == 3
        assert result.total_found == 10

    def test_scrape_with_error(self):
        """Test scrape handles errors gracefully."""
        config = ScraperConfig(name="test", base_url="https://example.com")
        scraper = ConcreteScraper(config)

        def raise_error(page):
            raise RuntimeError("Scraping failed")

        scraper.get_article_urls = raise_error

        result = scraper.scrape(pages=1, max_articles=10)

        assert result.success is False
        assert result.error_message == "Scraping failed"
        assert len(result.articles) == 0

    def test_normalize_verdict_false(self):
        """Test verdict normalization for FALSE."""
        assert BaseScraper.normalize_verdict("FALSO") == VerdictType.FALSE
        assert BaseScraper.normalize_verdict("fake") == VerdictType.FALSE
        assert BaseScraper.normalize_verdict("Mentira") == VerdictType.FALSE
        assert BaseScraper.normalize_verdict("FALSA") == VerdictType.FALSE
        assert BaseScraper.normalize_verdict("incorreto") == VerdictType.FALSE
        assert BaseScraper.normalize_verdict("errado") == VerdictType.FALSE

    def test_normalize_verdict_true(self):
        """Test verdict normalization for TRUE."""
        assert BaseScraper.normalize_verdict("VERDADEIRO") == VerdictType.TRUE
        assert BaseScraper.normalize_verdict("verdade") == VerdictType.TRUE
        assert BaseScraper.normalize_verdict("correto") == VerdictType.TRUE
        assert BaseScraper.normalize_verdict("certo") == VerdictType.TRUE
        assert BaseScraper.normalize_verdict("true") == VerdictType.TRUE

    def test_normalize_verdict_misleading(self):
        """Test verdict normalization for MISLEADING."""
        assert BaseScraper.normalize_verdict("ENGANA") == VerdictType.MISLEADING
        assert BaseScraper.normalize_verdict("enganoso") == VerdictType.MISLEADING
        assert BaseScraper.normalize_verdict("distorce") == VerdictType.MISLEADING
        assert BaseScraper.normalize_verdict("misleading") == VerdictType.MISLEADING
        assert BaseScraper.normalize_verdict("distorcido") == VerdictType.MISLEADING

    def test_normalize_verdict_partially_true(self):
        """Test verdict normalization for PARTIALLY_TRUE."""
        assert BaseScraper.normalize_verdict("PARCIALMENTE") == VerdictType.PARTIALLY_TRUE
        assert BaseScraper.normalize_verdict("partially") == VerdictType.PARTIALLY_TRUE
        assert BaseScraper.normalize_verdict("em parte") == VerdictType.PARTIALLY_TRUE
        assert BaseScraper.normalize_verdict("incompleto") == VerdictType.PARTIALLY_TRUE

    def test_normalize_verdict_exaggerated(self):
        """Test verdict normalization for EXAGGERATED."""
        assert BaseScraper.normalize_verdict("EXAGERADO") == VerdictType.EXAGGERATED
        assert BaseScraper.normalize_verdict("exaggerated") == VerdictType.EXAGGERATED
        assert BaseScraper.normalize_verdict("inflado") == VerdictType.EXAGGERATED

    def test_normalize_verdict_outdated(self):
        """Test verdict normalization for OUTDATED."""
        assert BaseScraper.normalize_verdict("DESATUALIZADO") == VerdictType.OUTDATED
        assert BaseScraper.normalize_verdict("outdated") == VerdictType.OUTDATED
        assert BaseScraper.normalize_verdict("antigo") == VerdictType.OUTDATED

    def test_normalize_verdict_unverifiable(self):
        """Test verdict normalization for UNVERIFIABLE."""
        assert BaseScraper.normalize_verdict("INVERIFICAVEL") == VerdictType.UNVERIFIABLE
        assert BaseScraper.normalize_verdict("unverifiable") == VerdictType.UNVERIFIABLE
        assert BaseScraper.normalize_verdict("impossivel verificar") == VerdictType.UNVERIFIABLE

    def test_normalize_verdict_unknown(self):
        """Test verdict normalization for UNKNOWN."""
        assert BaseScraper.normalize_verdict("DESCONHECIDO") == VerdictType.UNKNOWN
        assert BaseScraper.normalize_verdict("xyz123") == VerdictType.UNKNOWN
        assert BaseScraper.normalize_verdict("") == VerdictType.UNKNOWN

    def test_normalize_verdict_case_insensitive(self):
        """Test verdict normalization is case insensitive."""
        assert BaseScraper.normalize_verdict("FaLsO") == VerdictType.FALSE
        assert BaseScraper.normalize_verdict("VERDADEIRO") == VerdictType.TRUE
        assert BaseScraper.normalize_verdict("eNgAnA") == VerdictType.MISLEADING
