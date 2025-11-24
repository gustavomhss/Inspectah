# Sprint 21 — Ganchos para Debunker, Contestação e Redundância

Este documento detalha os campos e processos que conectam o Console de Fontes ao Debunker (Sprint 24), à contestação manual e à redundância tripla. Deve ser refletido no modelo (`models.py`), nos serviços e nos scripts de gate S21_G4.

## 1. Objetivos
- Tornar explícito onde conflitos e contestação são registrados.
- Permitir que o Debunker abra/feche contestação e marque conflitos entre fontes.
- Preservar rastreabilidade de decisões sobre confiabilidade e desativação.

## 2. Campos adicionados em Source
- `conflict_flags` (lista/JSON): tipos de conflito detectados (divergência, ausência, atraso, manipulação suspeita).
- `conflict_with_sources` (lista de ids): outras fontes envolvidas.
- `has_open_contestation` (bool): existe contestação ativa.
- `last_conflict_at` (datetime): último conflito registrado.
- `evidence_refs` (JSON): ids/links para evidências ou blocos relevantes.
- `redundancy_group` + `redundancy_role`: agrupamento para redundância tripla (primária/secundária/sentinela).
- `trust_severity` (enum: `info`, `warning`, `critical`): severidade atual atribuída pelo Debunker ou revisão.

## 3. Campos em SourceStateHistory
- `conflict_flag` (bool) e `conflict_types` (lista).
- `conflict_with_sources` (lista).
- `contestations` (JSON):
  - `opened_by`, `opened_at`
  - `status` (`open`, `under_review`, `resolved`, `rejected`)
  - `resolved_by`, `resolved_at`
  - `notes`
- `evidence_refs` (JSON) associados à transição.

## 4. Eventos (opcional)
- `SourceEvent` emitido nas transições relevantes:
  - `source.created`, `source.state_changed`, `source.healthcheck.recorded`
  - `source.conflict.detected`, `source.contestation.opened`, `source.contestation.resolved`
- Eventos carregam payload com ids de fonte, estados, severidade e evidências.

## 5. Fluxos com Debunker
- Debunker pode:
  - Marcar conflito → transição para `UNDER_REVIEW` ou `SUSPECT`.
  - Abrir contestação → `has_open_contestation = true`, histórico registrado.
  - Sugerir desativação → transição para `DISABLED_TEMP` ou `DISABLED_PERM`.
- UI/Admin devem visualizar conflitos e contestação ativos.

## 6. Redundância tripla e health-checks
- `redundancy_group` identifica fontes que cobrem o mesmo domínio.
- Health-check pode comparar primária x secundária x sentinela:
  - Divergência dispara `conflict_flags`.
  - Sentinela pode marcar primária como SUSPECT se inconsistente.

## 7. Persistência e API
- DTOs de leitura incluem flags de conflito/contestação e último evento relevante.
- DTOs de escrita permitem abrir/fechar contestação com campos mínimos (`opened_by`, `notes`).
- Endpoints de admin devem expor rota para abrir/fechar contestação e para registrar conflito (mesmo que proxy para Debunker v0).

## 8. Evidências e gates
- S21_G4 requer comprovação de:
  - Campos acima presentes no modelo e ciclo de vida.
  - Documento atualizado (este arquivo) referenciado em migrations e serviços.
  - Evidence em `out/evidence/S21_G4_ganchos_debunker/` com snapshots/diffs.
