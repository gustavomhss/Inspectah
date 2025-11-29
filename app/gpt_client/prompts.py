from __future__ import annotations

import json
from typing import Any, Dict, List

from app.core import storage
from app.core.models import EvidenceBundle


def build_price_prompt(bundle: EvidenceBundle, query_spec: Dict[str, Any], scenario_tag: str, user_query: str) -> Dict[str, Any]:
    context = _bundle_to_context(bundle, scenario_tag)
    system_prompt = (
        "Você responde perguntas sobre preço médio de uma cesta de itens. "
        "Use apenas os dados fornecidos; cite os IDs das fontes quando descrever resultados." )
    user_prompt = _format_user_prompt(
        user_query=user_query,
        query_spec=query_spec,
        context=context,
        expected_fields=(
            "summary_structured deve conter: resolution, main_value, range.min, range.max, unit, num_sources, num_items, info_type, scenario_tag."
        ),
    )
    return {"system": system_prompt, "user": user_prompt, "context": context, "settings": _deterministic_settings()}


def build_comparison_prompt(bundle: EvidenceBundle, query_spec: Dict[str, Any], scenario_tag: str, user_query: str) -> Dict[str, Any]:
    context = _bundle_to_context(bundle, scenario_tag)
    system_prompt = (
        "Você compara preços entre regiões/fornecedores e explica qual é o melhor custo. "
        "Use apenas os dados do EvidenceBundle; deixe claro quando as fontes divergem." )
    user_prompt = _format_user_prompt(
        user_query=user_query,
        query_spec=query_spec,
        context=context,
        expected_fields=(
            "summary_structured deve conter: resolution, best_location, best_value, runner_up opcional, price_delta_pct opcional, num_sources, num_items, info_type, scenario_tag."
        ),
    )
    return {"system": system_prompt, "user": user_prompt, "context": context, "settings": _deterministic_settings()}


def build_fact_prompt(bundle: EvidenceBundle, query_spec: Dict[str, Any], scenario_tag: str, user_query: str) -> Dict[str, Any]:
    context = _bundle_to_context(bundle, scenario_tag)
    system_prompt = (
        "Você checa declarações factuais simples. "
        "Classifique o resultado como confirmado/negado/divergente/indefinido e explique." )
    user_prompt = _format_user_prompt(
        user_query=user_query,
        query_spec=query_spec,
        context=context,
        expected_fields=(
            "summary_structured deve conter: resolution, verdict, confirmations, negatives, notes[], num_sources, num_items, info_type, scenario_tag."
        ),
    )
    return {"system": system_prompt, "user": user_prompt, "context": context, "settings": _deterministic_settings()}


def _format_user_prompt(*, user_query: str, query_spec: Dict[str, Any], context: Dict[str, Any], expected_fields: str) -> str:
    return (
        f"Pergunta original: {user_query}\n"
        f"Query estruturada: {json.dumps(query_spec, ensure_ascii=False)}\n"
        "Dados fornecidos pelas fontes (JSON):\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n"
        "Produza um JSON com: answer_text, summary_structured, confidence_flags, limitations.\n"
        f"{expected_fields}\n"
        "Use resolution='dados_insuficientes' quando não houver dados suficientes e 'fora_de_escopo' quando apropriado."
    )


def _deterministic_settings() -> Dict[str, Any]:
    return {"temperature": 0.0, "top_p": 0.0, "max_tokens": 800}


def _bundle_to_context(bundle: EvidenceBundle, scenario_tag: str) -> Dict[str, Any]:
    sources_payload: List[Dict[str, Any]] = []
    total_items = 0
    for source_id, refs in bundle.items_by_source.items():
        records: List[Dict[str, Any]] = []
        for ref in refs:
            item = storage.get_item(ref.item_id)
            record = {
                "item_id": ref.item_id,
                "source_id": source_id,
                "key_fields": ref.key_fields,
            }
            if item:
                record["payload"] = item.payload
                record["created_at"] = item.created_at.isoformat()
            records.append(record)
        sources_payload.append({"source_id": source_id, "items": records})
        total_items += len(records)
    return {
        "meta": {
            "num_sources": len(sources_payload),
            "num_items": total_items,
            "query_filters": bundle.query_filters,
            "info_type": bundle.info_type,
            "scenario_tag": scenario_tag,
        },
        "sources": sources_payload,
    }
