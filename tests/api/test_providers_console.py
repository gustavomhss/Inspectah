from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.api import providers_routes
from app.providers.models import IngestionProfile, ProfileKind, Provider, ProviderKind, ProviderStatus
from app.providers.run_store import RunStore
from app.providers.runner import ProfileRunner
from app.providers.service import ProviderService
from inspectah.api import build_app


def _build_client(tmp_path: Path) -> tuple[TestClient, ProviderService, RunStore]:
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


def _seed_provider_and_profile(svc: ProviderService) -> IngestionProfile:
    provider = Provider.create(
        id="prov-news",
        name="Provider News",
        kind=ProviderKind.NEWS,
        description="Stub provider",
        status=ProviderStatus.ACTIVE,
    )
    svc.save_provider(provider)
    profile = IngestionProfile.create(
        id="prof-1",
        provider_id=provider.id,
        name="Perfil BR",
        slug="perfil-br",
        kind=ProfileKind.NEWS,
        country="BR",
        language="pt",
        frequency_minutes=60,
        budget_daily_calls=5,
        budget_monthly_calls=100,
        enabled=True,
        status=ProviderStatus.ACTIVE,
    )
    svc.save_profile(profile)
    return profile


def test_list_and_detail_providers(tmp_path: Path):
    client, svc, _store = _build_client(tmp_path)
    _seed_provider_and_profile(svc)

    res = client.get("/api/providers")
    assert res.status_code == 200
    assert res.json()[0]["name"] == "Provider News"

    detail = client.get("/api/providers/prov-news")
    assert detail.status_code == 200
    body = detail.json()
    assert body["provider"]["id"] == "prov-news"
    assert len(body["profiles"]) == 1


def test_run_now_records_metrics_and_runs(tmp_path: Path):
    client, svc, store = _build_client(tmp_path)
    profile = _seed_provider_and_profile(svc)

    run_res = client.post(f"/api/providers/profiles/{profile.id}/run-now?limit=2")
    assert run_res.status_code == 200, run_res.text
    payload = run_res.json()
    assert payload["run"]["profile_id"] == profile.id

    runs_res = client.get(f"/api/providers/profiles/{profile.id}/runs")
    assert runs_res.status_code == 200
    runs = runs_res.json()
    assert len(runs) >= 1

    metrics_res = client.get(f"/api/providers/profiles/{profile.id}/metrics")
    metrics = metrics_res.json()
    assert metrics["total_runs"] >= 1
    assert metrics["items"] >= 0
    # ensure store is being updated as well
    assert store.metrics(profile.id)["total_runs"] >= 1


def test_filter_profiles_by_provider(tmp_path: Path):
    client, svc, _ = _build_client(tmp_path)
    _seed_provider_and_profile(svc)

    res = client.get("/api/providers/profiles", params={"provider_id": "prov-news"})
    assert res.status_code == 200
    profiles = res.json()
    assert len(profiles) == 1
    assert profiles[0]["provider_id"] == "prov-news"
