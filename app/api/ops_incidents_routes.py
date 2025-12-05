from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ops.incidents import Incident, IncidentService, IncidentSeverity, IncidentState

router = APIRouter(prefix="/api/ops/incidents", tags=["ops_incidents"])
service = IncidentService()


@router.post("")
def create_incident(payload: dict):
    try:
        incident = Incident(
            id=payload["id"],
            title=payload["title"],
            description=payload.get("description", ""),
            severity=payload.get("severity", IncidentSeverity.MEDIUM),
            component_id=payload.get("component_id"),
            slo_ids=payload.get("slo_ids") or [],
        )
        service.create_incident(incident)
        return incident.__dict__
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=f"campo obrigatório ausente: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{incident_id}")
def get_incident(incident_id: str):
    incident = service.get(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="incidente não encontrado")
    return incident.__dict__


@router.post("/{incident_id}/transition")
def transition_incident(incident_id: str, payload: dict):
    try:
        new_state = payload["new_state"]
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="new_state obrigatório") from exc
    try:
        incident = service.transition(incident_id, new_state)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return incident.__dict__
