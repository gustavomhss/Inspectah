"""
S38: Tests for API Contracts v1
"""
import pytest
from datetime import datetime, timezone

from app.contracts.v1 import (
    CONTRACT_VERSION,
    ContractStatus,
    ErrorContract,
    PaginationContract,
    ResponseEnvelope,
    ClaimContract,
    SourceContract,
    SignalContract,
    PolicyContract,
    VerdictContract,
    RelationContract,
    ContractValidator,
    success_response,
    error_response,
    partial_response,
)


class TestContractVersion:
    """Tests for contract version."""

    def test_version_format(self):
        assert CONTRACT_VERSION == "1.0.0"


class TestContractStatus:
    """Tests for ContractStatus enum."""

    def test_status_values(self):
        assert ContractStatus.SUCCESS.value == "success"
        assert ContractStatus.ERROR.value == "error"
        assert ContractStatus.PARTIAL.value == "partial"


class TestErrorContract:
    """Tests for ErrorContract."""

    def test_create_error_contract(self):
        error = ErrorContract(
            code="NOT_FOUND",
            message="Resource not found",
        )

        assert error.code == "NOT_FOUND"
        assert error.message == "Resource not found"

    def test_error_contract_with_details(self):
        error = ErrorContract(
            code="VALIDATION_ERROR",
            message="Validation failed",
            details={"field": "email", "error": "Invalid format"},
            field="email",
            trace_id="trace_123",
        )

        assert error.details is not None
        assert error.details["field"] == "email"
        assert error.field == "email"
        assert error.trace_id == "trace_123"

    def test_error_contract_to_dict(self):
        error = ErrorContract(
            code="BAD_REQUEST",
            message="Invalid input",
        )

        result = error.to_dict()
        assert result["code"] == "BAD_REQUEST"
        assert result["message"] == "Invalid input"


class TestPaginationContract:
    """Tests for PaginationContract."""

    def test_create_pagination(self):
        pagination = PaginationContract(
            page=2,
            page_size=10,
            total_items=45,
            total_pages=5,
            has_next=True,
            has_previous=True,
        )

        assert pagination.page == 2
        assert pagination.page_size == 10
        assert pagination.total_items == 45

    def test_pagination_create_factory(self):
        pagination = PaginationContract.create(
            page=1,
            page_size=20,
            total_items=100,
        )

        assert pagination.page == 1
        assert pagination.total_pages == 5
        assert pagination.has_next is True
        assert pagination.has_previous is False

    def test_pagination_to_dict(self):
        pagination = PaginationContract(
            page=1,
            page_size=20,
            total_items=200,
            total_pages=10,
            has_next=True,
            has_previous=False,
        )

        result = pagination.to_dict()
        assert result["page"] == 1
        assert result["has_next"] is True
        assert result["has_previous"] is False


class TestClaimContract:
    """Tests for ClaimContract."""

    def test_create_claim_contract(self):
        claim = ClaimContract(
            id="claim_001",
            text="Test claim text",
            source_id="source_001",
            verdict="false",
            confidence=0.85,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )

        assert claim.id == "claim_001"
        assert claim.text == "Test claim text"
        assert claim.confidence == 0.85

    def test_claim_contract_to_dict(self):
        claim = ClaimContract(
            id="claim_002",
            text="Another claim",
            source_id="source_002",
            verdict="true",
            confidence=0.9,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
            entities=["entity_1"],
            topics=["politics"],
            evidence_count=5,
        )

        result = claim.to_dict()
        assert result["id"] == "claim_002"
        assert result["confidence"] == 0.9
        assert result["evidence_count"] == 5


class TestSourceContract:
    """Tests for SourceContract."""

    def test_create_source_contract(self):
        source = SourceContract(
            id="source_001",
            name="Test Source",
            slug="test-source",
            source_type="news",
            url="https://example.com",
            enabled=True,
            state="active",
            health_status="healthy",
            credibility_score=0.8,
            created_at="2024-01-01T00:00:00",
            last_ingestion_at=None,
        )

        assert source.id == "source_001"
        assert source.name == "Test Source"
        assert source.source_type == "news"

    def test_source_contract_to_dict(self):
        source = SourceContract(
            id="source_002",
            name="Official Source",
            slug="official-source",
            source_type="government",
            url="https://gov.br",
            enabled=True,
            state="active",
            health_status="healthy",
            credibility_score=0.95,
            created_at="2024-01-01T00:00:00",
            last_ingestion_at="2024-01-02T00:00:00",
        )

        result = source.to_dict()
        assert result["id"] == "source_002"
        assert result["credibility_score"] == 0.95


class TestSignalContract:
    """Tests for SignalContract."""

    def test_create_signal_contract(self):
        signal = SignalContract(
            type="mentiras_em_circulacao",
            scope="global",
            scope_id=None,
            value=0.75,
            confidence=0.9,
            level="warning",
            calculated_at="2024-01-01T00:00:00",
            expires_at="2024-01-02T00:00:00",
        )

        assert signal.type == "mentiras_em_circulacao"
        assert signal.value == 0.75

    def test_signal_contract_to_dict(self):
        signal = SignalContract(
            type="credibility_score",
            scope="source",
            scope_id="source_001",
            value=0.8,
            confidence=0.95,
            level="normal",
            calculated_at="2024-01-01T00:00:00",
            expires_at="2024-01-02T00:00:00",
        )

        result = signal.to_dict()
        assert result["type"] == "credibility_score"
        assert result["scope_id"] == "source_001"


