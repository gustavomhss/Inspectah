from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from typing import Dict, List, Union

from app.sources.models import Source, SourceState
from app.sources.schemas import SourceCreate, SourceUpdate

LAB_ENDPOINT = "https://example.com/rss"
_NEWS_DEFAULT_THEME = "news"


def _looks_like_rss(endpoint: str | None) -> bool:
    if not endpoint:
        return False
    lowered = endpoint.lower()
    return lowered.endswith(".rss") or "/rss" in lowered


def _normalize_base_fields(data: Dict[str, object]) -> Dict[str, object]:
    normalized = deepcopy(data)
    source_type = normalized.get("type")
    endpoint = normalized.get("endpoint") or normalized.get("url_base")
    fmt = normalized.get("format")

    if source_type == "news_rss" or _looks_like_rss(str(endpoint)):
        normalized["format"] = "rss"
    # não force formatos para tipos de API/dataset, apenas mantenha coerência mínima
    if source_type == "science_dataset" and fmt not in (None, "csv"):
        normalized["format"] = "csv"

    if source_type == "news_rss":
        if not normalized.get("themes"):
            normalized["themes"] = [_NEWS_DEFAULT_THEME]
        if not normalized.get("info_types"):
            normalized["info_types"] = [_NEWS_DEFAULT_THEME]

    return normalized


def _apply_lab_rules(data: Dict[str, object]) -> Dict[str, object]:
    normalized = deepcopy(data)
    endpoint = normalized.get("endpoint") or normalized.get("url_base")
    if str(endpoint) != LAB_ENDPOINT:
        return normalized

    meta = dict(normalized.get("meta") or {})
    meta.setdefault("lab_source", True)
    normalized["meta"] = meta
    if not normalized.get("category") or normalized.get("category") == "official":
        normalized["category"] = "internal_test"
    return normalized


def normalize_source_payload(payload: Union[SourceCreate, SourceUpdate]) -> Union[SourceCreate, SourceUpdate]:
    """Normaliza campos antes de persistir uma fonte (criação/edição via API)."""
    data = payload.model_dump(exclude_none=True, by_alias=True)
    data = _normalize_base_fields(data)
    data = _apply_lab_rules(data)
    return payload.model_copy(update=data)


def normalize_source_model(source: Source) -> Source:
    """Normaliza uma instância de Source já carregada do banco."""
    data = _normalize_base_fields(source.__dict__)
    data = _apply_lab_rules(data)

    new_state = data.get("state", source.state)
    if str(data.get("endpoint")) == LAB_ENDPOINT:
        # fontes de laboratório não devem permanecer ACTIVE
        state_enum = new_state if isinstance(new_state, SourceState) else SourceState(new_state)
        if state_enum == SourceState.ACTIVE:
            data["state"] = SourceState.PROPOSED
            data.setdefault("state_reason", "Fonte de laboratório; desativada para evitar execução automática.")

    return replace(
        source,
        format=data.get("format", source.format),
        category=data.get("category", source.category),
        themes=data.get("themes", source.themes),
        info_types=data.get("info_types", source.info_types),
        meta=data.get("meta", source.meta),
        state=data.get("state", source.state),
        state_reason=data.get("state_reason", source.state_reason),
    )


def is_lab_endpoint(endpoint: str | None) -> bool:
    return str(endpoint) == LAB_ENDPOINT


__all__ = ["normalize_source_payload", "normalize_source_model", "is_lab_endpoint", "LAB_ENDPOINT"]
