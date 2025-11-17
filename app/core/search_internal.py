from __future__ import annotations

from typing import List

from . import storage
from .models import Item, ParsedQuery

DEFAULT_LIMIT_PER_SOURCE = 10


def search_internal(parsed: ParsedQuery, limit_per_source: int = DEFAULT_LIMIT_PER_SOURCE) -> List[Item]:
    if parsed.query_type not in {
        "agregacao_simples",
        "comparacao_simples",
        "checagem_factual_simples",
    }:
        return []
    filters = dict(parsed.filters)
    filters.setdefault("source_types", [])
    return storage.list_items_by_filter(filters=filters, limit_per_source=limit_per_source)
