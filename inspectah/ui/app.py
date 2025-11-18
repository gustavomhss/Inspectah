from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .runtime_bridge import is_runtime_available
from .schemas import HealthResponse
from .templating import render_fragment, render_page
from .views import admin_sources, evidence, model_fields, query


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.title, version=settings.version)
    app.state.settings = settings

    static_dir = Path(__file__).resolve().parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get('/', response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        body = render_fragment('home.html', {})
        return render_page(request, body, title=settings.title)

    @app.get('/health', response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status='ok', version=settings.version, runtime_s6_available=is_runtime_available())

    app.include_router(admin_sources.router)
    app.include_router(model_fields.router)
    app.include_router(query.router)
    app.include_router(evidence.router)
    return app
