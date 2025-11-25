from __future__ import annotations

from typing import Any, Dict, List, Optional

try:  # pragma: no cover
    from fastapi import APIRouter, File, HTTPException, UploadFile
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover
    APIRouter = None  # type: ignore[misc]
    HTTPException = None  # type: ignore[misc]
    UploadFile = None  # type: ignore[misc]
    BaseModel = object  # type: ignore[misc,assignment]

from inspectah.services import copiloto_files, copiloto_sessions
from inspectah.agents.s21_1_copiloto_fontes import run_copiloto_interaction


class SessionCreateRequest(BaseModel):  # type: ignore[misc]
    user_id: Optional[str] = None
    context: Dict[str, Any] = {}


class MessageRequest(BaseModel):  # type: ignore[misc]
    user_message: str
    form_state: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    files: List[Dict[str, Any]] = []


if APIRouter is not None:  # pragma: no cover
    router = APIRouter()

    @router.post("/sessions")
    def create_session(payload: SessionCreateRequest) -> Dict[str, Any]:
        session_id = copiloto_sessions.create_session(payload.user_id, payload.context)
        return {"session_id": session_id}

    @router.post("/sessions/{session_id}/messages")
    def send_message(session_id: str, payload: MessageRequest) -> Dict[str, Any]:
        session = copiloto_sessions.get_session(session_id)
        if not session:
            session_id = copiloto_sessions.create_session(None, {})
        copiloto_sessions.append_message(session_id, "user", payload.user_message)
        result = run_copiloto_interaction(session_id, payload.user_message, payload.form_state or {}, payload.files or [])
        copiloto_sessions.append_message(session_id, "assistant", result.get("assistant_message", ""))
        return {"session_id": session_id, **result}

    @router.post("/sessions/{session_id}/files")
    async def upload_file(session_id: str, file: UploadFile = File(...)) -> Dict[str, Any]:
        session = copiloto_sessions.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        content = await file.read()
        info = copiloto_files.save_upload(session_id, file.filename, content, file.content_type)
        copiloto_sessions.attach_file(session_id, info["file_id"], info)
        return info

    @router.get("/sessions/{session_id}")
    def get_session(session_id: str) -> Dict[str, Any]:
        data = copiloto_sessions.get_session(session_id)
        if not data:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        return data

else:  # pragma: no cover
    router = None
