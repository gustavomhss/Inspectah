from __future__ import annotations

from typing import List, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Depends, HTTPException, Query, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    Depends = None  # type: ignore[misc]
    Query = None  # type: ignore[misc]
    status = None  # type: ignore[misc]

from app.flows.models import FlowExecutionStatus, FlowState
from app.flows.schemas import (
    FlowCreateFromTemplateRequest,
    FlowCreateFromTemplateResponse,
    FlowExecutionDetailRead,
    FlowExecutionRead,
    FlowListItem,
    FlowRead,
    FlowReplaceAgentRequest,
    FlowReprocessRequest,
    FlowStepExecutionRead,
    FlowStepRead,
    FlowUpdateStateRequest,
)
from app.flows.service import FlowService


def _service() -> FlowService:
    return FlowService()


def _to_flow_read(flow, steps=None) -> FlowRead:
    steps = steps or []
    return FlowRead(
        id=flow.id,
        nome=flow.nome,
        slug=flow.slug,
        tipo_entrada=flow.tipo_entrada,
        estado=flow.estado,
        template_origem_id=flow.template_origem_id,
        percentual_teste=flow.percentual_teste,
        metadata=flow.metadata,
        created_at=flow.created_at,
        updated_at=flow.updated_at,
        steps=[
            FlowStepRead.model_validate(
                {
                    "id": s.id,
                    "flow_id": s.flow_id,
                    "ordem": s.ordem,
                    "tipo_etapa": s.tipo_etapa,
                    "agent_role": s.agent_role,
                    "agent_binding": s.agent_binding,
                    "config": s.config,
                    "flags": s.flags,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                }
            )
            for s in steps
        ],
    )


if APIRouter is not None:  # pragma: no cover

    router = APIRouter(prefix="/api/flows", tags=["flows"])

    @router.get("", response_model=List[FlowListItem])
    def list_flows(
        tipo_entrada: Optional[str] = Query(None),
        estado: Optional[FlowState] = Query(None),
        service: FlowService = Depends(_service),
    ):
        flows = service.list_flows()
        if tipo_entrada:
            flows = [f for f in flows if f.tipo_entrada == tipo_entrada]
        if estado:
            flows = [f for f in flows if f.estado == estado]
        return [
            FlowListItem(
                id=f.id,
                nome=f.nome,
                slug=f.slug,
                tipo_entrada=f.tipo_entrada,
                estado=f.estado,
                template_origem_id=f.template_origem_id,
                percentual_teste=f.percentual_teste,
                metadata=f.metadata,
                created_at=f.created_at,
                updated_at=f.updated_at,
            )
            for f in flows
        ]

    @router.get("/templates")
    def list_templates(service: FlowService = Depends(_service)):
        return [
            {
                "id": t.id,
                "slug": t.slug,
                "versao": t.versao,
                "tipo_entrada": t.tipo_entrada,
                "estrutura": t.estrutura,
                "ativo": t.ativo,
                "metadata": t.metadata,
            }
            for t in service.list_templates()
        ]

    @router.get("/{flow_id}", response_model=FlowRead)
    def get_flow(flow_id: str, service: FlowService = Depends(_service)):
        flow = service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Fluxo não encontrado")
        steps = service.list_steps(flow_id)
        return _to_flow_read(flow, steps=steps)

    @router.post("/from_template", response_model=FlowCreateFromTemplateResponse, status_code=status.HTTP_201_CREATED)
    def create_from_template(payload: FlowCreateFromTemplateRequest, service: FlowService = Depends(_service)):
        try:
            flow = service.create_flow_from_template(
                payload.template_slug,
                payload.nome,
                payload.slug,
                payload.bindings,
                payload.metadata,
                payload.percentual_teste,
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        steps = service.list_steps(flow.id)
        return _to_flow_read(flow, steps=steps)

    @router.post("/{flow_id}/state", response_model=FlowRead)
    def update_state(flow_id: str, payload: FlowUpdateStateRequest, service: FlowService = Depends(_service)):
        try:
            flow = service.set_flow_state(flow_id, payload.novo_estado, percentual_teste=payload.percentual_teste)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        steps = service.list_steps(flow_id)
        return _to_flow_read(flow, steps=steps)

    @router.post("/{flow_id}/replace_agent", response_model=FlowRead)
    def replace_agent(flow_id: str, payload: FlowReplaceAgentRequest, service: FlowService = Depends(_service)):
        try:
            service.replace_agent_for_step(flow_id, payload.step_id, payload.agent_binding)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        steps = service.list_steps(flow_id)
        flow = service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Fluxo não encontrado")
        return _to_flow_read(flow, steps=steps)

    @router.get("/{flow_id}/executions", response_model=List[FlowExecutionRead])
    def list_executions(
        flow_id: str,
        limit: int = Query(20, ge=1, le=100),
        service: FlowService = Depends(_service),
    ):
        flow = service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Fluxo não encontrado")
        execs = service.list_executions(flow_id, limit=limit)
        return [
            FlowExecutionRead(
                id=e.id,
                flow_id=e.flow_id,
                item_id=e.item_id,
                tipo_entrada=e.tipo_entrada,
                status=e.status,
                started_at=e.started_at,
                finished_at=e.finished_at,
                erro_resumo=e.erro_resumo,
                metadata=e.metadata,
            )
            for e in execs
        ]

    @router.get("/{flow_id}/executions/{execution_id}", response_model=FlowExecutionDetailRead)
    def execution_detail(flow_id: str, execution_id: str, service: FlowService = Depends(_service)):
        flow = service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Fluxo não encontrado")
        execution = service.get_execution(execution_id)
        if not execution or execution.flow_id != flow_id:
            raise HTTPException(status_code=404, detail="Execução não encontrada")
        steps = service.list_step_executions(execution_id)
        return FlowExecutionDetailRead(
            id=execution.id,
            flow_id=execution.flow_id,
            item_id=execution.item_id,
            tipo_entrada=execution.tipo_entrada,
            status=execution.status,
            started_at=execution.started_at,
            finished_at=execution.finished_at,
            erro_resumo=execution.erro_resumo,
            metadata=execution.metadata,
            steps=[
                FlowStepExecutionRead(
                    id=s.id,
                    flow_execution_id=s.flow_execution_id,
                    step_id=s.step_id,
                    status=s.status,
                    started_at=s.started_at,
                    finished_at=s.finished_at,
                    output_resumo=s.output_resumo,
                    erro_resumo=s.erro_resumo,
                    raw_ref=s.raw_ref,
                )
                for s in steps
            ],
        )

    @router.post("/{flow_id}/reprocess")
    def reprocess(flow_id: str, payload: FlowReprocessRequest, service: FlowService = Depends(_service)):
        try:
            result = service.reprocess_items(
                flow_id,
                criteria=payload.criteria.model_dump(),
                max_items=payload.criteria.max_items or 50,
            )
            return {
                "operation_id": result.id,
                "flow_id": result.flow_id,
                "status": result.resultado,
                "payload": result.payload,
                "created_at": result.created_at,
            }
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

else:  # pragma: no cover
    router = None
