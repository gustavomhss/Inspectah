"""
Comprehensive tests for memory_routes.py (S38-BE-043).

Covers all endpoints and error paths to achieve 95%+ coverage.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.memory_routes import router
from app.context.memory_controller import (
    MemoryEntry,
    MemoryScope,
    MemoryType,
    RetentionPolicy,
    MemoryStats,
    MemoryContext,
)


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_memory_entry():
    """Sample memory entry for tests."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return MemoryEntry(
        entry_id="entry-1",
        scope=MemoryScope.SESSION,
        scope_id="session-123",
        memory_type=MemoryType.CONTEXT,
        key="test_key",
        value={"data": "test"},
        retention=RetentionPolicy.SHORT,
        created_at=now,
        expires_at=now,
        accessed_at=now,
        access_count=1,
        importance=0.5,
        tags=["test"],
        metadata={},
    )


class TestRememberEndpoint:
    """Tests for POST /api/v1/memory/remember endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_remember_basic(self, mock_get_controller, client, sample_memory_entry):
        """Remember stores a memory entry."""
        mock_controller = MagicMock()
        mock_controller.remember = MagicMock(return_value=sample_memory_entry)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/remember", json={
            "scope": "session",
            "scope_id": "session-123",
            "key": "test_key",
            "value": {"data": "test"},
            "memory_type": "context",
            "retention": "short",
            "importance": 0.5,
            "tags": ["test"],
        })
        assert response.status_code == 200

        data = response.json()
        assert data["entry_id"] == "entry-1"
        assert data["scope"] == "session"
        assert data["key"] == "test_key"

    @patch("app.api.memory_routes._get_controller")
    def test_remember_with_metadata(self, mock_get_controller, client, sample_memory_entry):
        """Remember with metadata."""
        mock_controller = MagicMock()
        mock_controller.remember = MagicMock(return_value=sample_memory_entry)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/remember", json={
            "scope": "agent",
            "scope_id": "agent-1",
            "key": "config",
            "value": {"setting": "value"},
            "metadata": {"source": "api"},
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_remember_invalid_scope(self, mock_get_controller, client):
        """Remember with invalid scope returns 400."""
        mock_controller = MagicMock()
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/remember", json={
            "scope": "invalid_scope",
            "scope_id": "test",
            "key": "key",
            "value": "value",
        })
        assert response.status_code == 400
        assert "Invalid scope" in response.json()["detail"]

    @patch("app.api.memory_routes._get_controller")
    def test_remember_invalid_memory_type(self, mock_get_controller, client):
        """Remember with invalid memory type returns 400."""
        mock_controller = MagicMock()
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/remember", json={
            "scope": "session",
            "scope_id": "test",
            "key": "key",
            "value": "value",
            "memory_type": "invalid_type",
        })
        assert response.status_code == 400
        assert "Invalid memory type" in response.json()["detail"]

    @patch("app.api.memory_routes._get_controller")
    def test_remember_invalid_retention(self, mock_get_controller, client):
        """Remember with invalid retention returns 400."""
        mock_controller = MagicMock()
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/remember", json={
            "scope": "session",
            "scope_id": "test",
            "key": "key",
            "value": "value",
            "retention": "invalid_retention",
        })
        assert response.status_code == 400
        assert "Invalid retention" in response.json()["detail"]

    @patch("app.api.memory_routes._get_controller")
    def test_remember_all_scopes(self, mock_get_controller, client, sample_memory_entry):
        """Remember works with all scope types."""
        mock_controller = MagicMock()
        mock_controller.remember = MagicMock(return_value=sample_memory_entry)
        mock_get_controller.return_value = mock_controller

        for scope in MemoryScope:
            response = client.post("/api/v1/memory/remember", json={
                "scope": scope.value,
                "scope_id": "test-id",
                "key": "key",
                "value": "value",
            })
            assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_remember_all_memory_types(self, mock_get_controller, client, sample_memory_entry):
        """Remember works with all memory types."""
        mock_controller = MagicMock()
        mock_controller.remember = MagicMock(return_value=sample_memory_entry)
        mock_get_controller.return_value = mock_controller

        for mem_type in MemoryType:
            response = client.post("/api/v1/memory/remember", json={
                "scope": "session",
                "scope_id": "test-id",
                "key": "key",
                "value": "value",
                "memory_type": mem_type.value,
            })
            assert response.status_code == 200


class TestRecallEndpoint:
    """Tests for POST /api/v1/memory/recall endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_recall_basic(self, mock_get_controller, client, sample_memory_entry):
        """Recall retrieves memories."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
        })
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["entry_id"] == "entry-1"

    @patch("app.api.memory_routes._get_controller")
    def test_recall_with_key(self, mock_get_controller, client, sample_memory_entry):
        """Recall with specific key."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
            "key": "test_key",
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_with_memory_type(self, mock_get_controller, client, sample_memory_entry):
        """Recall with memory type filter."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
            "memory_type": "context",
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_with_tags(self, mock_get_controller, client, sample_memory_entry):
        """Recall with tags filter."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
            "tags": ["test"],
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_with_min_importance(self, mock_get_controller, client, sample_memory_entry):
        """Recall with minimum importance."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
            "min_importance": 0.3,
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_with_limit(self, mock_get_controller, client, sample_memory_entry):
        """Recall with custom limit."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
            "limit": 50,
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_include_expired(self, mock_get_controller, client, sample_memory_entry):
        """Recall can include expired entries."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "session-123",
            "include_expired": True,
        })
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_empty_results(self, mock_get_controller, client):
        """Recall with no results returns empty list."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[])
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "nonexistent",
        })
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 0

    @patch("app.api.memory_routes._get_controller")
    def test_recall_invalid_memory_type(self, mock_get_controller, client):
        """Recall with invalid memory type returns 400."""
        mock_controller = MagicMock()
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/recall", json={
            "scope": "session",
            "scope_id": "test",
            "memory_type": "invalid_type",
        })
        assert response.status_code == 400


