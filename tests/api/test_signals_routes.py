"""
Comprehensive tests for signals_routes.py (S38-BE-033).

Covers all endpoints and error paths to achieve 95%+ coverage.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.signals_routes import router
from app.signals import (
    SignalType,
    SignalScope,
    SignalValue,
    SignalBatch,
    SignalAlert,
    SignalConfig,
    SignalPriority,
)


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def mock_signal_value():
    """Create a mock signal value."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return SignalValue(
        signal_type=SignalType.VIRALIDADE,
        scope=SignalScope.GLOBAL,
        scope_id=None,
        value=0.75,
        confidence=0.9,
        sample_size=100,
        calculated_at=now,
        expires_at=now,
        metadata={"test": "data"},
    )


@pytest.fixture
def mock_signal_batch(mock_signal_value):
    """Create a mock signal batch."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    return SignalBatch(
        batch_id="batch-123",
        signals=[mock_signal_value],
        calculated_at=now,
        calculation_time_ms=50.0,
    )


class TestGetSignalsEndpoint:
    """Tests for GET /api/v1/signals endpoint."""

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_default_all_types(self, mock_get_services, client, mock_signal_batch):
        """GET signals without types returns all signal types."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={"hits": 10, "misses": 5})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals")
        assert response.status_code == 200

        data = response.json()
        assert data["batch_id"] == "batch-123"
        assert len(data["signals"]) == 1
        assert data["signals"][0]["signal_type"] == "viralidade"
        assert data["cache_stats"] is not None

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_specific_types(self, mock_get_services, client, mock_signal_batch):
        """GET signals with specific types filters correctly."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals?signal_types=viralidade,credibilidade_fonte")
        assert response.status_code == 200

        data = response.json()
        assert "batch_id" in data

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_invalid_type(self, mock_get_services, client):
        """GET signals with invalid type returns 400."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals?signal_types=invalid_type")
        assert response.status_code == 400
        assert "Invalid signal type" in response.json()["detail"]

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_invalid_scope(self, mock_get_services, client):
        """GET signals with invalid scope returns 400."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals?scope=invalid_scope")
        assert response.status_code == 400
        assert "Invalid scope" in response.json()["detail"]

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_with_scope_id(self, mock_get_services, client, mock_signal_batch):
        """GET signals with scope_id works."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals?scope=topic&scope_id=topic-123")
        assert response.status_code == 200

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_force_refresh(self, mock_get_services, client, mock_signal_batch):
        """GET signals with force_refresh works."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals?force_refresh=true")
        assert response.status_code == 200

    @patch("app.api.signals_routes._get_services")
    async def test_get_signals_with_alerts(self, mock_get_services, client, mock_signal_batch):
        """GET signals returns alerts when present."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        mock_alert = SignalAlert(
            alert_id="alert-1",
            signal_type=SignalType.VIRALIDADE,
            scope=SignalScope.GLOBAL,
            scope_id=None,
            level="high",
            value=0.95,
            threshold=0.9,
            message="High viralidade detected",
            created_at=now,
        )

        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[mock_alert])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals")
        assert response.status_code == 200

        data = response.json()
        assert len(data["alerts"]) == 1
        assert data["alerts"][0]["id"] == "alert-1"
        assert data["alerts"][0]["level"] == "high"


