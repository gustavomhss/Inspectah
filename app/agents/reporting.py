from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class AgentReport:
    agent_id: str
    committee_id: Optional[str]
    role: str
    status: str
    bundle_ref: Optional[str]
    notes: Optional[str]
    created_at: datetime = datetime.utcnow()
    payload: Dict[str, Any] = None  # type: ignore[assignment]


def log_agent_report(report: AgentReport) -> None:
    """Structured log for reports produced by agents. This is a stub for S23 and will be wired to metrics later."""
    payload = report.payload or {}
    entry = {**asdict(report), "payload": payload}
    logger.info("agent.report", extra={"event": entry})


def log_committee_decision(committee_id: str, run_id: str, outcome: str, disagreement_score: float | None = None) -> None:
    logger.info(
        "committee.decision",
        extra={
            "committee_id": committee_id,
            "run_id": run_id,
            "outcome": outcome,
            "disagreement_score": disagreement_score,
            "ts": datetime.utcnow().isoformat(),
        },
    )
