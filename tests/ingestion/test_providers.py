"""
Tests for Ingestion Providers — S37

Tests for news and social provider clients.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.ingestion.providers.news_provider_client import (
    NewsProviderClient,
    RawNewsItem,
)


class TestRawNewsItem:
    """Tests for RawNewsItem dataclass."""

    def test_create(self):
        """Create raw news item."""
        item = RawNewsItem(
            external_id="article_123",
            title="Breaking News",
            url="https://example.com/article",
            published_at="2024-01-15T10:30:00Z",
            summary="This is the article summary.",
            source_name="Example News",
            language="pt",
            country="br",
            categories=["politics", "economy"],
            payload={"full_content": "Full article content..."},
        )

        assert item.external_id == "article_123"
        assert item.title == "Breaking News"
        assert item.language == "pt"
        assert "politics" in item.categories


class TestNewsProviderClient:
    """Tests for NewsProviderClient class."""

    def test_init_default(self):
        """Initialize with defaults."""
        client = NewsProviderClient()

        assert client.api_key == "demo"
        assert client.base_url == "https://newsdata.io/api/1"
        assert client.timeout_seconds == 10

    def test_init_custom(self):
        """Initialize with custom values."""
        client = NewsProviderClient(
            api_key="my_api_key",
            base_url="https://custom.api.com",
            timeout_seconds=30,
        )

        assert client.api_key == "my_api_key"
        assert client.base_url == "https://custom.api.com"
        assert client.timeout_seconds == 30

    @pytest.mark.asyncio
    async def test_fetch_success(self):
        """Fetch returns news items on success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "article_id": "123",
                    "title": "Test Article",
                    "link": "https://example.com/1",
                    "pubDate": "2024-01-15T10:00:00Z",
                    "description": "Article description",
                    "source_id": "example",
                    "language": "pt",
                    "country": ["br"],
                    "category": ["news"],
                },
            ]
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient(api_key="test_key")
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                items = await client.fetch(profile, size=10)

        assert len(items) == 1
        assert items[0].title == "Test Article"
        assert items[0].external_id == "123"

    @pytest.mark.asyncio
    async def test_fetch_with_domains(self):
        """Fetch with domain filter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await client.fetch(profile, domains=["example.com", "test.com"])

        # Check that domainurl was set in params
        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["domainurl"] == "example.com,test.com"

    @pytest.mark.asyncio
    async def test_fetch_with_profile_filters(self):
        """Fetch uses profile filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {"category": "politics", "q": "eleicoes"}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await client.fetch(profile)

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["category"] == "politics"
        assert params["q"] == "eleicoes"

    @pytest.mark.asyncio
    async def test_fetch_retry_on_429(self):
        """Fetch retries on 429 rate limit."""
        mock_429 = MagicMock()
        mock_429.status_code = 429
        mock_429.raise_for_status.side_effect = Exception("Rate limited")

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get.side_effect = [mock_429, mock_success]
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with patch("random.uniform", return_value=0.1):
                    await client.fetch(profile, max_attempts=3)

        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_retry_on_500(self):
        """Fetch retries on 500 server error."""
        mock_500 = MagicMock()
        mock_500.status_code = 500

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get.side_effect = [mock_500, mock_success]
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with patch("random.uniform", return_value=0.1):
                    await client.fetch(profile, max_attempts=3)

        assert mock_client.get.call_count == 2

    @pytest.mark.asyncio
    async def test_fetch_no_retry_on_400(self):
        """Fetch does not retry on 400 client error."""
        mock_400 = MagicMock()
        mock_400.status_code = 400
        mock_400.raise_for_status.side_effect = Exception("Bad request")

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_400
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with pytest.raises(Exception):
            with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    await client.fetch(profile, max_attempts=3)

        # Should only try once for 400 error
        assert mock_client.get.call_count == 1

    @pytest.mark.asyncio
    async def test_fetch_attempt_log(self):
        """Fetch populates attempt log."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        attempt_log = []
        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await client.fetch(profile, attempt_log=attempt_log)

        assert len(attempt_log) == 1
        assert attempt_log[0]["attempt"] == 1
        assert attempt_log[0]["status_code"] == 200

    @pytest.mark.asyncio
    async def test_fetch_with_limit_kwarg(self):
        """Fetch accepts limit kwarg."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                await client.fetch(profile, limit=25)

        call_args = mock_client.get.call_args
        params = call_args[1]["params"]
        assert params["size"] == 25

    @pytest.mark.asyncio
    async def test_fetch_handles_missing_fields(self):
        """Fetch handles missing fields in response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    # Minimal fields
                    "link": "https://example.com/1",
                },
            ]
        }

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                items = await client.fetch(profile)

        assert len(items) == 1
        assert items[0].url == "https://example.com/1"
        assert items[0].title == ""  # Default for missing

    @pytest.mark.asyncio
    async def test_sleep_with_jitter(self):
        """Sleep with jitter adds randomness."""
        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with patch("random.uniform", return_value=0.15):
                delta = await NewsProviderClient._sleep_with_jitter(1.0)

        assert delta == 1.15
        mock_sleep.assert_called_once_with(1.15)

    @pytest.mark.asyncio
    async def test_fetch_http_error(self):
        """Fetch handles HTTP errors."""
        import httpx

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("Connection failed")
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with pytest.raises(httpx.HTTPError):
            with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
                with patch("asyncio.sleep", new_callable=AsyncMock):
                    with patch("random.uniform", return_value=0.1):
                        await client.fetch(profile, max_attempts=3)

    @pytest.mark.asyncio
    async def test_fetch_empty_results(self):
        """Fetch handles empty results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": None}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None

        client = NewsProviderClient()
        profile = MagicMock()
        profile.country = "br"
        profile.language = "pt"
        profile.filters = {}

        with patch("app.ingestion.providers.news_provider_client.httpx.AsyncClient", return_value=mock_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                items = await client.fetch(profile)

        assert items == []
