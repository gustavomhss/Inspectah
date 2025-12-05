from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Component:
    id: str
    tipo: str
    criticidade: str
    descricao: Optional[str] = None
    slos: Optional[List[str]] = None


def load_components_map(path: Path | str = "Programa 1/Sprint 33/s33_components_map.yaml") -> List[Component]:
    data = yaml.safe_load(Path(path).read_text())
    comps = []
    for raw in data.get("components", []):
        comps.append(
            Component(
                id=raw["id"],
                tipo=raw.get("tipo", ""),
                criticidade=raw.get("criticidade", ""),
                descricao=raw.get("descricao"),
                slos=raw.get("slos") or [],
            )
        )
    return comps


def component_ids(path: Path | str = "Programa 1/Sprint 33/s33_components_map.yaml") -> List[str]:
    return [c.id for c in load_components_map(path)]
