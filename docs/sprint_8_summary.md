# Sprint 8 — Inspectah (Resumo Executivo)

## Objetivo
Colocar em produção o esqueleto funcional do Inspectah: Admin v0 multi‑fonte, User v0 em linguagem natural e o pipeline Inspectah → Evidências → GPT → Resposta, operando apenas com dados internos e mantendo rastreabilidade total para evoluir rumo a Truth‑DB, blockchain e comunidade nas próximas sprints.

## Estado dos Gates
| Gate | Descrição resumida | Status |
|------|--------------------|--------|
| S8_T0_scope | Docs Cap. 1–4 e escopo alinhado | PASS |
| S8_T1_static | Qualidade estática / compileall / secret scan | PASS |
| S8_T2_unit_contracts | Testes unitários e contratos do core | PASS |
| S8_T3_property | Casos de borda / propriedades (dados insuficientes, fora de escopo) | PASS |
| S8_T4_golden_flows | 3 demos oficiais comparadas com goldens | PASS |
| S8_T5_perf | Métricas de latência/tamanho por cenário | PASS |
| S8_T6_logs_and_evidence | Auditoria QueryLog ↔ Bundle ↔ Resposta | PASS |
| S8_T7_ci | `bin/s8_ci.sh` rodando via workflow `.github/workflows/s8-ci.yml` | PASS |
| S8_T8_go_no_go | Consolidação dos scorecards → **GO** | PASS |

## Entregáveis Principais
- **Admin v0** (`app/admin/`): cadastro de fontes por tipo (`preco`, `fato`), ingestão baseada em fixtures oficiais (`tests/fixtures/s8_*`), status mínimo de ingestão e seed automático (`ensure_default_sources`).
- **User v0** (`app/user/`): endpoint programático `post_query` que chama o pipeline completo e devolve resposta humanizada, resumo estruturado, confidence flags e links para evidências.
- **Core Sprint 8** (`app/core/`): modelos, storage file‑based em `out/evidence/s8_*`, parser determinístico, busca multi‑fonte, builder de bundles com meta `num_sources >= 2`, pipeline integrado ao GPT e persistência de QueryLog + EvidenceBundle + UserResponse.
- **GPT Engine** (`app/gpt_client/`): prompts “bundle-only” e cliente determinístico que compara 2+ fontes, aponta convergências/divergências, produz resumo JSON + confidence.
- **Fixtures e Goldens**: dados multi‑fonte para os três cenários oficiais (preço médio, comparação simples, checagem factual) e snapshots em `tests/goldens/*.json` exercitados em `tests/s8_t4_golden_flows/`.
- **Gates & Automação**: scripts `bin/s8_t{0..8}_*.sh`, orquestrador `bin/s8_ci.sh`, workflow `.github/workflows/s8-ci.yml` e scorecards/evidências em `out/` para auditoria.

## Limitações & Próximos Passos
1. **Cobertura de fontes**: Sprint 8 trabalha apenas com tipos `preco` e `fato` usando fixtures locais. Próximas sprints devem ampliar tipos (indicadores, métricas setoriais) e integrar conectores reais.
2. **Observabilidade contínua**: Logs e bundles já existem em arquivo, mas ainda não há pipeline para dashboards ou Truth‑DB. Sprint 9+ deve transformar esses registros em entidades versionadas (blocos/fatos) e acoplar a futuras âncoras blockchain.
3. **Interface humana**: Admin/User hoje são camadas programáticas. Sprint 9 deve evoluir para UI utilizável (console, painéis) e fluxos de autenticação.
4. **Performance e escalabilidade**: T5 mede latência local; limites precisam ser revisitados quando a ingestão crescer e o GPT migrar para modelos hospedados/externos. Monitoramento em produção será essencial.
5. **Integração com roadmap Q2/Q3**: As saídas de S8 alimentam as frentes de Truth‑DB, guardião de blocos e contestação (S10–S12). Documentar claramente esses artefatos no handoff inicial da próxima sprint.

Com os gates T0–T8 em PASS e decisão **GO**, a Sprint 8 entrega a base funcional para que o time evolua o Inspectah nas sprints seguintes.