class TestRecallGetEndpoint:
    """Tests for GET /api/v1/memory/recall/{scope}/{scope_id} endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_recall_get_basic(self, mock_get_controller, client, sample_memory_entry):
        """Recall via GET works."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/recall/session/session-123")
        assert response.status_code == 200

        data = response.json()
        assert data["scope"] == "session"
        assert data["scope_id"] == "session-123"
        assert len(data["entries"]) == 1
        assert data["total"] == 1

    @patch("app.api.memory_routes._get_controller")
    def test_recall_get_with_key(self, mock_get_controller, client, sample_memory_entry):
        """Recall via GET with key parameter."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/recall/session/session-123?key=test_key")
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_get_with_memory_type(self, mock_get_controller, client, sample_memory_entry):
        """Recall via GET with memory_type parameter."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/recall/session/session-123?memory_type=context")
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_get_with_limit(self, mock_get_controller, client, sample_memory_entry):
        """Recall via GET with custom limit."""
        mock_controller = MagicMock()
        mock_controller.recall = MagicMock(return_value=[sample_memory_entry])
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/recall/session/session-123?limit=25")
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_recall_get_invalid_memory_type(self, mock_get_controller, client):
        """Recall via GET with invalid memory_type returns 400."""
        mock_controller = MagicMock()
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/recall/session/test?memory_type=invalid")
        assert response.status_code == 400


