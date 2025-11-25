# Sprint 21 — Modelo de Dados do Console de Fontes

Este documento descreve o modelo de dados implementável para o módulo de fontes na Fase 1. Ele deve ser mapeado diretamente em `app/sources/models.py` e nas migrations `migrations/versions/*_s21_sources_schema.py`.

## 1. Entidades principais

### 1.1 Source
- `id` (UUID/Texto, PK)
- `slug` (string única e estável, index)
- `name` (string, obrigatório)
- `description` (texto)
- `type` (enum `SourceType`, ver ontologia)
- `category` (enum simples: `official`, `community`, `monitoring`, `critical`, `redundant`)
- `themes` (lista/JSON de temas)
- `info_types` (lista/JSON)
- `protocol` (enum: `http`, `https`, `file`)
- `format` (enum: `rss`, `json`, `csv`, `xml`, `html`, `custom`)
- `endpoint` / `url_base` (string)
- `auth_type` (enum: `none`, `token`, `basic`, `api_key`)
- `auth_config` (JSON: headers, query/body tokens, scopes)
- `request_params` (JSON: default query/body)
- `headers` (JSON)
- `frequency` (enum: `manual`, `hourly`, `daily`, `weekly`)
- `timeout_ms` (int)
- `retry_policy` (JSON: attempts, backoff_ms)
- `parsing_config` (JSON: selectors/paths)
- `redundancy_group` (string) e `redundancy_role` (enum: `primary`, `secondary`, `sentinel`)
- `state` (enum, ver ciclo de vida)
- `state_reason` (texto)
- `state_updated_at` (datetime)
- `created_at`, `updated_at` (datetime)
- `created_by`, `updated_by`, `last_reviewed_by` (string/actor)
- `meta` (JSON genérico)

### 1.2 SourceType
- Tabela de referência opcional para tipos (id, name, description, defaults).
- Serve para popular UI e validações de config.
- Tipos suportados na Fase 1/2 incluem: `news_rss`, `gossip_feed`, `sports_api`, `weather_api`, `official_open`, `data_api` (APIs REST/JSON/GraphQL com endpoint obrigatório).

### 1.3 SourceCategory / SourceTag
- `SourceCategory`: id, name, description.
- Relação N:N `SourceCategoryLink` (source_id, category_id).
- `SourceTag`: tags livres (opcional) guardadas em JSON ou tabela de link simples.

### 1.4 SourceStateHistory
- `id` (PK)
- `source_id` (FK Source)
- `from_state`, `to_state` (enum)
- `reason` (texto)
- `changed_by` (string)
- `created_at` (datetime)
- `conflict_flag` (bool) e `conflict_with_sources` (JSON) para ganchos de Debunker.
- `contestations` (JSON leve) indicando abertura/fechamento.

### 1.5 SourceHealthCheck
- `id` (PK)
- `source_id` (FK Source)
- `status` (enum: `OK`, `DEGRADED`, `FAIL`)
- `latency_ms` (int)
- `checked_at` (datetime)
- `error` (texto opcional)
- `meta` (JSON: response snippets, http_status, sample payload hash)

### 1.6 Attachments auxiliares
- `SourceEndpointLog` (opcional para evidenciar health-checks/manual): id, source_id, http_status, hash, created_at.

## 2. Relacionamentos
- `Source` 1:N `SourceStateHistory`.
- `Source` 1:N `SourceHealthCheck`.
- `Source` N:N `SourceCategory`.
- `Source` N:N `themes` (armazenado como JSON simples na Fase 1).
- `Source` N:1 `SourceType` (referência de metadados).

## 3. Índices e constraints
- Índices em `slug`, `type`, `state`, `redundancy_group`, `category`.
- Constraint: `DISABLED_PERM` não pode ser atualizado para outro estado.
- Constraint: `state_updated_at` deve ser atualizado a cada transição.
- Constraint: `redundancy_role` não nula se `redundancy_group` preenchido.
- Unique: (`redundancy_group`, `redundancy_role`, `info_type`) opcional para evitar duplicação de função no grupo.

## 4. Ciclo de vida (resumo)
Estados: `PROPOSED`, `TESTING`, `ACTIVE`, `UNDER_REVIEW`, `SUSPECT`, `DISABLED_TEMP`, `DISABLED_PERM`.
Transições válidas conforme `docs/sprint_21_ciclo_vida_fontes.md`. Históricos devem registrar autor e motivo.

## 5. Auditoria e proveniência
- Todas as entidades principais têm `created_at`, `updated_at`.
- `SourceStateHistory` registra `changed_by` e `reason`.
- Campos `source_origin`/`definition_origin` podem registrar documento/issue de origem.

## 6. Ganchos para Debunker e contestação
- `Source` inclui flags `has_open_contestation`, `conflict_flags`, `last_conflict_at`.
- `SourceStateHistory` pode registrar `conflict_with_sources` e `contestations` (quem abriu, estado).
- `meta` aceita `evidence_refs` (ids de evidência/anchors).

## 7. Compatibilidade com ingestão (S22)
- Campos operacionais (`endpoint`, `auth`, `frequency`, `parsing_config`) são a base do scheduler/worker da S22.
- `state` controla se a ingestão pode executar; `ACTIVE` e `TESTING` permitem coleta controlada; estados de bloqueio impedem execução.

## 8. Persistência e migrations
- Implementação alvo: SQLite (Fase 1) com scripts em `migrations/versions/*_s21_sources_schema.py`.
- Scripts devem criar tabelas acima com comentários referenciando este documento e o ciclo de vida.
- Seeds em `*_s21_sources_seed_examples.py` inserem exemplos cobrindo domínios obrigatórios.

## 9. Representação JSON (para APIs)
- DTOs de leitura devem expor: campos principais de `Source`, último health-check, últimos estados (limite configurável), categorias e tags.
- DTOs de escrita (`SourceCreate`, `SourceUpdate`) recebem apenas campos permitidos; campos de auditoria são internos.

## 10. Métricas e scorecard
- Indicadores de qualidade (S21_G7) usam este modelo para medir:
  - Cobertura de estados.
  - Percentual de fontes com redundancy_group configurado.
  - Presença de audit fields em todas as entidades.
