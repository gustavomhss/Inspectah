# Sprint 17 — Capítulo 4 (Refatorado)
## Plano de Execução, Rotina Operacional e Amarração com Gates

### 1. Papel deste capítulo na Sprint 17

Os três primeiros capítulos da Sprint 17 respondem a:

- **Capítulo 1** – visão e escopo da UI de consulta (o que o usuário final deve sentir e conseguir fazer);
- **Capítulo 2** – matriz de **gates T0…T8** (como provamos, de forma objetiva, que a UI está pronta);
- **Capítulo 3** – **filemap e arquitetura** do frontend (onde entra cada peça de código e como ela se organiza).

Este **Capítulo 4** é o plano de execução:

> “Exatamente o que fazer, em que ordem, com quais arquivos, comandos e checks, para entregar a Sprint 17 em estado GO/GO_WITH_RESTRICTIONS, sem improviso.”

Ele serve simultaneamente para:

- o time humano (PO, front, back, QA) saber **como conduzir a sprint**;
- o agente de código saber **que arquivos criar/modificar e como amarrar tudo aos gates e evidências**.

Capítulo 4 não é script, nem prompt. É o **runbook oficial** da S17.

---

### 2. Contexto operacional e pré-requisitos

**Repositório principal**

- Caminho local: `/Users/gustavoschneiter/Documents/Inspectah`
- Estrutura relevante:
  - `bin/` – scripts de gates e orquestração das sprints;
  - `docs/` – documentação (overview, filemap, ORR, addenda);
  - `inspectah/` – núcleo do backend, Debunker, Comitês, Âncoras (S15/S16);
  - `scripts/` – scripts auxiliares Python para gates e evidências;
  - `out/` – scorecards e evidências por gate (S15, S16 e, agora, S17);
  - `frontend/inspectah-ui/` – projeto de frontend da S17 (novo).

**Dependências de sprints anteriores**

A Sprint 17 assume como baseline:

- **S15** – Debunker v1, Comitês V1/V2/V3, Âncoras e comandos com anti-canetada instalados e validados;
- **S16** – Threat Model, hardening de risco/anti-canetada, falhas simuladas de chain e GO_WITH_RESTRICTIONS documentado.

Antes de estabilizar a S17, é saudável garantir que:

- `PYTHONPATH=. bin/s15_all_gates.sh` roda verde;
- `PYTHONPATH=. bin/s16_all_gates.sh` roda verde (ou com restrições já documentadas em T8).

**Pré-requisitos de ambiente**

- Node.js instalado em versão suportada pela stack de front;
- ferramenta de pacote (npm/pnpm/yarn) escolhida e padronizada;
- Python e dependências do backend já instalados (como definido nas sprints anteriores).

---

### 3. Macro-estratégia da Sprint 17 em fases

A execução da S17 é dividida em quatro fases, cada uma vinculada a um subconjunto de gates.

| Fase | Foco principal                                      | Gates-alvo            |
|------|-----------------------------------------------------|-----------------------|
| 1    | Preparar terreno de frontend (projeto, build, teste)| T0, T7 (base)         |
| 2    | Estados, contratos e integração API                 | T1, T3                |
| 3    | UI/UX completa, golden flows e performance          | T2, T4, T5            |
| 4    | Observabilidade, CI completo, orquestração e ORR    | T6, T7 (full), T8     |

Cada fase produz artefatos específicos (código, scripts, docs, scorecards) e só deve ser considerada “pronta” quando os gates-alvo estiverem verdes.

---

### 4. Fase 1 — Preparar o terreno (T0 + base de T7)

**Objetivo:** criar o projeto `frontend/inspectah-ui/`, garantir que ele builda e testa em ambiente limpo e amarrá-lo a um T0 executável.

#### 4.1 Passos de criação do projeto

1. **Criar diretório e scaffold**
   - Dentro de `/Users/gustavoschneiter/Documents/Inspectah`, criar a pasta `frontend/inspectah-ui/`.
   - Inicializar projeto com Vite + React + TypeScript.
   - Adicionar Tailwind (com `tailwind.config.cjs`, `postcss.config.cjs`) e `src/styles/global.css`.

2. **Configurar scripts do `package.json`**
   - `dev` – dev server local;
   - `build` – build de produção;
   - `test` – testes de front (Vitest/Jest + RTL);
   - `lint` – lints de código.

