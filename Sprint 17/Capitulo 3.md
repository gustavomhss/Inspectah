# Sprint 17 — Capítulo 3 (Refatorado)
## Filemap, Arquitetura de Frontend e Contratos UI↔Backend

### 1. Objetivo deste capítulo

O Capítulo 1 definiu **o que** a UI de consulta precisa ser para o usuário final.  
O Capítulo 2 cravou **como vamos provar** que isso foi entregue (gates T0…T8).  

Este Capítulo 3 responde à pergunta:

> “Como organizamos o código de frontend da Sprint 17 para que a visão do Capítulo 1 e os gates do Capítulo 2 sejam naturais de implementar, testar e manter?”

Aqui, Bret Victor (experiência e interação) e Kent C. Dodds (arquitetura de UI, acessibilidade, testes) atuam em co-liderança para desenhar uma arquitetura que seja ao mesmo tempo:

- simples de entender e navegar;
- clara na separação de responsabilidades;
- alinhada aos contratos do backend;
- preparada para S18–S20 sem antecipar escopo demais.

O resultado final é um **filemap detalhado**, uma **arquitetura de componentes/estados** e uma **camada de contratos UI↔backend** que servem de blueprint para o Capítulo 4 (execução com Codex/time).

---

### 2. Posição do frontend no repositório Inspectah

O frontend da Sprint 17 vive **dentro** do repositório principal do Inspectah, mas isolado em um diretório próprio:

```text
/Users/gustavoschneiter/Documents/Inspectah
├─ bin/
├─ docs/
├─ inspectah/
├─ scripts/
├─ out/
└─ frontend/
   └─ inspectah-ui/
```

Dentro de `frontend/inspectah-ui/` vive o projeto React da S17 (que será evoluído nas S18–S20). Essa escolha garante:

- proximidade com o backend (fácil rodar tudo junto);  
- independência de build (front tem seu próprio pipeline);  
- um único repositório de verdade do Inspectah (monorepo leve).

Stack base assumida para a S17:

- **React + TypeScript** (simplicidade + tipos para contratos de API);
- **Vite** como bundler (rápido, DX boa, integração simples com TS e React);
- **Tailwind CSS** para estilos utilitários e tokens simples de design;
- **React Testing Library + Vitest/Jest** para testes de UI.

Nada impede que S18–S20 adicionem ferramentas (por exemplo, testes E2E), mas a S17 começa enxuta e bem estruturada.

---

### 3. Arquitetura lógica da UI de consulta

A UI da Sprint 17 segue três princípios estruturais, definidos em conjunto pela equipe:

1. **Uma rota principal, vários estados**  
   Em S17 existe essencialmente uma rota pública: a tela de consulta. Não há telas de admin, timeline ou auth. A complexidade vem de **estados** (idle, loading, success, error), não de navegação.

2. **UI como função de estado (state → UI)**  
   A página de consulta é concebida como uma função pura de um estado finito:

   ```ts
   type ConsultationStatus =
     | { kind: "idle" }
     | { kind: "submitting"; question: string }
     | { kind: "success"; question: string; result: ConsultationResponseUi }
     | { kind: "error"; question?: string; message: string };
   ```

   A tela não “adivinha” estados espalhados; tudo é derivado desse tipo central.

3. **Camadas bem definidas**  
   - Camada de **shell** (App, layout, roteamento);
   - Camada de **página de consulta** (coordenadora do fluxo);
   - Camada de **componentes de domínio** (formulário, resposta, risco, evidências, estados vazios/erro);
   - Camada de **API e contratos** (cliente HTTP + tipos do backend);
   - Camada de **observabilidade e erros** (error boundary, logs de eventos).

---

### 4. Filemap detalhado de frontend (S17)

#### 4.1 Raiz do projeto de front

```text
frontend/inspectah-ui/
├─ package.json
├─ tsconfig.json
├─ vite.config.ts
├─ index.html
├─ tailwind.config.cjs
├─ postcss.config.cjs
└─ src/
```

