from __future__ import annotations
from typing import List

try:
    from fastapi import APIRouter, HTTPException, Depends
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Depends = None  # type: ignore

from app.flows.service import FlowService
from app.flows.schemas import FlowCatalogEntry

# Rota dedicada de catálogo (sombra para compatibilidade)
if APIRouter:
    router = APIRouter(prefix="/api/flows", tags=["flows"])

    def _service() -> FlowService:
        return FlowService()

    @router.get("/catalog", response_model=List[FlowCatalogEntry])
    def list_catalog(service: FlowService = Depends(_service)):
        try:
            entries = service.list_catalog()
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=500, detail=str(exc))
        return [FlowCatalogEntry.model_validate(e) for e in entries]
else:  # pragma: no cover
    router = None