3. **Criar estrutura mínima `src/`**
   - `src/main.tsx` – monta o `App` e aplica `ErrorBoundary` (stub inicial);
   - `src/App.tsx` – layout mínimo com texto placeholder;
   - `src/styles/global.css` – importa Tailwind e define estilos base.

4. **Sanidade manual inicial**
   - Rodar `npm install` dentro de `frontend/inspectah-ui/`;
   - Rodar `npm run dev` (ver placeholder no navegador);
   - Rodar `npm run build` e `npm run test` (mesmo que com testes vazios ou triviais).

#### 4.2 Gate S17_T0 — Sanidade de front

1. **Criar script `bin/s17_t0_sanity.sh`**
   - Entrar em `frontend/inspectah-ui/`;
   - Executar na ordem: instalação leve (se necessário), `npm run lint`, `npm run test`, `npm run build`;
   - Capturar saídas em `out/evidence/S17_T0_sanity/`;
   - Escrever `out/scorecards/S17_T0_sanity.json` com:
     - comandos executados;
     - códigos de saída;
     - status PASS/FAIL;
     - caminho para logs.

2. **Rodar T0 em ambiente limpo**
   - A partir da raiz do repo, executar `PYTHONPATH=. bin/s17_t0_sanity.sh`;
   - Ajustar o que for necessário até o scorecard marcar PASS.

#### 4.3 Base de CI (T7 parcial)

1. **Workflow inicial de CI (ex.: `.ci/sprint_17_gates.yml`)**
   - Checkout do repo;
   - Setup de Node;
   - Execução de `bin/s17_t0_sanity.sh`.

2. **Critério de avanço da Fase 1**
   - T0 verde local;
   - workflow rodando com sucesso (mesmo que acionado manualmente);
   - nenhum “pedaço solto” de config de front (scripts quebrados, dependências faltando).

---

### 5. Fase 2 — Estados, contratos e integração API (T1 + T3)

**Objetivo:** implantar a espinha dorsal da UI de consulta: máquina de estados, tipos de request/response e integração com o endpoint de consulta do Inspectah.

#### 5.1 Arquitetura mínima a implantar

Criar a estrutura descrita no Capítulo 3:

- `src/routes/ConsultationRoute.tsx` – rota principal;
- `src/pages/ConsultationPage.tsx` – página de consulta (usa `useConsultation`);
- `src/components/layout/AppShell.tsx` e `Header.tsx`;
- `src/components/consultation/ResultContainer.tsx` (ainda simples);
- `src/api/httpClient.ts` e `src/api/inspectahClient.ts`;
- `src/types/inspectah.ts` (tipos de request/response e evidências);
- `src/hooks/useConsultation.ts` (máquina de estados);
- `src/observability/ErrorBoundary.tsx` e `logEvents.ts` (podem começar stubados);
- `src/__tests__/ConsultationPage.test.tsx` e `ResultContainer.test.tsx`.

#### 5.2 Máquinas de estado e contratos (T1)

1. **Definir tipos de estado**
   - Tipo discriminado `ConsultationStatus` com variantes `idle`, `submitting`, `success`, `error` (conforme Capítulo 3);
   - Tipo `ConsultationResponseUi` para a UI.

2. **Implementar `useConsultation`**
   - Estado inicial `idle`;
   - `submitQuestion(question)`:
     - seta `submitting`;
     - chama `inspectahClient.consultTruth`;
     - em sucesso, seta `success` com `ConsultationResponseUi`;
     - em erro, seta `error` com mensagem amigável;
     - chama funções de log (mesmo que ainda prototípicas).

3. **Testes de estados**
   - Em `__tests__/ConsultationPage.test.tsx` e `ResultContainer.test.tsx`:
     - forçar estados artificiais (mock de `useConsultation` / helpers) e validar DOM;
     - garantir transições básicas (por exemplo, envio → loading → sucesso/erro).

4. **Gate T1** — `bin/s17_t1_contracts_and_states.sh`
   - Rodar testes de contratos/estados;
   - Opcionalmente, validar presença de tipos-chave em `types/inspectah.ts`;
   - Escrever `out/scorecards/S17_T1_contracts_and_states.json` com:
     - estados implementados;
     - suites de testes executadas;
     - status PASS/FAIL.

