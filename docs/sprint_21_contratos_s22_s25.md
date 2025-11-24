# Sprint 21 — Contratos com S22–S25

Este documento fixa os contratos entre o Console de Fontes (S21) e as próximas sprints. Cada seção lista garantias entregues por S21, expectativas em relação ao squad seguinte e limitações conhecidas.

## 1. Com Squad 2 / Sprint 22 (Ingestão 2.0)
- **Garantias S21**:
  - Campos operacionais: `endpoint/url_base`, `auth_type/auth_config`, `request_params`, `headers`, `frequency`, `timeout_ms`, `retry_policy`, `parsing_config`.
  - Estado controla execução: somente `ACTIVE` e `TESTING` podem ser agendados; `SUSPECT/UNDER_REVIEW` opcionais com rate limit; `DISABLED_*` bloqueiam ingestão.
  - Redundância: `redundancy_group` e `redundancy_role` definem agrupamentos para coleta paralela.
  - Health-check schema: `SourceHealthCheck` com `status`, `latency_ms`, `error`, `meta`.
- **Expectativas de S22**:
  - Scheduler lê `frequency` e estados para decidir jobs.
  - Workers respeitam `timeout_ms/retry_policy`.
  - Reportam health-checks e resultados populando `SourceHealthCheck`.
- **Limitações**:
  - Sem filas/streaming nativo; ingestão é polling simples.
  - Sem atualização automática de schema de parsing (apenas hints armazenados).

## 2. Com Squad 3 / Sprint 23 (Interpretação e Classificação)
- **Garantias S21**:
  - Ontologia de tipos (`news_rss`, `gossip_feed`, `sports_api`, `weather_api`, `gov_record`, `legislation`, `science_dataset`, `static_dataset`).
  - Metadados por tipo: temas, info_types, categories, parsing hints.
  - Flags de confiabilidade (`trust_severity`, `conflict_flags`).
- **Expectativas de S23**:
  - Agentes consomem `type` e `parsing_config` para interpretar payloads.
  - Podem registrar observações no `meta` da fonte ou abrir contestação via API.
- **Limitações**:
  - Não há pipelines de ML/LLM ligados diretamente; somente metadados/hints.

## 3. Com Squad 4 / Sprint 24 (Debunker v0 + Humano-no-loop)
- **Garantias S21**:
  - Campos de conflito/contestação (`conflict_flags`, `conflict_with_sources`, `has_open_contestation`, `evidence_refs`).
  - Histórico de estados registra eventos de conflito e contestação.
  - Endpoints de admin permitem abrir/fechar contestação e marcar suspeita.
- **Expectativas de S24**:
  - Debunker pode acionar transições `UNDER_REVIEW`, `SUSPECT`, `DISABLED_TEMP/PERM`.
  - Pode anexar evidências via `evidence_refs` e `SourceStateHistory`.
- **Limitações**:
  - Não há workflow humano completo; apenas hooks básicos e flags.

## 4. Com Squad 5 / Sprint 25 (Governança, Verdade/Fato & promoção)
- **Garantias S21**:
  - Proveniência de fonte: audit fields, estado atual e histórico.
  - Redundância e grupos: base para política de promoção/rebaixamento de fontes.
  - Temas e info_types mapeados para casos/timelines.
- **Expectativas de S25**:
  - Governança usa histórico de estado e conflitos para decisões de confiança.
  - Pode consultar contestação aberta e health-checks para calibrar políticas.
- **Limitações**:
  - Sem reputação comunitária nem pontuação pública; somente flags internas.

## 5. Matriz de riscos e alinhamento
- Risco de campo faltante: mitigado por validações em schemas e scripts de gate.
- Risco de desvio de contrato: cada squad deve registrar revisões em `out/evidence/S21_G5_contratos/`.
- Risco de performance: ingestão inicial baseada em polling simples; squads futuros podem otimizar sem quebrar contrato semântico.
