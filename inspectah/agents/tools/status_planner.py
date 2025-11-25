from __future__ import annotations

from typing import Dict

from app.sources import status as domain_status
from app.sources.models import SourceState


def plan_status_change(current: str, target: str, reason: str = "") -> Dict:
    current_value = current.value if hasattr(current, "value") else current
    target_value = target.value if hasattr(target, "value") else target
    current_state = SourceState(current_value)
    target_state = SourceState(target_value)
    domain_status.assert_valid_transition(current_state, target_state)
    return {
        "from_state": current_state.value,
        "to_state": target_state.value,
        "reason": reason or "Plano de mudança de status a confirmar pelo admin.",
    }