#### 5.3 Integração UI ↔ backend de consulta (T3)

1. **Contratos de API**
   - Implementar `ConsultationRequest` e `ConsultationResponseRaw` em `types/inspectah.ts` alinhados ao endpoint real (ou stub homologado) da consulta;
   - Implementar função de mapeamento de `Raw` → `Ui`.

2. **Cliente `inspectahClient`**
   - Implementar `consultTruth(request)` usando `httpClient`;
   - mapear erros HTTP e timeouts em exceções coerentes para o hook.

3. **Testes de integração**
   - Introduzir MSW ou mecanismo similar para simular respostas de backend:
     - sucesso com dados;
     - sucesso com dados limitados/risco alto;
     - erro 4xx;
     - erro 5xx;
     - falha de rede.

4. **Gate T3** — `bin/s17_t3_api_integration.sh`
   - Rodar suite de testes de integração;
   - Escrever `out/scorecards/S17_T3_api_integration.json` com resumo dos cenários e status.

#### 5.4 Critério de avanço da Fase 2

- Máquina de estados implementada e testada;
- Contratos UI↔API definidos e exercitados em testes;
- T1 e T3 verdes em ambiente local.

---

### 6. Fase 3 — UI/UX, golden flows e performance (T2 + T4 + T5)

**Objetivo:** transformar a espinha dorsal em uma experiência concreta: UI de consulta, estados vazios, casos canônicos e métricas básicas de performance.

#### 6.1 Implementar UI de domínio

1. **Formulário de consulta**
   - `ConsultationForm.tsx` com:
     - input de texto com label e descrição;
     - botão de submit;
     - suporte a Enter;
     - desativação em `submitting`.

2. **Container de resultados**
   - `ResultContainer.tsx` com switch nos estados:
     - `idle` → `EmptyState`;
     - `submitting` → skeleton/loading;
     - `success` → `ResponseSummary` + `RiskBadge` + `EvidenceList`;
     - `error` → `ErrorState`.

3. **Componentes específicos**
   - `ResponseSummary.tsx` – exibe resposta textual;
   - `RiskBadge.tsx` – usa tokens de cor (Tailwind) e texto para risco;
   - `EvidenceList.tsx` – lista evidências principais;
   - `EmptyState.tsx` – orienta em tela inicial/sem dados;
   - `ErrorState.tsx` – mensagens de erro amigáveis.

#### 6.2 UX mínima e acessibilidade (T2)

1. **Checklist de UX/acessibilidade**
   - Heading claro explicando o que o Inspectah faz;
   - labels e descrições em inputs/botões;
   - foco de teclado visível e ordem lógica;
   - contraste minimamente aceitável (especialmente em badges de risco);
   - mensagens claras em estados vazios e de erro.

2. **Evidências**
   - Documentar checklists em arquivos dentro de `out/evidence/S17_T2_ux_and_accessibility/`;
   - Capturar screenshots dos estados principais (idle, pós-consulta, erro).

3. **Gate T2** — `bin/s17_t2_ux_and_accessibility.sh`
   - Rodar testes de UI focados em empty states, labels, textos;
   - Consolidar resultado dos checklists em `S17_T2_ux_and_accessibility.json`.

#### 6.3 Golden flows (T4)

1. **Definir 3–5 casos canônicos**, alinhados a fixtures do backend (ex.: ciência, clima, política):
   - caso com risco baixo e evidências robustas;
   - caso com risco alto ou conflito;
   - caso “não sei / informação insuficiente”.

2. **Fixtures e testes**
   - Criar fixtures de `ConsultationResponseUi` para cada caso;
   - Escrever testes que renderizem a UI para cada fixture e verifiquem:
     - presença de resposta;
     - badge de risco adequado;
     - exibição de evidências;
     - mensagens corretas.

3. **Gate T4** — `bin/s17_t4_golden_flows.sh`
   - Executar testes de golden flows;
   - Gerar `out/scorecards/S17_T4_golden_flows.json` listando os casos e status;
   - Anexar roteiros de demo em `out/evidence/S17_T4_golden_flows/`.

#### 6.4 Performance percebida e bundle (T5)

1. **Medições simples de performance**
   - Medir tempo:
     - entre clique em “Consultar” e feedback de loading;
     - entre clique e resposta renderizada em casos canônicos.

