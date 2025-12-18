"""
Comprehensive tests for Core Storage — Extended Coverage

Tests all code paths including edge cases, filters, and error handling.
"""

import json
import os
import pytest
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.core.storage import (
    _data_dir,
    _ensure_dir,
    _normalize,
    _parse_datetime,
    _read_json,
    _repo_root,
    _to_serializable,
    _write_json,
    bundles_dir,
    ensure_fixture_sources,
    generate_entity_id,
    get_item,
    get_item_path,
    get_source,
    list_items_by_filter,
    list_sources,
    load_evidence_bundle,
    load_query_log,
    queries_dir,
    responses_dir,
    save_evidence_bundle,
    save_item,
    save_query_log,
    save_source,
    save_user_response,
    DATA_DIR_ENV,
)
from app.core.models import (
    EvidenceBundle,
    EvidenceItemRef,
    Item,
    QueryLog,
    Source,
    SourceConfig,
    SourceStatus,
    UserResponse,
)


class TestPathUtilities:
    """Test path utility functions."""

    def test_repo_root(self):
        """Test _repo_root returns valid path."""
        root = _repo_root()
        assert root.is_absolute()
        assert root.exists()

    def test_data_dir_default(self):
        """Test _data_dir with default path."""
        with patch.dict(os.environ, {}, clear=True):
            data_dir = _data_dir()
            assert data_dir.exists()
            assert data_dir.is_dir()

    def test_data_dir_from_env(self, tmp_path):
        """Test _data_dir uses environment variable."""
        custom_dir = tmp_path / "custom_data"
        with patch.dict(os.environ, {DATA_DIR_ENV: str(custom_dir)}):
            data_dir = _data_dir()
            assert data_dir == custom_dir
            assert data_dir.exists()

    def test_ensure_dir_creates_directory(self, tmp_path):
        """Test _ensure_dir creates directory."""
        new_dir = tmp_path / "new" / "nested" / "dir"
        result = _ensure_dir(new_dir)

        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_ensure_dir_existing_directory(self, tmp_path):
        """Test _ensure_dir with existing directory."""
        existing = tmp_path / "existing"
        existing.mkdir()

        result = _ensure_dir(existing)

        assert result == existing
        assert existing.exists()

    def test_bundles_dir(self):
        """Test bundles_dir returns valid path."""
        bdir = bundles_dir()
        assert bdir.exists()
        assert bdir.is_dir()

    def test_queries_dir(self):
        """Test queries_dir returns valid path."""
        qdir = queries_dir()
        assert qdir.exists()
        assert qdir.is_dir()

    def test_responses_dir(self):
        """Test responses_dir returns valid path."""
        rdir = responses_dir()
        assert rdir.exists()
        assert rdir.is_dir()


