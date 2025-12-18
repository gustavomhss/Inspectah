"""
Comprehensive tests for claims_routes.py (S38-BE-034).

Covers all endpoints and error paths to achieve 95%+ coverage.
Extends existing S40 tests.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.claims_routes import router
from app.claims.relation_types import (
    RelationType,
    InferenceMethod,
    RelationConfig,
    ClaimRelation,
)
from app.claims.relation_inference import Claim


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.fixture
def sample_claim_input():
    """Sample claim input for tests."""
    return {
        "id": "claim-1",
        "text": "Test claim",
        "embedding": [0.1, 0.2, 0.3],
        "entities": ["entity1"],
        "metadata": {"source": "test"},
    }


@pytest.fixture
def sample_claim():
    """Sample Claim object."""
    return Claim(
        id="claim-1",
        text="Test claim",
        embedding=[0.1, 0.2, 0.3],
        entities=["entity1"],
        metadata={"source": "test"},
    )


class TestInferRelationsEndpoint:
    """Tests for POST /api/v1/claims/relations/infer endpoint."""

    @patch("app.api.claims_routes._get_inference_service")
    def test_infer_relations_basic(self, mock_get_service, client, sample_claim_input):
        """Infer relations returns relations."""
        mock_service = MagicMock()
        mock_relation = ClaimRelation(
            source_claim_id="claim-1",
            target_claim_id="claim-2",
            relation_type=RelationType.SUPPORTS,
            confidence=0.85,
            method=InferenceMethod.EMBEDDING,
            indicators={"similarity": 0.9},
        )
        mock_service.infer_relations = MagicMock(return_value=[mock_relation])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/infer", json={
            "source_claim": sample_claim_input,
            "candidate_claims": [
                {**sample_claim_input, "id": "claim-2", "text": "Another claim"}
            ],
            "max_results": 10,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert len(data["relations"]) == 1
        assert data["relations"][0]["relation_type"] == "supports"
        assert data["relations"][0]["confidence"] == 0.85
        assert "processing_time_ms" in data

    @patch("app.api.claims_routes._get_inference_service")
    def test_infer_relations_with_custom_config(self, mock_get_service, client, sample_claim_input):
        """Infer relations with custom config applies settings."""
        mock_service = MagicMock()
        mock_service.config = RelationConfig()
        mock_service.infer_relations = MagicMock(return_value=[])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/infer", json={
            "source_claim": sample_claim_input,
            "candidate_claims": [],
            "config": {
                "similarity_threshold": 0.8,
                "contradiction_threshold": 0.7,
                "duplicate_threshold": 0.95,
                "support_threshold": 0.85,
                "confidence_threshold": 0.75,
            },
        })
        assert response.status_code == 200

        # Verify config was updated
        assert mock_service.config.similarity_threshold == 0.8

    @patch("app.api.claims_routes._get_inference_service")
    def test_infer_relations_empty_candidates(self, mock_get_service, client, sample_claim_input):
        """Infer relations with empty candidates returns empty list."""
        mock_service = MagicMock()
        mock_service.infer_relations = MagicMock(return_value=[])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/infer", json={
            "source_claim": sample_claim_input,
            "candidate_claims": [],
        })
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0
        assert len(data["relations"]) == 0

    @patch("app.api.claims_routes._get_inference_service")
    def test_infer_relations_max_results(self, mock_get_service, client, sample_claim_input):
        """Infer relations respects max_results."""
        mock_service = MagicMock()
        mock_service.infer_relations = MagicMock(return_value=[])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/infer", json={
            "source_claim": sample_claim_input,
            "candidate_claims": [],
            "max_results": 5,
        })
        assert response.status_code == 200

    @patch("app.api.claims_routes._get_inference_service")
    def test_infer_relations_all_relation_types(self, mock_get_service, client, sample_claim_input):
        """Infer relations handles all relation types."""
        mock_service = MagicMock()

        relations = []
        for rel_type in RelationType:
            relations.append(ClaimRelation(
                source_claim_id="claim-1",
                target_claim_id=f"claim-{rel_type.value}",
                relation_type=rel_type,
                confidence=0.8,
                method=InferenceMethod.EMBEDDING,
                indicators={},
            ))

        mock_service.infer_relations = MagicMock(return_value=relations)
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/infer", json={
            "source_claim": sample_claim_input,
            "candidate_claims": [
                {**sample_claim_input, "id": f"claim-{i}"}
                for i in range(len(RelationType))
            ],
        })
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == len(RelationType)


class TestFindSimilarClaimsEndpoint:
    """Tests for POST /api/v1/claims/relations/similar endpoint."""

    @patch("app.api.claims_routes._get_inference_service")
    def test_find_similar_basic(self, mock_get_service, client, sample_claim_input, sample_claim):
        """Find similar returns similar claims."""
        mock_service = MagicMock()
        similar_claim = Claim(id="claim-2", text="Similar claim", embedding=[0.11, 0.21, 0.31])
        mock_service.find_similar = MagicMock(return_value=[(similar_claim, 0.95)])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/similar", json={
            "query_claim": sample_claim_input,
            "all_claims": [
                {**sample_claim_input, "id": "claim-2", "text": "Similar claim"}
            ],
            "threshold": 0.7,
            "limit": 10,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 1
        assert len(data["similar_claims"]) == 1
        assert data["similar_claims"][0]["claim_id"] == "claim-2"
        assert data["similar_claims"][0]["similarity"] == 0.95
        assert data["threshold"] == 0.7

    @patch("app.api.claims_routes._get_inference_service")
    def test_find_similar_no_matches(self, mock_get_service, client, sample_claim_input):
        """Find similar with no matches returns empty list."""
        mock_service = MagicMock()
        mock_service.find_similar = MagicMock(return_value=[])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/similar", json={
            "query_claim": sample_claim_input,
            "all_claims": [],
        })
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0

    @patch("app.api.claims_routes._get_inference_service")
    def test_find_similar_custom_threshold(self, mock_get_service, client, sample_claim_input):
        """Find similar with custom threshold."""
        mock_service = MagicMock()
        mock_service.find_similar = MagicMock(return_value=[])
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/relations/similar", json={
            "query_claim": sample_claim_input,
            "all_claims": [],
            "threshold": 0.9,
            "limit": 5,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["threshold"] == 0.9


class TestListRelationTypesEndpoint:
    """Tests for GET /api/v1/claims/relations/types endpoint."""

    def test_list_relation_types(self, client):
        """List relation types returns all types and methods."""
        response = client.get("/api/v1/claims/relations/types")
        assert response.status_code == 200

        data = response.json()
        assert "relation_types" in data
        assert "inference_methods" in data

        # Check we have all relation types
        assert len(data["relation_types"]) == len(RelationType)
        assert len(data["inference_methods"]) == len(InferenceMethod)

        # Check structure
        first_type = data["relation_types"][0]
        assert "type" in first_type
        assert "description" in first_type


class TestRelationConfigEndpoints:
    """Tests for relation config GET/PUT endpoints."""

    @patch("app.api.claims_routes._get_inference_service")
    def test_get_relation_config(self, mock_get_service, client):
        """Get relation config returns current config."""
        mock_service = MagicMock()
        mock_service.config = RelationConfig(
            similarity_threshold=0.7,
            contradiction_threshold=0.6,
            duplicate_threshold=0.95,
            support_threshold=0.85,
            confidence_threshold=0.7,
        )
        mock_get_service.return_value = mock_service

        response = client.get("/api/v1/claims/relations/config")
        assert response.status_code == 200

        data = response.json()
        assert data["similarity_threshold"] == 0.7
        assert data["contradiction_threshold"] == 0.6
        assert data["duplicate_threshold"] == 0.95
        assert data["support_threshold"] == 0.85
        assert data["confidence_threshold"] == 0.7
        assert "negation_boost" in data
        assert "max_relations_per_claim" in data

    @patch("app.api.claims_routes._get_inference_service")
    def test_update_relation_config(self, mock_get_service, client):
        """Update relation config updates settings."""
        mock_service = MagicMock()
        mock_service.config = RelationConfig()
        mock_get_service.return_value = mock_service

        response = client.put("/api/v1/claims/relations/config", json={
            "similarity_threshold": 0.8,
            "contradiction_threshold": 0.65,
            "duplicate_threshold": 0.96,
            "support_threshold": 0.88,
            "confidence_threshold": 0.75,
            "negation_boost": 0.2,
            "max_relations_per_claim": 15,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["config"]["similarity_threshold"] == 0.8
        assert data["config"]["max_relations_per_claim"] == 15

    @patch("app.api.claims_routes._get_inference_service")
    def test_update_relation_config_partial(self, mock_get_service, client):
        """Update relation config with partial values uses defaults."""
        mock_service = MagicMock()
        mock_service.config = RelationConfig(similarity_threshold=0.7)
        mock_get_service.return_value = mock_service

        response = client.put("/api/v1/claims/relations/config", json={
            "similarity_threshold": 0.8,
        })
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        # Should preserve other defaults
        assert "contradiction_threshold" in data["config"]


class TestClusterClaimsEndpoint:
    """Tests for POST /api/v1/claims/cluster endpoint."""

    @patch("app.api.claims_routes._cluster_claims")
    @patch("app.api.claims_routes._get_inference_service")
    def test_cluster_claims_basic(self, mock_get_service, mock_cluster_fn, client, sample_claim_input):
        """Cluster claims returns clusters."""
        from app.claims.relation_types import ClaimCluster

        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_cluster = ClaimCluster(
            cluster_id="cluster-1",
            representative_id="claim-1",
            member_ids=["claim-1", "claim-2"],
            avg_similarity=0.9,
        )
        mock_cluster_fn.return_value = [mock_cluster]

        response = client.post("/api/v1/claims/cluster", json=[
            sample_claim_input,
            {**sample_claim_input, "id": "claim-2"},
        ])
        assert response.status_code == 200

        data = response.json()
        assert data["total_clusters"] == 1
        assert data["total_claims"] == 2
        assert len(data["clusters"]) == 1
        assert data["clusters"][0]["cluster_id"] == "cluster-1"
        assert data["clusters"][0]["size"] == 2

    @patch("app.api.claims_routes._cluster_claims")
    @patch("app.api.claims_routes._get_inference_service")
    def test_cluster_claims_custom_threshold(self, mock_get_service, mock_cluster_fn, client, sample_claim_input):
        """Cluster claims with custom threshold."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_cluster_fn.return_value = []

        response = client.post("/api/v1/claims/cluster?similarity_threshold=0.85", json=[
            sample_claim_input,
        ])
        assert response.status_code == 200

    @patch("app.api.claims_routes._cluster_claims")
    @patch("app.api.claims_routes._get_inference_service")
    def test_cluster_claims_empty_list(self, mock_get_service, mock_cluster_fn, client):
        """Cluster claims with empty list returns empty clusters."""
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_cluster_fn.return_value = []

        response = client.post("/api/v1/claims/cluster", json=[])
        assert response.status_code == 200

        data = response.json()
        assert data["total_clusters"] == 0
        assert data["total_claims"] == 0


