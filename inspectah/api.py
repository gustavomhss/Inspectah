from __future__ import annotations

try:  # pragma: no cover
    from fastapi import FastAPI
except ModuleNotFoundError:  # pragma: no cover
    FastAPI = None  # type: ignore[misc]

from .explore.api import build_router


def build_app():  # pragma: no cover
    if FastAPI is None:
        return None
    app = FastAPI(title="Inspectah D8")
    router = build_router()
    if router is not None:
        app.include_router(router)
    return app
