"""Adapter between Sprint 12 pipeline and the Truth-DB/Guardião."""
from __future__ import annotations

from pathlib import Path
from typing import Dict


class _TruthDBState:
    def __init__(self) -> None:
        self.events: Dict[str, Dict[str, object]] = {}
        self.cases: Dict[str, Dict[str, object]] = {}

    def reset(self) -> None:
        self.events.clear()
        self.cases.clear()


_STATE = _TruthDBState()


def register_event_for_case(case_id: str, normalized_event: Dict[str, object], decision: Dict[str, object]) -> Dict[str, object]:
    """Persist an event as if it had gone through o Guardião."""

    event_id = normalized_event.get("id_evento")
    record = {
        "event_id": event_id,
        "case_id": case_id,
        "dominio": normalized_event.get("dominio"),
        "decision": decision.get("decision"),
        "rationale": decision.get("rationale"),
        "timestamp": normalized_event.get("event_timestamp"),
        "payload": normalized_event.get("payload"),
    }
    _STATE.events[event_id] = record
    case_entry = _STATE.cases.setdefault(case_id, {"case_id": case_id, "events": []})
    case_entry["events"].append(record)
    return record


def apply_debunker_decision(event_id: str, decision: Dict[str, object]) -> None:
    """Atualiza a decisão registrada para um evento."""

    record = _STATE.events.get(event_id)
    if not record:
        return
    record["decision"] = decision.get("decision", record.get("decision"))
    record["rationale"] = decision.get("rationale", record.get("rationale"))


def get_case_snapshot(case_id: str) -> Dict[str, object]:
    """Return a snapshot of the case/timeline required by Explorer v0."""

    snapshot = _STATE.cases.get(case_id, {"case_id": case_id, "events": []})
    return {"case_id": snapshot["case_id"], "events": list(snapshot.get("events", []))}


def export_state(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {"cases": _STATE.cases, "events": _STATE.events}
    path.write_text(_json_dumps(snapshot), encoding="utf-8")


def get_state_snapshot() -> Dict[str, object]:
    return {"cases": _STATE.cases, "events": _STATE.events}


def reset_state() -> None:
    _STATE.reset()


def _json_dumps(payload: object) -> str:
    import json

    return json.dumps(payload, indent=2, ensure_ascii=False)


__all__ = [
    "register_event_for_case",
    "apply_debunker_decision",
    "get_case_snapshot",
    "export_state",
    "get_state_snapshot",
    "reset_state",
]
