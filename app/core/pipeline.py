from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from app.gpt_client.client import run_query as gpt_run_query

from . import storage
from .evidence_bundle_builder import build_evidence_bundle
from .models import Item, QueryLog, QueryStatus, UserResponse
from .query_parser import parse_query
from .search_internal import search_internal


def run_pipeline(user_query: str) -> UserResponse:
    if not user_query or not user_query.strip():
        raise ValueError("user_query não pode ser vazio")

    parsed = parse_query(user_query)
    query_id = storage.generate_entity_id("ql")
    timestamp = datetime.utcnow()
    items: List[Item] = []
    if parsed.query_type != "fora_de_escopo":
        items = search_internal(parsed)

    bundle = build_evidence_bundle(parsed, items)
    gpt_answer = gpt_run_query(bundle, user_query, parsed.query_type)
    status = _determine_status(parsed.query_type, items)

    response = UserResponse(
        query_id=query_id,
        evidence_bundle_id=bundle.id,
        answer_text=gpt_answer.answer_text,
        summary=gpt_answer.summary_structured,
        evidence={
            "evidence_bundle_id": bundle.id,
            "sources": list(bundle.items_by_source.keys()),
            "items_preview": [
                {
                    "item_id": ref.item_id,
                    "source_id": ref.source_id,
                    "key_fields": ref.key_fields,
                }
                for refs in bundle.items_by_source.values()
                for ref in refs
            ][:10],
        },
        status=status,
        gpt_response_id=None,
        confidence=gpt_answer.confidence_flags,
        limitations=gpt_answer.limitations,
    )
    response_id = storage.generate_entity_id("resp")
    response.gpt_response_id = response_id
    storage.save_user_response(response, response_id=response_id)

    log = QueryLog(
        query_id=query_id,
        user_query=user_query,
        query_type=parsed.query_type,
        evidence_bundle_id=bundle.id,
        sources=list(bundle.items_by_source.keys()),
        items_used=[item.id for item in items],
        gpt_response_ref=response_id,
        timestamp=timestamp,
        status=status,
        error_code=_status_to_error_code(status),
    )
    storage.save_query_log(log)
    return response


def _determine_status(query_type: str, items: Iterable[Item]) -> QueryStatus:
    if query_type == "fora_de_escopo":
        return "fora_de_escopo"
    return "ok" if any(True for _ in items) else "dados_insuficientes"


def _status_to_error_code(status: QueryStatus) -> str | None:
    if status == "fora_de_escopo":
        return "OUT_OF_SCOPE"
    if status == "dados_insuficientes":
        return "NO_DATA"
    return None
