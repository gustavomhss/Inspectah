# Sprint 42 — Plano v5.6 ARCHITECTURE PATTERNS

> Refinamento 4 de 5: v5.5 → v5.6
> 20 gaps de arquitetura de codigo

---

## CHANGELOG v5.5 → v5.6

| Area | v5.5 | v5.6 | Delta |
|------|------|------|-------|
| Error Handling | RFC 7807 | Exception Hierarchy | Enhanced |
| DI Container | Ausente | Completo | New |
| Repository Pattern | Ausente | Completo | New |
| Service Layer | Ausente | Completo | New |
| Middleware Stack | Basico | Completo | Enhanced |
| Background Jobs | Mencionado | ARQ config | New |
| Event System | Ausente | Completo | New |
| State Machine | Ausente | Batch/Plan | New |
| Domain Patterns | Ausente | DDD | New |
| Documentation Site | Ausente | MkDocs | New |

---

## PARTE XLIII: EXCEPTION HIERARCHY

### Exception Structure

```python
# app/exceptions/base.py
from dataclasses import dataclass
from typing import Any

@dataclass
class ErrorContext:
    """Contextual information for errors."""
    trace_id: str | None = None
    correlation_id: str | None = None
    user_id: str | None = None
    resource_id: str | None = None
    additional: dict[str, Any] | None = None

class MACException(Exception):
    """Base exception for MAC service."""

    code: str = "MAC-SYS-000"
    status_code: int = 500
    message: str = "Internal server error"
    retryable: bool = False

    def __init__(
        self,
        message: str | None = None,
        context: ErrorContext | None = None,
        cause: Exception | None = None
    ):
        self.message = message or self.__class__.message
        self.context = context or ErrorContext()
        self.cause = cause
        super().__init__(self.message)

    def to_problem_detail(self) -> dict:
        """Convert to RFC 7807 Problem Detail."""
        return {
            "type": f"https://api.inspectah.com/errors/{self.code}",
            "title": self.message,
            "status": self.status_code,
            "code": self.code,
            "retryable": self.retryable,
            "trace_id": self.context.trace_id,
            "detail": str(self.cause) if self.cause else None,
        }

# Simulation Exceptions
class SimulationException(MACException):
    """Base for simulation errors."""
    pass

class AllegationNotFoundError(SimulationException):
    code = "MAC-SIM-001"
    status_code = 404
    message = "Allegation not found"
    retryable = False

class DeterminismViolationError(SimulationException):
    code = "MAC-SIM-002"
    status_code = 500
    message = "Determinism violation detected"
    retryable = True

class PolicyEvaluationError(SimulationException):
    code = "MAC-SIM-003"
    status_code = 500
    message = "Policy evaluation failed"
    retryable = True

class SimulationTimeoutError(SimulationException):
    code = "MAC-SIM-005"
    status_code = 504
    message = "Simulation timeout"
    retryable = True

# Batch Exceptions
class BatchException(MACException):
    """Base for batch errors."""
    pass

class BatchNotFoundError(BatchException):
    code = "MAC-BAT-001"
    status_code = 404
    message = "Batch not found"
    retryable = False

class BatchAlreadyCancelledError(BatchException):
    code = "MAC-BAT-002"
    status_code = 409
    message = "Batch already cancelled"
    retryable = False

class BatchLimitExceededError(BatchException):
    code = "MAC-BAT-003"
    status_code = 429
    message = "Batch limit exceeded"
    retryable = True

# MI Exceptions
class MIException(MACException):
    """Base for MI errors."""
    pass

class InsufficientPermissionsError(MIException):
    code = "MAC-MI-001"
    status_code = 403
    message = "Insufficient permissions"
    retryable = False

class MIDataNotAvailableError(MIException):
    code = "MAC-MI-002"
    status_code = 404
    message = "MI data not available"
    retryable = False

# Auth Exceptions
class AuthException(MACException):
    """Base for auth errors."""
    pass

class TokenExpiredError(AuthException):
    code = "MAC-AUTH-001"
    status_code = 401
    message = "Token expired"
    retryable = False

class InvalidTokenError(AuthException):
    code = "MAC-AUTH-002"
    status_code = 401
    message = "Invalid token"
    retryable = False

# Validation Exceptions
class ValidationException(MACException):
    """Base for validation errors."""
    status_code = 400
    retryable = False

class InvalidPayloadError(ValidationException):
    code = "MAC-VAL-001"
    message = "Invalid JSON payload"

class MissingFieldError(ValidationException):
    code = "MAC-VAL-002"
    message = "Missing required field"

    def __init__(self, field: str, **kwargs):
        super().__init__(f"Missing required field: {field}", **kwargs)
```

