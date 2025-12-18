"""
Tests for Sources Validators — S37

Tests for source validation functions.
"""

import pytest
from unittest.mock import MagicMock

from app.sources.validators import (
    validate_source_config,
    validate_source_payload,
    REQUIRED_BY_TYPE,
    MIN_REFRESH_INTERVAL,
    MAX_REFRESH_INTERVAL,
    OFFICIAL_OPEN_TYPE,
    DATA_API_TYPE,
)


class TestValidateSourceConfig:
    """Tests for validate_source_config function."""

    def test_validate_news_rss(self):
        """Validate news_rss config."""
        config = {"endpoint": "https://example.com/rss"}

        result = validate_source_config("news_rss", config)

        assert result["endpoint"] == "https://example.com/rss"

    def test_validate_gossip_feed(self):
        """Validate gossip_feed config."""
        config = {"endpoint": "https://example.com/gossip"}

        result = validate_source_config("gossip_feed", config)

        assert result["endpoint"] == "https://example.com/gossip"

    def test_validate_sports_api(self):
        """Validate sports_api config."""
        config = {"endpoint": "https://api.example.com/sports"}

        result = validate_source_config("sports_api", config)

        assert result == config

    def test_validate_weather_api(self):
        """Validate weather_api config."""
        config = {"endpoint": "https://api.weather.com/v1"}

        result = validate_source_config("weather_api", config)

        assert result == config

    def test_validate_gov_record(self):
        """Validate gov_record config."""
        config = {"endpoint": "https://gov.example.com/records"}

        result = validate_source_config("gov_record", config)

        assert result == config

    def test_validate_legislation(self):
        """Validate legislation config."""
        config = {"endpoint": "https://legislation.example.com"}

        result = validate_source_config("legislation", config)

        assert result == config

    def test_validate_science_dataset(self):
        """Validate science_dataset config."""
        config = {"endpoint": "https://data.science.com/dataset"}

        result = validate_source_config("science_dataset", config)

        assert result == config

    def test_validate_static_dataset(self):
        """Validate static_dataset config."""
        config = {"endpoint": "https://static.example.com/data.json"}

        result = validate_source_config("static_dataset", config)

        assert result == config

    def test_validate_with_url_base(self):
        """Config with url_base instead of endpoint."""
        config = {"url_base": "https://example.com"}

        result = validate_source_config("news_rss", config)

        assert "url_base" in result

    def test_validate_empty_config(self):
        """Validate empty config."""
        result = validate_source_config("news_rss", {})

        assert result == {}

    def test_validate_none_config(self):
        """Validate None config."""
        result = validate_source_config("news_rss", None)

        assert result == {}

    def test_validate_unknown_type_uses_fallback(self):
        """Unknown type uses HTTP API fallback."""
        config = {"endpoint": "https://example.com"}

        result = validate_source_config("unknown_type", config)

        assert result == config

    def test_validate_official_open_type(self):
        """Validate official_open type."""
        config = {"endpoint": "https://gov.example.com/api"}

        result = validate_source_config(OFFICIAL_OPEN_TYPE, config)

        assert result == config

    def test_validate_data_api_type(self):
        """Validate data_api type."""
        config = {"endpoint": "https://api.example.com/data"}

        result = validate_source_config(DATA_API_TYPE, config)

        assert result == config


