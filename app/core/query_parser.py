from __future__ import annotations

import re
from typing import Any, Dict, List

from .models import ParsedQuery, QueryType

SUPPORTED_TYPES: List[QueryType] = [
    "agregacao_simples",
    "comparacao_simples",
    "checagem_factual_simples",
    "fora_de_escopo",
]

TIME_WINDOW_HINTS = {
    "ultima semana": "last_7_days",
    "última semana": "last_7_days",
    "ultimo mes": "last_30_days",
    "último mês": "last_30_days",
}

OUT_OF_SCOPE_KEYWORDS = [
    "prever",
    "apostar",
    "opini",
    "vai ganhar",
    "ano que vem",
]


def parse_query(user_query: str) -> ParsedQuery:
    if not user_query or not user_query.strip():
        raise ValueError("user_query não pode ser vazio")
    raw_query = user_query.strip()
    lowered = raw_query.lower()

    query_type = _detect_type(lowered)
    entities: Dict[str, Any] = {}
    filters: Dict[str, Any] = {}

    time_window = _detect_time_window(lowered)
    if time_window:
        filters["time_window"] = time_window

    if query_type == "agregacao_simples":
        product = _extract_product(raw_query)
        city = _extract_city(raw_query)
        if product:
            entities["produto"] = product
            filters["produto"] = product.lower()
        if city:
            entities["cidade"] = city
            filters["cidade"] = city.lower()
        filters["source_types"] = ["precos_api_simples"]
        filters["info_type"] = "preco"
    elif query_type == "comparacao_simples":
        product = _extract_product(raw_query) or _extract_subject(raw_query)
        city = _extract_city(raw_query)
        if product:
            entities["produto"] = product
            filters["produto"] = product.lower()
        if city:
            entities["cidade"] = city
            filters["cidade"] = city.lower()
        filters["source_types"] = ["precos_api_simples"]
        filters["info_type"] = "preco"
    elif query_type == "checagem_factual_simples":
        person = _extract_person(raw_query)
        case = _extract_case(raw_query)
        if person:
            entities["pessoa"] = person
            filters["pessoa"] = person.lower()
        if case:
            entities["caso"] = case
            filters["caso"] = case.lower()
        filters["source_types"] = ["noticias_rss_simplificado"]
        filters["info_type"] = "fato"

    if query_type != "fora_de_escopo" and not entities:
        query_type = "fora_de_escopo"

    filters.setdefault("source_types", [])
    return ParsedQuery(
        raw_query=raw_query,
        query_type=query_type,
        entities=entities,
        filters=filters,
    )


def _detect_type(lowered_query: str) -> QueryType:
    if any(keyword in lowered_query for keyword in OUT_OF_SCOPE_KEYWORDS):
        return "fora_de_escopo"
    if "onde" in lowered_query and (
        "mais barato" in lowered_query or "compar" in lowered_query
    ):
        return "comparacao_simples"
    if "preço" in lowered_query or "preco" in lowered_query:
        if "médio" in lowered_query or "medio" in lowered_query or "qual" in lowered_query:
            return "agregacao_simples"
    if "foi" in lowered_query and (
        "condenado" in lowered_query or "acusado" in lowered_query or "envolvido" in lowered_query
    ):
        return "checagem_factual_simples"
    if "é verdade" in lowered_query or "e verdade" in lowered_query:
        return "checagem_factual_simples"
    return "fora_de_escopo"


def _detect_time_window(lowered_query: str) -> str | None:
    for phrase, code in TIME_WINDOW_HINTS.items():
        if phrase in lowered_query:
            return code
    return None


def _extract_product(raw_query: str) -> str | None:
    pattern = re.compile(
        r"pre[cç]o(?: médio)?(?: do| da| de)? ([^?]+?)(?: em | no | na |$)", re.IGNORECASE
    )
    match = pattern.search(raw_query)
    if match:
        return match.group(1).strip(" ?.")
    pattern_alt = re.compile(r"onde (?:o|a) ([^?]+?) está", re.IGNORECASE)
    match = pattern_alt.search(raw_query)
    if match:
        return match.group(1).strip(" ?.")
    return None


def _extract_subject(raw_query: str) -> str | None:
    match = re.search(r"comparar (.+?) em", raw_query, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(" ?.")
    return None


def _extract_city(raw_query: str) -> str | None:
    match = re.search(r" em ([^?]+)", raw_query, flags=re.IGNORECASE)
    if match:
        chunk = match.group(1).strip(" ?.!")
        chunk = re.sub(r"(onde .*)$", "", chunk, flags=re.IGNORECASE).strip()
        return chunk or None
    return None


def _extract_person(raw_query: str) -> str | None:
    match = re.search(r"([A-ZÁ-Ú][\wÁ-Úãõéêç\s]+?) foi", raw_query)
    if match:
        return match.group(1).strip()
    match = re.search(r"o ([A-ZÁ-Ú][\wÁ-Úãõéêç]+)", raw_query)
    if match:
        return match.group(1).strip()
    return None


def _extract_case(raw_query: str) -> str | None:
    match = re.search(r"caso ([^?]+)", raw_query, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(" ?.")
    return None
