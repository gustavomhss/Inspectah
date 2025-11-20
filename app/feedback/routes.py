"""Internal feedback routes for Sprint 12."""
from __future__ import annotations

from typing import Any, Dict, Optional

try:  # pragma: no cover
    from fastapi import APIRouter
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]

from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE, VALID_STATUSES


def list_feedbacks(status: Optional[str] = None) -> Dict[str, Any]:
    """Return feedback entries filtered by status."""

    normalized_status = status if status in VALID_STATUSES else None
    entries = DEFAULT_FEEDBACK_SERVICE.list_feedbacks(normalized_status)
    return {
        "status": normalized_status or "todos",
        "items": [entry.to_dict() for entry in entries],
    }


def update_feedback(feedback_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update a feedback status."""

    new_status = payload.get("status")
    if new_status not in VALID_STATUSES:
        raise ValueError("status inválido para feedback")
    entry = DEFAULT_FEEDBACK_SERVICE.update_feedback_status(feedback_id, new_status)
    return {"item": entry.to_dict()}


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/admin", tags=["feedback"], include_in_schema=False)

    @router.get("/feedback")
    def _list_feedbacks_route(status: Optional[str] = None) -> Dict[str, Any]:
        return list_feedbacks(status)

    @router.post("/feedback/{feedback_id}/status")
    def _update_feedback_route(feedback_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return update_feedback(feedback_id, payload)
else:  # pragma: no cover
    router = None


__all__ = ["list_feedbacks", "update_feedback", "router"]
