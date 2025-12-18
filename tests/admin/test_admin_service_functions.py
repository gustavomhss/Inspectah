"""
Tests for admin/service — S37

Tests for admin service functions.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.admin.service import (
    _parse_created_at,
    _scenario_from_info_type,
    _load_fixture_records_for_source,
    _load_fixture_payload,
    ensure_fixture_sources,
    get_source_status,
    prepare_sources_for_info_type,
    set_source_active,
    trigger_source_test,
    SCENARIO_SPECS,
)


class TestGetSourceStatus:
    """Tests for get_source_status function."""

    def test_get_source_status_not_found(self):
        """Return None when source not found."""
        with patch("app.admin.service.storage") as mock_storage:
            mock_storage.get_source.return_value = None

            result = get_source_status("nonexistent_source")

            assert result is None

    def test_get_source_status_found(self):
        """Return status when source found."""
        mock_source = MagicMock()
        mock_source.id = "src_1"
        mock_source.status.last_fetch_at = datetime.now(timezone.utc)
        mock_source.status.last_fetch_status = "ok"
        mock_source.status.last_fetch_error = None
        mock_source.status.recent_items_count = 10

        with patch("app.admin.service.storage") as mock_storage:
            mock_storage.get_source.return_value = mock_source

            result = get_source_status("src_1")

            assert result is not None
            assert result.source_id == "src_1"
            assert result.last_fetch_status == "ok"


class TestSetSourceActive:
    """Tests for set_source_active function."""

    def test_set_source_active_not_found(self):
        """Return None when source not found."""
        with patch("app.admin.service.storage") as mock_storage:
            mock_storage.get_source.return_value = None

            result = set_source_active("nonexistent_source", True)

            assert result is None

    def test_set_source_active_success(self):
        """Set source active successfully."""
        mock_source = MagicMock()
        mock_source.id = "src_1"
        mock_source.info_type = "news"

        with patch("app.admin.service.storage") as mock_storage:
            with patch("app.admin.service.metrics_s9"):
                mock_storage.get_source.return_value = mock_source

                result = set_source_active("src_1", False)

                assert result is not None
                assert result.is_active is False
                mock_storage.save_source.assert_called_once()


class TestTriggerSourceTest:
    """Tests for trigger_source_test function."""

    def test_trigger_source_test_not_found(self):
        """Return error result when source not found."""
        with patch("app.admin.service.storage") as mock_storage:
            mock_storage.get_source.return_value = None

            result = trigger_source_test("nonexistent_source")

            assert result.source_id == "nonexistent_source"
            assert result.status == "erro"
            assert "não encontrada" in result.notes

    def test_trigger_source_test_no_records(self):
        """Return error when no records loaded."""
        mock_source = MagicMock()
        mock_source.id = "src_1"
        mock_source.info_type = "news"

        with patch("app.admin.service.storage") as mock_storage:
            with patch("app.admin.service.metrics_s9"):
                with patch("app.admin.service._load_fixture_records_for_source", return_value=[]):
                    mock_storage.get_source.return_value = mock_source
                    mock_storage.generate_entity_id.return_value = "item_123"

                    result = trigger_source_test("src_1")

                    assert result.status == "erro"
                    assert result.items_ingested == 0

    def test_trigger_source_test_with_records(self):
        """Return success when records loaded."""
        mock_source = MagicMock()
        mock_source.id = "src_1"
        mock_source.info_type = "news"

        records = [
            {"id": "rec_1", "title": "Test 1"},
            {"id": "rec_2", "title": "Test 2"},
        ]

        with patch("app.admin.service.storage") as mock_storage:
            with patch("app.admin.service.metrics_s9"):
                with patch("app.admin.service._load_fixture_records_for_source", return_value=records):
                    mock_storage.get_source.return_value = mock_source

                    result = trigger_source_test("src_1")

                    assert result.status == "ok"
                    assert result.items_ingested == 2
                    assert len(result.preview_items) == 2


class TestPrepareSourcesForInfoType:
    """Tests for prepare_sources_for_info_type function."""

    def test_prepare_sources_unknown_info_type(self):
        """Raise ValueError for unknown info_type."""
        with pytest.raises(ValueError, match="não mapeado"):
            prepare_sources_for_info_type("unknown_info_type")


class TestEnsureFixtureSources:
    """Tests for ensure_fixture_sources function."""

    def test_ensure_fixture_sources(self):
        """Save all sources."""
        source1 = MagicMock()
        source2 = MagicMock()

        with patch("app.admin.service.storage") as mock_storage:
            ensure_fixture_sources([source1, source2])

            assert mock_storage.save_source.call_count == 2


class TestLoadFixtureRecordsForSource:
    """Tests for _load_fixture_records_for_source function."""

    def test_load_fixture_records_not_found(self, tmp_path):
        """Return empty list when fixture not found."""
        with patch.dict(SCENARIO_SPECS, {"C1": {"fixture_dir": tmp_path, "info_type": "test", "min_sources": 1}}):
            result = _load_fixture_records_for_source("nonexistent_source")

            assert result == []

    def test_load_fixture_records_found(self, tmp_path):
        """Return items from fixture file."""
        fixture_file = tmp_path / "src_fixture.json"
        fixture_file.write_text(json.dumps({
            "items": [{"id": "item_1"}, {"id": "item_2"}]
        }))

        with patch.dict(SCENARIO_SPECS, {"C1": {"fixture_dir": tmp_path, "info_type": "test", "min_sources": 1}}):
            result = _load_fixture_records_for_source("src_fixture")

            assert len(result) == 2
            assert result[0]["id"] == "item_1"


class TestLoadFixturePayload:
    """Tests for _load_fixture_payload function."""

    def test_load_fixture_payload_with_source(self, tmp_path):
        """Load payload with source section."""
        fixture_file = tmp_path / "fixture.json"
        fixture_file.write_text(json.dumps({
            "source": {"id": "src_1", "name": "Test Source", "type": "api"},
            "items": [{"data": 1}]
        }))

        meta, items = _load_fixture_payload(fixture_file)

        assert meta["id"] == "src_1"
        assert len(items) == 1

    def test_load_fixture_payload_legacy_format(self, tmp_path):
        """Load payload with legacy format."""
        fixture_file = tmp_path / "legacy.json"
        fixture_file.write_text(json.dumps({
            "source_id": "src_legacy",
            "source_name": "Legacy Source",
            "source_type": "rss",
            "info_type": "news",
            "items": [{"field1": "val1", "field2": "val2"}]
        }))

        meta, items = _load_fixture_payload(fixture_file)

        assert meta["id"] == "src_legacy"
        assert meta["name"] == "Legacy Source"
        assert meta["params"]["info_type"] == "news"

    def test_load_fixture_payload_infer_fields(self, tmp_path):
        """Infer selected_fields from items."""
        fixture_file = tmp_path / "infer.json"
        fixture_file.write_text(json.dumps({
            "source_id": "src_infer",
            "items": [{"a": 1, "b": 2, "c": 3}]
        }))

        meta, items = _load_fixture_payload(fixture_file)

        assert "a" in meta["selected_fields"]
        assert "b" in meta["selected_fields"]


class TestScenarioFromInfoType:
    """Tests for _scenario_from_info_type function."""

    def test_scenario_from_info_type_none(self):
        """Return None for None input."""
        result = _scenario_from_info_type(None)
        assert result is None

    def test_scenario_from_info_type_not_found(self):
        """Return None for unknown info_type."""
        result = _scenario_from_info_type("unknown_type_xyz")
        assert result is None

    def test_scenario_from_info_type_found(self):
        """Return scenario for known info_type."""
        # Get a real info_type from SCENARIO_SPECS
        if SCENARIO_SPECS:
            scenario_id, spec = next(iter(SCENARIO_SPECS.items()))
            info_type = spec["info_type"]

            result = _scenario_from_info_type(info_type)

            assert result == scenario_id


class TestParseCreatedAt:
    """Tests for _parse_created_at function."""

    def test_parse_created_at_none(self):
        """Return None for None input."""
        result = _parse_created_at(None)
        assert result is None

    def test_parse_created_at_valid_iso(self):
        """Parse valid ISO datetime."""
        result = _parse_created_at("2024-01-15T10:30:00")
        assert result is not None
        assert result.year == 2024
        assert result.month == 1

    def test_parse_created_at_with_z(self):
        """Parse datetime with Z suffix."""
        result = _parse_created_at("2024-01-15T10:30:00Z")
        assert result is not None
        assert result.tzinfo is not None

    def test_parse_created_at_invalid(self):
        """Return None for invalid format."""
        result = _parse_created_at("not a date")
        assert result is None

    def test_parse_created_at_partial(self):
        """Return None for partial date."""
        result = _parse_created_at("2024-01")
        assert result is None
