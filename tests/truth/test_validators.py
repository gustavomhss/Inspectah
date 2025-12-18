"""
Tests for DecisionBlock validators.

Task: S40-TST-001 (created early for gate compliance)
Tests invariants:
- INV-DB-01: DecisionBlock sem references.guias[] é inválido
- INV-DB-02: DecisionBlock sem references.e40_5 é inválido
- INV-DB-03: DecisionBlock sem state_transition é inválido
- INV-DB-04: DecisionBlock sem references.pilares[] é inválido
"""

import pytest

from app.truth.validators import (
    ValidationError,
    ValidationErrorCode,
    ValidationResult,
    is_valid_decision_block,
    validate_decision_block,
    validate_decision_block_strict,
)


def make_valid_decision_block() -> dict:
    """Create a valid DecisionBlock for testing."""
    return {
        "decision_id": "test-decision-001",
        "claim_id": "claim-001",
        "domain": "saude",
        "gate": "G23",
        "state_transition": {
            "from_state": "CLAIMED",
            "to_state": "UNDER_REVIEW",
            "reason": "Initial review triggered",
        },
        "references": {
            "guias": [
                {
                    "guia": "MQV",
                    "documento": "01_Guia_3X",
                    "tabela": "G2",
                    "secao": "Cap.2",
                }
            ],
            "pilares": [
                {
                    "pilar": "P5",
                    "documento": "P5-4",
                    "secao": "§3.2",
                }
            ],
            "e40_5": {
                "status": "PASS",
                "invariants_checked": ["INV-DB-01", "INV-DB-02"],
                "violations": [],
            },
        },
        "policy_version": "v1.0.0",
        "created_at": "2024-12-16T12:00:00Z",
    }


class TestValidateDecisionBlock:
    """Tests for validate_decision_block function."""

    def test_valid_decision_block(self):
        """Test that a valid DecisionBlock passes validation."""
        data = make_valid_decision_block()
        result = validate_decision_block(data)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_is_valid_shortcut(self):
        """Test is_valid_decision_block helper."""
        data = make_valid_decision_block()
        assert is_valid_decision_block(data) is True

        # Invalid
        invalid_data = {"claim_id": "test"}
        assert is_valid_decision_block(invalid_data) is False


class TestInvariantINV_DB_01:
    """Tests for INV-DB-01: references.guias[] required."""

    def test_missing_guias(self):
        """Test that missing guias fails validation."""
        data = make_valid_decision_block()
        del data["references"]["guias"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.invariant == "INV-DB-01" for e in result.errors)

    def test_empty_guias(self):
        """Test that empty guias array fails validation."""
        data = make_valid_decision_block()
        data["references"]["guias"] = []

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(
            e.code == ValidationErrorCode.EMPTY_ARRAY and "guias" in e.field
            for e in result.errors
        )

    def test_guias_without_required_fields(self):
        """Test that guias without guia/documento fails."""
        data = make_valid_decision_block()
        data["references"]["guias"] = [{"tabela": "G2"}]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("guias" in e.field for e in result.errors)


class TestInvariantINV_DB_02:
    """Tests for INV-DB-02: references.e40_5 required."""

    def test_missing_e40_5(self):
        """Test that missing e40_5 fails validation."""
        data = make_valid_decision_block()
        del data["references"]["e40_5"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.invariant == "INV-DB-02" for e in result.errors)

    def test_e40_5_without_status(self):
        """Test that e40_5 without status fails."""
        data = make_valid_decision_block()
        data["references"]["e40_5"] = {"invariants_checked": []}

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("e40_5.status" in e.field for e in result.errors)

    def test_e40_5_invalid_status(self):
        """Test that invalid e40_5 status fails."""
        data = make_valid_decision_block()
        data["references"]["e40_5"]["status"] = "INVALID"

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.INVALID_E40_5_STATUS for e in result.errors)

    def test_e40_5_valid_statuses(self):
        """Test all valid e40_5 statuses."""
        for status in ["PASS", "FAIL", "SKIP", "TIMEOUT", "DEGRADED"]:
            data = make_valid_decision_block()
            data["references"]["e40_5"]["status"] = status

            result = validate_decision_block(data)

            assert result.valid is True, f"Status {status} should be valid"


