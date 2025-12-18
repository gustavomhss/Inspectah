"""
Tests for Truth Policy DSL Coverage — Coverage gaps

Targeted tests to cover remaining uncovered lines in executor.py, grammar.py, and parser.py
"""

import pytest

from app.truth.policy_dsl.executor import PolicyExecutor, PolicyAction
from app.truth.policy_dsl.grammar import PolicyAST, RequireCondition, OnThenRule
from app.truth.policy_dsl.parser import PolicyParser, PolicyParseError, parse_policy


class TestExecutorTypeError:
    """Tests for executor TypeError handling."""

    def test_requirement_evaluation_type_error(self):
        """Lines 266-267 in executor.py: TypeError when comparing incompatible types."""
        executor = PolicyExecutor()

        policy = PolicyAST(
            name="test_policy",
            domain="test",
            gate="G1",
            requirements=[
                RequireCondition(
                    field="sources",
                    operator=">=",
                    value=2,
                )
            ],
        )

        # Context with incompatible type (string instead of number)
        context = {
            "sources": "not_a_number",  # This will cause TypeError in comparison
        }

        result = executor.execute(policy, context)

        # Should handle TypeError gracefully and mark requirement as failed
        assert result.requirement_results[0].passed is False
        assert "Cannot compare" in result.requirement_results[0].message


class TestGrammarValidationUnknownCondition:
    """Tests for grammar validation of unknown conditions."""

    def test_validate_unknown_condition_field(self):
        """Line 153 in grammar.py: Unknown condition field validation."""
        policy = PolicyAST(
            name="test",
            domain="test",
            gate="G1",
            requirements=[],
            rules=[
                OnThenRule(
                    condition_field="unknown_condition_xyz",  # Not in KNOWN_CONDITIONS or KNOWN_FIELDS
                    condition_operator="=",
                    condition_value=True,
                    action="auto_approve",
                )
            ],
        )

        errors = policy.validate()

        # Should report unknown condition field
        assert any("Unknown condition field" in err for err in errors)
        assert any("unknown_condition_xyz" in err for err in errors)


class TestParserDomainParsing:
    """Tests for parser domain parsing edge cases."""

    def test_parse_domain_as_identifier_fallthrough(self):
        """Line 164 in parser.py: Domain parsed as identifier (primary path)."""
        text = """
        POLICY test
        DOMAIN politics
        GATE G1
        REQUIRE sources >= 1
        """

        ast = parse_policy(text)

        # Domain should be parsed as identifier
        assert ast.domain == "politics"

    def test_parse_domain_missing_raises_error(self):
        """Line 345 in parser.py: Domain missing or invalid token."""
        text = """
        POLICY test
        DOMAIN
        GATE G1
        """

        # DOMAIN without a value should raise error
        with pytest.raises(PolicyParseError, match="Expected domain name"):
            parse_policy(text)

    def test_parse_domain_invalid_token_type(self):
        """Line 345 in parser.py: Domain with invalid token type."""
        text = """
        POLICY test
        DOMAIN >=
        """

        # DOMAIN followed by operator should raise error
        with pytest.raises(PolicyParseError, match="Expected domain name"):
            parse_policy(text)


class TestParserRequirementIdentifierValue:
    """Tests for parser requirement with identifier value."""

    def test_parse_requirement_with_identifier_value(self):
        """Lines 424-428 in parser.py: Requirement value can be identifier."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE confidence = high
        """

        ast = parse_policy(text)

        # Value should be parsed as identifier string
        assert ast.requirements[0].value == "high"

    def test_parse_requirement_invalid_value_raises(self):
        """Lines 424-428 in parser.py: Invalid value token raises error."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= {
        """

        # { is not a valid value token
        with pytest.raises(PolicyParseError, match="Expected value"):
            parse_policy(text)


class TestParserRuleConditionOperator:
    """Tests for parser rule condition operator edge cases."""

    def test_parse_rule_without_operator_uses_default(self):
        """Line 492 in parser.py: Rule without explicit operator uses '='."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON evidence_count THEN human_review
        """

        # This should parse with default operator
        ast = parse_policy(text)

        # When no operator, it defaults to "="
        assert ast.rules[0].condition_operator == "="

    def test_parse_rule_with_identifier_value_defaults_to_true(self):
        """Line 499 in parser.py: Rule value defaults to True when not NUMBER/STRING/IDENTIFIER."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON high_confidence THEN auto_approve
        """

        ast = parse_policy(text)

        # high_confidence is a known condition, so it uses True
        assert ast.rules[0].condition_value is True

    def test_parse_rule_complex_condition_invalid_value(self):
        """Line 499 in parser.py: Rule with invalid value token defaults to True."""
        # This tests the fallback where value_token is not NUMBER/STRING/IDENTIFIER
        # In practice, the parser handles this by defaulting to True
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON field_name THEN auto_approve
        """

        # When no operator and no valid value, it should use defaults
        ast = parse_policy(text)
        # The rule should be created with default operator and value
        assert len(ast.rules) == 1
        assert ast.rules[0].condition_field == "field_name"


class TestExecutorRuleEvaluation:
    """Tests for executor rule evaluation edge cases."""

    def test_rule_with_unknown_operator_defaults_to_equality(self):
        """Executor handles unknown operators by defaulting to equality."""
        executor = PolicyExecutor()

        policy = PolicyAST(
            name="test",
            domain="test",
            gate="G1",
            requirements=[
                RequireCondition(field="sources", operator=">=", value=1)
            ],
            rules=[
                OnThenRule(
                    condition_field="evidence_count",
                    condition_operator="unknown_op",  # Unknown operator
                    condition_value=5,
                    action="auto_approve",
                )
            ],
        )

        context = {
            "sources": 2,
            "evidence_count": 5,  # Equal to condition value
        }

        result = executor.execute(policy, context)

        # Unknown operator should default to equality check
        # Since evidence_count == 5, rule should trigger
        assert len(result.triggered_rules) > 0


class TestParserAdvancedEdgeCases:
    """Additional parser edge cases."""

    def test_parse_requirement_with_all_value_types(self):
        """Test requirement parsing with NUMBER, STRING, and IDENTIFIER values."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 2
        REQUIRE confidence = "high"
        REQUIRE risk_level = medium
        """

        ast = parse_policy(text)

        assert ast.requirements[0].value == 2  # NUMBER
        assert ast.requirements[1].value == "high"  # STRING
        assert ast.requirements[2].value == "medium"  # IDENTIFIER

    def test_parse_rule_with_field_comparison_all_value_types(self):
        """Test rule parsing with different value types."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON evidence_count >= 3 THEN auto_approve
        ON confidence = "high" THEN auto_approve
        ON risk = medium THEN human_review
        """

        ast = parse_policy(text)

        assert ast.rules[0].condition_value == 3  # NUMBER
        assert ast.rules[1].condition_value == "high"  # STRING
        assert ast.rules[2].condition_value == "medium"  # IDENTIFIER
