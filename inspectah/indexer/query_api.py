"""Query API para leitura do índice JSONL."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List, Optional

from inspectah.models import InspectahItem


class QueryAPI:
    """Interface simples de leitura do índice gerado pelo LocalIndexer."""

    def __init__(self, storage_path: str | Path = "data/index") -> None:
        self.storage_path = Path(storage_path)
        self.data_file = self.storage_path / "items.jsonl"

    def _iter_items(self) -> Iterable[InspectahItem]:
        if not self.data_file.exists():
            return iter(())

        def generator() -> Iterable[InspectahItem]:
            with self.data_file.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        yield InspectahItem.from_dict(data)
                    except Exception:
                        continue

        return generator()

    def list_items(self, source_id: Optional[str] = None, equivalence_key: Optional[str] = None) -> List[InspectahItem]:
        results = []
        for item in self._iter_items():
            if source_id and item.source_id != source_id:
                continue
            if equivalence_key and item.equivalence_key != equivalence_key:
                continue
            results.append(item)
        return results

    def get_item(self, item_id: str) -> Optional[InspectahItem]:
        for item in self._iter_items():
            if item.item_id == item_id:
                return item
        return None

    def list_sources(self) -> List[str]:
        return sorted({item.source_id for item in self._iter_items()})
