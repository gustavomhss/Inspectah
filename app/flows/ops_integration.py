from __future__ import annotations

import logging
from typing import Dict

logger = logging.getLogger("flows.ops_integration")


def emit_event(event_type: str, flow_id: str, flow_version_id: str, payload: Dict) -> None:
    """
    Placeholder para integração com OracleOps v2.
    Garante que sempre enviamos flow_id/flow_version_id.
    """
    logger.info(
        "flow_ops_event",
        extra={
            "event_type": event_type,
            "flow_id": flow_id,
            "flow_version_id": flow_version_id,
            **payload,
        },
    )
