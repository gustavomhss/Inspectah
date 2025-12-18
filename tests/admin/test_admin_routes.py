"""
Tests for admin/routes — S37

Tests for admin routes helper functions.
"""

import pytest
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

from app.admin.routes import (
    list_sources,
    create_source,
    test_source as source_test_fn,  # Renamed to avoid pytest collection
    get_source_status,
    set_source_active,
    prepare_scenario,
    DEMO_CASES,
    DEMO_TIMELINES,
    DEMO_XRAYS,
)
from app.admin.schemas import (
    SourceResponse,
    SourceStatusResponse,
    SourceTestResult,
)


class TestListSources:
    """Tests for list_sources function."""

    def test_list_sources_returns_sources(self):
        """List sources returns sources list."""
        mock_source = SourceResponse(
            id="src_1",
            name="Test Source",
            type="api",
            info_type="news",
            url_base="https://api.test.com",
            selected_fields=["title", "body"],
            params={},
            is_active=True,
        )

        with patch("app.admin.routes.service") as mock_service:
            mock_service.list_sources.return_value = [mock_source]

            result = list_sources()

            assert "sources" in result
            assert len(result["sources"]) == 1
            assert result["sources"][0]["id"] == "src_1"

    def test_list_sources_empty(self):
        """List sources when no sources exist."""
        with patch("app.admin.routes.service") as mock_service:
            mock_service.list_sources.return_value = []

            result = list_sources()

            assert "sources" in result
            assert result["sources"] == []


class TestCreateSource:
    """Tests for create_source function."""

    def test_create_source_success(self):
        """Create source successfully."""

        @dataclass
        class MockConfig:
            url_base: str = "https://api.example.com"
            selected_fields: List[str] = field(default_factory=list)
            params: Dict[str, Any] = field(default_factory=dict)

        @dataclass
        class MockSource:
            id: str = "src_new"
            name: str = "New Source"
            type: str = "api"
            info_type: str = "news"
            config: MockConfig = field(default_factory=MockConfig)
            is_active: bool = True

        mock_source = MockSource()
        mock_status = SourceStatusResponse(
            source_id="src_new",
            last_fetch_at=None,
            last_fetch_status="ok",
            last_fetch_error=None,
            recent_items_count=0,
        )

        with patch("app.admin.routes.service") as mock_service:
            mock_service.create_or_update_source.return_value = mock_source
            mock_service.get_source_status.return_value = mock_status

            payload = {
                "id": "src_new",
                "name": "New Source",
                "type": "api",
                "info_type": "news",
                "url_base": "https://api.example.com",
                "selected_fields": ["title", "body"],
            }

            result = create_source(payload)

            assert "source" in result
            assert result["source"]["id"] == "src_new"
            assert "status" in result


class TestTestSource:
    """Tests for test_source function."""

    def test_test_source_returns_result(self):
        """Test source returns result."""
        mock_result = SourceTestResult(
            source_id="src_1",
            items_ingested=5,
            preview_items=[],
            status="ok",
        )

        with patch("app.admin.routes.service") as mock_service:
            mock_service.trigger_source_test.return_value = mock_result

            result = source_test_fn("src_1")

            assert result["source_id"] == "src_1"
            assert result["items_ingested"] == 5
            mock_service.trigger_source_test.assert_called_once_with("src_1")


class TestGetSourceStatus:
    """Tests for get_source_status function."""

    def test_get_source_status_found(self):
        """Get status for existing source."""
        mock_status = SourceStatusResponse(
            source_id="src_1",
            last_fetch_at=datetime.now(timezone.utc),
            last_fetch_status="success",
            last_fetch_error=None,
            recent_items_count=10,
        )

        with patch("app.admin.routes.service") as mock_service:
            mock_service.get_source_status.return_value = mock_status

            result = get_source_status("src_1")

            assert result["source_id"] == "src_1"
            assert result["last_fetch_status"] == "success"

    def test_get_source_status_not_found(self):
        """Get status for non-existent source."""
        with patch("app.admin.routes.service") as mock_service:
            mock_service.get_source_status.return_value = None

            result = get_source_status("missing_src")

            assert result["source_id"] == "missing_src"
            assert "error" in result


class TestSetSourceActive:
    """Tests for set_source_active function."""

    def test_set_source_active_true(self):
        """Set source as active."""
        mock_source = MagicMock()
        mock_source.is_active = True

        with patch("app.admin.routes.service") as mock_service:
            mock_service.set_source_active.return_value = mock_source

            result = set_source_active("src_1", True)

            assert result["source_id"] == "src_1"
            assert result["is_active"] is True

    def test_set_source_active_false(self):
        """Set source as inactive."""
        mock_source = MagicMock()
        mock_source.is_active = False

        with patch("app.admin.routes.service") as mock_service:
            mock_service.set_source_active.return_value = mock_source

            result = set_source_active("src_1", False)

            assert result["source_id"] == "src_1"

    def test_set_source_active_not_found(self):
        """Set active for non-existent source."""
        with patch("app.admin.routes.service") as mock_service:
            mock_service.set_source_active.return_value = None

            result = set_source_active("missing_src", True)

            assert result["source_id"] == "missing_src"
            assert "error" in result


class TestPrepareScenario:
    """Tests for prepare_scenario function."""

    def test_prepare_scenario_success(self):
        """Prepare scenario successfully."""
        with patch("app.admin.routes.service") as mock_service:
            mock_service.prepare_scenario_sources.return_value = ["src_1", "src_2"]

            result = prepare_scenario({"scenario_id": "test_scenario"})

            assert result["scenario_id"] == "test_scenario"
            assert result["sources_prepared"] == ["src_1", "src_2"]

    def test_prepare_scenario_no_scenario_id(self):
        """Prepare scenario without scenario_id returns error."""
        result = prepare_scenario({})

        assert "error" in result
        assert "scenario_id" in result["error"]

    def test_prepare_scenario_empty_scenario_id(self):
        """Prepare scenario with empty scenario_id returns error."""
        result = prepare_scenario({"scenario_id": ""})

        assert "error" in result


class TestDemoCases:
    """Tests for DEMO_CASES data structure."""

    def test_demo_cases_not_empty(self):
        """Demo cases has entries."""
        assert len(DEMO_CASES) >= 2

    def test_demo_cases_have_required_fields(self):
        """Demo cases have required fields."""
        for case_id, case in DEMO_CASES.items():
            assert case["id"] == case_id
            assert "title" in case
            assert "category" in case
            assert "status" in case


class TestDemoTimelines:
    """Tests for DEMO_TIMELINES data structure."""

    def test_demo_timelines_not_empty(self):
        """Demo timelines has entries."""
        assert len(DEMO_TIMELINES) >= 1

    def test_demo_timelines_have_events(self):
        """Demo timelines have events."""
        for case_id, timeline in DEMO_TIMELINES.items():
            assert timeline["case_id"] == case_id
            assert "events" in timeline
            assert len(timeline["events"]) >= 1


class TestDemoXrays:
    """Tests for DEMO_XRAYS data structure."""

    def test_demo_xrays_not_empty(self):
        """Demo xrays has entries."""
        assert len(DEMO_XRAYS) >= 1

    def test_demo_xrays_have_required_sections(self):
        """Demo xrays have required sections."""
        for case_id, xray in DEMO_XRAYS.items():
            assert xray["case_id"] == case_id
            assert "debunker" in xray
            assert "committees" in xray
            assert "anchors" in xray
            assert "evidences" in xray
