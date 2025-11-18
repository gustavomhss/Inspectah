from __future__ import annotations

from typing import List

from . import storage
from .models import Item, ParsedQuery
from .query_types import normalize_query_type

DEFAULT_LIMIT_PER_SOURCE = 10


def search_internal(parsed: ParsedQuery, limit_per_source: int = DEFAULT_LIMIT_PER_SOURCE) -> List[Item]:
    canonical_type = normalize_query_type(parsed.query_type)
    if canonical_type not in {"preco_medio", "comparacao_simples", "checagem_factual"}:
        return []
    filters = dict(parsed.filters)
    filters.setdefault("source_types", [])
    return storage.list_items_by_filter(filters=filters, limit_per_source=limit_per_source)
