# Sprint 19 – Capítulo 2
## Gates, Métricas e Critérios de Validação (v3)

Este capítulo transforma a visão da Sprint 19 (Timeline e Raio‑X do Sistema de Blocos) em um conjunto de **gates executáveis**, **métricas objetivas** e **critérios de aprovação** alinhados ao DNA, ao Sprint Playbook e ao Capítulo 1 da própria S19.

A S19 só é considerada entregue quando for possível comprovar, via scripts e evidências, que:

1. A história que o Inspectah mostra para cada caso é **fiel** ao que está na Truth‑DB / Sistema de Blocos.
2. A experiência de diagnóstico é **rápida, navegável e estável** para operador, curador e investigador (sobre o Console de Admin da S18).
3. As novas peças de timeline e raio‑X se encaixam **sem quebrar** o que S17 (fluxo do usuário final) e S18 (Console de Admin) já entregaram.

Para isso, a S19 define nove gates S19_G0…S19_G8, apoiados em seis métricas oficiais (M1…M6). Cada gate tem:

- Um **objetivo claro**.
- Um **script binário único** em `bin/` (idempotente, reexecutável).
- Um **scorecard JSON** em `out/scorecards/`.
- Uma pasta de **evidências** em `out/evidence/`.
- **Critérios de PASS/FAIL** explícitos e fechados.

A implementação detalhada dos scripts e testes (shell + Python + testes de front) será descrita no Capítulo 4, mas este capítulo é a fonte de verdade para o que cada gate deve provar.

---
## 1. Métricas oficiais da Sprint 19 (M1…M6)

As métricas da S19 medem se a timeline e o raio‑X realmente ajudam a contar a história dos casos – com fidelidade, completude e desempenho aceitável.

Todas as métricas são numéricas e serão consolidadas em `out/scorecards/S19_G6_metrics_and_demo.json`.

### M1 — Tempo de carregamento da timeline (M1_timeline_load_p95_s)

Tempo p95 (percentil 95) em segundos da resposta do endpoint responsável por entregar a timeline de um caso/tema (por exemplo, `GET /admin/cases/{id}/timeline`), medido sobre um conjunto de casos‑fixture da S19, incluindo pelo menos:

- 1 caso “pesado” (muitos eventos na timeline).
- 1 caso “simples” (poucos eventos).

O cálculo é feito sobre N execuções por caso (N pequeno, mas > 1), agregando tempos por caso e depois consolidando o p95 global.

**Threshold:** `M1 ≤ 0.8` s (p95 global).

Interpretação: se o p95 da timeline passar de 0,8 s em cenários controlados, o custo cognitivo para diagnóstico em incidentes reais tende a ficar alto demais.

---
### M2 — Tempo de carregamento do raio‑X (M2_xray_load_p95_s)

Tempo p95, em segundos, da resposta do endpoint/túnel que entrega o raio‑X completo do caso (por exemplo, `GET /admin/cases/{id}/xray` ou rota equivalente). Usa a mesma amostra de casos que M1.

**Threshold:** `M2 ≤ 0.8` s (p95 global).

Interpretação: o raio‑X não pode ser um painel “lento e pesado”; precisa abrir rápido o bastante para operadores/curadores realmente usarem em dia de crise.

---
### M3 — Cobertura da timeline (M3_timeline_coverage_ratio)

Relação entre o número de eventos relevantes que **deveriam** aparecer na timeline (lista canônica por caso) e o número de eventos efetivamente retornados pela API de timeline.

Para cada caso‑fixture:

- `expected_events`: lista de eventos relevantes em `Sprint 19/fixtures/timeline_expected_{case_id}.json`.
- `actual_events`: lista vinda de `GET /admin/cases/{id}/timeline`.
- Define‑se uma função de match (por ID único ou por tupla `(timestamp, tipo, fonte/bloco)`):
  - `matched_events = match(expected_events, actual_events)`.
- `M3_case = |matched_events| / |expected_events|`.

M3 global é a média `mean(M3_case)` em todos os casos‑fixture.

**Thresholds:**
- Para cada caso de teste: `M3_case ≥ 0.90`.
- Valor agregado global: `M3 ≥ 0.95`.

