"""
Tests for ingestion/providers/social_provider_client — S37

Tests for SocialProviderClient.
"""

import pytest
from unittest.mock import MagicMock

from app.ingestion.providers.social_provider_client import SocialProviderClient, RawSocialItem
from app.providers.models import IngestionProfile, ProfileKind, ProviderStatus


class TestRawSocialItem:
    """Tests for RawSocialItem dataclass."""

    def test_raw_social_item_creation(self):
        """Create a RawSocialItem."""
        item = RawSocialItem(
            external_id="ext_1",
            text="Test text",
            url="https://example.com",
            published_at="2024-01-01T00:00:00Z",
            author="test_user",
            language="en",
            country="US",
            tags=["tag1", "tag2"],
            payload={"key": "value"},
        )

        assert item.external_id == "ext_1"
        assert item.text == "Test text"
        assert item.author == "test_user"
        assert len(item.tags) == 2


class TestSocialProviderClient:
    """Tests for SocialProviderClient class."""

    def test_init_with_defaults(self):
        """Initialize with default values."""
        client = SocialProviderClient()

        assert client.api_key == "demo"
        assert client.base_url == "https://social-api.local"

    def test_init_with_custom_values(self):
        """Initialize with custom values."""
        client = SocialProviderClient(api_key="custom_key", base_url="https://custom.api")

        assert client.api_key == "custom_key"
        assert client.base_url == "https://custom.api"

    def test_init_with_none_values(self):
        """Initialize with None values uses defaults."""
        client = SocialProviderClient(api_key=None, base_url=None)

        assert client.api_key == "demo"
        assert client.base_url == "https://social-api.local"

    @pytest.mark.asyncio
    async def test_fetch_default_limit(self):
        """Fetch with default limit of 5."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_1",
            provider_id="prov_1",
            name="Test Profile",
            slug="test-profile",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
            keywords=["keyword1"],
        )

        result = await client.fetch(profile)

        assert len(result) == 5
        for item in result:
            assert isinstance(item, RawSocialItem)
            assert item.language == "pt"
            assert item.country == "BR"

    @pytest.mark.asyncio
    async def test_fetch_custom_limit(self):
        """Fetch with custom limit."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_2",
            provider_id="prov_1",
            name="Test Profile 2",
            slug="test-profile-2",
            kind=ProfileKind.SOCIAL,
            country="US",
            language="en",
        )

        result = await client.fetch(profile, limit=3)

        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_fetch_external_id_format(self):
        """Fetched items have correct external_id format."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_3",
            provider_id="prov_1",
            name="Test Profile 3",
            slug="my-slug",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        result = await client.fetch(profile, limit=2)

        assert result[0].external_id == "social-my-slug-0"
        assert result[1].external_id == "social-my-slug-1"

    @pytest.mark.asyncio
    async def test_fetch_url_format(self):
        """Fetched items have correct URL format."""
        client = SocialProviderClient(base_url="https://api.test")
        profile = IngestionProfile.create(
            id="prof_4",
            provider_id="prov_1",
            name="Test Profile 4",
            slug="url-test",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        result = await client.fetch(profile, limit=1)

        assert result[0].url == "https://api.test/url-test/0"

    @pytest.mark.asyncio
    async def test_fetch_with_keywords(self):
        """Fetched items include profile keywords as tags."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_5",
            provider_id="prov_1",
            name="Test Profile 5",
            slug="keywords-test",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
            keywords=["tag1", "tag2", "tag3"],
        )

        result = await client.fetch(profile, limit=1)

        assert result[0].tags == ["tag1", "tag2", "tag3"]

    @pytest.mark.asyncio
    async def test_fetch_payload_structure(self):
        """Fetched items have correct payload structure."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_6",
            provider_id="prov_1",
            name="Test Profile 6",
            slug="payload-test",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        result = await client.fetch(profile, limit=1)

        assert result[0].payload["profile"] == "payload-test"
        assert result[0].payload["kind"] == "social"

    @pytest.mark.asyncio
    async def test_fetch_with_none_language(self):
        """Fetch uses default language when profile has None."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_7",
            provider_id="prov_1",
            name="Test Profile 7",
            slug="none-lang",
            kind=ProfileKind.SOCIAL,
            country=None,
            language=None,
        )

        result = await client.fetch(profile, limit=1)

        assert result[0].language == "pt"
        assert result[0].country == "BR"


