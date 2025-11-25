# Sprint 22 — G1 Modelos e Invariantes da Ingestão 2.0

## 1. Objetivo
Descrever modelos de domínio da ingestão 2.0 (IngestionConfig e IngestionRun), seus campos, domínios e invariantes formais. Estes modelos são base para migrations, serviços, FSM e testes automatizados da S22.

## 2. Entidades e campos

### 2.1. IngestionConfig
- `id` (str): identificador estável `ingcfg_{uuid10}`.
- `source_id` (str): FK para `sources.id` (Console de Fontes S21).
- `enabled` (bool): habilita/desabilita ingestão da fonte.
- `mode` (enum): `MANUAL_ONLY` ou `AUTOMATIC`.
- `interval_minutes` (int): intervalo alvo entre execuções automáticas (mín 15, máx 10080).
- `max_attempts` (int): tentativas por run antes de marcar FAIL (mín 1, default 3).
- `timeout_seconds` (int): timeout por run (mín 5, default 60).
- `last_run_id` (str|None): referência ao último run conhecido.
- `created_at` / `updated_at` (datetime ISO).
- `created_by` / `updated_by` (str): rastreabilidade operacional.

### 2.2. IngestionRun
- `id` (str): `run_{uuid10}`.
- `config_id` (str): FK para `ingestion_configs.id`.
- `source_id` (str): redundante para queries rápidas; deve bater com config.
- `trigger` (enum): `MANUAL`, `AUTOMATIC`, `REPROCESS`.
- `status` (enum): `PENDING`, `RUNNING`, `SUCCESS`, `PARTIAL_SUCCESS`, `FAIL`.
- `started_at` (datetime ISO): obrigatório no nascimento do run.
- `finished_at` (datetime ISO|None): preenchido apenas em estados finais.
- `items_processed` (int): contagem lógica de itens ingeridos.
- `error_code` / `error_message` (str|None): presentes em FAIL/PARTIAL.
- `payload_ref` (str|None): ponteiro para dados brutos (path ou chave).
- `meta` (json): detalhes adicionais do run (latência, origem do gatilho, etc.).

### 2.3. Enums
- `IngestionMode`: MANUAL_ONLY, AUTOMATIC.
- `IngestionStatus`: PENDING, RUNNING, SUCCESS, PARTIAL_SUCCESS, FAIL.
- `IngestionTrigger`: MANUAL, AUTOMATIC, REPROCESS.

## 3. Invariantes (INV-n)
1. **INV-1**: `IngestionConfig.source_id` referencia fonte existente e não deletada.  
2. **INV-2**: Fonte em estado `DEPRECATED` ou `DISABLED_*` não pode ter `mode=AUTOMATIC`.  
3. **INV-3**: `interval_minutes` entre 15 e 10080; `timeout_seconds` >= 5; `max_attempts` >= 1.  
4. **INV-4**: `IngestionRun` nasce apenas com status `PENDING` ou `RUNNING`.  
5. **INV-5**: Estados finais são apenas `SUCCESS`, `PARTIAL_SUCCESS`, `FAIL`; exigem `finished_at`.  
6. **INV-6**: Não pode existir mais de um `IngestionRun` com status `RUNNING` para a mesma fonte/config em paralelo.  
7. **INV-7**: `RUNNING` exige `started_at` preenchido; transições para estado final preservam `started_at`.  
8. **INV-8**: `finished_at` > `started_at` em runs finalizados.  
9. **INV-9**: `payload_ref` não pode ser nulo quando status é `SUCCESS` ou `PARTIAL_SUCCESS` (há dados brutos).  
10. **INV-10**: `error_code` ou `error_message` obrigatórios quando status = `FAIL` ou `PARTIAL_SUCCESS`.  
11. **INV-11**: `IngestionRun.source_id` deve bater com `IngestionConfig.source_id`.  
12. **INV-12**: `trigger=AUTOMATIC` só permitido se `mode=AUTOMATIC` e `enabled=true` na config.

## 4. Métricas do gate G1
- `invariants_defined_count`: 12
- `invariants_tested_count`: 12 (meta: 100% cobertos por pytest)
- `invariants_tests_pass_rate`: esperado = 1.0 nos scripts do gate

## 5. Notas de implementação
- Storage adotado para G1: SQLite em `out/databases/s22_ingestion.sqlite`, espelhando padrão S21 de serviços por fonte.
- `payload_ref` inicialmente aponta para arquivos em `data/ingestion_raw/{source_id}/{run_id}.json` (Wave 4 detalha), mas a FK é registrada desde já para garantir estabilidade de referência.
- Todos os horários são UTC em ISO8601 sem timezone local (sufixo `Z` no persistido).
