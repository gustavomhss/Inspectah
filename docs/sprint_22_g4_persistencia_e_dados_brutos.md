# Sprint 22 — G4 Persistência e Dados Brutos

## 1. Decisão
Para a Fase 1, a ingestão 2.0 armazena payloads brutos em arquivos versionados por fonte e data. Metadados ficam em SQLite (`out/databases/s22_ingestion.sqlite`). `payload_ref` guarda o caminho absoluto/relativo para o arquivo NDJSON do run.

## 2. Layout de arquivos de dados brutos
```
data/ingestion_raw/{source_id}/{YYYY}/{MM}/{DD}/{run_id}.ndjson
```
- Conteúdo: linhas JSON com itens ingeridos.
- Arquivo acompanha `meta` na primeira linha com cabeçalho opcional `{ "__meta__": { "content_type": "...", "item_count": N } }`.

## 3. Metadados em SQLite
- Tabela `ingestion_configs` (definida em G1).
- Tabela `ingestion_runs` inclui `payload_ref` e `error_code/error_message`.

## 4. Consultas exemplo
- Runs por fonte e janela:
```sql
SELECT * FROM ingestion_runs
 WHERE source_id = :source_id
   AND datetime(started_at) BETWEEN :start AND :end
 ORDER BY datetime(started_at) DESC;
```
- Localizar dados brutos de um run:
```sql
SELECT payload_ref FROM ingestion_runs WHERE id = :run_id;
-- abre caminho em data/ingestion_raw/... e lê NDJSON
```
- Runs com erro recente:
```sql
SELECT source_id, id, error_code, error_message, started_at
  FROM ingestion_runs
 WHERE status = 'FAIL'
   AND datetime(started_at) > datetime('now', '-1 day');
```

## 5. Rastreabilidade e compatibilidade futura
- `payload_ref` é path estável; futuro hash/âncora pode ser calculado sobre o arquivo.
- Sem formato proprietário; NDJSON é compatível com Truth-DB/Sistema de Blocos e pode ser encapsulado em bundles com hash.
- `runs_with_data_linked_ratio` esperado = 1.0 nos testes: todo run finalizado aponta para arquivo existente.

## 6. Métricas do gate G4
- `storage_schemes_documented`: 2 (metadados em SQLite + payloads em NDJSON).
- `sample_queries_executed`: 3 exemplos acima executados nos testes.
- `runs_with_data_linked_ratio`: validar via testes (meta 1.0).