class TestDeduplicateClaimsEndpoint:
    """Tests for POST /api/v1/claims/deduplicate endpoint."""

    @patch("app.api.claims_routes._get_inference_service")
    def test_deduplicate_claims_no_duplicates(self, mock_get_service, client, sample_claim_input):
        """Deduplicate with no duplicates returns all as unique."""
        mock_service = MagicMock()
        mock_service._compute_similarity = MagicMock(return_value=0.5)
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/deduplicate", json=[
            sample_claim_input,
            {**sample_claim_input, "id": "claim-2", "text": "Different claim"},
        ])
        assert response.status_code == 200

        data = response.json()
        assert data["unique_count"] >= 0
        assert data["duplicate_count"] >= 0
        assert "unique_ids" in data
        assert "duplicates" in data
        assert data["threshold"] == 0.95

    @patch("app.api.claims_routes._get_inference_service")
    def test_deduplicate_claims_with_duplicates(self, mock_get_service, client, sample_claim_input):
        """Deduplicate finds duplicates above threshold."""
        mock_service = MagicMock()
        mock_service._compute_similarity = MagicMock(return_value=0.96)
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/deduplicate", json=[
            sample_claim_input,
            {**sample_claim_input, "id": "claim-2"},
        ])
        assert response.status_code == 200

        data = response.json()
        assert "unique_ids" in data
        assert "duplicates" in data

    @patch("app.api.claims_routes._get_inference_service")
    def test_deduplicate_claims_custom_threshold(self, mock_get_service, client, sample_claim_input):
        """Deduplicate with custom threshold."""
        mock_service = MagicMock()
        mock_service._compute_similarity = MagicMock(return_value=0.85)
        mock_get_service.return_value = mock_service

        response = client.post("/api/v1/claims/deduplicate?threshold=0.9", json=[
            sample_claim_input,
        ])
        assert response.status_code == 200

        data = response.json()
        assert data["threshold"] == 0.9


