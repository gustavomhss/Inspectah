# Inspectah — Sprint 4 ORR Summary

## Objetivo da Sprint 4

Levar o Inspectah de experimento de laboratório a ferramenta interna confiável para 3 Fontes P0 reais (`api_market_prices`, `html_market_watch`, `rss_news_minimal`), com Evidence Vault vivo, Explore mínimo seguro e observabilidade séria com SLOs explícitos, tudo protegido por um ORR T0–T8 reproduzível e auditável.

## Estado dos gates S4_T0…S4_T7

| Gate | Nome | Status | Observações |
| --- | --- | --- | --- |
| S4_T0 | Discovery | PASS | Checklist completo, Fontes P0 definidas, Capítulos 1–4 absorvidos. |
| S4_T1 | Specs & Invariantes | PASS | Modelo de dados + matriz invariantes×gates publicados. |
| S4_T2 | Registry & Field Designer | PASS | YAMLs canônicos em `config/sources/sprint_4/fontes_p0/` + perfis do Field Designer validados pelo runner. |
| S4_T3 | Fixtures & Parsing | PASS | Fixtures reais por fonte, testes `T3_*` exercitando parsers. |
| S4_T4 | Goldens & Diffs | PASS | Goldens derivados dos fixtures, comparadores `T4_*` sem diffs críticos. |
| S4_T5 | Vault Repetition | PASS | Runner repete ingestões sem duplicatas/perdas; snapshots/diff confirmam idempotência. |
| S4_T6 | Observability & SLOs | PASS | Métricas e health matrix cobrem as 3 Fontes P0; html_market_watch marcado como DEGRADED (latência Explore > alvo) e monitorado. |
| S4_T7 | ORR Pipeline | PASS | `bin/orr_s4_t7_pipeline.sh` roda T0–T6 em sequência, summary único dos scorecards. |

## Principais entregas

1. Registry e Field Designer oficiais para as três Fontes P0, sem segredos versionados.  
2. Fixtures reais, testes de parsing e goldens determinísticos cobrindo os fluxos Fonte→Run→Item.  
3. Vault idempotente sob repetição controlada com snapshots/diffs versionados.  
4. Observabilidade mínima com métricas, health matrix e experimentos SLO (onboarding, detection, run success, evidence completeness, Explore).  
5. ORR pipeline (`bin/orr_s4_t7_pipeline.sh`) que roda T0–T6 e produz summary único, preparando T8.  

## Riscos & pendências

* `html_market_watch` em estado DEGRADED para explore_query_p95_ms (850 ms) — precisa otimização no parser/query antes de escalar.  
* Próxima sprint deve considerar automação de onboarding para novas Fontes P0 e expansão do Explore.  
* Monitorar consumo de storage do Vault ao incluir novas fontes; ajustes finos em `s4_t5_ingest` podem virar serviço real no futuro.  

## Decisão T8 — GO

Todos os gates S4_T0…S4_T7 estão em PASS, com evidências versionadas e riscos registrados. **Decisão: GO** para a Sprint 4, habilitando o Inspectah a operar Fontes P0 reais com Vault idempotente, Explore mínimo e observabilidade monitorada.
