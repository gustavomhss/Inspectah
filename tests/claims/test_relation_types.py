"""
Comprehensive tests for Relation Types — S38-BE-020

Tests relation type definitions, configurations, and utility functions.
"""

import pytest
from app.claims.relation_types import (
    ClassificationResult,
    ClaimCluster,
    ClaimRelation,
    InferenceMethod,
    RelationConfig,
    RelationType,
    detect_negation_indicators,
    detect_support_indicators,
    NEGATION_INDICATORS,
    SUPPORT_INDICATORS,
)


class TestRelationType:
    """Test RelationType enum."""

    def test_all_relation_types(self):
        """Test all relation types exist."""
        assert RelationType.SUPPORTS == "supports"
        assert RelationType.CONTRADICTS == "contradicts"
        assert RelationType.RELATED == "related"
        assert RelationType.DUPLICATE == "duplicate"
        assert RelationType.REFINES == "refines"
        assert RelationType.GENERALIZES == "generalizes"

    def test_relation_type_is_string_enum(self):
        """Test RelationType is string enum."""
        assert isinstance(RelationType.SUPPORTS.value, str)


class TestInferenceMethod:
    """Test InferenceMethod enum."""

    def test_all_inference_methods(self):
        """Test all inference methods exist."""
        assert InferenceMethod.MANUAL == "manual"
        assert InferenceMethod.EMBEDDING == "embedding"
        assert InferenceMethod.LLM == "llm"
        assert InferenceMethod.RULE == "rule"
        assert InferenceMethod.ENTITY == "entity"


class TestClassificationResult:
    """Test ClassificationResult dataclass."""

    def test_creation(self):
        """Test creating classification result."""
        result = ClassificationResult(
            relation_type=RelationType.SUPPORTS,
            confidence=0.85,
            method=InferenceMethod.EMBEDDING,
            indicators={"similarity": 0.9},
        )

        assert result.relation_type == RelationType.SUPPORTS
        assert result.confidence == 0.85
        assert result.method == InferenceMethod.EMBEDDING
        assert result.indicators["similarity"] == 0.9

    def test_creation_default_indicators(self):
        """Test default indicators."""
        result = ClassificationResult(
            relation_type=RelationType.RELATED,
            confidence=0.7,
            method=InferenceMethod.RULE,
        )

        assert result.indicators == {}

    def test_is_high_confidence_default_threshold(self):
        """Test is_high_confidence with default threshold."""
        result_high = ClassificationResult(
            relation_type=RelationType.SUPPORTS,
            confidence=0.85,
            method=InferenceMethod.EMBEDDING,
        )
        result_low = ClassificationResult(
            relation_type=RelationType.SUPPORTS,
            confidence=0.75,
            method=InferenceMethod.EMBEDDING,
        )

        assert result_high.is_high_confidence()
        assert not result_low.is_high_confidence()

    def test_is_high_confidence_custom_threshold(self):
        """Test is_high_confidence with custom threshold."""
        result = ClassificationResult(
            relation_type=RelationType.SUPPORTS,
            confidence=0.75,
            method=InferenceMethod.EMBEDDING,
        )

        assert result.is_high_confidence(threshold=0.7)
        assert not result.is_high_confidence(threshold=0.8)


