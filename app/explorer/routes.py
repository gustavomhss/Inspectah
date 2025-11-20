"""Explorer v0 routes skeleton for Sprint 12."""
from __future__ import annotations

from typing import Any, Dict, Optional

from scripts.s12_case_service import DEFAULT_CASE_SERVICE
from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE, Feedback
from scripts.s12_timeline_service import DEFAULT_TIMELINE_SERVICE


def list_cases(query: Optional[str] = None) -> Dict[str, Any]:
    """Return cases that match the user query (placeholder)."""

    cases = DEFAULT_CASE_SERVICE.search_cases(query or "")
    return {
        "query": query or "",
        "cases": [case.__dict__ for case in cases],
        "note": "Wire actual search logic during Wave 3.",
    }


def get_case(case_id: str) -> Dict[str, Any]:
    """Return a timeline-aware representation of a case (placeholder)."""

    case = DEFAULT_CASE_SERVICE.get_case(case_id)
    events = DEFAULT_TIMELINE_SERVICE.list_events(case_id)
    return {
        "case": case.__dict__ if case else None,
        "timeline": [event.__dict__ for event in events],
        "note": "Wave 3 will fetch snapshots from Truth-DB projections.",
    }


def create_case_feedback(case_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record feedback tied to a case (placeholder)."""

    feedback = Feedback(
        id_feedback=payload.get("id_feedback", f"case-{case_id}"),
        id_caso=case_id,
        id_evento=None,
        descricao=payload.get("descricao", ""),
        autor=payload.get("autor"),
    )
    DEFAULT_FEEDBACK_SERVICE.create_feedback(feedback)
    return {"status": "pending", "id_feedback": feedback.id_feedback}


def create_event_feedback(event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record feedback tied to a timeline event (placeholder)."""

    feedback = Feedback(
        id_feedback=payload.get("id_feedback", f"evento-{event_id}"),
        id_caso=payload.get("id_caso"),
        id_evento=event_id,
        descricao=payload.get("descricao", ""),
        autor=payload.get("autor"),
    )
    DEFAULT_FEEDBACK_SERVICE.create_feedback(feedback)
    return {"status": "pending", "id_feedback": feedback.id_feedback}


__all__ = [
    "list_cases",
    "get_case",
    "create_case_feedback",
    "create_event_feedback",
]