### Exception Handler

```python
# app/exceptions/handler.py
from fastapi import Request
from fastapi.responses import JSONResponse

async def mac_exception_handler(request: Request, exc: MACException) -> JSONResponse:
    """Handle MAC exceptions and return RFC 7807 response."""

    # Add request context
    exc.context.trace_id = request.state.trace_id
    exc.context.correlation_id = request.headers.get("X-Correlation-ID")

    # Log error
    logger.error(
        "request_failed",
        error_code=exc.code,
        error_message=exc.message,
        trace_id=exc.context.trace_id,
        cause=str(exc.cause) if exc.cause else None
    )

    # Track metric
    error_counter.labels(code=exc.code, endpoint=request.url.path).inc()

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_detail(),
        media_type="application/problem+json"
    )

# Register handlers
app.add_exception_handler(MACException, mac_exception_handler)
```

---

## PARTE XLIV: DEPENDENCY INJECTION

### DI Container Setup

```python
# app/container.py
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject

class Container(containers.DeclarativeContainer):
    """Application DI container."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.simulation_routes",
            "app.api.batch_routes",
            "app.api.mi_routes",
        ]
    )

    # Configuration
    config = providers.Configuration()

    # Infrastructure
    db_pool = providers.Singleton(
        create_db_pool,
        host=config.database.host,
        port=config.database.port,
        database=config.database.name,
        user=config.database.user,
        password=config.database.password,
        pool_size=config.database.pool_size,
    )

    redis_client = providers.Singleton(
        create_redis_client,
        host=config.redis.host,
        port=config.redis.port,
        password=config.redis.password,
    )

    kafka_producer = providers.Singleton(
        create_kafka_producer,
        bootstrap_servers=config.kafka.bootstrap_servers,
    )

    # Repositories
    simulation_repository = providers.Factory(
        SimulationRepository,
        db_pool=db_pool,
    )

    batch_repository = providers.Factory(
        BatchRepository,
        db_pool=db_pool,
    )

    mi_repository = providers.Factory(
        MIRepository,
        db_pool=db_pool,
    )

    # External Services
    truth_service = providers.Factory(
        TruthServiceClient,
        base_url=config.services.truth.url,
        timeout=config.services.truth.timeout,
    )

    policy_service = providers.Factory(
        PolicyServiceClient,
        base_url=config.services.policy.url,
        timeout=config.services.policy.timeout,
    )

    # Domain Services
    mac_engine = providers.Factory(
        MacEngine,
        truth_service=truth_service,
        policy_service=policy_service,
    )

    determinism_checker = providers.Factory(
        DeterminismChecker,
        simulation_repository=simulation_repository,
    )

    manifest_builder = providers.Factory(
        ManifestBuilder,
    )

    # Application Services
    simulation_service = providers.Factory(
        SimulationService,
        mac_engine=mac_engine,
        determinism_checker=determinism_checker,
        manifest_builder=manifest_builder,
        simulation_repository=simulation_repository,
        cache=redis_client,
    )

    batch_service = providers.Factory(
        BatchService,
        simulation_service=simulation_service,
        batch_repository=batch_repository,
        event_publisher=kafka_producer,
    )

    mi_service = providers.Factory(
        MIService,
        mi_repository=mi_repository,
        rbac_enforcer=providers.Factory(RBACEnforcer),
        redaction_engine=providers.Factory(RedactionEngine),
    )

# Usage in routes
@router.post("/simulate")
@inject
async def simulate(
    request: SimulateRequest,
    simulation_service: SimulationService = Depends(Provide[Container.simulation_service])
):
    return await simulation_service.simulate(request)
```

---

## PARTE XLV: REPOSITORY PATTERN

### Base Repository

