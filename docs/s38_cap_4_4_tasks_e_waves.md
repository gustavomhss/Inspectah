# Sprint 38 — Capitulo 4.4 — Tasks e Waves (Planner)

## Visao geral das waves

| Wave | Objetivo | Dominios | Dependencias | Criterio de saida |
| --- | --- | --- | --- | --- |
| W0 — Fontes Oficiais e Scrapers (G10) | Integrar fontes oficiais e implementar scrapers robustos. | backend | S37 entregue | G10 fontes integradas; scrapers funcionais; health monitoring. |
| W1 — Console Fontes v1 (G11) | Interface completa para gerenciamento de fontes. | frontend, backend | W0 | G11 CRUD funcional; metricas visiveis; historico disponivel. |
| W2 — ClaimGraph Relacoes e Sinais On-Demand (G12) | Inferir relacoes e calcular sinais em tempo real. | backend | W0 | G12 relacoes inferidas; sinais <200ms; cache >80%. |
| W3 — Policies Versionadas e Memory Controller (G13) | Versionar policies e controlar contexto. | backend, dados/db | W0 | G13 versionamento funcional; paginacao basica. |
| W4 — Dashboards, Contratos e Explicabilidade (G14) | Operacao, contratos formais e reasoning paths. | frontend, backend | W2, W3 | G14 dashboard ops; contratos v1; explicabilidade basica. |
| W5 — Metricas, ORR e GO/NO-GO | Consolidar metricas G10-G14, executar ORR. | qa_dados, ops | W4 | ORR executado; GO/NO-GO documentado; handoff S39. |

### Estrategia de waves e tasks
- W1, W2, W3 podem rodar em paralelo apos W0.
- W4 depende de W2 e W3 (integracao de sinais e policies).
- Cada gate G10-G14 tem wave correspondente.
- Total de 30 tasks distribuidas em 6 waves.

## Tabela de tasks

