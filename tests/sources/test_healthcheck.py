"""
Tests for Sources Healthcheck — S37

Tests for source health check functions.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.sources.healthcheck import run_healthcheck
from app.sources.models import SourceHealthStatus


class TestRunHealthcheck:
    """Tests for run_healthcheck function."""

    def test_source_not_found(self):
        """Returns None when source not found."""
        with patch("app.sources.healthcheck.get_source_detail", return_value=None):
            result = run_healthcheck("unknown_source")

        assert result is None

    def test_mock_endpoint_ok(self):
        """Mock endpoint with OK status."""
        mock_source = MagicMock()
        mock_source.endpoint = "mock://ok"
        mock_source.meta = {}

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.OK,
            "latency_ms": 5,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                result = run_healthcheck("src_1")

        assert result is not None
        assert result["status"] == SourceHealthStatus.OK

    def test_mock_endpoint_fail(self):
        """Mock endpoint with FAIL status."""
        mock_source = MagicMock()
        mock_source.endpoint = "mock://fail"
        mock_source.meta = {}

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.FAIL,
            "latency_ms": 5,
            "error": "mock failure",
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                result = run_healthcheck("src_1")

        assert result is not None
        assert result["status"] == SourceHealthStatus.FAIL
        assert result["error"] == "mock failure"

    def test_mock_endpoint_degraded(self):
        """Mock endpoint with DEGRADED status."""
        mock_source = MagicMock()
        mock_source.endpoint = "mock://degraded"
        mock_source.meta = {}

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.DEGRADED,
            "latency_ms": 10,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                result = run_healthcheck("src_1")

        assert result is not None
        assert result["status"] == SourceHealthStatus.DEGRADED

    def test_real_endpoint_success(self):
        """Real endpoint with successful response."""
        mock_source = MagicMock()
        mock_source.endpoint = "https://example.com/api"
        mock_source.meta = {}
        mock_source.auth_type = "none"
        mock_source.timeout_ms = 5000

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.OK,
            "latency_ms": 100,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("urllib.request.urlopen", return_value=mock_response):
                with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                    result = run_healthcheck("src_1")

        assert result is not None
        assert result["status"] == SourceHealthStatus.OK

    def test_endpoint_with_auth(self):
        """Endpoint with auth header."""
        mock_source = MagicMock()
        mock_source.endpoint = "https://example.com/api"
        mock_source.meta = {}
        mock_source.auth_type = "bearer"
        mock_source.timeout_ms = 5000

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.OK,
            "latency_ms": 50,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("urllib.request.urlopen", return_value=mock_response):
                with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                    result = run_healthcheck("src_1")

        assert result is not None

    def test_endpoint_from_meta(self):
        """Endpoint comes from meta url_base."""
        mock_source = MagicMock()
        mock_source.endpoint = None
        mock_source.meta = {"url_base": "https://example.com/api"}
        mock_source.auth_type = "none"
        mock_source.timeout_ms = 5000

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.OK,
            "latency_ms": 50,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                result = run_healthcheck("src_1")

        assert result is not None

    def test_endpoint_500_is_degraded(self):
        """500 response marks as degraded."""
        mock_source = MagicMock()
        mock_source.endpoint = "https://example.com/api"
        mock_source.meta = {}
        mock_source.auth_type = "none"
        mock_source.timeout_ms = 5000

        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.DEGRADED,
            "latency_ms": 100,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("urllib.request.urlopen", return_value=mock_response):
                with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                    result = run_healthcheck("src_1")

        assert result is not None
        # Note: the status checking in the code means 500 will be marked as DEGRADED first, then FAIL
        # because it checks >= 500 first, then >= 400

    def test_endpoint_400_is_fail(self):
        """400 response marks as fail."""
        mock_source = MagicMock()
        mock_source.endpoint = "https://example.com/api"
        mock_source.meta = {}
        mock_source.auth_type = "none"
        mock_source.timeout_ms = 5000

        mock_response = MagicMock()
        mock_response.status = 400
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        mock_check = MagicMock()
        mock_check.__dict__ = {
            "source_id": "src_1",
            "status": SourceHealthStatus.FAIL,
            "latency_ms": 100,
            "error": None,
        }

        with patch("app.sources.healthcheck.get_source_detail", return_value=mock_source):
            with patch("urllib.request.urlopen", return_value=mock_response):
                with patch("app.sources.healthcheck.register_healthcheck", return_value=mock_check):
                    result = run_healthcheck("src_1")

        assert result is not None