Interpretação: a timeline não pode “esquecer” blocos importantes. Eventos extras são tolerados se forem explicáveis (por exemplo, eventos suplementares marcados como tal), mas eventos relevantes faltando em quantidade derrubam a sprint.

---
### M4 — Completude do raio‑X (M4_xray_completeness_ratio)

Proporção das **seções obrigatórias** do raio‑X que estão presentes e não vazias para cada caso‑fixture.

Seções mínimas do raio‑X:

- `Resumo do Caso` (dados principais e estado atual).
- `Debunker` (avaliação, risco, flags principais).
- `Comitês` (como votaram, divergências relevantes).
- `Âncoras` (estado das âncoras relevantes e impacto na confiança).
- `Evidências principais` (ponte para artefatos da Truth‑DB / Sistema de Blocos).

Para cada caso:

- `sections_ok = número de seções obrigatórias presentes e com conteúdo relevante`.
- `M4_case = sections_ok / 5`.

M4 global é o mínimo dos `M4_case` (ou seja, o pior caso).

**Threshold:** `M4_case = 1.0` para todos os casos; logo, `M4 = 1.0`.

Interpretação: nenhuma seção obrigatória pode estar faltando ou vazia. Se qualquer caso tiver raio‑X “capado”, a sprint falha aqui.

---
### M5 — Profundidade de explicação (M5_explanation_depth_score)

Mede se o raio‑X oferece **explicações legíveis** do “porquê” das decisões, e não apenas dados crus ou frases vazias.

Para cada caso‑fixture, o script avalia campos textuais como:

- `debunker.explanation`.
- `committees.summary` (ou equivalente).
- `anchors.summary`.

Critérios mínimos por caso (todos precisam ser verdadeiros):

- Campo existe e não é vazio.
- Comprimento mínimo (por exemplo, `len(texto) ≥ N` caracteres, com N definido no Cap. 4, mas não ridiculamente baixo).
- Não é apenas um código/ID técnico ou placeholder (“TODO”, “TBD”…).
- Contém sinais de linguagem natural (frases, conectivos) que indiquem racional ou contexto.

Define‑se um score binário por caso: `M5_case = 1` se todos os critérios mínimos forem atendidos, caso contrário `0`.

M5 global é o mínimo de `M5_case` (ou seja, todos os casos precisam passar).

**Threshold:** `M5 = 1.0` na amostra oficial da sprint.

Interpretação: se o raio‑X não ajuda a explicar nada – só joga JSON maquiado – a S19 falhou no propósito principal de diagnóstico.

---
### M6 — Caminho até evidência (M6_steps_to_evidence_p95)

Número de passos/telas necessários, a partir do Raio‑X de um caso, para chegar a **pelo menos uma evidência concreta** (bloco, arquivo, anotação) já existente na árvore de evidências.

Medido em cenários automatizados de UI, por exemplo:

1. Abrir o Console de Admin (S18).
2. Navegar até um caso.
3. Abrir o Raio‑X desse caso.
4. A partir do raio‑X, seguir o caminho até uma evidência concreta (por exemplo, clicar em “Ver evidências” ou similar, e depois em um artefato específico).

Conta‑se o número de passos lógicos a partir do raio‑X até a evidência, para vários casos‑fixture. M6 é o p95 dessa distribuição.

**Threshold:** `M6 ≤ 2.0` (p95).

Interpretação: se, a partir do raio‑X, o operador precisar de mais de dois passos lógicos para chegar em evidência concreta em 95% das vezes, o fluxo está longo demais para ser realmente útil em operação.

---
## 2. Mapa Gate ↔ Métrica ↔ Objetivo

A S19 utiliza nove gates S19_G0…S19_G8, organizados assim em relação às métricas e aos objetivos do Capítulo 1:

- **S19_G0 – Scope e sanidade**  
  Garante que o escopo da S19 está bem definido, documentado, restrito a timeline/raio‑X e coerente com S17/S18. Não mede M1…M6 diretamente.

- **S19_G1 – Contratos e dados (backend)**  
  Verifica se endpoints de timeline e raio‑X existem, são estáveis e coerentes com a Truth‑DB / Sistema de Blocos. Prepara terreno para M3 e M4.

