from __future__ import annotations

from typing import Iterable

try:  # pragma: no cover
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ModuleNotFoundError:  # pragma: no cover
    FastAPI = None  # type: ignore[misc]
    CORSMiddleware = None  # type: ignore[misc]

from .explore.api import build_router
from .ui.consultation_api import router as consultation_router
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
    app = FastAPI(title="Inspectah API")
    _add_cors(app, origins=("http://localhost:5173", "http://127.0.0.1:5173"))

    explore_router = build_router()
    if explore_router is not None:
        app.include_router(explore_router)

    if consultation_router is not None:
        app.include_router(consultation_router, prefix="/api", tags=["consultation"])

    if admin_router is not None:
        app.include_router(admin_router)
    if dashboard_router is not None:
        app.include_router(dashboard_router)
    if sources_router is not None:
        app.include_router(sources_router)
    if ingestion_router is not None:
        app.include_router(ingestion_router)
    if agents_router is not None:
        app.include_router(agents_router)
    if debunk_router is not None:
        app.include_router(debunk_router, prefix="/api", tags=["debunk"])
    if cases_router is not None:
        app.include_router(cases_router, prefix="/api", tags=["cases"])
    if collections_router is not None:
        app.include_router(collections_router, prefix="/api", tags=["collections"])
    if truth_router is not None:
        app.include_router(truth_router)
    if console_router is not None:
        app.include_router(console_router)
    if copiloto_fontes_router is not None:
        app.include_router(copiloto_fontes_router, prefix="/admin/copiloto-fontes", tags=["admin-copiloto-fontes"])
    if auth_router is not None:
        app.include_router(auth_router)

    return app


# ASGI entrypoint expected by uvicorn
app = build_app()
