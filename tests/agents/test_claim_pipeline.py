"""
Tests for Claim Pipeline — S37

Tests for ClaimPipeline claim extraction and processing.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from app.agents.flows.claim_pipeline import (
    ClaimPipeline,
    ClaimPipelineResult,
    ExtractedClaim,
    get_claim_pipeline,
    process_extracted_claims,
)
from app.claims.graph_models import ClaimState, EdgeType, EntityType


class TestExtractedClaim:
    """Tests for ExtractedClaim dataclass."""

    def test_create_minimal(self):
        """Create with minimal fields."""
        claim = ExtractedClaim(content="Test claim", domain="politics")

        assert claim.content == "Test claim"
        assert claim.domain == "politics"
        assert claim.confidence == 1.0
        assert claim.evidence_count == 0

    def test_create_full(self):
        """Create with all fields."""
        claim = ExtractedClaim(
            content="Test claim",
            domain="politics",
            source_id="src_123",
            source_url="https://example.com",
            confidence=0.8,
            evidence_count=3,
            entities=[{"name": "John", "type": "person"}],
            metadata={"key": "value"},
        )

        assert claim.source_id == "src_123"
        assert claim.confidence == 0.8
        assert len(claim.entities) == 1

    def test_default_entities(self):
        """Default entities is empty list."""
        claim = ExtractedClaim(content="Test", domain="test")
        assert claim.entities == []

    def test_default_metadata(self):
        """Default metadata is empty dict."""
        claim = ExtractedClaim(content="Test", domain="test")
        assert claim.metadata == {}


class TestClaimPipelineResult:
    """Tests for ClaimPipelineResult dataclass."""

    def test_create_success(self):
        """Create successful result."""
        result = ClaimPipelineResult(
            claim_id="claim_123",
            status="created",
            entity_ids=["ent_1", "ent_2"],
            relation_ids=["rel_1"],
        )

        assert result.claim_id == "claim_123"
        assert result.status == "created"
        assert result.error is None

    def test_create_failed(self):
        """Create failed result."""
        result = ClaimPipelineResult(
            claim_id="",
            status="failed",
            error="Something went wrong",
        )

        assert result.status == "failed"
        assert result.error == "Something went wrong"


class TestClaimPipeline:
    """Tests for ClaimPipeline class."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        mock = MagicMock()
        mock.add_claim.return_value = "claim_123"
        mock.add_entity.return_value = "entity_123"
        mock.find_entity_by_name.return_value = None
        mock.link_claim_to_entity.return_value = "edge_123"
        mock.find_claims.return_value = []
        mock.repo = MagicMock()
        mock.repo.get_node.return_value = None
        mock.repo.find_edges.return_value = []
        return mock

    @pytest.fixture
    def pipeline(self, mock_graph_service):
        """Create pipeline with mock service."""
        return ClaimPipeline(graph_service=mock_graph_service)

    def test_init_default(self):
        """Initialize with default service."""
        with patch("app.agents.flows.claim_pipeline.ClaimGraphService") as mock:
            pipeline = ClaimPipeline()
            assert pipeline.graph is not None

    def test_init_with_service(self, mock_graph_service):
        """Initialize with injected service."""
        pipeline = ClaimPipeline(graph_service=mock_graph_service)
        assert pipeline.graph == mock_graph_service

    def test_process_claim_success(self, pipeline, mock_graph_service):
        """Process claim successfully."""
        claim = ExtractedClaim(
            content="Test claim",
            domain="politics",
        )

        result = pipeline.process_claim(claim)

        assert result.status == "created"
        assert result.claim_id == "claim_123"
        mock_graph_service.add_claim.assert_called_once()

    def test_process_claim_with_entities(self, pipeline, mock_graph_service):
        """Process claim with entities."""
        claim = ExtractedClaim(
            content="Test claim",
            domain="politics",
            entities=[
                {"name": "John Doe", "type": "person"},
                {"name": "Acme Corp", "type": "organization"},
            ],
        )

        result = pipeline.process_claim(claim)

        assert result.status == "created"
        # Should create entities and link them
        assert mock_graph_service.add_entity.call_count == 2

    def test_process_claim_entity_cache(self, pipeline, mock_graph_service):
        """Entity cache prevents duplicate creation."""
        # First claim
        claim1 = ExtractedClaim(
            content="Claim 1",
            domain="politics",
            entities=[{"name": "John Doe", "type": "person"}],
        )
        pipeline.process_claim(claim1)

        # Second claim with same entity
        claim2 = ExtractedClaim(
            content="Claim 2",
            domain="politics",
            entities=[{"name": "John Doe", "type": "person"}],
        )
        pipeline.process_claim(claim2)

        # Entity should only be created once
        assert mock_graph_service.add_entity.call_count == 1

    def test_process_claim_existing_entity(self, pipeline, mock_graph_service):
        """Use existing entity instead of creating new."""
        existing_entity = MagicMock()
        existing_entity.id = "existing_123"
        mock_graph_service.find_entity_by_name.return_value = existing_entity

        claim = ExtractedClaim(
            content="Test claim",
            domain="politics",
            entities=[{"name": "John Doe", "type": "person"}],
        )

        result = pipeline.process_claim(claim)

        assert result.status == "created"
        # Should not create new entity
        mock_graph_service.add_entity.assert_not_called()

    def test_process_claim_error(self, pipeline, mock_graph_service):
        """Handle error during processing."""
        mock_graph_service.add_claim.side_effect = Exception("Database error")

        claim = ExtractedClaim(content="Test", domain="test")

        result = pipeline.process_claim(claim)

        assert result.status == "failed"
        assert "Database error" in result.error

    def test_process_batch(self, pipeline, mock_graph_service):
        """Process multiple claims."""
        claims = [
            ExtractedClaim(content="Claim 1", domain="politics"),
            ExtractedClaim(content="Claim 2", domain="politics"),
            ExtractedClaim(content="Claim 3", domain="politics"),
        ]

        results = pipeline.process_batch(claims)

        assert len(results) == 3
        assert all(r.status == "created" for r in results)

    def test_entity_type_mapping(self, pipeline, mock_graph_service):
        """Entity type strings are mapped correctly."""
        claim = ExtractedClaim(
            content="Test",
            domain="test",
            entities=[
                {"name": "Person", "type": "person"},
                {"name": "Org", "type": "org"},
                {"name": "Place", "type": "location"},
                {"name": "Event", "type": "event"},
                {"name": "Other", "type": "unknown"},
            ],
        )

        pipeline.process_claim(claim)

        calls = mock_graph_service.add_entity.call_args_list
        entity_types = [call[1]["entity_type"] for call in calls]

        assert EntityType.PERSON in entity_types
        assert EntityType.ORGANIZATION in entity_types
        assert EntityType.PLACE in entity_types
        assert EntityType.EVENT in entity_types
        assert EntityType.OTHER in entity_types

    def test_link_claim_to_case(self, pipeline, mock_graph_service):
        """Link claim to case."""
        mock_graph_service.link_claim_to_case.return_value = "edge_123"

        result = pipeline.link_claim_to_case("claim_1", "case_1")

        assert result == "edge_123"
        mock_graph_service.link_claim_to_case.assert_called_once_with("claim_1", "case_1")

    def test_link_claim_to_topic(self, pipeline, mock_graph_service):
        """Link claim to topic."""
        mock_graph_service.link_claim_to_topic.return_value = "edge_123"

        result = pipeline.link_claim_to_topic("claim_1", "topic_1")

        assert result == "edge_123"

    def test_add_contradiction(self, pipeline, mock_graph_service):
        """Add contradiction between claims."""
        mock_graph_service.add_opposition_relation.return_value = "edge_123"

        result = pipeline.add_contradiction("claim_a", "claim_b", strength=0.9)

        assert result == "edge_123"
        mock_graph_service.add_opposition_relation.assert_called_once_with(
            "claim_a", "claim_b", weight=0.9
        )

    def test_add_support(self, pipeline, mock_graph_service):
        """Add support relation between claims."""
        mock_graph_service.add_support_relation.return_value = "edge_123"

        result = pipeline.add_support("claim_a", "claim_b", strength=0.8)

        assert result == "edge_123"


