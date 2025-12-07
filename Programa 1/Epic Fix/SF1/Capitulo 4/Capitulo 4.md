# SF1 — Capítulo 4 — Execução & Cenários

## 4.1 Backend/serviço
- Aplicar limites e políticas; bloquear operações em SLO/alerta negativo ou drift; registrar slo_breach/log/metric e policy_violation; salvar operation_id/actor/catalog_hash em toda mudança de estado.

## 4.2 APIs/Console
- Casos felizes: start canary/teste, promoção, rollback com actor/hash válidos; auditoria persistida; UI reflete estados sem refresh manual (polling curto).
- Casos negativos: sem actor, hash divergente, limite violado, SLO breach simulado → 4xx/bloqueio e log; UI mostra erro específico (drift/actor/alert).

## 4.3 Observabilidade
- `curl /metrics` + promtool; alertas disparados/resolvidos; painel com dados reais e labels corretos; FAIL se qualquer série essencial estiver vazia.

## 4.4 Pilotos (G4)
- news_v2 (newsdata.io/latest com filtros BR/PT + domains) e contestacao_v0 (mesma fonte, políticas distintas) via API/UI; rollback e promoção exercitados; hash publish/runtime comparado; alert firing + slo_breach registrado; evidências (logs, métricas, screenshots reais, timeline); scripts falham se detectarem fixtures duplicadas ou screenshots placeholder; respeitar rate limit (ex.: ≤60 req/min) com throttling.
