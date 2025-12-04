from __future__ import annotations

from typing import Dict, Optional

from app.flows import instrumentation
from app.flows.models import FlowExecutionStatus, FlowStepExecutionStatus
from app.flows.routing_policy import RoutingDecision, select_flow_for_event
from app.flows.service import FlowService


class FlowExecutionEngine:
    def __init__(self, service: Optional[FlowService] = None):
        self.service = service or FlowService()

    def execute_event(self, evento: Dict) -> str:
        decision: RoutingDecision = select_flow_for_event(evento, service=self.service)
        flow = decision.flow
        item_id = evento.get("item_id") or evento.get("id") or "unknown_item"
        exec_obj = self.service.record_execution(flow.id, item_id, flow.tipo_entrada, FlowExecutionStatus.EM_ANDAMENTO)
        instrumentation.record_flow_execution_started(exec_obj)

        steps = self.service.list_steps(flow.id)
        erro: Optional[str] = None
        for step in steps:
            try:
                summary = f"{step.tipo_etapa.value}:{step.agent_role}"
                step_exec = self.service.record_step_execution(
                    exec_obj.id,
                    step.id,
                    FlowStepExecutionStatus.OK,
                    output_resumo=summary,
                )
                instrumentation.record_flow_step_execution(step_exec)
            except Exception as exc:  # pragma: no cover - defensive
                erro = str(exc)
                step_exec = self.service.record_step_execution(
                    exec_obj.id,
                    step.id,
                    FlowStepExecutionStatus.ERRO,
                    erro_resumo=erro,
                )
                instrumentation.record_flow_step_execution(step_exec)
                break

        final_status = FlowExecutionStatus.CONCLUIDO if erro is None else FlowExecutionStatus.FALHOU
        self.service.update_execution_status(exec_obj.id, final_status, erro_resumo=erro)
        exec_obj.status = final_status
        instrumentation.record_flow_execution_finished(exec_obj)
        return exec_obj.id
