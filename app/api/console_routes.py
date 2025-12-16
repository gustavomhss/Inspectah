from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

try:  # pragma: no cover
    from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Depends = None  # type: ignore
    Query = None  # type: ignore

from app.agents import service
from app.agents.models import (
    AgentInstructionVersion,
    AgentKBRef,
    AgentLayer,
    AgentProfile,
    AgentRole,
    AgentStatus,
)
from app.agents.repository import AgentsRepository
from app.agents.schemas import (
    AgentInstructionVersionCreate,
    AgentInstructionVersionRead,
    AgentProfileCreate,
    AgentProfileRead,
    AgentProfileUpdate,
    ModelUpgradePolicySchema,
)


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

    @router.post("/agents", response_model=AgentProfileRead, status_code=status.HTTP_201_CREATED)
    def create_agent(payload: AgentProfileCreate, repo: AgentsRepository = Depends(_agents_repo)):
        kb_refs = [AgentKBRef(**kb.model_dump()) for kb in payload.kb_refs]
        agent = AgentProfile(
            id=service._gen_id("agent"),
            name=payload.name,
            description=payload.description,
            instructions=payload.instructions,
            role=payload.role,
            layer=payload.layer,
            model_name=payload.model_name,
            recommended_model_name=payload.recommended_model_name,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            top_p=payload.top_p,
            status=payload.status,
            kb_refs=kb_refs,
            created_by=payload.created_by,
            last_modified_by=payload.created_by,
        )
        try:
            service.create_agent_profile(repo, agent)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return AgentProfileRead.model_validate(agent.__dict__)

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
        except (json.JSONDecodeError, IOError, OSError) as exc:
            logger.warning("Failed to load console agents flow from %s: %s", FLOW_PATH, exc)
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
        except Exception:  # pragma: no cover
            logger.exception("Failed to save console agents flow to %s", FLOW_PATH)
            raise HTTPException(
                status_code=500,
                detail="Erro ao salvar fluxo de agentes. Verifique os logs do servidor.",
            )

    @router.get("/agents/{agent_id}", response_model=AgentProfileRead)
    def agent_detail(agent_id: str, repo: AgentsRepository = Depends(_agents_repo)):
        agent = repo.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return AgentProfileRead.model_validate(agent.__dict__)

    @router.put("/agents/{agent_id}", response_model=AgentProfileRead)
    def update_agent(agent_id: str, payload: AgentProfileUpdate, repo: AgentsRepository = Depends(_agents_repo)):
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        try:
            updated = service.update_agent_profile(repo, agent_id, updates)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if not updated:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return AgentProfileRead.model_validate(updated.__dict__)

    @router.get("/agents/{agent_id}/instructions", response_model=list[AgentInstructionVersionRead])
    def list_versions(agent_id: str, repo: AgentsRepository = Depends(_agents_repo)):
        versions: list[AgentInstructionVersion] = repo.list_instruction_versions(agent_id)
        return [AgentInstructionVersionRead.model_validate(v.__dict__) for v in versions]

    @router.post("/agents/{agent_id}/instructions", response_model=AgentInstructionVersionRead, status_code=status.HTTP_201_CREATED)
    def add_version(agent_id: str, payload: AgentInstructionVersionCreate, repo: AgentsRepository = Depends(_agents_repo)):
        version = service.add_instruction_version(
            repo=repo,
            agent_id=agent_id,
            instructions=payload.instructions,
            changelog=payload.changelog,
            model_name=payload.model_name,
            temperature=payload.temperature,
            max_tokens=payload.max_tokens,
            top_p=payload.top_p,
            kb_snapshot=[AgentKBRef(**kb.model_dump()) for kb in payload.kb_snapshot] if payload.kb_snapshot else None,
            author=payload.created_by,
        )
        if not version:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return AgentInstructionVersionRead.model_validate(version.__dict__)

    @router.get("/agents/policies/model-upgrades", response_model=ModelUpgradePolicySchema)
    def get_model_upgrade_policy(repo: AgentsRepository = Depends(_agents_repo)):
        policy = repo.get_model_policy()
        return ModelUpgradePolicySchema.model_validate(policy.__dict__)

else:  # pragma: no cover
    router = None
