"""
Tests for app/api/sources_routes.py

Comprehensive tests for sources API routes.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.sources_routes import router, _sources_store, _runs_store
from app.ingestion.health_monitor import HealthStatus


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_stores():
    """Clear in-memory stores before each test."""
    _sources_store.clear()
    _runs_store.clear()
    yield
    _sources_store.clear()
    _runs_store.clear()


class TestListSources:
    """Tests for GET / endpoint."""

    def test_list_sources_empty(self):
        """List sources when none exist."""
        client = _client()
        response = client.get("/api/v1/sources")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_sources_all(self):
        """List all sources."""
        # Add some sources
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Source 1",
            "slug": "source-1",
            "source_type": "official",
            "url": "https://example.com",
            "description": "Test source",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "HEALTHY",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.get("/api/v1/sources")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "src_1"

    def test_list_sources_filter_by_type(self):
        """List sources filtered by type."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Official",
            "slug": "official",
            "source_type": "official",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }
        _sources_store["src_2"] = {
            "id": "src_2",
            "name": "Scraper",
            "slug": "scraper",
            "source_type": "scraper",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.get("/api/v1/sources?source_type=official")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["source_type"] == "official"

    def test_list_sources_filter_by_state(self):
        """List sources filtered by state."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Active",
            "slug": "active",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.get("/api/v1/sources?state=ACTIVE")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_sources_filter_by_enabled(self):
        """List sources filtered by enabled status."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Enabled",
            "slug": "enabled",
            "source_type": "api",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }
        _sources_store["src_2"] = {
            "id": "src_2",
            "name": "Disabled",
            "slug": "disabled",
            "source_type": "api",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": False,
            "state": "DISABLED_TEMP",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.get("/api/v1/sources?enabled=true")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["enabled"] is True

    def test_list_sources_search_by_name(self):
        """List sources with text search."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test Source",
            "slug": "test-source",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.get("/api/v1/sources?q=test")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1


class TestCreateSource:
    """Tests for POST / endpoint."""

    def test_create_source_success(self):
        """Create source successfully."""
        with patch("app.api.sources_routes.get_rate_limiter") as mock_rl:
            with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
                mock_rl.return_value = MagicMock()
                mock_hm.return_value = MagicMock()

                client = _client()
                response = client.post(
                    "/api/v1/sources",
                    json={
                        "name": "New Source",
                        "slug": "new-source",
                        "source_type": "official",
                        "url": "https://example.com",
                        "description": "Test source",
                        "config": {},
                        "rate_limit_rpm": 10,
                        "enabled": True,
                    },
                )

                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "New Source"
                assert data["state"] == "PROPOSED"
                assert "id" in data

    def test_create_source_duplicate_slug(self):
        """Create source with duplicate slug."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "slug": "existing",
            "name": "Existing",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.post(
            "/api/v1/sources",
            json={
                "name": "Duplicate",
                "slug": "existing",
                "source_type": "rss",
                "url": "https://example.com",
            },
        )

        assert response.status_code == 409


class TestGetSource:
    """Tests for GET /{source_id} endpoint."""

    def test_get_source_success(self):
        """Get source successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
            with patch("app.api.sources_routes.get_rate_limiter") as mock_rl:
                with patch("app.api.sources_routes.get_circuit_breaker") as mock_cb:
                    mock_hm.return_value.get_stats.return_value = {}
                    mock_rl.return_value.get_stats.return_value = {}
                    mock_cb.return_value.get_stats.return_value = {}

                    client = _client()
                    response = client.get("/api/v1/sources/src_1")

                    assert response.status_code == 200
                    data = response.json()
                    assert data["id"] == "src_1"
                    assert "health_stats" in data
                    assert "rate_limit_stats" in data

    def test_get_source_not_found(self):
        """Get source that doesn't exist."""
        client = _client()
        response = client.get("/api/v1/sources/nonexistent")

        assert response.status_code == 404


class TestUpdateSource:
    """Tests for PUT /{source_id} endpoint."""

    def test_update_source_success(self):
        """Update source successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Original",
            "slug": "original",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_rate_limiter") as mock_rl:
            mock_rl.return_value = MagicMock()

            client = _client()
            response = client.put(
                "/api/v1/sources/src_1",
                json={"name": "Updated", "rate_limit_rpm": 20},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == "Updated"
            assert data["rate_limit_rpm"] == 20

    def test_update_source_not_found(self):
        """Update source that doesn't exist."""
        client = _client()
        response = client.put(
            "/api/v1/sources/nonexistent",
            json={"name": "Updated"},
        )

        assert response.status_code == 404


class TestDeleteSource:
    """Tests for DELETE /{source_id} endpoint."""

    def test_delete_source_success(self):
        """Delete source successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.delete("/api/v1/sources/src_1")

        assert response.status_code == 204
        assert "src_1" not in _sources_store

    def test_delete_source_with_runs(self):
        """Delete source that has ingestion runs."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }
        _runs_store["src_1"] = [{"run_id": "run_1"}]

        client = _client()
        response = client.delete("/api/v1/sources/src_1")

        assert response.status_code == 204
        assert "src_1" not in _sources_store
        assert "src_1" not in _runs_store

    def test_delete_source_not_found(self):
        """Delete source that doesn't exist."""
        client = _client()
        response = client.delete("/api/v1/sources/nonexistent")

        assert response.status_code == 404


class TestChangeSourceStatus:
    """Tests for POST /{source_id}/status endpoint."""

    def test_change_status_success(self):
        """Change source status successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "PROPOSED",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.post("/api/v1/sources/src_1/status?target_state=ACTIVE")

        assert response.status_code == 200
        data = response.json()
        assert data["state"] == "ACTIVE"

    def test_change_status_invalid_state(self):
        """Change source status to invalid state."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.post("/api/v1/sources/src_1/status?target_state=INVALID")

        assert response.status_code == 400

    def test_change_status_not_found(self):
        """Change status of non-existent source."""
        client = _client()
        response = client.post("/api/v1/sources/nonexistent/status?target_state=ACTIVE")

        assert response.status_code == 404


class TestDryRunSource:
    """Tests for POST /{source_id}/dry-run endpoint."""

    @pytest.mark.asyncio
    async def test_dry_run_official_source_success(self):
        """Dry run official source successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Official",
            "slug": "official",
            "source_type": "official",
            "url": "https://dados.gov.br",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "PROPOSED",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        mock_dataset = MagicMock()
        mock_dataset.title = "Test Dataset"
        mock_dataset.url = "https://example.com/dataset"

        with patch("app.ingestion.providers.gov_br.GovBrClient") as mock_client:
            mock_instance = AsyncMock()
            mock_instance.search_datasets = AsyncMock(return_value=[mock_dataset])
            mock_client.return_value = mock_instance

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/dry-run",
                json={"limit": 5},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["documents_found"] == 1

    @pytest.mark.asyncio
    async def test_dry_run_scraper_source(self):
        """Dry run scraper source."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Scraper",
            "slug": "scraper",
            "source_type": "scraper",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "PROPOSED",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.post(
            "/api/v1/sources/src_1/dry-run",
            json={"limit": 5},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dry_run_generic_source_success(self):
        """Dry run generic source successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "RSS",
            "slug": "rss",
            "source_type": "rss",
            "url": "https://example.com/feed",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "PROPOSED",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Sample content"

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/dry-run",
                json={"limit": 5},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_dry_run_generic_source_error(self):
        """Dry run generic source with HTTP error."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "RSS",
            "slug": "rss",
            "source_type": "rss",
            "url": "https://example.com/feed",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "PROPOSED",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/dry-run",
                json={"limit": 5},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["error_message"] is not None

    @pytest.mark.asyncio
    async def test_dry_run_exception(self):
        """Dry run with exception."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "RSS",
            "slug": "rss",
            "source_type": "rss",
            "url": "https://example.com/feed",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "PROPOSED",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.get = AsyncMock(side_effect=Exception("Connection error"))
            mock_client.return_value = mock_instance

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/dry-run",
                json={"limit": 5},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False

    def test_dry_run_not_found(self):
        """Dry run non-existent source."""
        client = _client()
        response = client.post(
            "/api/v1/sources/nonexistent/dry-run",
            json={"limit": 5},
        )

        assert response.status_code == 404


class TestTriggerIngestion:
    """Tests for POST /{source_id}/trigger endpoint."""

    def test_trigger_ingestion_success(self):
        """Trigger ingestion successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_circuit_breaker") as mock_cb:
            mock_cb.return_value.is_available.return_value = True

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/trigger",
                json={"force": False},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "PENDING"
            assert "run_id" in data

    def test_trigger_ingestion_not_found(self):
        """Trigger ingestion for non-existent source."""
        client = _client()
        response = client.post(
            "/api/v1/sources/nonexistent/trigger",
            json={"force": False},
        )

        assert response.status_code == 404

    def test_trigger_ingestion_source_disabled(self):
        """Trigger ingestion for disabled source."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": False,
            "state": "DISABLED_TEMP",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        client = _client()
        response = client.post(
            "/api/v1/sources/src_1/trigger",
            json={"force": False},
        )

        assert response.status_code == 400

    def test_trigger_ingestion_circuit_open(self):
        """Trigger ingestion when circuit breaker is open."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_circuit_breaker") as mock_cb:
            mock_cb.return_value.is_available.return_value = False

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/trigger",
                json={"force": False},
            )

            assert response.status_code == 503

    def test_trigger_ingestion_circuit_open_with_force(self):
        """Trigger ingestion with force when circuit is open."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_circuit_breaker") as mock_cb:
            mock_cb.return_value.is_available.return_value = False

            client = _client()
            response = client.post(
                "/api/v1/sources/src_1/trigger",
                json={"force": True},
            )

            assert response.status_code == 200


class TestGetSourceMetrics:
    """Tests for GET /{source_id}/metrics endpoint."""

    def test_get_metrics_success(self):
        """Get source metrics successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        now = datetime.now(timezone.utc)
        _runs_store["src_1"] = [
            {
                "run_id": "run_1",
                "status": "COMPLETED",
                "started_at": now - timedelta(hours=1),
                "finished_at": now,
                "documents_processed": 100,
            },
        ]

        with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
            mock_hm.return_value.get_stats.return_value = {"avg_latency_ms": 50}

            client = _client()
            response = client.get("/api/v1/sources/src_1/metrics?period=24h")

            assert response.status_code == 200
            data = response.json()
            assert data["source_id"] == "src_1"
            assert data["period"] == "24h"
            assert data["total_documents"] == 100

    def test_get_metrics_not_found(self):
        """Get metrics for non-existent source."""
        client = _client()
        response = client.get("/api/v1/sources/nonexistent/metrics")

        assert response.status_code == 404

    def test_get_metrics_different_periods(self):
        """Get metrics for different periods."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
            mock_hm.return_value.get_stats.return_value = {}

            client = _client()

            for period in ["1h", "24h", "7d"]:
                response = client.get(f"/api/v1/sources/src_1/metrics?period={period}")
                assert response.status_code == 200
                assert response.json()["period"] == period


class TestGetIngestionHistory:
    """Tests for GET /{source_id}/history endpoint."""

    def test_get_history_success(self):
        """Get ingestion history successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        now = datetime.now(timezone.utc)
        _runs_store["src_1"] = [
            {
                "run_id": "run_1",
                "status": "COMPLETED",
                "trigger": "MANUAL",
                "started_at": now - timedelta(hours=1),
                "finished_at": now,
                "documents_processed": 100,
                "error_message": None,
            },
        ]

        client = _client()
        response = client.get("/api/v1/sources/src_1/history")

        assert response.status_code == 200
        data = response.json()
        assert data["source_id"] == "src_1"
        assert len(data["runs"]) == 1
        assert data["runs"][0]["run_id"] == "run_1"

    def test_get_history_not_found(self):
        """Get history for non-existent source."""
        client = _client()
        response = client.get("/api/v1/sources/nonexistent/history")

        assert response.status_code == 404

    def test_get_history_with_pagination(self):
        """Get history with pagination."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        now = datetime.now(timezone.utc)
        _runs_store["src_1"] = [
            {
                "run_id": f"run_{i}",
                "status": "COMPLETED",
                "trigger": "MANUAL",
                "started_at": now - timedelta(hours=i),
                "finished_at": now,
                "documents_processed": 10,
                "error_message": None,
            }
            for i in range(30)
        ]

        client = _client()
        response = client.get("/api/v1/sources/src_1/history?limit=10&offset=5")

        assert response.status_code == 200
        data = response.json()
        assert len(data["runs"]) == 10
        assert data["pagination"]["limit"] == 10
        assert data["pagination"]["offset"] == 5


class TestGetSourceHealth:
    """Tests for GET /{source_id}/health endpoint."""

    def test_get_health_with_stats(self):
        """Get source health with stats."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "HEALTHY",
            "last_health_check": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
            mock_hm.return_value.get_stats.return_value = {
                "status": "HEALTHY",
                "avg_latency_ms": 50,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "consecutive_successes": 10,
                "consecutive_failures": 0,
                "uptime_percent": 99.5,
            }

            client = _client()
            response = client.get("/api/v1/sources/src_1/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "HEALTHY"
            assert data["uptime_percent"] == 99.5

    def test_get_health_no_stats(self):
        """Get source health when no stats available."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
            mock_hm.return_value.get_stats.return_value = None

            client = _client()
            response = client.get("/api/v1/sources/src_1/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "UNKNOWN"


class TestTriggerHealthCheck:
    """Tests for POST /{source_id}/health endpoint."""

    def test_trigger_health_check_success(self):
        """Trigger health check successfully."""
        _sources_store["src_1"] = {
            "id": "src_1",
            "name": "Test",
            "slug": "test",
            "source_type": "rss",
            "url": "https://example.com",
            "config": {},
            "rate_limit_rpm": 10,
            "enabled": True,
            "state": "ACTIVE",
            "last_health_status": "UNKNOWN",
            "last_health_check": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "created_by": "admin",
        }

        with patch("app.api.sources_routes.get_health_monitor") as mock_hm:
            mock_hm.return_value.check_source.return_value = HealthStatus.HEALTHY
            mock_hm.return_value.get_stats.return_value = {
                "status": "HEALTHY",
                "avg_latency_ms": 50,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "consecutive_successes": 1,
                "consecutive_failures": 0,
                "uptime_percent": 100.0,
            }

            client = _client()
            response = client.post("/api/v1/sources/src_1/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "HEALTHY"
            assert _sources_store["src_1"]["last_health_status"] == "HEALTHY"

    def test_trigger_health_check_not_found(self):
        """Trigger health check for non-existent source."""
        client = _client()
        response = client.post("/api/v1/sources/nonexistent/health")

        assert response.status_code == 404
