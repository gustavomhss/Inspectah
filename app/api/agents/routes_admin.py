from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Depends = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    status = None  # type: ignore[misc]

from app.agents import service
from app.agents.models import (
    AgentCommittee,
    AgentFlowLayer,
    AgentKBRef,
    AgentLayer,
    AgentProfile,
    AgentRole,
    AgentRunStatus,
    AgentStatus,
    CommitteePolicy,
)
from app.agents.repository import AgentsRepository
from app.agents.schemas import (
    AgentCommitteeCreate,
    AgentCommitteeRead,
    AgentInstructionVersionCreate,
    AgentInstructionVersionRead,
    AgentProfileCreate,
    AgentProfileRead,
    AgentProfileUpdate,
    AgentRunRead,
    CommitteeRunRequest,
    AgentFlowLayerCreate,
    AgentFlowLayerRead,
    ModelCatalogSchema,
    ModelUpgradePolicySchema,
)
from app.agents.service import _gen_id


def _to_dict(obj):
    if is_dataclass(obj):
        return asdict(obj)
    return obj.__dict__


def get_repo() -> AgentsRepository:
    return AgentsRepository()


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/admin/agents", tags=["admin-agents"])

    @router.get("", response_model=list[AgentProfileRead])
    def list_agents(
        layer: Optional[AgentLayer] = Query(None),
        role: Optional[AgentRole] = Query(None),
        status_filter: Optional[AgentStatus] = Query(None, alias="status"),
        repo: AgentsRepository = Depends(get_repo),
    ):
        agents = repo.list_agents(layer=layer, role=role, status=status_filter)
        return [AgentProfileRead.model_validate(_to_dict(a)) for a in agents]

    @router.get("/models-catalog", response_model=ModelCatalogSchema)
    def list_models(repo: AgentsRepository = Depends(get_repo)):
        catalog = service.get_model_catalog(repo)
        return ModelCatalogSchema.model_validate(catalog)

    # Flow endpoints
    @router.get("/flow")
    def get_flow(repo: AgentsRepository = Depends(get_repo)):
        return service.get_flow(repo)

    @router.put("/flow")
    def set_flow(payload: Any = Body(...), repo: AgentsRepository = Depends(get_repo)):
        flow_payload = payload if isinstance(payload, list) else []
        try:
            return service.save_flow(flow_payload, repo)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("", response_model=AgentProfileRead, status_code=status.HTTP_201_CREATED)
    def create_agent(payload: AgentProfileCreate, repo: AgentsRepository = Depends(get_repo)):
        kb_refs = [AgentKBRef(**kb.model_dump()) for kb in payload.kb_refs]
        agent = AgentProfile(
            id=_gen_id("agent"),
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
        return AgentProfileRead.model_validate(_to_dict(agent))

    @router.get("/{agent_id}", response_model=AgentProfileRead)
    def get_agent(agent_id: str, repo: AgentsRepository = Depends(get_repo)):
        agent = repo.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentProfileRead.model_validate(_to_dict(agent))

    @router.put("/{agent_id}", response_model=AgentProfileRead)
    def update_agent(agent_id: str, payload: AgentProfileUpdate, repo: AgentsRepository = Depends(get_repo)):
        updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
        try:
            updated = service.update_agent_profile(repo, agent_id, updates)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if not updated:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentProfileRead.model_validate(_to_dict(updated))

    @router.get("/{agent_id}/instructions", response_model=list[AgentInstructionVersionRead])
    def list_versions(agent_id: str, repo: AgentsRepository = Depends(get_repo)):
        versions = repo.list_instruction_versions(agent_id)
        return [AgentInstructionVersionRead.model_validate(_to_dict(v)) for v in versions]

    @router.post("/{agent_id}/instructions", response_model=AgentInstructionVersionRead, status_code=status.HTTP_201_CREATED)
    def add_version(agent_id: str, payload: AgentInstructionVersionCreate, repo: AgentsRepository = Depends(get_repo)):
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
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentInstructionVersionRead.model_validate(_to_dict(version))

    # Committees
    @router.get("/committees", response_model=list[AgentCommitteeRead])
    def list_committees(layer: Optional[AgentLayer] = Query(None), repo: AgentsRepository = Depends(get_repo)):
        committees = repo.list_committees(layer=layer)
        return [AgentCommitteeRead.model_validate(_to_dict(c)) for c in committees]

    @router.post("/committees", response_model=AgentCommitteeRead, status_code=status.HTTP_201_CREATED)
    def create_committee(payload: AgentCommitteeCreate, repo: AgentsRepository = Depends(get_repo)):
        committee = AgentCommittee(
            id=_gen_id("committee"),
            name=payload.name,
            description=payload.description,
            layer=payload.layer,
            primary_agents=payload.primary_agents,
            mediator_agent=payload.mediator_agent,
            policy=CommitteePolicy(**payload.policy.model_dump()),
            status=payload.status,
        )
        service.create_committee(repo, committee)
        return AgentCommitteeRead.model_validate(_to_dict(committee))

    @router.get("/committees/{committee_id}", response_model=AgentCommitteeRead)
    def get_committee(committee_id: str, repo: AgentsRepository = Depends(get_repo)):
        committee = repo.get_committee(committee_id)
        if not committee:
            raise HTTPException(status_code=404, detail="Committee not found")
        return AgentCommitteeRead.model_validate(_to_dict(committee))

    @router.put("/committees/{committee_id}", response_model=AgentCommitteeRead)
    def update_committee(committee_id: str, payload: AgentCommitteeCreate, repo: AgentsRepository = Depends(get_repo)):
        updates = payload.model_dump(exclude_unset=True)
        updated = service.update_committee(repo, committee_id, updates)
        if not updated:
            raise HTTPException(status_code=404, detail="Committee not found")
        return AgentCommitteeRead.model_validate(_to_dict(updated))

    @router.get("/committees/{committee_id}/runs", response_model=list[AgentRunRead])
    def list_runs(committee_id: str, repo: AgentsRepository = Depends(get_repo)):
        runs = repo.list_runs_by_committee(committee_id, limit=20)
        return [AgentRunRead.model_validate(_to_dict(r)) for r in runs]

    @router.post("/committees/{committee_id}/dry-run", response_model=AgentRunRead, status_code=status.HTTP_201_CREATED)
    def dry_run(committee_id: str, payload: CommitteeRunRequest, repo: AgentsRepository = Depends(get_repo)):
        run = service.start_committee_run(repo, committee_id, payload.input_ref, payload.payload)
        if not run:
            raise HTTPException(status_code=404, detail="Committee not found")
        run.status = AgentRunStatus.SUCCESS
        run.result_bundle_ref = "stub://s23/dry-run"
        run.finished_at = datetime.utcnow()
        repo.update_run(run)
        return AgentRunRead.model_validate(_to_dict(run))

    # Model policy
    @router.get("/policies/model-upgrades", response_model=ModelUpgradePolicySchema)
    def get_policy(repo: AgentsRepository = Depends(get_repo)):
        policy = repo.get_model_policy()
        return ModelUpgradePolicySchema.model_validate(_to_dict(policy))

    @router.put("/policies/model-upgrades", response_model=ModelUpgradePolicySchema)
    def update_policy(
        payload: ModelUpgradePolicySchema,
        repo: AgentsRepository = Depends(get_repo),
    ):
        policy = service.update_model_policy(
            repo=repo,
            global_default_model=payload.global_default_model,
            auto_upgrade_enabled=payload.auto_upgrade_enabled,
            adoption_delay_days=payload.adoption_delay_days,
            allowed_models=payload.allowed_models,
            next_upgrade_at=payload.next_upgrade_at,
        )
        return ModelUpgradePolicySchema.model_validate(_to_dict(policy))

else:  # pragma: no cover
    router = None