- **S19_G2 – Jornadas e UX**  
  Garante que as jornadas de diagnóstico (operador/curador/investigador) funcionam, na prática, sobre o Console de Admin da S18. Conecta M5 e M6 à experiência real.

- **S19_G3 – Qualidade de frontend**  
  Assegura que lint, testes e build da SPA com timeline/raio‑X passam. Não mede diretamente M1…M6, mas protege a base técnica e a confiabilidade da UI.

- **S19_G4 – Correção e cobertura da timeline**  
  Mede M3 usando fixtures canônicos: a timeline realmente conta a história correta dos casos.

- **S19_G5 – Consistência e profundidade do raio‑X**  
  Mede M4 e M5: raio‑X completo, com explicação mínima aceitável do “porquê”.

- **S19_G6 – Métricas e demo end‑to‑end**  
  Consolida M1, M2, M3, M4, M5, M6 em cenários end‑to‑end, exercitando tanto o backend quanto a UI.

- **S19_G7 – CI e observabilidade da sprint**  
  Garante que os gates e métricas essenciais da S19 estão plugados em CI e têm trilha de evidências reexecutável.

- **S19_G8 – GO/NO‑GO**  
  Lê todos os scorecards e métricas, aplica os thresholds e decide explicitamente se a Sprint 19 está apta a “voar” sem supervisão manual.

---
## 3. Definição detalhada dos Gates S19_G0…S19_G8

### S19_G0 – Scope e sanidade da sprint

**Script:** `bin/s19_g0_scope.sh`  
**Scorecard:** `out/scorecards/S19_G0_scope.json`  
**Evidências:** `out/evidence/S19_G0_scope/`

Objetivo: garantir que a Sprint 19 está ancorada em documentos claros e que as mudanças de código observadas no repo batem com o recorte declarado (Timeline + Raio‑X + fixtures + suporte mínimo de backend/CI).

O script deve:

1. Verificar a existência dos documentos da S19 (por exemplo, `Sprint 19/Capitulo 1.md`…`Capitulo 4.md`) e de qualquer macro‑doc da S19 referenciado.
2. Rodar um `git diff --name-only` entre o HEAD atual e o ponto de referência (por exemplo, o commit de fechamento da S18) e classificar arquivos modificados em:
   - `files_in_scope`: mudanças diretamente ligadas à S19 (backend timeline/raio‑X, frontend de timeline/raio‑X, fixtures S19, `bin/s19_*`, workflow de CI da S19).
   - `files_out_of_scope`: alterações em áreas que não deveriam ser tocadas pela S19 (sprints antigas, DNA, scripts ORR de outros ciclos, etc.).
3. Gerar scorecard JSON com:
   - `gate_id = "S19_G0"`.
   - `status = "PASS" | "FAIL"`.
   - `details.docs_ok` (boolean), `details.files_in_scope`, `details.files_out_of_scope`.

Critério de PASS:

- Todos os docs esperados existem.
- `files_out_of_scope` vazio ou contendo apenas alterações justificadas (explicitamente referenciadas no Capítulo 3/4).
- Nenhuma remoção acidental de gates, scripts ou docs de sprints anteriores.

Qualquer inconsistência relevante (doc faltando ou alteração suspeita em área proibida) derruba o gate.

---
### S19_G1 – Contratos e arquitetura de dados (backend)

**Script:** `bin/s19_g1_contracts_and_data.sh`  
**Scorecard:** `out/scorecards/S19_G1_contracts_and_data.json`  
**Evidências:** `out/evidence/S19_G1_contracts_and_data/`

Objetivo: garantir que o backend expõe contratos estáveis para timeline e raio‑X, coerentes com a Truth‑DB / Sistema de Blocos, sem mock escondido.

O script deve:

1. Inicializar a app FastAPI oficial (`inspectah.api:app`) via TestClient.
2. Verificar existência e comportamento de endpoints, por exemplo:
   - `GET /admin/cases/{id}/timeline` (ou rota equivalente definida na S19).
   - `GET /admin/cases/{id}/xray` (ou rota equivalente).