class TestForgetEndpoint:
    """Tests for POST /api/v1/memory/forget endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_forget_specific_key(self, mock_get_controller, client):
        """Forget with specific key."""
        mock_controller = MagicMock()
        mock_controller.forget = MagicMock(return_value=1)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/forget", json={
            "scope": "session",
            "scope_id": "session-123",
            "key": "test_key",
        })
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["forgotten_count"] == 1
        assert data["key"] == "test_key"

    @patch("app.api.memory_routes._get_controller")
    def test_forget_all_scope(self, mock_get_controller, client):
        """Forget without key removes all in scope."""
        mock_controller = MagicMock()
        mock_controller.forget = MagicMock(return_value=5)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/forget", json={
            "scope": "session",
            "scope_id": "session-123",
        })
        assert response.status_code == 200

        data = response.json()
        assert data["forgotten_count"] == 5
        assert data["key"] is None


class TestGetContextEndpoint:
    """Tests for GET /api/v1/memory/context/{scope}/{scope_id} endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_get_context_basic(self, mock_get_controller, client, sample_memory_entry):
        """Get context returns memory context."""
        mock_controller = MagicMock()
        mock_context = MemoryContext(
            context_id="ctx-1",
            scope=MemoryScope.SESSION,
            scope_id="session-123",
            entries={"test_key": sample_memory_entry},
        )
        mock_controller.build_context = MagicMock(return_value=mock_context)
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/context/session/session-123")
        assert response.status_code == 200

        data = response.json()
        assert data["context_id"] == "ctx-1"
        assert data["scope"] == "session"
        assert data["entry_count"] == 1

    @patch("app.api.memory_routes._get_controller")
    def test_get_context_with_include_types(self, mock_get_controller, client, sample_memory_entry):
        """Get context with specific memory types."""
        mock_controller = MagicMock()
        mock_context = MemoryContext(
            context_id="ctx-1",
            scope=MemoryScope.SESSION,
            scope_id="session-123",
            entries={},
        )
        mock_controller.build_context = MagicMock(return_value=mock_context)
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/context/session/session-123?include_types=context,fact")
        assert response.status_code == 200

    @patch("app.api.memory_routes._get_controller")
    def test_get_context_with_max_entries(self, mock_get_controller, client, sample_memory_entry):
        """Get context with max_entries limit."""
        mock_controller = MagicMock()
        mock_context = MemoryContext(
            context_id="ctx-1",
            scope=MemoryScope.SESSION,
            scope_id="session-123",
            entries={},
        )
        mock_controller.build_context = MagicMock(return_value=mock_context)
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/context/session/session-123?max_entries=25")
        assert response.status_code == 200


class TestSummarizeEndpoint:
    """Tests for POST /api/v1/memory/summarize/{scope}/{scope_id} endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_summarize(self, mock_get_controller, client, sample_memory_entry):
        """Summarize creates summary entry."""
        mock_controller = MagicMock()
        mock_controller.summarize = MagicMock(return_value=sample_memory_entry)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/summarize/session/session-123")
        assert response.status_code == 200

        data = response.json()
        assert data["entry_id"] == "entry-1"


class TestExportContextEndpoint:
    """Tests for GET /api/v1/memory/export/{scope}/{scope_id} endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_export_context(self, mock_get_controller, client):
        """Export context returns serialized data."""
        mock_controller = MagicMock()
        mock_controller.export_context = MagicMock(return_value={
            "version": "1.0",
            "scope": "session",
            "scope_id": "session-123",
            "entries": [],
        })
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/export/session/session-123")
        assert response.status_code == 200

        data = response.json()
        assert data["version"] == "1.0"
        assert data["scope"] == "session"


class TestImportContextEndpoint:
    """Tests for POST /api/v1/memory/import/{scope}/{scope_id} endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_import_context(self, mock_get_controller, client):
        """Import context restores from serialized data."""
        mock_controller = MagicMock()
        mock_controller.import_context = MagicMock(return_value=3)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/import/session/session-123", json={
            "version": "1.0",
            "entries": [],
        })
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["imported_count"] == 3


class TestCleanupExpiredEndpoint:
    """Tests for POST /api/v1/memory/cleanup endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_cleanup_expired(self, mock_get_controller, client):
        """Cleanup removes expired entries."""
        mock_controller = MagicMock()
        mock_controller.cleanup_expired = MagicMock(return_value=10)
        mock_get_controller.return_value = mock_controller

        response = client.post("/api/v1/memory/cleanup")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["cleaned_count"] == 10