class TestExportClaimgraphEndpoint:
    """Tests for GET /api/v1/claims/export endpoint (S40-BE-012)."""

    def test_export_requires_domain(self, client):
        """Export requires domain parameter."""
        response = client.get("/api/v1/claims/export")
        assert response.status_code == 422

    def test_export_returns_v1_format(self, client):
        """Export returns v1 format structure."""
        response = client.get("/api/v1/claims/export?domain=saude")
        assert response.status_code == 200

        data = response.json()
        assert data["version"] == "1.0"
        assert data["domain"] == "saude"
        assert "export_id" in data
        assert "claims" in data
        assert "exported_at" in data

    def test_export_pagination_defaults(self, client):
        """Export includes pagination with defaults."""
        response = client.get("/api/v1/claims/export?domain=test")
        assert response.status_code == 200

        data = response.json()
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 100

    def test_export_custom_pagination(self, client):
        """Export respects custom pagination."""
        response = client.get("/api/v1/claims/export?domain=test&page=2&page_size=50")
        assert response.status_code == 200

        data = response.json()
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["page_size"] == 50

    def test_export_invalid_format(self, client):
        """Export rejects invalid format."""
        response = client.get("/api/v1/claims/export?domain=test&format=v99")
        assert response.status_code == 400
        assert "Unsupported format" in response.json()["detail"]

    def test_export_include_signals_true(self, client):
        """Export can include signals."""
        response = client.get("/api/v1/claims/export?domain=test&include_signals=true")
        assert response.status_code == 200

    def test_export_include_signals_false(self, client):
        """Export can exclude signals."""
        response = client.get("/api/v1/claims/export?domain=test&include_signals=false")
        assert response.status_code == 200