- `package.json`  
  Scripts esperados:
  - `dev` – roda o dev server;
  - `build` – build de produção;
  - `test` – testes de front;
  - `lint` – lints de código.

- `tsconfig.json` – configura TS (paths, strict mode recomendado).
- `vite.config.ts` – entrypoints, plugins (React, TS), possíveis aliases.
- `tailwind.config.cjs` + `postcss.config.cjs` – Tailwind, autoprefixer, etc.
- `index.html` – ponto de entrada HTML da SPA.

Esses arquivos são o alvo principal do gate **S17_T0 (sanity)**.

#### 4.2 Diretório `src/`

Estrutura base:

```text
src/
├─ main.tsx
├─ App.tsx
├─ routes/
│  └─ ConsultationRoute.tsx
├─ pages/
│  └─ ConsultationPage.tsx
├─ components/
│  ├─ layout/
│  │  ├─ AppShell.tsx
│  │  └─ Header.tsx
│  └─ consultation/
│     ├─ ConsultationForm.tsx
│     ├─ ResultContainer.tsx
│     ├─ ResponseSummary.tsx
│     ├─ RiskBadge.tsx
│     ├─ EvidenceList.tsx
│     ├─ EmptyState.tsx
│     └─ ErrorState.tsx
├─ api/
│  ├─ httpClient.ts
│  └─ inspectahClient.ts
├─ types/
│  └─ inspectah.ts
├─ hooks/
│  └─ useConsultation.ts
├─ observability/
│  ├─ ErrorBoundary.tsx
│  └─ logEvents.ts
├─ styles/
│  └─ global.css
└─ __tests__/
   ├─ ConsultationPage.test.tsx
   ├─ ResultContainer.test.tsx
   └─ RiskBadge.test.tsx
```

Essa estrutura foi calibrada para suportar diretamente os gates T1…T7.

---

### 5. Componentes principais e responsabilidades

#### 5.1 `main.tsx`

Responsável por:

- montar a aplicação React na `index.html`;
- envolver a aplicação em providers globais (por exemplo, router, ErrorBoundary, eventual contexto de tema se surgir na S20).

Pseudo-código conceitual:

```tsx
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);
```

Gate associado: T0 (sanity), T6 (error boundary), T7 (CI/build).

#### 5.2 `App.tsx`

Define o shell da aplicação e o roteamento:

- aplica `AppShell`;
- registra rotas usando React Router (ou router mínimo equivalente);
- em S17, apenas a rota de consulta é exposta.

```tsx
export function App() {
  return (
    <AppShell>
      <ConsultationRoute />
    </AppShell>
  );
}
```

Gate associado: T1 (estado de UI visível), T2 (estrutura semântica, header), T4 (flows dourados).

#### 5.3 `routes/ConsultationRoute.tsx`

Rota principal da S17. Encapsula a `ConsultationPage` e define a URL base (ex.: `/`). Em S18–S20, novas rotas serão adicionadas neste diretório.

Responsabilidade: mapear rota → página, sem lógica de domínio.

#### 5.4 `pages/ConsultationPage.tsx`

É o "cérebro visual" da S17. Coordena:

- estado da consulta via `useConsultation`;
- renderização do `ConsultationForm` e do `ResultContainer`;
- integração com `logEvents`.

Em pseudo-código de responsabilidade:

```tsx
export function ConsultationPage() {
  const { status, submitQuestion } = useConsultation();

  return (
    <section aria-labelledby="consulta-heading" className="...">
      <Header />
      <ConsultationForm onSubmit={submitQuestion} status={status} />
      <ResultContainer status={status} />
    </section>
  );
}
```

Gates diretamente ligados: T1 (estados), T2 (UX/acessibilidade), T3 (integração API), T4 (flows), T6 (eventos), T7 (testes).

#### 5.5 `components/layout/AppShell.tsx`

Define a estrutura geral da página:

- header global;
- área central de conteúdo;
- rodapé simples (se necessário).

Deve respeitar boas práticas de layout, responsividade básica (sem exageros, S20 cuida do refinamento) e acessibilidade (landmarks, headings).

#### 5.6 `components/layout/Header.tsx`

