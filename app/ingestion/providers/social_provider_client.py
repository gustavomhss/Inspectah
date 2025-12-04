from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from app.providers.models import IngestionProfile


@dataclass
class RawSocialItem:
    external_id: str
    text: str
    url: str
    published_at: str
    author: str
    language: str
    country: str
    tags: List[str]
    payload: Dict


class SocialProviderClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or "demo"
        self.base_url = base_url or "https://social-api.local"

    def fetch(self, profile: IngestionProfile, limit: int = 5) -> List[RawSocialItem]:
        items: List[RawSocialItem] = []
        for idx in range(limit):
            external_id = f"social-{profile.slug}-{idx}"
            items.append(
                RawSocialItem(
                    external_id=external_id,
                    text=f"Post sintético {idx} para {profile.name}",
                    url=f"{self.base_url}/{profile.slug}/{idx}",
                    published_at="2025-12-04T00:00:00Z",
                    author="pilot_user",
                    language=profile.language or "pt",
                    country=profile.country or "BR",
                    tags=profile.keywords,
                    payload={"profile": profile.slug, "kind": profile.kind.value},
                )
            )
        return items
