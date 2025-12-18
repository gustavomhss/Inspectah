"""
Tests for Ingestion Normalize Provider — S37

Tests for normalizing news and social items.
"""

import pytest
from datetime import datetime

from app.ingestion.normalize_provider import (
    _hash_key,
    normalize_news,
    normalize_social,
)
from app.ingestion.providers.news_provider_client import RawNewsItem
from app.ingestion.providers.social_provider_client import RawSocialItem


class TestHashKey:
    """Tests for _hash_key function."""

    def test_hash_key_single_part(self):
        """Hash single part."""
        result = _hash_key("test")

        assert isinstance(result, str)
        assert len(result) == 64  # SHA256 hex digest

    def test_hash_key_multiple_parts(self):
        """Hash multiple parts."""
        result = _hash_key("part1", "part2", "part3")

        assert isinstance(result, str)
        assert len(result) == 64

    def test_hash_key_consistent(self):
        """Same input produces same hash."""
        result1 = _hash_key("a", "b", "c")
        result2 = _hash_key("a", "b", "c")

        assert result1 == result2

    def test_hash_key_order_matters(self):
        """Different order produces different hash."""
        result1 = _hash_key("a", "b", "c")
        result2 = _hash_key("c", "b", "a")

        assert result1 != result2


class TestNormalizeNews:
    """Tests for normalize_news function."""

    def test_normalize_news_empty(self):
        """Normalize empty list."""
        result = normalize_news([])

        assert result == []

    def test_normalize_news_single_item(self):
        """Normalize single news item."""
        item = RawNewsItem(
            external_id="ext_123",
            title="Test News Title",
            url="https://example.com/news/1",
            published_at="2024-01-01T00:00:00Z",
            language="pt",
            country="BR",
            categories=["politics"],
            source_name="Test Source",
            summary="Summary text",
            payload={"extra": "data"},
        )

        result = normalize_news([item])

        assert len(result) == 1
        assert result[0]["kind"] == "news"
        assert result[0]["external_id"] == "ext_123"
        assert result[0]["title"] == "Test News Title"
        assert result[0]["url"] == "https://example.com/news/1"
        assert result[0]["language"] == "pt"
        assert result[0]["country"] == "BR"
        assert result[0]["categories"] == ["politics"]
        assert result[0]["source_name"] == "Test Source"
        assert "content_id" in result[0]
        assert "payload" in result[0]

    def test_normalize_news_multiple_items(self):
        """Normalize multiple news items."""
        items = [
            RawNewsItem(
                external_id=f"ext_{i}",
                title=f"Title {i}",
                url=f"https://example.com/news/{i}",
                published_at="2024-01-01T00:00:00Z",
                language="pt",
                country="BR",
                categories=[],
                source_name="Source",
                summary="",
                payload={},
            )
            for i in range(5)
        ]

        result = normalize_news(items)

        assert len(result) == 5

    def test_normalize_news_deduplication(self):
        """Duplicate items are removed."""
        item = RawNewsItem(
            external_id="ext_1",
            title="Same Title",
            url="https://example.com/news/1",
            published_at="2024-01-01T00:00:00Z",
            language="pt",
            country="BR",
            categories=[],
            source_name="Source",
            summary="",
            payload={},
        )

        # Same item twice
        result = normalize_news([item, item])

        assert len(result) == 1

    def test_normalize_news_preserves_payload(self):
        """Payload is preserved as dict from dataclass."""
        item = RawNewsItem(
            external_id="ext_1",
            title="Title",
            url="https://example.com/1",
            published_at="2024-01-01T00:00:00Z",
            language="pt",
            country="BR",
            categories=["news"],
            source_name="Source",
            summary="Summary",
            payload={"custom": "value"},
        )

        result = normalize_news([item])

        # Payload is asdict of the dataclass, not the original payload field
        assert result[0]["payload"]["external_id"] == "ext_1"
        assert result[0]["payload"]["title"] == "Title"
        # The original payload dict is nested inside
        assert result[0]["payload"]["payload"] == {"custom": "value"}


class TestNormalizeSocial:
    """Tests for normalize_social function."""

    def test_normalize_social_empty(self):
        """Normalize empty list."""
        result = normalize_social([])

        assert result == []

    def test_normalize_social_single_item(self):
        """Normalize single social item."""
        item = RawSocialItem(
            external_id="social_123",
            text="This is a tweet",
            url="https://twitter.com/user/status/123",
            published_at="2024-01-01T00:00:00Z",
            author="test_user",
            language="pt",
            country="BR",
            tags=["hashtag1", "hashtag2"],
            payload={"likes": 100},
        )

        result = normalize_social([item])

        assert len(result) == 1
        assert result[0]["kind"] == "social"
        assert result[0]["external_id"] == "social_123"
        assert result[0]["text"] == "This is a tweet"
        assert result[0]["url"] == "https://twitter.com/user/status/123"
        assert result[0]["language"] == "pt"
        assert result[0]["country"] == "BR"
        assert result[0]["tags"] == ["hashtag1", "hashtag2"]
        assert "content_id" in result[0]
        assert "payload" in result[0]

    def test_normalize_social_multiple_items(self):
        """Normalize multiple social items."""
        items = [
            RawSocialItem(
                external_id=f"social_{i}",
                text=f"Tweet {i}",
                url=f"https://twitter.com/status/{i}",
                published_at="2024-01-01T00:00:00Z",
                author="user",
                language="pt",
                country="BR",
                tags=[],
                payload={},
            )
            for i in range(3)
        ]

        result = normalize_social(items)

        assert len(result) == 3

    def test_normalize_social_deduplication(self):
        """Duplicate items are removed."""
        item = RawSocialItem(
            external_id="social_1",
            text="Same tweet",
            url="https://twitter.com/status/1",
            published_at="2024-01-01T00:00:00Z",
            author="user",
            language="pt",
            country="BR",
            tags=[],
            payload={},
        )

        result = normalize_social([item, item])

        assert len(result) == 1

    def test_normalize_social_preserves_payload(self):
        """Payload is preserved as dict from dataclass."""
        item = RawSocialItem(
            external_id="social_1",
            text="Tweet",
            url="https://twitter.com/status/1",
            published_at="2024-01-01T00:00:00Z",
            author="user",
            language="pt",
            country="BR",
            tags=["tag1"],
            payload={"retweets": 50},
        )

        result = normalize_social([item])

        # Payload is asdict of the dataclass
        assert result[0]["payload"]["external_id"] == "social_1"
        assert result[0]["payload"]["text"] == "Tweet"
        # The original payload dict is nested inside
        assert result[0]["payload"]["payload"] == {"retweets": 50}
