"""
Comprehensive tests for providers_routes.py.

Covers all endpoints and error paths to achieve 95%+ coverage.
Extends existing test_providers_console.py tests.
"""
import pytest
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from fastapi.testclient import TestClient


def _to_json_dict(obj) -> dict:
    """Convert dataclass to JSON-serializable dict (datetime -> ISO string)."""
    data = asdict(obj)
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data

from app.api import providers_routes
from app.providers.models import (
    Provider,
    ProviderKind,
    ProviderStatus,
    IngestionProfile,
    ProfileKind,
)
from app.providers.service import ProviderService
from app.providers.run_store import RunStore
from app.providers.runner import ProfileRunner
from inspectah.api import build_app


def _build_client(tmp_path: Path) -> tuple[TestClient, ProviderService, RunStore]:
    """Build client with proper dependency injection."""
    db_path = tmp_path / "providers.sqlite"
    run_store = RunStore(path=tmp_path / "runs.jsonl")
    svc = ProviderService(db_path=db_path)
    runner = ProfileRunner(service=svc, run_store=run_store, evidence_dir=tmp_path / "runs")

    app = build_app()
    assert app
    app.dependency_overrides[providers_routes.get_service] = lambda: svc
    app.dependency_overrides[providers_routes.get_run_store] = lambda: run_store
    app.dependency_overrides[providers_routes.get_runner] = lambda: runner
    return TestClient(app), svc, run_store


def _create_provider(svc: ProviderService, provider_id: str = "test-provider") -> Provider:
    """Helper to create a provider."""
    provider = Provider.create(
        id=provider_id,
        name=f"Test Provider {provider_id}",
        kind=ProviderKind.NEWS,
        description="Test provider",
        status=ProviderStatus.ACTIVE,
    )
    return svc.save_provider(provider)


def _create_profile(svc: ProviderService, provider_id: str, profile_id: str = "test-profile") -> IngestionProfile:
    """Helper to create a profile."""
    profile = IngestionProfile.create(
        id=profile_id,
        provider_id=provider_id,
        name=f"Test Profile {profile_id}",
        slug=f"test-profile-{profile_id}",
        kind=ProfileKind.NEWS,
        country="BR",
        language="pt",
        frequency_minutes=60,
        budget_daily_calls=100,
        budget_monthly_calls=3000,
        enabled=True,
        status=ProviderStatus.ACTIVE,
    )
    return svc.save_profile(profile)


class TestListProvidersEndpoint:
    """Tests for GET /api/providers endpoint."""

    def test_list_providers_with_kind_filter(self, tmp_path: Path):
        """List providers filtered by kind."""
        client, svc, _ = _build_client(tmp_path)
        _create_provider(svc, "provider-news")

        # Filter by news kind (enum value is "news_provider")
        response = client.get("/api/providers", params={"kind": "news_provider"})
        assert response.status_code == 200
        data = response.json()
        # Should include the created provider
        news_providers = [p for p in data if p["kind"] == "news_provider"]
        assert len(news_providers) >= 1

    def test_list_providers_with_status_filter(self, tmp_path: Path):
        """List providers filtered by status."""
        client, svc, _ = _build_client(tmp_path)
        _create_provider(svc, "provider-active")

        response = client.get("/api/providers", params={"status": "active"})
        assert response.status_code == 200
        data = response.json()
        # All should be active
        for p in data:
            assert p["status"] == "active"


class TestCreateProviderEndpoint:
    """Tests for POST /api/providers endpoint."""

    def test_create_provider_via_api(self, tmp_path: Path):
        """Create provider via API endpoint."""
        client, svc, _ = _build_client(tmp_path)

        provider_obj = Provider.create(
            id="new-provider",
            name="New Provider",
            kind=ProviderKind.NEWS,
            description="Created via API",
            status=ProviderStatus.ACTIVE,
        )
        provider_data = _to_json_dict(provider_obj)

        response = client.post("/api/providers", json=provider_data)
        assert response.status_code == 201

        # Verify it was created
        created = svc.get_provider("new-provider")
        assert created is not None
        assert created.name == "New Provider"


class TestListProfilesEndpoint:
    """Tests for GET /api/providers/profiles endpoint."""

    def test_list_profiles_with_search_query(self, tmp_path: Path):
        """List profiles with search query."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)
        _create_profile(svc, provider.id, "searchable-profile")

        response = client.get("/api/providers/profiles", params={"q": "searchable"})
        assert response.status_code == 200
        data = response.json()
        # Should find the profile
        found = [p for p in data if "searchable" in p["name"].lower() or "searchable" in p["slug"].lower()]
        assert len(found) >= 1

    def test_list_profiles_filter_by_kind(self, tmp_path: Path):
        """List profiles filtered by kind."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)
        _create_profile(svc, provider.id)

        response = client.get("/api/providers/profiles", params={"kind": "news"})
        assert response.status_code == 200
        data = response.json()
        # Should include our profile
        news_profiles = [p for p in data if p["kind"] == "news"]
        assert len(news_profiles) >= 1

    def test_list_profiles_filter_by_status(self, tmp_path: Path):
        """List profiles filtered by status."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)
        _create_profile(svc, provider.id)

        response = client.get("/api/providers/profiles", params={"status": "active"})
        assert response.status_code == 200
        data = response.json()
        # All should be active
        for p in data:
            assert p["status"] == "active"


class TestCreateProfileEndpoint:
    """Tests for POST /api/providers/profiles endpoint."""

    def test_create_profile_via_api(self, tmp_path: Path):
        """Create profile via API endpoint."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)

        profile_obj = IngestionProfile.create(
            id="new-profile",
            provider_id=provider.id,
            name="New Profile",
            slug="new-profile",
            kind=ProfileKind.NEWS,
            country="BR",
            language="pt",
            frequency_minutes=120,
            budget_daily_calls=50,
            budget_monthly_calls=1500,
            enabled=True,
            status=ProviderStatus.ACTIVE,
        )
        profile_data = _to_json_dict(profile_obj)

        response = client.post("/api/providers/profiles", json=profile_data)
        assert response.status_code == 201

        # Verify it was created
        created = svc.get_profile("new-profile")
        assert created is not None
        assert created.name == "New Profile"


