from __future__ import annotations

import logging
from typing import List, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Depends, HTTPException, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Depends = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    status = None  # type: ignore[misc]

from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowConfigOut, AgentFlowStepOut
from app.agents.flows.service import AgentFlowService
from app.agents.flows.validator import AgentFlowValidationError

logger = logging.getLogger("agent_flows_admin")


def get_service() -> AgentFlowService:
    return AgentFlowService()


def _to_schema(flow) -> AgentFlowConfigOut:
    steps = [
        AgentFlowStepOut.model_validate(
            {
                "id": s.id,
                "flow_id": s.flow_id,
                "position": s.position,
                "agent_role": s.agent_role,
                "params": s.params,
                "required": s.required,
                "can_fail_soft": s.can_fail_soft,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
        )
        for s in flow.steps
    ]
    return AgentFlowConfigOut.model_validate(
        {
            "id": flow.id,
            "domain_key": flow.domain_key,
            "name": flow.name,
            "description": flow.description,
            "is_active": flow.is_active,
            "change_reason": flow.change_reason,
            "created_at": flow.created_at,
            "updated_at": flow.updated_at,
            "created_by": flow.created_by,
            "updated_by": flow.updated_by,
            "steps": steps,
        }
    )


if APIRouter is not None:  # pragma: no cover

    router = APIRouter(prefix="/admin/agent-flows", tags=["admin-agent-flows"])

    @router.get("", response_model=List[AgentFlowConfigOut])
    def list_flows(service: AgentFlowService = Depends(get_service)):
        flows = service.list_flows()
        return [_to_schema(f) for f in flows]

    @router.get("/{flow_id}", response_model=AgentFlowConfigOut)
    def get_flow(flow_id: str, service: AgentFlowService = Depends(get_service)):
        flow = service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        return _to_schema(flow)

    @router.get("/by-domain/{domain_key}", response_model=AgentFlowConfigOut)
    def get_flow_by_domain(domain_key: str, service: AgentFlowService = Depends(get_service)):
        flow = service.get_flow_by_domain(domain_key)
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        return _to_schema(flow)

    @router.post("", response_model=AgentFlowConfigOut, status_code=status.HTTP_201_CREATED)
    def create_flow(payload: AgentFlowConfigIn, service: AgentFlowService = Depends(get_service)):
        try:
            flow = service.create_flow(payload)
            logger.info(
                "agent_flow_created",
                extra={"domain_key": flow.domain_key, "flow_id": flow.id, "actor": payload.created_by},
            )
            return _to_schema(flow)
        except AgentFlowValidationError as exc:
            raise HTTPException(status_code=422, detail={"errors": exc.errors})
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.put("/{flow_id}", response_model=AgentFlowConfigOut)
    def update_flow(flow_id: str, payload: AgentFlowConfigIn, service: AgentFlowService = Depends(get_service)):
        try:
            flow = service.update_flow(flow_id, payload)
            logger.info(
                "agent_flow_updated",
                extra={"domain_key": flow.domain_key, "flow_id": flow.id, "actor": payload.updated_by or payload.created_by},
            )
            return _to_schema(flow)
        except AgentFlowValidationError as exc:
            raise HTTPException(status_code=422, detail={"errors": exc.errors})
        except ValueError as exc:
            message = str(exc)
            if "not found" in message.lower():
                raise HTTPException(status_code=404, detail=message)
            raise HTTPException(status_code=400, detail=message)

    @router.delete("/{flow_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_flow(flow_id: str, service: AgentFlowService = Depends(get_service)):
        flow = service.get_flow(flow_id)
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        service.delete_flow(flow_id)
        logger.info("agent_flow_deleted", extra={"domain_key": flow.domain_key, "flow_id": flow.id})
        return None

else:  # pragma: no cover
    router = None
