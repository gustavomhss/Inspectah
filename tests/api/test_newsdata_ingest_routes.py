"""
Tests for api/newsdata_ingest_routes — S37

Tests for newsdata ingest API with role checks.
"""

import pytest
from unittest.mock import MagicMock

from app.api.newsdata_ingest_routes import _require_ops_ingest


def _make_request_mock(role: str = None) -> MagicMock:
    """Create a mock Request object with the given role in state."""
    request = MagicMock()
    request.state = MagicMock()
    if role is not None:
        request.state.role = role
    else:
        # Simulate missing role attribute
        del request.state.role
    return request


class TestRequireOpsIngest:
    """Tests for _require_ops_ingest dependency."""

    def test_require_ops_ingest_valid_role(self):
        """Valid ops_ingest role passes."""
        request = _make_request_mock("ops_ingest")
        result = _require_ops_ingest(request)

        assert result == "ops_ingest"

    def test_require_ops_ingest_multiple_roles(self):
        """ops_ingest in multiple roles passes."""
        request = _make_request_mock("admin,ops_ingest,viewer")
        result = _require_ops_ingest(request)

        assert result == "admin,ops_ingest,viewer"

    def test_require_ops_ingest_missing_role(self):
        """Missing ops_ingest role raises 403."""
        from fastapi import HTTPException

        request = _make_request_mock("admin,viewer")
        with pytest.raises(HTTPException) as exc_info:
            _require_ops_ingest(request)

        assert exc_info.value.status_code == 403
        assert "ops_ingest" in str(exc_info.value.detail)

    def test_require_ops_ingest_empty_role(self):
        """Empty role string raises 403."""
        from fastapi import HTTPException

        request = _make_request_mock("")
        with pytest.raises(HTTPException) as exc_info:
            _require_ops_ingest(request)

        assert exc_info.value.status_code == 403

    def test_require_ops_ingest_no_role_in_state(self):
        """Missing role in request.state raises 403."""
        from fastapi import HTTPException

        request = _make_request_mock(None)  # No role attribute
        with pytest.raises(HTTPException) as exc_info:
            _require_ops_ingest(request)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail["error"] == "forbidden"
