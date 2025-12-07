from __future__ import annotations

from typing import Callable, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, Depends, HTTPException, status
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    Depends = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    status = None  # type: ignore[misc]

from app.ingestion import services
from app.ingestion.errors import (
    ConfigDisabledError,
    ConfigNotFoundError,
    ModeIncompatibleError,
    RunInProgressError,
    RunNotFoundError,
    SourceNotEligibleError,
    SourceNotFoundError,
)
from app.ingestion.models import IngestionTrigger
from app.ingestion.repository import IngestionRepository
from app.ingestion.schemas import (
    ConfigResponse,
    ErrorResponse,
    ManualRunRequest,
    RunDetail,
    RunSummary,
    RunsResponse,
    ToggleModeRequest,
    TriggerRunResponse,
)
from app.sources.service import get_source_detail
try:
    from app.utils.rbac import require_role
except ModuleNotFoundError:  # pragma: no cover
    def require_role(roles: Optional[set] = None, header_name: str = "x-role"):
        def _dep():
            return header_name  # dummy placeholder
        return _dep


def get_repo() -> IngestionRepository:
    return IngestionRepository()


def get_source_fetcher() -> Callable:
    return get_source_detail


def _handle_domain_error(exc: Exception) -> HTTPException:
    if isinstance(exc, (SourceNotFoundError, ConfigNotFoundError, RunNotFoundError)):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorResponse(error="not_found", detail=str(exc)).model_dump())
    if isinstance(exc, SourceNotEligibleError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorResponse(error="source_not_eligible", detail=str(exc)).model_dump())
    if isinstance(exc, ConfigDisabledError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorResponse(error="config_disabled", detail=str(exc)).model_dump())
    if isinstance(exc, ModeIncompatibleError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorResponse(error="mode_incompatible", detail=str(exc)).model_dump())
    if isinstance(exc, RunInProgressError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ErrorResponse(error="run_in_progress", detail=str(exc)).model_dump())
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=ErrorResponse(error="internal_error", detail=str(exc)).model_dump())


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/admin/ingestion", tags=["ingestion"])

    @router.post("/{source_id}/run", response_model=TriggerRunResponse, status_code=status.HTTP_201_CREATED)
    def trigger_manual_run(
        source_id: str,
        payload: ManualRunRequest,
        _: str = Depends(require_role(roles={"admin", "ops_ingest"}, header_name="x-role")),
        repo: IngestionRepository = Depends(get_repo),
        source_fetcher=Depends(get_source_fetcher),
    ) -> TriggerRunResponse:
        # newsdata_br usa pipeline ops-only (run_newsdata_ingestion)
        target_id = source_id
        try:
            source = source_fetcher(source_id)
            target_id = getattr(source, "id", source_id)
        except Exception:
            source = None
        if target_id in {"newsdata_br", "src_afca2b6b12"} or (source and getattr(source, "slug", None) == "newsdata_br"):
            try:
                run = services.run_newsdata_ingestion(
                    trigger_origin=payload.trigger_origin,
                    repo=repo,
                )
                return TriggerRunResponse(run_id=run.id, status=run.status, trigger=run.trigger)
            except Exception as exc:  # noqa: BLE001
                raise _handle_domain_error(exc) from exc
        try:
            run = services.start_ingestion_run(
                source_id,
                trigger=IngestionTrigger.MANUAL,
                trigger_origin=payload.trigger_origin,
                repo=repo,
                source_fetcher=source_fetcher,
                execute_inline=payload.force,
            )
            return TriggerRunResponse(run_id=run.id, status=run.status, trigger=run.trigger)
        except Exception as exc:  # noqa: BLE001
            raise _handle_domain_error(exc) from exc

    @router.post("/{source_id}/toggle-mode", response_model=ConfigResponse)
    def toggle_mode(
        source_id: str,
        payload: ToggleModeRequest,
        repo: IngestionRepository = Depends(get_repo),
        source_fetcher=Depends(get_source_fetcher),
    ) -> ConfigResponse:
        try:
            cfg = services.toggle_ingestion_mode(
                source_id,
                new_mode=payload.mode,
                enabled=payload.enabled,
                updated_by="admin_ui",
                repo=repo,
                source_fetcher=source_fetcher,
            )
            return ConfigResponse(
                id=cfg.id,
                source_id=cfg.source_id,
                enabled=cfg.enabled,
                mode=cfg.mode,
                interval_minutes=cfg.interval_minutes,
                max_attempts=cfg.max_attempts,
                timeout_seconds=cfg.timeout_seconds,
                last_run_id=cfg.last_run_id,
                updated_at=cfg.updated_at,
            )
        except Exception as exc:  # noqa: BLE001
            raise _handle_domain_error(exc) from exc

    @router.get("/{source_id}/runs", response_model=RunsResponse)
    def list_runs(source_id: str, limit: int = 20, offset: int = 0, repo: IngestionRepository = Depends(get_repo)) -> RunsResponse:
        try:
            runs = repo.list_runs_by_source(source_id, limit=limit, offset=offset)
            cfg = repo.get_config(source_id)
        except Exception:  # noqa: BLE001
            # Fonte sem config/ingestão: responder vazio (200) para não poluir logs da UI
            runs = []
            cfg = None
        summaries = [
            RunSummary(
                id=run.id,
                source_id=run.source_id,
                status=run.status,
                trigger=run.trigger,
                started_at=run.started_at,
                finished_at=run.finished_at,
                items_processed=run.items_processed,
                error_code=run.error_code,
                error_message=run.error_message,
                meta=run.meta or {},
            )
            for run in runs
        ]
        return RunsResponse(
            runs=summaries,
            pagination={"limit": limit, "offset": offset, "count": len(summaries)},
            config_mode=cfg.mode if cfg else None,
        )

    @router.get("/runs/{run_id}", response_model=RunDetail)
    def get_run_detail(run_id: str, repo: IngestionRepository = Depends(get_repo)) -> RunDetail:
        run = repo.get_run(run_id)
        if not run:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorResponse(error="not_found", detail="run not found").model_dump())
        return RunDetail(
            id=run.id,
            source_id=run.source_id,
            status=run.status,
            trigger=run.trigger,
            started_at=run.started_at,
            finished_at=run.finished_at,
            items_processed=run.items_processed,
            error_code=run.error_code,
            error_message=run.error_message,
            meta=run.meta or {},
            payload_ref=run.payload_ref,
        )
else:  # pragma: no cover
    router = None
