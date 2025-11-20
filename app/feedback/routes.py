"""Internal feedback routes skeleton for Sprint 12."""
from __future__ import annotations

from typing import Any, Dict, Optional

from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE


def list_feedbacks(status: Optional[str] = None) -> Dict[str, Any]:
    """Return feedback entries filtered by status."""

    entries = DEFAULT_FEEDBACK_SERVICE.list_feedbacks(status)
    return {"items": [entry.__dict__ for entry in entries], "status": status}


def update_feedback(feedback_id: str, status: str) -> Dict[str, Any]:
    """Update a feedback status."""

    entry = DEFAULT_FEEDBACK_SERVICE.update_feedback_status(feedback_id, status)
    return {"item": entry.__dict__}


__all__ = ["list_feedbacks", "update_feedback"]
