# D9.4 — Anexo C: Data Model, DDL & Migração (v1.0)
> Status: CONGELADO (LOCKED) — Inspectah D9 v1.1 — não editar fora de novas sprints ou PATCH_D9 explícito.

## 1. Visão Geral
O modelo de dados do Inspectah foi desenhado para:
- Manter histórico completo das coletas.
- Permitir consultas rápidas (API/BI) sem duplicar lógica.
- Registrar manifestos e snapshots de forma auditável.
- Facilitar migração inicial (SQLite) e evolução para Postgres.

## 2. Topologia de Armazenamento
| Ambiente | Banco primário | Observações |
|----------|----------------|-------------|
| Dev/local | SQLite 3 | Simples, arquivo único; usado para prototipagem/CLI.
| Staging/Prod | Postgres 15 | Recurso principal; suporta JSONB, FTS, views e particionamento.
| Evidence Vault | Object storage compatível com S3 (CE Object Store) | Buckets dedicados na região `sa-east-1` (São Paulo), com criptografia gerenciada (SSE-KMS) e política de residência de dados alinhada à LGPD.

## 3. Entidades Principais
### 3.1 `source`
```sql
CREATE TABLE source (
  id              TEXT PRIMARY KEY,
  name            TEXT NOT NULL,
  description     TEXT,
  schedule_cron   TEXT NOT NULL,
  tags            TEXT[] DEFAULT '{}',
  status          TEXT NOT NULL CHECK (status IN ('draft','active','paused')),
  config          JSONB NOT NULL,
  field_version   INTEGER NOT NULL,
  lgpd_profile    JSONB NOT NULL, -- {pii: bool, robots_ok: bool, retention_days: int}
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```
Indices: `idx_source_status`, `idx_source_tags` (GIN), `idx_source_field_version`.

### 3.2 `source_run`
Representa cada execução do pipeline.
```sql
CREATE TABLE source_run (
  id             UUID PRIMARY KEY,
  source_id      TEXT NOT NULL REFERENCES source(id),
  started_at     TIMESTAMPTZ NOT NULL,
  finished_at    TIMESTAMPTZ,
  status         TEXT NOT NULL CHECK (status IN ('success','partial','failed')),
  items_ingested INTEGER DEFAULT 0,
  error_code     TEXT,
  error_payload  JSONB,
  created_by     TEXT NOT NULL -- scheduler id
);
CREATE INDEX idx_source_run_source_time ON source_run (source_id, started_at DESC);
```

### 3.3 `item`
Representa item lógico (chave natural `source_id + item_key`).
```sql
CREATE TABLE item (
  id            UUID PRIMARY KEY,
  source_id     TEXT NOT NULL REFERENCES source(id),
  item_key      TEXT NOT NULL,
  latest_version UUID NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(source_id, item_key)
);
```

### 3.4 `item_version`
Cada coleta gera uma versão.
```sql
CREATE TABLE item_version (
  id             UUID PRIMARY KEY,
  item_id        UUID NOT NULL REFERENCES item(id),
  source_run_id  UUID NOT NULL REFERENCES source_run(id),
  collected_at   TIMESTAMPTZ NOT NULL,
  field_version  INTEGER NOT NULL,
  manifest_hash  TEXT NOT NULL,
  manifest_path  TEXT NOT NULL, -- pointer no Evidence Vault
  snapshot_path  TEXT,
  fields         JSONB NOT NULL,
  pii_mask       JSONB DEFAULT '{}'::jsonb,
  diff_summary   JSONB,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_item_version_item ON item_version (item_id, collected_at DESC);
CREATE INDEX idx_item_version_source_collected ON item_version (source_run_id, collected_at);
```

### 3.5 `item_kv`
Tabela normalizada para filtros performáticos.
```sql
CREATE TABLE item_kv (
  item_version_id UUID NOT NULL REFERENCES item_version(id) ON DELETE CASCADE,
  field_id        TEXT NOT NULL,
  field_type      TEXT NOT NULL,
  value_text      TEXT,
  value_number    NUMERIC,
  value_timestamp TIMESTAMPTZ,
  value_bool      BOOLEAN,
  PRIMARY KEY (item_version_id, field_id)
);
CREATE INDEX idx_item_kv_field_text ON item_kv (field_id, value_text);
CREATE INDEX idx_item_kv_field_num ON item_kv (field_id, value_number);
```

### 3.6 Full-Text Search
```sql
CREATE TABLE item_fts (
  item_version_id UUID PRIMARY KEY REFERENCES item_version(id) ON DELETE CASCADE,
  document        tsvector NOT NULL
);
CREATE INDEX idx_item_fts_document ON item_fts USING GIN (document);
```
`document` é construído concatenando campos marcados como `fts=true` no Field Designer.

