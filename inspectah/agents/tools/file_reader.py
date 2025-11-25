from __future__ import annotations

from pathlib import Path

from inspectah.services.copiloto_files import get_file


def read_file_as_text(file_id: str) -> str:
    info = get_file(file_id)
    path_value = info.get("path") if isinstance(info, dict) else None
    if not path_value:
        return ""
    path = Path(path_value)
    if not path.exists():
        return ""
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        return "Leitura de PDF ainda não suportada nesta fase."
    return path.read_text(encoding="utf-8", errors="ignore")
