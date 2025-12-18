"""
Tests for Claim validators.

Task: S40-BE-002 tests
Tests invariant:
- INV-CLAIM-01: Claim sem prior ou evidence_trail[] é inválida
"""

import pytest

from app.claims.validators import (
    ClaimValidationError,
    ClaimValidationErrorCode,
    ClaimValidationResult,
    is_valid_claim,
    validate_claim,
    validate_claim_for_export,
    validate_claim_strict,
    validate_evidence_trail,
    validate_prior,
)


def make_valid_claim() -> dict:
    """Create a valid Claim for testing."""
    return {
        "claim_id": "claim-001",
        "text": "A claim about something important",
        "current_state": "CLAIMED",
        "prior": {
            "probability": 0.7,
            "confidence": 0.85,
            "source": "model",
            "model_version": "v1.0",
            "computed_at": "2024-12-16T12:00:00Z",
        },
        "evidence_trail": [
            {
                "evidence_id": "ev-001",
                "type": "source",
                "stance": "supports",
                "weight": 0.8,
            }
        ],
        "created_at": "2024-12-16T12:00:00Z",
    }


class TestValidateClaim:
    """Tests for validate_claim function."""

    def test_valid_claim(self):
        """Test that a valid claim passes validation."""
        data = make_valid_claim()
        result = validate_claim(data)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_is_valid_shortcut(self):
        """Test is_valid_claim helper."""
        data = make_valid_claim()
        assert is_valid_claim(data) is True

        # Invalid
        invalid_data = {"claim_id": "test"}
        assert is_valid_claim(invalid_data) is False


class TestInvariantINV_CLAIM_01_Prior:
    """Tests for INV-CLAIM-01: prior required."""

    def test_missing_prior(self):
        """Test that missing prior fails validation."""
        data = make_valid_claim()
        del data["prior"]

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.code == ClaimValidationErrorCode.MISSING_PRIOR for e in result.errors)
        assert any(e.invariant == "INV-CLAIM-01" for e in result.errors)

    def test_prior_missing_probability(self):
        """Test that prior without probability fails."""
        data = make_valid_claim()
        del data["prior"]["probability"]

        result = validate_claim(data)

        assert result.valid is False
        assert any("probability" in e.field for e in result.errors)

    def test_prior_missing_confidence(self):
        """Test that prior without confidence fails."""
        data = make_valid_claim()
        del data["prior"]["confidence"]

        result = validate_claim(data)

        assert result.valid is False
        assert any("confidence" in e.field for e in result.errors)

    def test_prior_missing_source(self):
        """Test that prior without source fails."""
        data = make_valid_claim()
        del data["prior"]["source"]

        result = validate_claim(data)

        assert result.valid is False
        assert any("source" in e.field for e in result.errors)

    def test_prior_invalid_probability(self):
        """Test that probability out of range fails."""
        data = make_valid_claim()
        data["prior"]["probability"] = 1.5  # > 1

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.code == ClaimValidationErrorCode.OUT_OF_RANGE for e in result.errors)

    def test_prior_invalid_confidence(self):
        """Test that confidence out of range fails."""
        data = make_valid_claim()
        data["prior"]["confidence"] = -0.5  # < 0

        result = validate_claim(data)

        assert result.valid is False

    def test_prior_invalid_source(self):
        """Test that invalid source fails."""
        data = make_valid_claim()
        data["prior"]["source"] = "invalid_source"

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.code == ClaimValidationErrorCode.INVALID_PRIOR for e in result.errors)

    def test_prior_valid_sources(self):
        """Test all valid prior sources."""
        for source in ["model", "expert", "crowd", "official", "hybrid"]:
            data = make_valid_claim()
            data["prior"]["source"] = source

            result = validate_claim(data)

            assert result.valid is True, f"Source {source} should be valid"


class TestInvariantINV_CLAIM_01_EvidenceTrail:
    """Tests for INV-CLAIM-01: evidence_trail required."""

    def test_missing_evidence_trail(self):
        """Test that missing evidence_trail fails."""
        data = make_valid_claim()
        del data["evidence_trail"]

        result = validate_claim(data)

        assert result.valid is False
        assert any(
            e.code == ClaimValidationErrorCode.MISSING_EVIDENCE_TRAIL for e in result.errors
        )
        assert any(e.invariant == "INV-CLAIM-01" for e in result.errors)

    def test_empty_evidence_trail_is_valid(self):
        """Test that empty evidence_trail is valid (can have no evidence yet)."""
        data = make_valid_claim()
        data["evidence_trail"] = []

        result = validate_claim(data)

        assert result.valid is True

    def test_evidence_missing_evidence_id(self):
        """Test that evidence without evidence_id fails."""
        data = make_valid_claim()
        del data["evidence_trail"][0]["evidence_id"]

        result = validate_claim(data)

        assert result.valid is False
        assert any("evidence_id" in e.field for e in result.errors)

    def test_evidence_missing_type(self):
        """Test that evidence without type fails."""
        data = make_valid_claim()
        del data["evidence_trail"][0]["type"]

        result = validate_claim(data)

        assert result.valid is False

    def test_evidence_missing_stance(self):
        """Test that evidence without stance fails."""
        data = make_valid_claim()
        del data["evidence_trail"][0]["stance"]

        result = validate_claim(data)

        assert result.valid is False

    def test_evidence_invalid_type(self):
        """Test that invalid evidence type fails."""
        data = make_valid_claim()
        data["evidence_trail"][0]["type"] = "invalid_type"

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.code == ClaimValidationErrorCode.INVALID_EVIDENCE for e in result.errors)

    def test_evidence_invalid_stance(self):
        """Test that invalid stance fails."""
        data = make_valid_claim()
        data["evidence_trail"][0]["stance"] = "invalid_stance"

        result = validate_claim(data)

        assert result.valid is False

    def test_evidence_valid_types(self):
        """Test all valid evidence types."""
        valid_types = [
            "source",
            "fact_check",
            "expert_opinion",
            "official_data",
            "user_report",
            "contradiction",
            "support",
        ]
        for etype in valid_types:
            data = make_valid_claim()
            data["evidence_trail"][0]["type"] = etype

            result = validate_claim(data)

            assert result.valid is True, f"Type {etype} should be valid"

    def test_evidence_valid_stances(self):
        """Test all valid stances."""
        for stance in ["supports", "refutes", "neutral", "unclear"]:
            data = make_valid_claim()
            data["evidence_trail"][0]["stance"] = stance

            result = validate_claim(data)

            assert result.valid is True, f"Stance {stance} should be valid"

    def test_evidence_weight_out_of_range(self):
        """Test that weight out of range fails."""
        data = make_valid_claim()
        data["evidence_trail"][0]["weight"] = 1.5

        result = validate_claim(data)

        assert result.valid is False


