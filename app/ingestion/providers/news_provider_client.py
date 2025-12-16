from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

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
    """
    Cliente real para newsdata.io (G4).
    - GET /api/1/latest com filtros fixos (country, language, domains, size).
    - Throttling <= 60 rpm (sleep entre chamadas).
    - Retry/backoff 1/2/4s com jitter apenas para 5xx/429.
    - Sem retry em 4xx (invalid apikey ou filtros).
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        *,
        timeout_seconds: int = 10,
    ):
        self.api_key = api_key or "demo"
        self.base_url = base_url or "https://newsdata.io/api/1"
        self.timeout_seconds = timeout_seconds

    async def fetch(
        self,
        profile: IngestionProfile,
        *,
        size: int = 50,
        domains: Optional[List[str]] = None,
        throttle_seconds: float = 1.0,
        max_attempts: int = 3,
        attempt_log: Optional[List[dict]] = None,
        **kwargs,
    ) -> List[RawNewsItem]:
        if "limit" in kwargs and kwargs["limit"] is not None:
            size = kwargs["limit"]
        params = {
            "apikey": self.api_key,
            "country": profile.country or "br",
            "language": profile.language or "pt",
            "size": size,
        }
        if domains:
            params["domainurl"] = ",".join(domains)
        if profile.filters:
            for key, value in profile.filters.items():
                if key == "domainurl" and domains:
                    continue  # não sobrescrever override
                params[key] = value

        attempt = 0
        backoff = 1.0
        last_error: Optional[str] = None

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            while attempt < max_attempts:
                attempt += 1
                attempt_info = {
                    "attempt": attempt,
                    "domains": domains or [],
                    "size": size,
                    "status_code": None,
                    "error": None,
                    "backoff_seconds": 0.0,
                    "duration_seconds": None,
                }
                start_time = time.time()
                try:
                    response = await client.get(
                        f"{self.base_url}/latest",
                        params=params,
                    )
                except httpx.HTTPError as exc:  # rede tentativa
                    last_error = f"http_error:{exc}"
                    attempt_info["error"] = last_error
                    attempt_info["duration_seconds"] = time.time() - start_time
                    if attempt < max_attempts:
                        attempt_info["backoff_seconds"] = await self._sleep_with_jitter(backoff)
                        backoff *= 2
                        if attempt_log is not None:
                            attempt_log.append(attempt_info)
                        continue
                    if attempt_log is not None:
                        attempt_log.append(attempt_info)
                    raise

                attempt_info["status_code"] = response.status_code
                attempt_info["duration_seconds"] = time.time() - start_time
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results") or []
                    items: List[RawNewsItem] = []
                    for entry in results:
                        items.append(
                            RawNewsItem(
                                external_id=str(entry.get("article_id") or entry.get("link") or ""),
                                title=entry.get("title") or "",
                                url=entry.get("link") or "",
                                published_at=entry.get("pubDate") or "",
                                summary=entry.get("description") or entry.get("content") or "",
                                source_name=entry.get("source_id") or "",
                                language=entry.get("language") or profile.language or "",
                                country=entry.get("country") or profile.country or "",
                                categories=entry.get("category") or [],
                                payload=entry,
                        )
                    )
                    attempt_info["backoff_seconds"] = throttle_seconds
                    if attempt_log is not None:
                        attempt_log.append(attempt_info)
                    await asyncio.sleep(throttle_seconds)  # respeita <=60 rpm
                    return items

                # 429/5xx => retry com backoff, 4xx => falha imediata
                if response.status_code in (429, 500, 502, 503, 504):
                    last_error = f"status_{response.status_code}"
                    if attempt < max_attempts:
                        attempt_info["error"] = last_error
                        attempt_info["backoff_seconds"] = await self._sleep_with_jitter(backoff)
                        backoff *= 2
                        if attempt_log is not None:
                            attempt_log.append(attempt_info)
                        continue
                if attempt_log is not None:
                    attempt_log.append(attempt_info)
                response.raise_for_status()

        raise RuntimeError(last_error or "newsdata_fetch_failed")

    @staticmethod
    async def _sleep_with_jitter(base: float) -> float:
        jitter = random.uniform(0, 0.25)
        delta = base + jitter
        await asyncio.sleep(delta)
        return delta
