"""Item model alinhado ao schema inspectah_item_v0_1."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Dict, List, Optional

from .claim import Claim


@dataclass(slots=True)
class InspectahItem:
    """Representa um Item Inspectah nos estados S0–S4."""

    STATES: ClassVar[tuple[str, ...]] = ("S0", "S1", "S2", "S3", "S4")

    source_id: str
    item_id: str
    bundle_id: str
    state: str
    run_id: str
    watcher_type: str
    fetched_at: str
    request_url: str
    status_code: int
    response_size_bytes: int
    content_type: str
    equivalence_key: str
    confidence_local: float
    headline: Optional[str] = None
    published_at: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    facts: Dict[str, object] = field(default_factory=dict)
    claims: List[Claim] = field(default_factory=list)
    reasoning_short: Optional[str] = None
    text_sha256: Optional[str] = None
    bundle_path: Optional[str] = None

    def __post_init__(self) -> None:
        if self.state not in self.STATES:
            raise ValueError(f"Estado inválido: {self.state}")
        if not 0.0 <= float(self.confidence_local) <= 1.0:
            raise ValueError("confidence_local deve estar entre 0 e 1")
        if not self.source_id or not self.item_id:
            raise ValueError("source_id e item_id são obrigatórios")
        self.claims = [claim if isinstance(claim, Claim) else Claim.from_dict(claim) for claim in self.claims]
        self.entities = list(dict.fromkeys(self.entities))  # remove duplicatas preservando ordem

    def to_dict(self) -> dict:
        """Serializa o item para dicionário compatível com os schemas."""
        return {
            "source_id": self.source_id,
            "item_id": self.item_id,
            "bundle_id": self.bundle_id,
            "state": self.state,
            "run_id": self.run_id,
            "watcher_type": self.watcher_type,
            "fetched_at": self.fetched_at,
            "request_url": self.request_url,
            "status_code": int(self.status_code),
            "response_size_bytes": int(self.response_size_bytes),
            "content_type": self.content_type,
            "headline": self.headline,
            "published_at": self.published_at,
            "entities": self.entities,
            "facts": self.facts,
            "claims": [claim.to_dict() for claim in self.claims],
            "equivalence_key": self.equivalence_key,
            "confidence_local": float(self.confidence_local),
            "reasoning_short": self.reasoning_short,
            "text_sha256": self.text_sha256,
            "bundle_path": self.bundle_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InspectahItem":
        """Cria um item a partir de um dicionário validado."""
        return cls(
            source_id=data["source_id"],
            item_id=data["item_id"],
            bundle_id=data["bundle_id"],
            state=data["state"],
            run_id=data["run_id"],
            watcher_type=data["watcher_type"],
            fetched_at=data["fetched_at"],
            request_url=data["request_url"],
            status_code=int(data["status_code"]),
            response_size_bytes=int(data["response_size_bytes"]),
            content_type=data["content_type"],
            headline=data.get("headline"),
            published_at=data.get("published_at"),
            entities=data.get("entities", []),
            facts=data.get("facts", {}),
            claims=data.get("claims", []),
            equivalence_key=data["equivalence_key"],
            confidence_local=float(data.get("confidence_local", 0.0)),
            reasoning_short=data.get("reasoning_short"),
            text_sha256=data.get("text_sha256"),
            bundle_path=data.get("bundle_path"),
        )
