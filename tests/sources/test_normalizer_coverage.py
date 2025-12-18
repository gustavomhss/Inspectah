"""
Tests for Sources Normalizer Coverage — Coverage gaps

Targeted tests to cover remaining uncovered lines in normalizer.py
"""

import pytest
from unittest.mock import MagicMock
from dataclasses import replace
from datetime import datetime, timezone

from app.sources.normalizer import (
    _looks_like_rss,
    _normalize_base_fields,
    normalize_source_model,
    LAB_ENDPOINT,
)
from app.sources.models import Source, SourceState


def _make_source(**overrides):
    """Helper to create a Source with all required fields."""
    defaults = {
        "id": "test-id",
        "slug": "test-slug",
        "name": "Test Source",
        "description": "Test description",
        "type": "news_rss",
        "category": "official",
        "themes": [],
        "info_types": [],
        "refresh_interval": 60,
        "protocol": "https",
        "format": "rss",
        "endpoint": "https://example.com/rss",
        "auth_type": "none",
        "auth_config": {},
        "request_params": {},
        "headers": {},
        "frequency": "hourly",
        "timeout_ms": 30000,
        "retry_policy": {},
        "parsing_config": {},
        "redundancy_group": None,
        "redundancy_role": None,
        "state": SourceState.ACTIVE,
        "state_reason": None,
        "state_updated_at": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "created_by": "test",
        "updated_by": "test",
        "meta": {},
    }
    defaults.update(overrides)
    return Source(**defaults)


class TestLooksLikeRss:
    """Tests for _looks_like_rss function."""

    def test_none_endpoint_returns_false(self):
        """Line 16: None endpoint should return False."""
        result = _looks_like_rss(None)
        assert result is False

    def test_empty_string_endpoint_returns_false(self):
        """Line 16: Empty string endpoint should return False."""
        result = _looks_like_rss("")
        assert result is False


class TestNormalizeBaseFields:
    """Tests for _normalize_base_fields function."""

    def test_science_dataset_with_invalid_format(self):
        """Lines 30-31: Science dataset with invalid format should be set to csv."""
        data = {
            "type": "science_dataset",
            "endpoint": "https://example.com/data",
            "format": "xml",  # Invalid format, not csv
        }

        result = _normalize_base_fields(data)

        assert result["format"] == "csv"

    def test_science_dataset_with_csv_format_unchanged(self):
        """Lines 30-31: Science dataset with csv format should remain unchanged."""
        data = {
            "type": "science_dataset",
            "endpoint": "https://example.com/data",
            "format": "csv",
        }

        result = _normalize_base_fields(data)

        assert result["format"] == "csv"

    def test_science_dataset_with_none_format(self):
        """Lines 30-31: Science dataset with None format should not be changed to csv."""
        data = {
            "type": "science_dataset",
            "endpoint": "https://example.com/data",
            "format": None,
        }

        result = _normalize_base_fields(data)

        # format None should remain None, not be set to csv
        assert result.get("format") is None


class TestNormalizeSourceModel:
    """Tests for normalize_source_model function."""

    def test_lab_endpoint_active_state_becomes_proposed(self):
        """Lines 74-75: Lab endpoint with ACTIVE state should become PROPOSED."""
        source = _make_source(
            endpoint=LAB_ENDPOINT,
            state=SourceState.ACTIVE,
        )

        result = normalize_source_model(source)

        # State should be changed to PROPOSED
        assert result.state == SourceState.PROPOSED
        # Category should be changed to internal_test for lab sources
        assert result.category == "internal_test"

    def test_lab_endpoint_non_active_state_unchanged(self):
        """Lines 74-75: Lab endpoint with non-ACTIVE state should remain unchanged."""
        source = _make_source(
            endpoint=LAB_ENDPOINT,
            state=SourceState.PROPOSED,
        )

        result = normalize_source_model(source)

        # Should remain PROPOSED
        assert result.state == SourceState.PROPOSED

    def test_lab_endpoint_active_state_with_existing_state_reason(self):
        """Lines 74-75: Lab endpoint with existing state_reason should use setdefault."""
        # Test that setdefault doesn't override existing state_reason
        source = _make_source(
            endpoint=LAB_ENDPOINT,
            state=SourceState.ACTIVE,
            state_reason="Existing reason",
        )

        result = normalize_source_model(source)

        # State should be changed to PROPOSED
        assert result.state == SourceState.PROPOSED
        # Existing state_reason should be preserved (setdefault behavior)
        assert result.state_reason == "Existing reason"
