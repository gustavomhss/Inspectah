"""Timeline projection skeleton for Sprint 12 cases."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class TimelineEvent:
    """Simplified event view exposed to Explorer v0."""

    id_evento: str
    id_caso: str
    timestamp: str
    titulo: str
    status: str
    fonte: str


class TimelineService:
    """Append-only timeline projection placeholder."""

    def __init__(self) -> None:
        self._events: Dict[str, List[TimelineEvent]] = {}

    def append_event(self, event: TimelineEvent) -> None:
        self._events.setdefault(event.id_caso, []).append(event)

    def list_events(self, case_id: str) -> List[TimelineEvent]:
        return list(self._events.get(case_id, []))


DEFAULT_TIMELINE_SERVICE = TimelineService()
