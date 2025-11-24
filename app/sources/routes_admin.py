from __future__ import annotations

try:  # pragma: no cover
    from fastapi import APIRouter, HTTPException
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]

from . import service
from .healthcheck import run_healthcheck
from .models import SourceState
from .schemas import SourceCreate, SourceFilter, SourceRead, SourceUpdate


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/admin/sources", tags=["sources"])

    @router.get("", response_model=list[SourceRead])
    def list_admin_sources(
        type: str | None = None,
        category: str | None = None,
        state: SourceState | None = None,
        theme: str | None = None,
        redundancy_group: str | None = None,
    ):
        filters = SourceFilter(type=type, category=category, state=state, theme=theme, redundancy_group=redundancy_group)
        return service.list_sources(filters)

    @router.get("/{source_id}", response_model=SourceRead)
    def get_admin_source(source_id: str):
        src = service.get_source_detail(source_id)
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return src

    @router.post("", response_model=SourceRead, status_code=201)
    def create_admin_source(payload: SourceCreate):
        src = service.create_source(payload)
        return src

    @router.put("/{source_id}", response_model=SourceRead)
    def update_admin_source(source_id: str, payload: SourceUpdate):
        src = service.update_source(source_id, payload)
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return src

    @router.post("/{source_id}/healthcheck")
    def trigger_healthcheck(source_id: str):
        result = run_healthcheck(source_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        return result

    @router.get("/{source_id}/healthchecks")
    def list_healthchecks(source_id: str):
        return [hc.__dict__ for hc in service.list_healthchecks(source_id)]

else:  # pragma: no cover
    router = None

