"""
Tests for S40 Claims API endpoints.

S40-BE-012: Export endpoint
S40-BE-016: Signals endpoint
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.claims_routes import router


@pytest.fixture
def client():
    """Create test client."""
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestExportClaimgraphEndpoint:
    """Tests for GET /api/v1/claims/export (S40-BE-012)."""

    def test_export_requires_domain(self, client):
        """Export requires domain parameter."""
        response = client.get("/api/v1/claims/export")
        assert response.status_code == 422  # Validation error

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
    """Tests for GET /api/v1/claims/{claim_id}/signals (S40-BE-016)."""

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
        # First add a signal to the repository
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

        # Verify signal structure
        sig = data["signals"][0]
        assert "signal_id" in sig
        assert "type" in sig
        assert "severity" in sig
        assert "reason" in sig
        assert "detected_at" in sig
        assert "resolved" in sig

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
        # Resolved signals are excluded by default
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

        data = response.json()
        # Should include resolved signals
        all_signals = [s for s in data["signals"] if s["signal_id"] == signal.signal_id]
        assert len(all_signals) >= 1


class TestClaimsRoutesIntegration:
    """Integration tests for claims routes."""

    def test_export_then_check_signals(self, client):
        """Export and signals work together."""
        # Export first
        export_response = client.get("/api/v1/claims/export?domain=integration")
        assert export_response.status_code == 200

        # Then check signals
        signals_response = client.get("/api/v1/claims/integration-claim/signals")
        assert signals_response.status_code == 200