Exibe:

- nome/identidade básica do Inspectah;
- frase curta explicando o que o sistema faz (“verificar informações, mostrar risco e evidências”).

É importante para T2 (UX inicial) e para demos de T4.

#### 5.7 `components/consultation/ConsultationForm.tsx`

Responsável pelo formulário de pergunta:

- input de texto com label e descrição;  
- botão de submit;  
- mensagens de ajuda (ex.: exemplos de perguntas).

Recebe via props:

- `status: ConsultationStatus` (para saber se está `submitting` e desativar inputs);  
- `onSubmit(question: string)`.

Gates: T1 (transição de estados), T2 (acessibilidade, UX), T3 (integração, quando conectado ao hook).

#### 5.8 `components/consultation/ResultContainer.tsx`

Recebe o `status` e decide **o que** renderizar:

- `idle` → `EmptyState`;
- `submitting` → skeleton/loading;
- `success` → `ResponseSummary` + `RiskBadge` + `EvidenceList`;
- `error` → `ErrorState`.

Ele é a encarnação visual da máquina de estados. Qualquer mudança de estado deve refletir-se aqui de forma óbvia.

Gates: T1, T2, T3, T4 (flows), T5 (performance de renderização), T7 (testes unitários).

#### 5.9 `ResponseSummary.tsx`

Mostra a resposta consolidada em texto, com:

- título curto (por exemplo: "Resposta consolidada");
- parágrafo ou blocos de texto que venham da API.

Focado em legibilidade. Sem lógica complexa.

#### 5.10 `RiskBadge.tsx`

Responsável por:

- mapear `risk_level` / `risk_score` para cor, ícone e texto;
- exibir rótulos como "Risco baixo", "Risco alto", "Risco incerto".

Esta é a peça central do S17 para comunicar risco.

Deve usar tokens padronizados, por exemplo em Tailwind:

- `bg-risk-low`, `bg-risk-medium`, `bg-risk-high`, `bg-risk-unknown` (configurados no tema);
- texto contrastante e ícones simples (ex.: check, alerta, interrogação).

Gates: T2 (acessibilidade, contraste), T3 (integração), T4 (flows), T5 (render), T6 (logar se risco alto), T7 (testes).

#### 5.11 `EvidenceList.tsx`

Mostra uma lista de evidências principais:

- fonte (nome);
- tipo (ex.: notícia, banco de dados, documento oficial);
- descrição curta;
- link opcional.

Por padrão, a S17 pode exibir uma quantidade limitada (por exemplo, 3–5 evidências) para manter a tela limpa. S19 tratará de detalhes mais profundos.

#### 5.12 `EmptyState.tsx` e `ErrorState.tsx`

- `EmptyState`  
  Tela amigável quando nenhuma consulta foi feita ou não há dados suficientes. Deve indicar, por exemplo, “Faça uma pergunta para começarmos” e, em caso de falta de dados, “Não temos informação suficiente para responder com confiança” com orientação clara.

- `ErrorState`  
  Exibe mensagens amigáveis em caso de:
  - falha de rede;  
  - erro interno do backend;  
  - erro inesperado de contrato.

  Nunca exibe stacktrace ou termos técnicos.

Ambos são críticos para T2, T3 e T4.

---

### 6. API, contratos e tipos compartilhados

#### 6.1 `api/httpClient.ts`

Wrapper fino sobre `fetch` (ou similar) com responsabilidade de:

- configurar URL base da API;
- lidar com detalhes genéricos de requisições (headers, JSON, timeouts simples);
- mapear erros genéricos (4xx/5xx) para erros JS tratados.

Mantido o mais simples possível para não atrapalhar debugging.

#### 6.2 `api/inspectahClient.ts`

Ponto de entrada para o backend do Inspectah, com foco em consulta:

- `consultTruth(request: ConsultationRequest): Promise<ConsultationResponseRaw>`.

Aqui acontecem transformações iniciais:

- adequar o formato do payload à API real (ex.: `question`, `language`, `context`);
- traduzir status de erro HTTP em exceções coerentes para o hook.