```python
# app/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")

class Repository(ABC, Generic[T]):
    """Base repository interface."""

    @abstractmethod
    async def get(self, id: UUID) -> T | None:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        pass

class PaginatedResult(Generic[T]):
    """Paginated result wrapper."""

    def __init__(
        self,
        items: list[T],
        total: int,
        page: int,
        page_size: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.pages = (total + page_size - 1) // page_size

# Simulation Repository
class SimulationRepository(Repository[Simulation]):
    """Repository for simulation persistence."""

    def __init__(self, db_pool: Pool):
        self.db = db_pool

    async def get(self, id: UUID) -> Simulation | None:
        query = """
            SELECT id, allegation_id, seed, temperature, result, manifest, created_at
            FROM mac_simulations
            WHERE id = $1
        """
        row = await self.db.fetchrow(query, id)
        return Simulation.from_row(row) if row else None

    async def get_by_allegation(
        self,
        allegation_id: str,
        temperature: float = 0,
        seed: int | None = None
    ) -> Simulation | None:
        """Get simulation by inputs (for determinism check)."""
        query = """
            SELECT id, allegation_id, seed, temperature, result, manifest, created_at
            FROM mac_simulations
            WHERE allegation_id = $1
              AND temperature = $2
              AND ($3::bigint IS NULL OR seed = $3)
            ORDER BY created_at DESC
            LIMIT 1
        """
        row = await self.db.fetchrow(query, allegation_id, temperature, seed)
        return Simulation.from_row(row) if row else None

    async def save(self, simulation: Simulation) -> Simulation:
        query = """
            INSERT INTO mac_simulations (id, allegation_id, seed, temperature, result, manifest, created_by)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, created_at
        """
        row = await self.db.fetchrow(
            query,
            simulation.id,
            simulation.allegation_id,
            simulation.seed,
            simulation.temperature,
            simulation.result.to_json(),
            simulation.manifest.to_json(),
            simulation.created_by
        )
        simulation.created_at = row["created_at"]
        return simulation

    async def find_by_criteria(
        self,
        criteria: SimulationSearchCriteria,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedResult[Simulation]:
        """Search simulations with criteria."""
        conditions = ["1=1"]
        params = []
        param_idx = 1

        if criteria.allegation_id:
            conditions.append(f"allegation_id = ${param_idx}")
            params.append(criteria.allegation_id)
            param_idx += 1

        if criteria.verdict:
            conditions.append(f"result->>'verdict' = ${param_idx}")
            params.append(criteria.verdict)
            param_idx += 1

        if criteria.from_date:
            conditions.append(f"created_at >= ${param_idx}")
            params.append(criteria.from_date)
            param_idx += 1

        where_clause = " AND ".join(conditions)

        # Count total
        count_query = f"SELECT COUNT(*) FROM mac_simulations WHERE {where_clause}"
        total = await self.db.fetchval(count_query, *params)

        # Fetch page
        query = f"""
            SELECT * FROM mac_simulations
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_idx} OFFSET ${param_idx + 1}
        """
        params.extend([page_size, (page - 1) * page_size])
        rows = await self.db.fetch(query, *params)

        return PaginatedResult(
            items=[Simulation.from_row(r) for r in rows],
            total=total,
            page=page,
            page_size=page_size
        )

    async def delete(self, id: UUID) -> bool:
        query = "DELETE FROM mac_simulations WHERE id = $1"
        result = await self.db.execute(query, id)
        return result == "DELETE 1"
```

---

## PARTE XLVI: SERVICE LAYER

### Service Structure