3. Para casos‑fixture válidos:
   - Garantir retorno `200` com payload JSON.
   - Validar campos mínimos da timeline: `id_evento`, `tipo_evento`, `timestamp`, `severidade`, referência a fonte/bloco.
   - Validar campos mínimos do raio‑X: presença de seções `summary`, `debunker`, `committees`, `anchors`, `evidences` (mesmo que ainda não com todo o conteúdo final).
4. Para IDs inexistentes, checar se retornam `404` ou código consistente.
5. Gravar exemplos de payload em arquivos:
   - `out/evidence/S19_G1_contracts_and_data/timeline_{id}.json`.
   - `out/evidence/S19_G1_contracts_and_data/xray_{id}.json`.
6. Gerar scorecard com:
   - `gate_id`, `status`.
   - `details.endpoints_checked` e resumo dos campos encontrados.

Critério de PASS: todos os endpoints esperados existem, se comportam corretamente para casos válidos e inválidos e o shape mínimo do payload bate com o desenho da S19.

---
### S19_G2 – Jornadas de UX de diagnóstico

**Script:** `bin/s19_g2_journeys_and_ux.sh`  
**Scorecard:** `out/scorecards/S19_G2_journeys_and_ux.json`  
**Evidências:** `out/evidence/S19_G2_journeys_and_ux/`

Objetivo: garantir que as jornadas reais de operador/curador/investigador funcionam, na prática, usando a SPA do Inspectah (S18 + S19).

O script deve, usando testes de frontend (React Testing Library + MSW, Playwright ou similar):

1. Simular a entrada no Console de Admin (S18).
2. Navegar até a lista de casos.
3. Para pelo menos dois casos‑fixture (um simples e um complexo):
   - Abrir o Raio‑X direto a partir da lista **ou** abrir timeline e depois o Raio‑X, conforme fluxo definido no Capítulo 3.
   - Validar que a timeline renderiza (pelo menos um evento visível) e que o raio‑X exibe todas as seções principais.
4. Exercitar estados especiais:
   - Caso sem timeline relevante (empty state amigável).
   - Erro de backend simulado (estado de erro coerente, sem quebrar a tela).
   - Loading perceptível, mas sem travar.
5. Salvar screenshots relevantes em `out/evidence/S19_G2_journeys_and_ux/` (por exemplo, `timeline_ok.png`, `xray_ok.png`, `error_state.png`).
6. Escrever scorecard com lista de cenários executados e resultado de cada um.

Critério de PASS:

- Todos os cenários de jornada definidos passam.
- Nenhuma navegação crítica quebra (tela em branco, loops de loading, erros não tratados).
- Empty/error/loading states se comportam de forma minimamente adulta.

---
### S19_G3 – Qualidade de frontend (lint, testes, build)

**Script:** `bin/s19_g3_front_quality.sh`  
**Scorecard:** `out/scorecards/S19_G3_front_quality.json`  
**Evidências:** `out/evidence/S19_G3_front_quality/`

Objetivo: manter a disciplina de qualidade do frontend após a chegada de timeline e raio‑X.

O script deve:

1. Entrar em `frontend/inspectah-ui`.
2. Rodar, em sequência:
   - `npm run lint`.
   - `npm run test -- --watch=false` (incluindo testes específicos da S19, por exemplo `AdminTimelineXray.test.tsx` ou equivalente).
   - `npm run build`.
3. Guardar logs em:
   - `out/evidence/S19_G3_front_quality/lint.log`.
   - `out/evidence/S19_G3_front_quality/test.log`.
   - `out/evidence/S19_G3_front_quality/build.log`.
4. Gerar scorecard com:
   - `status = "PASS"` se todos os comandos retornarem exit code 0.
   - Em `details`, contagem de testes, tempo da suite e qualquer warning relevante.

Critério de PASS: lint, testes e build terminam sem erros. Falha em qualquer etapa derruba o gate.

---
### S19_G4 – Correção e cobertura da timeline (M3)

**Script:** `bin/s19_g4_timeline_correctness.sh`  
**Scorecard:** `out/scorecards/S19_G4_timeline_correctness.json`  
**Evidências:** `out/evidence/S19_G4_timeline_correctness/`

Objetivo: garantir, com dados concretos, que a timeline reflete bem os eventos históricos relevantes de cada caso.

O script deve:

