# Sprint 37 — Capitulo 4.4 — Tasks e Waves (Planner)

## Visao geral das waves

| Wave | Objetivo | Dominios | Dependencias | Criterio de saida |
| --- | --- | --- | --- | --- |
| W0 — ClaimGraph modelo e persistencia (G5) | Definir modelo de grafo, schemas, indices e operacoes basicas para claims/entidades/relacoes. | backend, dados/db | S36 entregue | G5 modelo definido; tabelas/indices criados; operacoes basicas funcionando. |
| W1 — Motor de Sinais batch (G6) | Implementar calculo periodico de 4 sinais agregados sobre ClaimGraph. | backend, dados | W0 | G6 sinais calculados; batch job rodando; snapshots persistidos. |
| W2 — Truth Policy DSL v1 (G7) | Parser e executor de linguagem declarativa para politicas de decisao por dominio. | backend, docs | W0 | G7 parser/executor funcionando; 3+ policies validas; integracao E40.5. |
| W3 — Guardiao v0 e integracao E40.5 (G8) | Orquestrador de comites com papeis, fluxo de validacao e integracao com E40.5. | backend | W2 | G8 fluxo completo; latencia <=20s; human_review funcional. |
| W4 — API Gateway, Cockpit e Fact Cards (G9) | Expor ClaimGraph, sinais e estados via APIs; UIs de Cockpit e Fact Cards v0. | backend, frontend | W3 | G9 APIs funcionando; UIs renderizando; source.guia declarado. |
| W5 — Metricas, ORR e GO/NO-GO | Consolidar metricas G5-G9, executar ORR e documentar GO/NO-GO. | qa_dados, ops | W4 | ORR executado; GO/NO-GO documentado; handoff para S38. |

### Estrategia de waves e tasks
- Waves seguem G5-G9: modelo → sinais → policies → guardiao → APIs/UIs → ORR.
- Cada gate G5-G9 aparece explicitamente em uma ou mais waves.
- Fluxo principal: ClaimGraph → Motor de Sinais → Policy DSL → Guardiao → API Gateway → Cockpit/Fact Cards.
- Riscos explicitados em Cap.7 tem tasks de mitigacao dedicadas.

## Tabela de tasks

