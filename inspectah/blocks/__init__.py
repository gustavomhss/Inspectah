"""Extensões leves do modelo de blocos para incluir âncoras e sinais da S15."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Sequence

from inspectah.anchors.registry import AnchorRegistry
from inspectah.truthdb.models import TruthDB


@dataclass(slots=True)
class AnchoredFact:
    fact_id: str
    state: str
    anchors: Sequence[Dict[str, object]] = field(default_factory=tuple)
    debunker_refs: Sequence[str] = field(default_factory=tuple)
    committee_refs: Sequence[str] = field(default_factory=tuple)


def snapshot_with_anchors(db: TruthDB, registry: AnchorRegistry) -> Dict[str, AnchoredFact]:
    snap = db.snapshot()
    anchored: Dict[str, AnchoredFact] = {}
    for fact_id, estado in snap["estados"].items():
        anchors = [record.to_dict() for record in registry.anchors_for_fact(fact_id)]
        anchored[fact_id] = AnchoredFact(
            fact_id=fact_id,
            state=str(estado.estado_atual.value),
            anchors=anchors,
            debunker_refs=[],
            committee_refs=[],
        )
    return anchored


__all__ = ["AnchoredFact", "snapshot_with_anchors"]
