from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger("inspectah.copiloto.tools")


def log_tool_call(tool_name: str, params: Dict[str, Any], result_summary: str) -> None:
    logger.info("copiloto_tool_call", extra={"tool": tool_name, "params": params, "result": result_summary})
