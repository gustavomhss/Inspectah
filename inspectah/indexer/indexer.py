"""Indexer simples para a Fase 2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from inspectah.models import InspectahItem


class LocalIndexer:
    """Persiste itens S3 em arquivo JSON lines consultável."""

    def __init__(self, storage_path: str | Path = "data/index") -> None:
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.data_file = self.storage_path / "items.jsonl"
        if not self.data_file.exists():
            self.data_file.write_text("")

    def index(self, item: InspectahItem) -> None:
        if item.state != "S3":
            raise ValueError("Somente itens S3 podem ser indexados")
        record = item.to_dict()
        with self.data_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def query(self, *, source_id: Optional[str] = None, equivalence_key: Optional[str] = None) -> List[InspectahItem]:
        results: List[InspectahItem] = []
        for line in self.data_file.read_text().splitlines():
            if not line:
                continue
            data = json.loads(line)
            if source_id and data.get("source_id") != source_id:
                continue
            if equivalence_key and data.get("equivalence_key") != equivalence_key:
                continue
            results.append(InspectahItem.from_dict(data))
        return results
