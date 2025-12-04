from __future__ import annotations

import hashlib
from dataclasses import asdict
from typing import Dict, List, Set

from app.ingestion.providers.news_provider_client import RawNewsItem
from app.ingestion.providers.social_provider_client import RawSocialItem


def _hash_key(*parts: str) -> str:
    payload = "::".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def normalize_news(items: List[RawNewsItem]) -> List[Dict]:
    seen: Set[str] = set()
    normalized: List[Dict] = []
    for item in items:
        dedupe_key = _hash_key(item.url, item.external_id, item.title)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(
            {
                "content_id": dedupe_key,
                "kind": "news",
                "external_id": item.external_id,
                "title": item.title,
                "url": item.url,
                "published_at": item.published_at,
                "language": item.language,
                "country": item.country,
                "categories": item.categories,
                "source_name": item.source_name,
                "payload": asdict(item),
            }
        )
    return normalized


def normalize_social(items: List[RawSocialItem]) -> List[Dict]:
    seen: Set[str] = set()
    normalized: List[Dict] = []
    for item in items:
        dedupe_key = _hash_key(item.url, item.external_id, item.text)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized.append(
            {
                "content_id": dedupe_key,
                "kind": "social",
                "external_id": item.external_id,
                "text": item.text,
                "url": item.url,
                "published_at": item.published_at,
                "language": item.language,
                "country": item.country,
                "tags": item.tags,
                "payload": asdict(item),
            }
        )
    return normalized