```python
# app/services/simulation_service.py
from dataclasses import dataclass
from typing import Protocol

class SimulationService:
    """
    Application service for simulation operations.

    Orchestrates domain logic, repositories, and external services.
    """

    def __init__(
        self,
        mac_engine: MacEngine,
        determinism_checker: DeterminismChecker,
        manifest_builder: ManifestBuilder,
        simulation_repository: SimulationRepository,
        cache: Redis,
        event_publisher: EventPublisher,
    ):
        self.mac_engine = mac_engine
        self.determinism_checker = determinism_checker
        self.manifest_builder = manifest_builder
        self.repository = simulation_repository
        self.cache = cache
        self.events = event_publisher

    async def simulate(
        self,
        request: SimulateRequest,
        user: User
    ) -> SimulationResult:
        """
        Execute simulation for an allegation.

        1. Validate inputs
        2. Check cache for deterministic replay
        3. Execute simulation
        4. Verify determinism
        5. Build manifest
        6. Persist and return
        """
        # 1. Validate
        await self._validate_request(request)

        # 2. Check cache (for T=0)
        if request.temperature == 0:
            cached = await self._get_cached_result(request)
            if cached:
                return cached

        # 3. Execute
        with tracer.start_span("simulation.execute"):
            result = await self.mac_engine.evaluate(
                allegation_id=request.allegation_id,
                temperature=request.temperature,
                seed=request.seed
            )

        # 4. Verify determinism
        if request.temperature == 0:
            await self.determinism_checker.verify(
                allegation_id=request.allegation_id,
                result=result
            )

        # 5. Build manifest
        manifest = self.manifest_builder.build(
            inputs=request,
            outputs=result,
            include_lineage=request.options.include_lineage
        )

        # 6. Persist
        simulation = Simulation(
            allegation_id=request.allegation_id,
            seed=request.seed or result.seed,
            temperature=request.temperature,
            result=result,
            manifest=manifest,
            created_by=user.id
        )
        await self.repository.save(simulation)

        # 7. Cache (for T=0)
        if request.temperature == 0:
            await self._cache_result(request, simulation)

        # 8. Publish event
        await self.events.publish(
            SimulationCompletedEvent(
                simulation_id=simulation.id,
                allegation_id=request.allegation_id,
                verdict=result.verdict,
                user_id=user.id
            )
        )

        return SimulationResult(
            id=simulation.id,
            allegation_id=request.allegation_id,
            verdict=result.verdict,
            confidence=result.confidence,
            manifest=manifest if request.options.include_manifest else None,
            created_at=simulation.created_at
        )

    async def _validate_request(self, request: SimulateRequest):
        """Validate simulation request."""
        # Check allegation exists
        truth_state = await self.mac_engine.truth_service.get_state(
            request.allegation_id
        )
        if not truth_state:
            raise AllegationNotFoundError(
                context=ErrorContext(resource_id=request.allegation_id)
            )

    async def _get_cached_result(
        self,
        request: SimulateRequest
    ) -> SimulationResult | None:
        """Get cached simulation result."""
        cache_key = f"sim:{request.allegation_id}:{request.seed or 'default'}"
        cached = await self.cache.get(cache_key)
        if cached:
            return SimulationResult.from_json(cached)
        return None

    async def _cache_result(
        self,
        request: SimulateRequest,
        simulation: Simulation
    ):
        """Cache simulation result."""
        cache_key = f"sim:{request.allegation_id}:{request.seed or 'default'}"
        await self.cache.setex(
            cache_key,
            86400,  # 24h TTL
            simulation.to_result().to_json()
        )
```

### Unit of Work Pattern

```python
# app/services/unit_of_work.py
from contextlib import asynccontextmanager

class UnitOfWork:
    """
    Unit of Work pattern for transaction management.

    Ensures all operations in a business transaction
    succeed or fail together.
    """

    def __init__(self, db_pool: Pool):
        self.db_pool = db_pool
        self._connection: Connection | None = None
        self._transaction: Transaction | None = None

    @asynccontextmanager
    async def transaction(self):
        """Start a transaction context."""
        self._connection = await self.db_pool.acquire()
        self._transaction = self._connection.transaction()
        await self._transaction.start()

        try:
            yield self
            await self._transaction.commit()
        except Exception:
            await self._transaction.rollback()
            raise
        finally:
            await self.db_pool.release(self._connection)
            self._connection = None
            self._transaction = None

    @property
    def simulations(self) -> SimulationRepository:
        return SimulationRepository(self._connection)

    @property
    def batches(self) -> BatchRepository:
        return BatchRepository(self._connection)

# Usage
async def create_batch_with_items(batch_data: BatchData, uow: UnitOfWork):
    async with uow.transaction():
        batch = await uow.batches.save(Batch(**batch_data.batch))
        for item in batch_data.items:
            await uow.batches.add_item(batch.id, item)
        return batch
```

---

## PARTE XLVII: MIDDLEWARE STACK

### Complete Middleware Configuration

