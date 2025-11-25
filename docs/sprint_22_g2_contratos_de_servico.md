# Sprint 22 — G2 Contratos de Serviços de Ingestão

## 1. Objetivo
Formalizar operações expostas para operar a ingestão 2.0 (serviços internos + HTTP admin). Cada operação aplica invariantes de G1 e usa a FSM de G3. Todos os endpoints são autenticados como admin e retornam JSON estruturado.

## 2. Operações principais

### 2.1. Acionar ingestão manual
- **Endpoint**: `POST /admin/ingestion/{source_id}/run`
- **Payload**: `{ "trigger_origin": "admin_ui", "force": false }`
- **Comportamento**: cria `IngestionRun` com `trigger=MANUAL` e status `PENDING`, dispara transição para `RUNNING`, registra `started_at`.
- **Respostas**:
  - 201: `{ "run_id": "...", "status": "RUNNING" }`
  - 400: config desabilitada ou `force=false` com run em andamento.
  - 404: fonte inexistente ou sem config.

### 2.2. Alternar modo/manual/automático
- **Endpoint**: `POST /admin/ingestion/{source_id}/toggle-mode`
- **Payload**: `{ "mode": "MANUAL_ONLY" | "AUTOMATIC", "enabled": true|false }`
- **Comportamento**: aplica INV-2 e INV-12; atualiza config com audit trail.
- **Respostas**:
  - 200: config atualizada com timestamps.
  - 400: modo AUTOMATIC em fonte inválida ou parâmetros fora de domínio.
  - 404: fonte/config não encontrada.

### 2.3. Listar runs de uma fonte
- **Endpoint**: `GET /admin/ingestion/{source_id}/runs?limit=20&offset=0`
- **Resposta**: `{ "runs": [ {run_summary...} ], "pagination": { ... } }`
- **Erros**: 404 fonte/config inexistente.

### 2.4. Detalhe de run
- **Endpoint**: `GET /admin/ingestion/runs/{run_id}`
- **Resposta**: `{ "run": { all fields, payload_preview? } }`
- **Erros**: 404 se run não existe.

### 2.5. Reprocessar run
- **Endpoint**: `POST /admin/ingestion/runs/{run_id}/reprocess`
- **Payload**: `{ "reason": "string" }`
- **Comportamento**: cria novo run com `trigger=REPROCESS` preservando source/config; idempotente por `run_id` + reason (segundo envio retorna run já criado).
- **Respostas**:
  - 202: run reprocessado criado.
  - 400: run original ainda RUNNING ou config desabilitada.
  - 404: run não encontrado.

## 3. Erros padronizados
- `source_not_found`, `config_not_found`
- `config_disabled`, `mode_incompatible`
- `run_in_progress`
- `invalid_payload`
- Cada erro retorna `{ "error": "<code>", "detail": "...", "trace_id": "<uuid>" }`.

## 4. Idempotência e pré-condições
- `POST /run` falha se já existe RUNNING para a fonte (INV-6), salvo `force=true` que cancela/fecha o run anterior com FAIL e cria novo.
- `reprocess_run` é idempotente por (`run_id`, `reason`); segunda chamada retorna o run já existente.
- `toggle-mode` exige que `enabled=false` não deixe runs RUNNING órfãos; serviço finaliza runs pendentes com FAIL antes de desligar automático.

## 5. Métricas do gate G2
- `api_operations_documented`: 5
- `api_tests_count`: cobrir happy path + erros por operação (meta inicial 12+ casos).
- `error_cases_covered`: pelo menos: fonte inexistente, config desabilitada, run em andamento, payload inválido.
- `api_tests_pass_rate`: 1.0 nos scripts do gate.
