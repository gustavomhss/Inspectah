"""Timeline projection for Sprint 12 cases."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


def _parse_ts(value: str | None) -> str:
    return value or "1970-01-01T00:00:00Z"


@dataclass
class TimelineEvent:
    """Simplified event view exposed to Explorer v0."""

    id_evento: str
    id_caso: str
    timestamp: str
    titulo: str
    status_debunker: str
    fonte: str
    resumo: str
    tipo_evento: str
    rationale: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class TimelineService:
    """Append-only timeline projection with invariants enforcement."""

    def __init__(self) -> None:
        self._events: Dict[str, List[TimelineEvent]] = {}
        self._event_ids: set[str] = set()

    def reset(self) -> None:
        self._events.clear()
        self._event_ids.clear()

    def append_event(self, case_id: str, normalized_event: Dict[str, object], decision: Dict[str, object]) -> None:
        event_id = normalized_event.get("id_evento")
        if not event_id:
            return
        if event_id in self._event_ids:
            return
        self._event_ids.add(event_id)
        timeline_event = TimelineEvent(
            id_evento=event_id,
            id_caso=case_id,
            timestamp=_parse_ts(normalized_event.get("event_timestamp")),
            titulo=normalized_event.get("titulo", "Evento"),
            status_debunker=decision.get("decision", "incerto"),
            fonte=normalized_event.get("source_id", "desconhecida"),
            resumo=normalized_event.get("resumo", ""),
            tipo_evento=normalized_event.get("tipo_evento", "atualizacao"),
            rationale=decision.get("rationale", ""),
        )
        bucket = self._events.setdefault(case_id, [])
        bucket.append(timeline_event)
        bucket.sort(key=lambda evt: evt.timestamp)

    def list_events(self, case_id: str) -> List[TimelineEvent]:
        return list(self._events.get(case_id, []))

    def export_snapshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        snapshot = {case_id: [evt.to_dict() for evt in events] for case_id, events in self._events.items()}
        path.write_text(_json_dumps(snapshot), encoding="utf-8")

    def integrity_ratio(self) -> Tuple[float, List[str]]:
        violations: List[str] = []
        total_events = sum(len(events) for events in self._events.values())
        for case_id, events in self._events.items():
            timestamps = [evt.timestamp for evt in events]
            if timestamps != sorted(timestamps):
                violations.append(f"I3 violada: timeline fora de ordem para {case_id}")
            seen_ids = set()
            for evt in events:
                if evt.id_evento in seen_ids:
                    violations.append(f"I1 violada: duplicata {evt.id_evento} em {case_id}")
                seen_ids.add(evt.id_evento)
        ratio = 1.0 if total_events == 0 else (total_events - len(violations)) / total_events
        return ratio, violations

    def to_dict(self) -> Dict[str, List[Dict[str, object]]]:
        return {case_id: [evt.to_dict() for evt in events] for case_id, events in self._events.items()}


def _json_dumps(payload: object) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)


DEFAULT_TIMELINE_SERVICE = TimelineService()


def validate_timeline_snapshot(snapshot: Dict[str, List[Dict[str, object]]]) -> Dict[str, object]:
    """Validate a serialized snapshot for gate G4."""

    violations: List[str] = []
    total_events = 0
    seen_events: set[str] = set()
    for case_id, events in snapshot.items():
        timestamps = [evt.get("timestamp") for evt in events]
        total_events += len(events)
        if timestamps != sorted(timestamps):
            violations.append(f"I3 violada: ordem cronológica inconsistente para {case_id}")
        for evt in events:
            event_id = evt.get("id_evento")
            if event_id in seen_events:
                violations.append(f"I1 violada: evento {event_id} aparece em múltiplas timelines")
            seen_events.add(event_id)
    ratio = 1.0 if total_events == 0 else (total_events - len(violations)) / total_events
    return {"timeline_integrity_ratio": ratio, "violations": violations}