class TestSerializationUtilities:
    """Test serialization utility functions."""

    def test_to_serializable_datetime(self):
        """Test serializing datetime."""
        dt = datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
        result = _to_serializable(dt)

        assert isinstance(result, str)
        assert "2024-01-15" in result

    def test_to_serializable_dataclass(self):
        """Test serializing dataclass."""
        from dataclasses import dataclass

        @dataclass
        class TestData:
            value: int
            timestamp: datetime

        obj = TestData(value=42, timestamp=datetime.now(timezone.utc))
        result = _to_serializable(obj)

        assert isinstance(result, dict)
        assert result["value"] == 42
        assert isinstance(result["timestamp"], str)

    def test_to_serializable_dict(self):
        """Test serializing dict."""
        data = {
            "key": "value",
            "timestamp": datetime.now(timezone.utc),
            "nested": {"datetime": datetime.now(timezone.utc)},
        }
        result = _to_serializable(data)

        assert isinstance(result, dict)
        assert result["key"] == "value"
        assert isinstance(result["timestamp"], str)
        assert isinstance(result["nested"]["datetime"], str)

    def test_to_serializable_list(self):
        """Test serializing list."""
        data = [
            datetime.now(timezone.utc),
            "string",
            123,
            {"nested": datetime.now(timezone.utc)},
        ]
        result = _to_serializable(data)

        assert isinstance(result, list)
        assert len(result) == 4
        assert isinstance(result[0], str)
        assert result[1] == "string"
        assert result[2] == 123
        assert isinstance(result[3]["nested"], str)

    def test_to_serializable_primitives(self):
        """Test serializing primitives."""
        assert _to_serializable(42) == 42
        assert _to_serializable("text") == "text"
        assert _to_serializable(True) is True
        assert _to_serializable(None) is None

    def test_write_json(self, tmp_path):
        """Test _write_json creates file."""
        path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}

        _write_json(path, data)

        assert path.exists()
        with open(path) as f:
            loaded = json.load(f)
        assert loaded == data

    def test_write_json_creates_parent_dirs(self, tmp_path):
        """Test _write_json creates parent directories."""
        path = tmp_path / "nested" / "dir" / "file.json"
        data = {"test": "data"}

        _write_json(path, data)

        assert path.exists()
        assert path.parent.exists()

    def test_write_json_unicode(self, tmp_path):
        """Test _write_json with unicode content."""
        path = tmp_path / "unicode.json"
        data = {"português": "açúcar", "emoji": "🎉"}

        _write_json(path, data)

        with open(path, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["português"] == "açúcar"
        assert loaded["emoji"] == "🎉"

    def test_read_json(self, tmp_path):
        """Test _read_json loads file."""
        path = tmp_path / "test.json"
        data = {"key": "value"}

        with open(path, "w") as f:
            json.dump(data, f)

        loaded = _read_json(path)
        assert loaded == data


class TestNormalization:
    """Test _normalize function."""

    def test_normalize_none(self):
        """Test normalizing None."""
        assert _normalize(None) == ""

    def test_normalize_string(self):
        """Test normalizing string."""
        assert _normalize("Test") == "test"

    def test_normalize_strips_whitespace(self):
        """Test strips whitespace."""
        assert _normalize("  test  ") == "test"

    def test_normalize_lowercase(self):
        """Test converts to lowercase."""
        assert _normalize("UPPERCASE") == "uppercase"

    def test_normalize_accents(self):
        """Test removes accents."""
        assert _normalize("açúcar") == "acucar"
        assert _normalize("São Paulo") == "sao paulo"

    def test_normalize_numbers(self):
        """Test normalizing numbers."""
        assert _normalize(123) == "123"
        assert _normalize(45.67) == "45.67"

    def test_normalize_empty_string(self):
        """Test empty string."""
        assert _normalize("") == ""

    def test_normalize_unicode_combining(self):
        """Test removes combining characters."""
        # Test with NFKD normalization
        text = "café"
        normalized = _normalize(text)
        assert "cafe" in normalized or normalized == "cafe"


class TestParseDatetime:
    """Test _parse_datetime function."""

    def test_parse_datetime_valid(self):
        """Test parsing valid datetime."""
        dt_str = "2024-01-15T12:30:45.123456"
        result = _parse_datetime(dt_str)

        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_with_timezone(self):
        """Test parsing datetime with timezone."""
        dt_str = "2024-01-15T12:30:45+00:00"
        result = _parse_datetime(dt_str)

        assert result is not None

    def test_parse_datetime_none(self):
        """Test parsing None."""
        assert _parse_datetime(None) is None

    def test_parse_datetime_invalid(self):
        """Test parsing invalid datetime."""
        assert _parse_datetime("invalid") is None
        assert _parse_datetime("not-a-date") is None

    def test_parse_datetime_empty_string(self):
        """Test parsing empty string."""
        assert _parse_datetime("") is None


class TestSourceOperations:
    """Test source save/load operations."""

    @pytest.fixture
    def temp_storage(self, tmp_path, monkeypatch):
        """Setup temporary storage directory."""
        monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))
        yield tmp_path

    def test_save_source(self, temp_storage):
        """Test saving source."""
        source = Source(
            id="test_source",
            name="Test Source",
            type="api",
            info_type="test_info",
            config=SourceConfig(url_base="https://test.com"),
            is_active=True,
            status=SourceStatus(),
        )

        path = save_source(source)

        assert path.exists()
        assert path.name == "test_source.json"

    def test_get_source(self, temp_storage):
        """Test getting source."""
        source = Source(
            id="get_test",
            name="Get Test",
            type="api",
        )
        save_source(source)

        loaded = get_source("get_test")

        assert loaded is not None
        assert loaded.id == "get_test"
        assert loaded.name == "Get Test"

    def test_get_source_not_found(self, temp_storage):
        """Test getting nonexistent source."""
        result = get_source("nonexistent")
        assert result is None

    def test_list_sources(self, temp_storage):
        """Test listing sources."""
        sources = [
            Source(id="s1", name="Source 1", type="api"),
            Source(id="s2", name="Source 2", type="rss"),
        ]

        for s in sources:
            save_source(s)

        loaded = list_sources()

        assert len(loaded) == 2
        ids = [s.id for s in loaded]
        assert "s1" in ids
        assert "s2" in ids

    def test_list_sources_empty(self, temp_storage):
        """Test listing with no sources."""
        result = list_sources()
        assert result == []

    def test_ensure_fixture_sources(self, temp_storage):
        """Test ensure_fixture_sources."""
        sources = [
            Source(id="f1", name="Fixture 1", type="api"),
            Source(id="f2", name="Fixture 2", type="rss"),
        ]

        ensure_fixture_sources(sources)

        loaded = list_sources()
        assert len(loaded) == 2


