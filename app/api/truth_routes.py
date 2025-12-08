from __future__ import annotations

from typing import Any, Dict

try:  # pragma: no cover
    from fastapi import APIRouter, Body, HTTPException, status, Request
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Body = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    status = None  # type: ignore[misc]
    Request = None  # type: ignore[misc]

from app.truthdb import metrics as truth_metrics
from app.truthdb.metrics import LatencyTimer


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/api/truth", tags=["truth"])

    @router.post("/promotion")
    async def promote_claim(
        request: Request,
        payload: Dict[str, Any] = Body(...),
    ):
        """
        Promotion SF3 com state machine e métricas.

        Payload mínimo: claim_id, actor, role, op_id, current_state, target_state, justification, hash_manifest.
        Transições permitidas: PENDING->UNDER_REVIEW; UNDER_REVIEW->PROMOTED/CONTESTABLE/REJECTED.
        """
        claim_id = payload.get("claim_id")
        current_state = payload.get("current_state")
        target_state = payload.get("target_state")
        hash_manifest = payload.get("hash_manifest")
        if not all([claim_id, current_state, target_state, hash_manifest]):
            truth_metrics.record_failure(reason="missing_fields")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Campos obrigatórios ausentes")

        allowed = {
            ("PENDING", "UNDER_REVIEW"),
            ("UNDER_REVIEW", "PROMOTED"),
            ("UNDER_REVIEW", "CONTESTABLE"),
            ("UNDER_REVIEW", "REJECTED"),
        }
        if (current_state, target_state) not in allowed:
            truth_metrics.record_failure(reason="invalid_transition")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transição inválida")

        role = getattr(request.state, "role", None) or payload.get("role")
        actor = getattr(request.state, "actor", None)
        op_id = getattr(request.state, "op_id", None)
        with LatencyTimer(current_state, target_state):
            truth_metrics.record_transition(current_state, target_state, "success", role or "unknown")
        return {
            "claim_id": claim_id,
            "current_state": current_state,
            "target_state": target_state,
            "result": "promoted",
            "actor": actor,
            "role": role,
            "op_id": op_id,
            "hash_manifest": hash_manifest,
        }

    @router.post("/promotion/invalid")
    async def promote_invalid(
        request: Request,
        payload: Dict[str, Any] = Body(None),
    ):
        """
        Força trajeto inválido para métricas/negativos.

        Sempre retorna 400 e registra flow_error.
        """
        truth_metrics.record_failure(reason="invalid_transition")
        actor = getattr(request.state, "actor", None)
        role = getattr(request.state, "role", None)
        op_id = getattr(request.state, "op_id", None)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "invalid_transition",
                "actor": actor,
                "role": role,
                "op_id": op_id,
                "payload": payload or {},
            },
        )
else:  # pragma: no cover
    router = None
