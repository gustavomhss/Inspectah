# Sprint 21 — Contratos com S22–S25

Este documento fixa os contratos entre o Console de Fontes (S21) e as próximas sprints. Cada seção lista garantias entregues por S21, expectativas em relação ao squad seguinte e limitações conhecidas.

## 1. Com Squad 2 / Sprint 22 (Ingestão 2.0)
- **Garantias S21**:
  - Campos operacionais consolidados no modelo/DB: `endpoint/url_base`, `auth_type/auth_config`, `request_params`, `headers`, `frequency`, `timeout_ms`, `retry_policy`, `parsing_config`, `redundancy_group/role`.
  - Estados controlam execução: `ACTIVE` e `TESTING` liberam coleta; `SUSPECT/UNDER_REVIEW` podem ser agendados com rate limit; `DISABLED_*` bloqueiam.
  - Health-check: tabela `source_health_checks` com `status` (`OK/DEGRADED/FAIL`), `latency_ms`, `error`, `meta`.
  - Seeds disponíveis para cenários de teste com endpoints `mock://` (OK/DEGRADED/FAIL).
- **Expectativas de S22**:
  - Scheduler lê `frequency` + `state` para agenda.
  - Workers respeitam `timeout_ms/retry_policy` e registram health-checks via API/serviço.
  - Ingestão pode confiar que configs mínimas estão validadas pelo serviço.
- **Limitações**:
  - Sem filas/streaming; polling simples.
  - Sem refresh automático de parsing; apenas hints armazenados.

## 2. Com Squad 3 / Sprint 23 (Interpretação e Classificação)
- **Garantias S21**:
  - Ontologia fixa da Fase 1 (tipos em `docs/sprint_21_ontologia_fontes.md`) implementada em models/seeds.
  - Metadados: `themes`, `info_types`, `parsing_config`, `category`.
  - Flags de confiança: `trust_severity`, `conflict_flags`, `state`/`state_history`.
- **Expectativas de S23**:
  - Agentes usam `type` + `parsing_config` para interpretar payloads.
  - Podem anotar observações em `meta` ou abrir contestação via API (ganchos prontos).
- **Limitações**:
  - Sem pipeline de interpretação; apenas hooks e metadados.

## 3. Com Squad 4 / Sprint 24 (Debunker v0 + Humano-no-loop)
- **Garantias S21**:
  - Campos e histórico para conflito/contestação: `conflict_flags`, `conflict_with_sources`, `has_open_contestation`, `evidence_refs` em Source/StateHistory.
  - API permite mudar estado para `UNDER_REVIEW`, `SUSPECT`, `DISABLED_*`.
- **Expectativas de S24**:
  - Debunker pode abrir contestação (marcar flags/estado) e anexar evidências via `evidence_refs`.
  - Pode registrar conflitos entre fontes e escalar para revisão.
- **Limitações**:
  - Workflow humano simplificado; apenas flags e mudanças de estado.

## 4. Com Squad 5 / Sprint 25 (Governança, Verdade/Fato & promoção)
- **Garantias S21**:
  - Proveniência e auditoria completas (created/updated, state_history, healthchecks).
  - Redundância definida (`redundancy_group/role`) para políticas de promoção/rebaixamento.
  - Temas/info_types mapeados e disponíveis na API.
- **Expectativas de S25**:
  - Governança consulta estados e conflitos para decisões de confiança e promoção de verdades/fatos.
  - Pode ler contestação aberta e saúde recente para políticas.
- **Limitações**:
  - Sem reputação comunitária ou pontuação pública; apenas flags internas.

## 5. Matriz de riscos e alinhamento
- Risco de campo faltante: mitigado por validações em schemas e scripts de gate.
- Risco de desvio de contrato: cada squad deve registrar revisões em `out/evidence/S21_G5_contratos/`.
- Risco de performance: ingestão inicial baseada em polling simples; squads futuros podem otimizar sem quebrar contrato semântico.
