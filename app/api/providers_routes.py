from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.providers.models import IngestionProfile, ProfileKind, Provider, ProviderKind, ProviderStatus
from app.providers.run_store import RunStore
from app.providers.runner import ProfileRunner
from app.providers.service import ProviderService

router = APIRouter(prefix="/api/providers", tags=["providers"])


def get_service() -> ProviderService:
    return ProviderService()


def get_run_store() -> RunStore:
    return RunStore()


def get_runner(
    svc: ProviderService = Depends(get_service), run_store: RunStore = Depends(get_run_store)
) -> ProfileRunner:
    return ProfileRunner(service=svc, run_store=run_store)


@router.get("", response_model=List[Provider])
def list_providers(
    kind: Optional[ProviderKind] = Query(None),
    status_filter: Optional[ProviderStatus] = Query(None, alias="status"),
    svc: ProviderService = Depends(get_service),
):
    providers = svc.list_providers()
    if kind:
        providers = [p for p in providers if p.kind == kind]
    if status_filter:
        providers = [p for p in providers if p.status == status_filter]
    return providers


@router.post("", response_model=Provider, status_code=status.HTTP_201_CREATED)
def create_provider(payload: Provider, svc: ProviderService = Depends(get_service)):
    provider = Provider(
        id=payload.id,
        name=payload.name,
        kind=ProviderKind(payload.kind),
        description=payload.description,
        auth=payload.auth,
        config=payload.config,
        limits=payload.limits,
        status=ProviderStatus(payload.status),
        created_by=payload.created_by,
        updated_by=payload.updated_by,
        created_at=payload.created_at,
        updated_at=payload.updated_at,
    )
    return svc.save_provider(provider)


@router.get("/profiles", response_model=List[IngestionProfile])
def list_profiles(
    provider_id: Optional[str] = Query(None),
    kind: Optional[ProfileKind] = Query(None),
    status_filter: Optional[ProviderStatus] = Query(None, alias="status"),
    q: Optional[str] = Query(None, description="Busca por nome/slug"),
    svc: ProviderService = Depends(get_service),
):
    profiles = svc.list_profiles()
    if provider_id:
        profiles = [p for p in profiles if p.provider_id == provider_id]
    if kind:
        profiles = [p for p in profiles if p.kind == kind]
    if status_filter:
        profiles = [p for p in profiles if p.status == status_filter]
    if q:
        q_lower = q.lower()
        profiles = [p for p in profiles if q_lower in p.name.lower() or q_lower in p.slug.lower()]
    return profiles


@router.post("/profiles", response_model=IngestionProfile, status_code=status.HTTP_201_CREATED)
def create_profile(payload: IngestionProfile, svc: ProviderService = Depends(get_service)):
    profile = IngestionProfile(
        id=payload.id,
        provider_id=payload.provider_id,
        name=payload.name,
        slug=payload.slug,
        kind=ProfileKind(payload.kind),
        country=payload.country,
        language=payload.language,
        categories=payload.categories,
        keywords=payload.keywords,
        filters=payload.filters,
        frequency_minutes=payload.frequency_minutes,
        budget_daily_calls=payload.budget_daily_calls,
        budget_monthly_calls=payload.budget_monthly_calls,
        enabled=payload.enabled,
        status=ProviderStatus(payload.status),
        metadata=payload.metadata,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
        created_at=payload.created_at,
        updated_at=payload.updated_at,
    )
    return svc.save_profile(profile)


@router.put("/profiles/{profile_id}", response_model=IngestionProfile)
def update_profile(profile_id: str, payload: IngestionProfile, svc: ProviderService = Depends(get_service)):
    profile = svc.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile.name = payload.name
    profile.slug = payload.slug
    profile.kind = ProfileKind(payload.kind)
    profile.country = payload.country
    profile.language = payload.language
    profile.categories = payload.categories
    profile.keywords = payload.keywords
    profile.filters = payload.filters
    profile.frequency_minutes = payload.frequency_minutes
    profile.budget_daily_calls = payload.budget_daily_calls
    profile.budget_monthly_calls = payload.budget_monthly_calls
    profile.enabled = payload.enabled
    profile.status = ProviderStatus(payload.status)
    profile.metadata = payload.metadata
    profile.updated_by = payload.updated_by or payload.created_by
    return svc.save_profile(profile)


@router.get("/profiles/{profile_id}")
def get_profile_detail(profile_id: str, svc: ProviderService = Depends(get_service), store: RunStore = Depends(get_run_store)):
    profile = svc.get_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    runs = store.list_runs(profile_id, limit=10)
    metrics = store.metrics(profile_id)
    return {"profile": profile, "runs": runs, "metrics": metrics}


@router.post("/profiles/{profile_id}/run-now")
async def run_profile_now(
    profile_id: str,
    limit: int = 3,
    runner: ProfileRunner = Depends(get_runner),
):
    try:
        run = await runner.enqueue(profile_id, limit=limit)
    except ValueError:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"status": "queued", "run": runner.as_dict(run)}


@router.get("/profiles/{profile_id}/runs")
def list_profile_runs(profile_id: str, store: RunStore = Depends(get_run_store)):
    return store.list_runs(profile_id, limit=20)


@router.get("/profiles/{profile_id}/metrics")
def list_profile_metrics(profile_id: str, store: RunStore = Depends(get_run_store)):
    return store.metrics(profile_id)


@router.put("/{provider_id}", response_model=Provider)
def update_provider(provider_id: str, payload: Provider, svc: ProviderService = Depends(get_service)):
    provider = svc.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    provider.name = payload.name
    provider.description = payload.description
    provider.auth = payload.auth
    provider.config = payload.config
    provider.limits = payload.limits
    provider.status = ProviderStatus(payload.status)
    provider.updated_by = payload.updated_by or payload.created_by
    return svc.save_provider(provider)


@router.get("/{provider_id}")
def get_provider_detail(provider_id: str, svc: ProviderService = Depends(get_service), store: RunStore = Depends(get_run_store)):
    provider = svc.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    profiles = svc.list_profiles_by_provider(provider_id)
    summaries: List[Dict] = []
    for profile in profiles:
        metrics = store.metrics(profile.id)
        last_run = store.list_runs(profile.id, limit=1)
        summaries.append(
            {
                "profile": profile,
                "metrics": metrics,
                "last_run": last_run[-1] if last_run else None,
            }
        )
    return {"provider": provider, "profiles": summaries}