1. Para cada caso‑fixture da S19:
   - Ler `Sprint 19/fixtures/timeline_expected_{case_id}.json` (lista canônica de eventos).
   - Consultar o endpoint de timeline correspondente.
2. Fazer o match entre eventos esperados e retornados.
3. Calcular `M3_case` para cada caso.
4. Computar M3 global como média dos `M3_case`.
5. Escrever scorecard com:
   - `metrics: { "M3": <valor_global> }`.
   - `details.cases[case_id].M3_case`.
   - Listas `missing_events` / `extra_events` por caso.
6. Salvar payloads brutos e comparações em `out/evidence/S19_G4_timeline_correctness/`.

Critério de PASS:

- Para todos os casos: `M3_case ≥ 0.90`.
- M3 global: `M3 ≥ 0.95`.

Caso contrário, o gate falha e o scorecard lista explicitamente quais eventos faltaram ou sobraram.

---
### S19_G5 – Consistência e profundidade do raio‑X (M4, M5)

**Script:** `bin/s19_g5_xray_consistency_and_depth.sh`  
**Scorecard:** `out/scorecards/S19_G5_xray_consistency_and_depth.json`  
**Evidências:** `out/evidence/S19_G5_xray_consistency_and_depth/`

Objetivo: garantir que o raio‑X não é nem raso, nem quebrado: todas as seções existem, têm conteúdo e oferecem alguma explicação.

O script deve:

1. Para cada caso‑fixture:
   - Chamar o endpoint de raio‑X.
   - Verificar presença de todas as seções obrigatórias: `summary`, `debunker`, `committees`, `anchors`, `evidences`.
2. Verificar se cada seção tem conteúdo relevante (não vazia, não placeholder).
3. Calcular `M4_case = seções_ok / 5`.
4. Avaliar `M5_case` usando os campos de explicação (debunker/committees/anchors) com os critérios mínimos (existência, tamanho, linguagem natural).
5. Calcular M4 global (mínimo dos `M4_case`) e M5 global (mínimo dos `M5_case`).
6. Escrever no scorecard:
   - `metrics: { "M4": <valor_global>, "M5": <valor_global> }`.
   - `details.cases[case_id].M4_case`, `M5_case` e flags de seções/explicações problemáticas.

Critério de PASS:

- `M4 = 1.0` (nenhuma seção obrigatória faltando ou vazia em nenhum caso).
- `M5 = 1.0` (todas as explicações dos casos‑fixture passam nos critérios mínimos).

Qualquer seção ausente ou explicação vazia derruba o gate.

---
### S19_G6 – Métricas e demo end‑to‑end (M1…M6)

**Script:** `bin/s19_g6_metrics_and_demo.sh`  
**Scorecard:** `out/scorecards/S19_G6_metrics_and_demo.json`  
**Evidências:** `out/evidence/S19_G6_metrics_and_demo/`

Objetivo: consolidar todas as métricas da Sprint 19 em um único cenário executável, reproduzível e fácil de demonstrar para humanos (PO, stakeholders, etc.).

O script deve:

1. Medir M1 e M2:
   - Para cada caso‑fixture, fazer múltiplas chamadas aos endpoints de timeline e raio‑X, medindo tempos e calculando p95 global.
2. Recuperar (ou recalcular de forma leve) M3, M4, M5:
   - Ler scorecards de `S19_G4` e `S19_G5` ou repetir as contas com as mesmas fontes de dados.
3. Medir M6:
   - Rodar cenários automatizados de UI que contem quantos passos são necessários, a partir do raio‑X, para chegar a uma evidência concreta, e calcular p95.
4. Consolidar tudo em um único scorecard com:
   - `metrics: { "M1": ..., "M2": ..., "M3": ..., "M4": ..., "M5": ..., "M6": ... }`.
   - `details` com casos usados, amostras de tempos e exemplos de fluxos.

Critério de PASS:

- `M1 ≤ 0.8` s.
- `M2 ≤ 0.8` s.
- `M3 ≥ 0.95`.
- `M4 = 1.0`.
- `M5 = 1.0`.
- `M6 ≤ 2.0` (p95).

Qualquer métrica fora de faixa derruba o gate e a causa fica registrada no scorecard.

---
### S19_G7 – CI e observabilidade da Sprint 19

