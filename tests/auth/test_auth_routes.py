"""
Tests for Auth Routes — S37

Tests for authentication routes (login).
"""

import pytest
import os
from unittest.mock import patch

from app.auth.routes import (
    LoginRequest,
    _build_user_payload,
    DEV_USERNAME,
    DEV_PASSWORD,
    DEV_TOKEN,
    DEV_ENV,
)


class TestBuildUserPayload:
    """Tests for _build_user_payload function."""

    def test_build_user_payload(self):
        """Build user payload from username."""
        payload = _build_user_payload("test@example.com")

        assert payload["id"] == "dev-admin"
        assert payload["name"] == "Dev Admin"
        assert payload["email"] == "test@example.com"
        assert payload["roles"] == ["admin"]

    def test_build_user_payload_different_email(self):
        """Build user payload with different email."""
        payload = _build_user_payload("another@test.com")

        assert payload["email"] == "another@test.com"


class TestLoginRequest:
    """Tests for LoginRequest model."""

    def test_login_request_creation(self):
        """Create login request."""
        request = LoginRequest(username="test@test.com", password="password123")

        assert request.username == "test@test.com"
        assert request.password == "password123"


class TestDevCredentials:
    """Tests for dev environment credentials (fail-closed security)."""

    def test_no_default_credentials(self):
        """Credentials should NOT have hardcoded defaults (security fix).

        This is a security-critical test: dev credentials must come from
        environment variables only. Hardcoded defaults were a vulnerability.
        """
        # After security fix, these should be None unless env vars are set
        # If env vars are set in test environment, they should match
        import os
        assert DEV_USERNAME == os.environ.get("INSPECTAH_DEV_USER")
        assert DEV_PASSWORD == os.environ.get("INSPECTAH_DEV_PASSWORD")
        assert DEV_TOKEN == os.environ.get("INSPECTAH_DEV_TOKEN")

    def test_dev_env_defaults_to_production(self):
        """DEV_ENV should default to 'production' (fail-closed)."""
        import os
        # If INSPECTAH_ENV is not set, default should be 'production'
        if not os.environ.get("INSPECTAH_ENV"):
            assert DEV_ENV == "production"


@pytest.mark.skipif(
    os.environ.get("SKIP_FASTAPI_TESTS", "").lower() == "true",
    reason="FastAPI tests skipped"
)
class TestLoginEndpoint:
    """Tests for /auth/login endpoint."""

    # Test credentials for dev environment
    TEST_USERNAME = "test@inspectah.dev"
    TEST_PASSWORD = "test-password-123"
    TEST_TOKEN = "test-dev-token-xyz"

    @pytest.fixture
    def client(self):
        """Create test client with mocked dev credentials."""
        try:
            from fastapi.testclient import TestClient
            from fastapi import FastAPI
        except ImportError:
            pytest.skip("FastAPI not available")

        # Patch environment to set dev credentials
        with patch.dict(os.environ, {
            "INSPECTAH_ENV": "dev",
            "INSPECTAH_DEV_USER": self.TEST_USERNAME,
            "INSPECTAH_DEV_PASSWORD": self.TEST_PASSWORD,
            "INSPECTAH_DEV_TOKEN": self.TEST_TOKEN,
        }):
            # Reload module to pick up patched env vars
            import importlib
            import app.auth.routes as routes_module
            importlib.reload(routes_module)

            app = FastAPI()
            app.include_router(routes_module.router)
            yield TestClient(app)

    def test_login_success(self, client):
        """Successful login returns token."""
        response = client.post(
            "/auth/login",
            json={
                "username": self.TEST_USERNAME,
                "password": self.TEST_PASSWORD,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["email"] == self.TEST_USERNAME

    def test_login_invalid_credentials(self, client):
        """Invalid credentials return 401."""
        response = client.post(
            "/auth/login",
            json={
                "username": "wrong@email.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    def test_login_wrong_password(self, client):
        """Wrong password returns 401."""
        response = client.post(
            "/auth/login",
            json={
                "username": self.TEST_USERNAME,
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401


@pytest.mark.skipif(
    os.environ.get("SKIP_FASTAPI_TESTS", "").lower() == "true",
    reason="FastAPI tests skipped"
)
class TestLoginEndpointProductionEnv:
    """Tests for /auth/login in production environment."""

    @pytest.fixture
    def client(self):
        """Create test client with production environment."""
        try:
            from fastapi.testclient import TestClient
            from fastapi import FastAPI
        except ImportError:
            pytest.skip("FastAPI not available")

        # Patch environment to production (login should be disabled)
        with patch.dict(os.environ, {
            "INSPECTAH_ENV": "production",
            "INSPECTAH_DEV_USER": "test@test.com",
            "INSPECTAH_DEV_PASSWORD": "testpass",
            "INSPECTAH_DEV_TOKEN": "testtoken",
        }):
            import importlib
            import app.auth.routes as routes_module
            importlib.reload(routes_module)

            app = FastAPI()
            app.include_router(routes_module.router)
            yield TestClient(app)

    def test_login_non_dev_env(self, client):
        """Login disabled outside dev environment."""
        response = client.post(
            "/auth/login",
            json={
                "username": "test@test.com",
                "password": "testpass",
            },
        )

        # In production, should return 403
        assert response.status_code == 403