# =============================================================================
# S40-BE-018: Enhanced Social Provider Tests
# =============================================================================


class TestRateLimitState:
    """Tests for RateLimitState dataclass."""

    def test_rate_limit_state_defaults(self):
        """RateLimitState has correct defaults."""
        from app.ingestion.providers.social_provider_client import RateLimitState

        state = RateLimitState()
        assert state.requests_made == 0
        assert state.limit_per_minute == 60

    def test_rate_limit_state_custom_limit(self):
        """RateLimitState accepts custom limit."""
        from app.ingestion.providers.social_provider_client import RateLimitState

        state = RateLimitState(limit_per_minute=30)
        assert state.limit_per_minute == 30


class TestSocialProviderError:
    """Tests for SocialProviderError exception."""

    def test_error_creation(self):
        """Create SocialProviderError with message."""
        from app.ingestion.providers.social_provider_client import SocialProviderError

        err = SocialProviderError("Test error")
        assert str(err) == "Test error"
        assert err.error_code is None
        assert err.retryable is False

    def test_error_with_code(self):
        """Create SocialProviderError with error code."""
        from app.ingestion.providers.social_provider_client import SocialProviderError

        err = SocialProviderError("Test", error_code="E001", retryable=True)
        assert err.error_code == "E001"
        assert err.retryable is True


