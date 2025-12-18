"""
Tests for Explorer Routes — S37

Tests for explorer v0 routes.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from tempfile import TemporaryDirectory

from fastapi import HTTPException

from app.explorer import routes


class TestLoadCases:
    """Tests for _load_cases function."""

    def test_load_cases_no_file(self):
        """Returns empty list when file doesn't exist."""
        with patch.object(routes, "CASES_SNAPSHOT_PATH", Path("/nonexistent/path.json")):
            result = routes._load_cases()

        assert result == []

    def test_load_cases_from_file(self, tmp_path):
        """Loads cases from file."""
        cases_file = tmp_path / "cases.json"
        cases = [{"id_caso": "c1", "titulo": "Test Case"}]
        cases_file.write_text(json.dumps(cases), encoding="utf-8")

        with patch.object(routes, "CASES_SNAPSHOT_PATH", cases_file):
            result = routes._load_cases()

        assert len(result) == 1
        assert result[0]["id_caso"] == "c1"


class TestLoadTimelines:
    """Tests for _load_timelines function."""

    def test_load_timelines_no_file(self):
        """Returns empty dict when file doesn't exist."""
        with patch.object(routes, "TIMELINE_SNAPSHOT_PATH", Path("/nonexistent/path.json")):
            result = routes._load_timelines()

        assert result == {}

    def test_load_timelines_from_file(self, tmp_path):
        """Loads timelines from file."""
        timeline_file = tmp_path / "timelines.json"
        timelines = {
            "c1": [{"id_evento": "e1", "descricao": "Event 1"}],
        }
        timeline_file.write_text(json.dumps(timelines), encoding="utf-8")

        with patch.object(routes, "TIMELINE_SNAPSHOT_PATH", timeline_file):
            result = routes._load_timelines()

        assert "c1" in result
        assert len(result["c1"]) == 1


class TestLookupCase:
    """Tests for _lookup_case function."""

    def test_lookup_case_found(self):
        """Returns case when found."""
        cases = [
            {"id_caso": "c1", "titulo": "Case 1"},
            {"id_caso": "c2", "titulo": "Case 2"},
        ]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes._lookup_case("c2")

        assert result["titulo"] == "Case 2"

    def test_lookup_case_not_found(self):
        """Returns None when not found."""
        cases = [{"id_caso": "c1", "titulo": "Case 1"}]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes._lookup_case("c99")

        assert result is None


class TestFindEvent:
    """Tests for _find_event function."""

    def test_find_event_found(self):
        """Returns event when found."""
        timelines = {
            "c1": [
                {"id_evento": "e1", "descricao": "Event 1"},
                {"id_evento": "e2", "descricao": "Event 2"},
            ],
        }

        with patch.object(routes, "_load_timelines", return_value=timelines):
            result = routes._find_event("e2")

        assert result["descricao"] == "Event 2"
        assert result["case_id"] == "c1"

    def test_find_event_not_found(self):
        """Returns None when not found."""
        timelines = {"c1": [{"id_evento": "e1"}]}

        with patch.object(routes, "_load_timelines", return_value=timelines):
            result = routes._find_event("e99")

        assert result is None

    def test_find_event_adds_case_id(self):
        """Adds case_id to found event."""
        timelines = {"case_abc": [{"id_evento": "e1"}]}

        with patch.object(routes, "_load_timelines", return_value=timelines):
            result = routes._find_event("e1")

        assert result["case_id"] == "case_abc"


class TestFilterCases:
    """Tests for _filter_cases function."""

    def test_filter_cases_no_query(self):
        """Returns all cases when no query."""
        cases = [{"id_caso": "c1"}, {"id_caso": "c2"}]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes._filter_cases("")

        assert len(result) == 2

    def test_filter_cases_by_id(self):
        """Filters by case id."""
        cases = [
            {"id_caso": "abc123", "titulo": "", "descricao": "", "dominio": ""},
            {"id_caso": "xyz789", "titulo": "", "descricao": "", "dominio": ""},
        ]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes._filter_cases("abc")

        assert len(result) == 1
        assert result[0]["id_caso"] == "abc123"

    def test_filter_cases_by_titulo(self):
        """Filters by titulo."""
        cases = [
            {"id_caso": "c1", "titulo": "Test Title", "descricao": "", "dominio": ""},
            {"id_caso": "c2", "titulo": "Other", "descricao": "", "dominio": ""},
        ]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes._filter_cases("title")

        assert len(result) == 1
        assert result[0]["id_caso"] == "c1"

    def test_filter_cases_case_insensitive(self):
        """Filter is case insensitive."""
        cases = [{"id_caso": "c1", "titulo": "UPPER", "descricao": "", "dominio": ""}]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes._filter_cases("upper")

        assert len(result) == 1


