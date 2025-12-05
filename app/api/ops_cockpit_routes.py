from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.flows.service import FlowService
from app.ops.components import load_components_map
from app.ops.incidents import IncidentService
from app.ops.slo_evaluator import evaluate_slos

router = APIRouter(prefix="/api/ops/cockpit", tags=["ops_cockpit"])
incident_service = IncidentService()
flow_service = FlowService()


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
    flows = []
    try:
        flows = [
            {
                "id": f.id,
                "slug": f.slug,
                "domain": f.domain,
                "estado": f.estado,
                "flow_version_id": f.flow_version_id,
                "active_version_id": f.active_version_id,
                "test_version_id": f.test_version_id,
            }
            for f in flow_service.list_flows()
        ]
    except Exception:
        flows = []
    return {
        "components": len(comps),
        "components_list": comps,
        "incidents": len(incs),
        "incidents_list": incs,
        "slos": slos,
        "flows": len(flows),
        "flows_list": flows,
    }


@router.get("/flows")
def flows():
    comps = {c.id: c for c in load_components_map()}
    slo_status_map = {s["slo_id"]: s.get("status", "UNKNOWN") for s in evaluate_slos()}
    flows = []
    for f in flow_service.list_flows():
        comp_key = f"flow_{f.slug}"
        comp = comps.get(comp_key)
        slos = comp.slos if comp else []
        flows.append(
            {
                "id": f.id,
                "slug": f.slug,
                "domain": f.domain,
                "estado": f.estado,
                "flow_version_id": f.flow_version_id,
                "active_version_id": f.active_version_id,
                "test_version_id": f.test_version_id,
                "component_id": comp.id if comp else None,
                "slos": [
                    {"id": slo, "status": slo_status_map.get(slo, "UNKNOWN")}
                    for slo in slos  # type: ignore[arg-type]
                ],
            }
        )
    return flows
