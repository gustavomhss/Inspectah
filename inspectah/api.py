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
try:  # pragma: no cover
    from app.admin.routes import router as admin_router
    from app.auth.routes import router as auth_router
    from app.sources.routes_admin import router as sources_router
except ModuleNotFoundError:  # pragma: no cover
    admin_router = None
    auth_router = None
    sources_router = None


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
    if sources_router is not None:
        app.include_router(sources_router)
    if auth_router is not None:
        app.include_router(auth_router)

    return app


# ASGI entrypoint expected by uvicorn
app = build_app()
