from __future__ import annotations

import logging

try:  # pragma: no cover
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    BaseModel = object  # type: ignore[misc,assignment]

from . import service

logger = logging.getLogger(__name__)
from .healthcheck import run_healthcheck
from .models import SourceState
from .schemas import SourceCreate, SourceFilter, SourceRead, SourceUpdate
from .audit import record_admin_action
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
        if not src and source_id == "newsdata_br":
            # stub minimal para provedor newsdata_br quando não existe em DB
            now = service._now_iso()  # type: ignore[attr-defined]
            stub = SourceRead(
                id="newsdata_br",
                slug="newsdata_br",
                name="newsdata",
                description="Fonte do provedor newsdata.io (ops_only).",
                type="news_api",
                category="news",
                themes=[],
                info_types=[],
                refresh_interval=1440,
                protocol="https",
                format="json",
                endpoint="https://newsdata.io/api/1/latest",
                auth_type="api_key",
                auth_config={"header": "apikey", "value": "masked"},
                request_params={"country": "br", "language": "pt"},
                headers={},
                frequency="manual",
                timeout_ms=30000,
                retry_policy={"max_attempts": 3},
                parsing_config={},
                redundancy_group=None,
                redundancy_role=None,
                meta={"provider_id": "newsdata_br", "provider_kind": "newsdata"},
                state=SourceState.ACTIVE,
                state_reason=None,
                state_updated_at=now,
                created_at=now,
                updated_at=now,
                created_by="system",
                updated_by="system",
                last_reviewed_by=None,
                conflict_flags=[],
                conflict_with_sources=[],
                has_open_contestation=False,
                last_conflict_at=None,
                evidence_refs=[],
                trust_severity=None,
                last_health_status="unknown",
                last_health_error=None,
                last_health_at=now,
                recent_items_count=0,
                ingestion_mode="MANUAL_ONLY",
                health_status="unknown",
                health_reason=None,
                last_run_status=None,
                last_run_finished_at=None,
                last_run_latency_ms=None,
                last_run_items=None,
                failure_streak=0,
            )
            source_payload = {**stub.model_dump(), "state_history": []}
            source_payload.setdefault("status", stub.state.value if hasattr(stub.state, "value") else stub.state)
            return {"source": source_payload}
        if not src:
            raise HTTPException(status_code=404, detail="Fonte não encontrada")
        history = service.list_state_history(source_id)
        enriched = service.enrich_source_read(src)
        source_payload = {**enriched.model_dump(), "state_history": history}
        # expõe status para compatibilidade com testes/admin UI
        source_payload.setdefault("status", enriched.state.value if hasattr(enriched.state, "value") else enriched.state)
        return {"source": source_payload}

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
        try:
            # No admin endpoint usamos a execução padrão (não-inline) para evitar falhas de rede em ambientes de teste
            run = ingestion_services.start_ingestion_run(
                source_id,
                trigger=IngestionTrigger.MANUAL,
                trigger_origin="admin_ui",
                execute_inline=False,
            )
            record_admin_action("manual_run", source_id, "admin-ui", {"run_id": run.id, "status": run.status.value})
            return {"run_id": run.id, "status": run.status.value}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to start manual ingestion run for source %s", source_id)
            raise HTTPException(
                status_code=500,
                detail="Failed to start ingestion run. Check server logs for details."
            )

    @router.post("/{source_id}/ingestion/pause")
    def pause_ingestion(source_id: str):
        config = ingestion_services.toggle_ingestion_mode(source_id, new_mode=IngestionMode.MANUAL_ONLY, enabled=False, updated_by="admin-ui")
        return {"config": config.__dict__}

    @router.post("/{source_id}/ingestion/resume")
    def resume_ingestion(source_id: str):
        config = ingestion_services.toggle_ingestion_mode(source_id, new_mode=IngestionMode.AUTOMATIC, enabled=True, updated_by="admin-ui")
        return {"config": config.__dict__}

else:  # pragma: no cover
    router = None
