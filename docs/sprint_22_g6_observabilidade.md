# Sprint 22 — G6 Observabilidade da Ingestão

## 1. Logs estruturados
- Cada run gera linha JSON com: `run_id`, `source_id`, `config_id`, `trigger`, `status`, `started_at`, `finished_at`, `items_processed`, `latency_ms`, `error_code`, `error_message`, `payload_ref`.
- Logs gravados em `out/evidence/S22_G6_observability/ingestion_runs.log` durante os testes.

## 2. Métricas implementadas (metrics/ingestion_s22.py)
- `ingestion_runs_total{source_id,status,trigger}`
- `ingestion_runs_success_total{source_id}`
- `ingestion_runs_fail_total{source_id}`
- `ingestion_latency_ms_bucket{source_id}` (histogram)
- `ingestion_last_success_timestamp{source_id}`
- `ingestion_last_failure_timestamp{source_id}`
- `ingestion_sources_without_recent_runs` (gauge calculada em script health)

## 3. Consultas/painéis
- Dashboard `dashboards/ingestion_s22_overview.json` com:
  - gráfico de runs_total por fonte;
  - taxa de sucesso/falha;
  - tabela de fontes sem runs recentes (threshold 24h configurável);
  - latência p95.
- Script auxiliar `app/ingestion/observability.py` expõe helpers para registrar e exportar métricas.

## 4. Cenário de falha simulada
- Testes criam run FAIL com `error_code="network_error"`; métrica `ingestion_runs_fail_total` incrementa e painel aponta fonte em “erros recentes”.
- Script health identifica fontes sem runs há mais de 24h e popula `sources_without_recent_runs`.

## 5. Métricas do gate G6
- `observability_metrics_defined`: 7
- `sources_with_recent_errors`: >=1 durante testes controlados.
- `sources_without_recent_runs`: >=1 em cenário sintético de fonte parada.
- `metrics_query_paths_documented`: 2 (dashboard + script health).