#### 6.3 `types/inspectah.ts`

Define a contratualização de request/response, com **duas camadas**:

- `ConsultationRequest` – tipo usado pelo front ao chamar o backend;
- `ConsultationResponseRaw` – shape bruto que vem da API;
- `ConsultationResponseUi` – shape já adaptado para UI (por exemplo, normalizando nomes de campos).

Exemplo conceitual:

```ts
type RiskLevel = "low" | "medium" | "high" | "unknown";

interface EvidenceItemUi {
  id: string;
  sourceName: string;
  sourceType: string;
  description: string;
  link?: string;
}

interface ConsultationResponseUi {
  answer: string;
  riskLevel: RiskLevel;
  riskScore?: number;
  riskFlags?: string[];
  evidences: EvidenceItemUi[];
  requestId?: string;
  generatedAt?: string;
}
```

Essa separação dá segurança à UI e permite adaptar o backend sem quebrar o front a cada mudança interna.

Gates envolvidos: T1 (contratos e estados), T3 (integração), T4 (fixtures para flows), T7 (testes tipados).

---

### 7. Hooks e máquina de estados

#### 7.1 `hooks/useConsultation.ts`

Este hook encapsula toda a lógica de:

- estado da consulta;
- submissão;
- tratamento de respostas e erros;
- integração com `logEvents`.

Interface conceitual:

```ts
interface UseConsultation {
  status: ConsultationStatus;
  submitQuestion: (question: string) => Promise<void>;
}

export function useConsultation(): UseConsultation {
  // implementação baseada na máquina de estados
}
```

Dentro dele:

1. `submitQuestion`:
   - atualiza `status` para `submitting`;
   - chama `logConsultationStarted` com a pergunta (sem dados sensíveis extras);
   - aciona `inspectahClient.consultTruth`;
   - mapeia resposta para `ConsultationResponseUi`;
   - em caso de sucesso, atualiza `status` para `success` e chama `logConsultationSuccess` (incluindo `requestId` se existir);
   - em caso de erro, atualiza `status` para `error` com mensagem amigável e chama `logConsultationError`.

2. Tratamento de incerteza (quando backend retornar risco alto/unknown) pode ser modelado ainda como `success`, mas com `riskLevel` apropriado, deixando a UI comunicar isso ao usuário.

Este hook é o principal alvo de testes em T1, T3, T4 e T6.

---

### 8. Observabilidade e erros

#### 8.1 `observability/ErrorBoundary.tsx`

Componente que envolve o `App` (e/ou a `ConsultationPage`) e captura exceções de renderização, exibindo fallback amigável e registrando erro.

Responsabilidades:

- exibir mensagem genérica de falha (“Algo deu errado, tente novamente”);
- permitir recarregar a página ou tentar nova consulta;
- chamar função de log (`logUiError`) com detalhes limitados (sem payload sensível).

#### 8.2 `observability/logEvents.ts`

Define conjunto mínimo de funções de log, por exemplo:

- `logConsultationStarted(questionSnippet: string)`;  
- `logConsultationSuccess(requestId?: string, riskLevel?: RiskLevel)`;  
- `logConsultationError(message: string)`;  
- `logUiError(error: Error, info?: unknown)`.

Na S17, essas funções podem simplesmente escrever em `console` ou mandar para um endpoint simples de log local. O importante é existir **um lugar único** para instrumentar eventos de UI, alinhado ao gate T6.

---

### 9. Estilos, tokens e design mínimo

#### 9.1 `styles/global.css`

Inclui:

- imports de Tailwind (`@tailwind base; @tailwind components; @tailwind utilities;`);
- pequenos ajustes globais (fontes padrão, altura de linha, background da página);
- resets leves se necessário.

#### 9.2 Tokens de risco em Tailwind

No `tailwind.config.cjs`, são definidos tokens mínimos para cores de risco, por exemplo:

```js
theme: {
  extend: {
    colors: {
      risk: {
        low: "#0f766e",      // verde sóbrio
        medium: "#ca8a04",   // amarelo/âmbar
        high: "#b91c1c",     // vermelho forte
        unknown: "#4b5563",  // cinza neutro
      },
    },
  },
}
```

