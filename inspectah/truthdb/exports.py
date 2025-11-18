from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Dict, Sequence

from .models import TruthDB


def export_truthdb(truthdb: TruthDB) -> Dict[str, object]:
    return _convert(truthdb.snapshot())


def export_facts(truthdb: TruthDB, fact_ids: Sequence[str]) -> Dict[str, object]:
    snapshot = truthdb.snapshot()
    versoes = snapshot["versoes"]
    estados = snapshot["estados"]
    complementos = snapshot["complementos"]
    exports: Dict[str, object] = {}
    for fid in fact_ids:
        fato = snapshot["fatos"].get(fid)
        if fato is None:
            continue
        exports[fid] = {
            "fato": _convert(fato),
            "versoes": [_convert(v) for v in versoes.values() if v.fato_id == fid],
            "estado": _convert(estados.get(fid)),
            "complementos": [_convert(c) for c in complementos.values() if c.fato_id == fid],
        }
    return exports


def audit_trace_completeness(fact_exports: Dict[str, object]) -> float:
    if not fact_exports:
        return 1.0
    complete = 0
    for data in fact_exports.values():
        versoes = data.get("versoes", [])
        estado = data.get("estado")
        if versoes and estado:
            complete += 1
    return round(complete / len(fact_exports), 4)


def future_ready_completeness(fact_exports: Dict[str, object]) -> float:
    if not fact_exports:
        return 1.0
    ready = 0
    for data in fact_exports.values():
        fato = data.get("fato") or {}
        there_hash = bool(fato.get("hash_conteudo"))
        there_anchor = bool(fato.get("ancora_externa"))
        evidencias = fato.get("evidencias", [])
        versoes = data.get("versoes", [])
        versao_hashes = all(v.get("hash_conteudo") for v in versoes)
        if there_hash and there_anchor and evidencias and versao_hashes:
            ready += 1
    return round(ready / len(fact_exports), 4)


def build_export_metrics(fact_exports: Dict[str, object]) -> Dict[str, float]:
    return {
        "audit_trace_completeness": audit_trace_completeness(fact_exports),
        "future_ready_completeness": future_ready_completeness(fact_exports),
        "facts_count": len(fact_exports),
    }


def _convert(value):
    if is_dataclass(value):
        return _convert(asdict(value))
    if isinstance(value, dict):
        return {k: _convert(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_convert(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value