class TestInvariantINV_DB_03:
    """Tests for INV-DB-03: state_transition required."""

    def test_missing_state_transition(self):
        """Test that missing state_transition fails."""
        data = make_valid_decision_block()
        del data["state_transition"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.field == "state_transition" for e in result.errors)

    def test_missing_from_state(self):
        """Test that missing from_state fails."""
        data = make_valid_decision_block()
        del data["state_transition"]["from_state"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("from_state" in e.field for e in result.errors)

    def test_missing_to_state(self):
        """Test that missing to_state fails."""
        data = make_valid_decision_block()
        del data["state_transition"]["to_state"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("to_state" in e.field for e in result.errors)

    def test_missing_reason(self):
        """Test that missing reason fails."""
        data = make_valid_decision_block()
        del data["state_transition"]["reason"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("reason" in e.field for e in result.errors)

    def test_empty_reason(self):
        """Test that empty reason fails."""
        data = make_valid_decision_block()
        data["state_transition"]["reason"] = "   "

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.MISSING_REASON for e in result.errors)

    def test_invalid_from_state(self):
        """Test that invalid from_state fails."""
        data = make_valid_decision_block()
        data["state_transition"]["from_state"] = "INVALID_STATE"

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.INVALID_STATE for e in result.errors)

    def test_invalid_to_state(self):
        """Test that invalid to_state fails."""
        data = make_valid_decision_block()
        data["state_transition"]["to_state"] = "INVALID_STATE"

        result = validate_decision_block(data)

        assert result.valid is False

    def test_valid_states(self):
        """Test all valid states."""
        valid_states = [
            "UNKNOWN",
            "CLAIMED",
            "UNDER_REVIEW",
            "PROVISIONAL",
            "ESTABLISHED_FACT",
            "UNDER_DISPUTE",
            "RETRACTED",
            "BLOCKED",
            "DEGRADED",
        ]
        for state in valid_states:
            data = make_valid_decision_block()
            data["state_transition"]["from_state"] = state
            data["state_transition"]["to_state"] = state

            result = validate_decision_block(data)

            assert result.valid is True, f"State {state} should be valid"


class TestInvariantINV_DB_04:
    """Tests for INV-DB-04: references.pilares[] required."""

    def test_missing_pilares(self):
        """Test that missing pilares fails validation."""
        data = make_valid_decision_block()
        del data["references"]["pilares"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.invariant == "INV-DB-04" for e in result.errors)

    def test_empty_pilares(self):
        """Test that empty pilares array fails validation."""
        data = make_valid_decision_block()
        data["references"]["pilares"] = []

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(
            e.code == ValidationErrorCode.EMPTY_ARRAY and "pilares" in e.field
            for e in result.errors
        )

    def test_pilares_without_required_fields(self):
        """Test that pilares without pilar/documento fails."""
        data = make_valid_decision_block()
        data["references"]["pilares"] = [{"secao": "§3.2"}]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("pilares" in e.field for e in result.errors)


class TestRequiredFields:
    """Tests for required top-level fields."""

    def test_missing_claim_id(self):
        """Test that missing claim_id fails."""
        data = make_valid_decision_block()
        del data["claim_id"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.field == "claim_id" for e in result.errors)

    def test_missing_domain(self):
        """Test that missing domain fails."""
        data = make_valid_decision_block()
        del data["domain"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.field == "domain" for e in result.errors)

    def test_missing_gate(self):
        """Test that missing gate fails."""
        data = make_valid_decision_block()
        del data["gate"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.field == "gate" for e in result.errors)

    def test_missing_policy_version(self):
        """Test that missing policy_version fails."""
        data = make_valid_decision_block()
        del data["policy_version"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.field == "policy_version" for e in result.errors)


class TestStrictMode:
    """Tests for strict validation mode."""

    def test_strict_raises_on_invalid(self):
        """Test that strict mode raises ValidationError."""
        data = {"claim_id": "test"}

        with pytest.raises(ValidationError) as exc_info:
            validate_decision_block_strict(data)

        assert exc_info.value.code == ValidationErrorCode.MISSING_REQUIRED_FIELD

    def test_strict_passes_on_valid(self):
        """Test that strict mode doesn't raise for valid data."""
        data = make_valid_decision_block()

        # Should not raise
        validate_decision_block_strict(data)


class TestValidationResult:
    """Tests for ValidationResult object."""

    def test_error_messages_property(self):
        """Test error_messages property."""
        data = {"claim_id": "test"}  # Missing many fields
        result = validate_decision_block(data)

        assert result.valid is False
        assert len(result.error_messages) > 0
        assert all(isinstance(msg, str) for msg in result.error_messages)


class TestEdgeCases:
    """Tests for edge cases and type errors."""

    def test_state_transition_not_dict(self):
        """Test that state_transition as non-dict fails validation."""
        data = make_valid_decision_block()
        data["state_transition"] = "invalid_type"

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.INVALID_TYPE for e in result.errors)
        assert any("state_transition" in e.field for e in result.errors)

    def test_references_not_dict(self):
        """Test that references as non-dict fails validation."""
        data = make_valid_decision_block()
        data["references"] = "invalid_type"

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.INVALID_TYPE for e in result.errors)
        assert any("references" in e.field for e in result.errors)

    def test_guia_not_dict(self):
        """Test that guia item as non-dict fails validation."""
        data = make_valid_decision_block()
        data["references"]["guias"] = ["invalid_type"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.INVALID_TYPE for e in result.errors)
        assert any("guias[0]" in e.field for e in result.errors)

    def test_pilar_not_dict(self):
        """Test that pilar item as non-dict fails validation."""
        data = make_valid_decision_block()
        data["references"]["pilares"] = ["invalid_type"]

        result = validate_decision_block(data)

        assert result.valid is False
        assert any(e.code == ValidationErrorCode.INVALID_TYPE for e in result.errors)
        assert any("pilares[0]" in e.field for e in result.errors)

    def test_e40_5_not_dict(self):
        """Test that e40_5 as non-dict fails validation."""
        data = make_valid_decision_block()
        data["references"]["e40_5"] = "invalid_type"

        result = validate_decision_block(data)

        assert result.valid is False
        assert any("e40_5" in e.field for e in result.errors)
