"""Adaptadores de KB para agentes (stub na Sprint 23)."""

from __future__ import annotations

from typing import List

from app.agents.models import AgentKBRef


def render_kb_context(kb_refs: List[AgentKBRef]) -> str:
    """Gera um contexto textual simples a partir das refs de KB."""
    parts = []
    for ref in kb_refs:
        parts.append(f"[{ref.kind}] {ref.label} ({ref.path_or_uri})")
    return "\n".join(parts)
