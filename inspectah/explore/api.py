from __future__ import annotations
from datetime import datetime
import time
from typing import Any, Dict, List, Optional

import logging

try:  # pragma: no cover
    from fastapi import APIRouter, Request, Response
    from fastapi.responses import JSONResponse
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Request = None  # type: ignore[misc]
    Response = None  # type: ignore[misc]
    JSONResponse = None  # type: ignore[misc]

from ..models import get_legacy_item, list_legacy_items
from ..metrics import record_explore_query_latency, record_explore_request, record_explore_query
from ..registry.loader import load_sources
from .rate_limit import (
    IDENTITY_HEADER,
    RATE_LIMIT_POLICY,
    RateLimitDecision,
    check_rate_limit,
)

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def _apply_rate_limit(identity: Optional[str]) -> RateLimitDecision:
    decision = check_rate_limit(identity)
    record_explore_request(rate_limited=not decision.allowed)
    return decision


def _parse_iso(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise ValueError(f"invalid ISO timestamp: {value}") from exc


def _load_items(
    source_id: Optional[str],
    collected_from: Optional[str],
    collected_to: Optional[str],
    limit: int,
    offset: int,
) -> List[Dict[str, Any]]:
    records = list_legacy_items(
        source_id=source_id,
        collected_from=collected_from,
        collected_to=collected_to,
    )
    if not records:
        return []
    sliced = records[offset : offset + limit]
    results: List[Dict[str, Any]] = []
    for record in sliced:
        fields = dict(record.fields)
        results.append(
            {
                "item_id": record.item_id,
                "source_id": record.source_id,
                "title": fields.get("title"),
                "url": fields.get("url"),
                "published_at": fields.get("published_at"),
                "source_name": fields.get("source_name"),
                "canonical_url": record.canonical_url,
                "collected_at": record.collected_at.isoformat(),
                "manifest_path": record.manifest_path,
                "content_hash": record.content_hash,
                "fields": fields,
            }
        )
    return results


def query_items(
    source_id: Optional[str] = None,
    collected_from: Optional[str] = None,
    collected_to: Optional[str] = None,
    q: Optional[str] = None,
    page: int = 1,
    page_size: int = DEFAULT_PAGE_SIZE,
) -> Dict[str, Any]:
    start = time.perf_counter()
    page = max(page, 1)
    page_size = max(1, min(page_size, MAX_PAGE_SIZE))
    offset = (page - 1) * page_size
    from_iso = _parse_iso(collected_from)
    to_iso = _parse_iso(collected_to)
    items = _load_items(source_id, from_iso, to_iso, page_size, offset)
    if q:
        q_lower = q.lower()
        items = [item for item in items if (item.get("title") or "").lower().find(q_lower) != -1]
    duration_ms = (time.perf_counter() - start) * 1000.0
    record_explore_query_latency(duration_ms)
    record_explore_query()
    logger.info(
        "explore_query",
        extra={
            "items": len(items),
            "source_filter": source_id or "",
            "has_search": bool(q),
            "page": page,
            "page_size": page_size,
            "duration_ms": duration_ms,
        },
    )
    return {"items": items, "page": page, "page_size": page_size}


def get_item_detail(item_id: int) -> Dict[str, Any]:
    start = time.perf_counter()
    record = get_legacy_item(item_id)
    if record is None:
        raise KeyError(f"item {item_id} not found")
    fields = dict(record.fields)
    duration_ms = (time.perf_counter() - start) * 1000.0
    record_explore_query_latency(duration_ms)
    record_explore_query()
    logger.info(
        "explore_get_item",
        extra={
            "item_id": item_id,
            "source_id": record.source_id,
            "duration_ms": duration_ms,
        },
    )
    return {
        "item_id": record.item_id,
        "source_id": record.source_id,
        "canonical_url": record.canonical_url,
        "content_hash": record.content_hash,
        "collected_at": record.collected_at.isoformat(),
        "manifest_path": record.manifest_path,
        "fields": fields,
    }


def list_sources() -> List[Dict[str, Any]]:
    sources = load_sources()
    return [
        {
            "id": cfg.id,
            "name": cfg.name,
            "type": cfg.type,
            "url": cfg.url,
            "schedule_minutes": cfg.schedule_minutes,
            "enabled": cfg.enabled,
        }
        for cfg in sources.values()
    ]


def build_router():
    if APIRouter is None:  # pragma: no cover
        return None
    router = APIRouter()

    def _enforce_rate_limit(request: Request, response: Response) -> Optional[JSONResponse]:
        # v0: identity follows the Inspectah client header contract (X-Client-Id).
        identity = request.headers.get(IDENTITY_HEADER) or "ANONYMOUS"
        decision = _apply_rate_limit(identity)
        for header, value in decision.headers.items():
            response.headers[header] = value
        if not decision.allowed:
            body = {
                "error": {
                    "code": "RATE_LIMITED",
                    "message": f"Rate limit exceeded ({RATE_LIMIT_POLICY})",
                    "retry_after": decision.retry_after,
                    "policy": RATE_LIMIT_POLICY,
                }
            }
            return JSONResponse(status_code=429, content=body, headers=decision.headers)
        return None

    @router.get("/explore/items")
    def list_items(
        request: Request,
        response: Response,
        source_id: Optional[str] = None,
        collected_from: Optional[str] = None,
        collected_to: Optional[str] = None,
        q: Optional[str] = None,
        page: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> Dict[str, Any]:
        limit_response = _enforce_rate_limit(request, response)
        if limit_response is not None:
            return limit_response
        return query_items(
            source_id=source_id,
            collected_from=collected_from,
            collected_to=collected_to,
            q=q,
            page=page,
            page_size=page_size,
        )

    @router.get("/explore/items/{item_id}")
    def get_item(item_id: int, request: Request, response: Response) -> Dict[str, Any]:
        limit_response = _enforce_rate_limit(request, response)
        if limit_response is not None:
            return limit_response
        return get_item_detail(item_id)

    @router.get("/explore/sources")
    def list_sources_endpoint(request: Request, response: Response) -> Dict[str, Any]:
        limit_response = _enforce_rate_limit(request, response)
        if limit_response is not None:
            return limit_response
        sources = list_sources()
        logger.info("explore_list_sources", extra={"count": len(sources)})
        return {"sources": sources}

    return router


__all__ = ["build_router", "query_items", "get_item_detail", "list_sources"]
logger = logging.getLogger(__name__)
