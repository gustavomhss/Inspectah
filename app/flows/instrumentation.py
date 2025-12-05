"""
Instrumentação de fluxos para métricas/logs (G4).
Registra métricas Prometheus e logs estruturados com IDs de correlação.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

try:
    from prometheus_client import Counter, Histogram, generate_latest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback
    class _DummyMetric:
        def __init__(self, *args, **kwargs):
            pass

        def labels(self, **kwargs):
            return self

        def inc(self, value: int = 1):
            return None

        def observe(self, value):
            return None

    Counter = Histogram = _DummyMetric  # type: ignore

    def generate_latest():  # type: ignore
        return b""

from app.flows.models import FlowExecution, FlowStepExecution

logger = logging.getLogger("flows.instrumentation")

# Métricas básicas por execução de fluxo
_exec_total = Counter(
    "inspectah_flow_executions_total",
    "Total de execuções de fluxo",
    ["flow_id", "flow_version_id", "tipo_entrada", "status"],
)
_exec_success = Counter(
    "inspectah_flow_executions_success_total",
    "Total de execuções com sucesso",
    ["flow_id", "flow_version_id", "tipo_entrada"],
)
_exec_failure = Counter(
    "inspectah_flow_executions_failure_total",
    "Total de execuções com falha",
    ["flow_id", "flow_version_id", "tipo_entrada", "error_class"],
)
_exec_latency = Histogram(
    "inspectah_flow_latency_seconds",
    "Latência por execução de fluxo",
    ["flow_id", "flow_version_id", "tipo_entrada"],
)
_policy_violations = Counter(
    "inspectah_flow_policy_violations_total",
    "Total de violações de políticas por fluxo/versão",
    ["flow_id", "flow_version_id"],
)
_rollbacks = Counter(
    "inspectah_flow_rollbacks_total",
    "Total de rollbacks acionados por fluxo/versão",
    ["flow_id", "flow_version_id"],
)
_slo_breaches = Counter(
    "inspectah_flow_slo_breach_total",
    "Total de violações de SLO por fluxo/versão",
    ["flow_id", "flow_version_id", "slo_id"],
)


def _duration_seconds(started_at: datetime, finished_at: Optional[datetime]) -> Optional[float]:
    if not finished_at:
        return None
    return (finished_at - started_at).total_seconds()


def record_flow_execution_started(execution: FlowExecution) -> None:
    logger.info(
        "flow_execution_started",
        extra={
            "flow_id": execution.flow_id,
            "flow_version_id": execution.flow_version_id,
            "exec_fluxo_id": execution.id,
            "operation_id": execution.operation_id,
            "item_id": execution.item_id,
            "tipo_entrada": execution.tipo_entrada,
            "status": execution.status.value,
        },
    )


def record_flow_execution_finished(execution: FlowExecution) -> None:
    status = execution.status.value
    labels = {
        "flow_id": execution.flow_id,
        "flow_version_id": execution.flow_version_id or "unknown",
        "tipo_entrada": execution.tipo_entrada,
    }
    _exec_total.labels(**labels, status=status).inc()
    if status == "concluido":
        _exec_success.labels(**labels).inc()
    else:
        _exec_failure.labels(**labels, error_class=status).inc()
    duration = _duration_seconds(execution.started_at, execution.finished_at)
    if duration is not None:
        _exec_latency.labels(**labels).observe(duration)
    logger.info(
        "flow_execution_finished",
        extra={
            "flow_id": execution.flow_id,
            "flow_version_id": execution.flow_version_id,
            "exec_fluxo_id": execution.id,
            "operation_id": execution.operation_id,
            "item_id": execution.item_id,
            "tipo_entrada": execution.tipo_entrada,
            "status": status,
            "erro_resumo": execution.erro_resumo,
            "duration_seconds": duration,
        },
    )


def record_flow_step_execution(step_exec: FlowStepExecution) -> None:
    logger.info(
        "flow_step_execution",
        extra={
            "flow_id": step_exec.flow_execution_id,
            "exec_fluxo_id": step_exec.flow_execution_id,
            "exec_etapa_id": step_exec.id,
            "step_id": step_exec.step_id,
            "status": step_exec.status.value,
            "output_resumo": step_exec.output_resumo,
            "erro_resumo": step_exec.erro_resumo,
        },
    )


def record_policy_violation(flow_id: str, flow_version_id: Optional[str]) -> None:
    _policy_violations.labels(flow_id=flow_id, flow_version_id=flow_version_id or "unknown").inc()
    logger.warning(
        "flow_policy_violation",
        extra={
            "flow_id": flow_id,
            "flow_version_id": flow_version_id,
        },
    )


def record_rollback(flow_id: str, flow_version_id: Optional[str], operation_id: Optional[str]) -> None:
    _rollbacks.labels(flow_id=flow_id, flow_version_id=flow_version_id or "unknown").inc()
    logger.info(
        "flow_rollback",
        extra={"flow_id": flow_id, "flow_version_id": flow_version_id, "operation_id": operation_id},
    )


def record_slo_breach(flow_id: str, flow_version_id: Optional[str], slo_id: str) -> None:
    _slo_breaches.labels(flow_id=flow_id, flow_version_id=flow_version_id or "unknown", slo_id=slo_id).inc()
    logger.warning(
        "flow_slo_breach",
        extra={"flow_id": flow_id, "flow_version_id": flow_version_id, "slo_id": slo_id},
    )