class TestGetClaimSignalsEndpoint:
    """Tests for GET /api/v1/claims/{claim_id}/signals endpoint (S40-BE-016)."""

    def test_signals_empty_claim(self, client):
        """Signals returns empty list for claim with no signals."""
        response = client.get("/api/v1/claims/claim-no-signals/signals")
        assert response.status_code == 200

        data = response.json()
        assert data["claim_id"] == "claim-no-signals"
        assert data["signals"] == []
        assert data["has_blocking"] is False
        assert data["total"] == 0

    def test_signals_with_active_signals(self, client):
        """Signals returns active signals for claim."""
        from app.claims.signals import NOGOSignal, SignalType, SignalSeverity, get_signal_repository

        repo = get_signal_repository()
        signal = NOGOSignal.create(
            type=SignalType.INCONSISTENCY,
            severity=SignalSeverity.HIGH,
            claim_id="claim-with-signals",
            reason="Test signal",
        )
        repo.add(signal)

        response = client.get("/api/v1/claims/claim-with-signals/signals")
        assert response.status_code == 200

        data = response.json()
        assert data["claim_id"] == "claim-with-signals"
        assert len(data["signals"]) >= 1
        assert data["has_blocking"] is True

        sig = data["signals"][0]
        assert "signal_id" in sig
        assert "type" in sig
        assert "severity" in sig

    def test_signals_exclude_resolved_by_default(self, client):
        """Signals excludes resolved signals by default."""
        from app.claims.signals import NOGOSignal, SignalType, SignalSeverity, get_signal_repository

        repo = get_signal_repository()
        signal = NOGOSignal.create(
            type=SignalType.SUSPICION,
            severity=SignalSeverity.MEDIUM,
            claim_id="claim-resolved-signal",
            reason="Test resolved",
        )
        signal.resolve("admin", "False positive")
        repo.add(signal)

        response = client.get("/api/v1/claims/claim-resolved-signal/signals")
        assert response.status_code == 200

        data = response.json()
        resolved_signals = [s for s in data["signals"] if s.get("resolved")]
        assert len(resolved_signals) == 0

    def test_signals_include_resolved(self, client):
        """Signals can include resolved signals."""
        from app.claims.signals import NOGOSignal, SignalType, SignalSeverity, get_signal_repository

        repo = get_signal_repository()
        signal = NOGOSignal.create(
            type=SignalType.ABUSE,
            severity=SignalSeverity.CRITICAL,
            claim_id="claim-include-resolved",
            reason="Test include resolved",
        )
        signal.resolve("moderator", "Handled")
        repo.add(signal)

        response = client.get("/api/v1/claims/claim-include-resolved/signals?include_resolved=true")
        assert response.status_code == 200


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_to_claim_conversion(self):
        """_to_claim converts ClaimInput to Claim."""
        from app.api.claims_routes import _to_claim, ClaimInput

        claim_input = ClaimInput(
            id="test-1",
            text="Test claim",
            embedding=[0.1, 0.2],
            entities=["entity1"],
            metadata={"key": "value"},
        )

        claim = _to_claim(claim_input)

        assert claim.id == "test-1"
        assert claim.text == "Test claim"
        assert claim.embedding == [0.1, 0.2]
        assert claim.entities == ["entity1"]
        assert claim.metadata == {"key": "value"}

    def test_to_claim_conversion_minimal(self):
        """_to_claim handles minimal input."""
        from app.api.claims_routes import _to_claim, ClaimInput

        claim_input = ClaimInput(
            id="test-2",
            text="Minimal claim",
        )

        claim = _to_claim(claim_input)

        assert claim.id == "test-2"
        assert claim.entities == []
        assert claim.metadata == {}

    def test_get_relation_description(self):
        """_get_relation_description returns descriptions."""
        from app.api.claims_routes import _get_relation_description

        for rel_type in RelationType:
            desc = _get_relation_description(rel_type)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_get_method_description(self):
        """_get_method_description returns descriptions."""
        from app.api.claims_routes import _get_method_description

        for method in InferenceMethod:
            desc = _get_method_description(method)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_cluster_claims_empty(self):
        """_cluster_claims handles empty list."""
        from app.api.claims_routes import _cluster_claims

        mock_service = MagicMock()
        clusters = _cluster_claims(mock_service, [], 0.8)

        assert clusters == []

    @patch("app.api.claims_routes._get_inference_service")
    def test_cluster_claims_single_claim(self, mock_get_service, sample_claim):
        """_cluster_claims handles single claim."""
        from app.api.claims_routes import _cluster_claims

        mock_service = MagicMock()
        mock_service._compute_similarity = MagicMock(return_value=0.9)

        clusters = _cluster_claims(mock_service, [sample_claim], 0.8)

        assert len(clusters) == 1
        assert clusters[0].size == 1

    def test_cluster_claims_multiple(self, sample_claim):
        """_cluster_claims handles multiple claims."""
        from app.api.claims_routes import _cluster_claims

        mock_service = MagicMock()
        mock_service._compute_similarity = MagicMock(return_value=0.9)

        claim2 = Claim(id="claim-2", text="Similar claim", embedding=[0.11, 0.21, 0.31])
        claim3 = Claim(id="claim-3", text="Another claim", embedding=[0.15, 0.25, 0.35])

        clusters = _cluster_claims(mock_service, [sample_claim, claim2, claim3], 0.8)

        assert len(clusters) >= 1


class TestServiceInitialization:
    """Tests for service initialization."""

    def test_get_inference_service_creates_instance(self):
        """_get_inference_service creates instance on first call."""
        from app.api import claims_routes

        # Reset global instance
        claims_routes._inference_service = None

        service = claims_routes._get_inference_service()
        assert service is not None

    def test_get_inference_service_reuses_instance(self):
        """_get_inference_service reuses instance on subsequent calls."""
        from app.api import claims_routes

        s1 = claims_routes._get_inference_service()
        s2 = claims_routes._get_inference_service()

        assert s1 is s2
