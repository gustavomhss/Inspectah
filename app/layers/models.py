from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class LayerExecution:
    layer_name: str
    input_snapshot: Dict[str, Any]
    output_snapshot: Dict[str, Any]
    status: str = "OK"
    created_at: datetime = field(default_factory=utcnow)


@dataclass
class LayersTrace:
    claim_id: str
    pipeline: str
    executions: List[LayerExecution] = field(default_factory=list)
    created_at: datetime = field(default_factory=utcnow)

    def add_execution(self, execution: LayerExecution) -> None:
        self.executions.append(execution)