2. **Tamanho de bundle**
   - Coletar tamanho de bundles gerados por `npm run build`;
   - Registrar peso total inicial e componentes mais pesados.

3. **Gate T5** — `bin/s17_t5_performance_and_bundle.sh`
   - Executar build + script de medição;
   - Gerar `S17_T5_performance_and_bundle.json` com métricas e limites-alvo;
   - Guardar evidências em `out/evidence/S17_T5_performance_and_bundle/`.

#### 6.5 Critério de avanço da Fase 3

- UI de consulta funcional (formulário + resultado + risco + evidências + erros/vazios);
- T2, T4 e T5 verdes em ambiente local, com evidências registradas.

---

### 7. Fase 4 — Observabilidade, CI completo e Go/No-Go (T6 + T7 + T8)

**Objetivo:** fechar a S17 com observabilidade mínima, CI confiável e decisão explícita de GO/NO_GO.

#### 7.1 Observabilidade de front (T6)

1. **ErrorBoundary**
   - Completar implementação em `observability/ErrorBoundary.tsx`;
   - Envolver `App` ou `ConsultationPage`;
   - Fallback amigável + botão de “tentar novamente” ou reload.

2. **Logs de eventos**
   - Implementar funções em `logEvents.ts`:
     - `logConsultationStarted`, `logConsultationSuccess`, `logConsultationError`, `logUiError`;
   - Garantir que `useConsultation` e ErrorBoundary chamem essas funções;
   - Na S17, logs podem ir para console e/ou endpoint simples, desde que não exponham dados sensíveis.

3. **Gate T6** — `bin/s17_t6_frontend_observability.sh`
   - Forçar um erro de UI controlado;
   - Executar consulta bem-sucedida e consulta com erro de backend;
   - Verificar logs gerados;
   - Gerar `S17_T6_frontend_observability.json` com resumo dos eventos e checagem de privacidade.

#### 7.2 CI e reprodutibilidade (T7 completo)

1. **Ampliar workflow `.ci/sprint_17_gates.yml`**
   - Incluir chamadas ou steps correspondentes a T0…T6;
   - Garantir que qualquer falha quebre a pipeline.

2. **Workflow periódico (`.ci/sprint_17_nightly.yml`)**
   - Opcional, rodando subconjunto de gates (ex.: T1–T4, T6) diariamente.

3. **Gate T7** — `bin/s17_t7_ci_and_repro.sh`
   - Rodar localmente o mesmo conjunto de checks da CI;
   - Registrar commit SHA, resultado da última pipeline e comandos relevantes em `S17_T7_ci_and_repro.json`.

#### 7.3 Orquestração geral e Go/No-Go (T8)

1. **Script de orquestração** — `bin/s17_all_gates.sh`
   - Chamar, em sequência, `s17_t0`…`s17_t7`;
   - Abortar em caso de falha;
   - Ao final, chamar `s17_t8_go_no_go.sh`.

2. **Agregador T8** — `bin/s17_t8_go_no_go.sh`
   - Ler todos os scorecards T0…T7;
   - Determinar decisão sugerida (GO/GO_WITH_RESTRICTIONS/NO_GO);
   - Escrever `out/scorecards/S17_T8_go_no_go.json` com:
     - decisão final;
     - commit SHA da S17;
     - restrições (se houver) e riscos;
     - referências aos scorecards anteriores.

3. **Ritual de Go/No-Go**
   - Participantes mínimos: backend, frontend, produto/PO;
   - Rodar `PYTHONPATH=. bin/s17_all_gates.sh` e garantir verde;
   - Passar pelos golden flows em UI real;
   - Confirmar mensagens de erro/vazios;
   - Validar percepção de UX;
   - Bater o martelo em GO, GO_WITH_RESTRICTIONS ou NO_GO.

4. **Docs finais da S17**
   - `docs/sprint_17_overview.md` — visão, escopo, resumo de entregas;
   - `docs/sprint_17_filemap_e_arquitetura.md` — filemap de front, máquina de estados, contratos UI↔API;
   - `docs/sprint_17_orr_summary.md` — estado T0…T8, decisão final, commit SHA, riscos e próximos passos.

---

### 8. Rotina operacional recomendada para a S17

