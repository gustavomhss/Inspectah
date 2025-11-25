from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

SessionData = Dict[str, Any]

_SESSIONS: Dict[str, SessionData] = {}


def create_session(user_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> str:
    session_id = f"s21_1_{uuid.uuid4().hex}"
    _SESSIONS[session_id] = {
        "user_id": user_id,
        "context": context or {},
        "messages": [],
        "files": [],
    }
    return session_id


def get_session(session_id: str) -> SessionData:
    return _SESSIONS.get(session_id)


def append_message(session_id: str, role: str, content: str) -> None:
    if session_id not in _SESSIONS:
        return
    _SESSIONS[session_id]["messages"].append({"role": role, "content": content})


def attach_file(session_id: str, file_id: str, metadata: Dict[str, Any]) -> None:
    if session_id not in _SESSIONS:
        return
    _SESSIONS[session_id]["files"].append({"file_id": file_id, "metadata": metadata})
