# Runbook — Fonte de notícias atrasada (S33)

## Contexto
- Componente: `fonte_noticias_principal`
- SLO: `s33_slo_recencia_fonte_noticias` (<= 900s, janela 15m)
- Sintoma: recência > 900s ou falhas repetidas na coleta.

## Sinais
- Alerta `alert_recencia_fonte_noticias_principal` disparado.
- Cockpit mostra componente em estado anômalo e incidente associado.
- Logs de ingestão com erros 4xx/5xx da fonte.

## Diagnóstico
1) Checar logs do pipeline: `kubectl logs deploy/ingest-noticias -n ingest --tail=200`.
2) Verificar metrica recência: consultar `ingest_source_recency_seconds{source="fonte_noticias_principal"}`.
3) Confirmar se RSS está acessível manualmente.

## Mitigação
1) Se fonte fora do ar: abrir incidente e marcar `severity=HIGH`; registrar workaround (fonte alternativa).
2) Se erro temporário: reiniciar job `ingest-noticias` e reavaliar métrica após 5 min.
3) Atualizar incidente com causa e ação tomada.

## Critério de sucesso
- Métrica de recência volta a <= 900s em até 15m.
- Incidente atualizado com causa e resolução.
- Cockpit mostra componente em OK ou degradado aceitável.