### 3.7 `field_definition`
```sql
CREATE TABLE field_definition (
  id           UUID PRIMARY KEY,
  source_id    TEXT NOT NULL REFERENCES source(id),
  version      INTEGER NOT NULL,
  status       TEXT NOT NULL CHECK (status IN ('draft','active','deprecated')),
  definition   JSONB NOT NULL,
  created_by   TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(source_id, version)
);
```

### 3.8 `webhook_endpoint` e `webhook_delivery`
- `webhook_endpoint`: configurações de destino (URL, secret, eventos, status).
- `webhook_delivery`: histórico de tentativas com `status`, `response_code`, `latency_ms`.

## 4. Evidence Vault
- Armazenamento oficial: **CE Object Store**, compatível com S3, provisionado na região `sa-east-1` (São Paulo) para garantir residência de dados no Brasil.
- Configuração de path: `inspectah-evidence/<source_id>/<YYYY/MM>/<item_version_id>.json`.
- Snapshots (HTML, PDF, JSON original) ficam no mesmo bucket com sufixo `.raw`. Hash SHA-256 salvo em `manifest_hash`.
- Criptografia: SSE-KMS com chaves dedicadas ao Inspectah (`kms_key_inspectah_ev`). Rotação anual obrigatória.
- Controles de acesso: políticas IAM restritas por fonte/ambiente, require TLS 1.2+, URLs pré-assinadas expiram em 15 min.
- Replicação opcional (cross-region) só ocorre para regiões equivalentes LGPD; por padrão fica desativada.

## 5. Retenção e Política de Purga
| Classe de dado | Retenção padrão | Observações |
|----------------|-----------------|-------------|
| `item_version` / `item_kv` | Indefinida (v0). Futuro: política configurável por fonte. |
| `snapshot` com PII | 90 dias ou menor, conforme D9.5. Após expirar, apenas hash permanece. |
| `source_run` logs | 180 dias. Resumir métricas após esse período. |
| `api_audit_log` | 180 dias para tokens padrão; 365 dias para tokens críticos. |

Purga executada por job semanal. Antes de remover snapshots, gera manifest de deleção anexado ao Evidence Vault.

## 6. Migração SQLite → Postgres
1. **Schema parity**: manter scripts `schema_sqlite.sql` e `schema_postgres.sql` versionados lado a lado.
2. **Abstração de acesso**: usar camada de repositório única (ex.: `inspectah_store`) para suportar ambos.
3. **Export/import**:
   - Exportar SQLite via `.dump` ou utilitário `litecli`.
   - Converter tipos (`TEXT[]` → tabelas auxiliares) durante import usando scripts Python/Go.
   - Recalcular índices e FTS após import (não tentar reaproveitar).
4. **Verificação**: executar `checksum` por tabela e comparar contagens; reprocessar 5% das fontes para garantir determinismo.
5. **Cutover**: congelar ingestão durante janela curta (≤ 30 min), rodar export/import, apontar pipelines para Postgres e reabilitar jobs.

## 7. Performance e Escalabilidade
- Particionamento por `collected_at` mensal em `item_version` quando chegar a >50M registros.
- `item_kv` usa partial indexes por campo mais consultado (ex.: `value_text WHERE field_id='city'`).
- FTS atualizado assíncronamente via job `fts_refresher` para evitar impacto em ingestão.

## 8. Backup & Restore
- Postgres: PITR com WAL em objeto storage, snapshots diários (retenção 14 dias) + semanal (retenção 6 meses).
- SQLite: cópia do arquivo após cada ingestão relevante (dev) — meramente conveniência.
- Evidence Vault: versão habilitada; exclusões registradas.
- Procedimento de restore inclui validação da `d9_summary_gate_matrix.json` correspondente para garantir consistência documental.

## 9. Observabilidade do Data Layer
- Métricas: tamanho das tabelas, crescimento diário de `item_version`, latência média de queries de Explore.
- Alertas: `source_run` com falha consecutiva >3, `item_kv` com taxa de nulos > tolerância, FTS atrasado >1h.

## 10. Conexões com Outros D9.x
- Tipos de campos e transforms vêm de D9.2.
- APIs expõem dados das views definidas aqui (D9.3).
- Guardrails de retenção e PII alinhados a D9.5.
- Evolução do schema seguirá D9.8.

Este anexo estabelece o blueprint físico do armazenamento do Inspectah, garantindo que o modelo sustente os casos de uso descritos no D9.0 e permita migração segura para Postgres sem improvisos.