class TestVerdictContract:
    """Tests for VerdictContract."""

    def test_create_verdict_contract(self):
        verdict = VerdictContract(
            claim_id="claim_001",
            verdict="false",
            confidence=0.9,
            reasoning="Multiple sources contradict the claim",
            evidence_ids=["ev_001", "ev_002"],
            sources_count=3,
            decided_at="2024-01-01T00:00:00",
            decided_by="system",
            policy_id="policy_001",
        )

        assert verdict.claim_id == "claim_001"
        assert verdict.verdict == "false"
        assert verdict.confidence == 0.9

    def test_verdict_contract_to_dict(self):
        verdict = VerdictContract(
            claim_id="claim_002",
            verdict="true",
            confidence=0.95,
            reasoning="Verified by official sources",
            evidence_ids=["ev_003"],
            sources_count=2,
            decided_at="2024-01-01T00:00:00",
            decided_by="analyst",
            policy_id=None,
        )

        result = verdict.to_dict()
        assert result["verdict"] == "true"
        assert result["reasoning"] == "Verified by official sources"
        assert result["sources_count"] == 2


class TestPolicyContract:
    """Tests for PolicyContract."""

    def test_create_policy_contract(self):
        policy = PolicyContract(
            id="policy_001",
            name="Default Policy",
            domain="general",
            version=1,
            status="active",
            min_confidence=0.7,
            min_sources=2,
            sensitive=False,
            created_at="2024-01-01T00:00:00",
            activated_at="2024-01-01T00:00:00",
        )

        assert policy.id == "policy_001"
        assert policy.min_confidence == 0.7

    def test_policy_contract_to_dict(self):
        policy = PolicyContract(
            id="policy_002",
            name="Sensitive Policy",
            domain="health",
            version=2,
            status="draft",
            min_confidence=0.9,
            min_sources=3,
            sensitive=True,
            created_at="2024-01-01T00:00:00",
            activated_at=None,
        )

        result = policy.to_dict()
        assert result["sensitive"] is True
        assert result["status"] == "draft"


class TestRelationContract:
    """Tests for RelationContract."""

    def test_create_relation_contract(self):
        relation = RelationContract(
            source_claim_id="claim_001",
            target_claim_id="claim_002",
            relation_type="contradicts",
            confidence=0.85,
            method="semantic",
            created_at="2024-01-01T00:00:00",
        )

        assert relation.relation_type == "contradicts"
        assert relation.confidence == 0.85

    def test_relation_contract_to_dict(self):
        relation = RelationContract(
            source_claim_id="claim_003",
            target_claim_id="claim_004",
            relation_type="supports",
            confidence=0.9,
            method="embedding",
            created_at="2024-01-01T00:00:00",
        )

        result = relation.to_dict()
        assert result["relation_type"] == "supports"
        assert result["method"] == "embedding"


class TestResponseEnvelope:
    """Tests for ResponseEnvelope."""

    def test_create_success_envelope(self):
        envelope = ResponseEnvelope(
            status=ContractStatus.SUCCESS,
            data={"key": "value"},
        )

        assert envelope.status == ContractStatus.SUCCESS
        assert envelope.data == {"key": "value"}

    def test_create_error_envelope(self):
        errors = [ErrorContract("INVALID_REQUEST", "Invalid request parameters")]
        envelope = ResponseEnvelope(
            status=ContractStatus.ERROR,
            errors=errors,
        )

        assert envelope.status == ContractStatus.ERROR
        assert len(envelope.errors) == 1

    def test_envelope_to_dict(self):
        envelope = ResponseEnvelope(
            status=ContractStatus.SUCCESS,
            data={"items": [1, 2, 3]},
        )

        result = envelope.to_dict()
        assert result["status"] == "success"
        assert "meta" in result
        assert result["data"] == {"items": [1, 2, 3]}

    def test_envelope_with_pagination(self):
        pagination = PaginationContract.create(
            page=1,
            page_size=20,
            total_items=100,
        )

        envelope = ResponseEnvelope(
            status=ContractStatus.SUCCESS,
            data={"items": []},
            pagination=pagination,
        )

        result = envelope.to_dict()
        assert "pagination" in result
        assert result["pagination"]["total_items"] == 100


class TestContractValidator:
    """Tests for ContractValidator."""

    def test_validate_claim_valid(self):
        errors = ContractValidator.validate_claim({
            "id": "claim_001",
            "text": "Test claim",
        })
        assert len(errors) == 0

    def test_validate_claim_missing_id(self):
        errors = ContractValidator.validate_claim({
            "text": "Test claim",
        })
        assert len(errors) == 1
        assert errors[0].code == "MISSING_FIELD"
        assert errors[0].field == "id"

    def test_validate_claim_missing_text(self):
        errors = ContractValidator.validate_claim({
            "id": "claim_001",
        })
        assert len(errors) == 1
        assert errors[0].field == "text"

    def test_validate_source_valid(self):
        errors = ContractValidator.validate_source({
            "name": "Test Source",
            "url": "https://example.com",
            "source_type": "news",
        })
        assert len(errors) == 0

    def test_validate_source_missing_fields(self):
        errors = ContractValidator.validate_source({})
        assert len(errors) == 3


class TestResponseHelpers:
    """Tests for response helper functions."""

    def test_success_response(self):
        response = success_response(
            data={"result": "ok"},
            meta={"request_id": "123"},
        )

        assert response["status"] == "success"
        assert response["data"] == {"result": "ok"}
        assert response["meta"]["request_id"] == "123"

    def test_error_response(self):
        errors = [ErrorContract("ERR_001", "Something went wrong")]
        response = error_response(errors)

        assert response["status"] == "error"
        assert len(response["errors"]) == 1

    def test_partial_response(self):
        errors = [ErrorContract("WARN_001", "Partial data")]
        response = partial_response(
            data={"items": [1, 2]},
            errors=errors,
        )

        assert response["status"] == "partial"
        assert response["data"] == {"items": [1, 2]}
        assert len(response["errors"]) == 1
