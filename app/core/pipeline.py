from __future__ import annotations

from datetime import datetime
import shutil
from typing import Any, Iterable, List

from app.gpt_client.client import run_query as gpt_run_query
from app.observability import metrics_s9

from . import storage
from .evidence_bundle_builder import build_evidence_bundle
from .models import EvidenceBundle, Item, ParsedQuery, QueryLog, QueryStatus, UserResponse
from .query_parser import parse_query
from .query_types import scenario_from_info_type
from .search_internal import search_internal


def run_pipeline(user_query: str) -> UserResponse:
    if not user_query or not user_query.strip():
        raise ValueError("user_query não pode ser vazio")

    parsed = parse_query(user_query)
    query_id = storage.generate_entity_id("s9_ql")
    timestamp = datetime.utcnow()
    items: List[Item] = []
    if parsed.query_type != "fora_de_escopo":
        items = search_internal(parsed)

    bundle = build_evidence_bundle(parsed, items)
    query_spec = {
        "raw_query": parsed.raw_query,
        "query_type": parsed.detailed_type,
        "filters": parsed.filters,
        "entities": parsed.entities,
    }
    scenario_tag = scenario_from_info_type(parsed.info_type)
    num_sources = bundle.meta.get("num_sources", 0)
    try:
        gpt_answer = gpt_run_query(
            info_type=parsed.info_type,
            bundle=bundle,
            query_spec=query_spec,
            scenario_tag=scenario_tag,
            user_query=user_query,
        )
    except TypeError:
        gpt_answer = gpt_run_query(bundle, user_query, parsed.query_type)
    except Exception:
        metrics_s9.record_error("gpt", "run_failure")
        raise
    confidence_flags = dict(gpt_answer.confidence_flags or {})
    reasons = confidence_flags.get("reasons") or []
    if num_sources <= 1:
        confidence_flags["level"] = "low"
        if isinstance(reasons, list):
            reasons.append("poucas_fontes")
        confidence_flags["reasons"] = reasons
    status = _determine_status(gpt_answer, parsed, bundle, items)

    response_id = storage.generate_entity_id("s9_resp")
    response = UserResponse(
        id=response_id,
        query_id=query_id,
        query_log_id=query_id,
        info_type=parsed.info_type,
        query_type=parsed.detailed_type,
        evidence_bundle_id=bundle.id,
        answer_text=gpt_answer.answer_text,
        summary={
            **gpt_answer.summary_structured,
            "num_sources": num_sources,
            "sources_count": num_sources,
            "bundle_id": bundle.id,
        },
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
        confidence=confidence_flags,
        limitations=gpt_answer.limitations,
        raw_gpt_payload=gpt_answer.prompt_used,
    )
    storage.save_user_response(response)

    log = QueryLog(
        query_id=query_id,
        user_query=user_query,
        query_type=parsed.detailed_type,
        info_type=parsed.info_type,
        scenario_tag=scenario_tag,
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
        },
    )
    storage.save_query_log(log)
    _mirror_legacy_artifacts(log, response, bundle)
    return response


def _determine_status(answer: Any, parsed: ParsedQuery, bundle: EvidenceBundle, items: Iterable[Item]) -> QueryStatus:
    resolution = answer.summary_structured.get("resolution") if answer else None
    if resolution in {"fora_de_escopo", "dados_insuficientes", "erro"}:
        return resolution  # type: ignore[return-value]
    if parsed.query_type == "fora_de_escopo":
        return "fora_de_escopo"
    if bundle.meta.get("num_sources", 0) == 0:
        return "dados_insuficientes"
    return "ok" if any(True for _ in items) else "dados_insuficientes"


def _status_to_error_code(status: QueryStatus) -> str | None:
    if status == "fora_de_escopo":
        return "OUT_OF_SCOPE"
    if status == "dados_insuficientes":
        return "NO_DATA"
    return None


def _mirror_legacy_artifacts(log: QueryLog, response: UserResponse, bundle: EvidenceBundle) -> None:
    """Espelha artefatos gerados no layout atual para o prefixo s8_* usado pelos gates da S8."""
    legacy_root = storage._repo_root() / "out" / "evidence"
    mappings = [
        (storage.queries_dir() / f"{log.query_id}.json", legacy_root / "s8_queries"),
        (storage.bundles_dir() / f"{bundle.id}.json", legacy_root / "s8_bundles"),
        (storage.responses_dir() / f"{response.id}.json", legacy_root / "s8_responses"),
    ]
    for src, dst_dir in mappings:
        if not src.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst_dir / src.name)


def _mirror_legacy_artifacts(log: QueryLog, response: UserResponse, bundle: EvidenceBundle) -> None:
    """Copia artefatos gerados no layout atual para o prefixo s8_* usado pelos gates antigos."""
    legacy_root = storage._repo_root() / "out" / "evidence"
    mappings = [
        (storage.queries_dir() / f"{log.query_id}.json", legacy_root / "s8_queries"),
        (storage.bundles_dir() / f"{bundle.id}.json", legacy_root / "s8_bundles"),
        (storage.responses_dir() / f"{response.id}.json", legacy_root / "s8_responses"),
    ]
    for src, dst_dir in mappings:
        if not src.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst_dir / src.name)


def _mirror_legacy_artifacts(log: QueryLog, response: UserResponse, bundle: EvidenceBundle) -> None:
    """Duplicar artefatos críticos nas pastas s8_* para compatibilidade com os gates legados."""
    legacy_root = storage._repo_root() / "out" / "evidence"
    mappings = [
        (storage.queries_dir() / f"{log.query_id}.json", legacy_root / "s8_queries"),
        (storage.bundles_dir() / f"{bundle.id}.json", legacy_root / "s8_bundles"),
        (storage.responses_dir() / f"{response.id}.json", legacy_root / "s8_responses"),
    ]
    for src, dst_dir in mappings:
        if not src.exists():
            continue
        dst_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst_dir / src.name)
