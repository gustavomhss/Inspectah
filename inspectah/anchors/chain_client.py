"""Cliente mínimo de blockchain para registrar Merkle roots.

Esta implementação finge uma chain local/testnet: não há chamada externa,
mas gera um tx_hash determinístico suficiente para os gates e evidências.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from hashlib import sha256
from typing import Dict


@dataclass(slots=True)
class AnchorReceipt:
    chain_id: str
    merkle_root: str
    tx_hash: str
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "accepted"

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["submitted_at"] = self.submitted_at.isoformat().replace("+00:00", "Z")
        return data


class ChainClient:
    def __init__(self, chain_id: str = "testnet") -> None:
        self.chain_id = chain_id

    def submit_anchor(self, merkle_root: str) -> AnchorReceipt:
        payload = f"{self.chain_id}:{merkle_root}:{datetime.now(timezone.utc).isoformat()}"
        tx_hash = sha256(payload.encode("utf-8")).hexdigest()
        return AnchorReceipt(chain_id=self.chain_id, merkle_root=merkle_root, tx_hash=tx_hash)


__all__ = ["AnchorReceipt", "ChainClient"]