**Script:** `bin/s19_g7_ci_and_observability.sh`  
**Scorecard:** `out/scorecards/S19_G7_ci_and_observability.json`  
**Evidências:** `out/evidence/S19_G7_ci_and_observability/`

Objetivo: garantir que a Sprint 19 não é um “ritual só local”: os gates principais precisam estar plugados em CI e minimamente observáveis.

O script deve:

1. Verificar a existência de um workflow de CI dedicado da S19 em `.github/workflows/` (por exemplo, `_s19_timeline_xray.yml`).
2. Validar que este workflow executa, pelo menos:
   - `bin/s19_g3_front_quality.sh`.
   - Um subconjunto representativo de `S19_G4`, `S19_G5` e `S19_G6` (ou scripts equivalentes de métricas), em ambiente CI.
3. Conferir se o workflow está configurado para rodar em:
   - PRs que mexem em código da S19.
   - Push para branches relevantes (como `main`).
4. Opcionalmente, consultar logs ou artefatos de uma execução recente para comprovar que scorecards S19_* foram gerados em CI.
5. Escrever scorecard com `status` e `details` descrevendo workflows encontrados, scripts invocados e triggers.

Critério de PASS:

- Workflow específico da S19 existe e referencia scripts críticos.
- Triggers fazem sentido (não é um workflow morto).
- A execução em CI é capaz de gerar scorecards da S19 sem intervenção manual.

---
### S19_G8 – GO/NO‑GO da Sprint 19

**Script:** `bin/s19_g8_go_no_go.sh`  
**Scorecard:** `out/scorecards/S19_G8_go_no_go.json`  
**Evidências:** `out/evidence/S19_G8_go_no_go/`

Objetivo: cristalizar o estado da Sprint 19 em uma decisão simples e auditável: GO ou NO_GO.

O script deve:

1. Ler todos os scorecards `S19_G0`…`S19_G7` em `out/scorecards/`.
2. Verificar se todos têm `status = "PASS"`.
3. Ler as métricas consolidadas de `S19_G6` (`M1`…`M6`).
4. Aplicar os thresholds definidos neste capítulo, marcando explicitamente quais, se algum, falharam.
5. Produzir um scorecard final com:
   - `gate_id = "S19_G8"`.
   - `status = "PASS" | "FAIL"`.
   - `decision = "GO" | "NO_GO"`.
   - `metrics`: snapshot de `M1…M6`.
   - `details.failures`: lista com gates ou métricas reprovadas.

Critério de PASS / GO:

- Todos os gates S19_G0…S19_G7 com `status = "PASS"`.
- Todas as métricas dentro dos thresholds.

Qualquer gate em FAIL ou métrica fora de faixa força `decision = "NO_GO"` e `status = "FAIL"`.

---
## 4. Invariantes de implementação e disciplina de evidências

Todos os scripts de gate S19_G* seguem os invariantes já estabelecidos pelo DNA e pelo Sprint Playbook, alinhados ao que foi praticado em S10, S14 e S18:

- **Idempotência:** rodar o mesmo script duas vezes produz artefatos consistentes, sem efeitos colaterais inesperados no repo.
- **Fail‑fast:** qualquer violação de critério faz o script sair com código de erro (`exit != 0`). Nenhum gate “finge que passou” silenciosamente.
- **Scorecards obrigatórios:** cada gate sempre escreve um JSON em `out/scorecards/` com campos básicos (`gate_id`, `status`, `timestamp`, `metrics`, `details`).
- **Evidências suficientes:** `out/evidence/S19_G*/` sempre contém logs, snapshots ou payloads que permitam, semanas depois, entender por que o gate passou ou falhou.
- **Sem dependências mágicas:** nenhum script depende de variáveis de ambiente obscuras ou de serviços externos não controlados; qualquer pré‑requisito é documentado no Capítulo 4.

Com isso, o Capítulo 2 da S19 define um contrato verificável e auditável para timeline e raio‑X. O Capítulo 3 (filemap/arquitetura) e o Capítulo 4 (runbook e implementação) se apoiam diretamente neste texto para desenhar pastas, scripts, testes e fluxos, mantendo a Sprint 19 no mesmo nível de rigor que S10, S14, S18 – ou acima.

