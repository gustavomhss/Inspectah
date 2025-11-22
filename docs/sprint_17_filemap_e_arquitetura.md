# Sprint 17 — Filemap e Arquitetura de Front

## Estrutura do projeto
```
frontend/inspectah-ui/
├─ package.json (scripts dev/build/test/lint)
├─ tsconfig.json / tsconfig.node.json
├─ vite.config.ts (React + TS, alias @ → src)
├─ tailwind.config.cjs / postcss.config.cjs
├─ index.html
└─ src/
   ├─ main.tsx (monta App + ErrorBoundary)
   ├─ App.tsx (router + AppShell)
   ├─ routes/ConsultationRoute.tsx
   ├─ pages/ConsultationPage.tsx
   ├─ components/
   │  ├─ layout/AppShell.tsx, Header.tsx
   │  └─ consultation/
   │     ├─ ConsultationForm.tsx
   │     ├─ ResultContainer.tsx
   │     ├─ ResponseSummary.tsx
   │     ├─ RiskBadge.tsx
   │     ├─ EvidenceList.tsx
   │     ├─ EmptyState.tsx
   │     └─ ErrorState.tsx
   ├─ api/httpClient.ts, api/inspectahClient.ts
   ├─ types/inspectah.ts
   ├─ hooks/useConsultation.ts
   ├─ observability/ErrorBoundary.tsx, logEvents.ts
   ├─ styles/global.css (Tailwind + tema)
   ├─ __tests__/ (ConsultationPage, ResultContainer, RiskBadge + mocks MSW)
   └─ setupTests.ts (RTL, jest-dom, MSW server)
```

## Máquina de estados (UI)
Tipo discriminado em `types/inspectah.ts`:
- `idle` — sem consulta.
- `submitting` — consulta em andamento (mantém pergunta).
- `success` — resposta consolidada + risco + evidências.
- `error` — mensagem amigável e retry.
`ResultContainer` é a função visual de `status → UI` (idle → EmptyState, submitting → skeleton, success → summary/risk/evidence, error → ErrorState).

## Contratos UI↔API
`ConsultationRequest` e `ConsultationResponseRaw` vivem em `types/inspectah.ts`. `inspectahClient.consultTruth`:
- envia `{ question, locale?, context? }` para `VITE_INSPECTAH_CONSULT_PATH` (default `/api/consultation`).
- trata HTTP/network errors via `HttpError` (httpClient).
- converte `Raw` → `ConsultationResponseUi` (normaliza `risk_level`, `risk_score`, evidências e metadados como `request_id`/`generated_at`).

## Componentes chave
- `ConsultationForm` — formulário acessível, exemplo de perguntas, Enter/Click, desabilita em submitting.
- `ResponseSummary` — texto da resposta + flags de risco + timestamp.
- `RiskBadge` — mapeia `RiskLevel` para cores do tema (`risk.low/medium/high/unknown`).
- `EvidenceList` — lista recortada de evidências (fonte, tipo, descrição, link opcional).
- `EmptyState`/`ErrorState` — mensagens claras para vazio/erro.
- `AppShell`/`Header` — shell com contexto do produto (Inspectah, Sprint 17).

## Observabilidade
- `ErrorBoundary` cobre a aplicação e mostra fallback com botão de retry, logando via `logUiError`.
- `logEvents.ts` define funções centralizadas (`logConsultationStarted`, `logConsultationSuccess`, `logConsultationError`, `logUiError`) sem vazar payload sensível (logs usam trechos da pergunta e metadados básicos).

## Estilos e tokens
- Tailwind com tema estendido em `tailwind.config.cjs` (cores de risco, fontes Manrope, sombras).
- `global.css` aplica fundo com gradientes leves e focus visível.

## Testes
- `ConsultationPage.test.tsx` (RTL + MSW) cobre sucesso, risco alto/unknown, erros 4xx/5xx, falha de rede e evidência vazia.
- `ResultContainer.test.tsx` valida renderização de cada estado da máquina.
- `RiskBadge.test.tsx` garante rotulagem e score.
- MSW configurado em `src/__tests__/mocks` e ativado em `setupTests.ts`.

## Scripts de gates
- Scripts `bin/s17_t0...t7.sh` rodam lint/test/build, validação de estados, UX, integração API, golden flows, bundle e observabilidade.
- `bin/s17_all_gates.sh` orquestra T0–T8.
