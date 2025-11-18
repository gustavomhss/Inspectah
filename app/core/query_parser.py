from __future__ import annotations

import re
import os
from typing import Any, Dict

from .models import ParsedQuery
from .query_types import QueryType, resolve_info_type, to_legacy_query_type

TIME_WINDOW_HINTS = {
    "ultima semana": "last_7_days",
    "última semana": "last_7_days",
    "ultimo mes": "last_30_days",
    "último mês": "last_30_days",
}

OUT_OF_SCOPE_KEYWORDS = [
    "prever",
    "apostar",
    "opin",
    "vai ganhar",
    "ano que vem",
]

PRODUCT_PREFIX_STOPWORDS = {"atual", "qual", "quanto", "o", "a", "os", "as", "do", "da"}


def parse_query(user_query: str) -> ParsedQuery:
    if not user_query or not user_query.strip():
        raise ValueError("user_query não pode ser vazio")
    raw_query = user_query.strip()
    lowered = raw_query.lower()

    canonical_type = _detect_type(lowered)
    info_type = resolve_info_type(canonical_type)
    entities: Dict[str, Any] = {}
    filters: Dict[str, Any] = {}

    time_window = _detect_time_window(lowered)
    if time_window:
        filters["time_window"] = time_window

    if canonical_type == "preco_medio":
        product = _extract_product(raw_query)
        city = _extract_city(raw_query)
        if product:
            clean_product = _clean_entity(product)
            entities["produto"] = clean_product
            filters["produto"] = clean_product.lower()
        if city:
            entities["cidade"] = city
            filters["cidade"] = city.lower()
        filters["source_types"] = ["precos_api_simples"]
        filters["info_type"] = "preco"
    elif canonical_type == "comparacao_simples":
        product = _extract_product(raw_query) or _extract_subject(raw_query)
        city = _extract_city(raw_query)
        if product:
            clean_product = _clean_entity(product)
            entities["produto"] = clean_product
            filters["produto"] = clean_product.lower()
        if city:
            entities["cidade"] = city
            filters["cidade"] = city.lower()
        filters["source_types"] = ["precos_api_simples"]
        filters["info_type"] = "preco"
    elif canonical_type == "checagem_factual":
        person = _extract_person(raw_query)
        case = _extract_case(raw_query)
        if person:
            entities["pessoa"] = person
            filters["pessoa"] = person.lower()
        if case:
            entities["caso"] = case
            filters["caso"] = case.lower()
        if not entities:
            entities["claim"] = raw_query
            filters["claim_hash"] = _normalize(raw_query)
        filters["source_types"] = ["noticias_rss_simplificado"]
        filters["info_type"] = "fato"

    if canonical_type != "fora_de_escopo" and not entities:
        canonical_type = "fora_de_escopo"
        info_type = "fora_de_escopo"

    filters.setdefault("source_types", [])
    legacy_type = to_legacy_query_type(canonical_type)
    result_type = legacy_type if _use_legacy_query_types() else canonical_type
    return ParsedQuery(
        raw_query=raw_query,
        query_type=result_type,
        info_type=info_type,
        entities=entities,
        filters=filters,
    )


def _use_legacy_query_types() -> bool:
    return os.getenv("INSPECTAH_PARSER_LEGACY_TYPES") == "1"


def _detect_type(lowered_query: str) -> QueryType:
    if any(keyword in lowered_query for keyword in OUT_OF_SCOPE_KEYWORDS):
        return "fora_de_escopo"
    if _looks_like_factual(lowered_query):
        return "checagem_factual"
    if "onde" in lowered_query and (
        "mais barato" in lowered_query or "compar" in lowered_query
    ):
        return "comparacao_simples"
    if "preço" in lowered_query or "preco" in lowered_query:
        if "médio" in lowered_query or "medio" in lowered_query or "qual" in lowered_query:
            return "preco_medio"
    if "foi" in lowered_query and (
        "condenado" in lowered_query or "acusado" in lowered_query or "envolvido" in lowered_query
    ):
        return "checagem_factual"
    if "é verdade" in lowered_query or "e verdade" in lowered_query:
        return "checagem_factual"
    return "fora_de_escopo"


def _looks_like_factual(lowered_query: str) -> bool:
    if "é verdade" in lowered_query or "e verdade" in lowered_query:
        return True
    if "checagem" in lowered_query or "verificar" in lowered_query:
        return True
    if "caiu" in lowered_query and "%" in lowered_query:
        return True
    return False


def _detect_time_window(lowered_query: str) -> str | None:
    for phrase, code in TIME_WINDOW_HINTS.items():
        if phrase in lowered_query:
            return code
    return None


def _extract_product(raw_query: str) -> str | None:
    pattern = re.compile(
        r"pre[cç]o(?: médio)?(?: [^ ]+)?(?: do| da| de)? ([^?]+?)(?: em | no | na |$)",
        re.IGNORECASE,
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
    return None


def _extract_case(raw_query: str) -> str | None:
    match = re.search(r"caso ([^?]+)", raw_query, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip(" ?.")
    return None


def _clean_entity(value: str) -> str:
    if not value:
        return value
    tokens = value.strip(" ?.").split()
    while tokens and tokens[0].lower() in PRODUCT_PREFIX_STOPWORDS:
        tokens.pop(0)
    return " ".join(tokens)


def _normalize(value: str) -> str:
    return value.strip().lower() if value else ""