| ID | Wave | Area | Descricao | Arquivos principais | Gates | Done Condition | Evidencias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S37-BE-001 | W0 | backend | Definir modelo de dados do ClaimGraph (nos, arestas, propriedades). | docs/architecture/p2_s37_claimgraph_model.md; app/claims/graph_models.py | G5 | Modelo documentado; schema versionado. | Doc de modelo; diagrama. |
| S37-DB-001 | W0 | dados/db | Criar migrations e indices para ClaimGraph. | db/migrations/027_sprint37_claimgraph.sql | G5 | Tabelas criadas; queries com planos aceitaveis. | Log de migration; explain plans. |
| S37-BE-002 | W0 | backend | Implementar operacoes basicas do ClaimGraph. | app/claims/graph_service.py; app/claims/graph_repository.py | G5 | add_claim, add_relation, get_cluster, get_contradictions funcionando. | Testes unitarios. |
| S37-BE-003 | W0 | backend | Integrar pipeline de claims existente com ClaimGraph. | app/agents/flows/claim_pipeline.py; app/claims/graph_service.py | G5 | Claims automaticamente adicionadas ao grafo. | Logs de integracao. |
| S37-BE-010 | W1 | backend | Implementar calculo de sinal mentiras_em_circulacao. | app/signals/calculators/lies_in_circulation.py | G6 | Query funcional; snapshot persistido. | Output do calculador. |
| S37-BE-011 | W1 | backend | Implementar calculo de sinal campo_batalha. | app/signals/calculators/battleground.py | G6 | Pares identificados; metrica calculada. | Output do calculador. |
| S37-BE-012 | W1 | backend | Implementar calculo de sinal radar_silencio. | app/signals/calculators/silence_radar.py | G6 | Topicos com queda detectados. | Output do calculador. |
| S37-BE-013 | W1 | backend | Implementar calculo de sinal fragilidade_narrativa. | app/signals/calculators/narrative_fragility.py | G6 | Claims frageis identificadas. | Output do calculador. |
| S37-BE-014 | W1 | backend | Implementar batch job para calculo periodico de sinais. | app/signals/batch_calculator.py; app/signals/signal_repository.py | G6 | Job executando a cada 1h; snapshots consultaveis. | Logs do job; query de snapshots. |
| S37-BE-020 | W2 | backend | Definir gramatica e parser do Truth Policy DSL v1. | app/truth/policy_dsl/grammar.py; app/truth/policy_dsl/parser.py | G7 | Gramatica completa; parser com erros claros. | Testes de parsing. |
| S37-BE-021 | W2 | backend | Implementar executor do Truth Policy DSL. | app/truth/policy_dsl/executor.py; app/truth/policy_engine.py | G7 | REQUIRE e ON-THEN executando; integracao E40.5. | Testes de execucao. |
| S37-DOC-020 | W2 | docs | Criar policies iniciais para dominios piloto. | policies/pilot_politics_v1.policy; policies/saude_v1.policy; policies/economia_v1.policy | G7 | 3+ policies validas e versionadas. | Arquivos de policy. |
| S37-BE-030 | W3 | backend | Implementar modelo de papeis do Guardiao. | app/guardian/roles.py; app/guardian/models.py | G8 | 4 papeis definidos; atribuicao funcional. | Testes de roles. |
| S37-BE-031 | W3 | backend | Implementar fluxo de validacao do Guardiao. | app/guardian/flow.py; app/guardian/service.py | G8 | Fluxo completo; timeout e fallback. | Testes de fluxo. |
| S37-BE-032 | W3 | backend | Integrar Guardiao com E40.5 e Truth Policy Engine. | app/guardian/service.py; app/truth/e40_5/checker.py | G8 | Policy carregada; E40.5 verificando. | Logs de integracao. |
| S37-BE-033 | W3 | backend | Implementar human_review flow no Guardiao. | app/guardian/human_review.py; app/guardian/service.py | G8 | Decisoes pausadas; UI permite resolver. | Screenshots; logs. |
| S37-BE-040 | W4 | backend | Setup API Gateway com rotas principais. | app/api/gateway.py; app/api/routes/claimgraph.py; app/api/routes/signals.py | G9 | Rotas funcionando; auth integrada. | Testes de API. |
| S37-FE-040 | W4 | frontend | Implementar Cockpit Casos com claims, sinais, estados. | frontend/.../cases/pages/CaseCockpitPage.tsx; .../ClaimGraphView.tsx | G9 | Visualizacao de claims e sinais. | Screenshots. |
| S37-FE-041 | W4 | frontend | Implementar Fact Cards v0 com MQV/entropia. | frontend/.../products/components/FactCard.tsx | G9 | Card com estado, metricas, disclaimers. | Screenshots. |
| S37-FE-042 | W4 | frontend | Integrar Explore API no frontend. | frontend/.../core/api/endpoints.ts; .../explore/pages/ExplorePage.tsx | G9 | ClaimGraph consultavel via UI. | Screenshots. |
| S37-QA-050 | W5 | qa_dados | Implementar scripts para metricas de ClaimGraph. | scripts/metrics/s37_claimgraph_metrics.py | G5 | Metricas calculadas; output JSON. | Output do script. |
| S37-QA-051 | W5 | qa_dados | Implementar scripts para metricas de Guardiao. | scripts/metrics/s37_guardian_metrics.py | G8 | coverage, latency, reversal_rate calculados. | Output do script. |
| S37-OPS-050 | W5 | ops | Preparar checklist e script de ORR S37. | bin/s37_orr.sh; docs/runbooks/S37_orr_checklist.md | G9 | Checklist G5-G9; script consolidando metricas. | Arquivos criados. |
| S37-OPS-051 | W5 | ops | Executar ORR S37 e documentar GO/NO-GO. | out/scorecards/S37_ORR.json; out/evidence/S37_ORR_summary.txt | G9 | ORR executado; GO/NO-GO documentado. | Scorecard; summary. |

### Matriz de Cobertura (gates, fluxos, riscos ↔ waves/tasks)

- **G5 — ClaimGraph operacional**
  - Waves: W0, W5
  - Tasks: S37-BE-001, S37-DB-001, S37-BE-002, S37-BE-003, S37-QA-050

- **G6 — Motor de Sinais batch**
  - Waves: W1
  - Tasks: S37-BE-010, S37-BE-011, S37-BE-012, S37-BE-013, S37-BE-014

- **G7 — Truth Policy DSL v1**
  - Waves: W2
  - Tasks: S37-BE-020, S37-BE-021, S37-DOC-020

- **G8 — Guardiao v0**
  - Waves: W3, W5
  - Tasks: S37-BE-030, S37-BE-031, S37-BE-032, S37-BE-033, S37-QA-051

- **G9 — API Gateway, Cockpit, Fact Cards**
  - Waves: W4, W5
  - Tasks: S37-BE-040, S37-FE-040, S37-FE-041, S37-FE-042, S37-OPS-050, S37-OPS-051

- **Riscos mitigados:**
  - Complexidade ClaimGraph: S37-BE-001 (modelo minimo), S37-DB-001 (indices)
  - Latencia Sinais: S37-BE-014 (batch otimizado)
  - Expressividade DSL: S37-DOC-020 (feedback via policies piloto)
  - Gargalo Guardiao: S37-BE-031 (timeouts), S37-BE-033 (human_review fallback)