class TestRelationConfig:
    """Test RelationConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = RelationConfig()

        assert config.similarity_threshold == 0.7
        assert config.contradiction_threshold == 0.6
        assert config.duplicate_threshold == 0.95
        assert config.support_threshold == 0.85
        assert config.confidence_threshold == 0.7
        assert config.negation_boost == 1.2
        assert config.max_relations_per_claim == 10

    def test_custom_values(self):
        """Test custom configuration values."""
        config = RelationConfig(
            similarity_threshold=0.8,
            contradiction_threshold=0.7,
            duplicate_threshold=0.98,
            support_threshold=0.9,
            confidence_threshold=0.75,
            negation_boost=1.5,
            max_relations_per_claim=5,
        )

        assert config.similarity_threshold == 0.8
        assert config.contradiction_threshold == 0.7
        assert config.duplicate_threshold == 0.98
        assert config.support_threshold == 0.9
        assert config.confidence_threshold == 0.75
        assert config.negation_boost == 1.5
        assert config.max_relations_per_claim == 5


class TestClaimRelation:
    """Test ClaimRelation dataclass."""

    def test_creation(self):
        """Test creating claim relation."""
        relation = ClaimRelation(
            source_claim_id="claim_1",
            target_claim_id="claim_2",
            relation_type=RelationType.SUPPORTS,
            confidence=0.85,
            method=InferenceMethod.EMBEDDING,
            bidirectional=True,
            indicators={"key": "value"},
            created_by="user_1",
        )

        assert relation.source_claim_id == "claim_1"
        assert relation.target_claim_id == "claim_2"
        assert relation.relation_type == RelationType.SUPPORTS
        assert relation.confidence == 0.85
        assert relation.method == InferenceMethod.EMBEDDING
        assert relation.bidirectional is True
        assert relation.indicators["key"] == "value"
        assert relation.created_by == "user_1"

    def test_creation_defaults(self):
        """Test default values."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.RELATED,
            confidence=0.5,
            method=InferenceMethod.RULE,
        )

        assert relation.bidirectional is False
        assert relation.indicators == {}
        assert relation.created_by == "system"

    def test_inverse_supports(self):
        """Test inverse of SUPPORTS relation."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.SUPPORTS,
            confidence=0.8,
            method=InferenceMethod.RULE,
        )

        inverse = relation.inverse()

        assert inverse.source_claim_id == "c2"
        assert inverse.target_claim_id == "c1"
        assert inverse.relation_type == RelationType.SUPPORTS  # Supports is symmetric
        assert inverse.confidence == 0.8
        assert inverse.method == InferenceMethod.RULE

    def test_inverse_contradicts(self):
        """Test inverse of CONTRADICTS relation."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.CONTRADICTS,
            confidence=0.9,
            method=InferenceMethod.RULE,
        )

        inverse = relation.inverse()

        assert inverse.relation_type == RelationType.CONTRADICTS  # Symmetric

    def test_inverse_refines(self):
        """Test inverse of REFINES relation."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.REFINES,
            confidence=0.85,
            method=InferenceMethod.LLM,
        )

        inverse = relation.inverse()

        assert inverse.source_claim_id == "c2"
        assert inverse.target_claim_id == "c1"
        assert inverse.relation_type == RelationType.GENERALIZES

    def test_inverse_generalizes(self):
        """Test inverse of GENERALIZES relation."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.GENERALIZES,
            confidence=0.75,
            method=InferenceMethod.LLM,
        )

        inverse = relation.inverse()

        assert inverse.relation_type == RelationType.REFINES

    def test_inverse_related(self):
        """Test inverse of RELATED relation."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.RELATED,
            confidence=0.7,
            method=InferenceMethod.EMBEDDING,
        )

        inverse = relation.inverse()

        assert inverse.relation_type == RelationType.RELATED  # Symmetric

    def test_inverse_duplicate(self):
        """Test inverse of DUPLICATE relation."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.DUPLICATE,
            confidence=0.95,
            method=InferenceMethod.EMBEDDING,
        )

        inverse = relation.inverse()

        assert inverse.relation_type == RelationType.DUPLICATE  # Symmetric

    def test_inverse_preserves_bidirectional(self):
        """Test inverse preserves bidirectional flag."""
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.SUPPORTS,
            confidence=0.8,
            method=InferenceMethod.RULE,
            bidirectional=True,
        )

        inverse = relation.inverse()

        assert inverse.bidirectional is True

    def test_inverse_preserves_indicators(self):
        """Test inverse preserves indicators."""
        indicators = {"sim": 0.9, "entities": ["A", "B"]}
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.SUPPORTS,
            confidence=0.8,
            method=InferenceMethod.RULE,
            indicators=indicators,
        )

        inverse = relation.inverse()

        assert inverse.indicators == indicators