class TestGetStatsEndpoint:
    """Tests for GET /api/v1/memory/stats endpoint."""

    @patch("app.api.memory_routes._get_controller")
    def test_get_stats(self, mock_get_controller, client):
        """Get stats returns memory statistics."""
        mock_controller = MagicMock()
        mock_stats = MemoryStats(
            total_entries=100,
            active_entries=80,
            expired_entries=20,
            by_scope={"session": 50, "agent": 30},
            by_type={"context": 60, "fact": 40},
            by_retention={"short": 70, "medium": 30},
            total_access_count=500,
            avg_importance=0.6,
        )
        mock_controller.get_stats = MagicMock(return_value=mock_stats)
        mock_get_controller.return_value = mock_controller

        response = client.get("/api/v1/memory/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["total_entries"] == 100
        assert data["active_entries"] == 80
        assert data["expired_entries"] == 20
        assert data["avg_importance"] == 0.6


class TestListScopesEndpoint:
    """Tests for GET /api/v1/memory/scopes endpoint."""

    def test_list_scopes(self, client):
        """List scopes returns all scopes, types, and policies."""
        response = client.get("/api/v1/memory/scopes")
        assert response.status_code == 200

        data = response.json()
        assert "scopes" in data
        assert "memory_types" in data
        assert "retention_policies" in data

        # Check counts
        assert len(data["scopes"]) == len(MemoryScope)
        assert len(data["memory_types"]) == len(MemoryType)
        assert len(data["retention_policies"]) == len(RetentionPolicy)

        # Check structure
        first_scope = data["scopes"][0]
        assert "scope" in first_scope
        assert "description" in first_scope


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_parse_scope_valid(self):
        """_parse_scope with valid scope."""
        from app.api.memory_routes import _parse_scope

        for scope in MemoryScope:
            result = _parse_scope(scope.value)
            assert result == scope

    def test_parse_scope_invalid(self):
        """_parse_scope with invalid scope raises HTTPException."""
        from app.api.memory_routes import _parse_scope
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _parse_scope("invalid_scope")

        assert exc_info.value.status_code == 400
        assert "Invalid scope" in exc_info.value.detail

    def test_parse_memory_type_valid(self):
        """_parse_memory_type with valid type."""
        from app.api.memory_routes import _parse_memory_type

        for mem_type in MemoryType:
            result = _parse_memory_type(mem_type.value)
            assert result == mem_type

    def test_parse_memory_type_invalid(self):
        """_parse_memory_type with invalid type raises HTTPException."""
        from app.api.memory_routes import _parse_memory_type
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _parse_memory_type("invalid_type")

        assert exc_info.value.status_code == 400
        assert "Invalid memory type" in exc_info.value.detail

    def test_parse_retention_valid(self):
        """_parse_retention with valid retention."""
        from app.api.memory_routes import _parse_retention

        for retention in RetentionPolicy:
            result = _parse_retention(retention.value)
            assert result == retention

    def test_parse_retention_invalid(self):
        """_parse_retention with invalid retention raises HTTPException."""
        from app.api.memory_routes import _parse_retention
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _parse_retention("invalid_retention")

        assert exc_info.value.status_code == 400
        assert "Invalid retention" in exc_info.value.detail

    def test_to_response(self, sample_memory_entry):
        """_to_response converts MemoryEntry to response."""
        from app.api.memory_routes import _to_response

        response = _to_response(sample_memory_entry)

        assert response.entry_id == "entry-1"
        assert response.scope == "session"
        assert response.key == "test_key"
        assert response.memory_type == "context"

    def test_get_scope_description(self):
        """_get_scope_description returns descriptions."""
        from app.api.memory_routes import _get_scope_description

        for scope in MemoryScope:
            desc = _get_scope_description(scope)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_get_type_description(self):
        """_get_type_description returns descriptions."""
        from app.api.memory_routes import _get_type_description

        for mem_type in MemoryType:
            desc = _get_type_description(mem_type)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_get_retention_description(self):
        """_get_retention_description returns descriptions."""
        from app.api.memory_routes import _get_retention_description

        for retention in RetentionPolicy:
            desc = _get_retention_description(retention)
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestControllerInitialization:
    """Tests for controller initialization."""

    def test_get_controller_creates_instance(self):
        """_get_controller creates instance on first call."""
        from app.api import memory_routes

        # Reset global instance
        memory_routes._controller = None

        controller = memory_routes._get_controller()
        assert controller is not None

    def test_get_controller_reuses_instance(self):
        """_get_controller reuses instance on subsequent calls."""
        from app.api import memory_routes

        c1 = memory_routes._get_controller()
        c2 = memory_routes._get_controller()

        assert c1 is c2
