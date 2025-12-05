# Runbook — Latência alta no pipeline de notícias (S33)

## Contexto
- Componente: `pipeline_noticias`
- SLO: `s33_slo_latencia_pipeline_noticias` (p95 <= 60s, janela 30m)
- Sintoma: alerta de latência degradada ou backlog crescente.

## Sinais
- Alerta `alert_latencia_pipeline_noticias_p95` disparado.
- Cockpit mostra pipeline degradado e incidente aberto.
- Métrica `pipeline_latency_seconds{pipeline="pipeline_noticias"}` acima do limiar.

## Diagnóstico
1) Checar backlog/fila: `kubectl exec -n ingest deploy/ingest-noticias -- python bin/queue_stats.py`.
2) Verificar erros de agentes downstream no log.
3) Conferir variações de volume de eventos (picos de RSS).

## Mitigação
1) Escalar workers (ex.: aumentar réplicas do job de ingestão para 2-3).
2) Se agente lento, habilitar modo degradado ou pular etapa pesada temporariamente (registrar no incidente).
3) Reprocessar lote afetado após estabilização.

## Critério de sucesso
- p95 volta a <= 60s na janela de 30m.
- Backlog esvaziado.
- Incidente atualizado com ações e próxima revisão.
