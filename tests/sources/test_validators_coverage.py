"""
Tests for Sources Validators Coverage — Additional coverage

Targeted tests to cover remaining uncovered line 34 in validators.py
"""

import pytest
from unittest.mock import MagicMock

from app.sources.validators import validate_source_config


class TestValidateSourceConfigMissingFields:
    """Tests for validate_source_config with missing fields."""

    def test_missing_endpoint_with_url_base_present(self):
        """Line 34: Config with url_base but missing required fields should not add to missing list."""
        # This tests the path where endpoint_val exists (from url_base)
        # but the field is in required list
        config = {
            "url_base": "https://example.com/api",
            # endpoint is missing but url_base is present
        }

        # For news_rss, endpoint is required
        result = validate_source_config("news_rss", config)

        # Should not raise, just normalize
        assert "url_base" in result

    def test_missing_endpoint_no_url_base_allows_creation(self):
        """Line 34: Missing endpoint without url_base in development mode."""
        # In development, we allow creation without endpoint for simple cases
        config = {}

        # Should not raise, allowing development flexibility
        result = validate_source_config("news_rss", config)

        assert result == {}

    def test_config_with_endpoint_clears_missing_list(self):
        """Line 34: When endpoint is present, missing list should be cleared."""
        config = {
            "endpoint": "https://example.com/rss",
        }

        # Even if other required fields are missing, endpoint presence clears the missing list
        result = validate_source_config("news_rss", config)

        # Should successfully validate
        assert result["endpoint"] == "https://example.com/rss"
