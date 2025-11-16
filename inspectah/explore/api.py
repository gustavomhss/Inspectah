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

from ..models import get_connection
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
    conditions = []
    params: List[Any] = []
    if source_id:
        conditions.append("source_id = ?")
        params.append(source_id)
    if collected_from:
        conditions.append("collected_at >= ?")
        params.append(collected_from)
    if collected_to:
        conditions.append("collected_at <= ?")
        params.append(collected_to)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = (
        "SELECT id, source_id, canonical_url, content_hash, collected_at, manifest_path "
        "FROM items "
        f"{where} ORDER BY collected_at DESC LIMIT ? OFFSET ?"
    )
    params.extend([limit, offset])
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        if not rows:
            return []
        item_ids = [row["id"] for row in rows]
        placeholders = ",".join("?" for _ in item_ids)
        kv_rows = conn.execute(
            "SELECT item_id, field_name, field_type, value_string, value_numeric, value_timestamp "
            f"FROM item_kv WHERE item_id IN ({placeholders})",
            item_ids,
        ).fetchall()
    field_map: Dict[int, Dict[str, Any]] = {item_id: {} for item_id in item_ids}
    for kv in kv_rows:
        value: Any = kv["value_string"]
        if kv["value_timestamp"]:
            value = kv["value_timestamp"]
        elif kv["value_numeric"] is not None:
            value = kv["value_numeric"]
        field_map[kv["item_id"]][kv["field_name"]] = value
    results: List[Dict[str, Any]] = []
    for row in rows:
        fields = field_map.get(row["id"], {})
        results.append(
            {
                "item_id": row["id"],
                "source_id": row["source_id"],
                "title": fields.get("title"),
                "url": fields.get("url"),
                "published_at": fields.get("published_at"),
                "source_name": fields.get("source_name"),
                "canonical_url": row["canonical_url"],
                "collected_at": row["collected_at"],
                "manifest_path": row["manifest_path"],
                "content_hash": row["content_hash"],
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
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, source_id, canonical_url, content_hash, collected_at, manifest_path FROM items WHERE id = ?",
            (item_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"item {item_id} not found")
        kv_rows = conn.execute(
            "SELECT field_name, field_type, value_string, value_numeric, value_timestamp FROM item_kv WHERE item_id = ?",
            (item_id,),
        ).fetchall()
    fields: Dict[str, Any] = {}
    for kv in kv_rows:
        value: Any = kv["value_string"]
        if kv["value_timestamp"]:
            value = kv["value_timestamp"]
        elif kv["value_numeric"] is not None:
            value = kv["value_numeric"]
        fields[kv["field_name"]] = value
    duration_ms = (time.perf_counter() - start) * 1000.0
    record_explore_query_latency(duration_ms)
    record_explore_query()
    logger.info(
        "explore_get_item",
        extra={
            "item_id": item_id,
            "source_id": row["source_id"],
            "duration_ms": duration_ms,
        },
    )
    return {
        "item_id": row["id"],
        "source_id": row["source_id"],
        "canonical_url": row["canonical_url"],
        "content_hash": row["content_hash"],
        "collected_at": row["collected_at"],
        "manifest_path": row["manifest_path"],
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
