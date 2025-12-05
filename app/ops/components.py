from __future__ import annotations

import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class Component:
    id: str
    tipo: str
    criticidade: str
    descricao: Optional[str] = None
    slos: Optional[List[str]] = None
    flow_id: Optional[str] = None
    flow_version_id: Optional[str] = None


def _load_single(path: Path) -> List[Component]:
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text()) or {}
    comps = []
    for raw in data.get("components", []):
        comps.append(
            Component(
                id=raw["id"],
                tipo=raw.get("tipo", ""),
                criticidade=raw.get("criticidade", ""),
                descricao=raw.get("descricao"),
                slos=raw.get("slos") or [],
                flow_id=raw.get("flow_id"),
                flow_version_id=raw.get("flow_version_id"),
            )
        )
    return comps


def load_components_map(path: Path | str = "Programa 1/Epico 28/Sprint 34/s34_components_map.yaml") -> List[Component]:
    # Carrega mapa principal (S34) e, se existir, o mapa legado da S33 para compatibilidade com testes/operadores.
    primary = Path(path)
    legacy = Path("Programa 1/Sprint 33/s33_components_map.yaml")
    merged: Dict[str, Component] = {}
    for p in (primary, legacy):
        for comp in _load_single(p):
            merged[comp.id] = comp
    return list(merged.values())


def component_ids(path: Path | str = "Programa 1/Epico 28/Sprint 34/s34_components_map.yaml") -> List[str]:
    return [c.id for c in load_components_map(path)]