```python
# app/middleware/__init__.py
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

def setup_middleware(app: FastAPI):
    """Configure complete middleware stack."""

    # Order matters! First added = outermost (executed first on request, last on response)

    # 1. Request ID (outermost - for correlation)
    app.add_middleware(RequestIDMiddleware)

    # 2. Logging (log all requests)
    app.add_middleware(LoggingMiddleware)

    # 3. Metrics (track all requests)
    app.add_middleware(MetricsMiddleware)

    # 4. Tracing (distributed tracing)
    app.add_middleware(TracingMiddleware)

    # 5. Error handling (catch and format errors)
    app.add_middleware(ErrorHandlingMiddleware)

    # 6. CORS (handle preflight)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 7. Compression (compress responses)
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 8. Rate limiting
    app.add_middleware(RateLimitMiddleware)

    # 9. Authentication
    app.add_middleware(AuthenticationMiddleware)

    # 10. Request validation
    app.add_middleware(RequestValidationMiddleware)

# Request ID Middleware
class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# Logging Middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()

        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            request_id=request.state.request_id
        )

        response = await call_next(request)

        # Log response
        duration = time.monotonic() - start
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration * 1000,
            request_id=request.state.request_id
        )

        return response

# Metrics Middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()

        response = await call_next(request)

        duration = time.monotonic() - start

        REQUEST_LATENCY.labels(
            method=request.method,
            path=request.url.path,
            status=response.status_code
        ).observe(duration)

        REQUEST_COUNT.labels(
            method=request.method,
            path=request.url.path,
            status=response.status_code
        ).inc()

        return response
```

---

## PARTE XLVIII: BACKGROUND JOBS (ARQ)

### Worker Configuration

```python
# app/workers/config.py
from arq import create_pool
from arq.connections import RedisSettings

class WorkerSettings:
    """ARQ worker settings."""

    redis_settings = RedisSettings(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
    )

    # Job functions to register
    functions = [
        process_batch_item,
        send_webhook,
        cleanup_old_batches,
        generate_scorecard,
    ]

    # Cron jobs
    cron_jobs = [
        cron(cleanup_old_batches, hour=3, minute=0),  # Daily at 3 AM
        cron(generate_daily_report, hour=6, minute=0),  # Daily at 6 AM
    ]

    # Worker options
    max_jobs = 10
    job_timeout = 300  # 5 minutes
    max_tries = 3
    retry_jobs = True

# Job definitions
async def process_batch_item(ctx: dict, batch_id: str, item_id: str):
    """Process a single batch item."""
    simulation_service = ctx["simulation_service"]

    item = await ctx["batch_repo"].get_item(item_id)
    if not item:
        return

    try:
        result = await simulation_service.simulate(
            SimulateRequest(allegation_id=item.allegation_id),
            user=ctx["system_user"]
        )
        await ctx["batch_repo"].update_item(
            item_id,
            status="completed",
            simulation_id=result.id
        )
    except Exception as e:
        await ctx["batch_repo"].update_item(
            item_id,
            status="failed",
            error_message=str(e)
        )

async def send_webhook(ctx: dict, webhook_id: str, event: str, payload: dict):
    """Send webhook notification."""
    webhook = await ctx["webhook_repo"].get(webhook_id)
    if not webhook or not webhook.active:
        return

    await ctx["webhook_delivery"].deliver(
        url=webhook.url,
        event=event,
        payload=payload,
        secret=webhook.secret
    )

# Startup
async def startup(ctx: dict):
    """Initialize worker context."""
    ctx["db_pool"] = await create_db_pool()
    ctx["simulation_service"] = SimulationService(...)
    ctx["batch_repo"] = BatchRepository(ctx["db_pool"])
    ctx["webhook_repo"] = WebhookRepository(ctx["db_pool"])

async def shutdown(ctx: dict):
    """Cleanup worker context."""
    await ctx["db_pool"].close()

# Enqueue jobs
async def enqueue_batch_processing(batch_id: str, item_ids: list[str]):
    """Enqueue batch items for processing."""
    redis = await create_pool(WorkerSettings.redis_settings)

    for item_id in item_ids:
        await redis.enqueue_job(
            "process_batch_item",
            batch_id,
            item_id,
            _queue_name="batch_processing"
        )
```

---

## PARTE XLIX: EVENT SYSTEM

### Domain Events

