"""
Middleware de autenticação/RBAC com JWT RS256 (JWKS) para SF3.

Regras:
- Fail-closed: erro de JWKS/token => 401.
- JWT claims: iss=inspectah-idp, aud=inspectah-api, exp/iat/nbf, sub (actor), role, op_id, request_id.
- Roles por rota:
    /admin/**, /api/admin/**, /api/ingestion/** -> admin|ops_ingest
    /api/truth/** -> truth_admin|truth_reviewer
    /api/providers/**, /api/console/** -> admin|ops_ingest
- Sem token/expirado -> 401; role errada -> 403; nunca 200 sem role.
- Métricas: auth_requests_total{status,role}, auth_latency_seconds{route} (buckets 0.1,0.5,1,2,5,10).
- Auditoria JSON em out/logs/sf3_audit.log (ts, request_id, op_id, actor, role, route, method, status, latency_ms, error_type).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Iterable, Optional

import jwt
from jwt import InvalidTokenError

try:  # pragma: no cover
    from prometheus_client import Counter, Histogram  # type: ignore
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import JSONResponse, Response
except ModuleNotFoundError:  # pragma: no cover
    raise RuntimeError("Dependencies missing for auth middleware")

logger = logging.getLogger("auth.jwt")

AUDIENCE = "inspectah-api"
ISSUER = "inspectah-idp"
JWKS_PATH = Path(".well-known/jwks.json")
JWKS_CACHE_TTL = 300  # seconds
AUDIT_LOG = Path("out/logs/sf3_audit.log")
AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)

_auth_requests_total = Counter(
    "auth_requests_total",
    "Total de requisições autenticadas por status/role",
    ["status", "role"],
)
_auth_latency = Histogram(
    "auth_latency_seconds",
    "Latência de requisições protegidas",
    ["route"],
    buckets=(0.1, 0.5, 1, 2, 5, 10),
)


def _load_jwks() -> dict:
    if not JWKS_PATH.exists():
        raise FileNotFoundError(f"JWKS não encontrado em {JWKS_PATH}")
    return json.loads(JWKS_PATH.read_text(encoding="utf-8"))


def _now() -> float:
    return time.time()


class AuthJWTMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        protected_prefixes: Iterable[str] = ("/api", "/admin"),
        public_prefixes: Iterable[str] = (
            "/auth",
            "/metrics",
            "/health",
            "/docs",
            "/openapi",
            "/static",
            "/explorer",
            "/.well-known",
        ),
    ):
        super().__init__(app)
        self._protected = tuple(protected_prefixes)
        self._public = tuple(public_prefixes)
        self._jwks_cache: dict | None = None
        self._jwks_loaded_at: float = 0.0

    async def dispatch(self, request: Request, call_next) -> Response:
        path: str = request.url.path
        if self._is_public(path):
            return await call_next(request)
        if not self._is_protected(path):
            return await call_next(request)

        start = _now()
        try:
            token = self._extract_token(request)
            claims = self._decode_token(token)
            role = claims.get("role")
            actor = claims.get("sub")
            op_id = claims.get("op_id")
            request_id = claims.get("request_id")

            allowed = self._allowed_roles(path)
            if allowed and role not in allowed:
                self._record("403", role, path, start, error="forbidden")
                return JSONResponse(
                    {"error": "forbidden", "role": role, "op_id": op_id, "request_id": request_id},
                    status_code=403,
                )

            request.state.actor = actor
            request.state.role = role
            request.state.op_id = op_id
            request.state.request_id = request_id

            response = await call_next(request)
            self._record(str(response.status_code), role, path, start)
            self._audit(request, response.status_code, start, actor, role, op_id, request_id, None)
            return response
        except InvalidTokenError as exc:
            self._record("401", "none", path, start, error="invalid_token")
            self._audit(request, 401, start, None, None, None, None, "invalid_token")
            return JSONResponse({"error": "invalid_token", "detail": str(exc)}, status_code=401)
        except FileNotFoundError:
            self._record("401", "none", path, start, error="jwks_missing")
            self._audit(request, 401, start, None, None, None, None, "jwks_missing")
            return JSONResponse({"error": "jwks_missing"}, status_code=401)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Auth middleware error")
            self._record("401", "none", path, start, error="auth_error")
            self._audit(request, 401, start, None, None, None, None, "auth_error")
            return JSONResponse({"error": "auth_error", "detail": str(exc)}, status_code=401)

    def _extract_token(self, request: Request) -> str:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            raise InvalidTokenError("missing bearer token")
        return auth_header.split(" ", 1)[1]

    def _decode_token(self, token: str) -> dict:
        jwks = self._get_jwks()
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise InvalidTokenError("missing kid")
        key_data = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key_data:
            raise InvalidTokenError("kid not found")
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))
        return jwt.decode(
            token,
            key=public_key,
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
        )

    def _get_jwks(self) -> dict:
        now = _now()
        if self._jwks_cache and (now - self._jwks_loaded_at) < JWKS_CACHE_TTL:
            return self._jwks_cache
        jwks = _load_jwks()
        self._jwks_cache = jwks
        self._jwks_loaded_at = now
        return jwks

    def _is_public(self, path: str) -> bool:
        return path == "/" or path.startswith(self._public)

    def _is_protected(self, path: str) -> bool:
        return path.startswith(self._protected)

    def _allowed_roles(self, path: str) -> Optional[set[str]]:
        if path.startswith("/admin") or path.startswith("/api/admin") or path.startswith("/api/ingestion"):
            return {"admin", "ops_ingest"}
        if path.startswith("/api/truth"):
            return {"truth_admin", "truth_reviewer"}
        if path.startswith("/api/providers") or path.startswith("/api/console"):
            return {"admin", "ops_ingest"}
        return None

    def _record(self, status: str, role: Optional[str], route: str, started: float, error: Optional[str] = None) -> None:
        _auth_requests_total.labels(status=status, role=role or "none").inc()
        _auth_latency.labels(route=self._route_label(route)).observe(max(_now() - started, 0.0))

    def _route_label(self, route: str) -> str:
        for prefix in ("/admin", "/api/ingestion", "/api/truth", "/api/providers", "/api/console", "/api"):
            if route.startswith(prefix):
                return prefix
        return "other"

    def _audit(
        self,
        request: Request,
        status: int,
        started: float,
        actor: Optional[str],
        role: Optional[str],
        op_id: Optional[str],
        request_id: Optional[str],
        error_type: Optional[str],
    ) -> None:
        try:
            latency_ms = int((max(_now() - started, 0.0)) * 1000)
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "request_id": request_id,
                "op_id": op_id,
                "actor": actor,
                "role": role,
                "route": request.url.path,
                "method": request.method,
                "status": status,
                "latency_ms": latency_ms,
                "payload_hash": None,
                "error_type": error_type,
            }
            AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
            with AUDIT_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:  # pragma: no cover
            logger.warning("Failed to write audit log", exc_info=True)
