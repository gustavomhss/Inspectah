from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from app.providers.models import IngestionProfile


@dataclass
class RawNewsItem:
    external_id: str
    title: str
    url: str
    published_at: str
    summary: str
    source_name: str
    language: str
    country: str
    categories: List[str]
    payload: Dict


class NewsProviderClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or "demo"
        self.base_url = base_url or "https://news-api.local"

    def fetch(self, profile: IngestionProfile, limit: int = 5) -> List[RawNewsItem]:
        # Stubbed client: return synthetic items using profile filters.
        items: List[RawNewsItem] = []
        for idx in range(limit):
            external_id = f"{profile.slug}-{idx}"
            items.append(
                RawNewsItem(
                    external_id=external_id,
                    title=f"{profile.name} notícia {idx}",
                    url=f"{self.base_url}/{profile.slug}/{idx}",
                    published_at="2025-12-04T00:00:00Z",
                    summary="Conteúdo sintético para sanity S31",
                    source_name=profile.name,
                    language=profile.language or "pt",
                    country=profile.country or "BR",
                    categories=profile.categories,
                    payload={"profile": profile.slug, "kind": profile.kind.value},
                )
            )
        return items