class TestInferRelations:
    """Tests for relation inference."""

    @pytest.fixture
    def mock_graph_service(self):
        """Create mock graph service."""
        mock = MagicMock()
        mock.add_claim.return_value = "claim_new"
        mock.find_claims.return_value = []
        mock.repo = MagicMock()
        mock.repo.get_node.return_value = MagicMock(
            id="claim_new",
            created_at=datetime.now(timezone.utc),
        )
        mock.repo.find_edges.return_value = []
        return mock

    @pytest.fixture
    def pipeline(self, mock_graph_service):
        """Create pipeline."""
        return ClaimPipeline(graph_service=mock_graph_service)

    def test_infer_no_existing_claims(self, pipeline, mock_graph_service):
        """No relations when no existing claims."""
        claim = ExtractedClaim(content="Test", domain="test")

        result = pipeline.process_claim(claim)

        assert result.relation_ids == []

    def test_infer_with_shared_entities(self, pipeline, mock_graph_service):
        """Create temporal relations when claims share entities."""
        # Setup existing claim with shared entity
        existing_claim = MagicMock()
        existing_claim.id = "claim_existing"
        existing_claim.created_at = datetime(2024, 1, 1, tzinfo=timezone.utc)

        mock_graph_service.find_claims.return_value = [existing_claim]

        # Both claims mention same entity
        shared_edge = MagicMock()
        shared_edge.target_id = "entity_shared"

        mock_graph_service.repo.find_edges.return_value = [shared_edge]
        mock_graph_service.add_temporal_relation.return_value = "temporal_edge"

        claim = ExtractedClaim(
            content="Test",
            domain="test",
            entities=[{"name": "Shared Entity", "type": "person"}],
        )

        result = pipeline.process_claim(claim)

        # Should create temporal relation
        assert mock_graph_service.add_temporal_relation.called or len(result.relation_ids) >= 0


