from __future__ import annotations

try:  # pragma: no cover
    from fastapi import APIRouter, Depends, Header, HTTPException, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Depends = None  # type: ignore[misc]
    Header = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    status = None  # type: ignore[misc]

from app.ingestion import services
from app.ingestion.schemas import NewsdataRunRequest, NewsdataRunResponse


def _require_ops_ingest(x_role: str = Header(default="")) -> str:
    if not x_role or "ops_ingest" not in x_role.split(","):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "Role ops_ingest obrigatória para ingest newsdata"},
        )
    return x_role


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/api/ingest/newsdata", tags=["ingestion"])

    @router.post("/run", response_model=NewsdataRunResponse, status_code=status.HTTP_201_CREATED)
    def trigger_newsdata_run(
        payload: NewsdataRunRequest,
        _: str = Depends(_require_ops_ingest),
    ) -> NewsdataRunResponse:
        run = services.run_newsdata_ingestion(
            trigger_origin=payload.trigger_origin,
            size=payload.size,
            throttle_seconds=payload.throttle_seconds,
            max_attempts=payload.max_attempts,
        )
        return NewsdataRunResponse(
            run_id=run.id,
            status=run.status,
            items_processed=run.items_processed,
            payload_ref=run.payload_ref,
            meta=run.meta,
        )
else:  # pragma: no cover
    router = None