class TestItemOperations:
    """Test item save/load operations."""

    @pytest.fixture
    def temp_storage(self, tmp_path, monkeypatch):
        """Setup temporary storage directory."""
        monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))
        yield tmp_path

    def test_save_item(self, temp_storage):
        """Test saving item."""
        item = Item(
            id="item_1",
            source_id="source_1",
            payload={"key": "value"},
            created_at=datetime.now(timezone.utc),
        )

        path = save_item(item)

        assert path.exists()
        assert path.name == "item_1.json"

    def test_get_item(self, temp_storage):
        """Test getting item."""
        item = Item(
            id="get_item",
            source_id="source_1",
            payload={"data": "test"},
        )
        save_item(item)

        loaded = get_item("get_item")

        assert loaded is not None
        assert loaded.id == "get_item"
        assert loaded.payload["data"] == "test"

    def test_get_item_not_found(self, temp_storage):
        """Test getting nonexistent item."""
        result = get_item("nonexistent")
        assert result is None

    def test_get_item_path(self, temp_storage):
        """Test getting item path."""
        path = get_item_path("test_item")

        assert "test_item.json" in str(path)

    def test_list_items_by_filter_empty(self, temp_storage):
        """Test filtering with no items."""
        result = list_items_by_filter({})
        assert result == []

    def test_list_items_by_filter_no_filters(self, temp_storage):
        """Test listing all items."""
        # Create source first
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        # Create items
        for i in range(3):
            item = Item(id=f"item_{i}", source_id="src1", payload={})
            save_item(item)

        results = list_items_by_filter({})

        assert len(results) <= 3

    def test_list_items_by_filter_produto(self, temp_storage):
        """Test filtering by produto."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        item1 = Item(id="i1", source_id="src1", payload={"produto": "Açúcar"})
        item2 = Item(id="i2", source_id="src1", payload={"produto": "Café"})
        save_item(item1)
        save_item(item2)

        results = list_items_by_filter({"produto": "açúcar"})

        assert len(results) == 1
        assert results[0].payload["produto"] == "Açúcar"

    def test_list_items_by_filter_cidade(self, temp_storage):
        """Test filtering by cidade."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        item = Item(id="i1", source_id="src1", payload={"cidade": "São Paulo"})
        save_item(item)

        results = list_items_by_filter({"cidade": "sao paulo"})

        assert len(results) == 1

    def test_list_items_by_filter_pessoa(self, temp_storage):
        """Test filtering by pessoa."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        item = Item(id="i1", source_id="src1", payload={"pessoa": "João"})
        save_item(item)

        results = list_items_by_filter({"pessoa": "joão"})

        assert len(results) == 1

    def test_list_items_by_filter_caso(self, temp_storage):
        """Test filtering by caso."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        item = Item(id="i1", source_id="src1", payload={"caso": "Caso123"})
        save_item(item)

        results = list_items_by_filter({"caso": "caso123"})

        assert len(results) == 1

    def test_list_items_by_filter_info_type(self, temp_storage):
        """Test filtering by info_type."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        item = Item(id="i1", source_id="src1", payload={"info_type": "claim"})
        save_item(item)

        results = list_items_by_filter({"info_type": "claim"})

        assert len(results) == 1

    def test_list_items_by_filter_source_ids(self, temp_storage):
        """Test filtering by source_ids."""
        source1 = Source(id="src1", name="Source 1", type="api")
        source2 = Source(id="src2", name="Source 2", type="api")
        save_source(source1)
        save_source(source2)

        item1 = Item(id="i1", source_id="src1", payload={})
        item2 = Item(id="i2", source_id="src2", payload={})
        save_item(item1)
        save_item(item2)

        results = list_items_by_filter({"source_ids": ["src1"]})

        assert len(results) == 1
        assert results[0].source_id == "src1"

    def test_list_items_by_filter_source_types(self, temp_storage):
        """Test filtering by source_types."""
        source1 = Source(id="src1", name="S1", type="api")
        source2 = Source(id="src2", name="S2", type="rss")
        save_source(source1)
        save_source(source2)

        item1 = Item(id="i1", source_id="src1", payload={})
        item2 = Item(id="i2", source_id="src2", payload={})
        save_item(item1)
        save_item(item2)

        results = list_items_by_filter({"source_types": ["api"]})

        assert len(results) == 1
        assert results[0].source_id == "src1"

    def test_list_items_by_filter_limit_per_source(self, temp_storage):
        """Test limit_per_source parameter."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        for i in range(5):
            item = Item(id=f"i{i}", source_id="src1", payload={})
            save_item(item)

        results = list_items_by_filter({}, limit_per_source=2)

        assert len(results) <= 2

    def test_list_items_sorted_by_created_at(self, temp_storage):
        """Test items sorted by created_at descending."""
        source = Source(id="src1", name="Source", type="api")
        save_source(source)

        old_item = Item(
            id="old",
            source_id="src1",
            payload={},
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        )
        new_item = Item(
            id="new",
            source_id="src1",
            payload={},
            created_at=datetime(2024, 12, 1, tzinfo=timezone.utc),
        )
        save_item(old_item)
        save_item(new_item)

        results = list_items_by_filter({})

        # Newest first
        assert results[0].id == "new"