```python
# app/events/domain.py
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class DomainEvent(ABC):
    """Base class for domain events."""

    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1

    @property
    def event_type(self) -> str:
        return self.__class__.__name__

@dataclass
class SimulationCompletedEvent(DomainEvent):
    """Emitted when a simulation completes."""

    simulation_id: UUID
    allegation_id: str
    verdict: str
    confidence: float
    user_id: str

@dataclass
class BatchCreatedEvent(DomainEvent):
    """Emitted when a batch is created."""

    batch_id: UUID
    total_items: int
    created_by: str

@dataclass
class BatchCompletedEvent(DomainEvent):
    """Emitted when a batch completes."""

    batch_id: UUID
    completed_items: int
    failed_items: int
    duration_seconds: float

@dataclass
class MIAccessedEvent(DomainEvent):
    """Emitted when MI is accessed."""

    allegation_id: str
    user_id: str
    role: str
    fields_accessed: list[str]
    fields_redacted: list[str]

# Event Publisher
class EventPublisher:
    """Publishes domain events to Kafka."""

    def __init__(self, producer: KafkaProducer):
        self.producer = producer

    async def publish(self, event: DomainEvent):
        """Publish event to Kafka topic."""
        topic = f"mac.events.{event.event_type.lower()}"

        await self.producer.send(
            topic,
            key=str(event.event_id).encode(),
            value=json.dumps(asdict(event), default=str).encode()
        )

# Event Handlers
class EventHandler(ABC):
    """Base class for event handlers."""

    @abstractmethod
    async def handle(self, event: DomainEvent):
        pass

class SimulationCompletedHandler(EventHandler):
    """Handle simulation completed events."""

    def __init__(self, analytics: AnalyticsClient):
        self.analytics = analytics

    async def handle(self, event: SimulationCompletedEvent):
        # Track analytics
        await self.analytics.track(
            event_name="simulation_completed",
            properties={
                "allegation_id": event.allegation_id,
                "verdict": event.verdict,
                "user_id": event.user_id
            }
        )

# Event Dispatcher
class EventDispatcher:
    """Dispatches events to registered handlers."""

    def __init__(self):
        self._handlers: dict[type, list[EventHandler]] = {}

    def register(self, event_type: type, handler: EventHandler):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event: DomainEvent):
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                await handler.handle(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")
```

---

## PARTE L: STATE MACHINE

### Batch State Machine

```python
# app/domain/state_machines/batch.py
from enum import Enum
from transitions import Machine

class BatchState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class BatchStateMachine:
    """
    State machine for batch lifecycle.

    States: pending -> running -> completed
                   |          |-> cancelled
                   |          |-> failed
                   |-> paused -> running
    """

    states = [s.value for s in BatchState]

    transitions = [
        # Start processing
        {
            "trigger": "start",
            "source": BatchState.PENDING,
            "dest": BatchState.RUNNING,
            "before": "_on_start"
        },
        # Pause processing
        {
            "trigger": "pause",
            "source": BatchState.RUNNING,
            "dest": BatchState.PAUSED,
            "before": "_on_pause"
        },
        # Resume processing
        {
            "trigger": "resume",
            "source": BatchState.PAUSED,
            "dest": BatchState.RUNNING,
            "before": "_on_resume"
        },
        # Complete successfully
        {
            "trigger": "complete",
            "source": BatchState.RUNNING,
            "dest": BatchState.COMPLETED,
            "before": "_on_complete"
        },
        # Cancel
        {
            "trigger": "cancel",
            "source": [BatchState.PENDING, BatchState.RUNNING, BatchState.PAUSED],
            "dest": BatchState.CANCELLED,
            "before": "_on_cancel"
        },
        # Fail
        {
            "trigger": "fail",
            "source": BatchState.RUNNING,
            "dest": BatchState.FAILED,
            "before": "_on_fail"
        },
    ]

    def __init__(self, batch: Batch):
        self.batch = batch
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial=batch.status,
            send_event=True
        )

    def _on_start(self, event):
        self.batch.started_at = datetime.utcnow()
        logger.info(f"Batch {self.batch.id} started")

    def _on_pause(self, event):
        self.batch.paused_at = datetime.utcnow()
        logger.info(f"Batch {self.batch.id} paused")

    def _on_resume(self, event):
        self.batch.resumed_at = datetime.utcnow()
        logger.info(f"Batch {self.batch.id} resumed")

    def _on_complete(self, event):
        self.batch.completed_at = datetime.utcnow()
        logger.info(f"Batch {self.batch.id} completed")

    def _on_cancel(self, event):
        self.batch.cancelled_at = datetime.utcnow()
        self.batch.cancelled_by = event.kwargs.get("user_id")
        logger.info(f"Batch {self.batch.id} cancelled by {self.batch.cancelled_by}")

    def _on_fail(self, event):
        self.batch.failed_at = datetime.utcnow()
        self.batch.error_message = event.kwargs.get("error")
        logger.error(f"Batch {self.batch.id} failed: {self.batch.error_message}")

    @property
    def can_cancel(self) -> bool:
        return self.state in [BatchState.PENDING, BatchState.RUNNING, BatchState.PAUSED]

    @property
    def is_terminal(self) -> bool:
        return self.state in [BatchState.COMPLETED, BatchState.CANCELLED, BatchState.FAILED]
```

