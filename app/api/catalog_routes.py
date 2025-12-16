from __future__ import annotations
import logging
from typing import List

try:
    from fastapi import APIRouter, HTTPException, Depends
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore
    HTTPException = None  # type: ignore
    Depends = None  # type: ignore

from app.flows.service import FlowService
from app.flows.schemas import FlowCatalogEntry

logger = logging.getLogger(__name__)

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
            logger.exception("Failed to list flow catalog")
            raise HTTPException(
                status_code=500,
                detail="Failed to load flow catalog. Check server logs for details."
            )
        return [FlowCatalogEntry.model_validate(e) for e in entries]
else:  # pragma: no cover
    router = None
