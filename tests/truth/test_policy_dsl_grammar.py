"""
Tests for Truth Policy DSL Grammar — S37

Tests for policy grammar tokens and AST nodes.
"""

import pytest

from app.truth.policy_dsl.grammar import (
    KNOWN_ACTIONS,
    KNOWN_CONDITIONS,
    KNOWN_FIELDS,
    KNOWN_MODIFIERS,
    OnThenRule,
    PolicyAST,
    RequireCondition,
    Token,
    TokenType,
)


class TestTokenType:
    """Tests for TokenType enum."""

    def test_keywords(self):
        """Token types include keywords."""
        assert TokenType.POLICY.value == "POLICY"
        assert TokenType.DOMAIN.value == "DOMAIN"
        assert TokenType.GATE.value == "GATE"
        assert TokenType.REQUIRE.value == "REQUIRE"
        assert TokenType.ON.value == "ON"
        assert TokenType.THEN.value == "THEN"
        assert TokenType.VERSION.value == "VERSION"

    def test_operators(self):
        """Token types include operators."""
        assert TokenType.GTE.value == ">="
        assert TokenType.LTE.value == "<="
        assert TokenType.GT.value == ">"
        assert TokenType.LT.value == "<"
        assert TokenType.EQ.value == "="
        assert TokenType.NEQ.value == "!="
        assert TokenType.AND.value == "AND"
        assert TokenType.OR.value == "OR"
        assert TokenType.NOT.value == "NOT"

    def test_literals(self):
        """Token types include literals."""
        assert TokenType.IDENTIFIER.value == "IDENTIFIER"
        assert TokenType.NUMBER.value == "NUMBER"
        assert TokenType.STRING.value == "STRING"

    def test_symbols(self):
        """Token types include symbols."""
        assert TokenType.LBRACE.value == "{"
        assert TokenType.RBRACE.value == "}"
        assert TokenType.LPAREN.value == "("
        assert TokenType.RPAREN.value == ")"
        assert TokenType.SEMICOLON.value == ";"
        assert TokenType.COMMA.value == ","

    def test_special(self):
        """Token types include special tokens."""
        assert TokenType.NEWLINE.value == "NEWLINE"
        assert TokenType.EOF.value == "EOF"


class TestToken:
    """Tests for Token dataclass."""

    def test_create_token(self):
        """Create a token."""
        token = Token(
            type=TokenType.IDENTIFIER,
            value="sources",
            line=1,
            column=5,
        )

        assert token.type == TokenType.IDENTIFIER
        assert token.value == "sources"
        assert token.line == 1
        assert token.column == 5

    def test_create_number_token(self):
        """Create a number token."""
        token = Token(
            type=TokenType.NUMBER,
            value=42,
            line=2,
            column=10,
        )

        assert token.type == TokenType.NUMBER
        assert token.value == 42


class TestRequireCondition:
    """Tests for RequireCondition dataclass."""

    def test_create_basic(self):
        """Create basic requirement."""
        req = RequireCondition(
            field="sources",
            operator=">=",
            value=2,
        )

        assert req.field == "sources"
        assert req.operator == ">="
        assert req.value == 2
        assert req.modifier is None

    def test_create_with_modifier(self):
        """Create requirement with modifier."""
        req = RequireCondition(
            field="sources",
            operator=">=",
            value=2,
            modifier="independent",
        )

        assert req.modifier == "independent"

    def test_boolean_requirement(self):
        """Create boolean requirement."""
        req = RequireCondition(
            field="no_contradiction",
            operator="=",
            value=True,
            modifier="strong",
        )

        assert req.value is True
        assert req.modifier == "strong"


class TestOnThenRule:
    """Tests for OnThenRule dataclass."""

    def test_create_basic(self):
        """Create basic rule."""
        rule = OnThenRule(
            condition_field="high_confidence",
            condition_operator="=",
            condition_value=True,
            action="auto_approve",
        )

        assert rule.condition_field == "high_confidence"
        assert rule.action == "auto_approve"
        assert rule.action_params == {}

    def test_create_with_params(self):
        """Create rule with action params."""
        rule = OnThenRule(
            condition_field="low_confidence",
            condition_operator="=",
            condition_value=True,
            action="human_review",
            action_params={"priority": "high", "timeout": 3600},
        )

        assert rule.action_params["priority"] == "high"
        assert rule.action_params["timeout"] == 3600

    def test_create_comparison_rule(self):
        """Create rule with comparison condition."""
        rule = OnThenRule(
            condition_field="evidence_count",
            condition_operator="<",
            condition_value=3,
            action="flag_for_review",
        )

        assert rule.condition_operator == "<"
        assert rule.condition_value == 3


