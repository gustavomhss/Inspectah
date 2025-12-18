"""
Sprint 40: Social Provider Client (S40-BE-018).

Enhanced for pilot domains (saude, politica) with rate limiting and retry.
"""

from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.providers.models import IngestionProfile

logger = logging.getLogger(__name__)

# Pilot domains supported (S40-BE-018)
PILOT_DOMAINS = {"saude", "politica"}

# Rate limiting configuration
DEFAULT_RATE_LIMIT_PER_MINUTE = 60
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 1.0
DEFAULT_RETRY_BACKOFF_MULTIPLIER = 2.0
DEFAULT_RETRY_JITTER = 0.1  # 10% jitter


@dataclass
class RawSocialItem:
    """Raw social media item from provider."""

    external_id: str
    text: str
    url: str
    published_at: str
    author: str
    language: str
    country: str
    tags: List[str]
    payload: Dict[str, Any]
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    domain: Optional[str] = None


@dataclass
class RateLimitState:
    """Track rate limiting state."""

    requests_made: int = 0
    window_start: float = field(default_factory=time.time)
    limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE


class SocialProviderError(Exception):
    """Error from social provider."""

    def __init__(self, message: str, error_code: Optional[str] = None, retryable: bool = False):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable


class SocialProviderClient:
    """
    Social media provider client (S40-BE-018).

    Features:
    - Support for pilot domains (saude, politica)
    - Rate limiting (configurable per minute)
    - Automatic retry with exponential backoff
    - Error handling and logging
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY_SECONDS,
    ):
        self.api_key = api_key or "demo"
        self.base_url = base_url or "https://social-api.local"
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._rate_limit = RateLimitState(limit_per_minute=rate_limit_per_minute)
        self._request_count = 0
        self._error_count = 0

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting (sync version for backward compat)."""
        now = time.time()
        elapsed = now - self._rate_limit.window_start

        # Reset window if a minute has passed
        if elapsed >= 60:
            self._rate_limit.requests_made = 0
            self._rate_limit.window_start = now

        if self._rate_limit.requests_made >= self._rate_limit.limit_per_minute:
            # Wait until window resets
            wait_time = 60 - elapsed
            logger.warning(f"[social_provider] Rate limit reached, waiting {wait_time:.1f}s")
            time.sleep(wait_time)
            self._rate_limit.requests_made = 0
            self._rate_limit.window_start = time.time()

        self._rate_limit.requests_made += 1

    async def _check_rate_limit_async(self) -> None:
        """Check and enforce rate limiting (async version)."""
        now = time.time()
        elapsed = now - self._rate_limit.window_start

        # Reset window if a minute has passed
        if elapsed >= 60:
            self._rate_limit.requests_made = 0
            self._rate_limit.window_start = now

        if self._rate_limit.requests_made >= self._rate_limit.limit_per_minute:
            # Wait until window resets (async)
            wait_time = 60 - elapsed
            logger.warning(f"[social_provider] Rate limit reached, waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            self._rate_limit.requests_made = 0
            self._rate_limit.window_start = time.time()

        self._rate_limit.requests_made += 1

    def _add_jitter(self, delay: float) -> float:
        """Add jitter to delay to prevent thundering herd."""
        jitter = delay * DEFAULT_RETRY_JITTER * random.uniform(-1, 1)
        return max(0.01, delay + jitter)  # Ensure minimum delay

    async def _fetch_with_retry(
        self,
        profile: IngestionProfile,
        limit: int,
    ) -> List[RawSocialItem]:
        """Fetch with automatic retry on failure."""
        last_error: Optional[Exception] = None
        delay = self.retry_delay

        for attempt in range(1, self.max_retries + 1):
            try:
                await self._check_rate_limit_async()
                return await self._do_fetch(profile, limit)
            except SocialProviderError as e:
                last_error = e
                self._error_count += 1
                if not e.retryable or attempt >= self.max_retries:
                    logger.error(f"[social_provider] Fetch failed after {attempt} attempts for {profile.slug}: {e}")
                    raise
                jittered_delay = self._add_jitter(delay)
                logger.warning(
                    f"[social_provider] Fetch attempt {attempt}/{self.max_retries} failed for {profile.slug}, "
                    f"retrying in {jittered_delay:.2f}s: {e}"
                )
                await asyncio.sleep(jittered_delay)
                delay *= DEFAULT_RETRY_BACKOFF_MULTIPLIER
            except Exception as e:
                last_error = e
                self._error_count += 1
                logger.error(f"[social_provider] Unexpected error fetching {profile.slug}: {e}")
                raise

        raise last_error or SocialProviderError("Max retries exceeded")

    async def _do_fetch(
        self,
        profile: IngestionProfile,
        limit: int,
    ) -> List[RawSocialItem]:
        """Actual fetch implementation (stub for demo)."""
        self._request_count += 1
        items: List[RawSocialItem] = []

        # Determine domain from profile
        domain = self._get_domain(profile)

        for idx in range(limit):
            external_id = f"social-{profile.slug}-{idx}"
            items.append(
                RawSocialItem(
                    external_id=external_id,
                    text=f"Post sintético {idx} para {profile.name}",
                    url=f"{self.base_url}/{profile.slug}/{idx}",
                    published_at=datetime.now(timezone.utc).isoformat(),
                    author="pilot_user",
                    language=profile.language or "pt",
                    country=profile.country or "BR",
                    tags=profile.keywords,
                    payload={"profile": profile.slug, "kind": profile.kind.value},
                    domain=domain,
                )
            )

        logger.debug(f"Fetched {len(items)} social items for {profile.slug}")
        return items

    def _get_domain(self, profile: IngestionProfile) -> Optional[str]:
        """Extract domain from profile keywords or slug."""
        # Check if profile is for a pilot domain
        for domain in PILOT_DOMAINS:
            if domain in profile.slug.lower():
                return domain
            if profile.keywords and any(domain in kw.lower() for kw in profile.keywords):
                return domain
        return None

    async def fetch(
        self,
        profile: IngestionProfile,
        limit: int = 5,
    ) -> List[RawSocialItem]:
        """
        Fetch social items for a profile (S40-BE-018).

        Args:
            profile: Ingestion profile
            limit: Maximum items to fetch (must be > 0)

        Returns:
            List of RawSocialItem

        Raises:
            ValueError: If limit <= 0
            SocialProviderError: On fetch failure
        """
        if limit <= 0:
            raise ValueError(f"limit must be > 0, got {limit}")
        return await self._fetch_with_retry(profile, limit)

    async def fetch_for_domain(
        self,
        domain: str,
        keywords: List[str],
        limit: int = 10,
    ) -> List[RawSocialItem]:
        """
        Fetch social items for a specific domain (S40-BE-018).

        Convenience method for pilot domains.

        Args:
            domain: Domain name (saude, politica)
            keywords: Keywords to search (must not be empty)
            limit: Maximum items (must be > 0)

        Returns:
            List of RawSocialItem

        Raises:
            ValueError: If domain not in pilot domains, limit <= 0, or keywords empty
            SocialProviderError: On fetch failure
        """
        if domain not in PILOT_DOMAINS:
            raise ValueError(f"Domain '{domain}' not in pilot domains: {PILOT_DOMAINS}")
        if limit <= 0:
            raise ValueError(f"limit must be > 0, got {limit}")
        if not keywords:
            raise ValueError("keywords must not be empty")

        # Create a synthetic profile for the domain
        from app.providers.models import ProfileKind

        profile = IngestionProfile.create(
            id=f"synth-{domain}-social",
            provider_id="synthetic",
            slug=f"{domain}-social",
            name=f"Social - {domain.title()}",
            kind=ProfileKind.SOCIAL,
            language="pt",
            country="BR",
            keywords=keywords,
        )

        return await self._fetch_with_retry(profile, limit)

    def get_stats(self) -> Dict[str, Any]:
        """Get client statistics."""
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "rate_limit_requests": self._rate_limit.requests_made,
            "rate_limit_per_minute": self._rate_limit.limit_per_minute,
        }

    def reset_stats(self) -> None:
        """Reset client statistics (useful for testing)."""
        self._request_count = 0
        self._error_count = 0
        self._rate_limit.requests_made = 0
        self._rate_limit.window_start = time.time()
        logger.debug("[social_provider] Stats reset")

    def is_pilot_domain(self, domain: str) -> bool:
        """Check if domain is a pilot domain (case-insensitive)."""
        return domain.lower() in PILOT_DOMAINS
