from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


def utcnow() -> datetime:
    return datetime.utcnow()


class ProviderKind(str, Enum):
    NEWS = "news_provider"
    SOCIAL = "social_provider"


class ProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


@dataclass
class Provider:
    id: str
    name: str
    kind: ProviderKind
    description: str
    auth: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, Any] = field(default_factory=dict)
    status: ProviderStatus = ProviderStatus.INACTIVE
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @classmethod
    def create(
        cls,
        *,
        id: str,
        name: str,
        kind: ProviderKind,
        description: str,
        auth: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        limits: Optional[Dict[str, Any]] = None,
        status: ProviderStatus = ProviderStatus.INACTIVE,
        created_by: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> "Provider":
        now = utcnow()
        return cls(
            id=id,
            name=name,
            kind=kind,
            description=description,
            auth=auth or {},
            config=config or {},
            limits=limits or {},
            status=status,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=updated_by or created_by,
        )


class ProfileKind(str, Enum):
    NEWS = "news"
    SOCIAL = "social"


@dataclass
class IngestionProfile:
    id: str
    provider_id: str
    name: str
    slug: str
    kind: ProfileKind
    country: Optional[str]
    language: Optional[str]
    categories: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    frequency_minutes: int = 60
    budget_daily_calls: Optional[int] = None
    budget_monthly_calls: Optional[int] = None
    enabled: bool = True
    status: ProviderStatus = ProviderStatus.INACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utcnow)
    updated_at: datetime = field(default_factory=utcnow)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    @classmethod
    def create(
        cls,
        *,
        id: str,
        provider_id: str,
        name: str,
        slug: str,
        kind: ProfileKind,
        country: Optional[str],
        language: Optional[str],
        categories: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        frequency_minutes: int = 60,
        budget_daily_calls: Optional[int] = None,
        budget_monthly_calls: Optional[int] = None,
        enabled: bool = True,
        status: ProviderStatus = ProviderStatus.INACTIVE,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> "IngestionProfile":
        now = utcnow()
        return cls(
            id=id,
            provider_id=provider_id,
            name=name,
            slug=slug,
            kind=kind,
            country=country,
            language=language,
            categories=categories or [],
            keywords=keywords or [],
            filters=filters or {},
            frequency_minutes=frequency_minutes,
            budget_daily_calls=budget_daily_calls,
            budget_monthly_calls=budget_monthly_calls,
            enabled=enabled,
            status=status,
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
            created_by=created_by,
            updated_by=updated_by or created_by,
        )
