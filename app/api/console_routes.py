from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Body, Depends, HTTPException, Query
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Depends = None  # type: ignore
    Query = None  # type: ignore

from app.agents.models import AgentLayer, AgentRole, AgentStatus
from app.agents.repository import AgentsRepository
from app.agents.schemas import AgentProfileRead, ModelUpgradePolicySchema


FLOW_PATH = Path("out/runtime/console_agents_flow.json")


def _agents_repo() -> AgentsRepository:
    return AgentsRepository()


if APIRouter is not None:  # pragma: no cover

    router = APIRouter(prefix="/api/console", tags=["console"])

    @router.get("/agents", response_model=List[AgentProfileRead])
    def list_agents(
        layer: Optional[AgentLayer] = Query(None),
        role: Optional[AgentRole] = Query(None),
        status: Optional[AgentStatus] = Query(None, alias="status"),
        repo: AgentsRepository = Depends(_agents_repo),
    ):
        agents = repo.list_agents(layer=layer, role=role, status=status)
        return [AgentProfileRead.model_validate(a.__dict__) for a in agents]

    @router.get("/agents/flow")
    async def get_console_agents_flow():
        """
        Console: retorna o fluxo de agentes salvo em disco.

        - Não consulta serviços fortes.
        - Nunca retorna 404.
        - Em qualquer problema, retorna [] com 200.
        """
        try:
            if not FLOW_PATH.exists():
                return []
            text = FLOW_PATH.read_text(encoding="utf-8")
            if not text.strip():
                return []
            data = json.loads(text)
            if data is None or data == "":
                return []
            return data
        except Exception:
            return []

    @router.put("/agents/flow")
    async def save_console_agents_flow(payload: Any = Body(...)):
        """
        Console: salva o fluxo de agentes em disco.

        - Não valida contra serviços fortes.
        - Grava o JSON bruto em out/runtime/console_agents_flow.json.
        """
        try:
            FLOW_PATH.parent.mkdir(parents=True, exist_ok=True)
            text = json.dumps(payload, ensure_ascii=False, indent=2)
            FLOW_PATH.write_text(text, encoding="utf-8")
            return payload
        except Exception as exc:  # pragma: no cover
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao salvar fluxo de agentes do console: {exc}",
            )

    @router.get("/agents/{agent_id}", response_model=AgentProfileRead)
    def agent_detail(agent_id: str, repo: AgentsRepository = Depends(_agents_repo)):
        agent = repo.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return AgentProfileRead.model_validate(agent.__dict__)

    @router.get("/agents/policies/model-upgrades", response_model=ModelUpgradePolicySchema)
    def get_model_upgrade_policy(repo: AgentsRepository = Depends(_agents_repo)):
        policy = repo.get_model_policy()
        return ModelUpgradePolicySchema.model_validate(policy.__dict__)

else:  # pragma: no cover
    router = None