class TestValidClaimStates:
    """Tests for valid claim states."""

    def test_valid_states(self):
        """Test all valid claim states."""
        valid_states = [
            "UNKNOWN",
            "CLAIMED",
            "UNDER_REVIEW",
            "PROVISIONAL",
            "ESTABLISHED_FACT",
            "UNDER_DISPUTE",
            "RETRACTED",
        ]
        for state in valid_states:
            data = make_valid_claim()
            data["current_state"] = state

            result = validate_claim(data)

            assert result.valid is True, f"State {state} should be valid"

    def test_invalid_state(self):
        """Test that invalid state fails."""
        data = make_valid_claim()
        data["current_state"] = "INVALID_STATE"

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.code == ClaimValidationErrorCode.INVALID_STATE for e in result.errors)


class TestRequiredFields:
    """Tests for required top-level fields."""

    def test_missing_claim_id(self):
        """Test that missing claim_id fails."""
        data = make_valid_claim()
        del data["claim_id"]

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.field == "claim_id" for e in result.errors)

    def test_missing_text(self):
        """Test that missing text fails."""
        data = make_valid_claim()
        del data["text"]

        result = validate_claim(data)

        assert result.valid is False
        assert any(e.field == "text" for e in result.errors)


class TestStrictMode:
    """Tests for strict validation mode."""

    def test_strict_raises_on_invalid(self):
        """Test that strict mode raises ClaimValidationError."""
        data = {"claim_id": "test"}

        with pytest.raises(ClaimValidationError) as exc_info:
            validate_claim_strict(data)

        assert exc_info.value.code == ClaimValidationErrorCode.MISSING_REQUIRED_FIELD

    def test_strict_passes_on_valid(self):
        """Test that strict mode doesn't raise for valid data."""
        data = make_valid_claim()

        # Should not raise
        validate_claim_strict(data)


class TestValidateClaimForExport:
    """Tests for export-specific validation."""

    def test_export_requires_created_at(self):
        """Test that export validation requires created_at."""
        data = make_valid_claim()
        del data["created_at"]

        result = validate_claim_for_export(data)

        assert result.valid is False
        assert any("created_at" in e.field for e in result.errors)

    def test_export_valid_claim(self):
        """Test that full claim passes export validation."""
        data = make_valid_claim()

        result = validate_claim_for_export(data)

        # May have warnings but should pass basic validation
        # computed_at is recommended but not required
        assert len([e for e in result.errors if "computed_at" not in e.field]) == 0 or result.valid


class TestValidatePrior:
    """Tests for validate_prior helper function."""

    def test_validate_prior_directly(self):
        """Test validate_prior function directly."""
        valid_prior = {
            "probability": 0.5,
            "confidence": 0.8,
            "source": "model",
        }
        errors = validate_prior(valid_prior)
        assert len(errors) == 0

    def test_validate_prior_invalid_type(self):
        """Test that non-dict prior fails."""
        errors = validate_prior("not a dict")
        assert len(errors) > 0
        assert any(e.code == ClaimValidationErrorCode.INVALID_TYPE for e in errors)


class TestValidateEvidenceTrail:
    """Tests for validate_evidence_trail helper function."""

    def test_validate_evidence_trail_directly(self):
        """Test validate_evidence_trail function directly."""
        valid_trail = [
            {
                "evidence_id": "ev-001",
                "type": "source",
                "stance": "supports",
            }
        ]
        errors = validate_evidence_trail(valid_trail)
        assert len(errors) == 0

    def test_validate_evidence_trail_invalid_type(self):
        """Test that non-list trail fails."""
        errors = validate_evidence_trail("not a list")
        assert len(errors) > 0
        assert any(e.code == ClaimValidationErrorCode.INVALID_TYPE for e in errors)


class TestValidationResult:
    """Tests for ClaimValidationResult object."""

    def test_error_messages_property(self):
        """Test error_messages property."""
        data = {"claim_id": "test"}  # Missing many fields
        result = validate_claim(data)

        assert result.valid is False
        assert len(result.error_messages) > 0
        assert all(isinstance(msg, str) for msg in result.error_messages)
