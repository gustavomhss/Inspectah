"""
Tests for Auth JWT Middleware — S37

Tests for AuthJWTMiddleware authentication and authorization.
"""

import pytest
import json
import time
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path

import jwt


class TestAuthJWTMiddleware:
    """Tests for AuthJWTMiddleware class."""

    @pytest.fixture
    def mock_jwks(self, tmp_path):
        """Create mock JWKS file."""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        # Generate RSA key pair
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

        # Create JWKS
        public_numbers = public_key.public_numbers()
        import base64

        def int_to_base64url(n, length=None):
            data = n.to_bytes((n.bit_length() + 7) // 8, 'big')
            if length and len(data) < length:
                data = b'\x00' * (length - len(data)) + data
            return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

        jwks = {
            "keys": [
                {
                    "kty": "RSA",
                    "kid": "test-key-1",
                    "use": "sig",
                    "alg": "RS256",
                    "n": int_to_base64url(public_numbers.n),
                    "e": int_to_base64url(public_numbers.e),
                }
            ]
        }

        jwks_path = tmp_path / ".well-known" / "jwks.json"
        jwks_path.parent.mkdir(parents=True)
        jwks_path.write_text(json.dumps(jwks))

        return {
            "path": jwks_path,
            "private_key": private_key,
            "public_key": public_key,
            "kid": "test-key-1",
        }

    @pytest.fixture
    def create_token(self, mock_jwks):
        """Factory for creating JWT tokens."""
        def _create(
            sub: str = "test-user",
            role: str = "admin",
            exp_offset: int = 3600,
            **extra_claims
        ):
            now = int(time.time())
            payload = {
                "sub": sub,
                "role": role,
                "iss": "inspectah-idp",
                "aud": "inspectah-api",
                "iat": now,
                "exp": now + exp_offset,
                "nbf": now,
                **extra_claims,
            }
            return jwt.encode(
                payload,
                mock_jwks["private_key"],
                algorithm="RS256",
                headers={"kid": mock_jwks["kid"]},
            )
        return _create

    def test_is_public_root(self):
        """Root path is public."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_public("/") is True

    def test_is_public_auth(self):
        """Auth routes are public."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_public("/auth/login") is True
        assert middleware._is_public("/auth/callback") is True

    def test_is_public_metrics(self):
        """Metrics route is public."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_public("/metrics") is True

    def test_is_public_health(self):
        """Health route is public."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_public("/health") is True

    def test_is_public_docs(self):
        """Docs routes are public."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_public("/docs") is True
        assert middleware._is_public("/openapi.json") is True

    def test_is_protected_api(self):
        """API routes are protected."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_protected("/api/something") is True
        assert middleware._is_protected("/api/truth/claims") is True

    def test_is_protected_admin(self):
        """Admin routes are protected."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._is_protected("/admin/users") is True
        assert middleware._is_protected("/admin/cases") is True

    def test_allowed_roles_admin(self):
        """Admin routes require admin or ops_ingest."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())

        allowed = middleware._allowed_roles("/admin/users")
        assert allowed == {"admin", "ops_ingest"}

        allowed = middleware._allowed_roles("/api/admin/something")
        assert allowed == {"admin", "ops_ingest"}

    def test_allowed_roles_ingestion(self):
        """Ingestion routes require admin or ops_ingest."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        allowed = middleware._allowed_roles("/api/ingestion/run")
        assert allowed == {"admin", "ops_ingest"}

    def test_allowed_roles_truth(self):
        """Truth routes require truth_admin or truth_reviewer."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        allowed = middleware._allowed_roles("/api/truth/claims")
        assert allowed == {"truth_admin", "truth_reviewer"}

    def test_allowed_roles_providers(self):
        """Providers routes require admin or ops_ingest."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        allowed = middleware._allowed_roles("/api/providers/list")
        assert allowed == {"admin", "ops_ingest"}

    def test_allowed_roles_console(self):
        """Console routes require admin or ops_ingest."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        allowed = middleware._allowed_roles("/api/console/query")
        assert allowed == {"admin", "ops_ingest"}

    def test_allowed_roles_other(self):
        """Other routes have no role restriction."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        allowed = middleware._allowed_roles("/api/other/endpoint")
        assert allowed is None

    def test_route_label_admin(self):
        """Route label for admin paths."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._route_label("/admin/users") == "/admin"

    def test_route_label_api(self):
        """Route label for API paths."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._route_label("/api/something") == "/api"

    def test_route_label_ingestion(self):
        """Route label for ingestion paths."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._route_label("/api/ingestion/run") == "/api/ingestion"

    def test_route_label_truth(self):
        """Route label for truth paths."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._route_label("/api/truth/claims") == "/api/truth"

    def test_extract_token_valid(self):
        """Extract token from valid Authorization header."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Bearer abc123token"

        token = middleware._extract_token(mock_request)
        assert token == "abc123token"

    def test_extract_token_missing(self):
        """Extract token raises when header missing."""
        from app.middlewares.auth import AuthJWTMiddleware
        from jwt import InvalidTokenError

        middleware = AuthJWTMiddleware(MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None

        with pytest.raises(InvalidTokenError, match="missing bearer token"):
            middleware._extract_token(mock_request)

    def test_extract_token_no_bearer(self):
        """Extract token raises when not Bearer type."""
        from app.middlewares.auth import AuthJWTMiddleware
        from jwt import InvalidTokenError

        middleware = AuthJWTMiddleware(MagicMock())
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "Basic abc123"

        with pytest.raises(InvalidTokenError, match="missing bearer token"):
            middleware._extract_token(mock_request)

    def test_jwks_caching(self, mock_jwks, tmp_path):
        """JWKS is cached."""
        from app.middlewares.auth import AuthJWTMiddleware, JWKS_CACHE_TTL

        with patch("app.middlewares.auth.JWKS_PATH", mock_jwks["path"]):
            middleware = AuthJWTMiddleware(MagicMock())

            # First call loads JWKS
            jwks1 = middleware._get_jwks()
            loaded_at = middleware._jwks_loaded_at

            # Second call uses cache
            jwks2 = middleware._get_jwks()
            assert jwks1 == jwks2
            assert middleware._jwks_loaded_at == loaded_at

    def test_custom_protected_prefixes(self):
        """Custom protected prefixes."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(
            MagicMock(),
            protected_prefixes=("/custom", "/other"),
        )
        assert middleware._is_protected("/custom/path") is True
        assert middleware._is_protected("/other/path") is True
        assert middleware._is_protected("/api/path") is False

    def test_custom_public_prefixes(self):
        """Custom public prefixes."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(
            MagicMock(),
            public_prefixes=("/public", "/open"),
        )
        assert middleware._is_public("/public/path") is True
        assert middleware._is_public("/open/path") is True
        assert middleware._is_public("/auth/login") is False


class TestAuditLogging:
    """Tests for audit logging functionality."""

    def test_audit_log_format(self, tmp_path):
        """Audit log entries are JSON formatted."""
        from app.middlewares.auth import AuthJWTMiddleware

        audit_log = tmp_path / "audit.log"

        with patch("app.middlewares.auth.AUDIT_LOG", audit_log):
            middleware = AuthJWTMiddleware(MagicMock())

            mock_request = MagicMock()
            mock_request.url.path = "/api/test"
            mock_request.method = "GET"

            middleware._audit(
                request=mock_request,
                status=200,
                started=time.time(),
                actor="test-user",
                role="admin",
                op_id="op_123",
                request_id="req_456",
                error_type=None,
            )

            # Read audit log
            content = audit_log.read_text()
            entry = json.loads(content.strip())

            assert entry["route"] == "/api/test"
            assert entry["method"] == "GET"
            assert entry["status"] == 200
            assert entry["actor"] == "test-user"
            assert entry["role"] == "admin"
            assert entry["op_id"] == "op_123"
            assert entry["request_id"] == "req_456"
            assert entry["error_type"] is None
            assert "ts" in entry
            assert "latency_ms" in entry


class TestLoadJwks:
    """Tests for _load_jwks function."""

    def test_load_jwks_file_not_found(self, tmp_path):
        """_load_jwks raises FileNotFoundError when file missing."""
        from app.middlewares.auth import _load_jwks

        with patch("app.middlewares.auth.JWKS_PATH", tmp_path / "nonexistent.json"):
            with pytest.raises(FileNotFoundError, match="JWKS não encontrado"):
                _load_jwks()

    def test_load_jwks_success(self, tmp_path):
        """_load_jwks loads JWKS successfully."""
        from app.middlewares.auth import _load_jwks

        jwks_file = tmp_path / "jwks.json"
        jwks_data = {"keys": [{"kid": "test", "kty": "RSA"}]}
        jwks_file.write_text(json.dumps(jwks_data))

        with patch("app.middlewares.auth.JWKS_PATH", jwks_file):
            result = _load_jwks()

        assert result == jwks_data


class TestDecodeToken:
    """Tests for token decoding edge cases."""

    def test_decode_token_missing_kid(self, tmp_path):
        """Decode token raises when kid is missing."""
        from app.middlewares.auth import AuthJWTMiddleware
        from jwt import InvalidTokenError

        # Create a token without kid in header
        import jwt as pyjwt

        token = pyjwt.encode(
            {"sub": "user", "iss": "inspectah-idp", "aud": "inspectah-api"},
            "secret",
            algorithm="HS256",
        )

        jwks_file = tmp_path / "jwks.json"
        jwks_file.write_text(json.dumps({"keys": []}))

        with patch("app.middlewares.auth.JWKS_PATH", jwks_file):
            middleware = AuthJWTMiddleware(MagicMock())

            with pytest.raises(InvalidTokenError, match="missing kid"):
                middleware._decode_token(token)

    def test_decode_token_kid_not_found(self, tmp_path):
        """Decode token raises when kid not in JWKS."""
        from app.middlewares.auth import AuthJWTMiddleware
        from jwt import InvalidTokenError
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        import jwt as pyjwt

        # Generate a key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Create token with kid that's not in JWKS
        token = pyjwt.encode(
            {"sub": "user", "iss": "inspectah-idp", "aud": "inspectah-api"},
            private_key,
            algorithm="RS256",
            headers={"kid": "unknown-kid"},
        )

        # JWKS has a different kid
        jwks_file = tmp_path / "jwks.json"
        jwks_file.write_text(json.dumps({"keys": [{"kid": "other-kid", "kty": "RSA"}]}))

        with patch("app.middlewares.auth.JWKS_PATH", jwks_file):
            middleware = AuthJWTMiddleware(MagicMock())

            with pytest.raises(InvalidTokenError, match="kid not found"):
                middleware._decode_token(token)


class TestRouteLabelOther:
    """Tests for route label edge cases."""

    def test_route_label_other(self):
        """Route label returns 'other' for unknown paths."""
        from app.middlewares.auth import AuthJWTMiddleware

        middleware = AuthJWTMiddleware(MagicMock())
        assert middleware._route_label("/unknown/path") == "other"
        assert middleware._route_label("/some/random/path") == "other"


class TestDispatchAsync:
    """Async tests for dispatch method."""

    def test_dispatch_public_path(self):
        """Dispatch allows public paths without auth."""
        import anyio
        from app.middlewares.auth import AuthJWTMiddleware

        async def run_test():
            mock_app = MagicMock()
            middleware = AuthJWTMiddleware(mock_app)

            mock_request = MagicMock()
            mock_request.url.path = "/health"

            mock_response = MagicMock()
            mock_call_next = AsyncMock(return_value=mock_response)

            result = await middleware.dispatch(mock_request, mock_call_next)

            assert result == mock_response
            mock_call_next.assert_called_once_with(mock_request)

        anyio.run(run_test)

    def test_dispatch_non_protected_path(self):
        """Dispatch allows non-protected paths without auth."""
        import anyio
        from app.middlewares.auth import AuthJWTMiddleware

        async def run_test():
            mock_app = MagicMock()
            middleware = AuthJWTMiddleware(mock_app)

            mock_request = MagicMock()
            mock_request.url.path = "/some/random/path"  # Not in protected or public

            mock_response = MagicMock()
            mock_call_next = AsyncMock(return_value=mock_response)

            result = await middleware.dispatch(mock_request, mock_call_next)

            assert result == mock_response

        anyio.run(run_test)

    def test_dispatch_forbidden_role(self, tmp_path):
        """Dispatch returns 403 for forbidden role."""
        import anyio
        from app.middlewares.auth import AuthJWTMiddleware
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend
        import jwt as pyjwt
        import base64

        # Generate RSA key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        public_numbers = public_key.public_numbers()

        def int_to_base64url(n, length=None):
            data = n.to_bytes((n.bit_length() + 7) // 8, 'big')
            return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

        # Create JWKS
        jwks = {
            "keys": [{
                "kty": "RSA",
                "kid": "test-key",
                "use": "sig",
                "alg": "RS256",
                "n": int_to_base64url(public_numbers.n),
                "e": int_to_base64url(public_numbers.e),
            }]
        }
        jwks_file = tmp_path / "jwks.json"
        jwks_file.write_text(json.dumps(jwks))

        # Create token with wrong role
        now = int(time.time())
        token = pyjwt.encode(
            {
                "sub": "user",
                "role": "viewer",  # Not admin or ops_ingest
                "iss": "inspectah-idp",
                "aud": "inspectah-api",
                "iat": now,
                "exp": now + 3600,
            },
            private_key,
            algorithm="RS256",
            headers={"kid": "test-key"},
        )

        async def run_test():
            with patch("app.middlewares.auth.JWKS_PATH", jwks_file):
                with patch("app.middlewares.auth.AUDIT_LOG", tmp_path / "audit.log"):
                    middleware = AuthJWTMiddleware(MagicMock())

                    mock_request = MagicMock()
                    mock_request.url.path = "/admin/users"  # Requires admin role
                    mock_request.method = "GET"
                    mock_request.headers.get.return_value = f"Bearer {token}"

                    mock_call_next = AsyncMock()

                    result = await middleware.dispatch(mock_request, mock_call_next)

                    assert result.status_code == 403
                    mock_call_next.assert_not_called()

        anyio.run(run_test)

    def test_dispatch_invalid_token(self, tmp_path):
        """Dispatch returns 401 for invalid token."""
        import anyio
        from app.middlewares.auth import AuthJWTMiddleware

        jwks_file = tmp_path / "jwks.json"
        jwks_file.write_text(json.dumps({"keys": []}))

        async def run_test():
            with patch("app.middlewares.auth.JWKS_PATH", jwks_file):
                with patch("app.middlewares.auth.AUDIT_LOG", tmp_path / "audit.log"):
                    middleware = AuthJWTMiddleware(MagicMock())

                    mock_request = MagicMock()
                    mock_request.url.path = "/api/test"
                    mock_request.method = "GET"
                    mock_request.headers.get.return_value = "Bearer invalid_token"

                    mock_call_next = AsyncMock()

                    result = await middleware.dispatch(mock_request, mock_call_next)

                    assert result.status_code == 401

        anyio.run(run_test)

    def test_dispatch_jwks_missing(self, tmp_path):
        """Dispatch returns 401 when JWKS missing."""
        import anyio
        from app.middlewares.auth import AuthJWTMiddleware

        async def run_test():
            with patch("app.middlewares.auth.JWKS_PATH", tmp_path / "nonexistent.json"):
                with patch("app.middlewares.auth.AUDIT_LOG", tmp_path / "audit.log"):
                    middleware = AuthJWTMiddleware(MagicMock())

                    mock_request = MagicMock()
                    mock_request.url.path = "/api/test"
                    mock_request.method = "GET"
                    mock_request.headers.get.return_value = "Bearer some_token"

                    mock_call_next = AsyncMock()

                    result = await middleware.dispatch(mock_request, mock_call_next)

                    assert result.status_code == 401

        anyio.run(run_test)
