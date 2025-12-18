from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Body, HTTPException, Query, status, Request
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Body = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    Query = None  # type: ignore[misc]
    status = None  # type: ignore[misc]
    Request = None  # type: ignore[misc]

from app.truthdb import metrics as truth_metrics
from app.truthdb.metrics import LatencyTimer
from app.api.truth_schemas import (
    TruthTwinResponse,
    DecisionInspectResponse,
    build_truth_twin_response,
    build_decision_inspect_response,
)
from app.api.metrics import record_p4_request
from app.api.middleware.provenance import record_provenance_check
from app.truth.repository import TruthRepository, DecisionBlockRepository

logger = logging.getLogger(__name__)

# Validation constants
_MAX_ID_LENGTH = 128
_MAX_LIMIT = 1000
_DEFAULT_LIMIT = 50
_VALID_ID_PATTERN = re.compile(r"^[\w\-\.]+$")


def _validate_id(value: str, field_name: str = "id") -> str:
    """
    Validate and sanitize an ID parameter.

    Args:
        value: The ID value to validate
        field_name: Name of the field for error messages

    Returns:
        Sanitized ID

    Raises:
        HTTPException: If validation fails
    """
    if not value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} is required",
        )

    # Remove whitespace
    value = value.strip()

    if len(value) > _MAX_ID_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} exceeds maximum length ({_MAX_ID_LENGTH})",
        )

    if not _VALID_ID_PATTERN.match(value):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} contains invalid characters",
        )

    return value


