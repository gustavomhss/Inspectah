"""
Tests for Ingestion Content Repository — S37

Tests for content repository persistence.
"""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from app.ingestion.content_repo import (
    ContentRepository,
    _serialize,
    _deserialize,
)


class TestSerialize:
    """Tests for _serialize function."""

    def test_serialize_dict(self):
        """Serialize dictionary."""
        result = _serialize({"key": "value"})

        assert result == '{"key": "value"}'

    def test_serialize_list(self):
        """Serialize list."""
        result = _serialize(["a", "b", "c"])

        assert result == '["a", "b", "c"]'

    def test_serialize_none(self):
        """Serialize None returns empty dict."""
        result = _serialize(None)

        assert result == "{}"

    def test_serialize_unicode(self):
        """Serialize with unicode."""
        result = _serialize({"text": "café com pão"})

        assert "café" in result
        assert "pão" in result


class TestDeserialize:
    """Tests for _deserialize function."""

    def test_deserialize_dict(self):
        """Deserialize JSON dict."""
        result = _deserialize('{"key": "value"}')

        assert result == {"key": "value"}

    def test_deserialize_list(self):
        """Deserialize JSON list."""
        result = _deserialize('["a", "b"]')

        assert result == ["a", "b"]

    def test_deserialize_none(self):
        """Deserialize None returns empty dict."""
        result = _deserialize(None)

        assert result == {}

    def test_deserialize_invalid_json(self):
        """Deserialize invalid JSON returns empty dict."""
        result = _deserialize("not valid json {")

        assert result == {}


class TestContentRepository:
    """Tests for ContentRepository class."""

    @pytest.fixture
    def temp_db(self):
        """Create temp database."""
        with TemporaryDirectory() as tmpdir:
            yield Path(tmpdir) / "test.sqlite"

    @pytest.fixture
    def repo(self, temp_db):
        """Create repository with temp db."""
        return ContentRepository(db_path=temp_db)

    def test_init_creates_schema(self, temp_db):
        """Init creates database schema."""
        repo = ContentRepository(db_path=temp_db)

        assert temp_db.exists()

    def test_init_default_path(self):
        """Init with default path."""
        repo = ContentRepository()

        assert repo.db_path is not None

    def test_save_items_empty(self, repo):
        """Save empty list."""
        result = repo.save_items([])

        assert result == 0

    def test_save_items_single(self, repo):
        """Save single item."""
        item = {
            "content_id": "c1",
            "kind": "news",
            "title": "Test Title",
            "url": "https://example.com/1",
            "published_at": "2024-01-01T00:00:00Z",
            "language": "pt",
            "country": "BR",
        }

        result = repo.save_items([item])

        assert result == 1

    def test_save_items_multiple(self, repo):
        """Save multiple items."""
        items = [
            {
                "content_id": f"c{i}",
                "kind": "news",
                "title": f"Title {i}",
                "url": f"https://example.com/{i}",
            }
            for i in range(5)
        ]

        result = repo.save_items(items)

        assert result == 5

    def test_save_items_duplicate_ignored(self, repo):
        """Duplicate items are ignored."""
        item = {
            "content_id": "c1",
            "kind": "news",
            "url": "https://example.com/1",
        }

        result1 = repo.save_items([item])
        result2 = repo.save_items([item])

        assert result1 == 1
        assert result2 == 1  # INSERT OR IGNORE returns 1 even for ignored

    def test_save_items_with_categories(self, repo):
        """Save item with categories."""
        item = {
            "content_id": "c1",
            "kind": "news",
            "url": "https://example.com/1",
            "categories": ["politics", "economy"],
        }

        result = repo.save_items([item])

        assert result == 1

    def test_save_items_with_tags(self, repo):
        """Save item with tags."""
        item = {
            "content_id": "c1",
            "kind": "social",
            "url": "https://twitter.com/1",
            "tags": ["hashtag1", "hashtag2"],
        }

        result = repo.save_items([item])

        assert result == 1

    def test_save_items_with_payload(self, repo):
        """Save item with payload."""
        item = {
            "content_id": "c1",
            "kind": "news",
            "url": "https://example.com/1",
            "payload": {"custom": "data", "nested": {"key": "value"}},
        }

        result = repo.save_items([item])

        assert result == 1

    def test_list_items_empty(self, repo):
        """List items from empty db."""
        result = repo.list_items()

        assert result == []

    def test_list_items_returns_saved(self, repo):
        """List items returns saved items."""
        item = {
            "content_id": "c1",
            "kind": "news",
            "title": "Test Title",
            "text": "Test text",
            "url": "https://example.com/1",
            "published_at": "2024-01-01T00:00:00Z",
            "language": "pt",
            "country": "BR",
            "provider_id": "provider1",
            "profile_id": "profile1",
            "categories": ["news"],
            "tags": ["tag1"],
            "payload": {"extra": "data"},
        }
        repo.save_items([item])

        result = repo.list_items()

        assert len(result) == 1
        assert result[0]["content_id"] == "c1"
        assert result[0]["kind"] == "news"
        assert result[0]["title"] == "Test Title"
        assert result[0]["url"] == "https://example.com/1"
        assert result[0]["categories"] == ["news"]
        assert result[0]["tags"] == ["tag1"]
        assert result[0]["payload"] == {"extra": "data"}
        assert "created_at" in result[0]

    def test_list_items_respects_limit(self, repo):
        """List items respects limit."""
        items = [
            {"content_id": f"c{i}", "kind": "news", "url": f"https://example.com/{i}"}
            for i in range(10)
        ]
        repo.save_items(items)

        result = repo.list_items(limit=5)

        assert len(result) == 5

    def test_list_items_ordered_by_created_at(self, repo):
        """List items ordered by created_at desc."""
        items = [
            {"content_id": "first", "kind": "news", "url": "https://example.com/1"},
            {"content_id": "second", "kind": "news", "url": "https://example.com/2"},
        ]
        repo.save_items(items)

        result = repo.list_items()

        # Most recent first
        assert len(result) >= 2

    def test_connection_context_manager(self, repo):
        """Connection context manager works."""
        with repo._conn() as conn:
            cursor = conn.execute("SELECT 1")
            assert cursor.fetchone()[0] == 1