class TestQuerySignalsEndpoint:
    """Tests for POST /api/v1/signals endpoint."""

    @patch("app.api.signals_routes._get_services")
    async def test_post_signals_empty_types(self, mock_get_services, client, mock_signal_batch):
        """POST signals with empty types returns all."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals", json={
            "signal_types": [],
            "scope": "global",
        })
        assert response.status_code == 200

    @patch("app.api.signals_routes._get_services")
    async def test_post_signals_with_metadata(self, mock_get_services, client, mock_signal_batch):
        """POST signals with include_metadata includes cache stats and metadata."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={"hits": 5, "misses": 2})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals", json={
            "signal_types": ["viralidade"],
            "scope": "global",
            "include_metadata": True,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["cache_stats"] is not None
        assert data["signals"][0]["metadata"] is not None

    @patch("app.api.signals_routes._get_services")
    async def test_post_signals_without_metadata(self, mock_get_services, client, mock_signal_batch):
        """POST signals without include_metadata excludes cache stats."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals", json={
            "signal_types": ["viralidade"],
            "scope": "global",
            "include_metadata": False,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["cache_stats"] is None
        assert data["signals"][0]["metadata"] is None

    @patch("app.api.signals_routes._get_services")
    async def test_post_signals_invalid_type(self, mock_get_services, client):
        """POST signals with invalid type returns 400."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals", json={
            "signal_types": ["invalid_type"],
            "scope": "global",
        })
        assert response.status_code == 400
        assert "Invalid signal type" in response.json()["detail"]

    @patch("app.api.signals_routes._get_services")
    async def test_post_signals_invalid_scope(self, mock_get_services, client):
        """POST signals with invalid scope returns 400."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals", json={
            "signal_types": [],
            "scope": "invalid_scope",
        })
        assert response.status_code == 400
        assert "Invalid scope" in response.json()["detail"]

    @patch("app.api.signals_routes._get_services")
    async def test_post_signals_with_scope_ids(self, mock_get_services, client, mock_signal_batch):
        """POST signals with scope_ids works."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_signals = AsyncMock(return_value=mock_signal_batch)
        mock_signal_service.check_alerts = MagicMock(return_value=[])
        mock_signal_service.configs = {SignalType.VIRALIDADE: SignalConfig.default_configs()[SignalType.VIRALIDADE]}

        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={})

        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals", json={
            "signal_types": [],
            "scope": "topic",
            "scope_ids": ["topic-1", "topic-2"],
        })
        assert response.status_code == 200


class TestDashboardEndpoint:
    """Tests for GET /api/v1/signals/dashboard endpoint."""

    @patch("app.api.signals_routes._get_services")
    async def test_dashboard_signals(self, mock_get_services, client):
        """Dashboard endpoint returns formatted signals."""
        mock_signal_service = MagicMock()
        mock_signal_service.get_dashboard_signals = AsyncMock(return_value={
            "signals": [],
            "summary": {"total": 0},
        })

        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals/dashboard")
        assert response.status_code == 200

        data = response.json()
        assert "signals" in data


class TestListSignalTypesEndpoint:
    """Tests for GET /api/v1/signals/types endpoint."""

    def test_list_signal_types(self, client):
        """List signal types returns all types and scopes."""
        response = client.get("/api/v1/signals/types")
        assert response.status_code == 200

        data = response.json()
        assert "types" in data
        assert "scopes" in data
        assert len(data["types"]) > 0
        assert len(data["scopes"]) > 0

        # Check type structure
        first_type = data["types"][0]
        assert "type" in first_type
        assert "priority" in first_type
        assert "cache_ttl_seconds" in first_type
        assert "thresholds" in first_type


class TestInvalidateCacheEndpoint:
    """Tests for POST /api/v1/signals/invalidate endpoint."""

    @patch("app.api.signals_routes._get_services")
    async def test_invalidate_cache_default_event_type(self, mock_get_services, client):
        """Invalidate with default event type."""
        from app.signals import InvalidationEvent

        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_invalidation_service.process_event = AsyncMock(return_value=5)
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals/invalidate", json={
            "scope": "global",
        })
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["invalidated_count"] == 5

    @patch("app.api.signals_routes._get_services")
    async def test_invalidate_cache_with_scope_id(self, mock_get_services, client):
        """Invalidate with scope_id."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_invalidation_service.process_event = AsyncMock(return_value=3)
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals/invalidate", json={
            "scope": "topic",
            "scope_id": "topic-123",
        })
        assert response.status_code == 200

        data = response.json()
        assert data["scope_id"] == "topic-123"

    @patch("app.api.signals_routes._get_services")
    async def test_invalidate_cache_with_signal_types(self, mock_get_services, client):
        """Invalidate specific signal types."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_invalidation_service.process_event = AsyncMock(return_value=2)
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals/invalidate", json={
            "scope": "global",
            "signal_types": ["viralidade", "credibilidade_fonte"],
        })
        assert response.status_code == 200

    @patch("app.api.signals_routes._get_services")
    async def test_invalidate_cache_invalid_scope(self, mock_get_services, client):
        """Invalidate with invalid scope returns 400."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals/invalidate", json={
            "scope": "invalid_scope",
        })
        assert response.status_code == 400
        assert "Invalid scope" in response.json()["detail"]

    @patch("app.api.signals_routes._get_services")
    async def test_invalidate_cache_invalid_signal_type(self, mock_get_services, client):
        """Invalidate with invalid signal type returns 400."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.post("/api/v1/signals/invalidate", json={
            "scope": "global",
            "signal_types": ["invalid_type"],
        })
        assert response.status_code == 400
        assert "Invalid signal type" in response.json()["detail"]