class TestUpdateProfileEndpoint:
    """Tests for PUT /api/providers/profiles/{profile_id} endpoint."""

    def test_update_profile(self, tmp_path: Path):
        """Update an existing profile."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)
        profile = _create_profile(svc, provider.id, "update-me")

        # Update the profile
        updated_data = _to_json_dict(profile)
        updated_data["name"] = "Updated Profile Name"
        updated_data["frequency_minutes"] = 180

        response = client.put(f"/api/providers/profiles/{profile.id}", json=updated_data)
        assert response.status_code == 200

        # Verify update
        updated = svc.get_profile(profile.id)
        assert updated.name == "Updated Profile Name"
        assert updated.frequency_minutes == 180

    def test_update_nonexistent_profile(self, tmp_path: Path):
        """Update non-existent profile returns 404."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)

        profile_obj = IngestionProfile.create(
            id="nonexistent",
            provider_id=provider.id,
            name="Ghost",
            slug="ghost",
            kind=ProfileKind.NEWS,
            country="BR",
            language="pt",
            frequency_minutes=60,
            budget_daily_calls=10,
            budget_monthly_calls=300,
            enabled=True,
            status=ProviderStatus.ACTIVE,
        )
        profile_data = _to_json_dict(profile_obj)

        response = client.put("/api/providers/profiles/nonexistent", json=profile_data)
        assert response.status_code == 404


class TestGetProfileDetailEndpoint:
    """Tests for GET /api/providers/profiles/{profile_id} endpoint."""

    def test_get_profile_detail(self, tmp_path: Path):
        """Get profile detail with runs and metrics."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc)
        profile = _create_profile(svc, provider.id, "detail-test")

        response = client.get(f"/api/providers/profiles/{profile.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["profile"]["id"] == profile.id
        assert "runs" in data
        assert "metrics" in data

    def test_get_nonexistent_profile_detail(self, tmp_path: Path):
        """Get non-existent profile returns 404."""
        client, svc, _ = _build_client(tmp_path)

        response = client.get("/api/providers/profiles/nonexistent")
        assert response.status_code == 404


class TestRunProfileNowEndpoint:
    """Tests for POST /api/providers/profiles/{profile_id}/run-now endpoint."""

    def test_run_nonexistent_profile(self, tmp_path: Path):
        """Run non-existent profile returns 404."""
        client, svc, _ = _build_client(tmp_path)

        response = client.post("/api/providers/profiles/nonexistent/run-now")
        assert response.status_code == 404


class TestUpdateProviderEndpoint:
    """Tests for PUT /api/providers/{provider_id} endpoint."""

    def test_update_provider(self, tmp_path: Path):
        """Update an existing provider."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc, "update-provider")

        # Update the provider
        updated_data = _to_json_dict(provider)
        updated_data["name"] = "Updated Provider Name"
        updated_data["description"] = "New description"

        response = client.put(f"/api/providers/{provider.id}", json=updated_data)
        assert response.status_code == 200

        # Verify update
        updated = svc.get_provider(provider.id)
        assert updated.name == "Updated Provider Name"
        assert updated.description == "New description"

    def test_update_nonexistent_provider(self, tmp_path: Path):
        """Update non-existent provider returns 404."""
        client, svc, _ = _build_client(tmp_path)

        provider_obj = Provider.create(
            id="nonexistent",
            name="Ghost Provider",
            kind=ProviderKind.NEWS,
            description="Does not exist",
            status=ProviderStatus.ACTIVE,
        )
        provider_data = _to_json_dict(provider_obj)

        response = client.put("/api/providers/nonexistent", json=provider_data)
        assert response.status_code == 404


class TestGetProviderDetailEndpoint:
    """Tests for GET /api/providers/{provider_id} endpoint."""

    def test_get_provider_detail_with_profiles(self, tmp_path: Path):
        """Get provider detail includes profiles."""
        client, svc, _ = _build_client(tmp_path)
        provider = _create_provider(svc, "detail-provider")
        _create_profile(svc, provider.id, "profile-1")
        _create_profile(svc, provider.id, "profile-2")

        response = client.get(f"/api/providers/{provider.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["provider"]["id"] == provider.id
        assert "profiles" in data
        assert len(data["profiles"]) >= 2

    def test_get_nonexistent_provider_detail(self, tmp_path: Path):
        """Get non-existent provider returns 404."""
        client, svc, _ = _build_client(tmp_path)

        response = client.get("/api/providers/nonexistent")
        assert response.status_code == 404


class TestDependencyInjection:
    """Tests for dependency injection functions."""

    def test_get_service_creates_instance(self):
        """get_service returns ProviderService instance."""
        from app.api.providers_routes import get_service

        service = get_service()
        assert isinstance(service, ProviderService)

    def test_get_run_store_creates_instance(self):
        """get_run_store returns RunStore instance."""
        from app.api.providers_routes import get_run_store

        store = get_run_store()
        assert isinstance(store, RunStore)

    def test_get_runner_creates_instance(self):
        """get_runner returns ProfileRunner instance."""
        from app.api.providers_routes import get_runner, get_service, get_run_store

        svc = get_service()
        store = get_run_store()
        runner = get_runner(svc=svc, run_store=store)
        assert isinstance(runner, ProfileRunner)
