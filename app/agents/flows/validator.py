from __future__ import annotations

from typing import Iterable, List, Sequence

from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowConfigOut, AgentFlowStepIn, AgentFlowStepOut
from app.agents.models import AgentRole

# Permitted param keys to avoid "magic" knobs sneaking into the flow.
ALLOWED_PARAM_KEYS = {"committee_id", "strict_mode", "threshold", "max_depth", "notes", "allow_retry"}
REQUIRED_ROLES = {AgentRole.INTERPRETER.value, AgentRole.CLASSIFIER.value, AgentRole.DECISION_MAKER.value}


class AgentFlowValidationError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def _normalize_role(role: str | AgentRole) -> str:
    return role.value if isinstance(role, AgentRole) else str(role)


def _normalize_steps(steps: Iterable[AgentFlowStepIn | AgentFlowStepOut]) -> List[AgentFlowStepIn | AgentFlowStepOut]:
    return list(steps)


def validate_agent_flow(config: AgentFlowConfigIn | AgentFlowConfigOut) -> List[str]:
    errors: List[str] = []
    steps: Sequence[AgentFlowStepIn | AgentFlowStepOut] = _normalize_steps(config.steps)
    if not steps:
        return ["Flow must contain at least one step"]

    positions = [s.position for s in steps]
    if len(set(positions)) != len(positions):
        errors.append("Flow has duplicate step positions")

    expected_positions = list(range(1, len(positions) + 1))
    if sorted(positions) != expected_positions:
        errors.append("Step positions must start at 1 and be contiguous with no gaps")

    allowed_roles = {r.value for r in AgentRole}
    role_sequence: List[str] = []
    for step in steps:
        role_value = _normalize_role(step.agent_role)
        role_sequence.append(role_value)
        if role_value not in allowed_roles:
            errors.append(f"Unknown agent role '{role_value}'")
        if not isinstance(step.params, dict):
            errors.append(f"Step at position {step.position} has invalid params (must be object)")
        else:
            unknown_keys = set(step.params.keys()) - ALLOWED_PARAM_KEYS
            if unknown_keys:
                errors.append(f"Step at position {step.position} has unsupported params keys: {sorted(unknown_keys)}")

    if not REQUIRED_ROLES.issubset(set(role_sequence)):
        missing = REQUIRED_ROLES - set(role_sequence)
        errors.append(f"Missing required roles: {sorted(missing)}")

    decision_positions = [idx for idx, role in enumerate(role_sequence, start=1) if role == AgentRole.DECISION_MAKER.value]
    if len(decision_positions) > 1:
        errors.append("Decision maker role must appear only once")
    if decision_positions:
        if decision_positions[0] != len(role_sequence):
            errors.append("Decision maker must be the last step in the flow")
        # enforce that interpreter/classifier occur before decision maker
        dm_index = decision_positions[0]
        if AgentRole.INTERPRETER.value not in role_sequence[: dm_index - 1]:
            errors.append("Interpreter must appear before the decision maker")
        if AgentRole.CLASSIFIER.value not in role_sequence[: dm_index - 1]:
            errors.append("Classifier must appear before the decision maker")

    return errors