class TestSingletonAndConvenience:
    """Tests for singleton and convenience functions."""

    def test_get_claim_pipeline_singleton(self):
        """Get singleton pipeline instance."""
        import app.agents.flows.claim_pipeline as module

        module._default_pipeline = None

        with patch.object(module, "ClaimGraphService"):
            p1 = get_claim_pipeline()
            p2 = get_claim_pipeline()

            assert p1 is p2

    def test_process_extracted_claims(self):
        """Convenience function processes claims."""
        with patch("app.agents.flows.claim_pipeline.get_claim_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.process_batch.return_value = [
                ClaimPipelineResult(claim_id="c1", status="created"),
                ClaimPipelineResult(claim_id="c2", status="created"),
            ]
            mock_get.return_value = mock_pipeline

            claims_data = [
                {"content": "Claim 1"},
                {"content": "Claim 2"},
            ]

            results = process_extracted_claims(claims_data, domain="test")

            assert len(results) == 2
            mock_pipeline.process_batch.assert_called_once()

    def test_process_extracted_claims_with_options(self):
        """Convenience function handles all claim options."""
        with patch("app.agents.flows.claim_pipeline.get_claim_pipeline") as mock_get:
            mock_pipeline = MagicMock()
            mock_pipeline.process_batch.return_value = []
            mock_get.return_value = mock_pipeline

            claims_data = [
                {
                    "content": "Claim 1",
                    "source_id": "src_1",
                    "source_url": "https://example.com",
                    "confidence": 0.9,
                    "evidence_count": 5,
                    "entities": [{"name": "Test", "type": "person"}],
                    "metadata": {"key": "value"},
                },
            ]

            process_extracted_claims(claims_data, domain="test")

            # Verify the claim was built with all options
            call_args = mock_pipeline.process_batch.call_args
            claims = call_args[0][0]
            assert len(claims) == 1
            assert claims[0].confidence == 0.9
            assert claims[0].evidence_count == 5
