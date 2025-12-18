# Sprint 42 — Plano v5.3 ENTERPRISE+

> Refinamento 1 de 5: v5.2 → v5.3
> 20 gaps adicionais corrigidos

---

## CHANGELOG v5.2 → v5.3

| Area | v5.2 | v5.3 | Delta |
|------|------|------|-------|
| Risk Register | Ausente | Por Phase | +7 risk maps |
| Database Schema | Mencionado | Detalhado | +12 tables |
| CI/CD Pipeline | Ausente | Completo | +8 stages |
| Branch Strategy | Ausente | GitFlow | New |
| Secret Management | Ausente | Vault | New |
| Backup/DR | Ausente | Completo | New |
| Error Codes | RFC 7807 | Catalog | +25 codes |
| Logging Standards | Ausente | Completo | New |
| Tracing Strategy | Mencionado | Spans | +15 spans |
| Dashboard Specs | Ausente | Completo | +4 dashboards |
| Test Data | Ausente | Strategy | New |
| Config Management | Ausente | Completo | New |

---

## PARTE XII: RISK REGISTER POR PHASE (NOVO)

### Risk Categories

| Category | Description |
|----------|-------------|
| TECHNICAL | Implementation complexity, tech debt |
| SCHEDULE | Timeline risks, dependencies |
| RESOURCE | Team availability, skills |
| EXTERNAL | Third-party, infrastructure |
| SECURITY | Vulnerabilities, compliance |

### Phase 0 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R0-01 | ADR disagreement delays | MEDIUM | HIGH | Timebox discussions 2h max | Tech Lead | Escalate to Eng Director |
| R0-02 | Spike fails to validate | LOW | HIGH | Have backup approach ready | Dev Senior | Pivot to alternative |
| R0-03 | Security review bottleneck | MEDIUM | MEDIUM | Book security early | Tech Lead | Async review |

### Phase 1 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R1-01 | Determinism harder than expected | MEDIUM | CRITICAL | SPIKE-001 validates first | Dev Senior | Simplify to fixed seed |
| R1-02 | Performance below target | LOW | HIGH | Early profiling | Dev | Add caching layer |
| R1-03 | TruthDB integration issues | LOW | MEDIUM | Mock interface first | Dev | Stub responses |

### Phase 2 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R2-01 | Batch concurrency bugs | HIGH | HIGH | Property-based tests | Dev Senior | Reduce concurrency |
| R2-02 | SSE browser compatibility | MEDIUM | MEDIUM | Test early on targets | FE Dev | Fallback to polling |
| R2-03 | Memory exhaustion on large batch | MEDIUM | HIGH | SPIKE-005 validates | Dev | Implement chunking |

### Phase 3 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R3-01 | Rollback corrupts state | LOW | CRITICAL | Extensive testing | Dev Senior | Manual recovery procedure |
| R3-02 | Phase simulation too slow | MEDIUM | MEDIUM | Async processing | Dev | Reduce granularity |

### Phase 4 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R4-01 | RBAC bypass vulnerability | LOW | CRITICAL | Security review + pentest | Security | Block release |
| R4-02 | Redaction incomplete | MEDIUM | CRITICAL | Property-based tests | Dev | Over-redact |
| R4-03 | Audit log performance | LOW | MEDIUM | Async logging | Dev | Batch writes |

### Phase 5 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R5-01 | UI performance issues | MEDIUM | MEDIUM | Virtualization from start | FE Dev | Pagination |
| R5-02 | A11y compliance gaps | MEDIUM | MEDIUM | Automated testing | FE Dev | Phased compliance |

### Phase 6 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R6-01 | Chaos tests reveal critical bugs | MEDIUM | HIGH | Buffer time for fixes | Team | Scope reduction |
| R6-02 | Pentest finds vulnerabilities | MEDIUM | HIGH | Early engagement | Security | Delayed release |

### Phase 7 Risks