| ID | Wave | Area | Descricao | Arquivos principais | Gates | Done Condition | Evidencias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S38-BE-001 | W0 | backend | Integrador de fontes oficiais | app/sources/official_integrator.py | G10 | Integrador funcional com 3+ fontes | Logs de ingestao |
| S38-BE-002 | W0 | backend | APIs gov.br e dados.gov | app/sources/adapters/gov_br.py, dados_gov.py | G10 | Adapters funcionando | Documentos ingeridos |
| S38-BE-003 | W0 | backend | Framework de scrapers | app/sources/scrapers/base.py | G10 | Base scraper com retry e rate limit | Testes unitarios |
| S38-BE-004 | W0 | backend | Scrapers de sites de checagem | app/sources/scrapers/aosfatos.py, lupa.py, boatos.py | G10 | 5+ scrapers funcionais | Conteudo extraido |
| S38-BE-005 | W0 | backend | Rate limiting e retry | app/sources/rate_limiter.py | G10 | Rate limiting por fonte | Logs de throttling |
| S38-BE-006 | W0 | backend | Health monitoring | app/sources/health_monitor.py | G10 | Health check periodico | Dashboard de status |
| S38-FE-010 | W1 | frontend | CRUD de fontes na UI | frontend/.../sources/SourcesPage.tsx | G11 | CRUD completo funcionando | Screenshots |
| S38-FE-011 | W1 | frontend | Visualizacao de metricas | frontend/.../sources/SourceMetrics.tsx | G11 | Graficos de metricas | Screenshots |
| S38-FE-012 | W1 | frontend | Historico de ingestao | frontend/.../sources/IngestionHistory.tsx | G11 | Timeline de ingestao | Screenshots |
| S38-BE-010 | W1 | backend | API de gerenciamento de fontes | app/api/routes/sources.py | G11 | Endpoints CRUD funcionando | Testes de API |
| S38-BE-020 | W2 | backend | Inferencia de relacoes | app/claims/relation_inference.py | G12 | Relacoes inferidas automaticamente | Grafo com edges |
| S38-BE-021 | W2 | backend | Algoritmo de clustering v2 | app/claims/clustering.py | G12 | 30% menos clusters redundantes | Metricas de clustering |
| S38-BE-022 | W2 | backend | API de sinais on-demand | app/api/routes/signals.py | G12 | Endpoint funcional | Response time <200ms |
| S38-BE-023 | W2 | backend | Cache de sinais com TTL | app/signals/cache.py | G12 | Cache hit rate >80% | Metricas de cache |
| S38-BE-024 | W2 | backend | Calculo real-time de sinais | app/signals/realtime_calculator.py | G12 | Calculo funcional | Outputs de sinais |
| S38-BE-030 | W3 | backend | Versionamento de policies | app/truth/policy_versioning.py | G13 | Versoes salvas e recuperaveis | Historico de versoes |
| S38-BE-031 | W3 | backend | Diff e rollback de policies | app/truth/policy_diff.py | G13 | Diff e rollback funcionais | Testes de rollback |
| S38-DB-030 | W3 | dados/db | Schema de versoes | db/migrations/028_sprint38_policy_versions.sql | G13 | Tabela criada com indices | Explain plans |
| S38-BE-032 | W3 | backend | Memory Controller core | app/memory/controller.py | G13 | Paginacao basica funcional | Logs de paginacao |
| S38-BE-033 | W3 | backend | Paginacao de contexto | app/memory/context_pager.py | G13 | Contexto longo dividido | Testes com claims longas |
| S38-FE-040 | W4 | frontend | Dashboard de operacao | frontend/.../ops/OpsDashboard.tsx | G14 | Dashboard funcional | Screenshots |
| S38-FE-041 | W4 | frontend | Metricas real-time | frontend/.../ops/RealtimeMetrics.tsx | G14 | Auto-refresh funcional | Screenshots |
| S38-BE-040 | W4 | backend | Schema de contratos v1 | app/contracts/schema.py | G14 | Schema definido | Documentacao OpenAPI |
| S38-BE-041 | W4 | backend | Validacao de contratos | app/contracts/validator.py | G14 | Validacao funcionando | Testes de validacao |
| S38-BE-042 | W4 | backend | Reasoning paths | app/explain/reasoning.py | G14 | Paths gerados | JSON de reasoning |
| S38-FE-042 | W4 | frontend | Visualizacao de explicabilidade | frontend/.../explain/ReasoningView.tsx | G14 | UI de reasoning | Screenshots |
| S38-QA-050 | W5 | qa_dados | Metricas de fontes e scrapers | scripts/metrics/s38_sources_metrics.py | G10-G11 | Metricas calculadas | JSON output |
| S38-QA-051 | W5 | qa_dados | Metricas de sinais on-demand | scripts/metrics/s38_signals_metrics.py | G12 | Latencia e cache rate | JSON output |
| S38-OPS-050 | W5 | ops | Checklist e script ORR | bin/s38_orr.sh | G14 | ORR executavel | Arquivos criados |
| S38-OPS-051 | W5 | ops | Executar ORR e GO/NO-GO | out/scorecards/S38_ORR.json | - | GO/NO-GO documentado | Scorecard final |

### Matriz de Cobertura (gates, fluxos, riscos -> waves/tasks)

- **G10 — Fontes e Scrapers**
  - Waves: W0, W5
  - Tasks: S38-BE-001, S38-BE-002, S38-BE-003, S38-BE-004, S38-BE-005, S38-BE-006, S38-QA-050

- **G11 — Console Fontes v1**
  - Waves: W1
  - Tasks: S38-FE-010, S38-FE-011, S38-FE-012, S38-BE-010

- **G12 — ClaimGraph Relacoes e Sinais On-Demand**
  - Waves: W2, W5
  - Tasks: S38-BE-020, S38-BE-021, S38-BE-022, S38-BE-023, S38-BE-024, S38-QA-051

- **G13 — Policies Versionadas e Memory Controller**
  - Waves: W3
  - Tasks: S38-BE-030, S38-BE-031, S38-DB-030, S38-BE-032, S38-BE-033

- **G14 — Dashboards, Contratos e Explicabilidade**
  - Waves: W4, W5
  - Tasks: S38-FE-040, S38-FE-041, S38-BE-040, S38-BE-041, S38-BE-042, S38-FE-042, S38-OPS-050, S38-OPS-051

- **Riscos mitigados:**
  - APIs indisponiveis: S38-BE-005 (retry), S38-BE-006 (health)
  - Scrapers bloqueados: S38-BE-003 (rate limit), S38-BE-005 (retry)
  - Latencia sinais: S38-BE-023 (cache), S38-BE-024 (otimizacao)
  - Memory Controller complexo: S38-BE-032 (MVP minimo)
  - Contratos incompletos: S38-BE-040 (schema evolutivo)
