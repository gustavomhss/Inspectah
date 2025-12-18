"""
S38-BE-050: Ops Dashboard Service

Servico centralizado de dashboard operacional.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Status de saude de componente."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricType(str, Enum):
    """Tipos de metricas."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertSeverity(str, Enum):
    """Severidade de alertas."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ComponentHealth:
    """Saude de um componente."""
    component_id: str
    name: str
    status: HealthStatus
    last_check: datetime
    latency_ms: float
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "name": self.name,
            "status": self.status.value,
            "last_check": self.last_check.isoformat(),
            "latency_ms": self.latency_ms,
            "details": self.details,
            "dependencies": self.dependencies,
        }


@dataclass
class MetricValue:
    """Valor de uma metrica."""
    name: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "unit": self.unit,
        }


@dataclass
class ActiveAlert:
    """Alerta ativo."""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    component: str
    started_at: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "severity": self.severity.value,
            "message": self.message,
            "component": self.component,
            "started_at": self.started_at.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "duration_minutes": (datetime.now(timezone.utc).replace(tzinfo=None) - self.started_at).total_seconds() / 60,
        }


@dataclass
class SLOStatus:
    """Status de um SLO."""
    slo_id: str
    name: str
    target: float  # Target percentage (e.g., 99.9)
    current: float  # Current percentage
    budget_remaining: float  # Error budget remaining
    period_days: int
    in_violation: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slo_id": self.slo_id,
            "name": self.name,
            "target": self.target,
            "current": self.current,
            "budget_remaining": self.budget_remaining,
            "period_days": self.period_days,
            "in_violation": self.in_violation,
        }


@dataclass
class DashboardSnapshot:
    """Snapshot completo do dashboard."""
    snapshot_id: str
    timestamp: datetime
    overall_health: HealthStatus
    components: List[ComponentHealth]
    metrics: List[MetricValue]
    alerts: List[ActiveAlert]
    slos: List[SLOStatus]
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "overall_health": self.overall_health.value,
            "components": [c.to_dict() for c in self.components],
            "metrics": [m.to_dict() for m in self.metrics],
            "alerts": [a.to_dict() for a in self.alerts],
            "slos": [s.to_dict() for s in self.slos],
            "summary": self.summary,
        }


class HealthChecker:
    """Verificador de saude de componentes."""

    def __init__(self):
        self._checks: Dict[str, Callable[[], ComponentHealth]] = {}

    def register(
        self,
        component_id: str,
        name: str,
        check_fn: Callable[[], Dict[str, Any]],
        dependencies: Optional[List[str]] = None,
    ) -> None:
        """Registra verificador de saude."""
        def _wrapped_check() -> ComponentHealth:
            import time
            start = time.time()
            try:
                result = check_fn()
                latency = (time.time() - start) * 1000
                status = HealthStatus(result.get("status", "healthy"))
                return ComponentHealth(
                    component_id=component_id,
                    name=name,
                    status=status,
                    last_check=datetime.now(timezone.utc).replace(tzinfo=None),
                    latency_ms=latency,
                    details=result.get("details", {}),
                    dependencies=dependencies or [],
                )
            except Exception as e:
                latency = (time.time() - start) * 1000
                return ComponentHealth(
                    component_id=component_id,
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    last_check=datetime.now(timezone.utc).replace(tzinfo=None),
                    latency_ms=latency,
                    details={"error": str(e)},
                    dependencies=dependencies or [],
                )

        self._checks[component_id] = _wrapped_check

    def check_all(self) -> List[ComponentHealth]:
        """Executa todas as verificacoes."""
        return [check() for check in self._checks.values()]

    def check_one(self, component_id: str) -> Optional[ComponentHealth]:
        """Verifica um componente."""
        if component_id in self._checks:
            return self._checks[component_id]()
        return None


class MetricsCollector:
    """Coletor de metricas."""

    def __init__(self):
        self._metrics: Dict[str, MetricValue] = {}
        self._collectors: List[Callable[[], List[MetricValue]]] = []

    def register_collector(self, collector: Callable[[], List[MetricValue]]) -> None:
        """Registra coletor de metricas."""
        self._collectors.append(collector)

    def set_metric(
        self,
        name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        labels: Optional[Dict[str, str]] = None,
        unit: str = "",
    ) -> None:
        """Define valor de metrica."""
        key = f"{name}:{','.join(f'{k}={v}' for k, v in (labels or {}).items())}"
        self._metrics[key] = MetricValue(
            name=name,
            metric_type=metric_type,
            value=value,
            timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
            labels=labels or {},
            unit=unit,
        )

    def collect_all(self) -> List[MetricValue]:
        """Coleta todas as metricas."""
        results = list(self._metrics.values())
        for collector in self._collectors:
            try:
                results.extend(collector())
            except Exception as e:
                logger.error(f"Metric collector error: {e}")
        return results


class AlertManager:
    """Gerenciador de alertas."""

    def __init__(self):
        self._alerts: Dict[str, ActiveAlert] = {}

    def fire_alert(
        self,
        name: str,
        severity: AlertSeverity,
        message: str,
        component: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ActiveAlert:
        """Dispara alerta."""
        alert_key = f"{name}:{component}"

        if alert_key in self._alerts:
            return self._alerts[alert_key]

        alert = ActiveAlert(
            alert_id=f"alert_{uuid4().hex[:8]}",
            name=name,
            severity=severity,
            message=message,
            component=component,
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
            metadata=metadata or {},
        )

        self._alerts[alert_key] = alert
        logger.warning(f"Alert fired: {name} [{severity.value}] - {message}")
        return alert

    def resolve_alert(self, name: str, component: str) -> bool:
        """Resolve alerta."""
        alert_key = f"{name}:{component}"
        if alert_key in self._alerts:
            del self._alerts[alert_key]
            return True
        return False

    def acknowledge(
        self,
        alert_id: str,
        acknowledged_by: str,
    ) -> Optional[ActiveAlert]:
        """Reconhece alerta."""
        for alert in self._alerts.values():
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now(timezone.utc).replace(tzinfo=None)
                return alert
        return None

    def get_active(self, severity: Optional[AlertSeverity] = None) -> List[ActiveAlert]:
        """Retorna alertas ativos."""
        alerts = list(self._alerts.values())
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        return sorted(alerts, key=lambda a: a.started_at, reverse=True)


class OpsDashboardService:
    """
    Servico de dashboard operacional.

    Centraliza:
    - Health checks de componentes
    - Coleta de metricas
    - Gerenciamento de alertas
    - Status de SLOs

    Uso:
        dashboard = OpsDashboardService()

        # Registrar health check
        dashboard.health.register(
            "database",
            "PostgreSQL",
            lambda: {"status": "healthy", "details": {"connections": 10}},
        )

        # Obter snapshot
        snapshot = dashboard.get_snapshot()
    """

    def __init__(self):
        self.health = HealthChecker()
        self.metrics = MetricsCollector()
        self.alerts = AlertManager()
        self._slos: List[SLOStatus] = []
        self._snapshot_history: List[DashboardSnapshot] = []
        self._max_history = 100

        # Register default checks
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Registra checks padrao."""
        self.health.register(
            "api",
            "API Server",
            lambda: {"status": "healthy", "details": {"uptime": "ok"}},
        )

    def register_slo(
        self,
        slo_id: str,
        name: str,
        target: float,
        calculator: Callable[[], float],
        period_days: int = 30,
    ) -> None:
        """Registra SLO."""
        # Remove existing if any
        self._slos = [s for s in self._slos if s.slo_id != slo_id]

        current = calculator()
        budget_total = 100.0 - target
        budget_used = max(0, target - current)
        budget_remaining = max(0, budget_total - budget_used)

        slo = SLOStatus(
            slo_id=slo_id,
            name=name,
            target=target,
            current=current,
            budget_remaining=budget_remaining,
            period_days=period_days,
            in_violation=current < target,
        )
        self._slos.append(slo)

    def get_snapshot(self) -> DashboardSnapshot:
        """Gera snapshot completo do dashboard."""
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        # Collect data
        components = self.health.check_all()
        metrics = self.metrics.collect_all()
        alerts = self.alerts.get_active()
        slos = self._slos

        # Calculate overall health
        if any(c.status == HealthStatus.UNHEALTHY for c in components):
            overall = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in components):
            overall = HealthStatus.DEGRADED
        elif components:
            overall = HealthStatus.HEALTHY
        else:
            overall = HealthStatus.UNKNOWN

        # Build summary
        summary = {
            "components_total": len(components),
            "components_healthy": sum(1 for c in components if c.status == HealthStatus.HEALTHY),
            "components_degraded": sum(1 for c in components if c.status == HealthStatus.DEGRADED),
            "components_unhealthy": sum(1 for c in components if c.status == HealthStatus.UNHEALTHY),
            "alerts_total": len(alerts),
            "alerts_critical": sum(1 for a in alerts if a.severity == AlertSeverity.CRITICAL),
            "alerts_error": sum(1 for a in alerts if a.severity == AlertSeverity.ERROR),
            "alerts_warning": sum(1 for a in alerts if a.severity == AlertSeverity.WARNING),
            "slos_total": len(slos),
            "slos_in_violation": sum(1 for s in slos if s.in_violation),
        }

        snapshot = DashboardSnapshot(
            snapshot_id=f"snap_{uuid4().hex[:8]}",
            timestamp=now,
            overall_health=overall,
            components=components,
            metrics=metrics,
            alerts=alerts,
            slos=slos,
            summary=summary,
        )

        # Store in history
        self._snapshot_history.append(snapshot)
        if len(self._snapshot_history) > self._max_history:
            self._snapshot_history = self._snapshot_history[-self._max_history:]

        return snapshot

    def get_component_history(
        self,
        component_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Retorna historico de um componente."""
        history = []
        for snapshot in reversed(self._snapshot_history):
            for comp in snapshot.components:
                if comp.component_id == component_id:
                    history.append({
                        "timestamp": snapshot.timestamp.isoformat(),
                        "status": comp.status.value,
                        "latency_ms": comp.latency_ms,
                    })
                    break
            if len(history) >= limit:
                break
        return history

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Retorna resumo de metricas."""
        metrics = self.metrics.collect_all()

        by_type = {}
        for m in metrics:
            if m.metric_type.value not in by_type:
                by_type[m.metric_type.value] = 0
            by_type[m.metric_type.value] += 1

        return {
            "total_metrics": len(metrics),
            "by_type": by_type,
            "latest": [m.to_dict() for m in metrics[:10]],
        }

    def evaluate_health_dependencies(self) -> Dict[str, List[str]]:
        """Avalia impacto de dependencias na saude."""
        components = self.health.check_all()
        component_map = {c.component_id: c for c in components}

        impacts = {}
        for comp in components:
            if comp.status == HealthStatus.UNHEALTHY:
                affected = []
                for other in components:
                    if comp.component_id in other.dependencies:
                        affected.append(other.component_id)
                if affected:
                    impacts[comp.component_id] = affected

        return impacts


# Global instance
_dashboard: Optional[OpsDashboardService] = None


def get_dashboard() -> OpsDashboardService:
    """Retorna instancia global do dashboard."""
    global _dashboard
    if _dashboard is None:
        _dashboard = OpsDashboardService()
    return _dashboard


def reset_dashboard() -> None:
    """Reset the global dashboard instance. For testing only."""
    global _dashboard
    _dashboard = None
