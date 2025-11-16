# D9-G3 — Explore API & Integrações

**Responsável:** Codex (Inspectah Sprint D9)
**Data:** 2025-11-13T22:50:39Z

## Endpoints de Explore
- [x] Endpoints principais definidos (GET /items, /sources etc.) (D9.3 §3)
- [x] Filtros, paginação e ordenação especificados (§3.2 + princípios)

## Formatos de Resposta
- [x] Estrutura JSON descrita com campos, tipos e significado (§3.1–3.3)
- [x] Padrão de erros 4xx/5xx definido (§7)

## Erros e Rate Limiting
- [x] Rate limit v0 (120 req/min + burst 240) e cabeçalhos `X-RateLimit-*` documentados (§7)
- [x] Plano de revisão pós-teste (ação D9-API-001) descrito e vinculado ao playbook (§7, D9.8)

## Export
- [x] Formatos suportados definidos com exemplo (§3.6)
- [x] Limites de export/paginação documentados (§3.6 + princípios)

## Webhooks
- [x] Eventos listados (item.created, source.error etc.) (§4)
- [x] Payload completo e mecanismo de autenticação descritos (§2 + §4)

## Views e Consumo por BI
- [x] Estratégia de views/materializações explicada (§5)

## Integrações com MBP e demais sistemas
- [x] Exemplos claros de consumo pelo MBP/outros clientes (§6)
- [x] Responsabilidades entre Inspectah e consumidores delimitadas (§6 + §8)

## Observações
- Checklist finalizado após teste de mesa com filtros complexos + export encadeado; referência explícita à ação D9-API-001 adicionada.
