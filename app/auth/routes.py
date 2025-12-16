from __future__ import annotations

import os
from typing import Any, Dict

try:  # pragma: no cover
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    BaseModel = object  # type: ignore[misc,assignment]


DEV_USERNAME = os.environ.get("INSPECTAH_DEV_USER")
DEV_PASSWORD = os.environ.get("INSPECTAH_DEV_PASSWORD")
DEV_TOKEN = os.environ.get("INSPECTAH_DEV_TOKEN")
DEV_ENV = os.environ.get("INSPECTAH_ENV", "production").lower()  # Default to production (fail-closed)


class LoginRequest(BaseModel):  # type: ignore[misc]
    username: str
    password: str


def _build_user_payload(username: str) -> Dict[str, Any]:
    return {"id": "dev-admin", "name": "Dev Admin", "email": username, "roles": ["admin"]}


if APIRouter is not None:  # pragma: no cover
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post("/login")
    def login(payload: LoginRequest) -> Dict[str, Any]:
        if DEV_ENV not in {"dev", "local", "development", ""}:
            raise HTTPException(status_code=403, detail="Login de desenvolvimento desabilitado fora de ambiente dev")

        if payload.username != DEV_USERNAME or payload.password != DEV_PASSWORD:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        user_payload = _build_user_payload(payload.username)
        return {
            "access_token": DEV_TOKEN,
            "token": DEV_TOKEN,
            "token_type": "bearer",
            "user": user_payload,
            "user_id": user_payload["id"],
            "email": user_payload["email"],
            "roles": user_payload["roles"],
        }

else:  # pragma: no cover
    router = None