Para o dia-a-dia da sprint, a rotina sugerida é:

**Início do bloco de trabalho**

1. `cd /Users/gustavoschneiter/Documents/Inspectah`;
2. `git status` (garantir árvore limpa ou ver o que está pendente);
3. Rodar `PYTHONPATH=. bin/s17_t0_sanity.sh` para checar front básico.

**Durante a implementação**

1. Escolher uma mini-tarefa alinhada a este capítulo (ex.: “implementar RiskBadge”, “finalizar T3”, “ajustar ErrorBoundary”);
2. Editar arquivos em `frontend/inspectah-ui/src/**` conforme Capítulo 3;
3. Rodar `npm run test` e `npm run lint` no front;
4. Voltar à raiz e rodar o gate correspondente (`bin/s17_t1_*`, `t2_*`, etc.);
5. Ajustar até o gate ficar verde.

**Checkpoints frequentes**

- Ao terminar um conjunto de mini-tarefas, rodar `PYTHONPATH=. bin/s17_all_gates.sh` para ver o quadro geral;
- Corrigir regressões imediatamente (não acumular gates quebrados).

**Antes de commit/push importantes**

1. Garantir `bin/s17_all_gates.sh` verde;
2. `git diff` e `git diff --cached` para revisar alterações;
3. `git commit -m "feat: ..."` e `git push origin main`.

**Fechamento da sprint**

1. Rodar `PYTHONPATH=. bin/s17_all_gates.sh` em ambiente limpo;
2. Atualizar docs da S17 (overview, filemap, ORR);
3. Realizar ritual de Go/No-Go;
4. Registrar decisão, riscos e próximos passos.

---

### 9. Riscos, limites e como tratá-los

Principais riscos identificados para a S17:

- **Front over-engineered**: gastar esforço demais em detalhes visuais e pouco em contrato/estado/gates.
- **Acoplamento excessivo ao backend**: UI depender de campos instáveis ou internos do Truth-DB.
- **Acessibilidade negligenciada**: criar uma UI agradável apenas para parte dos usuários.
- **Observabilidade simbólica**: logs que não ajudam em incidentes reais.

Mitigações embutidas neste capítulo:

- foco em **uma tela** bem validada (consulta) na S17;
- contratos tipados em `types/inspectah.ts` como única fonte de verdade de front;
- gate T2 com checklist explícito de UX/acessibilidade;
- gate T6 exigindo exemplos de logs úteis e revisados sob ótica de privacidade.

---

### 10. Definition of Done (DoD) da Sprint 17

A S17 só é considerada concluída quando **todas** as condições abaixo forem verdadeiras:

1. `frontend/inspectah-ui/` existe, builda, testa e lint em ambiente limpo, e o gate T0 registra isso.
2. A UI de consulta permite que uma pessoa não técnica:
   - entenda em segundos o que o Inspectah faz;
   - faça uma pergunta;
   - veja resposta consolidada, risco e evidências;
   - veja mensagens claras em estados vazios, de erro e de incerteza.
3. A máquina de estados da UI está explicitamente implementada, testada e mapeada em T1.
4. A integração UI↔backend de consulta funciona em cenários de sucesso, incerteza e erro, coberta por T3.
5. Existem casos canônicos (golden flows) funcionando, testados e documentados, cobertos por T4.
6. Métricas iniciais de performance e tamanho de bundle foram medidas, registradas e avaliadas em T5.
7. Observabilidade mínima de front (ErrorBoundary + logs de eventos críticos) está em funcionamento e verificada em T6, sem vazamento de dados sensíveis.
8. CI executa os gates principais de front (T0–T6), falhas quebram a integração e T7 registra isso.
9. `bin/s17_all_gates.sh` roda em ambiente limpo, produz scorecards T0…T8 com PASS, e T8 registra decisão (GO ou GO_WITH_RESTRICTIONS) com commit SHA.
10. `docs/sprint_17_overview.md`, `docs/sprint_17_filemap_e_arquitetura.md` e `docs/sprint_17_orr_summary.md` estão atualizados e coerentes com o estado final da S17.

Com este Capítulo 4, a S17 deixa de depender de improviso. A partir daqui, a pergunta não é mais “o que falta decidir?”, mas apenas “quando vamos executar cada passo e marcar cada gate como verde”.

