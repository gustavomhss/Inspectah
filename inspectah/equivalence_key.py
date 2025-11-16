"""Função determinística de equivalence_key."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional


def _normalize_token(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_")
    allowed = [ch for ch in normalized if ch.isalnum() or ch in {"_", "-"}]
    return "".join(allowed)


def _normalize_date(value: Optional[str]) -> str:
    if not value:
        return "undated"
    parsed = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(parsed)
    except ValueError:
        return "undated"
    return dt.strftime("%Y%m%d")


def generate_equivalence_key(
    *,
    declared_metric: str,
    declared_subject: Optional[str] = None,
    published_at: Optional[str] = None,
    entities: Optional[Iterable[str]] = None,
) -> str:
    """Gera chave estável independente da fonte.

    A chave inclui métrica, sujeito (se houver), data e até duas entidades
    adicionais para desambiguar casos complexos.
    """

    if not declared_metric:
        raise ValueError("declared_metric é obrigatório")

    metric_token = _normalize_token(declared_metric)
    subject_token = _normalize_token(declared_subject or "na")
    date_token = _normalize_date(published_at)

    entity_tokens: list[str] = []
    if entities:
        seen: list[str] = []
        for entity in entities:
            if not entity:
                continue
            token = _normalize_token(entity)
            if token and token not in seen:
                seen.append(token)
        entity_tokens = sorted(seen)[:2]

    parts = [metric_token, subject_token, date_token]
    if entity_tokens:
        parts.extend(entity_tokens)

    return "__".join(parts)