---

## PARTE LI: DOMAIN MODEL (DDD)

### Value Objects

```python
# app/domain/value_objects.py
from dataclasses import dataclass
from typing import Self

@dataclass(frozen=True)
class AllegationId:
    """Value object for allegation identifier."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) > 64:
            raise ValueError("Invalid allegation ID")
        if not self.value.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Allegation ID must be alphanumeric")

    def __str__(self) -> str:
        return self.value

@dataclass(frozen=True)
class Verdict:
    """Value object for simulation verdict."""

    MAINTAINS = "VERDICT_MAINTAINS"
    REFUTES = "VERDICT_REFUTES"
    INCONCLUSIVE = "VERDICT_INCONCLUSIVE"

    value: str
    confidence: float

    def __post_init__(self):
        valid = [self.MAINTAINS, self.REFUTES, self.INCONCLUSIVE]
        if self.value not in valid:
            raise ValueError(f"Invalid verdict: {self.value}")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")

    @property
    def is_conclusive(self) -> bool:
        return self.value != self.INCONCLUSIVE and self.confidence > 0.8

@dataclass(frozen=True)
class Temperature:
    """Value object for simulation temperature."""

    value: float

    def __post_init__(self):
        if not 0 <= self.value <= 1:
            raise ValueError("Temperature must be between 0 and 1")

    @property
    def is_deterministic(self) -> bool:
        return self.value == 0

@dataclass(frozen=True)
class Role:
    """Value object for user role."""

    OPS = "ops"
    REVIEWER = "reviewer"
    COUNCIL = "council"

    value: str

    def __post_init__(self):
        valid = [self.OPS, self.REVIEWER, self.COUNCIL]
        if self.value not in valid:
            raise ValueError(f"Invalid role: {self.value}")

    def can_access_level(self, level: str) -> bool:
        hierarchy = {self.OPS: 1, self.REVIEWER: 2, self.COUNCIL: 3}
        required = {self.OPS: 1, self.REVIEWER: 2, self.COUNCIL: 3}
        return hierarchy[self.value] >= required.get(level, 3)
```

### Aggregate Root

```python
# app/domain/aggregates/batch.py
from dataclasses import dataclass, field
from uuid import UUID, uuid4

@dataclass
class BatchItem:
    """Entity within Batch aggregate."""

    id: UUID
    allegation_id: AllegationId
    status: str = "pending"
    simulation_id: UUID | None = None
    error_message: str | None = None

@dataclass
class Batch:
    """
    Batch aggregate root.

    Encapsulates batch processing logic and maintains invariants.
    """

    id: UUID = field(default_factory=uuid4)
    items: list[BatchItem] = field(default_factory=list)
    status: str = "pending"
    created_by: str = ""
    created_at: datetime | None = None

    # Invariant: max 1000 items
    MAX_ITEMS = 1000

    def add_item(self, allegation_id: AllegationId) -> BatchItem:
        """Add item to batch."""
        if len(self.items) >= self.MAX_ITEMS:
            raise BatchLimitExceededError(
                f"Batch cannot exceed {self.MAX_ITEMS} items"
            )

        item = BatchItem(
            id=uuid4(),
            allegation_id=allegation_id
        )
        self.items.append(item)
        return item

    def mark_item_completed(self, item_id: UUID, simulation_id: UUID):
        """Mark item as completed."""
        item = self._get_item(item_id)
        item.status = "completed"
        item.simulation_id = simulation_id
        self._check_completion()

    def mark_item_failed(self, item_id: UUID, error: str):
        """Mark item as failed."""
        item = self._get_item(item_id)
        item.status = "failed"
        item.error_message = error
        self._check_completion()

    def _get_item(self, item_id: UUID) -> BatchItem:
        for item in self.items:
            if item.id == item_id:
                return item
        raise ValueError(f"Item {item_id} not found")

    def _check_completion(self):
        """Check if all items are processed."""
        pending = sum(1 for i in self.items if i.status == "pending")
        if pending == 0 and self.status == "running":
            self.status = "completed"

    @property
    def progress(self) -> float:
        if not self.items:
            return 0
        completed = sum(1 for i in self.items if i.status in ["completed", "failed"])
        return completed / len(self.items)

    @property
    def scorecard(self) -> dict:
        """Generate scorecard for completed batch."""
        return {
            "total": len(self.items),
            "completed": sum(1 for i in self.items if i.status == "completed"),
            "failed": sum(1 for i in self.items if i.status == "failed"),
            "pending": sum(1 for i in self.items if i.status == "pending"),
        }
```