def _validate_limit(limit: int) -> int:
    """
    Validate and bound a limit parameter.

    Args:
        limit: The requested limit

    Returns:
        Bounded limit value
    """
    if limit < 1:
        return _DEFAULT_LIMIT
    return min(limit, _MAX_LIMIT)


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

    # =========================================================================
    # S40-BE-023: Truth Twin endpoint
    # =========================================================================

    @router.get("/{claim_id}/twin")
    async def get_truth_twin(
        claim_id: str,
        request: Request,
    ) -> Dict[str, Any]:
        """
        Get Truth Twin for a claim (S40-BE-023).

        Returns complete truth status with decision timeline and provenance.

        Args:
            claim_id: The claim ID to fetch truth status for

        Returns:
            TruthTwinResponse with full provenance

        Raises:
            400: If claim_id is invalid
            404: If claim not found
        """
        start_time = time.time()
        endpoint = "twin"
        request_status = "success"
        provenance_valid = False

        try:
            # Validate input
            claim_id = _validate_id(claim_id, "claim_id")

            # Get truth record
            truth_repo = TruthRepository()
            decision_repo = DecisionBlockRepository()

            # Try to find by claim_id, id, or slug
            record = truth_repo.get_record_by_claim_id(claim_id)
            if not record:
                record = truth_repo.get_record(claim_id)
            if not record:
                record = truth_repo.get_record_by_slug(claim_id)

            if not record:
                # Still try to get decision blocks even without truth record
                blocks = decision_repo.get_by_claim(claim_id)
                if not blocks:
                    request_status = "error"
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Claim {claim_id} not found",
                    )
                # Build minimal record from blocks
                first_block = blocks[0] if blocks else {}
                last_block = blocks[-1] if blocks else {}
                record_dict = {
                    "claim_id": claim_id,
                    "domain": first_block.get("domain", "unknown"),
                    "current_state": last_block.get("final_state", "unknown"),
                    "created_at": first_block.get("created_at", ""),
                    "updated_at": last_block.get("created_at", ""),
                    "metadata": {},
                    "last_decision_id": last_block.get("decision_id"),
                }
                events = []
            else:
                metadata = record.metadata or {}
                record_dict = {
                    "claim_id": record.claim_id or record.id,
                    "slug": record.slug,
                    "headline": metadata.get("headline", record.slug),
                    "domain": record.domain,
                    "current_state": record.current_state.value if record.current_state else "unknown",
                    "created_at": record.created_at,
                    "updated_at": record.updated_at,
                    "metadata": metadata,
                    "last_decision_id": record.last_decision_id,
                }
                blocks = decision_repo.get_by_claim(record.claim_id or record.id)
                events_raw = truth_repo.list_events(record.id)
                events = [
                    {
                        "previous_state": e.previous_state.value if e.previous_state else "",
                        "new_state": e.new_state.value if e.new_state else "",
                        "reason": e.reason or "",
                        "created_at": e.created_at,
                        "decision_id": e.decision_id,
                    }
                    for e in events_raw
                ]

            # Build response
            response = build_truth_twin_response(record_dict, blocks, events)
            provenance_valid = response.has_valid_provenance()

            # Record latency metric (S40-BE-027)
            latency_ms = int((time.time() - start_time) * 1000)

            return {
                **response.to_dict(),
                "_latency_ms": latency_ms,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"[get_truth_twin] Error for claim_id={claim_id}: {e}")
            request_status = "error"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
        finally:
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            record_p4_request(endpoint, latency_ms, request_status, provenance_valid)
            record_provenance_check(provenance_valid)

    # =========================================================================
    # S40-BE-024: Decision Inspector endpoint
    # =========================================================================

    @router.get("/decision/{decision_id}/inspect")
    async def inspect_decision(
        decision_id: str,
        request: Request,
    ) -> Dict[str, Any]:
        """
        Inspect a specific decision (S40-BE-024).

        Returns complete decision details with full provenance.

        Args:
            decision_id: The decision ID to inspect

        Returns:
            DecisionInspectResponse with full provenance

        Raises:
            400: If decision_id is invalid
            404: If decision not found
        """
        start_time = time.time()
        endpoint = "inspect"
        request_status = "success"
        provenance_valid = False

        try:
            # Validate input
            decision_id = _validate_id(decision_id, "decision_id")

            decision_repo = DecisionBlockRepository()

            # Get decision block
            block = decision_repo.get_by_decision(decision_id)
            if not block:
                # Try by block ID
                block = decision_repo.get(decision_id)

            if not block:
                request_status = "error"
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Decision {decision_id} not found",
                )

            # Build response
            response = build_decision_inspect_response(block)
            provenance_valid = response.has_valid_provenance()

            # Record latency metric (S40-BE-027)
            latency_ms = int((time.time() - start_time) * 1000)

            return {
                **response.to_dict(),
                "_latency_ms": latency_ms,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"[inspect_decision] Error for decision_id={decision_id}: {e}")
            request_status = "error"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
        finally:
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            record_p4_request(endpoint, latency_ms, request_status, provenance_valid)
            record_provenance_check(provenance_valid)

    # =========================================================================
    # S40-BE-023: Timeline endpoint (convenience)
    # =========================================================================

    @router.get("/{claim_id}/timeline")
    async def get_decision_timeline(
        claim_id: str,
        request: Request,
        limit: int = _DEFAULT_LIMIT,
    ) -> Dict[str, Any]:
        """
        Get decision timeline for a claim.

        Convenience endpoint that returns just the timeline portion.

        Args:
            claim_id: The claim ID
            limit: Maximum number of decisions to return (default 50, max 1000)

        Returns:
            Timeline of decisions

        Raises:
            400: If claim_id is invalid
        """
        start_time = time.time()
        endpoint = "timeline"
        request_status = "success"

        try:
            # Validate inputs
            claim_id = _validate_id(claim_id, "claim_id")
            limit = _validate_limit(limit)

            decision_repo = DecisionBlockRepository()
            blocks = decision_repo.get_by_claim(claim_id)[:limit]

            timeline = [
                {
                    "id": b.get("id", ""),
                    "decision_id": b.get("decision_id", ""),
                    "gate": b.get("gate", ""),
                    "decision_type": b.get("decision_type", ""),
                    "initial_state": b.get("initial_state", ""),
                    "final_state": b.get("final_state", ""),
                    "created_at": str(b.get("created_at", "")),
                    "latency_ms": b.get("latency_ms"),
                }
                for b in blocks
                if isinstance(b, dict)
            ]

            latency_ms = int((time.time() - start_time) * 1000)

            # Timeline has implicit provenance via blocks
            provenance_valid = len(timeline) > 0

            return {
                "claim_id": claim_id,
                "timeline": timeline,
                "count": len(timeline),
                "limit": limit,
                "_latency_ms": latency_ms,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"[get_decision_timeline] Error for claim_id={claim_id}: {e}")
            request_status = "error"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )
        finally:
            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            record_p4_request(endpoint, latency_ms, request_status, True)

else:  # pragma: no cover
    router = None
