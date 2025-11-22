"""Batcher de eventos/versões para geração de Merkle roots e âncoras."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Sequence

from .chain_client import AnchorReceipt, ChainClient
from .merkle import build_merkle_root


@dataclass(slots=True)
class BatchResult:
    anchor_id: str
    merkle_root: str
    receipt: AnchorReceipt
    items: Sequence[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "anchor_id": self.anchor_id,
            "merkle_root": self.merkle_root,
            "receipt": self.receipt.to_dict(),
            "items": list(self.items),
        }


class Batcher:
    def __init__(self, *, max_entries: int = 5, max_age_seconds: int = 300, chain: ChainClient | None = None) -> None:
        self.max_entries = max_entries
        self.max_age = timedelta(seconds=max_age_seconds)
        self.chain = chain or ChainClient()
        self._pending: List[str] = []
        self._pending_since: datetime | None = None
        self._counter = 0
        self._history: List[BatchResult] = []
        self._failure_log: List[Dict[str, object]] = []
        self._last_failure: Dict[str, object] | None = None

    def add_entry(self, entry: str) -> BatchResult | None:
        now = datetime.now(timezone.utc)
        self._pending.append(entry)
        self._pending_since = self._pending_since or now
        if len(self._pending) >= self.max_entries or (now - self._pending_since) >= self.max_age:
            return self.flush()
        return None

    def flush(self) -> BatchResult:
        if not self._pending:
            raise RuntimeError("nenhum item para ancorar")
        merkle_root = build_merkle_root(self._pending)
        try:
            receipt = self.chain.submit_anchor(merkle_root)
        except Exception as exc:  # noqa: BLE001
            failure = {"error": str(exc), "pending": list(self._pending)}
            self._last_failure = failure
            self._failure_log.append(failure)
            raise
        self._counter += 1
        anchor_id = f"anchor-{self._counter}"
        result = BatchResult(anchor_id=anchor_id, merkle_root=merkle_root, receipt=receipt, items=tuple(self._pending))
        self._history.append(result)
        self._pending = []
        self._pending_since = None
        return result

    @property
    def history(self) -> Sequence[BatchResult]:
        return tuple(self._history)

    @property
    def pending_items(self) -> Sequence[str]:
        return tuple(self._pending)

    @property
    def failures(self) -> Sequence[Dict[str, object]]:
        return tuple(self._failure_log)

    @property
    def last_failure(self) -> Dict[str, object] | None:
        return self._last_failure


__all__ = ["Batcher", "BatchResult"]
