from pathlib import Path

from inspectah.truthdb.invariants import validate_state_machine_alignment
from inspectah.truthdb.state_machine import (
    FactState,
    InvalidStateTransition,
    StateMachine,
    load_state_machine_spec,
)


def test_default_machine_matches_config():
    spec = load_state_machine_spec(Path("config/s10_state_machine.yml"))
    sm = StateMachine()
    validate_state_machine_alignment(sm, spec)


def test_valid_transitions_pass():
    sm = StateMachine()
    sm.validate_transition(FactState.PLANEJADO, FactState.CONFIRMADO)
    sm.validate_transition(FactState.CONFIRMADO, FactState.CONCLUIDO)


def test_invalid_transitions_raise():
    sm = StateMachine()
    for origin, target in [
        (FactState.CONCLUIDO, FactState.PLANEJADO),
        (FactState.CANCELADO, FactState.CONFIRMADO),
    ]:
        try:
            sm.validate_transition(origin, target)
        except InvalidStateTransition:
            continue
        raise AssertionError(f"Transição {origin.value}->{target.value} deveria falhar")


def test_invalid_transition_ratio_is_perfect():
    sm = StateMachine()
    value = sm.invalid_transition_rejection_ratio()
    if abs(value - 1.0) > 1e-6:
        raise AssertionError(f"Esperado 1.0, obtido {value}")
