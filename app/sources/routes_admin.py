from __future__ import annotations

try:  # pragma: no cover
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    BaseModel = object  # type: ignore[misc,assignment]

from . import service
from .healthcheck import run_healthcheck
from .models import SourceState
from .schemas import SourceCreate, SourceFilter, SourceRead, SourceUpdate
from app.ingestion.models import IngestionTrigger, IngestionMode
from app.ingestion import services as ingestion_services


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/admin/sources", tags=["sources"])

    class StatusChange(BaseModel):  # type: ignore[misc]
        target_state: SourceState
        reason: str = "Solicitado via admin"
        changed_by: str = "admin-ui"

    @router.get("")
    def list_admin_sources(
        type: str | None = None,
        category: str | None = None,
        state: SourceState | None = None,
        theme: str | None = None,
        redundancy_group: str | None = None,
    ):
        filters = SourceFilter(type=type, category=category, state=state, theme=theme, redundancy_group=redundancy_group)
        sources = [service.enrich_source_read(src) for src in service.list_sources(filters)]
        return {"sources": [src.model_dump() for src in sources]}

    @router.get("/{source_id}")
    def get_admin_source(source_id: str):
        src = service.get_source_detail(source_id)
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        history = service.list_state_history(source_id)
        enriched = service.enrich_source_read(src)
        return {"source": {**enriched.model_dump(), "state_history": history}}

    @router.post("", status_code=201)
    def create_admin_source(payload: SourceCreate):
        src = service.create_source(payload)
        return {"source": service.enrich_source_read(src).model_dump()}

    @router.put("/{source_id}")
    def update_admin_source(source_id: str, payload: SourceUpdate):
        src = service.update_source(source_id, payload)
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return {"source": service.enrich_source_read(src).model_dump()}

    @router.post("/{source_id}/status")
    def change_status(source_id: str, payload: StatusChange):
        try:
            src = service.change_source_state(source_id, payload.target_state, payload.reason, payload.changed_by)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return {"source": service.enrich_source_read(src).model_dump()}

    @router.post("/{source_id}/healthcheck")
    def trigger_healthcheck(source_id: str):
        result = run_healthcheck(source_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return result

    @router.get("/{source_id}/healthchecks")
    def list_healthchecks(source_id: str):
        return {"healthchecks": [hc.__dict__ for hc in service.list_healthchecks(source_id)]}

    @router.post("/{source_id}/ingestion/run")
    def trigger_manual_run(source_id: str):
        run = ingestion_services.start_ingestion_run(source_id, trigger=IngestionTrigger.MANUAL, trigger_origin="admin_ui")
        return {"run_id": run.id, "status": run.status.value}

    @router.post("/{source_id}/ingestion/pause")
    def pause_ingestion(source_id: str):
        config = ingestion_services.toggle_ingestion_mode(source_id, new_mode=IngestionMode.MANUAL_ONLY, enabled=False, updated_by="admin-ui")
        return {"config": config.to_dict()}

    @router.post("/{source_id}/ingestion/resume")
    def resume_ingestion(source_id: str):
        config = ingestion_services.toggle_ingestion_mode(source_id, new_mode=IngestionMode.AUTOMATIC, enabled=True, updated_by="admin-ui")
        return {"config": config.to_dict()}

else:  # pragma: no cover
    router = None
