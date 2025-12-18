"""
Tests for S40-BE-025: Provenance Middleware.

Tests for app/api/middleware/provenance.py.
"""

from __future__ import annotations

import pytest

from app.api.middleware.provenance import (
    check_provenance,
    mark_invalid_provenance,
    validate_provenance_response,
    validate_provenance_dict,
    record_provenance_check,
    get_provenance_stats,
    reset_provenance_stats,
    PROVENANCE_REQUIRED_PATHS,
    PROVENANCE_PATTERNS,
)


class TestCheckProvenance:
    """Tests for check_provenance function."""

    def test_valid_provenance(self):
        """Test valid provenance with source and timestamp."""
        data = {
            "provenance": {
                "source": "decision_block",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        assert check_provenance(data) is True

    def test_valid_provenance_with_extra_fields(self):
        """Test valid provenance with additional fields."""
        data = {
            "provenance": {
                "source": "guardian_flow",
                "timestamp": "2025-01-01T00:00:00Z",
                "policy_version": "1.0.0",
                "policy_name": "saude_v1",
                "actor": "system",
                "evidence_refs": ["ev-001"],
            }
        }
        assert check_provenance(data) is True

    def test_invalid_no_provenance_field(self):
        """Test invalid when provenance field is missing."""
        data = {"claim_id": "claim-001", "status": "ok"}
        assert check_provenance(data) is False

    def test_invalid_provenance_none(self):
        """Test invalid when provenance is None."""
        data = {"provenance": None}
        assert check_provenance(data) is False

    def test_invalid_provenance_not_dict(self):
        """Test invalid when provenance is not a dict."""
        data = {"provenance": "string_value"}
        assert check_provenance(data) is False

    def test_invalid_provenance_list(self):
        """Test invalid when provenance is a list."""
        data = {"provenance": ["source", "timestamp"]}
        assert check_provenance(data) is False

    def test_invalid_missing_source(self):
        """Test invalid when source is missing."""
        data = {
            "provenance": {
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        assert check_provenance(data) is False

    def test_invalid_missing_timestamp(self):
        """Test invalid when timestamp is missing."""
        data = {
            "provenance": {
                "source": "decision_block",
            }
        }
        assert check_provenance(data) is False

    def test_invalid_empty_source(self):
        """Test invalid when source is empty string."""
        data = {
            "provenance": {
                "source": "",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        assert check_provenance(data) is False

    def test_invalid_empty_timestamp(self):
        """Test invalid when timestamp is empty string."""
        data = {
            "provenance": {
                "source": "decision_block",
                "timestamp": "",
            }
        }
        assert check_provenance(data) is False

    def test_invalid_data_not_dict(self):
        """Test invalid when data is not a dict."""
        assert check_provenance("string") is False
        assert check_provenance(123) is False
        assert check_provenance([]) is False
        assert check_provenance(None) is False

    def test_valid_provenance_with_none_optional_fields(self):
        """Test valid provenance when optional fields are None."""
        data = {
            "provenance": {
                "source": "test",
                "timestamp": "2025-01-01T00:00:00Z",
                "policy_version": None,
                "policy_name": None,
            }
        }
        assert check_provenance(data) is True


class TestMarkInvalidProvenance:
    """Tests for mark_invalid_provenance function."""

    def test_mark_invalid_adds_fields(self):
        """Test that marking adds _provenance_valid and _provenance_warning."""
        data = {"claim_id": "claim-001"}
        result = mark_invalid_provenance(data)

        assert result["_provenance_valid"] is False
        assert "_provenance_warning" in result
        assert "lacks valid provenance" in result["_provenance_warning"]

    def test_mark_invalid_preserves_existing_data(self):
        """Test that marking preserves existing data."""
        data = {
            "claim_id": "claim-001",
            "domain": "saude",
            "status": "pending",
        }
        result = mark_invalid_provenance(data)

        assert result["claim_id"] == "claim-001"
        assert result["domain"] == "saude"
        assert result["status"] == "pending"
        assert result["_provenance_valid"] is False

    def test_mark_invalid_overwrites_existing_flag(self):
        """Test that marking overwrites existing _provenance_valid."""
        data = {"_provenance_valid": True}
        result = mark_invalid_provenance(data)

        assert result["_provenance_valid"] is False


class TestValidateProvenanceResponse:
    """Tests for validate_provenance_response function."""

    def test_validate_valid_provenance(self):
        """Test validating data with valid provenance."""
        data = {
            "claim_id": "claim-001",
            "provenance": {
                "source": "decision_block",
                "timestamp": "2025-01-01T00:00:00Z",
            },
        }
        result = validate_provenance_response(data)

        assert result["_provenance_valid"] is True
        assert "_provenance_warning" not in result

    def test_validate_invalid_provenance(self):
        """Test validating data without valid provenance."""
        data = {"claim_id": "claim-001"}
        result = validate_provenance_response(data)

        assert result["_provenance_valid"] is False
        assert "_provenance_warning" in result

    def test_validate_preserves_data(self):
        """Test that validation preserves original data."""
        data = {
            "claim_id": "claim-001",
            "domain": "saude",
            "nested": {"key": "value"},
            "provenance": {
                "source": "test",
                "timestamp": "2025-01-01T00:00:00Z",
            },
        }
        result = validate_provenance_response(data)

        assert result["claim_id"] == "claim-001"
        assert result["domain"] == "saude"
        assert result["nested"]["key"] == "value"


class TestValidateProvenanceDict:
    """Tests for validate_provenance_dict function."""

    def test_validates_truth_twin_path(self):
        """Test validation for truth twin path."""
        data = {"claim_id": "claim-001"}
        result = validate_provenance_dict(data, "/api/truth/claim-001/twin")

        assert result["_provenance_valid"] is False

    def test_validates_truth_inspect_path(self):
        """Test validation for truth inspect path."""
        data = {"decision_id": "dec-001"}
        result = validate_provenance_dict(data, "/api/truth/decision/dec-001/inspect")

        assert result["_provenance_valid"] is False

    def test_validates_truth_timeline_path(self):
        """Test validation for truth timeline path."""
        data = {"claim_id": "claim-001"}
        result = validate_provenance_dict(data, "/api/truth/claim-001/timeline")

        assert result["_provenance_valid"] is False

    def test_skips_non_truth_path(self):
        """Test that non-truth paths are skipped."""
        data = {"claim_id": "claim-001"}
        result = validate_provenance_dict(data, "/api/claims/claim-001")

        # Should return original data unchanged
        assert "_provenance_valid" not in result
        assert result == data

    def test_skips_truth_path_without_patterns(self):
        """Test that truth paths without patterns are skipped."""
        data = {"claim_id": "claim-001"}
        result = validate_provenance_dict(data, "/api/truth/promotion")

        # Should return original data unchanged
        assert "_provenance_valid" not in result

    def test_valid_provenance_on_truth_path(self):
        """Test valid provenance on truth path."""
        data = {
            "claim_id": "claim-001",
            "provenance": {
                "source": "decision_block",
                "timestamp": "2025-01-01T00:00:00Z",
            },
        }
        result = validate_provenance_dict(data, "/api/truth/claim-001/twin")

        assert result["_provenance_valid"] is True


class TestProvenancePaths:
    """Tests for provenance path configuration."""

    def test_required_paths_defined(self):
        """Test that required paths are defined."""
        assert len(PROVENANCE_REQUIRED_PATHS) > 0
        assert "/api/truth/" in PROVENANCE_REQUIRED_PATHS

    def test_patterns_defined(self):
        """Test that patterns are defined."""
        assert len(PROVENANCE_PATTERNS) > 0
        assert "/twin" in PROVENANCE_PATTERNS
        assert "/inspect" in PROVENANCE_PATTERNS
        assert "/timeline" in PROVENANCE_PATTERNS


class TestProvenanceStats:
    """Tests for provenance statistics tracking."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_provenance_stats()

    def test_record_valid_check(self):
        """Test recording a valid provenance check."""
        record_provenance_check(valid=True)
        stats = get_provenance_stats()

        assert stats["total_checks"] == 1
        assert stats["valid"] == 1
        assert stats["invalid"] == 0

    def test_record_invalid_check(self):
        """Test recording an invalid provenance check."""
        record_provenance_check(valid=False)
        stats = get_provenance_stats()

        assert stats["total_checks"] == 1
        assert stats["valid"] == 0
        assert stats["invalid"] == 1

    def test_record_multiple_checks(self):
        """Test recording multiple checks."""
        record_provenance_check(valid=True)
        record_provenance_check(valid=True)
        record_provenance_check(valid=False)
        record_provenance_check(valid=True)
        record_provenance_check(valid=False)

        stats = get_provenance_stats()

        assert stats["total_checks"] == 5
        assert stats["valid"] == 3
        assert stats["invalid"] == 2

    def test_get_stats_initial(self):
        """Test getting initial stats."""
        stats = get_provenance_stats()

        assert stats["total_checks"] == 0
        assert stats["valid"] == 0
        assert stats["invalid"] == 0

    def test_reset_stats(self):
        """Test resetting stats."""
        record_provenance_check(valid=True)
        record_provenance_check(valid=False)

        reset_provenance_stats()

        stats = get_provenance_stats()
        assert stats["total_checks"] == 0
        assert stats["valid"] == 0
        assert stats["invalid"] == 0


class TestProvenanceMiddlewareImport:
    """Tests for ProvenanceMiddleware class import."""

    def test_middleware_class_importable(self):
        """Test that ProvenanceMiddleware is importable."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        assert ProvenanceMiddleware is not None

    def test_middleware_init_importable(self):
        """Test that middleware __init__ exports are correct."""
        from app.api.middleware import ProvenanceMiddleware, check_provenance
        assert ProvenanceMiddleware is not None
        assert check_provenance is not None


class TestProvenanceMiddlewareClass:
    """Tests for ProvenanceMiddleware class."""

    def test_requires_provenance_truth_twin(self):
        """Test _requires_provenance for twin path."""
        from app.api.middleware.provenance import ProvenanceMiddleware

        middleware = ProvenanceMiddleware(app=None)
        assert middleware._requires_provenance("/api/truth/claim-001/twin") is True

    def test_requires_provenance_truth_inspect(self):
        """Test _requires_provenance for inspect path."""
        from app.api.middleware.provenance import ProvenanceMiddleware

        middleware = ProvenanceMiddleware(app=None)
        assert middleware._requires_provenance("/api/truth/decision/dec-001/inspect") is True

    def test_requires_provenance_truth_timeline(self):
        """Test _requires_provenance for timeline path."""
        from app.api.middleware.provenance import ProvenanceMiddleware

        middleware = ProvenanceMiddleware(app=None)
        assert middleware._requires_provenance("/api/truth/claim-001/timeline") is True

    def test_requires_provenance_non_truth_path(self):
        """Test _requires_provenance for non-truth path."""
        from app.api.middleware.provenance import ProvenanceMiddleware

        middleware = ProvenanceMiddleware(app=None)
        assert middleware._requires_provenance("/api/claims/claim-001") is False

    def test_requires_provenance_truth_without_pattern(self):
        """Test _requires_provenance for truth path without pattern."""
        from app.api.middleware.provenance import ProvenanceMiddleware

        middleware = ProvenanceMiddleware(app=None)
        assert middleware._requires_provenance("/api/truth/promotion") is False

    @pytest.mark.asyncio
    async def test_validate_response_valid_json(self):
        """Test _validate_response with valid JSON and provenance."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        import json

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        body = json.dumps({
            "claim_id": "claim-001",
            "provenance": {"source": "test", "timestamp": "2025-01-01T00:00:00Z"},
        }).encode()

        async def body_iterator():
            yield body

        mock_response = Response(content=body, media_type="application/json")
        mock_response.body_iterator = body_iterator()

        result = await middleware._validate_response(mock_response)
        result_body = result.body
        result_data = json.loads(result_body)

        assert result_data["_provenance_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_response_invalid_json(self):
        """Test _validate_response with invalid JSON."""
        from app.api.middleware.provenance import ProvenanceMiddleware

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        body = b"not valid json"

        async def body_iterator():
            yield body

        mock_response = Response(content=body, media_type="application/json")
        mock_response.body_iterator = body_iterator()

        result = await middleware._validate_response(mock_response)
        # Should return unchanged when JSON is invalid
        assert result.body == body

    @pytest.mark.asyncio
    async def test_validate_response_missing_provenance(self):
        """Test _validate_response with missing provenance."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        import json

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        body = json.dumps({"claim_id": "claim-001"}).encode()

        async def body_iterator():
            yield body

        mock_response = Response(content=body, media_type="application/json")
        mock_response.body_iterator = body_iterator()

        result = await middleware._validate_response(mock_response)
        result_data = json.loads(result.body)

        assert result_data["_provenance_valid"] is False
        assert "_provenance_warning" in result_data

    @pytest.mark.asyncio
    async def test_dispatch_non_provenance_path(self):
        """Test dispatch for non-provenance path."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        from unittest.mock import AsyncMock, MagicMock

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        # Mock request
        mock_request = MagicMock()
        mock_request.url.path = "/api/claims/claim-001"

        # Mock response
        mock_response = Response(content=b'{"test": true}', status_code=200)

        # Mock call_next
        async def call_next(request):
            return mock_response

        result = await middleware.dispatch(mock_request, call_next)

        # Should add latency header
        assert "X-Provenance-Check-Latency-Ms" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_provenance_path_200(self):
        """Test dispatch for provenance path with 200 response."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        from unittest.mock import MagicMock
        import json

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        # Mock request
        mock_request = MagicMock()
        mock_request.url.path = "/api/truth/claim-001/twin"

        # Create response with proper body_iterator
        body = json.dumps({"claim_id": "claim-001"}).encode()

        class MockResponse:
            status_code = 200
            headers = {"content-type": "application/json"}
            media_type = "application/json"

            async def __aiter__(self):
                yield body

            @property
            def body_iterator(self):
                return self.__aiter__()

        mock_response = MockResponse()

        async def call_next(request):
            return mock_response

        result = await middleware.dispatch(mock_request, call_next)
        assert "X-Provenance-Check-Latency-Ms" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_provenance_path_non_200(self):
        """Test dispatch for provenance path with non-200 response."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        from unittest.mock import MagicMock

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        # Mock request
        mock_request = MagicMock()
        mock_request.url.path = "/api/truth/claim-001/twin"

        # Mock 404 response
        mock_response = Response(content=b'{"error": "not found"}', status_code=404)

        async def call_next(request):
            return mock_response

        result = await middleware.dispatch(mock_request, call_next)

        # Should not modify non-200 responses
        assert result.status_code == 404

    @pytest.mark.asyncio
    async def test_dispatch_validation_exception(self):
        """Test dispatch handles validation exceptions gracefully."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        from unittest.mock import MagicMock, patch

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        # Mock request for provenance path
        mock_request = MagicMock()
        mock_request.url.path = "/api/truth/claim-001/twin"

        # Create a mock response that will cause an exception during validation
        class BrokenResponse:
            status_code = 200
            headers = {"content-type": "application/json"}
            media_type = "application/json"

            async def __aiter__(self):
                raise RuntimeError("Broken iterator")

            @property
            def body_iterator(self):
                return self.__aiter__()

        mock_response = BrokenResponse()

        async def call_next(request):
            return mock_response

        # Should not raise, should log warning and continue
        result = await middleware.dispatch(mock_request, call_next)
        assert "X-Provenance-Check-Latency-Ms" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_non_json_content_type(self):
        """Test dispatch skips validation for non-JSON content."""
        from app.api.middleware.provenance import ProvenanceMiddleware
        from unittest.mock import MagicMock

        try:
            from starlette.responses import Response
        except ImportError:
            pytest.skip("Starlette not available")

        middleware = ProvenanceMiddleware(app=None)

        # Mock request for provenance path
        mock_request = MagicMock()
        mock_request.url.path = "/api/truth/claim-001/twin"

        # Mock response with non-JSON content type
        mock_response = Response(
            content=b"<html>test</html>",
            status_code=200,
            media_type="text/html",
        )

        async def call_next(request):
            return mock_response

        result = await middleware.dispatch(mock_request, call_next)

        # Should return unchanged for non-JSON
        assert result.body == b"<html>test</html>"
        assert "X-Provenance-Check-Latency-Ms" in result.headers


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_data_dict(self):
        """Test validation with empty dict."""
        data = {}
        result = validate_provenance_response(data)

        assert result["_provenance_valid"] is False

    def test_deeply_nested_provenance(self):
        """Test that only top-level provenance is checked."""
        data = {
            "nested": {
                "provenance": {
                    "source": "nested",
                    "timestamp": "2025-01-01T00:00:00Z",
                }
            }
        }
        # Top-level provenance is missing
        result = validate_provenance_response(data)
        assert result["_provenance_valid"] is False

    def test_provenance_with_whitespace_source(self):
        """Test provenance with whitespace-only source."""
        data = {
            "provenance": {
                "source": "   ",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        # Whitespace is truthy, so this passes
        assert check_provenance(data) is True

    def test_provenance_with_numeric_source(self):
        """Test provenance with numeric source."""
        data = {
            "provenance": {
                "source": 123,
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        # Non-zero number is truthy
        assert check_provenance(data) is True

    def test_provenance_with_zero_source(self):
        """Test provenance with zero source."""
        data = {
            "provenance": {
                "source": 0,
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        # Zero is falsy
        assert check_provenance(data) is False

    def test_validate_dict_with_query_params_in_path(self):
        """Test validation with query params in path."""
        data = {"claim_id": "claim-001"}
        result = validate_provenance_dict(data, "/api/truth/claim-001/twin?limit=10")

        assert result["_provenance_valid"] is False

    def test_validate_dict_case_sensitivity(self):
        """Test that path matching is case-sensitive."""
        data = {"claim_id": "claim-001"}

        # Uppercase should not match
        result = validate_provenance_dict(data, "/API/TRUTH/claim-001/TWIN")
        assert "_provenance_valid" not in result

    def test_multiple_patterns_in_path(self):
        """Test path with multiple patterns."""
        data = {"claim_id": "claim-001"}
        # Both twin and timeline in path - should still validate
        result = validate_provenance_dict(data, "/api/truth/claim-001/twin/timeline")

        assert result["_provenance_valid"] is False


class TestTimestampValidation:
    """Tests for timestamp validation."""

    def test_valid_iso8601_timestamp(self):
        """Test valid ISO 8601 timestamps."""
        from app.api.middleware.provenance import _is_valid_timestamp

        assert _is_valid_timestamp("2025-01-01T00:00:00Z") is True
        assert _is_valid_timestamp("2025-12-31T23:59:59Z") is True
        assert _is_valid_timestamp("2025-06-15T12:30:45.123Z") is True
        assert _is_valid_timestamp("2025-01-01 00:00:00") is True  # Space separator

    def test_invalid_timestamp_format(self):
        """Test invalid timestamp formats."""
        from app.api.middleware.provenance import _is_valid_timestamp

        assert _is_valid_timestamp("01-01-2025") is False
        assert _is_valid_timestamp("2025/01/01") is False
        assert _is_valid_timestamp("Jan 1, 2025") is False
        assert _is_valid_timestamp("yesterday") is False

    def test_invalid_timestamp_types(self):
        """Test non-string timestamp types."""
        from app.api.middleware.provenance import _is_valid_timestamp

        assert _is_valid_timestamp(None) is False
        assert _is_valid_timestamp(123456789) is False
        assert _is_valid_timestamp([]) is False
        assert _is_valid_timestamp({}) is False

    def test_empty_timestamp(self):
        """Test empty timestamp."""
        from app.api.middleware.provenance import _is_valid_timestamp

        assert _is_valid_timestamp("") is False
        assert _is_valid_timestamp("   ") is False


class TestDetailedValidation:
    """Tests for check_provenance_detailed function."""

    def test_detailed_valid_provenance(self):
        """Test detailed validation with valid provenance."""
        from app.api.middleware.provenance import check_provenance_detailed

        data = {
            "provenance": {
                "source": "test_source",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        is_valid, issues = check_provenance_detailed(data)

        assert is_valid is True
        assert issues == []

    def test_detailed_missing_provenance(self):
        """Test detailed validation with missing provenance."""
        from app.api.middleware.provenance import check_provenance_detailed

        data = {"claim_id": "c1"}
        is_valid, issues = check_provenance_detailed(data)

        assert is_valid is False
        assert "Missing 'provenance' field" in issues

    def test_detailed_missing_source(self):
        """Test detailed validation with missing source."""
        from app.api.middleware.provenance import check_provenance_detailed

        data = {
            "provenance": {
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        is_valid, issues = check_provenance_detailed(data)

        assert is_valid is False
        assert any("source" in issue for issue in issues)

    def test_detailed_invalid_timestamp_format(self):
        """Test detailed validation reports timestamp format issues."""
        from app.api.middleware.provenance import check_provenance_detailed

        data = {
            "provenance": {
                "source": "test",
                "timestamp": "invalid-date",
            }
        }
        is_valid, issues = check_provenance_detailed(data)

        # Note: non-ISO timestamps with valid source still pass basic check
        # but detailed check reports the format issue
        assert any("ISO 8601" in issue for issue in issues)

    def test_detailed_none_data(self):
        """Test detailed validation with None data."""
        from app.api.middleware.provenance import check_provenance_detailed

        is_valid, issues = check_provenance_detailed(None)

        assert is_valid is False
        assert "Data is None" in issues

    def test_detailed_non_dict_data(self):
        """Test detailed validation with non-dict data."""
        from app.api.middleware.provenance import check_provenance_detailed

        is_valid, issues = check_provenance_detailed("not a dict")

        assert is_valid is False
        assert any("not a dict" in issue for issue in issues)


class TestValidateProvenanceResponseDetailed:
    """Tests for validate_provenance_response with detailed mode."""

    def test_detailed_mode_includes_issues(self):
        """Test that detailed mode includes validation issues."""
        data = {"claim_id": "c1"}
        result = validate_provenance_response(data, detailed=True)

        assert result["_provenance_valid"] is False
        assert "_provenance_issues" in result
        assert len(result["_provenance_issues"]) > 0

    def test_detailed_mode_valid(self):
        """Test detailed mode with valid provenance."""
        data = {
            "provenance": {
                "source": "test",
                "timestamp": "2025-01-01T00:00:00Z",
            }
        }
        result = validate_provenance_response(data, detailed=True)

        assert result["_provenance_valid"] is True
        assert "_provenance_issues" not in result


class TestMarkInvalidProvenanceEnhanced:
    """Tests for enhanced mark_invalid_provenance function."""

    def test_mark_with_issues(self):
        """Test marking with validation issues."""
        data = {"claim_id": "c1"}
        issues = ["Missing source", "Invalid timestamp"]
        result = mark_invalid_provenance(data, issues=issues)

        assert result["_provenance_valid"] is False
        assert result["_provenance_issues"] == issues

    def test_mark_with_copy(self):
        """Test marking with copy mode."""
        original = {"claim_id": "c1"}
        result = mark_invalid_provenance(original, copy_data=True)

        assert result["_provenance_valid"] is False
        # Original should not be modified
        assert "_provenance_valid" not in original

    def test_mark_none_data(self):
        """Test marking None data."""
        result = mark_invalid_provenance(None)

        assert result["_provenance_valid"] is False
        assert "_provenance_warning" in result


class TestCreateProvenance:
    """Tests for create_provenance helper function."""

    def test_create_minimal_provenance(self):
        """Test creating provenance with minimal args."""
        from app.api.middleware.provenance import create_provenance

        result = create_provenance("test_source")

        assert result["source"] == "test_source"
        assert "timestamp" in result
        # Should be valid ISO 8601
        assert "T" in result["timestamp"]

    def test_create_provenance_with_timestamp(self):
        """Test creating provenance with custom timestamp."""
        from app.api.middleware.provenance import create_provenance

        result = create_provenance("test", timestamp="2025-01-01T00:00:00Z")

        assert result["timestamp"] == "2025-01-01T00:00:00Z"

    def test_create_provenance_with_all_fields(self):
        """Test creating provenance with all optional fields."""
        from app.api.middleware.provenance import create_provenance

        result = create_provenance(
            "test_source",
            timestamp="2025-01-01T00:00:00Z",
            policy_version="1.0",
            policy_name="test_policy",
            actor="test_actor",
            evidence_refs=["ref1", "ref2"],
            references={"key": "value"},
        )

        assert result["source"] == "test_source"
        assert result["timestamp"] == "2025-01-01T00:00:00Z"
        assert result["policy_version"] == "1.0"
        assert result["policy_name"] == "test_policy"
        assert result["actor"] == "test_actor"
        assert result["evidence_refs"] == ["ref1", "ref2"]
        assert result["references"] == {"key": "value"}

    def test_create_provenance_empty_source_raises(self):
        """Test that empty source raises ValueError."""
        from app.api.middleware.provenance import create_provenance

        with pytest.raises(ValueError, match="source is required"):
            create_provenance("")

        with pytest.raises(ValueError, match="source is required"):
            create_provenance(None)

    def test_create_provenance_defensive_copy(self):
        """Test that evidence_refs and references are copied."""
        from app.api.middleware.provenance import create_provenance

        refs = ["ref1", "ref2"]
        references = {"key": "value"}

        result = create_provenance(
            "test",
            evidence_refs=refs,
            references=references,
        )

        # Modify originals
        refs.append("ref3")
        references["new_key"] = "new_value"

        # Result should not be affected
        assert len(result["evidence_refs"]) == 2
        assert "new_key" not in result["references"]


class TestProvenanceStatsEnhanced:
    """Tests for enhanced provenance stats."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_provenance_stats()

    def test_stats_includes_rate(self):
        """Test that stats includes valid rate percent."""
        record_provenance_check(True)
        record_provenance_check(True)
        record_provenance_check(False)

        stats = get_provenance_stats()

        assert "valid_rate_percent" in stats
        # 2 valid out of 3 = 66.67%
        assert stats["valid_rate_percent"] == 66.67

    def test_stats_zero_rate_with_no_data(self):
        """Test stats rate is 0 with no data."""
        stats = get_provenance_stats()

        assert stats["valid_rate_percent"] == 0.0


class TestThreadSafetyProvenance:
    """Tests for thread safety in provenance stats."""

    def setup_method(self):
        """Reset stats before each test."""
        reset_provenance_stats()

    def test_concurrent_record_checks(self):
        """Test concurrent recording of checks."""
        import threading

        def record_many(valid: bool, count: int):
            for _ in range(count):
                record_provenance_check(valid)

        threads = [
            threading.Thread(target=record_many, args=(True, 1000)),
            threading.Thread(target=record_many, args=(False, 500)),
            threading.Thread(target=record_many, args=(True, 500)),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = get_provenance_stats()

        assert stats["total_checks"] == 2000
        assert stats["valid"] == 1500
        assert stats["invalid"] == 500

    def test_concurrent_read_write_stats(self):
        """Test concurrent reads and writes to stats."""
        import threading

        errors = []

        def writer():
            for _ in range(100):
                record_provenance_check(True)

        def reader():
            for _ in range(100):
                try:
                    stats = get_provenance_stats()
                    # Should not raise
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=reader),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


class TestProvenanceConstants:
    """Tests for provenance constants."""

    def test_required_paths_is_frozenset(self):
        """Test that required paths is immutable."""
        from app.api.middleware.provenance import PROVENANCE_REQUIRED_PATHS

        assert isinstance(PROVENANCE_REQUIRED_PATHS, frozenset)

    def test_patterns_is_tuple(self):
        """Test that patterns is immutable."""
        from app.api.middleware.provenance import PROVENANCE_PATTERNS

        assert isinstance(PROVENANCE_PATTERNS, tuple)

    def test_required_fields_is_frozenset(self):
        """Test that required fields is immutable."""
        from app.api.middleware.provenance import PROVENANCE_REQUIRED_FIELDS

        assert isinstance(PROVENANCE_REQUIRED_FIELDS, frozenset)
        assert "source" in PROVENANCE_REQUIRED_FIELDS
        assert "timestamp" in PROVENANCE_REQUIRED_FIELDS
