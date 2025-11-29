from __future__ import annotations

from typing import List

from .models import Item, ParsedQuery
from . import storage

DEFAULT_LIMIT_PER_SOURCE = 10


def search_internal(parsed: ParsedQuery, limit_per_source: int = DEFAULT_LIMIT_PER_SOURCE) -> List[Item]:
    if parsed.detailed_type not in {
        "preco_medio",
        "comparacao_simples",
        "checagem_factual",
    }:
        return []
    filters = dict(parsed.filters)
    filters.setdefault("source_types", [])
    items = storage.list_items_by_filter(filters=filters, limit_per_source=limit_per_source)
    return items
