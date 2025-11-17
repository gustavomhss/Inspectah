from __future__ import annotations

import json
from typing import Any, Dict, List

from app.core import storage
from app.core.models import EvidenceBundle


def build_decision_prompt(bundle: EvidenceBundle, user_query: str, query_type: str) -> Dict[str, Any]:
    context = _bundle_to_context(bundle)
    system_prompt = (
        "Você é o motor de decisão do Inspectah. "
        "Use apenas os dados fornecidos pelo EvidenceBundle. "
        "Compare fontes, destaque convergências, divergências e outliers. "
        "Se algum dado estiver faltando, explique. "
        "Responda sempre citando os IDs das fontes consideradas. "
        "Sua saída precisa ter texto amigável + JSON estruturado."
    )
    user_prompt = (
        f"Pergunta original: {user_query}\n"
        f"Tipo de query: {query_type}\n"
        "Dados fornecidos pelas fontes (JSON):\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}\n"
        "Produza:\n"
        "1. answer_text (humano, neutro, explicando a decisão citando fontes).\n"
        "2. summary_structured JSON com campos: "
        "query_type, main_value, range/interval, num_sources, num_items, "
        "detalhes específicos do tipo.\n"
        "3. confidence_flags JSON com level + reasons.\n"
        "4. limitations array explicando restrições dos dados."
    )
    return {"system": system_prompt, "user": user_prompt, "context": context}


def _bundle_to_context(bundle: EvidenceBundle) -> Dict[str, Any]:
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
        },
        "sources": sources_payload,
    }
