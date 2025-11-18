from __future__ import annotations

import shutil
from datetime import datetime
from typing import List

from app.gpt_client.client import run_query as gpt_run_query

from . import storage
from .evidence_bundle_builder import build_evidence_bundle
from .models import EvidenceBundle, Item, ParsedQuery, QueryLog, QueryStatus, UserResponse
from .query_parser import parse_query
from .query_types import QueryType, normalize_query_type, scenario_from_info_type, to_legacy_query_type
from .search_internal import search_internal


def run_pipeline(user_query: str) -> UserResponse:
    if not user_query or not user_query.strip():
        raise ValueError("user_query não pode ser vazio")

    parsed = parse_query(user_query)
    query_id = storage.generate_entity_id("s9_ql")
    timestamp = datetime.utcnow()
    items: List[Item] = []
    canonical_type = normalize_query_type(parsed.query_type)
    if canonical_type != "fora_de_escopo":
        items = search_internal(parsed)

    bundle = build_evidence_bundle(parsed, items)
    gpt_answer = gpt_run_query(bundle, user_query, canonical_type)
    status = _determine_status(canonical_type, bundle, items)
    legacy_type = to_legacy_query_type(canonical_type)

    response_id = storage.generate_entity_id("s9_resp")
    response = UserResponse(
        id=response_id,
        query_id=query_id,
        query_log_id=query_id,
        info_type=parsed.info_type,
        query_type=canonical_type,
        evidence_bundle_id=bundle.id,
        answer_text=gpt_answer.answer_text,
        summary={**gpt_answer.summary_structured, "query_type": legacy_type},
        evidence={
            "bundle_id": bundle.id,
            "evidence_bundle_id": bundle.id,
            "bundle_path": str(storage.bundles_dir() / f"{bundle.id}.json"),
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
        confidence=gpt_answer.confidence_flags,
        limitations=gpt_answer.limitations,
        raw_gpt_payload=gpt_answer.prompt_used,
    )
    storage.save_user_response(response)

    log = QueryLog(
        query_id=query_id,
        user_query=user_query,
        query_type=canonical_type,
        info_type=parsed.info_type,
        scenario_tag=scenario_from_info_type(parsed.info_type),
        evidence_bundle_id=bundle.id,
        user_response_id=response.id,
        sources=list(bundle.items_by_source.keys()),
        items_used=[item.id for item in items],
        gpt_response_ref=response.id,
        timestamp=timestamp,
        status=status,
        error_code=_status_to_error_code(status),
        meta={
            "bundle_path": str(storage.bundles_dir() / f"{bundle.id}.json"),
            "response_path": str(storage.responses_dir() / f"{response.id}.json"),
            "legacy_type": legacy_type,
            "query_type": canonical_type,
        },
    )
    storage.save_query_log(log)
    _mirror_legacy_artifacts(log, response, bundle)
    return response


def _determine_status(query_type: QueryType, bundle: EvidenceBundle, items: List[Item]) -> QueryStatus:
    if query_type == "fora_de_escopo":
        return "fora_de_escopo"
    source_count = bundle.meta.get("num_sources") or len(bundle.items_by_source)
    if not items:
        return "dados_insuficientes"
    if source_count < 2 and query_type == "preco_medio":
        reliabilities = {
            bundle.sources_meta.get(source_id, {}).get("reliability", "desconhecida")
            for source_id in bundle.items_by_source
        }
        if any(str(rel).lower() == "baixa" for rel in reliabilities):
            return "ok"
        return "dados_insuficientes"
    if source_count < 1:
        return "dados_insuficientes"
    return "ok"


def _status_to_error_code(status: QueryStatus) -> str | None:
    if status == "fora_de_escopo":
        return "OUT_OF_SCOPE"
    if status == "dados_insuficientes":
        return "NO_DATA"
    return None


def _mirror_legacy_artifacts(log: QueryLog, response: UserResponse, bundle: EvidenceBundle) -> None:
    base_dir = storage.bundles_dir().parent
    legacy_queries = (base_dir / "s8_queries")
    legacy_bundles = (base_dir / "s8_bundles")
    legacy_responses = (base_dir / "s8_responses")
    for path in (legacy_queries, legacy_bundles, legacy_responses):
        path.mkdir(parents=True, exist_ok=True)

    src_log = storage.queries_dir() / f"{log.query_id}.json"
    if src_log.exists():
        shutil.copy(src_log, legacy_queries / src_log.name)

    src_bundle = storage.bundles_dir() / f"{bundle.id}.json"
    if src_bundle.exists():
        shutil.copy(src_bundle, legacy_bundles / src_bundle.name)

    src_response = storage.responses_dir() / f"{response.id}.json"
    if src_response.exists():
        shutil.copy(src_response, legacy_responses / src_response.name)
