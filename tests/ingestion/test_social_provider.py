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