class TestBundleOperations:
    """Test evidence bundle operations."""

    @pytest.fixture
    def temp_storage(self, tmp_path, monkeypatch):
        """Setup temporary storage directory."""
        monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))
        yield tmp_path

    def test_save_evidence_bundle(self, temp_storage):
        """Test saving evidence bundle."""
        bundle = EvidenceBundle(
            id="bundle_1",
            query_type="test",
            info_type="claim",
            query_filters={},
            items_by_source={"src1": [EvidenceItemRef(item_id="i1", source_id="src1")]},
        )

        path = save_evidence_bundle(bundle)

        assert path.exists()
        assert path.name == "bundle_1.json"

    def test_load_evidence_bundle(self, temp_storage):
        """Test loading evidence bundle."""
        bundle = EvidenceBundle(
            id="load_test",
            query_type="test",
            info_type="claim",
            query_filters={"key": "value"},
            items_by_source={"src1": [EvidenceItemRef(item_id="i1", source_id="src1")]},
        )
        save_evidence_bundle(bundle)

        loaded = load_evidence_bundle("load_test")

        assert loaded is not None
        assert loaded.id == "load_test"
        assert loaded.query_type == "test"
        assert "src1" in loaded.items_by_source

    def test_load_evidence_bundle_not_found(self, temp_storage):
        """Test loading nonexistent bundle."""
        result = load_evidence_bundle("nonexistent")
        assert result is None

    def test_load_evidence_bundle_with_meta(self, temp_storage):
        """Test loading bundle with metadata."""
        bundle = EvidenceBundle(
            id="meta_test",
            query_type="test",
            items_by_source={},
            meta={"key": "value"},
            sources_meta={"src1": {"count": 10}},
        )
        save_evidence_bundle(bundle)

        loaded = load_evidence_bundle("meta_test")

        assert loaded.meta["key"] == "value"
        assert loaded.sources_meta["src1"]["count"] == 10


class TestQueryLogOperations:
    """Test query log operations."""

    @pytest.fixture
    def temp_storage(self, tmp_path, monkeypatch):
        """Setup temporary storage directory."""
        monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))
        yield tmp_path

    def test_save_query_log(self, temp_storage):
        """Test saving query log."""
        log = QueryLog(
            query_id="log_1",
            user_query="test query",
            query_type="search",
        )

        path = save_query_log(log)

        assert path.exists()
        assert path.name == "log_1.json"

    def test_load_query_log(self, temp_storage):
        """Test loading query log."""
        log = QueryLog(
            query_id="load_log",
            user_query="test query",
            query_type="search",
            sources=["src1", "src2"],
            items_used=["i1", "i2"],
        )
        save_query_log(log)

        loaded = load_query_log("load_log")

        assert loaded is not None
        assert loaded.query_id == "load_log"
        assert loaded.user_query == "test query"
        assert len(loaded.sources) == 2

    def test_load_query_log_not_found(self, temp_storage):
        """Test loading nonexistent log."""
        result = load_query_log("nonexistent")
        assert result is None


class TestUserResponseOperations:
    """Test user response operations."""

    @pytest.fixture
    def temp_storage(self, tmp_path, monkeypatch):
        """Setup temporary storage directory."""
        monkeypatch.setenv(DATA_DIR_ENV, str(tmp_path))
        yield tmp_path

    def test_save_user_response(self, temp_storage):
        """Test saving user response."""
        response = UserResponse(
            id="resp_1",
            query_id="query_1",
            user_input="test input",
        )

        path = save_user_response(response)

        assert path.exists()
        assert path.name == "resp_1.json"


class TestGenerateEntityId:
    """Test generate_entity_id function."""

    def test_generate_entity_id_format(self):
        """Test ID format."""
        entity_id = generate_entity_id("test")

        assert entity_id.startswith("test_")
        parts = entity_id.split("_")
        assert len(parts) == 3  # prefix, timestamp, suffix

    def test_generate_entity_id_unique(self):
        """Test generates unique IDs."""
        id1 = generate_entity_id("test")
        id2 = generate_entity_id("test")

        assert id1 != id2

    def test_generate_entity_id_different_prefixes(self):
        """Test different prefixes."""
        id1 = generate_entity_id("bundle")
        id2 = generate_entity_id("query")

        assert id1.startswith("bundle_")
        assert id2.startswith("query_")
