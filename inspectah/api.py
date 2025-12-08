from __future__ import annotations

from typing import Iterable

try:  # pragma: no cover
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import Response
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    FastAPI = None  # type: ignore[misc]
    CORSMiddleware = None  # type: ignore[misc]
    Response = None  # type: ignore[misc]
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
    def generate_latest():  # type: ignore[misc]
        return b""

from .explore.api import build_router
try:  # pragma: no cover
    from .ui.consultation_api import router as consultation_router
except ModuleNotFoundError:  # pragma: no cover
    consultation_router = None
# Routers carregados individualmente para que uma falha não silencie as demais rotas admin
try:  # pragma: no cover
    from app.admin.routes import dashboard_router, router as admin_router
except ModuleNotFoundError:  # pragma: no cover
    admin_router = None
    dashboard_router = None
try:  # pragma: no cover
    from app.auth.routes import router as auth_router
except ModuleNotFoundError:  # pragma: no cover
    auth_router = None
try:  # pragma: no cover
    from app.sources.routes_admin import router as sources_router
except ModuleNotFoundError:  # pragma: no cover
    sources_router = None
try:  # pragma: no cover
    from inspectah.routers.copiloto_fontes import router as copiloto_fontes_router
except ModuleNotFoundError:  # pragma: no cover
    copiloto_fontes_router = None
try:  # pragma: no cover
    from app.api.ingestion.routes import router as ingestion_router
except ModuleNotFoundError:  # pragma: no cover
    ingestion_router = None
try:  # pragma: no cover
    from app.api.agents.routes_admin import router as agents_router
except ModuleNotFoundError:  # pragma: no cover
    agents_router = None
try:  # pragma: no cover
    from app.api.admin_agent_flows_routes import router as agent_flows_admin_router
except ModuleNotFoundError:  # pragma: no cover
    agent_flows_admin_router = None
try:  # pragma: no cover
    from app.api.debunk.routes import router as debunk_router
except ModuleNotFoundError:  # pragma: no cover
    debunk_router = None
try:  # pragma: no cover
    from app.api.cases.routes import cases_router, collections_router
except ModuleNotFoundError:  # pragma: no cover
    cases_router = None
    collections_router = None
try:  # pragma: no cover
    from app.api.truth_routes import router as truth_router
except ModuleNotFoundError:  # pragma: no cover
    truth_router = None
try:  # pragma: no cover
    from app.api.console_routes import router as console_router
except ModuleNotFoundError:  # pragma: no cover
    console_router = None
try:  # pragma: no cover
    from app.api.flow_console_routes import router as flows_router
except ModuleNotFoundError:  # pragma: no cover
    flows_router = None
try:  # pragma: no cover
    from app.api.catalog_routes import router as catalog_router
except ModuleNotFoundError:  # pragma: no cover
    catalog_router = None
try:  # pragma: no cover
    from app.api.providers_routes import router as providers_router
except ModuleNotFoundError:  # pragma: no cover
    providers_router = None
try:  # pragma: no cover
    from app.api.ops_cockpit_routes import router as ops_cockpit_router
except ModuleNotFoundError:  # pragma: no cover
    ops_cockpit_router = None
try:  # pragma: no cover
    from app.api.newsdata_ingest_routes import router as newsdata_router
except ModuleNotFoundError:  # pragma: no cover
    newsdata_router = None


def _add_cors(app: FastAPI, origins: Iterable[str]) -> None:
    if CORSMiddleware is None:  # pragma: no cover
        return
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def build_app():  # pragma: no cover
    if FastAPI is None:
        return None
    api_app = FastAPI(title="Inspectah API")
    _add_cors(api_app, origins=("http://localhost:5173", "http://127.0.0.1:5173"))

    # Semeia métricas admin/obs
    try:  # pragma: no cover
        import app.obs.metrics  # noqa: F401
    except Exception:
        pass

    # Middleware de auth/RBAC com JWT RS256 (fail-closed)
    try:  # pragma: no cover
        from app.middlewares.auth import AuthJWTMiddleware
        api_app.add_middleware(AuthJWTMiddleware)
    except Exception:  # pragma: no cover
        pass

    explore_router = build_router()
    if explore_router is not None:
        api_app.include_router(explore_router)

    if consultation_router is not None:
        api_app.include_router(consultation_router, prefix="/api", tags=["consultation"])

    if sources_router is not None:
        api_app.include_router(sources_router)
    if admin_router is not None:
        api_app.include_router(admin_router)
    if dashboard_router is not None:
        api_app.include_router(dashboard_router)
    if ingestion_router is not None:
        api_app.include_router(ingestion_router)
    if agents_router is not None:
        api_app.include_router(agents_router)
    if agent_flows_admin_router is not None:
        api_app.include_router(agent_flows_admin_router)
    if debunk_router is not None:
        api_app.include_router(debunk_router, prefix="/api", tags=["debunk"])
    if cases_router is not None:
        api_app.include_router(cases_router, prefix="/api", tags=["cases"])
    if collections_router is not None:
        api_app.include_router(collections_router, prefix="/api", tags=["collections"])
    if truth_router is not None:
        api_app.include_router(truth_router)
    if console_router is not None:
        api_app.include_router(console_router)
    if flows_router is not None:
        api_app.include_router(flows_router)
    if catalog_router is not None:
        api_app.include_router(catalog_router)
    if providers_router is not None:
        api_app.include_router(providers_router, tags=["providers"])
    if ops_cockpit_router is not None:
        api_app.include_router(ops_cockpit_router)
    if newsdata_router is not None:
        # Router já define prefixo /api/ingest/newsdata; não aplicar prefixo extra
        api_app.include_router(newsdata_router, tags=["ingestion"])
    if copiloto_fontes_router is not None:
        api_app.include_router(copiloto_fontes_router, prefix="/admin/copiloto-fontes", tags=["admin-copiloto-fontes"])
    if auth_router is not None:
        api_app.include_router(auth_router)

    @api_app.get("/metrics")
    def metrics():  # pragma: no cover
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @api_app.get("/.well-known/jwks.json")
    def jwks():  # pragma: no cover
        path = ".well-known/jwks.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                return Response(f.read(), media_type="application/json")
        except FileNotFoundError:
            return Response(status_code=404)

    return api_app


# ASGI entrypoint expected by uvicorn
app = build_app()
