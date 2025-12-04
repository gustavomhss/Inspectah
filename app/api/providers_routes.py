from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.providers.models import IngestionProfile, ProfileKind, Provider, ProviderKind, ProviderStatus
from app.providers.service import ProviderService

router = APIRouter(prefix="/api/providers", tags=["providers"])


def get_service() -> ProviderService:
    return ProviderService()


@router.get("", response_model=List[Provider])
def list_providers(svc: ProviderService = Depends(get_service)):
    return svc.list_providers()


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


@router.get("/profiles", response_model=List[IngestionProfile])
def list_profiles(svc: ProviderService = Depends(get_service)):
    return svc.list_profiles()


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
