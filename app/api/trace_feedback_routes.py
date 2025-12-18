from __future__ import annotations

from typing import Any, Dict, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Depends = None  # type: ignore
    Query = None  # type: ignore

from app.agents.trace_repository import TraceRepository
from app.feedback.repository import FeedbackRepository, FeedbackOnTrace, FeedbackOnDecision


def _trace_repo() -> TraceRepository:
    return TraceRepository()


def _feedback_repo() -> FeedbackRepository:
    return FeedbackRepository()


if APIRouter is not None:  # pragma: no cover

    router = APIRouter(prefix="/api", tags=["traces", "feedback"])

    @router.get("/traces/recent")
    def list_recent_traces(
        domain: Optional[str] = Query(None),
        limit: int = Query(20, le=100),
        repo: TraceRepository = Depends(_trace_repo),
    ):
        traces = repo.list_recent(domain=domain, limit=limit)
        return {"items": traces}

    @router.get("/traces/decision/{decision_id}")
    def list_traces_by_decision(decision_id: str, repo: TraceRepository = Depends(_trace_repo)):
        agent_traces = repo.list_traces_by_decision(decision_id)
        return {"decision_id": decision_id, "agent_traces": agent_traces}

    @router.get("/traces/claim/{claim_id}")
    def list_traces_by_claim(claim_id: str, repo: TraceRepository = Depends(_trace_repo)):
        agent_traces = repo.list_traces_by_claim(claim_id)
        return {"claim_id": claim_id, "agent_traces": agent_traces}

    @router.get("/traces/{trace_id}")
    def trace_detail(trace_id: str, repo: TraceRepository = Depends(_trace_repo)):
        trace = repo.get_trace(trace_id)
        if not trace:
            raise HTTPException(status_code=404, detail="Trace não encontrado")
        steps = repo.list_steps_for_trace(trace_id)
        return {"trace": trace, "steps": steps}

    @router.post("/feedback/trace", status_code=status.HTTP_201_CREATED)
    def submit_feedback_trace(payload: Dict[str, Any] = Body(...), repo: FeedbackRepository = Depends(_feedback_repo)):
        target_id = payload.get("target_id")
        if not target_id:
            raise HTTPException(status_code=400, detail="target_id obrigatório")
        fb = FeedbackOnTrace(
            target_id=target_id,
            feedback_kind=payload.get("feedback_kind"),
            severity=payload.get("severity"),
            comment=payload.get("comment") or "",
            authored_by_actor=payload.get("authored_by_actor"),
            authored_by_role=payload.get("authored_by_role"),
            origin_surface=payload.get("origin_surface") or "ui_console",
        )
        repo.record_feedback_on_trace(fb)
        return {"ok": True, "feedback_id": fb.feedback_id}

    @router.post("/feedback/decision", status_code=status.HTTP_201_CREATED)
    def submit_feedback_decision(payload: Dict[str, Any] = Body(...), repo: FeedbackRepository = Depends(_feedback_repo)):
        decision_id = payload.get("decision_record_id")
        if not decision_id:
            raise HTTPException(status_code=400, detail="decision_record_id obrigatório")
        fb = FeedbackOnDecision(
            decision_record_id=decision_id,
            committee_trace_id=payload.get("committee_trace_id"),
            agent_trace_id=payload.get("agent_trace_id"),
            feedback_kind=payload.get("feedback_kind"),
            severity=payload.get("severity"),
            comment=payload.get("comment") or "",
            authored_by_actor=payload.get("authored_by_actor"),
            authored_by_role=payload.get("authored_by_role"),
            origin_surface=payload.get("origin_surface") or "ui_console",
        )
        repo.record_feedback_on_decision(fb)
        return {"ok": True, "feedback_id": fb.feedback_id}

else:  # pragma: no cover
    router = None
