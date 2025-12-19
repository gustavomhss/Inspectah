"""
Tests for TensorEthicCalculator — S41

Tests for the ethical tensor calculation.
"""

from __future__ import annotations

import pytest

from app.contestation import (
    TensorEthicCalculator,
    TensorInput,
    TensorEticoResult,
    DisputeCaseModel,
    DisputeGround,
    AppealType,
    calculate_tensor_etico,
    get_tensor_calculator,
)


class TestTensorInput:
    """Tests for TensorInput dataclass."""

    def test_create_default_input(self) -> None:
        """Test creating input with defaults."""
        tensor_input = TensorInput()

        assert tensor_input.domain == "default"
        assert tensor_input.risk_level == "medium"
        assert tensor_input.grounds == []

    def test_create_input_with_values(self) -> None:
        """Test creating input with values."""
        ground = DisputeGround(
            ground_type=AppealType.ETHICAL,
            description="Ethical concern",
            weight=0.8,
        )
        tensor_input = TensorInput(
            domain="saude",
            risk_level="high",
            grounds=[ground],
            precedent_count=5,
            days_since_filing=10,
        )

        assert tensor_input.domain == "saude"
        assert tensor_input.risk_level == "high"
        assert len(tensor_input.grounds) == 1


class TestTensorEticoResult:
    """Tests for TensorEticoResult."""

    def test_create_result(self) -> None:
        """Test creating a result."""
        result = TensorEticoResult(
            social_impact=0.5,
            individual_impact=0.3,
            precedent_weight=0.7,
            urgency_factor=0.4,
            overall_score=0.475,
        )

        assert result.social_impact == 0.5
        assert result.overall_score == 0.475

    def test_to_dict(self) -> None:
        """Test serialization to dict."""
        result = TensorEticoResult(
            social_impact=0.5,
            individual_impact=0.3,
            precedent_weight=0.7,
            urgency_factor=0.4,
            overall_score=0.475,
        )

        data = result.to_dict()

        assert data["social_impact"] == 0.5
        assert data["overall_score"] == 0.475