O `RiskBadge` consome esses tokens, garantindo uma linguagem visual consistente para riscos em toda a app (S17 e além).

Responsabilidade de T2 (acessibilidade/contraste) e T5 (performance de renderização simples).

---

### 10. Testes e integração com os gates

#### 10.1 Diretório `__tests__/`

Testes iniciais da S17, vinculados diretamente aos gates:

- `ConsultationPage.test.tsx`  
  - cobre fluxo principal de envio de consulta (com mocks de API);
  - verifica estados idle/loading/success/error.

- `ResultContainer.test.tsx`  
  - garante que cada `ConsultationStatus` rende o componente correto.

- `RiskBadge.test.tsx`  
  - mapeia corretamente os níveis de risco para classes CSS e textos.

Eventualmente, podem existir testes adicionais para `ConsultationForm`, `EmptyState`, `ErrorState`, etc., conforme a S17 evoluir.

#### 10.2 Relação com gates

- T0 – garante que os testes rodam (sanity).
- T1 – foca em estados e contratos (tests de `ResultContainer`, `useConsultation`).
- T2 – testa UX básica (labels, textos, estados vazios) via assertions em DOM.
- T3 – integra com mocks do backend (via MSW ou similar) para simular API real.
- T4 – usa fixtures dos casos canônicos como base de expectativas.
- T7 – CI roda todos esses testes em ambiente limpo.

---

### 11. Scripts `bin/` e conexão com a S17

Na raiz do repo, os scripts de gate da S17 assumem a arquitetura descrita aqui.

Exemplo conceitual (nomes exatos serão definidos no Capítulo 4):

- `bin/s17_t0_sanity.sh`  
  - entra em `frontend/inspectah-ui/`;  
  - roda `npm install`, `npm run lint`, `npm run test`, `npm run build`;  
  - grava scorecard T0.

- `bin/s17_t1_contracts_and_states.sh`  
  - roda suite de testes focada em tipos e estados (pode ser subset de tests ou tags);
  - valida presença de tipos em `types/inspectah.ts`.

- `bin/s17_t2_ux_and_accessibility.sh`  
  - dispara testes focados em empty states + checklist manual salvo em `out/evidence`.

- `bin/s17_t3_api_integration.sh`  
  - roda testes com backend stub/real.

- `bin/s17_t4_golden_flows.sh`  
  - garante que fixtures de casos canônicos renderizam como esperado.

- `bin/s17_t5_performance_and_bundle.sh`  
  - mede bundle + tempos simples de resposta.

- `bin/s17_t6_frontend_observability.sh`  
  - força erro e verifica logs.

- `bin/s17_t7_ci_and_repro.sh`  
  - orquestra os anteriores em modo “dev local”.

- `bin/s17_t8_go_no_go.sh`  
  - agrega scorecards;  
  - escreve scorecard final T8.

Essa camada de scripts garante que o filemap não é só “organização bonita”, mas base real para gates e ORR.

---

### 12. Conclusão: prontidão para execução (Capítulo 4)

Com este Capítulo 3, a Sprint 17 passa a ter:

- um **lugar claro** no repo para o frontend (`frontend/inspectah-ui/`);
- uma **arquitetura de componentes, hooks e contratos** alinhada à visão Bret + Kent;
- uma **máquina de estados explícita** para a UI de consulta;
- um **filemap detalhado** que amarra o front aos gates T0…T8 e aos scripts `bin/s17_*`.

O Capítulo 4 vai pegar esse blueprint e transformá-lo em um plano concreto de execução:

- quais arquivos criar/modificar e em que ordem;
- quais comandos o Codex e o time devem rodar;
- como gerar scorecards e evidências em cada gate.

A partir daqui, não há mais ambiguidade sobre “onde vai o código de front da S17” ou “como o front fala com o backend”. Tudo isso está definido — falta apenas **executar** com o mesmo padrão de excelência dos capítulos anteriores.

