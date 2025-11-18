from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Any, Dict, List

from app.core.models import EvidenceBundle
from app.core.query_types import QueryType

from . import prompts


@dataclass
class GptAnswer:
    answer_text: str
    summary_structured: Dict[str, Any]
    confidence_flags: Dict[str, Any]
    limitations: List[str] = field(default_factory=list)
    prompt_used: Dict[str, Any] = field(default_factory=dict)


def run_query(bundle: EvidenceBundle, user_query: str, query_type: QueryType) -> GptAnswer:
    if not bundle.id:
        raise ValueError("EvidenceBundle.id não pode ser vazio")
    supported_types = {"preco_medio", "comparacao_simples", "checagem_factual", "fora_de_escopo"}
    if query_type not in supported_types:
        raise ValueError(f"Tipo de query não suportado na Sprint 9: {query_type}")

    prompt_payload = prompts.build_decision_prompt(bundle, user_query, query_type)
    context = prompt_payload["context"]
    meta = context["meta"]
    sources = context["sources"]

    limitations = ["Somente dados do EvidenceBundle foram considerados."]
    if meta["num_sources"] < 2:
        limitations.append("Menos de duas fontes disponíveis para o tipo consultado.")

    if query_type == "fora_de_escopo":
        summary = _base_summary(query_type, meta, extra={"resolution": "fora_de_escopo"})
        answer_text = "A pergunta está fora do escopo suportado nesta sprint."
        confidence = {"level": "low", "reasons": ["fora de escopo"]}
        return GptAnswer(answer_text, summary, confidence, limitations, prompt_payload)

    if meta["num_items"] == 0:
        extra = {"main_value": None, "range": None, "resolution": "dados_insuficientes"}
        summary = _base_summary(query_type, meta, extra)
        answer_text = "Dados insuficientes para chegar a uma conclusão."
        confidence = {"level": "low", "reasons": ["sem itens no bundle"]}
        return GptAnswer(answer_text, summary, confidence, limitations, prompt_payload)

    if query_type == "preco_medio":
        extra, answer_text = _summarize_agregacao(meta, sources)
    elif query_type == "comparacao_simples":
        extra, answer_text = _summarize_comparacao(meta, sources)
    else:
        extra, answer_text = _summarize_factual(meta, sources)

    summary = _base_summary(query_type, meta, extra)
    confidence = _derive_confidence(meta, extra)
    return GptAnswer(answer_text, summary, confidence, limitations, prompt_payload)


def _base_summary(query_type: str, meta: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    summary = {
        "query_type": query_type,
        "num_sources": meta["num_sources"],
        "num_items": meta["num_items"],
        "info_type": meta.get("info_type"),
        "scenario_tag": meta.get("scenario_tag"),
    }
    summary.update(extra)
    return summary


def _summarize_agregacao(meta: Dict[str, Any], sources: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
    values: List[float] = []
    produto = None
    cidade = None
    moeda = "BRL"
    details: List[str] = []
    for source in sources:
        for item in source["items"]:
            payload = item.get("payload", {})
            if produto is None and payload.get("produto"):
                produto = payload["produto"]
            if cidade is None and payload.get("cidade"):
                cidade = payload["cidade"]
            if payload.get("moeda"):
                moeda = payload["moeda"]
            valor = _to_float(payload.get("valor") or payload.get("valor_medio"))
            if valor is None:
                continue
            values.append(valor)
            details.append(f"{source['source_id']} registrou {valor:.2f} {moeda}")
    if not values:
        extra = {"main_value": None, "range": None, "unit": moeda}
        return extra, "As fontes não forneceram valores numéricos suficientes."
    avg_val = mean(values)
    extra = {
        "main_value": avg_val,
        "range": {"min": min(values), "max": max(values)},
        "unit": moeda,
    }
    product_desc = produto or "o item consultado"
    location_hint = f" em {cidade}" if cidade else ""
    answer_text = (
        f"Com {meta['num_sources']} fontes, o preço médio de {product_desc}{location_hint} fica em {avg_val:.2f} {moeda}. "
        f"Detalhes: {'; '.join(details)}."
    )
    return extra, answer_text


def _summarize_comparacao(meta: Dict[str, Any], sources: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
    best_location = None
    best_value = None
    best_source = None
    moeda = "BRL"
    produto = None
    for source in sources:
        for item in source["items"]:
            payload = item.get("payload", {})
            if produto is None and payload.get("produto"):
                produto = payload["produto"]
            if payload.get("moeda"):
                moeda = payload["moeda"]
            valor = _to_float(payload.get("valor"))
            location = payload.get("bairro") or payload.get("cidade")
            if valor is None or not location:
                continue
            if best_value is None or valor < best_value:
                best_value = valor
                best_location = location
                best_source = source["source_id"]
    extra = {"best_location": best_location, "best_value": best_value, "unit": moeda}
    if best_location is None or best_value is None:
        return extra, "Não há dados suficientes para comparar regiões."
    product_desc = produto or "o item consultado"
    answer = (
        f"{product_desc} está mais barato em {best_location} segundo {best_source}, custando {best_value:.2f} {moeda}."
    )
    return extra, answer


def _summarize_factual(meta: Dict[str, Any], sources: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
    confirmations = 0
    negatives = 0
    person = None
    case = None
    notes: List[str] = []
    for source in sources:
        for item in source["items"]:
            payload = item.get("payload", {})
            if person is None and payload.get("pessoa"):
                person = payload["pessoa"]
            if case is None and payload.get("caso"):
                case = payload["caso"]
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
    }
    return extra, answer


def _derive_confidence(meta: Dict[str, Any], summary_extra: Dict[str, Any]) -> Dict[str, Any]:
    level = "high"
    reasons: List[str] = []
    if meta["num_sources"] < 2:
        level = "medium"
        reasons.append("apenas uma fonte disponível")
    rng = summary_extra.get("range")
    if rng and rng.get("max") and rng.get("min"):
        spread = rng["max"] - rng["min"]
        if spread > 0.15 * rng["max"]:
            level = "medium"
            reasons.append("variação relevante entre as fontes")
    if summary_extra.get("verdict") == "divergente":
        level = "low"
        reasons.append("fontes se contradizem")
    return {"level": level, "reasons": reasons}


def _to_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