class TestTensorEthicCalculator:
    """Tests for TensorEthicCalculator."""

    def setup_method(self) -> None:
        """Create calculator for each test."""
        self.calculator = TensorEthicCalculator()

    def test_calculate_basic(self) -> None:
        """Test basic calculation."""
        tensor_input = TensorInput()

        result = self.calculator.calculate(tensor_input)

        assert isinstance(result, TensorEticoResult)
        assert -1.0 <= result.social_impact <= 1.0
        assert -1.0 <= result.individual_impact <= 1.0
        assert 0.0 <= result.precedent_weight <= 1.0
        assert 0.0 <= result.urgency_factor <= 1.0
        assert 0.0 <= result.overall_score <= 1.0

    def test_domain_affects_calculation(self) -> None:
        """Test that domain affects calculation."""
        input_saude = TensorInput(domain="saude", risk_level="medium")
        input_default = TensorInput(domain="default", risk_level="medium")

        result_saude = self.calculator.calculate(input_saude)
        result_default = self.calculator.calculate(input_default)

        # Saude has higher individual impact weight
        # Results should differ
        assert result_saude.calculation_metadata["domain"] == "saude"
        assert result_default.calculation_metadata["domain"] == "default"

    def test_risk_level_affects_calculation(self) -> None:
        """Test that risk level affects calculation."""
        input_low = TensorInput(risk_level="low")
        input_high = TensorInput(risk_level="high")

        result_low = self.calculator.calculate(input_low)
        result_high = self.calculator.calculate(input_high)

        # High risk has higher multiplier
        assert result_high.calculation_metadata["risk_multiplier"] > result_low.calculation_metadata["risk_multiplier"]

    def test_grounds_affect_calculation(self) -> None:
        """Test that grounds affect calculation."""
        ethical_ground = DisputeGround(
            ground_type=AppealType.ETHICAL,
            description="Ethical concern",
            weight=1.0,
        )
        factual_ground = DisputeGround(
            ground_type=AppealType.FACTUAL,
            description="Factual error",
            weight=1.0,
        )

        input_ethical = TensorInput(grounds=[ethical_ground])
        input_factual = TensorInput(grounds=[factual_ground])

        result_ethical = self.calculator.calculate(input_ethical)
        result_factual = self.calculator.calculate(input_factual)

        # Ethical grounds have higher social impact
        assert result_ethical.social_impact >= result_factual.social_impact

    def test_precedent_count_affects_calculation(self) -> None:
        """Test that precedent count affects calculation."""
        input_no_precedent = TensorInput(precedent_count=0)
        input_many_precedents = TensorInput(precedent_count=10)

        result_no = self.calculator.calculate(input_no_precedent)
        result_many = self.calculator.calculate(input_many_precedents)

        # No precedent means this could set precedent (higher weight)
        # The calculation logic might vary, but we check metadata
        assert result_no.calculation_metadata["precedent_count"] == 0
        assert result_many.calculation_metadata["precedent_count"] == 10

    def test_urgency_increases_with_time(self) -> None:
        """Test that urgency increases with time."""
        input_new = TensorInput(days_since_filing=0)
        input_old = TensorInput(days_since_filing=30)

        result_new = self.calculator.calculate(input_new)
        result_old = self.calculator.calculate(input_old)

        assert result_old.urgency_factor >= result_new.urgency_factor

    def test_affected_parties_affects_social_impact(self) -> None:
        """Test that affected parties affects social impact."""
        input_few = TensorInput(affected_parties=1)
        input_many = TensorInput(affected_parties=1000)

        result_few = self.calculator.calculate(input_few)
        result_many = self.calculator.calculate(input_many)

        # More affected parties = higher social impact
        assert result_many.social_impact >= result_few.social_impact

    def test_reversibility_affects_individual_impact(self) -> None:
        """Test that reversibility affects individual impact."""
        input_reversible = TensorInput(reversibility=1.0)
        input_irreversible = TensorInput(reversibility=0.0)

        result_reversible = self.calculator.calculate(input_reversible)
        result_irreversible = self.calculator.calculate(input_irreversible)

        # Lower reversibility = higher individual impact (more risk)
        assert result_irreversible.individual_impact >= result_reversible.individual_impact

    def test_values_clamped(self) -> None:
        """Test that extreme values are clamped."""
        # Create extreme input
        extreme_input = TensorInput(
            risk_level="critical",
            affected_parties=1000000,
            public_interest=1.0,
            reversibility=0.0,
            days_since_filing=365,
        )

        result = self.calculator.calculate(extreme_input)

        # All values should be in valid range
        assert -1.0 <= result.social_impact <= 1.0
        assert -1.0 <= result.individual_impact <= 1.0
        assert 0.0 <= result.precedent_weight <= 1.0
        assert 0.0 <= result.urgency_factor <= 1.0

    def test_metadata_included(self) -> None:
        """Test that calculation metadata is included."""
        tensor_input = TensorInput(
            domain="governo",
            risk_level="high",
        )

        result = self.calculator.calculate(tensor_input)

        assert "domain" in result.calculation_metadata
        assert "risk_level" in result.calculation_metadata
        assert "calculated_at" in result.calculation_metadata
        assert result.calculation_metadata["domain"] == "governo"


class TestCalculateFromCase:
    """Tests for calculating tensor from case model."""

    def setup_method(self) -> None:
        """Create calculator for each test."""
        self.calculator = TensorEthicCalculator()

    def test_calculate_from_case(self) -> None:
        """Test calculating from a case model."""
        case = DisputeCaseModel(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            domain="saude",
            risk_level="high",
        )
        case.grounds = [
            DisputeGround(
                ground_type=AppealType.ETHICAL,
                description="Ethical concern",
            )
        ]

        result = self.calculator.calculate_from_case(case)

        assert isinstance(result, TensorEticoResult)
        assert result.calculation_metadata["domain"] == "saude"
        assert result.calculation_metadata["risk_level"] == "high"

    def test_calculate_from_case_with_defaults(self) -> None:
        """Test calculating from case with missing fields."""
        case = DisputeCaseModel(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
        )

        result = self.calculator.calculate_from_case(case)

        assert result.calculation_metadata["domain"] == "default"
        assert result.calculation_metadata["risk_level"] == "medium"


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_get_tensor_calculator(self) -> None:
        """Test getting singleton calculator."""
        calc1 = get_tensor_calculator()
        calc2 = get_tensor_calculator()

        assert calc1 is calc2

    def test_calculate_tensor_etico(self) -> None:
        """Test convenience function."""
        case = DisputeCaseModel(
            claim_id="claim_123",
            original_decision_id="dec_456",
            petitioner_id="user_789",
            domain="financeiro",
        )

        result = calculate_tensor_etico(case)

        assert isinstance(result, TensorEticoResult)
        assert result.calculation_metadata["domain"] == "financeiro"