---

## PARTE LII: DOCUMENTATION SITE

### MkDocs Configuration

```yaml
# mkdocs.yml
site_name: MAC Service Documentation
site_url: https://docs.inspectah.com/mac
repo_url: https://github.com/inspectah/mac-service
repo_name: inspectah/mac-service

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
    - Configuration: getting-started/configuration.md
  - API Reference:
    - Overview: api/overview.md
    - Simulation: api/simulation.md
    - Batch: api/batch.md
    - MI Exposure: api/mi.md
    - Adiabatic: api/adiabatic.md
  - Architecture:
    - Overview: architecture/overview.md
    - Domain Model: architecture/domain.md
    - Event System: architecture/events.md
    - State Machines: architecture/state-machines.md
  - Operations:
    - Deployment: operations/deployment.md
    - Monitoring: operations/monitoring.md
    - Runbooks: operations/runbooks.md
  - Development:
    - Setup: development/setup.md
    - Testing: development/testing.md
    - Contributing: development/contributing.md

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - admonition
  - pymdownx.details
  - pymdownx.tabbed:
      alternate_style: true
  - attr_list
  - md_in_html
```

### Documentation Structure

```
docs/
├── index.md                    # Home page
├── getting-started/
│   ├── installation.md        # Installation guide
│   ├── quickstart.md          # Quick start guide
│   └── configuration.md       # Configuration reference
├── api/
│   ├── overview.md            # API overview
│   ├── simulation.md          # Simulation API
│   ├── batch.md               # Batch API
│   ├── mi.md                  # MI API
│   └── adiabatic.md           # Adiabatic API
├── architecture/
│   ├── overview.md            # Architecture overview
│   ├── domain.md              # Domain model
│   ├── events.md              # Event system
│   └── state-machines.md      # State machines
├── operations/
│   ├── deployment.md          # Deployment guide
│   ├── monitoring.md          # Monitoring guide
│   └── runbooks.md            # Operational runbooks
└── development/
    ├── setup.md               # Development setup
    ├── testing.md             # Testing guide
    └── contributing.md        # Contributing guide
```

---

## ASSINATURA v5.6

```
Sprint: S42
Versao: 5.6 ARCHITECTURE PATTERNS
Status: CODE READY

Novidades v5.6:
  Exception Hierarchy: 20+ exceptions
  DI Container: dependency-injector
  Repository Pattern: Base + Implementations
  Service Layer: Application services
  Middleware Stack: 10 middlewares
  Background Jobs: ARQ config
  Event System: Domain events + handlers
  State Machine: Batch lifecycle
  Domain Patterns: Value Objects, Aggregates
  Documentation Site: MkDocs Material

Acumulado:
  Gaps corrigidos v5.2→v5.3: 20
  Gaps corrigidos v5.3→v5.4: 20
  Gaps corrigidos v5.4→v5.5: 20
  Gaps corrigidos v5.5→v5.6: 20
  Total gaps corrigidos: 80

Refinamento: 4 de 5
```

*Plano v5.6 ARCHITECTURE PATTERNS*
*v5.5 + 20 refinamentos*
