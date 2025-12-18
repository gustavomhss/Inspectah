"""
Truth Policy DSL Grammar — S37

Defines the grammar and AST nodes for the Policy DSL.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class TokenType(str, Enum):
    """Token types for the policy lexer."""

    # Keywords
    POLICY = "POLICY"
    DOMAIN = "DOMAIN"
    GATE = "GATE"
    REQUIRE = "REQUIRE"
    ON = "ON"
    THEN = "THEN"
    VERSION = "VERSION"

    # Operators
    GTE = ">="
    LTE = "<="
    GT = ">"
    LT = "<"
    EQ = "="
    NEQ = "!="
    AND = "AND"
    OR = "OR"
    NOT = "NOT"

    # Literals
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"

    # Symbols
    LBRACE = "{"
    RBRACE = "}"
    LPAREN = "("
    RPAREN = ")"
    SEMICOLON = ";"
    COMMA = ","

    # Special
    NEWLINE = "NEWLINE"
    EOF = "EOF"


@dataclass
class Token:
    """A single token from the lexer."""

    type: TokenType
    value: Any
    line: int
    column: int


# ==================== AST NODES ====================


@dataclass
class RequireCondition:
    """A REQUIRE condition in the policy."""

    field: str
    operator: str
    value: Union[str, int, float]
    modifier: Optional[str] = None  # e.g., "independent", "strong", "weak"


@dataclass
class OnThenRule:
    """An ON...THEN rule in the policy."""

    condition_field: str
    condition_operator: str
    condition_value: Union[str, int, float]
    action: str
    action_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PolicyAST:
    """
    Abstract Syntax Tree for a parsed policy.

    Example policy:
    ```
    POLICY pilot_politics_v1
    DOMAIN politics
    GATE G2

    REQUIRE sources >= 2 independent
    REQUIRE no_contradiction strong
    REQUIRE evidence_strength >= 0.7

    ON high_confidence THEN auto_approve
    ON low_confidence THEN human_review

    VERSION "1.0.0"
    ```
    """

    name: str
    domain: str
    gate: str
    requirements: List[RequireCondition] = field(default_factory=list)
    rules: List[OnThenRule] = field(default_factory=list)
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> List[str]:
        """Validate the policy and return any errors."""
        errors = []

        if not self.name:
            errors.append("Policy name is required")

        if not self.domain:
            errors.append("Domain is required")

        if not self.gate:
            errors.append("Gate is required")
        elif self.gate not in ("G1", "G2", "G3", "G5", "G6", "G7", "G8", "G9"):
            errors.append(f"Invalid gate: {self.gate}. Must be G1-G9")

        if not self.requirements and not self.rules:
            errors.append("Policy must have at least one REQUIRE or ON...THEN rule")

        # Validate requirement fields
        for req in self.requirements:
            if req.field not in KNOWN_FIELDS:
                errors.append(f"Unknown requirement field: {req.field}")
            if req.modifier and req.modifier not in KNOWN_MODIFIERS:
                errors.append(f"Unknown modifier: {req.modifier}")

        # Validate rule actions and conditions
        for rule in self.rules:
            if rule.action not in KNOWN_ACTIONS:
                errors.append(f"Unknown action: {rule.action}")
            # Only validate condition_field if it's a known condition type
            if (
                rule.condition_field not in KNOWN_CONDITIONS
                and rule.condition_field not in KNOWN_FIELDS
            ):
                errors.append(f"Unknown condition field: {rule.condition_field}")

        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "domain": self.domain,
            "gate": self.gate,
            "requirements": [
                {
                    "field": r.field,
                    "operator": r.operator,
                    "value": r.value,
                    "modifier": r.modifier,
                }
                for r in self.requirements
            ],
            "rules": [
                {
                    "condition_field": r.condition_field,
                    "condition_operator": r.condition_operator,
                    "condition_value": r.condition_value,
                    "action": r.action,
                    "action_params": r.action_params,
                }
                for r in self.rules
            ],
            "version": self.version,
            "metadata": self.metadata,
        }


# ==================== KNOWN FIELDS AND ACTIONS ====================


KNOWN_FIELDS = {
    "sources",
    "evidence_count",
    "evidence_strength",
    "source_diversity",
    "confidence",
    "no_contradiction",
    "temporal_consistency",
    "entity_coverage",
    "claim_age_hours",
    "support_count",
    "opposition_count",
    "risk_level",
}

KNOWN_CONDITIONS = {
    "high_confidence",
    "low_confidence",
    "medium_confidence",
    "disputed",
    "no_evidence",
    "high_risk",
    "low_risk",
}

KNOWN_ACTIONS = {
    "auto_approve",
    "auto_reject",
    "human_review",
    "committee_quorum",
    "escalate",
    "defer",
    "flag_for_review",
}

KNOWN_MODIFIERS = {
    "independent",
    "strong",
    "weak",
}
