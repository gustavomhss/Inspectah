"""
Tests for flows/policy_engine — S37

Tests for flow policy engine: validate_transition and validate_step.
"""

import pytest

from app.flows.policy_engine import (
    DEFAULT_POLICIES,
    PolicyViolation,
    policies_for_domain,
    validate_transition,
    validate_step,
)


class TestPoliciesForDomain:
    """Tests for policies_for_domain function."""

    def test_policies_for_noticias(self):
        """Get policies for noticias domain."""
        policies = policies_for_domain("noticias")

        assert len(policies) == 2
        assert policies[0]["id"] == "pol_news_source_trust"
        assert policies[1]["id"] == "pol_news_confidence_gate"

    def test_policies_for_contestacao(self):
        """Get policies for contestacao domain."""
        policies = policies_for_domain("contestacao")

        assert len(policies) == 2
        assert policies[0]["id"] == "pol_contestacao_origem_obrigatoria"
        assert policies[1]["id"] == "pol_contestacao_protecao_dados"

    def test_policies_for_unknown_domain(self):
        """Get empty policies for unknown domain."""
        policies = policies_for_domain("unknown_domain")

        assert policies == []


class TestValidateTransition:
    """Tests for validate_transition function."""

    def test_validate_transition_to_em_teste_with_policies(self):
        """Transition to em_teste with policies succeeds."""
        validate_transition("noticias", "em_teste")

    def test_validate_transition_to_ativo_with_policies(self):
        """Transition to ativo with policies succeeds."""
        validate_transition("contestacao", "ativo")

    def test_validate_transition_to_em_teste_without_policies(self):
        """Transition to em_teste without policies raises error."""
        with pytest.raises(PolicyViolation, match="sem políticas definidas"):
            validate_transition("unknown_domain", "em_teste")

    def test_validate_transition_to_ativo_without_policies(self):
        """Transition to ativo without policies raises error."""
        with pytest.raises(PolicyViolation, match="sem políticas definidas"):
            validate_transition("no_policies", "ativo")

    def test_validate_transition_to_other_states(self):
        """Transition to other states doesn't check policies."""
        validate_transition("unknown_domain", "draft")
        validate_transition("unknown_domain", "disabled")
        validate_transition("unknown_domain", "archived")


class TestValidateStep:
    """Tests for validate_step function."""

    def test_validate_step_interprete_no_violation(self):
        """Validate interprete step without violation."""
        context = {"violation": False}

        validate_step("noticias", "interprete", context)

    def test_validate_step_interprete_with_violation(self):
        """Validate interprete step with violation raises error."""
        context = {"violation": True}

        with pytest.raises(PolicyViolation, match="Violação de política"):
            validate_step("noticias", "interprete", context)

    def test_validate_step_debunker_with_violation(self):
        """Validate debunker step with violation in contestacao."""
        context = {"violation": True}

        with pytest.raises(PolicyViolation, match="pol_contestacao_protecao_dados"):
            validate_step("contestacao", "debunker", context)

    def test_validate_step_decision_maker_require_confidence_pass(self):
        """Validate decision_maker step with sufficient confidence."""
        context = {"confidence": 0.8, "min_confidence": 0.6}

        validate_step("noticias", "decision_maker", context)

    def test_validate_step_decision_maker_require_confidence_fail(self):
        """Validate decision_maker step with insufficient confidence."""
        context = {"confidence": 0.5, "min_confidence": 0.6}

        with pytest.raises(PolicyViolation, match="Confiança mínima não atendida"):
            validate_step("noticias", "decision_maker", context)

    def test_validate_step_decision_maker_default_min_confidence(self):
        """Validate decision_maker with default min confidence."""
        context = {"confidence": 0.5}

        with pytest.raises(PolicyViolation, match="Confiança mínima"):
            validate_step("noticias", "decision_maker", context)

    def test_validate_step_unknown_domain(self):
        """Validate step for unknown domain passes."""
        validate_step("unknown", "interprete", {"violation": True})

    def test_validate_step_unknown_step_type(self):
        """Validate unknown step type passes."""
        validate_step("noticias", "unknown_step", {"violation": True})

    def test_validate_step_none_context(self):
        """Validate step with None context."""
        validate_step("noticias", "interprete")

    def test_validate_step_empty_context(self):
        """Validate step with empty context."""
        validate_step("noticias", "interprete", {})


class TestDefaultPolicies:
    """Tests for DEFAULT_POLICIES constant."""

    def test_default_policies_structure(self):
        """Default policies have expected structure."""
        assert "noticias" in DEFAULT_POLICIES
        assert "contestacao" in DEFAULT_POLICIES

        for domain, policies in DEFAULT_POLICIES.items():
            assert isinstance(policies, list)
            for pol in policies:
                assert "id" in pol
                assert "etapa" in pol
                assert "enforcement" in pol

    def test_noticias_policies_enforcement_types(self):
        """Noticias policies have correct enforcement types."""
        noticias = DEFAULT_POLICIES["noticias"]

        assert noticias[0]["enforcement"] == "block_on_violation"
        assert noticias[1]["enforcement"] == "require_confidence"

    def test_contestacao_policies_enforcement_types(self):
        """Contestacao policies have block_on_violation enforcement."""
        contestacao = DEFAULT_POLICIES["contestacao"]

        for pol in contestacao:
            assert pol["enforcement"] == "block_on_violation"


class TestPolicyViolation:
    """Tests for PolicyViolation exception."""

    def test_policy_violation_is_exception(self):
        """PolicyViolation is an Exception."""
        assert issubclass(PolicyViolation, Exception)

    def test_policy_violation_message(self):
        """PolicyViolation stores message."""
        error = PolicyViolation("test message")

        assert str(error) == "test message"
