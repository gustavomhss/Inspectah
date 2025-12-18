"""
S38-BE-053: Dashboard API Routes

Endpoints para dashboard operacional.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ops.dashboard_service import (
    AlertSeverity,
    get_dashboard,
    HealthStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


# Request/Response models

class FireAlertRequest(BaseModel):
    """Request para disparar alerta."""
    name: str
    severity: str = Field(description="info, warning, error, critical")
    message: str
    component: str
    metadata: Optional[Dict[str, Any]] = None


class AcknowledgeRequest(BaseModel):
    """Request para reconhecer alerta."""
    acknowledged_by: str


class SetMetricRequest(BaseModel):
    """Request para definir metrica."""
    name: str
    value: float
    metric_type: str = Field(default="gauge", description="counter, gauge, histogram, summary")
    labels: Optional[Dict[str, str]] = None
    unit: str = ""


# Endpoints

@router.get("/snapshot")
async def get_snapshot():
    """
    Retorna snapshot completo do dashboard.

    Inclui:
    - Status geral de saude
    - Componentes
    - Metricas
    - Alertas ativos
    - Status de SLOs
    """
    dashboard = get_dashboard()
    snapshot = dashboard.get_snapshot()
    return snapshot.to_dict()


@router.get("/health")
async def get_health_status():
    """Retorna status de saude dos componentes."""
    dashboard = get_dashboard()
    components = dashboard.health.check_all()

    # Calculate overall
    if any(c.status == HealthStatus.UNHEALTHY for c in components):
        overall = "unhealthy"
    elif any(c.status == HealthStatus.DEGRADED for c in components):
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "overall": overall,
        "components": [c.to_dict() for c in components],
        "total": len(components),
        "healthy": sum(1 for c in components if c.status == HealthStatus.HEALTHY),
        "degraded": sum(1 for c in components if c.status == HealthStatus.DEGRADED),
        "unhealthy": sum(1 for c in components if c.status == HealthStatus.UNHEALTHY),
    }


@router.get("/health/{component_id}")
async def get_component_health(component_id: str):
    """Retorna saude de um componente especifico."""
    dashboard = get_dashboard()
    health = dashboard.health.check_one(component_id)

    if not health:
        raise HTTPException(404, f"Component {component_id} not found")

    return health.to_dict()


@router.get("/health/{component_id}/history")
async def get_component_history(
    component_id: str,
    limit: int = Query(20, le=100),
):
    """Retorna historico de saude de um componente."""
    dashboard = get_dashboard()
    history = dashboard.get_component_history(component_id, limit)
    return {"component_id": component_id, "history": history}


@router.get("/metrics")
async def get_metrics():
    """Retorna metricas coletadas."""
    dashboard = get_dashboard()
    return dashboard.get_metrics_summary()


@router.post("/metrics")
async def set_metric(body: SetMetricRequest):
    """Define valor de uma metrica."""
    from app.ops.dashboard_service import MetricType

    dashboard = get_dashboard()

    try:
        metric_type = MetricType(body.metric_type)
    except ValueError:
        raise HTTPException(400, f"Invalid metric type: {body.metric_type}")

    dashboard.metrics.set_metric(
        name=body.name,
        value=body.value,
        metric_type=metric_type,
        labels=body.labels,
        unit=body.unit,
    )

    return {"success": True, "name": body.name, "value": body.value}


@router.get("/alerts")
async def get_alerts(severity: Optional[str] = Query(None)):
    """Retorna alertas ativos."""
    dashboard = get_dashboard()

    sev = None
    if severity:
        try:
            sev = AlertSeverity(severity)
        except ValueError:
            raise HTTPException(400, f"Invalid severity: {severity}")

    alerts = dashboard.alerts.get_active(sev)
    return {
        "alerts": [a.to_dict() for a in alerts],
        "total": len(alerts),
        "critical": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
        "error": sum(1 for a in alerts if a.severity == AlertSeverity.ERROR),
        "warning": sum(1 for a in alerts if a.severity == AlertSeverity.WARNING),
        "info": sum(1 for a in alerts if a.severity == AlertSeverity.INFO),
    }


@router.post("/alerts")
async def fire_alert(body: FireAlertRequest):
    """Dispara um alerta."""
    dashboard = get_dashboard()

    try:
        severity = AlertSeverity(body.severity)
    except ValueError:
        raise HTTPException(400, f"Invalid severity: {body.severity}")

    alert = dashboard.alerts.fire_alert(
        name=body.name,
        severity=severity,
        message=body.message,
        component=body.component,
        metadata=body.metadata,
    )

    return alert.to_dict()


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, body: AcknowledgeRequest):
    """Reconhece um alerta."""
    dashboard = get_dashboard()
    alert = dashboard.alerts.acknowledge(alert_id, body.acknowledged_by)

    if not alert:
        raise HTTPException(404, f"Alert {alert_id} not found")

    return alert.to_dict()


@router.delete("/alerts/{name}/{component}")
async def resolve_alert(name: str, component: str):
    """Resolve um alerta."""
    dashboard = get_dashboard()
    resolved = dashboard.alerts.resolve_alert(name, component)

    return {"success": resolved, "name": name, "component": component}


@router.get("/slos")
async def get_slos():
    """Retorna status dos SLOs."""
    dashboard = get_dashboard()
    snapshot = dashboard.get_snapshot()

    return {
        "slos": [s.to_dict() for s in snapshot.slos],
        "total": len(snapshot.slos),
        "in_violation": sum(1 for s in snapshot.slos if s.in_violation),
    }


@router.get("/dependencies")
async def get_dependency_impacts():
    """Retorna analise de impacto de dependencias."""
    dashboard = get_dashboard()
    impacts = dashboard.evaluate_health_dependencies()

    return {
        "impacts": impacts,
        "unhealthy_components_count": len(impacts),
    }


@router.get("/summary")
async def get_summary():
    """Retorna resumo executivo do dashboard."""
    dashboard = get_dashboard()
    snapshot = dashboard.get_snapshot()

    return {
        "overall_health": snapshot.overall_health.value,
        "summary": snapshot.summary,
        "timestamp": snapshot.timestamp.isoformat(),
    }
