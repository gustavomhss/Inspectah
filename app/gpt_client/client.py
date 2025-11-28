from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Dict, List

from app.core.models import EvidenceBundle
from app.core.query_types import InfoType, QueryType

from . import prompts


@dataclass
class GptAnswer:
    answer_text: str
    summary_structured: Dict[str, Any]
    confidence_flags: Dict[str, Any]
    limitations: List[str] = field(default_factory=list)
    prompt_used: Dict[str, Any] = field(default_factory=dict)


PROMPT_BUILDERS: Dict[str, Any] = {
    "C1_preco_medio": prompts.build_price_prompt,
    "C2_comparacao_simples": prompts.build_comparison_prompt,
    "C3_checagem_factual": prompts.build_fact_prompt,
}


def run_query(
    *,
    info_type: InfoType,
    bundle: EvidenceBundle,
    query_spec: Dict[str, Any],
    scenario_tag: str,
    user_query: str,
) -> GptAnswer:
    builder = PROMPT_BUILDERS.get(info_type)
    if not builder:
        raise ValueError(f"InfoType não suportado na Sprint 9: {info_type}")

    prompt_payload = builder(bundle, query_spec, scenario_tag, user_query)
    context = prompt_payload["context"]
    decision = _simulate_model_decision(info_type, context, query_spec)
    return GptAnswer(
        answer_text=decision["answer_text"],
        summary_structured=decision["summary_structured"],
        confidence_flags=decision["confidence_flags"],
        limitations=decision["limitations"],
        prompt_used={**prompt_payload, "context": context},
    )


def _simulate_model_decision(info_type: InfoType, context: Dict[str, Any], query_spec: Dict[str, Any]) -> Dict[str, Any]:
    meta = context["meta"]
    sources = context["sources"]
    limitations = ["Somente dados do EvidenceBundle foram considerados."]

    query_type: QueryType = query_spec.get("query_type", "fora_de_escopo")  # type: ignore[assignment]
    if query_type == "fora_de_escopo":
        summary = _base_summary(meta, query_type)
        summary["resolution"] = "fora_de_escopo"
        return {
            "answer_text": "A pergunta está fora do escopo suportado nesta fase.",
            "summary_structured": summary,
            "confidence_flags": {"level": "low", "reasons": ["fora de escopo"]},
            "limitations": limitations,
        }

    if meta["num_sources"] < 2 or meta["num_items"] == 0:
        summary = _base_summary(meta, query_type)
        summary["resolution"] = "dados_insuficientes"
        return {
            "answer_text": "Dados insuficientes para chegar a uma conclusão confiável.",
            "summary_structured": summary,
            "confidence_flags": {"level": "low", "reasons": ["dados insuficientes"]},
            "limitations": limitations + ["Menos de duas fontes úteis."],
        }

    if query_type == "preco_medio":
        extra, answer = _summarize_price(meta, sources)
    elif query_type == "comparacao_simples":
        extra, answer = _summarize_comparison(meta, sources)
    else:
        extra, answer = _summarize_fact(meta, sources)

    summary = _base_summary(meta, query_type)
    summary.update(extra)
    summary.setdefault("resolution", "ok")
    confidence = _derive_confidence(summary)
    return {
        "answer_text": answer,
        "summary_structured": summary,
        "confidence_flags": confidence,
        "limitations": limitations,
    }


def _base_summary(meta: Dict[str, Any], query_type: str) -> Dict[str, Any]:
    return {
        "query_type": query_type,
        "info_type": meta.get("info_type"),
        "scenario_tag": meta.get("scenario_tag"),
        "num_sources": meta.get("num_sources", 0),
        "num_items": meta.get("num_items", 0),
    }


