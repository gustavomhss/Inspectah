"""Debunker v0 runner used throughout Sprint 12."""
from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


Decision = Dict[str, object]


def evaluate_event(event: Dict[str, object], case_context: Dict[str, object] | None = None) -> Decision:
    """Evaluate a single normalized event using heuristics compatible with Debunker v0."""

    domain = event.get("dominio")
    if domain == "obra_publica":
        decision, rationale = _evaluate_obra_publica(event)
    elif domain == "evento_climatico":
        decision, rationale = _evaluate_evento_climatico(event)
    else:
        decision, rationale = ("incerto", "Domínio ainda não calibrado, manter incerto")

    return {
        "event_id": event.get("id_evento"),
        "case_id": event.get("case_id") or event.get("case_key"),
        "decision": decision,
        "rationale": rationale,
        "domain": domain,
        "case_context": case_context or {},
    }


def evaluate_batch(events: Iterable[Dict[str, object]]) -> List[Decision]:
    """Evaluate a batch of normalized events."""

    return [evaluate_event(event) for event in events]


def summarize_decisions(decisions: List[Decision]) -> Dict[str, object]:
    """Return coverage/aggregation helpers for G3."""

    total = len(decisions)
    by_decision: Dict[str, int] = {}
    for decision in decisions:
        by_decision[decision["decision"]] = by_decision.get(decision["decision"], 0) + 1
    return {
        "total": total,
        "by_decision": by_decision,
    }


def _evaluate_obra_publica(event: Dict[str, object]) -> Tuple[str, str]:
    payload = event.get("payload", {})
    status = str(event.get("tipo_evento") or payload.get("status", "")).lower()
    resumo = (event.get("resumo") or "").lower()
    if "denuncia" in resumo or "paralisa" in resumo:
        return "suspeito", "Relato indica denúncia/paralisação de obra."
    if "pagamento" in status or "emp" in status:
        return "aceito", "Atualização financeira normal."
    if "relatorio" in status:
        return "incerto", "Relatório de progresso requer validação manual."
    return "aceito", "Evento de rotina em obra pública."


def _evaluate_evento_climatico(event: Dict[str, object]) -> Tuple[str, str]:
    metadata = event.get("metadata", {})
    nivel = str(metadata.get("nivel", "incerto")).lower()
    if nivel in {"vermelho"}:
        return "suspeito", "Alerta climático crítico (nível vermelho)."
    if nivel == "laranja":
        return "incerto", "Alerta nível laranja requer monitoramento adicional."
    return "aceito", "Alertas abaixo de laranja considerados informativos."


__all__ = ["Decision", "evaluate_event", "evaluate_batch", "summarize_decisions"]