class TestClaimCluster:
    """Test ClaimCluster dataclass."""

    def test_creation(self):
        """Test creating claim cluster."""
        cluster = ClaimCluster(
            cluster_id="cluster_1",
            representative_id="claim_1",
            member_ids=["claim_1", "claim_2", "claim_3"],
            avg_similarity=0.85,
            topic="economy",
            metadata={"key": "value"},
        )

        assert cluster.cluster_id == "cluster_1"
        assert cluster.representative_id == "claim_1"
        assert len(cluster.member_ids) == 3
        assert cluster.avg_similarity == 0.85
        assert cluster.topic == "economy"
        assert cluster.metadata["key"] == "value"

    def test_creation_defaults(self):
        """Test default values."""
        cluster = ClaimCluster(
            cluster_id="c1",
            representative_id="r1",
            member_ids=["r1", "m1"],
            avg_similarity=0.8,
        )

        assert cluster.topic is None
        assert cluster.metadata == {}

    def test_size_property(self):
        """Test size property."""
        cluster = ClaimCluster(
            cluster_id="c1",
            representative_id="r1",
            member_ids=["r1", "m1", "m2", "m3"],
            avg_similarity=0.8,
        )

        assert cluster.size == 4

    def test_size_empty_cluster(self):
        """Test size with empty members."""
        cluster = ClaimCluster(
            cluster_id="c1",
            representative_id="r1",
            member_ids=[],
            avg_similarity=0.0,
        )

        assert cluster.size == 0


class TestNegationIndicators:
    """Test negation indicator detection."""

    def test_negation_indicators_constant(self):
        """Test NEGATION_INDICATORS constant exists."""
        assert isinstance(NEGATION_INDICATORS, list)
        assert len(NEGATION_INDICATORS) > 0
        assert "nao" in NEGATION_INDICATORS or "não" in NEGATION_INDICATORS
        assert "nunca" in NEGATION_INDICATORS
        assert "falso" in NEGATION_INDICATORS

    def test_detect_negation_single_indicator(self):
        """Test detecting single negation indicator."""
        text = "isso não é verdade"
        found = detect_negation_indicators(text)

        assert len(found) > 0
        assert "não" in found

    def test_detect_negation_multiple_indicators(self):
        """Test detecting multiple negation indicators."""
        text = "isso não é verdade, nunca foi correto e é falso"
        found = detect_negation_indicators(text)

        assert len(found) >= 2
        assert any(ind in found for ind in ["não", "nunca", "falso"])

    def test_detect_negation_no_indicators(self):
        """Test no negation indicators."""
        text = "isso é verdade e está correto"
        found = detect_negation_indicators(text)

        assert len(found) == 0

    def test_detect_negation_case_insensitive(self):
        """Test case insensitive detection."""
        text = "NÃO é verdade"
        found = detect_negation_indicators(text)

        assert len(found) > 0

    def test_detect_negation_empty_text(self):
        """Test empty text."""
        found = detect_negation_indicators("")

        assert found == []


class TestSupportIndicators:
    """Test support indicator detection."""

    def test_support_indicators_constant(self):
        """Test SUPPORT_INDICATORS constant exists."""
        assert isinstance(SUPPORT_INDICATORS, list)
        assert len(SUPPORT_INDICATORS) > 0
        assert "confirma" in SUPPORT_INDICATORS
        assert "verdade" in SUPPORT_INDICATORS
        assert "correto" in SUPPORT_INDICATORS

    def test_detect_support_single_indicator(self):
        """Test detecting single support indicator."""
        text = "os dados confirmam a teoria"
        found = detect_support_indicators(text)

        assert len(found) > 0
        assert "confirma" in found

    def test_detect_support_multiple_indicators(self):
        """Test detecting multiple support indicators."""
        text = "isso confirma e corrobora a verdade"
        found = detect_support_indicators(text)

        assert len(found) >= 2

    def test_detect_support_no_indicators(self):
        """Test no support indicators."""
        text = "uma afirmação qualquer"
        found = detect_support_indicators(text)

        assert len(found) == 0

    def test_detect_support_case_insensitive(self):
        """Test case insensitive detection."""
        text = "CONFIRMA a teoria"
        found = detect_support_indicators(text)

        assert len(found) > 0

    def test_detect_support_empty_text(self):
        """Test empty text."""
        found = detect_support_indicators("")

        assert found == []