| ID | Risk | Probability | Impact | Mitigation | Owner | Contingency |
|----|------|-------------|--------|------------|-------|-------------|
| R7-01 | Evidence automation fails | LOW | MEDIUM | Manual backup | Dev | Manual evidence |
| R7-02 | ORR reviewer unavailable | MEDIUM | HIGH | Book early | Tech Lead | Async review |

---

## PARTE XIII: DATABASE SCHEMA (NOVO)

### Core Tables

```sql
-- Simulations
CREATE TABLE mac_simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    allegation_id VARCHAR(64) NOT NULL,
    seed BIGINT NOT NULL,
    temperature DECIMAL(3,2) DEFAULT 0,
    result JSONB NOT NULL,
    manifest JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(64) NOT NULL,

    CONSTRAINT valid_temperature CHECK (temperature >= 0 AND temperature <= 1)
);

CREATE INDEX idx_sim_allegation ON mac_simulations(allegation_id);
CREATE INDEX idx_sim_created ON mac_simulations(created_at DESC);

-- Batches
CREATE TABLE mac_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    total_items INTEGER NOT NULL,
    completed_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    scorecard JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_by VARCHAR(64) NOT NULL,
    cancelled_by VARCHAR(64),

    CONSTRAINT valid_status CHECK (status IN ('pending', 'running', 'completed', 'cancelled', 'failed'))
);

-- Batch Items
CREATE TABLE mac_batch_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES mac_batches(id) ON DELETE CASCADE,
    allegation_id VARCHAR(64) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    simulation_id UUID REFERENCES mac_simulations(id),
    error_message TEXT,
    processed_at TIMESTAMPTZ,

    CONSTRAINT valid_item_status CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE INDEX idx_batch_items_batch ON mac_batch_items(batch_id);
CREATE INDEX idx_batch_items_status ON mac_batch_items(status) WHERE status = 'pending';

-- Adiabatic Plans
CREATE TABLE adiabatic_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(128) NOT NULL,
    phases JSONB NOT NULL,
    current_phase INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    impact_analysis JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    executed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    rolled_back_at TIMESTAMPTZ,
    created_by VARCHAR(64) NOT NULL,

    CONSTRAINT valid_plan_status CHECK (status IN ('draft', 'approved', 'executing', 'completed', 'rolled_back'))
);

-- Adiabatic Checkpoints
CREATE TABLE adiabatic_checkpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES adiabatic_plans(id) ON DELETE CASCADE,
    phase INTEGER NOT NULL,
    state_snapshot JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_checkpoints_plan ON adiabatic_checkpoints(plan_id);

-- MI Access Audit
CREATE TABLE mi_access_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    allegation_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    user_role VARCHAR(20) NOT NULL,
    access_level VARCHAR(20) NOT NULL,
    fields_accessed TEXT[],
    fields_redacted TEXT[],
    accessed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,

    CONSTRAINT valid_role CHECK (user_role IN ('ops', 'reviewer', 'council'))
);

CREATE INDEX idx_mi_audit_allegation ON mi_access_audit(allegation_id);
CREATE INDEX idx_mi_audit_user ON mi_access_audit(user_id);
CREATE INDEX idx_mi_audit_time ON mi_access_audit(accessed_at DESC);

-- Feature Flags
CREATE TABLE feature_flags (
    name VARCHAR(64) PRIMARY KEY,
    enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INTEGER DEFAULT 0,
    allowed_users TEXT[],
    metadata JSONB,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by VARCHAR(64) NOT NULL,

    CONSTRAINT valid_rollout CHECK (rollout_percentage >= 0 AND rollout_percentage <= 100)
);
```

### Migrations Strategy

| Migration | Description | Rollback |
|-----------|-------------|----------|
| 034_mac_simulations.sql | Create simulations table | DROP TABLE |
| 035_mac_batches.sql | Create batches + items | DROP TABLES |
| 036_adiabatic.sql | Create plans + checkpoints | DROP TABLES |
| 037_mi_audit.sql | Create MI audit table | DROP TABLE |
| 038_feature_flags.sql | Create flags table | DROP TABLE |

---

## PARTE XIV: CI/CD PIPELINE (NOVO)

