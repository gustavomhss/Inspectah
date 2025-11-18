from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = REPO_ROOT / "config" / "ui_sprint_7.yaml"


@dataclass(slots=True)
class UISettings:
    host: str = "127.0.0.1"
    port: int = 8077
    debug: bool = False
    version: str = "sprint7-alpha"
    title: str = "Inspectah UI Alpha"

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def _load_yaml(path: Path) -> Mapping[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise ValueError(f"{path} deve conter um mapeamento de configuração")
    return data


@lru_cache(maxsize=1)
def get_settings(config_path: str | Path | None = None) -> UISettings:
    path = Path(config_path) if config_path else DEFAULT_CONFIG
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    data: Mapping[str, Any] = {}
    if path.exists():
        data = _load_yaml(path)
    host = str(data.get("host", "127.0.0.1"))
    port = int(data.get("port", 8077))
    debug = bool(data.get("debug", False))
    version = str(data.get("version", "sprint7-alpha"))
    title = str(data.get("title", "Inspectah UI Alpha"))
    return UISettings(host=host, port=port, debug=debug, version=version, title=title)