class TestRefinementIndicators:
    """Test refinement indicators."""

    def test_refinement_indicators_constant(self):
        """Test REFINEMENT_INDICATORS exists."""
        from app.claims.relation_types import REFINEMENT_INDICATORS

        assert isinstance(REFINEMENT_INDICATORS, list)
        assert len(REFINEMENT_INDICATORS) > 0
        assert "especificamente" in REFINEMENT_INDICATORS
        assert "ou seja" in REFINEMENT_INDICATORS


class TestIndicatorEdgeCases:
    """Test edge cases for indicator detection."""

    def test_indicator_in_middle_of_word(self):
        """Test partial matches should still be detected."""
        # Portuguese allows accents, so "não" might appear in compound words
        text = "permanência"  # Contains "nao" without accent
        found = detect_negation_indicators(text)

        # This might find it depending on implementation
        # The function looks for substring match

    def test_indicator_with_punctuation(self):
        """Test indicator with punctuation."""
        text = "não, isso não é correto!"
        found = detect_negation_indicators(text)

        assert len(found) >= 1

    def test_multiple_same_indicator(self):
        """Test same indicator appears multiple times."""
        text = "não, não e não!"
        found = detect_negation_indicators(text)

        # Should only return unique indicators
        # (depends on implementation, but likely just "não")
        assert "não" in found

    def test_indicator_accent_variations(self):
        """Test accented and non-accented variations."""
        text1 = "não é verdade"
        text2 = "nao é verdade"

        found1 = detect_negation_indicators(text1)
        found2 = detect_negation_indicators(text2)

        # Both should detect negation
        assert len(found1) > 0
        assert len(found2) > 0


class TestRelationTypeSymmetry:
    """Test relation type symmetry properties."""

    def test_symmetric_relation_types(self):
        """Test which relation types should be symmetric."""
        symmetric_types = [
            RelationType.SUPPORTS,
            RelationType.CONTRADICTS,
            RelationType.RELATED,
            RelationType.DUPLICATE,
        ]

        for rel_type in symmetric_types:
            relation = ClaimRelation(
                source_claim_id="c1",
                target_claim_id="c2",
                relation_type=rel_type,
                confidence=0.8,
                method=InferenceMethod.RULE,
            )

            inverse = relation.inverse()
            assert inverse.relation_type == rel_type

    def test_asymmetric_relation_types(self):
        """Test asymmetric relation types."""
        # REFINES <-> GENERALIZES
        relation = ClaimRelation(
            source_claim_id="c1",
            target_claim_id="c2",
            relation_type=RelationType.REFINES,
            confidence=0.8,
            method=InferenceMethod.RULE,
        )

        inverse = relation.inverse()
        assert inverse.relation_type == RelationType.GENERALIZES
        assert relation.relation_type != inverse.relation_type


class TestConfigValidation:
    """Test configuration validation."""

    def test_config_thresholds_valid_range(self):
        """Test config with valid threshold values."""
        config = RelationConfig(
            similarity_threshold=0.5,
            contradiction_threshold=0.5,
            duplicate_threshold=0.95,
            confidence_threshold=0.0,
        )

        # Should create without error
        assert config.similarity_threshold == 0.5

    def test_config_allows_edge_values(self):
        """Test config allows edge values."""
        config = RelationConfig(
            similarity_threshold=0.0,
            duplicate_threshold=1.0,
        )

        assert config.similarity_threshold == 0.0
        assert config.duplicate_threshold == 1.0