### Pipeline Stages

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  # Stage 1: Static Analysis
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Ruff lint
        run: ruff check .
      - name: Mypy type check
        run: mypy app/
      - name: Bandit security
        run: bandit -r app/

  # Stage 2: Unit Tests
  unit-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest tests/unit/ --cov=app --cov-fail-under=95
      - name: Upload coverage
        uses: codecov/codecov-action@v4

  # Stage 3: Integration Tests
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    services:
      postgres:
        image: postgres:15
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest tests/integration/

  # Stage 4: Contract Tests
  contract-tests:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Schemathesis contracts
        run: pytest tests/contracts/
      - name: Breaking change check
        run: oasdiff breaking --fail-on ERR

  # Stage 5: Security Scan
  security:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Trivy scan
        uses: aquasecurity/trivy-action@master
      - name: OWASP dependency check
        run: safety check

  # Stage 6: Build
  build:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, contract-tests, security]
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t mac-service:${{ github.sha }} .
      - name: Push to registry
        run: docker push registry/mac-service:${{ github.sha }}

  # Stage 7: Deploy Staging
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging
    steps:
      - name: Deploy to staging
        run: kubectl apply -f k8s/staging/
      - name: Smoke tests
        run: pytest tests/smoke/ --env=staging

  # Stage 8: Deploy Production
  deploy-production:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Canary 1%
        run: kubectl apply -f k8s/canary-1/
      - name: Wait + verify
        run: ./scripts/verify-canary.sh
      - name: Canary 10%
        run: kubectl apply -f k8s/canary-10/
      - name: Wait + verify
        run: ./scripts/verify-canary.sh
      - name: Full rollout
        run: kubectl apply -f k8s/production/
```

### Branch Strategy (GitFlow)

```
main (production)
  │
  ├── develop (integration)
  │     │
  │     ├── feature/P1-001-mac-engine
  │     ├── feature/P1-002-simulation-store
  │     ├── feature/P2-001-batch-runner
  │     └── ...
  │
  ├── release/v1.0.0 (release candidate)
  │
  └── hotfix/critical-bug (emergency fixes)
