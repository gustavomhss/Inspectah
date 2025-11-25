from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import uuid

UPLOAD_DIR = Path("out/copiloto_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
_FILES: Dict[str, Dict[str, Any]] = {}


def save_upload(session_id: str, filename: str, content: bytes, content_type: str | None = None) -> Dict[str, Any]:
    file_id = f"file_{uuid.uuid4().hex}"
    safe_name = filename.replace("/", "_")
    path = UPLOAD_DIR / f"{file_id}_{safe_name}"
    path.write_bytes(content)
    info = {
        "file_id": file_id,
        "filename": safe_name,
        "content_type": content_type or "application/octet-stream",
        "path": str(path),
        "session_id": session_id,
    }
    _FILES[file_id] = info
    return info


def get_file(file_id: str) -> Dict[str, Any]:
    return _FILES.get(file_id, {})