class TestValidateSourcePayload:
    """Tests for validate_source_payload function."""

    def test_valid_payload(self):
        """Validate valid payload."""
        payload = MagicMock()
        payload.name = "Test Source"
        payload.type = "news_rss"
        payload.description = "Description"
        payload.endpoint = "https://example.com/rss"
        payload.auth_type = "none"
        payload.redundancy_role = None
        payload.redundancy_group = None
        payload.refresh_interval = 60

        # Should not raise
        validate_source_payload(payload)

    def test_empty_name_raises(self):
        """Empty name raises error."""
        payload = MagicMock()
        payload.name = "   "
        payload.type = "news_rss"

        with pytest.raises(ValueError, match="Nome da fonte"):
            validate_source_payload(payload)

    def test_missing_type_raises(self):
        """Missing type raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = ""

        with pytest.raises(ValueError, match="Tipo da fonte"):
            validate_source_payload(payload)

    def test_none_type_raises(self):
        """None type raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = None

        with pytest.raises(ValueError, match="Tipo da fonte"):
            validate_source_payload(payload)

    def test_redundancy_role_without_group_raises(self):
        """Redundancy role without group raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = "news_rss"
        payload.redundancy_role = "primary"
        payload.redundancy_group = None
        payload.refresh_interval = None

        with pytest.raises(ValueError, match="redundancy_role exige"):
            validate_source_payload(payload)

    def test_refresh_interval_too_low_raises(self):
        """Refresh interval below minimum raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = "news_rss"
        payload.redundancy_role = None
        payload.refresh_interval = 5  # Below MIN_REFRESH_INTERVAL

        with pytest.raises(ValueError, match="refresh_interval fora"):
            validate_source_payload(payload)

    def test_refresh_interval_too_high_raises(self):
        """Refresh interval above maximum raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = "news_rss"
        payload.redundancy_role = None
        payload.refresh_interval = 20000  # Above MAX_REFRESH_INTERVAL

        with pytest.raises(ValueError, match="refresh_interval fora"):
            validate_source_payload(payload)

    def test_official_open_missing_description_raises(self):
        """Official open without description raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = OFFICIAL_OPEN_TYPE
        payload.description = "   "
        payload.endpoint = "https://gov.example.com"
        payload.auth_type = "none"
        payload.redundancy_role = None
        payload.refresh_interval = None

        with pytest.raises(ValueError, match="descrição"):
            validate_source_payload(payload)

    def test_official_open_missing_endpoint_raises(self):
        """Official open without endpoint raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = OFFICIAL_OPEN_TYPE
        payload.description = "Valid description"
        payload.endpoint = None
        payload.auth_type = "none"
        payload.redundancy_role = None
        payload.refresh_interval = None

        with pytest.raises(ValueError, match="endpoint"):
            validate_source_payload(payload)

    def test_official_open_with_auth_raises(self):
        """Official open with auth raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = OFFICIAL_OPEN_TYPE
        payload.description = "Valid description"
        payload.endpoint = "https://gov.example.com"
        payload.auth_type = "bearer"  # Should be none
        payload.redundancy_role = None
        payload.refresh_interval = None

        with pytest.raises(ValueError, match="autenticação"):
            validate_source_payload(payload)

    def test_data_api_missing_endpoint_raises(self):
        """Data API without endpoint raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = DATA_API_TYPE
        payload.endpoint = None
        payload.redundancy_role = None
        payload.refresh_interval = None

        with pytest.raises(ValueError, match="endpoint público"):
            validate_source_payload(payload)

    def test_data_api_invalid_endpoint_raises(self):
        """Data API with invalid endpoint raises error."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = DATA_API_TYPE
        payload.endpoint = "https://example.com/data"  # Missing /api or /v1
        payload.redundancy_role = None
        payload.refresh_interval = None

        with pytest.raises(ValueError, match="parece inválido"):
            validate_source_payload(payload)

    def test_data_api_valid_endpoint_with_api(self):
        """Data API with valid /api endpoint."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = DATA_API_TYPE
        payload.endpoint = "https://example.com/api/v1/data"
        payload.redundancy_role = None
        payload.refresh_interval = None

        # Should not raise
        validate_source_payload(payload)

    def test_data_api_valid_endpoint_with_v1(self):
        """Data API with valid /v1 endpoint."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = DATA_API_TYPE
        payload.endpoint = "https://example.com/v1/data"
        payload.redundancy_role = None
        payload.refresh_interval = None

        # Should not raise
        validate_source_payload(payload)

    def test_data_api_valid_endpoint_with_query(self):
        """Data API with valid query endpoint."""
        payload = MagicMock()
        payload.name = "Test"
        payload.type = DATA_API_TYPE
        payload.endpoint = "https://example.com/data?format=json"
        payload.redundancy_role = None
        payload.refresh_interval = None

        # Should not raise
        validate_source_payload(payload)


class TestConstants:
    """Tests for module constants."""

    def test_min_refresh_interval(self):
        """MIN_REFRESH_INTERVAL is defined."""
        assert MIN_REFRESH_INTERVAL == 15

    def test_max_refresh_interval(self):
        """MAX_REFRESH_INTERVAL is defined."""
        assert MAX_REFRESH_INTERVAL == 10080

    def test_required_by_type_has_expected_keys(self):
        """REQUIRED_BY_TYPE has expected keys."""
        assert "news_rss" in REQUIRED_BY_TYPE
        assert "gossip_feed" in REQUIRED_BY_TYPE
        assert "sports_api" in REQUIRED_BY_TYPE
        assert "weather_api" in REQUIRED_BY_TYPE
        assert "gov_record" in REQUIRED_BY_TYPE
        assert OFFICIAL_OPEN_TYPE in REQUIRED_BY_TYPE
        assert DATA_API_TYPE in REQUIRED_BY_TYPE