class TestSocialProviderClientS40:
    """S40-BE-018 Tests for rate limiting and retry."""

    def test_init_with_rate_limit(self):
        """Initialize with custom rate limit."""
        client = SocialProviderClient(rate_limit_per_minute=30)
        assert client._rate_limit.limit_per_minute == 30

    def test_init_with_max_retries(self):
        """Initialize with custom max retries."""
        client = SocialProviderClient(max_retries=5)
        assert client.max_retries == 5

    def test_init_with_retry_delay(self):
        """Initialize with custom retry delay."""
        client = SocialProviderClient(retry_delay=2.0)
        assert client.retry_delay == 2.0

    def test_get_stats(self):
        """get_stats returns client statistics."""
        client = SocialProviderClient()
        stats = client.get_stats()

        assert "request_count" in stats
        assert "error_count" in stats
        assert "rate_limit_requests" in stats
        assert "rate_limit_per_minute" in stats

    def test_is_pilot_domain_saude(self):
        """is_pilot_domain returns True for saude."""
        client = SocialProviderClient()
        assert client.is_pilot_domain("saude") is True

    def test_is_pilot_domain_politica(self):
        """is_pilot_domain returns True for politica."""
        client = SocialProviderClient()
        assert client.is_pilot_domain("politica") is True

    def test_is_pilot_domain_other(self):
        """is_pilot_domain returns False for non-pilot."""
        client = SocialProviderClient()
        assert client.is_pilot_domain("economia") is False

    @pytest.mark.asyncio
    async def test_fetch_for_domain_saude(self):
        """fetch_for_domain works for saude."""
        client = SocialProviderClient()
        result = await client.fetch_for_domain(
            domain="saude",
            keywords=["vacina", "covid"],
            limit=3,
        )

        assert len(result) == 3
        for item in result:
            assert item.domain == "saude"

    @pytest.mark.asyncio
    async def test_fetch_for_domain_politica(self):
        """fetch_for_domain works for politica."""
        client = SocialProviderClient()
        result = await client.fetch_for_domain(
            domain="politica",
            keywords=["eleicao"],
            limit=2,
        )

        assert len(result) == 2
        for item in result:
            assert item.domain == "politica"

    @pytest.mark.asyncio
    async def test_fetch_for_domain_invalid(self):
        """fetch_for_domain raises for non-pilot domain."""
        client = SocialProviderClient()

        with pytest.raises(ValueError) as exc_info:
            await client.fetch_for_domain("economia", ["pib"], 5)

        assert "not in pilot domains" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_fetch_detects_domain_from_slug(self):
        """Fetch detects domain from profile slug."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_domain_slug",
            provider_id="prov_1",
            name="Saude Profile",
            slug="saude-news",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        result = await client.fetch(profile, limit=1)
        assert result[0].domain == "saude"

    @pytest.mark.asyncio
    async def test_fetch_detects_domain_from_keywords(self):
        """Fetch detects domain from profile keywords."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_domain_kw",
            provider_id="prov_1",
            name="News Profile",
            slug="generic-news",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
            keywords=["politica", "eleicoes"],
        )

        result = await client.fetch(profile, limit=1)
        assert result[0].domain == "politica"

    @pytest.mark.asyncio
    async def test_request_count_increments(self):
        """Request count increments after fetch."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="prof_count",
            provider_id="prov_1",
            name="Count Profile",
            slug="count-test",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        initial_count = client._request_count
        await client.fetch(profile, limit=1)

        assert client._request_count == initial_count + 1


class TestSocialProviderRateLimiting:
    """Tests for rate limiting behavior."""

    def test_rate_limit_window_reset(self):
        """Rate limit window resets after 60 seconds."""
        import time

        client = SocialProviderClient(rate_limit_per_minute=5)

        # Simulate old window
        client._rate_limit.window_start = time.time() - 61  # 61 seconds ago
        client._rate_limit.requests_made = 5

        # This should reset the window
        client._check_rate_limit()

        assert client._rate_limit.requests_made == 1  # 1 because we just made a request
        assert client._rate_limit.window_start > time.time() - 1  # Window was reset

    def test_rate_limit_increments_requests(self):
        """Rate limit increments request count."""
        client = SocialProviderClient(rate_limit_per_minute=100)

        initial = client._rate_limit.requests_made
        client._check_rate_limit()

        assert client._rate_limit.requests_made == initial + 1

    def test_get_stats_structure(self):
        """get_stats returns expected structure."""
        client = SocialProviderClient()
        client._request_count = 10
        client._error_count = 2

        stats = client.get_stats()

        assert stats["request_count"] == 10
        assert stats["error_count"] == 2
        assert "rate_limit_requests" in stats
        assert "rate_limit_per_minute" in stats


class TestSocialProviderDomainDetection:
    """Tests for domain detection from profiles."""

    def test_get_domain_from_slug_saude(self):
        """Detects saude domain from slug."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="p1",
            provider_id="prov",
            slug="saude-noticias",
            name="Saude News",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        domain = client._get_domain(profile)
        assert domain == "saude"

    def test_get_domain_from_slug_politica(self):
        """Detects politica domain from slug."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="p2",
            provider_id="prov",
            slug="politica-brasil",
            name="Politica News",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
        )

        domain = client._get_domain(profile)
        assert domain == "politica"

    def test_get_domain_from_keywords(self):
        """Detects domain from keywords."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="p3",
            provider_id="prov",
            slug="general-news",
            name="General",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
            keywords=["eleicoes", "politica"],
        )

        domain = client._get_domain(profile)
        assert domain == "politica"

    def test_get_domain_none_for_non_pilot(self):
        """Returns None for non-pilot domain."""
        client = SocialProviderClient()
        profile = IngestionProfile.create(
            id="p4",
            provider_id="prov",
            slug="esporte-noticias",
            name="Esporte",
            kind=ProfileKind.SOCIAL,
            country="BR",
            language="pt",
            keywords=["futebol", "esporte"],
        )

        domain = client._get_domain(profile)
        assert domain is None


class TestRawSocialItemS40:
    """S40 tests for RawSocialItem."""

    def test_raw_item_with_domain(self):
        """RawSocialItem includes domain field."""
        item = RawSocialItem(
            external_id="ext_1",
            text="Test",
            url="https://example.com",
            published_at="2024-01-01",
            author="user",
            language="pt",
            country="BR",
            tags=[],
            payload={},
            domain="saude",
        )

        assert item.domain == "saude"

    def test_raw_item_default_domain(self):
        """RawSocialItem domain defaults to None."""
        item = RawSocialItem(
            external_id="ext_2",
            text="Test",
            url="https://example.com",
            published_at="2024-01-01",
            author="user",
            language="pt",
            country="BR",
            tags=[],
            payload={},
        )

        assert item.domain is None

    def test_raw_item_collected_at(self):
        """RawSocialItem has collected_at timestamp."""
        from datetime import datetime, timezone

        item = RawSocialItem(
            external_id="ext_3",
            text="Test",
            url="https://example.com",
            published_at="2024-01-01",
            author="user",
            language="pt",
            country="BR",
            tags=[],
            payload={},
        )

        # collected_at should be set automatically
        assert item.collected_at is not None
        assert isinstance(item.collected_at, datetime)