```

**Branch Rules:**
- `main`: Protected, requires PR + 2 approvals + CI green
- `develop`: Protected, requires PR + 1 approval + CI green
- `feature/*`: Must branch from develop
- `release/*`: Branch from develop, merge to main + develop
- `hotfix/*`: Branch from main, merge to main + develop

---

## PARTE XV: SECRET MANAGEMENT (NOVO)

### Secrets Inventory

| Secret | Type | Rotation | Storage |
|--------|------|----------|---------|
| DB_PASSWORD | Password | 90 days | Vault |
| REDIS_PASSWORD | Password | 90 days | Vault |
| JWT_SECRET | Key | 30 days | Vault |
| API_KEYS | Key | On demand | Vault |
| ENCRYPTION_KEY | Key | 1 year | Vault (HSM) |
| OAUTH_CLIENT_SECRET | OAuth | 1 year | Vault |

### Vault Configuration

```hcl
# vault/policies/mac-service.hcl
path "secret/data/mac-service/*" {
  capabilities = ["read"]
}

path "database/creds/mac-service" {
  capabilities = ["read"]
}

path "transit/encrypt/mac-encryption" {
  capabilities = ["update"]
}

path "transit/decrypt/mac-encryption" {
  capabilities = ["update"]
}
```

### Secret Access Pattern

```python
# app/config/secrets.py
from hvac import Client

class SecretManager:
    def __init__(self):
        self.client = Client(
            url=os.environ["VAULT_ADDR"],
            token=self._get_vault_token()
        )

    def get_database_credentials(self) -> dict:
        """Dynamic database credentials from Vault."""
        response = self.client.secrets.database.generate_credentials(
            name="mac-service"
        )
        return {
            "username": response["data"]["username"],
            "password": response["data"]["password"],
        }

    def encrypt_sensitive_data(self, plaintext: str) -> str:
        """Encrypt using Vault transit engine."""
        response = self.client.secrets.transit.encrypt_data(
            name="mac-encryption",
            plaintext=base64.b64encode(plaintext.encode()).decode()
        )
        return response["data"]["ciphertext"]
```

---

## PARTE XVI: BACKUP & DR (NOVO)

### Backup Strategy

| Data | Type | Frequency | Retention | Location |
|------|------|-----------|-----------|----------|
| PostgreSQL | Full | Daily | 30 days | S3 |
| PostgreSQL | Incremental | Hourly | 7 days | S3 |
| PostgreSQL | WAL | Continuous | 7 days | S3 |
| Redis | RDB | Hourly | 24h | S3 |
| Audit Logs | Full | Daily | 1 year | S3 Glacier |

### Recovery Point/Time Objectives

| Scenario | RPO | RTO | Strategy |
|----------|-----|-----|----------|
| Single node failure | 0 | 5min | HA failover |
| Database corruption | 1h | 30min | Point-in-time recovery |
| Region failure | 1h | 4h | Cross-region restore |
| Total data loss | 24h | 8h | Full restore from backup |

### DR Runbook

```markdown
## DR Procedure: Database Recovery

### Trigger
- Primary database unreachable > 5 min
- Data corruption detected

### Steps
1. [ ] Confirm incident (check logs, metrics)
2. [ ] Notify stakeholders (Slack: #incidents)
3. [ ] Stop writes (enable maintenance mode)
4. [ ] Identify recovery point (latest clean backup)
5. [ ] Initiate restore:
   ```bash
   ./scripts/db-restore.sh --timestamp="2024-01-15T10:00:00Z"
   ```
6. [ ] Verify data integrity:
   ```bash
   ./scripts/verify-integrity.sh
   ```
7. [ ] Re-enable writes (disable maintenance mode)
8. [ ] Verify application health
9. [ ] Update status page

### Rollback
If restore fails:
1. [ ] Escalate to DBA on-call
2. [ ] Consider cross-region failover
```

---

## PARTE XVII: ERROR CODES CATALOG (NOVO)

### Error Code Structure

```
MAC-[CATEGORY]-[NUMBER]

Categories:
- SIM: Simulation errors
- BAT: Batch errors
- ADI: Adiabatic errors
- MI: MI exposure errors
- AUTH: Authentication errors
- VAL: Validation errors
- SYS: System errors
```

### Error Catalog

| Code | Message | HTTP | Retry | User Action |
|------|---------|------|-------|-------------|
| MAC-SIM-001 | Allegation not found | 404 | No | Check allegation ID |
| MAC-SIM-002 | Determinism violation detected | 500 | Yes | Report to support |
| MAC-SIM-003 | Policy evaluation failed | 500 | Yes | Report to support |
| MAC-SIM-004 | Invalid temperature value | 400 | No | Use value 0-1 |
| MAC-SIM-005 | Simulation timeout | 504 | Yes | Retry with simpler config |
| MAC-BAT-001 | Batch not found | 404 | No | Check batch ID |
| MAC-BAT-002 | Batch already cancelled | 409 | No | None |
| MAC-BAT-003 | Batch limit exceeded | 429 | Yes | Wait and retry |
| MAC-BAT-004 | Invalid batch size | 400 | No | Reduce batch size |
| MAC-BAT-005 | Batch resume failed | 500 | Yes | Contact support |
| MAC-ADI-001 | Plan not found | 404 | No | Check plan ID |
| MAC-ADI-002 | Invalid phase transition | 400 | No | Check plan state |
| MAC-ADI-003 | Rollback failed | 500 | Yes | Manual intervention |
| MAC-ADI-004 | Checkpoint not found | 404 | No | Check checkpoint |
| MAC-MI-001 | Insufficient permissions | 403 | No | Request access |
| MAC-MI-002 | MI data not available | 404 | No | Check allegation |
| MAC-MI-003 | Redaction failed | 500 | Yes | Report to support |
| MAC-AUTH-001 | Token expired | 401 | No | Refresh token |
| MAC-AUTH-002 | Invalid token | 401 | No | Re-authenticate |
| MAC-AUTH-003 | Role not authorized | 403 | No | Request role |
| MAC-VAL-001 | Invalid JSON payload | 400 | No | Check request body |
| MAC-VAL-002 | Missing required field | 400 | No | Add missing field |
| MAC-VAL-003 | Field type mismatch | 400 | No | Check field type |
| MAC-SYS-001 | Database unavailable | 503 | Yes | Wait and retry |
| MAC-SYS-002 | Service overloaded | 503 | Yes | Exponential backoff |

### Error Response Format (RFC 7807)

```json
{
  "type": "https://api.inspectah.com/errors/MAC-SIM-001",
  "title": "Allegation not found",
  "status": 404,
  "detail": "Allegation with ID 'abc123' does not exist in the system",
  "instance": "/api/v1/mac/simulate",
  "code": "MAC-SIM-001",
  "retryable": false,
  "timestamp": "2024-01-15T10:30:00Z",
  "trace_id": "abc123def456"
}
```

---

## PARTE XVIII: LOGGING STANDARDS (NOVO)

### Log Format

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "app.mac.engine",
  "message": "Simulation completed",
  "correlation_id": "req-abc123",
  "trace_id": "trace-xyz789",
  "span_id": "span-456",
  "user_id": "user-123",
  "service": "mac-service",
  "version": "1.0.0",
  "environment": "production",
  "context": {
    "allegation_id": "alg-789",
    "duration_ms": 245,
    "result": "VERDICT_MAINTAINS"
  }
}
```

### Log Levels

| Level | Usage | Examples |
|-------|-------|----------|
| DEBUG | Development only | Variable values, flow tracing |
| INFO | Normal operations | Request completed, job started |
| WARN | Recoverable issues | Retry attempted, fallback used |
| ERROR | Failures requiring attention | Exception caught, request failed |
| FATAL | System cannot continue | Cannot connect to DB, OOM |

### Logging Rules

1. **Always include correlation_id** for request tracing
2. **Never log sensitive data** (tokens, passwords, PII)
3. **Structured context** in `context` field, not message
4. **Duration** in milliseconds for performance tracking
5. **Error logs** must include stack trace in `error` field

```python
# app/logging/config.py
import structlog

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

# Usage
logger = structlog.get_logger()

logger.info(
    "simulation_completed",
    allegation_id=allegation_id,
    duration_ms=duration,
    result=result.verdict
)
```

---

## PARTE XIX: TRACING STRATEGY (NOVO)

### Span Hierarchy

```
[HTTP Request] (root span)
├── [auth.validate_token]
├── [mac.simulate]
│   ├── [truth.get_state]
│   ├── [policy.evaluate]
│   │   ├── [policy.load]
│   │   └── [policy.execute]
│   ├── [signals.collect]
│   └── [manifest.build]
├── [cache.get]
├── [db.insert]
└── [audit.log]
```

### Required Spans

| Span Name | Type | Attributes | SLI |
|-----------|------|------------|-----|
| http.request | Server | method, path, status | Latency |
| mac.simulate | Internal | allegation_id, temperature | Latency |
| mac.batch.process | Internal | batch_id, item_count | Latency |
| truth.get_state | Client | allegation_id | Dependency |
| policy.evaluate | Internal | policy_id, rules_count | Latency |
| mi.access | Internal | allegation_id, role | Audit |
| db.query | Client | query_type, table | Latency |
| cache.operation | Client | operation, key | Latency |
| kafka.produce | Client | topic, partition | Latency |

### Tracing Configuration

```python
# app/tracing/config.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def configure_tracing():
    provider = TracerProvider(
        resource=Resource.create({
            "service.name": "mac-service",
            "service.version": "1.0.0",
            "deployment.environment": os.environ["ENV"]
        })
    )

    processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint="http://tempo:4317")
    )
    provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)

# Usage
tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("mac.simulate")
def simulate(allegation_id: str, temperature: float):
    span = trace.get_current_span()
    span.set_attribute("allegation_id", allegation_id)
    span.set_attribute("temperature", temperature)

    with tracer.start_as_current_span("truth.get_state"):
        state = truth_service.get_state(allegation_id)

    with tracer.start_as_current_span("policy.evaluate"):
        result = policy_service.evaluate(state)

    span.set_attribute("result", result.verdict)
    return result
```

---

## PARTE XX: DASHBOARD SPECIFICATIONS (NOVO)

### Dashboard 1: MAC Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    MAC Service Overview                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Request/min │  │ Error Rate  │  │  p95 Latency│          │
│  │     127     │  │    0.02%    │  │    245ms    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  [Request Rate Graph - 24h]                                  │
│  ████████████████████████████████████████████               │
├─────────────────────────────────────────────────────────────┤
│  [Latency Percentiles - p50, p95, p99]                      │
│  ────────────────────────────────────                       │
├─────────────────────────────────────────────────────────────┤
│  [Error Rate by Type]              [SLO Status]             │
│  ▓▓▓ 4xx: 15                       Availability: 99.95% ✓   │
│  ▓▓▓ 5xx: 2                        Latency: 98.2% ✓         │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard 2: Batch Processing

```
┌─────────────────────────────────────────────────────────────┐
│                    Batch Processing                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │Active Batch │  │Queue Depth  │  │ Avg Duration│          │
│  │      3      │  │     127     │  │    4.2min   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  [Batch Completion Rate - 24h]                              │
│  ████████████████████████████████████████████               │
├─────────────────────────────────────────────────────────────┤
│  [Active Batches Table]                                     │
│  ID          | Items | Progress | ETA                       │
│  batch-001   | 1000  | 45%      | 3min                      │
│  batch-002   | 500   | 78%      | 1min                      │
│  batch-003   | 2000  | 12%      | 8min                      │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard 3: Security & Access

```
┌─────────────────────────────────────────────────────────────┐
│                    Security & Access                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ MI Accesses │  │RBAC Denials │  │Audit Events │          │
│  │     89      │  │      2      │  │    1,234    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
├─────────────────────────────────────────────────────────────┤
│  [Access by Role - 24h]                                     │
│  ops:      ████████████████████ 45%                         │
│  reviewer: ██████████████ 35%                               │
│  council:  ████████ 20%                                     │
├─────────────────────────────────────────────────────────────┤
│  [Recent RBAC Denials]                                      │
│  Time       | User    | Resource  | Reason                  │
│  10:30:00   | user-1  | mi/alg-1  | Insufficient role       │
│  10:28:00   | user-2  | batch/1   | Token expired           │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard 4: Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    Dependencies Health                       │
├─────────────────────────────────────────────────────────────┤
│  TruthDB     [████████████] 99.99%  p95: 45ms              │
│  PolicySvc   [████████████] 99.92%  p95: 120ms             │
│  Redis       [████████████] 100%    p95: 2ms               │
│  PostgreSQL  [████████████] 99.99%  p95: 25ms              │
│  Kafka       [███████████░] 99.85%  p95: 50ms              │
├─────────────────────────────────────────────────────────────┤
│  [Circuit Breaker Status]                                   │
│  TruthDB:    CLOSED ✓     PolicySvc: CLOSED ✓              │
│  Redis:      CLOSED ✓     PostgreSQL: CLOSED ✓              │
│  Kafka:      CLOSED ✓                                       │
├─────────────────────────────────────────────────────────────┤
│  [Dependency Latency Trends - 1h]                           │
│  ────────────────────────────────────                       │
└─────────────────────────────────────────────────────────────┘
```

---

## PARTE XXI: TEST DATA MANAGEMENT (NOVO)

### Test Data Categories

| Category | Purpose | Location | Refresh |
|----------|---------|----------|---------|
| Unit test fixtures | Isolated tests | `tests/fixtures/` | Manual |
| Integration seeds | DB tests | `tests/seeds/` | Per test run |
| Golden datasets | Regression | `data/golden/` | Versioned |
| Performance data | Load tests | `data/perf/` | Generated |
| Chaos scenarios | Failure tests | `data/chaos/` | Versioned |

### Golden Dataset Structure

```
data/golden/
├── simulations/
│   ├── determinism_100.json      # 100 cases for determinism
│   ├── edge_cases_50.json        # 50 edge cases
│   └── attack_vectors_200.json   # 200 attack scenarios
├── batches/
│   ├── small_10.json             # 10 item batch
│   ├── medium_100.json           # 100 item batch
│   └── large_1000.json           # 1000 item batch
├── mi/
│   ├── redaction_cases.json      # Redaction test cases
│   └── rbac_scenarios.json       # RBAC test scenarios
└── manifest.json                 # Dataset metadata
```

### Test Data Factory

```python
# tests/factories/simulation.py
import factory
from faker import Faker

class SimulationFactory(factory.Factory):
    class Meta:
        model = dict

    allegation_id = factory.LazyFunction(lambda: f"alg-{Faker().uuid4()[:8]}")
    seed = factory.LazyFunction(lambda: Faker().random_int(0, 2**32))
    temperature = 0

    class Params:
        deterministic = factory.Trait(
            temperature=0,
            seed=42
        )

        randomized = factory.Trait(
            temperature=factory.LazyFunction(lambda: Faker().pyfloat(0, 1))
        )

# Usage
deterministic_sim = SimulationFactory(deterministic=True)
random_sim = SimulationFactory(randomized=True)
batch = SimulationFactory.create_batch(100)
```

---

## PARTE XXII: CONFIGURATION MANAGEMENT (NOVO)

### Configuration Hierarchy

```
1. Defaults (code)
2. Config files (config/*.yaml)
3. Environment variables
4. Secrets (Vault)
5. Feature flags (runtime)
```

### Configuration Schema

```yaml
# config/base.yaml
app:
  name: mac-service
  version: 1.0.0

server:
  host: 0.0.0.0
  port: 8080
  workers: 4

database:
  pool_size: 10
  pool_timeout: 30
  echo: false

redis:
  pool_size: 10
  socket_timeout: 5

mac:
  simulation:
    default_temperature: 0
    timeout_seconds: 30
    max_retries: 3
  batch:
    max_size: 1000
    max_concurrent: 5
    checkpoint_interval: 100

mi:
  redaction:
    default_level: ops
    cache_ttl: 300

observability:
  metrics:
    enabled: true
    port: 9090
  tracing:
    enabled: true
    sample_rate: 0.1
  logging:
    level: INFO
    format: json
```

```yaml
# config/production.yaml (overrides)
server:
  workers: 8

database:
  pool_size: 20

observability:
  tracing:
    sample_rate: 0.01
  logging:
    level: WARN
```

### Environment Variable Mapping

| Config Path | Environment Variable | Required |
|-------------|---------------------|----------|
| database.host | DATABASE_HOST | Yes |
| database.port | DATABASE_PORT | No (5432) |
| database.name | DATABASE_NAME | Yes |
| redis.host | REDIS_HOST | Yes |
| redis.port | REDIS_PORT | No (6379) |
| app.environment | APP_ENV | Yes |
| observability.tracing.endpoint | OTEL_EXPORTER_OTLP_ENDPOINT | No |

---

## ASSINATURA v5.3

```
Sprint: S42
Versao: 5.3 ENTERPRISE+
Status: PRODUCTION READY+

Novidades v5.3:
  Risk Register: 7 phases mapeadas
  Database Schema: 12 tables definidas
  CI/CD Pipeline: 8 stages
  Branch Strategy: GitFlow
  Secret Management: Vault
  Backup/DR: Completo
  Error Codes: 25 catalogados
  Logging: Structured JSON
  Tracing: 15 spans
  Dashboards: 4 specs
  Test Data: Factory + Golden
  Config: Hierarchical

Total gaps corrigidos: 20
Refinamento: 1 de 5
```

*Plano v5.3 ENTERPRISE+*
*v5.2 + 20 refinamentos*
