# S33 — SLOs priorizados

IDs e métricas alinhados ao recorte e mapa de componentes. Todos devem ter métrica/consulta concreta.

## s33_slo_recencia_fonte_noticias
- descricao: recência dos eventos da `fonte_noticias_principal`.
- metrica: `ingest_source_recency_seconds{source="fonte_noticias_principal"}`
- limiar: `<= 900` segundos
- janela: 15m
- alerta: `alert_recencia_fonte_noticias_principal` (threshold 900s, canal #ops)
- componentes: [`fonte_noticias_principal`]

## s33_slo_recencia_fonte_ibge
- descricao: recência dos dados da `fonte_oficial_ibge`.
- metrica: `ingest_source_recency_seconds{source="fonte_oficial_ibge"}`
- limiar: `<= 3600` segundos
- janela: 1h
- alerta: `alert_recencia_fonte_ibge` (threshold 3600s, canal #ops)
- componentes: [`fonte_oficial_ibge`]

## s33_slo_latencia_pipeline_noticias
- descricao: latência p95 do pipeline de notícias (ingestão → normalização → dispatch).
- metrica: `pipeline_latency_seconds{pipeline="pipeline_noticias", quantile="0.95"}`
- limiar: `<= 60` segundos
- janela: 30m
- alerta: `alert_latencia_pipeline_noticias_p95` (threshold 60s, canal #ops)
- componentes: [`pipeline_noticias`]

## s33_slo_disponibilidade_api_cockpit
- descricao: disponibilidade do endpoint `/api/ops/cockpit/overview`.
- metrica: `http_request_success_rate{service="api_cockpit_ops", route="/api/ops/cockpit/overview"}`
- limiar: `>= 0.995`
- janela: 1h
- alerta: `alert_disponibilidade_api_cockpit` (trigger <0.995, canal #ops)
- componentes: [`api_cockpit_ops`]