def _summarize_price(meta: Dict[str, Any], sources: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
    values: List[float] = []
    produto = None
    cidade = None
    moeda = "BRL"
    details: List[str] = []
    for source in sources:
        for item in source["items"]:
            payload = item.get("payload", {})
            produto = produto or payload.get("produto")
            cidade = cidade or payload.get("cidade")
            if payload.get("moeda"):
                moeda = payload["moeda"]
            valor = _to_float(payload.get("valor") or payload.get("valor_medio"))
            if valor is None:
                continue
            values.append(valor)
            details.append(f"{source['source_id']} registrou {valor:.2f} {moeda}")
    if not values:
        return {"resolution": "dados_insuficientes", "main_value": None, "range": None}, "Sem dados suficientes."
    avg_val = mean(values)
    extra = {
        "main_value": avg_val,
        "range": {"min": min(values), "max": max(values)},
        "unit": moeda,
        "resolution": "ok",
    }
    product_desc = produto or "o item consultado"
    location_hint = f" em {cidade}" if cidade else ""
    answer = (
        f"Com {meta['num_sources']} fontes, o preço médio de {product_desc}{location_hint} é {avg_val:.2f} {moeda}. "
        f"Detalhes: {'; '.join(details)}."
    )
    return extra, answer


def _summarize_comparison(meta: Dict[str, Any], sources: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
    best_location = None
    best_value = None
    best_source = None
    second_value = None
    moeda = "BRL"
    produto = None
    for source in sources:
        for item in source["items"]:
            payload = item.get("payload", {})
            produto = produto or payload.get("produto")
            if payload.get("moeda"):
                moeda = payload["moeda"]
            valor = _to_float(payload.get("valor"))
            location = payload.get("bairro") or payload.get("cidade")
            if valor is None or not location:
                continue
            if best_value is None or valor < best_value:
                second_value = best_value
                best_value = valor
                best_location = location
                best_source = source["source_id"]
            elif second_value is None or valor < second_value:
                second_value = valor
    extra = {
        "best_location": best_location,
        "best_value": best_value,
        "runner_up": second_value,
        "price_delta_pct": None,
        "unit": moeda,
        "resolution": "ok" if best_location and best_value is not None else "dados_insuficientes",
    }
    if best_location is None or best_value is None:
        return extra, "Não há dados suficientes para comparar regiões."
    if second_value is not None and second_value:
        extra["price_delta_pct"] = (second_value - best_value) / second_value * 100
    product_desc = produto or "o item consultado"
    answer = (
        f"{product_desc} está mais barato em {best_location} segundo {best_source}, custando {best_value:.2f} {moeda}."
    )
    return extra, answer


def _summarize_fact(meta: Dict[str, Any], sources: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
    confirmations = 0
    negatives = 0
    person = None
    case = None
    notes: List[str] = []
    for source in sources:
        for item in source["items"]:
            payload = item.get("payload", {})
            person = person or payload.get("pessoa")
            case = case or payload.get("caso")
            status = str(payload.get("status", "")).lower()
            if status in {"confirmado", "sim", "true"}:
                confirmations += 1
                notes.append(f"{source['source_id']} confirma.")
            elif status in {"negado", "nao", "não", "false"}:
                negatives += 1
                notes.append(f"{source['source_id']} nega.")
    if confirmations and not negatives:
        verdict = "confirmado"
        answer = f"As fontes confirmam o fato envolvendo {person or 'o sujeito analisado'} {('no caso ' + case) if case else ''}."
    elif negatives and not confirmations:
        verdict = "negado"
        answer = f"As fontes consultadas negam o fato para {person or 'o sujeito analisado'}."
    elif confirmations and negatives:
        verdict = "divergente"
        answer = "Há divergência entre as fontes; revisão manual recomendada."
    else:
        verdict = "indefinido"
        answer = "Nenhuma fonte trouxe afirmações conclusivas."
    extra = {
        "verdict": verdict,
        "confirmations": confirmations,
        "negatives": negatives,
        "notes": notes,
        "resolution": "ok" if confirmations or negatives else "dados_insuficientes",
    }
    return extra, answer


def _derive_confidence(summary: Dict[str, Any]) -> Dict[str, Any]:
    level = "high"
    reasons: List[str] = []
    if summary.get("num_sources", 0) < 2:
        level = "medium"
        reasons.append("apenas uma fonte disponível")
    rng = summary.get("range")
    if rng and isinstance(rng, dict) and rng.get("max") and rng.get("min"):
        spread = rng["max"] - rng["min"]
        if rng["max"] and spread > 0.15 * rng["max"]:
            level = "medium"
            reasons.append("variação relevante entre as fontes")
    if summary.get("verdict") == "divergente":
        level = "low"
        reasons.append("fontes se contradizem")
    if summary.get("resolution") != "ok":
        level = "low"
        reasons.append(f"resolução {summary['resolution']}")
    return {"level": level, "reasons": reasons}


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
