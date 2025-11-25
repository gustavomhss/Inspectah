from __future__ import annotations

from typing import Dict, Set

from .models import SourceState

# Transições válidas alinhadas à ontologia v2 (aprovar, suspender, desativar/reativar).
ALLOWED_TRANSITIONS: Dict[SourceState, Set[SourceState]] = {
    SourceState.PROPOSED: {SourceState.TESTING, SourceState.ACTIVE},
    SourceState.TESTING: {SourceState.ACTIVE, SourceState.UNDER_REVIEW},
    SourceState.ACTIVE: {SourceState.UNDER_REVIEW, SourceState.SUSPECT, SourceState.DISABLED_TEMP},
    SourceState.UNDER_REVIEW: {
        SourceState.ACTIVE,
        SourceState.SUSPECT,
        SourceState.DISABLED_TEMP,
        SourceState.DISABLED_PERM,
    },
    SourceState.SUSPECT: {SourceState.UNDER_REVIEW, SourceState.DISABLED_TEMP, SourceState.DISABLED_PERM},
    SourceState.DISABLED_TEMP: {SourceState.UNDER_REVIEW, SourceState.ACTIVE},
    SourceState.DISABLED_PERM: set(),
}


def can_transition(from_state: SourceState, to_state: SourceState) -> bool:
    if from_state == SourceState.DISABLED_PERM:
        return False
    if to_state == SourceState.DISABLED_PERM:
        return True
    return to_state in ALLOWED_TRANSITIONS.get(from_state, set())


def assert_valid_transition(from_state: SourceState, to_state: SourceState) -> None:
    if not can_transition(from_state, to_state):
        raise ValueError(f"Transição inválida: {from_state.value} -> {to_state.value}")
