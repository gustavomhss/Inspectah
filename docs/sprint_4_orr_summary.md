# Inspectah — Sprint 4 ORR Summary

## Objetivo da Sprint 4

Levar o Inspectah de experimento de laboratório a ferramenta interna confiável para 3 Fontes P0 reais (`api_market_prices`, `html_market_watch`, `rss_news_minimal`), com Evidence Vault vivo, Explore mínimo seguro e observabilidade séria com SLOs explícitos, tudo protegido por um ORR T0–T8 reproduzível e auditável.

## Estado dos Gates S4_T0…S4_T7

| Gate | Nome | Status | Observações |
| --- | --- | --- | --- |
| S4_T0 | Discovery | PASS | Checklist completo, Fontes P0 definidas, Capítulos 1–4 absorvidos. |
| S4_T1 | Specs & Invariantes | PASS | Modelo de dados + matriz invariantes×gates publicados. |
| S4_T2 | Registry & Field Designer | PASS | YAMLs canônicos em `config/sources/sprint_4/fontes_p0/` + perfis do Field Designer validados pelo runner. |
| S4_T3 | Fixtures & Parsing | PASS | Fixtures reais por fonte e testes `T3_*` exercitando os parsers. |
| S4_T4 | Goldens & Diffs | PASS | Goldens derivados dos fixtures sem diffs críticos em `tests/sprint_4/T4_*`. |
| S4_T5 | Vault Repetition | PASS | Runner repete ingestões sem duplicatas ou perdas, snapshots monitorados. |
| S4_T6 | Observability & SLOs | PASS | Métricas/health matrix cobrem as fontes; `html_market_watch` DEGRADED (latência Explore > alvo) e monitorada. |
| S4_T7 | ORR Pipeline | PASS | `bin/orr_s4_t7_pipeline.sh` roda T0–T6 e produz summary único dos scorecards. |

## Principais entregas

1. Registry + Field Designer oficiais das Fontes P0 sem segredos versionados.  
2. Fixtures reais, goldens determinísticos e comparadores para Fonte→Run→Item.  
3. Evidence Vault idempotente sob repetição controlada com snapshots/diffs versionados.  
4. Observabilidade mínima com métricas, health matrix e experimentos de SLO.  
5. ORR pipeline único (`bin/orr_s4_t7_pipeline.sh`) preparando o GO/NO_GO da S4.  

## Riscos & pendências

* `html_market_watch` marcado como DEGRADED por latência de Explore (p95 0,85s > alvo 0,8s) — precisa tuning na próxima sprint.  
* Planejar onboarding para novas Fontes P0 e expansão do Explore após a S4.  
* Monitorar crescimento do Vault ao adicionar novas fontes; transformar os scripts de repetição em serviço permanente.  

## Decisão T8 — GO

Todos os gates S4_T0…S4_T7 estão em PASS, riscos conhecidos documentados e mitigados. **Decisão final da Sprint 4: GO.**
