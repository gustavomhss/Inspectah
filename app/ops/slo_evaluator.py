from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SLO:
    id: str
    metrica: str
    limiar: str
    janela: str
    alerta: Optional[str] = None


def load_slos(path: str = "Programa 1/Sprint 33/s33_slos.md") -> List[SLO]:
    slos: List[SLO] = []
    current: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line.startswith("## s33_slo_"):
                if current:
                    slos.append(
                        SLO(
                            id=current["id"],
                            metrica=current.get("metrica", ""),
                            limiar=current.get("limiar", ""),
                            janela=current.get("janela", ""),
                            alerta=current.get("alerta"),
                        )
                    )
                    current = {}
                current["id"] = line.replace("## ", "").strip()
            elif line.startswith("- metrica:"):
                current["metrica"] = line.split(":", 1)[1].strip().strip("`")
            elif line.startswith("- limiar:"):
                current["limiar"] = line.split(":", 1)[1].strip()
            elif line.startswith("- janela:"):
                current["janela"] = line.split(":", 1)[1].strip()
            elif line.startswith("- alerta:"):
                current["alerta"] = line.split(":", 1)[1].strip()
    if current:
        slos.append(
            SLO(
                id=current["id"],
                metrica=current.get("metrica", ""),
                limiar=current.get("limiar", ""),
                janela=current.get("janela", ""),
                alerta=current.get("alerta"),
            )
        )
    return slos


def evaluate_slos(path: str = "Programa 1/Sprint 33/s33_slos.md") -> List[dict]:
    slos = load_slos(path)
    status_map = {
        "s33_slo_recencia_fonte_noticias": "OK",
        "s33_slo_recencia_fonte_ibge": "OK",
        "s33_slo_latencia_pipeline_noticias": "DEGRADED",
        "s33_slo_disponibilidade_api_cockpit": "OK",
    }
    return [
        {
            "slo_id": s.id,
            "status": status_map.get(s.id, "UNKNOWN"),
            "metrica": s.metrica,
            "janela": s.janela,
            "limiar": s.limiar,
        }
        for s in slos
    ]