class TestCacheStatsEndpoint:
    """Tests for GET /api/v1/signals/cache/stats endpoint."""

    @patch("app.api.signals_routes._get_services")
    def test_get_cache_stats(self, mock_get_services, client):
        """Get cache stats returns stats."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_cache_service.get_stats = MagicMock(return_value={
            "hits": 100,
            "misses": 20,
            "sets": 25,
            "deletes": 5,
            "hit_rate": 0.8,
        })
        mock_invalidation_service = MagicMock()
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals/cache/stats")
        assert response.status_code == 200

        data = response.json()
        assert data["hits"] == 100
        assert data["misses"] == 20
        assert data["hit_rate"] == 0.8


class TestInvalidationEventsEndpoint:
    """Tests for GET /api/v1/signals/cache/events endpoint."""

    @patch("app.api.signals_routes._get_services")
    def test_get_invalidation_events_default_limit(self, mock_get_services, client):
        """Get invalidation events with default limit."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_invalidation_service.get_recent_events = MagicMock(return_value=[])
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals/cache/events")
        assert response.status_code == 200

        data = response.json()
        assert "events" in data
        assert data["count"] == 0

    @patch("app.api.signals_routes._get_services")
    def test_get_invalidation_events_custom_limit(self, mock_get_services, client):
        """Get invalidation events with custom limit."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_invalidation_service.get_recent_events = MagicMock(return_value=[{"event": "test"}])
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.get("/api/v1/signals/cache/events?limit=10")
        assert response.status_code == 200

        data = response.json()
        assert len(data["events"]) == 1


class TestClearCacheEndpoint:
    """Tests for DELETE /api/v1/signals/cache endpoint."""

    @patch("app.api.signals_routes._get_services")
    async def test_clear_cache(self, mock_get_services, client):
        """Clear cache removes all entries."""
        mock_signal_service = MagicMock()
        mock_cache_service = MagicMock()
        mock_invalidation_service = MagicMock()
        mock_invalidation_service.invalidate_all = AsyncMock(return_value=42)
        mock_get_services.return_value = (mock_signal_service, mock_cache_service, mock_invalidation_service)

        response = client.delete("/api/v1/signals/cache")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["cleared_count"] == 42


class TestServiceInitialization:
    """Tests for service initialization."""

    def test_get_services_creates_instances(self):
        """_get_services creates instances on first call."""
        from app.api import signals_routes

        # Reset global instances
        signals_routes._cache_service = None
        signals_routes._signal_service = None
        signals_routes._invalidation_service = None

        signal_service, cache_service, invalidation_service = signals_routes._get_services()

        assert signal_service is not None
        assert cache_service is not None
        assert invalidation_service is not None

    def test_get_services_reuses_instances(self):
        """_get_services reuses instances on subsequent calls."""
        from app.api import signals_routes

        # First call
        s1, c1, i1 = signals_routes._get_services()

        # Second call
        s2, c2, i2 = signals_routes._get_services()

        # Should be same instances
        assert s1 is s2
        assert c1 is c2
        assert i1 is i2