class TestPolicyAST:
    """Tests for PolicyAST dataclass."""

    def test_create_minimal(self):
        """Create minimal policy."""
        policy = PolicyAST(
            name="test_policy",
            domain="politics",
            gate="G1",
        )

        assert policy.name == "test_policy"
        assert policy.domain == "politics"
        assert policy.gate == "G1"
        assert policy.version == "1.0.0"

    def test_create_full(self):
        """Create full policy."""
        policy = PolicyAST(
            name="full_policy",
            domain="health",
            gate="G2",
            requirements=[
                RequireCondition("sources", ">=", 2),
                RequireCondition("evidence_strength", ">=", 0.7),
            ],
            rules=[
                OnThenRule("high_confidence", "=", True, "auto_approve"),
                OnThenRule("low_confidence", "=", True, "human_review"),
            ],
            version="2.0.0",
            metadata={"author": "test"},
        )

        assert len(policy.requirements) == 2
        assert len(policy.rules) == 2
        assert policy.version == "2.0.0"
        assert policy.metadata["author"] == "test"

    def test_validate_valid_policy(self):
        """Validate a valid policy."""
        policy = PolicyAST(
            name="valid_policy",
            domain="politics",
            gate="G1",
            requirements=[
                RequireCondition("sources", ">=", 2),
            ],
        )

        errors = policy.validate()
        assert len(errors) == 0

    def test_validate_missing_name(self):
        """Validate catches missing name."""
        policy = PolicyAST(
            name="",
            domain="politics",
            gate="G1",
            requirements=[RequireCondition("sources", ">=", 1)],
        )

        errors = policy.validate()
        assert any("name" in e.lower() for e in errors)

    def test_validate_missing_domain(self):
        """Validate catches missing domain."""
        policy = PolicyAST(
            name="test",
            domain="",
            gate="G1",
            requirements=[RequireCondition("sources", ">=", 1)],
        )

        errors = policy.validate()
        assert any("domain" in e.lower() for e in errors)

    def test_validate_missing_gate(self):
        """Validate catches missing gate."""
        policy = PolicyAST(
            name="test",
            domain="politics",
            gate="",
            requirements=[RequireCondition("sources", ">=", 1)],
        )

        errors = policy.validate()
        assert any("gate" in e.lower() for e in errors)

    def test_validate_invalid_gate(self):
        """Validate catches invalid gate."""
        policy = PolicyAST(
            name="test",
            domain="politics",
            gate="G99",
            requirements=[RequireCondition("sources", ">=", 1)],
        )

        errors = policy.validate()
        assert any("invalid gate" in e.lower() for e in errors)

    def test_validate_valid_gates(self):
        """All valid gates are accepted."""
        valid_gates = ["G1", "G2", "G3", "G5", "G6", "G7", "G8", "G9"]
        for gate in valid_gates:
            policy = PolicyAST(
                name="test",
                domain="politics",
                gate=gate,
                requirements=[RequireCondition("sources", ">=", 1)],
            )
            errors = policy.validate()
            assert not any("invalid gate" in e.lower() for e in errors)

    def test_validate_no_rules(self):
        """Validate catches no rules or requirements."""
        policy = PolicyAST(
            name="test",
            domain="politics",
            gate="G1",
        )

        errors = policy.validate()
        assert any("at least one" in e.lower() for e in errors)

    def test_validate_unknown_field(self):
        """Validate catches unknown requirement field."""
        policy = PolicyAST(
            name="test",
            domain="politics",
            gate="G1",
            requirements=[RequireCondition("unknown_field", ">=", 1)],
        )

        errors = policy.validate()
        assert any("unknown" in e.lower() and "field" in e.lower() for e in errors)

    def test_validate_unknown_modifier(self):
        """Validate catches unknown modifier."""
        policy = PolicyAST(
            name="test",
            domain="politics",
            gate="G1",
            requirements=[
                RequireCondition("sources", ">=", 1, modifier="unknown_modifier")
            ],
        )

        errors = policy.validate()
        assert any("modifier" in e.lower() for e in errors)

    def test_validate_unknown_action(self):
        """Validate catches unknown action."""
        policy = PolicyAST(
            name="test",
            domain="politics",
            gate="G1",
            rules=[OnThenRule("high_confidence", "=", True, "unknown_action")],
        )

        errors = policy.validate()
        assert any("action" in e.lower() for e in errors)

    def test_to_dict(self):
        """Convert policy to dictionary."""
        policy = PolicyAST(
            name="test_policy",
            domain="politics",
            gate="G2",
            requirements=[RequireCondition("sources", ">=", 2, "independent")],
            rules=[OnThenRule("high_confidence", "=", True, "auto_approve")],
            version="1.5.0",
        )

        d = policy.to_dict()

        assert d["name"] == "test_policy"
        assert d["domain"] == "politics"
        assert d["gate"] == "G2"
        assert d["version"] == "1.5.0"
        assert len(d["requirements"]) == 1
        assert d["requirements"][0]["field"] == "sources"
        assert d["requirements"][0]["modifier"] == "independent"
        assert len(d["rules"]) == 1
        assert d["rules"][0]["action"] == "auto_approve"


class TestKnownSets:
    """Tests for known fields, conditions, actions, and modifiers."""

    def test_known_fields(self):
        """KNOWN_FIELDS contains expected fields."""
        expected = {
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
        assert KNOWN_FIELDS == expected

    def test_known_conditions(self):
        """KNOWN_CONDITIONS contains expected conditions."""
        expected = {
            "high_confidence",
            "low_confidence",
            "medium_confidence",
            "disputed",
            "no_evidence",
            "high_risk",
            "low_risk",
        }
        assert KNOWN_CONDITIONS == expected

    def test_known_actions(self):
        """KNOWN_ACTIONS contains expected actions."""
        expected = {
            "auto_approve",
            "auto_reject",
            "human_review",
            "committee_quorum",
            "escalate",
            "defer",
            "flag_for_review",
        }
        assert KNOWN_ACTIONS == expected

    def test_known_modifiers(self):
        """KNOWN_MODIFIERS contains expected modifiers."""
        expected = {"independent", "strong", "weak"}
        assert KNOWN_MODIFIERS == expected
