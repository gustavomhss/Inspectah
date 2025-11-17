from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Iterable, Mapping, Optional, Sequence, Set

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


class InvalidStateTransition(RuntimeError):
    """Erro disparado ao tentar aplicar uma transição proibida."""


class FactState(str, Enum):
    PLANEJADO = "planejado"
    CONFIRMADO = "confirmado"
    CONCLUIDO = "concluido"
    NAO_CONFIRMADO = "nao_confirmado"
    ADIADO = "adiado"
    CANCELADO = "cancelado"
    INCERTO = "incerto"

    @classmethod
    def ordered(cls) -> Sequence["FactState"]:
        return (
            cls.PLANEJADO,
            cls.CONFIRMADO,
            cls.CONCLUIDO,
            cls.NAO_CONFIRMADO,
            cls.ADIADO,
            cls.CANCELADO,
            cls.INCERTO,
        )


DEFAULT_TRANSITIONS: Dict[str, Set[str]] = {
    FactState.PLANEJADO: {
        FactState.CONFIRMADO,
        FactState.ADIADO,
        FactState.CANCELADO,
        FactState.INCERTO,
    },
    FactState.CONFIRMADO: {
        FactState.CONCLUIDO,
        FactState.ADIADO,
        FactState.CANCELADO,
        FactState.NAO_CONFIRMADO,
    },
    FactState.CONCLUIDO: {FactState.INCERTO},
    FactState.NAO_CONFIRMADO: {FactState.CONFIRMADO, FactState.CANCELADO},
    FactState.ADIADO: {FactState.CONFIRMADO, FactState.CANCELADO, FactState.INCERTO},
    FactState.CANCELADO: set(),
    FactState.INCERTO: {FactState.CONFIRMADO, FactState.CANCELADO, FactState.NAO_CONFIRMADO},
}


@dataclass(frozen=True)
class TransitionAttempt:
    origin: FactState
    target: FactState
    allowed: bool


class StateMachine:
    def __init__(self, transitions: Optional[Mapping[str, Iterable[str]]] = None) -> None:
        raw = transitions or DEFAULT_TRANSITIONS
        self._allowed: Dict[FactState, Set[FactState]] = {
            self._coerce_state(origin): {self._coerce_state(dest) for dest in targets}
            for origin, targets in raw.items()
        }

    def is_valid_state(self, state: object) -> bool:
        try:
            self._coerce_state(state)
        except ValueError:
            return False
        return True

    def is_valid_transition(self, origin: FactState, target: FactState) -> bool:
        origin_state = self._coerce_state(origin)
        target_state = self._coerce_state(target)
        return target_state in self._allowed.get(origin_state, set())

    def validate_transition(self, origin: FactState, target: FactState) -> None:
        if not self.is_valid_transition(origin, target):
            raise InvalidStateTransition(f"Transição proibida: {origin.value} -> {target.value}")

    def describe(self) -> Dict[str, Sequence[str]]:
        return {
            origin.value: sorted(dest.value for dest in targets)
            for origin, targets in self._allowed.items()
        }

    def coverage_suite(self) -> Sequence[TransitionAttempt]:
        attempts: list[TransitionAttempt] = []
        for origin in self._allowed.keys():
            for candidate in FactState.ordered():
                attempts.append(
                    TransitionAttempt(
                        origin=origin,
                        target=candidate,
                        allowed=self.is_valid_transition(origin, candidate),
                    )
                )
        return attempts

    def invalid_transition_rejection_ratio(self) -> float:
        attempts = self.coverage_suite()
        invalid = [attempt for attempt in attempts if not attempt.allowed]
        if not invalid:
            return 1.0
        rejected = 0
        for attempt in invalid:
            try:
                self.validate_transition(attempt.origin, attempt.target)
            except InvalidStateTransition:
                rejected += 1
        return rejected / len(invalid)

    @staticmethod
    def _coerce_state(value: object) -> FactState:
        if isinstance(value, FactState):
            return value
        text = str(value)
        if text.startswith("FactState."):
            text = text.split(".", 1)[1]
        return FactState(text.lower())


def load_state_machine_spec(path: Path) -> Dict[str, Sequence[str]]:
    text = path.read_text()
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = _parse_simple_yaml(text)
    return {origin: tuple(targets) for origin, targets in data["transitions"].items()}


def _parse_simple_yaml(text: str) -> Dict[str, Sequence[str]]:
    states: list[str] = []
    transitions: Dict[str, list[str]] = {}
    current_section = None
    current_state = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":") and ":" not in line[:-1]:
            key = line[:-1]
            if key in {"states", "transitions"}:
                current_section = key
                current_state = None
            else:
                current_state = key
                transitions.setdefault(current_state, [])
            continue
        if ":" in line and current_section == "transitions" and not line.startswith("-"):
            key, value = line.split(":", 1)
            key = key.strip()
            values = [v.strip() for v in value.strip().strip("[]").split(",") if v.strip()]
            transitions[key] = values
            current_state = key
            continue
        if line.startswith("- "):
            item = line[2:].strip()
            if current_section == "states":
                states.append(item)
            elif current_section == "transitions" and current_state:
                transitions.setdefault(current_state, []).append(item)
    return {"states": states, "transitions": transitions}
