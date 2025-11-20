"""Feedback service skeleton for Sprint 12."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Feedback:
    """Represents a feedback entry produced by Explorer v0."""

    id_feedback: str
    id_caso: Optional[str]
    id_evento: Optional[str]
    descricao: str
    status: str = "novo"
    autor: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    meta: Dict[str, str] = field(default_factory=dict)


class FeedbackService:
    """Store and mutate feedback lifecycle for G5/G6 workflows."""

    def __init__(self) -> None:
        self._items: Dict[str, Feedback] = {}

    def create_feedback(self, feedback: Feedback) -> Feedback:
        self._items[feedback.id_feedback] = feedback
        return feedback

    def list_feedbacks(self, status: Optional[str] = None) -> List[Feedback]:
        if status is None:
            return list(self._items.values())
        return [item for item in self._items.values() if item.status == status]

    def update_feedback_status(self, feedback_id: str, status: str) -> Feedback:
        entry = self._items[feedback_id]
        entry.status = status
        return entry


DEFAULT_FEEDBACK_SERVICE = FeedbackService()
