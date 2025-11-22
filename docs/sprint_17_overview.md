# Sprint 17 — Overview

## Objetivo
Entregar a primeira UI de consulta do Inspectah: uma tela única onde qualquer pessoa pergunta em linguagem natural, recebe resposta consolidada, vê o nível de risco e um recorte das evidências principais. A sprint não inclui admin, timeline ou features além do fluxo de consulta.

## Stack e local de código
- Projeto: `frontend/inspectah-ui/`
- Stack: React + TypeScript, Vite, Tailwind CSS, Vitest + React Testing Library, MSW para mocks.
- Alias: `@` aponta para `src/` via `vite.config.ts`.

## Fluxo principal da UI
- Estado inicial (idle) com orientação de uso.
- Submissão → estado `submitting` com loading.
- Resposta → estado `success` exibindo `ResponseSummary`, `RiskBadge`, `EvidenceList`.
- Falha → estado `error` com mensagem amigável e opção de tentar novamente.

## Como rodar localmente
```bash
cd /Users/gustavoschneiter/Documents/Inspectah/frontend/inspectah-ui
npm ci
npm run dev   # dev server
npm run test  # testes de UI/integracao
npm run build # bundle de produção
npm run lint  # lint com ESLint flat config
```

## Gates da Sprint 17
Scripts em `bin/` geram scorecards em `out/scorecards/` e evidências em `out/evidence/`:
- `bin/s17_t0_sanity.sh` — sanity de ambiente (lint/test/build).
- `bin/s17_t1_contracts_and_states.sh` — máquina de estados + contratos UI↔API.
- `bin/s17_t2_ux_and_accessibility.sh` — UX mínima e acessibilidade básica.
- `bin/s17_t3_api_integration.sh` — integração UI↔API (sucesso/erro/risco).
- `bin/s17_t4_golden_flows.sh` — casos canônicos (baixo, alto, incerto).
- `bin/s17_t5_performance_and_bundle.sh` — build e tamanho de bundle.
- `bin/s17_t6_frontend_observability.sh` — error boundary + logs de eventos.
- `bin/s17_t7_ci_and_repro.sh` — checks reprodutíveis + workflows de CI.
- `bin/s17_t8_go_no_go.sh` — agregador e decisão final.
- `bin/s17_all_gates.sh` — orquestrador T0–T8.

## CI
Workflows adicionados em `.ci/`:
- `.ci/sprint_17_gates.yml` roda T0–T7 em PR/main.
- `.ci/sprint_17_nightly.yml` roda subset diário (T1–T4, T6).

## Alinhamento com S15/S16
A UI consome o endpoint de consulta do Inspectah via `inspectahClient.consultTruth`, converte respostas brutas em `ConsultationResponseUi` e não expõe detalhes internos do Debunker/Truth-DB. Logs respeitam privacidade e não revelam payloads sensíveis.
