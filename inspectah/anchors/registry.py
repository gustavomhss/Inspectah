"""Registro interno de âncoras do Sistema de Blocos."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


@dataclass(slots=True)
class AnchorRecord:
    anchor_id: str
    chain_id: str
    tx_hash: str
    merkle_root: str
    items: Sequence[str] = field(default_factory=tuple)
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "anchor_id": self.anchor_id,
            "chain_id": self.chain_id,
            "tx_hash": self.tx_hash,
            "merkle_root": self.merkle_root,
            "items": list(self.items),
            "metadata": self.metadata,
        }


class AnchorRegistry:
    def __init__(self, store_path: Path | None = None) -> None:
        self._anchors: Dict[str, AnchorRecord] = {}
        self._by_fact: Dict[str, List[str]] = {}
        self._store_path = store_path
        if store_path and store_path.exists():
            self._load(store_path)

    def register(self, record: AnchorRecord, *, facts: Iterable[str] = ()) -> None:
        self._anchors[record.anchor_id] = record
        for fact_id in facts:
            bucket = self._by_fact.setdefault(str(fact_id), [])
            if record.anchor_id not in bucket:
                bucket.append(record.anchor_id)
        self._persist()

    def anchors_for_fact(self, fact_id: str) -> Sequence[AnchorRecord]:
        anchor_ids = self._by_fact.get(str(fact_id), [])
        return [self._anchors[aid] for aid in anchor_ids if aid in self._anchors]

    def get(self, anchor_id: str) -> AnchorRecord | None:
        return self._anchors.get(anchor_id)

    def snapshot(self) -> Dict[str, object]:
        return {
            "anchors": {k: v.to_dict() for k, v in self._anchors.items()},
            "by_fact": self._by_fact,
        }

    def _persist(self) -> None:
        if not self._store_path:
            return
        payload = self.snapshot()
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        for anchor_id, raw in data.get("anchors", {}).items():
            record = AnchorRecord(
                anchor_id=anchor_id,
                chain_id=raw["chain_id"],
                tx_hash=raw["tx_hash"],
                merkle_root=raw["merkle_root"],
                items=tuple(raw.get("items", [])),
                metadata=raw.get("metadata", {}),
            )
            self._anchors[anchor_id] = record
        self._by_fact = {k: list(v) for k, v in data.get("by_fact", {}).items()}


__all__ = ["AnchorRecord", "AnchorRegistry"]
