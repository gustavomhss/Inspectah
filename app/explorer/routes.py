"""Explorer v0 routes wired to Sprint 12 services and snapshots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - FastAPI é opcional para testes locais
    from fastapi import APIRouter, HTTPException, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    status = None  # type: ignore[misc]

from scripts.s12_feedback_service import DEFAULT_FEEDBACK_SERVICE

ROOT_DIR = Path(__file__).resolve().parents[2]
EVIDENCE_G2 = ROOT_DIR / "out" / "evidence" / "S12_G2"
CASES_SNAPSHOT_PATH = EVIDENCE_G2 / "cases_snapshot.json"
TIMELINE_SNAPSHOT_PATH = EVIDENCE_G2 / "timelines_snapshot.json"


def _load_cases() -> List[Dict[str, Any]]:
    if not CASES_SNAPSHOT_PATH.exists():
        return []
    return json.loads(CASES_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def _load_timelines() -> Dict[str, List[Dict[str, Any]]]:
    if not TIMELINE_SNAPSHOT_PATH.exists():
        return {}
    return json.loads(TIMELINE_SNAPSHOT_PATH.read_text(encoding="utf-8"))


def _lookup_case(case_id: str) -> Optional[Dict[str, Any]]:
    for case in _load_cases():
        if case.get("id_caso") == case_id:
            return case
    return None


def _find_event(event_id: str) -> Optional[Dict[str, Any]]:
    timelines = _load_timelines()
    for case_id, events in timelines.items():
        for event in events:
            if event.get("id_evento") == event_id:
                payload = dict(event)
                payload.setdefault("case_id", case_id)
                return payload
    return None


def _filter_cases(query: str) -> List[Dict[str, Any]]:
    entries = _load_cases()
    if not query:
        return entries
    needle = query.lower()
    filtered = []
    for entry in entries:
        haystack = " ".join(
            [
                entry.get("id_caso", ""),
                entry.get("titulo", ""),
                entry.get("descricao", ""),
                entry.get("dominio", ""),
            ]
        ).lower()
        if needle in haystack:
            filtered.append(entry)
    return filtered


def list_cases(query: str = "", limit: int = 25) -> Dict[str, Any]:
    """Return cases that match the user query."""

    cases = _filter_cases(query)
    cases.sort(key=lambda entry: entry.get("updated_at", ""), reverse=True)
    limited = cases[:limit]
    return {
        "query": query,
        "results": limited,
        "total": len(cases),
    }


def get_case(case_id: str) -> Dict[str, Any]:
    """Return a timeline-aware representation of a case."""

    case = _lookup_case(case_id)
    if case is None:
        _raise_not_found(f"Caso {case_id} não encontrado")
    timelines = _load_timelines()
    timeline = timelines.get(case_id, [])
    by_status: Dict[str, int] = {}
    for event in timeline:
        status_key = event.get("status_debunker", "incerto")
        by_status[status_key] = by_status.get(status_key, 0) + 1
    return {
        "case": case,
        "timeline": timeline,
        "stats": {
            "events": len(timeline),
            "by_status": by_status,
        },
    }


def create_case_feedback(case_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record feedback tied to a case."""

    if not payload.get("mensagem"):
        _raise_bad_request("mensagem é obrigatória para feedback")
    case = _lookup_case(case_id)
    if case is None:
        _raise_not_found(f"Caso {case_id} não encontrado")
    feedback = DEFAULT_FEEDBACK_SERVICE.create_feedback_for_case(
        case_id,
        mensagem=payload["mensagem"],
        autor=payload.get("autor"),
        extra={"source": "explorer"},
    )
    return {"status": "registrado", "feedback": feedback.to_dict()}


def create_event_feedback(event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record feedback tied to a timeline event."""

    if not payload.get("mensagem"):
        _raise_bad_request("mensagem é obrigatória para feedback")
    event = _find_event(event_id)
    if event is None:
        _raise_not_found(f"Evento {event_id} não encontrado na timeline")
    feedback = DEFAULT_FEEDBACK_SERVICE.create_feedback_for_event(
        event_id,
        mensagem=payload["mensagem"],
        autor=payload.get("autor"),
        extra={"case_id": event.get("case_id", "")},
    )
    return {"status": "registrado", "feedback": feedback.to_dict()}


def _raise_not_found(message: str) -> None:
    if HTTPException is not None and status is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
    raise KeyError(message)


def _raise_bad_request(message: str) -> None:
    if HTTPException is not None and status is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    raise ValueError(message)


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/explorer", tags=["explorer"])

    @router.get("/cases")
    def _list_cases_route(query: str = "", limit: int = 25) -> Dict[str, Any]:
        return list_cases(query=query, limit=limit)

    @router.get("/cases/{case_id}")
    def _get_case_route(case_id: str) -> Dict[str, Any]:
        return get_case(case_id)

    @router.post("/cases/{case_id}/feedback")
    def _create_case_feedback(case_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return create_case_feedback(case_id, payload)

    @router.post("/events/{event_id}/feedback")
    def _create_event_feedback(event_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return create_event_feedback(event_id, payload)
else:  # pragma: no cover
    router = None


__all__ = [
    "list_cases",
    "get_case",
    "create_case_feedback",
    "create_event_feedback",
    "router",
]
