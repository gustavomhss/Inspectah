from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.ops.components import load_components_map
from app.ops.slo_evaluator import evaluate_slos
from app.ops.incidents import IncidentService

router = APIRouter(prefix="/api/ops/cockpit", tags=["ops_cockpit"])
incident_service = IncidentService()


@router.get("/components")
def list_components():
    comps = load_components_map()
    return [c.__dict__ for c in comps]


@router.get("/incidents")
def list_incidents():
    with incident_service._conn() as conn:
        rows = conn.execute(
            "SELECT id, title, severity, state, component_id, slo_ids, created_at, updated_at FROM ops_incidents"
        ).fetchall()
        conn.commit()
    incidents = []
    for r in rows:
        incidents.append(
            {
                "id": r[0],
                "title": r[1],
                "severity": r[2],
                "state": r[3],
                "component_id": r[4],
                "slo_ids": r[5].split(",") if r[5] else [],
                "created_at": r[6],
                "updated_at": r[7],
            }
        )
    return incidents


@router.get("/overview")
def overview():
    comps = load_components_map()
    incs = list_incidents()
    slos = evaluate_slos()
    return {
        "components": len(comps),
        "incidents": len(incs),
        "slos": slos,
    }