class TestListCases:
    """Tests for list_cases function."""

    def test_list_cases_basic(self):
        """List cases returns filtered results."""
        cases = [
            {"id_caso": "c1", "titulo": "Case 1", "descricao": "", "dominio": "", "updated_at": "2024-01-02"},
            {"id_caso": "c2", "titulo": "Case 2", "descricao": "", "dominio": "", "updated_at": "2024-01-01"},
        ]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes.list_cases()

        assert result["total"] == 2
        assert len(result["results"]) == 2
        # Sorted by updated_at descending
        assert result["results"][0]["id_caso"] == "c1"

    def test_list_cases_with_query(self):
        """List cases with query filter."""
        cases = [
            {"id_caso": "c1", "titulo": "Politics", "descricao": "", "dominio": "", "updated_at": "2024-01-01"},
            {"id_caso": "c2", "titulo": "Health", "descricao": "", "dominio": "", "updated_at": "2024-01-01"},
        ]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes.list_cases(query="politics")

        assert result["total"] == 1
        assert result["query"] == "politics"

    def test_list_cases_with_limit(self):
        """List cases respects limit."""
        cases = [
            {"id_caso": f"c{i}", "titulo": "", "descricao": "", "dominio": "", "updated_at": ""}
            for i in range(100)
        ]

        with patch.object(routes, "_load_cases", return_value=cases):
            result = routes.list_cases(limit=10)

        assert result["total"] == 100
        assert len(result["results"]) == 10


class TestGetCase:
    """Tests for get_case function."""

    def test_get_case_success(self):
        """Get case returns case with timeline."""
        case = {"id_caso": "c1", "titulo": "Test"}
        timelines = {
            "c1": [
                {"id_evento": "e1", "status_debunker": "verdadeiro"},
                {"id_evento": "e2", "status_debunker": "falso"},
            ],
        }

        with patch.object(routes, "_lookup_case", return_value=case):
            with patch.object(routes, "_load_timelines", return_value=timelines):
                result = routes.get_case("c1")

        assert result["case"] == case
        assert len(result["timeline"]) == 2
        assert result["stats"]["events"] == 2
        assert result["stats"]["by_status"]["verdadeiro"] == 1
        assert result["stats"]["by_status"]["falso"] == 1

    def test_get_case_not_found(self):
        """Get case raises when not found."""
        with patch.object(routes, "_lookup_case", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                routes.get_case("c99")
            assert exc_info.value.status_code == 404
            assert "não encontrado" in exc_info.value.detail

    def test_get_case_no_timeline(self):
        """Get case handles missing timeline."""
        case = {"id_caso": "c1"}
        timelines = {}

        with patch.object(routes, "_lookup_case", return_value=case):
            with patch.object(routes, "_load_timelines", return_value=timelines):
                result = routes.get_case("c1")

        assert result["timeline"] == []
        assert result["stats"]["events"] == 0


class TestCreateCaseFeedback:
    """Tests for create_case_feedback function."""

    def test_create_case_feedback_success(self):
        """Create feedback for case."""
        case = {"id_caso": "c1"}
        mock_feedback = MagicMock()
        mock_feedback.to_dict.return_value = {"id": "fb1", "mensagem": "Test"}

        with patch.object(routes, "_lookup_case", return_value=case):
            with patch.object(routes.DEFAULT_FEEDBACK_SERVICE, "create_feedback_for_case", return_value=mock_feedback):
                result = routes.create_case_feedback("c1", {"mensagem": "Test"})

        assert result["status"] == "registrado"
        assert result["feedback"]["id"] == "fb1"

    def test_create_case_feedback_missing_message(self):
        """Create feedback fails without message."""
        with pytest.raises(HTTPException) as exc_info:
            routes.create_case_feedback("c1", {})
        assert exc_info.value.status_code == 400
        assert "obrigatória" in exc_info.value.detail

    def test_create_case_feedback_case_not_found(self):
        """Create feedback fails when case not found."""
        with patch.object(routes, "_lookup_case", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                routes.create_case_feedback("c99", {"mensagem": "Test"})
            assert exc_info.value.status_code == 404


class TestCreateEventFeedback:
    """Tests for create_event_feedback function."""

    def test_create_event_feedback_success(self):
        """Create feedback for event."""
        event = {"id_evento": "e1", "case_id": "c1"}
        mock_feedback = MagicMock()
        mock_feedback.to_dict.return_value = {"id": "fb1"}

        with patch.object(routes, "_find_event", return_value=event):
            with patch.object(routes.DEFAULT_FEEDBACK_SERVICE, "create_feedback_for_event", return_value=mock_feedback):
                result = routes.create_event_feedback("e1", {"mensagem": "Test"})

        assert result["status"] == "registrado"

    def test_create_event_feedback_missing_message(self):
        """Create feedback fails without message."""
        with pytest.raises(HTTPException) as exc_info:
            routes.create_event_feedback("e1", {})
        assert exc_info.value.status_code == 400
        assert "obrigatória" in exc_info.value.detail

    def test_create_event_feedback_event_not_found(self):
        """Create feedback fails when event not found."""
        with patch.object(routes, "_find_event", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                routes.create_event_feedback("e99", {"mensagem": "Test"})
            assert exc_info.value.status_code == 404


class TestRaiseHelpers:
    """Tests for _raise_not_found and _raise_bad_request."""

    def test_raise_not_found_with_fastapi(self):
        """Raises HTTPException 404 with FastAPI."""
        with pytest.raises(HTTPException) as exc_info:
            routes._raise_not_found("test message")
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "test message"

    def test_raise_bad_request_with_fastapi(self):
        """Raises HTTPException 400 with FastAPI."""
        with pytest.raises(HTTPException) as exc_info:
            routes._raise_bad_request("test message")
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "test message"
