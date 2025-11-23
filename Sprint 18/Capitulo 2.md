# Inspectah — Sprint 18
## Capítulo 2 — Gates de validação, métricas e evidências do Console de Admin

> Arquivo alvo no repositório: `Sprint 18/Capitulo 2.md`  
> Domínio: Frontend — Console de Admin (Fontes, Casos/Temas, Saúde Operacional)

---

### 1. Propósito deste capítulo

O Capítulo 1 definiu **o que** a Sprint 18 precisa entregar: um Console de Admin que coloque o Inspectah em modo cockpit, permitindo enxergar em segundos a saúde do sistema, das fontes e dos casos/temas.

Este Capítulo 2 define **como vamos comprovar**, de forma objetiva e repetível, que isso aconteceu, usando a gramática da DNA:

- **gates S18_G0…S18_G8** (checks automatizados e agregadores);
- **métricas oficiais M1…M6** (tempo, cobertura, profundidade de explicação, caminho até evidência);
- **artefatos de evidência** sob `out/` (scorecards, bundles, manifests, snapshots).

No final da sprint, qualquer pessoa (não apenas quem implementou) deve conseguir, olhando os scorecards e evidências da S18, responder:

- se o Console de Admin **existe, sobe e funciona**;
- se o que ele mostra é **coerente com o que o backend sabe**;
- se ele **respeita o DNA** (sem painel decorativo, sem backdoor de canetada, sem UI que inventa verdade);
- se um operador consegue, de fato, **usar o console para operar o Inspectah**.

---

### 2. Visão geral dos gates S18_G0…S18_G8

A Sprint 18 herda o formato já consolidado em sprints anteriores (como S7), com nove gates:

- **S18_G0 — Intenção & escopo travados**  
  Garante que estamos construindo a coisa certa: visão da S18 fechada, backlog alinhado ao Capítulo 1 e respeito ao recorte S17–S18–S19–S20.

- **S18_G1 — Arquitetura de front & contratos de admin**  
  Assegura que rotas, componentes, organização de pastas e contratos de API de admin estão claros, revisados e viáveis.

- **S18_G2 — Journeys & UX do Console de Admin**  
  Verifica se as jornadas principais (Operador, Curador, PO) funcionam de ponta a ponta na UI, mesmo com dados de teste.

- **S18_G3 — Qualidade de implementação de frontend**  
  Confirma que lint, build e testes básicos cobrindo o Console de Admin estão verdes, sem dívidas técnicas grosseiras.

- **S18_G4 — Coerência UI ↔ Backend (Fontes & Casos)**  
  Mede se a UI mostra o mesmo universo de fontes e casos exposto pelos endpoints de admin do backend.

- **S18_G5 — Saúde operacional refletida na UI**  
  Verifica se os sinais de health do backend aparecem, de forma correta e útil, na Visão Geral do Console de Admin.

- **S18_G6 — Experiência de operação end‑to‑end**  
  Valida, com cenários guiados e métricas, se um operador consegue usar o console para entender o estado do sistema em tempo aceitável.

- **S18_G7 — Observabilidade + CI da S18**  
  Garante que o Console de Admin está incorporado aos pipelines de CI e à observabilidade mínima de frontend, evitando regressões silenciosas.

- **S18_G8 — GO/NO‑GO da Sprint 18**  
  Gate agregador que olha todos os anteriores, registra evidências e decide se a S18 está pronta para ser tratada como parte estável do Inspectah.

Cada gate produz, no mínimo, um **scorecard JSON em `out/scorecards/S18_G*.json`** e, quando faz sentido, um **bundle em `out/evidence/S18_G*/`**, seguindo o Sprint Playbook.

---

### 3. Métricas oficiais da Sprint 18 (M1…M6)

A S18 adota um conjunto de métricas focadas no que importa para um cockpit de operação. Elas são referenciadas explicitamente nos gates.

- **M1 — Tempo de carregamento do Console de Admin**  
  Tempo, em segundos, entre acessar `/admin` e a Visão Geral ficar utilizável (cards de health renderizados).  
  • Alvo: ≤ 1,5 s em ambiente local com dataset de referência.

- **M2 — Tempo da jornada “do alerta à fonte”**  
  Tempo, em segundos, para um operador sair de um alerta na Visão Geral, navegar até a lista de fontes, filtrar por degradadas e abrir o detalhe da fonte problemática.  
  • Alvo: ≤ 1,0 s de tempo de UI (descontando o tempo humano — medido em script/automação).

- **M3 — Cobertura de fontes na UI**  
  Razão entre o número de fontes ativas visíveis na tela de Fontes e o número de fontes ativas reportadas pelo endpoint de admin.  
  • Alvo: ≥ 0,99.

- **M4 — Cobertura de casos/temas na UI**  
  Razão entre o número de casos/temas visíveis na tela de Casos/Temas e o número de casos/temas reportados pelo endpoint de admin.  
  • Alvo: ≥ 0,99.

- **M5 — Profundidade de explicação nas telas de detalhe**  
  Percentual de casos/temas (no conjunto de teste) em que a tela de detalhe exibe:  
  • estado atual;  
  • um resumo textual curto;  
  • pelo menos uma razão/explicação principal (por exemplo, referência às principais fontes/evidências).  
  • Alvo: 1,0 (100%).

- **M6 — Caminho até evidência em até 2 cliques**  
  Percentual de casos/temas e fontes em que o operador consegue, em até dois cliques a partir da Visão Geral ou das listas, chegar em uma tela com contexto suficiente (detalhe com estado + evidências principais).  
  • Alvo: 1,0 (100%).

Essas métricas são consolidadas em um scorecard de métricas da S18 (por exemplo, `out/scorecards/S18_G6_metrics_and_demo.json`) e apontadas nos gates G4, G5 e G6.

---

### 4. Mapa rápido Gates × Métricas

Para evitar ambiguidade:

- **G0** — não usa métricas numéricas; é gate de escopo/visão.  
- **G1** — não usa métricas numéricas; é gate de arquitetura/contratos.  
- **G2** — começa a exercitar M2 e M6 de forma exploratória (sem alvo rígido).  
- **G3** — foca em build/lint/test; sem uso direto de M1…M6.  
- **G4** — usa diretamente **M3** e **M4** (cobertura de fontes e casos).  
- **G5** — usa diretamente **M1** (tempo de carregamento) e valida consistência de health.  
- **G6** — usa diretamente **M2**, **M5** e **M6** (experiência end‑to‑end).  
- **G7** — não introduz métricas novas; observa se testes que cobrem M1…M6 fazem parte da CI.  
- **G8** — lê os valores finais de M1…M6 e decide GO/NO‑GO.

---

### 5. Definição detalhada dos gates

#### 5.1 Gate S18_G0 — Intenção & escopo travados

**Pergunta principal**  
Estamos indo na direção certa? A visão da S18 (Cap. 1) e o backlog espelham o mesmo recorte de produto?

**Entradas**

- `Sprint 18/Capitulo 1.md` final.  
- Quadro de sprint / backlog da S18.  
- Qualquer macro‑doc da S18 (ex.: `docs/inspectah_sprint_18_macro.md`).

**Critérios de PASS**

- Cap. 1 sem TODOs, sem “decidir depois” em seções centrais.  
- Não há histórias/tarefas de S18 que sejam, na prática, escopo de S19 ou S20 (timeline detalhada, raio‑X, tuning de parâmetros pela UI, auth completa).  
- O recorte entre usuário final (S17), admin cockpit (S18), timeline/raio‑X (S19) e polimento/auth (S20) está explícito e respeitado.

**Evidências**

- `out/scorecards/S18_G0_scope.json` contendo:  
  • status PASS/FAIL;  
  • paths e hashes dos documentos revisados;  
  • lista resumida de itens “explicitamente fora de escopo da S18” empurrados para S19/S20.

**Fail fast**  
Se G0 falhar, a sprint não deve seguir para G1: volta para alinhamento de escopo.

---

#### 5.2 Gate S18_G1 — Arquitetura de front & contratos de admin

**Pergunta principal**  
A arquitetura do frontend de admin e os contratos de backend estão claros, consistentes e implementáveis sem gambiarras?

**Entradas**

- Proposta de organização de pastas e módulos para admin (Cap. 3, rascunhos ou diagramas).  
- Definição de rotas (`/admin`, `/admin/sources`, `/admin/cases`, etc.).  
- Especificação de contratos de admin:  
  • `GET /admin/sources`;  
  • `GET /admin/sources/{id}`;  
  • `GET /admin/cases`;  
  • `GET /admin/cases/{id}`;  
  • `GET /admin/health` (ou equivalente).

**Critérios de PASS**

- Existe descrição clara (texto e/ou diagrama) das rotas e componentes principais de admin.  
- Campos essenciais dos contratos estão documentados (tipos, semântica, erros esperados).  
- Não há acoplamento da UI a artefatos frágis (por exemplo, parse de arquivos de scorecard sem uma camada de API).  
- A arquitetura respeita a separação: módulo de admin isolado, reuso de layout/componentes base da S17.

**Evidências**

- `out/scorecards/S18_G1_arch_front_and_api.json` com status e lista de contratos aprovados.  
- Paths de docs/diagramas de arquitetura referenciados.

---

#### 5.3 Gate S18_G2 — Journeys & UX do Console de Admin

**Pergunta principal**  
As jornadas principais dos perfis definidos (Operador, Curador, PO) fazem sentido e são navegáveis na UI?

**Entradas**

- Implementação inicial das páginas de admin em ambiente local/homolog.  
- Roteiros simples de navegação:  
  • Operador: ver saúde geral → investigar fontes → revisar casos em atenção;  
  • Curador: focar em fontes sensíveis e casos com dados frágeis;  
  • PO: check pré‑demo.

**Critérios de PASS**

- Rotas `/admin`, `/admin/sources` e `/admin/cases` acessíveis e funcionando.  
- Pessoa que não implementou o código consegue seguir os roteiros com um mínimo de instrução escrita.  
- Existem estados de loading/erro minimamente amigáveis (sem tela branca ou stacktrace bruto).  
- Não há becos sem saída óbvios na navegação.

**Evidências**

- `out/scorecards/S18_G2_journeys_and_ux.json` com status e um resumo de cada jornada testada.  
- Opcional: screenshots ou vídeo curto em `out/evidence/S18_G2/`.

**Relação com métricas**  
M2 e M6 podem ser medidos de forma preliminar, mesmo que o cálculo formal fique para G6.

---

#### 5.4 Gate S18_G3 — Qualidade de implementação de frontend

**Pergunta principal**  
O código do Console de Admin atende ao patamar mínimo de qualidade (build, lint, testes) aceito pela DNA?

**Entradas**

- Código do frontend incluindo admin integrado à SPA.  
- Scripts de build/lint/teste atualizados.

**Critérios de PASS**

- Comando de build (`npm run build`, `pnpm build` ou equivalente) roda verde com as rotas de admin incluídas.  
- Linters (ESLint, TypeScript etc., conforme stack) passam sem erros bloqueantes.  
- Há pelo menos um teste automatizado cobrindo:  
  • renderização da rota `/admin`; e/ou  
  • renderização de componentes centrais de Fontes/Casos.  
- Ausência de gambiarras óbvias em produção (por exemplo, `console.log` deixado, comentários de debug, código morto gritante).

**Evidências**

- `out/scorecards/S18_G3_front_quality.json` com:  
  • status de build;  
  • status de lint;  
  • contagem de testes e pass/fail.  
- Logs resumidos em `out/evidence/S18_G3/` quando necessário.

---

#### 5.5 Gate S18_G4 — Coerência UI ↔ Backend (Fontes & Casos)

**Pergunta principal**  
A UI de admin está mostrando, com alta fidelidade, as mesmas fontes e casos que o backend expõe via APIs de admin?

**Entradas**

- Backend com endpoints de admin disponíveis.  
- UI de Fontes e Casos/Temas integrada.  
- Fixture(s) de dados de referência (cluster controlado de fontes e casos com estados conhecidos).

**Critérios de PASS**

- Em cenário controlado:  
  • **M3 ≥ 0,99** (cobertura de fontes);  
  • **M4 ≥ 0,99** (cobertura de casos/temas).  
- Campos críticos (estado, timestamps principais) batem entre UI e backend, com tolerância pequena quando há diferença (por exemplo, segundos de diferença por causa de refresh).  
- Nenhuma família inteira de fontes ou casos some na UI.

**Evidências**

- `out/scorecards/S18_G4_ui_vs_backend.json` com valores medidos de M3 e M4 e contagens absolutas.  
- Snapshots de respostas de API e, se útil, dumps dos dados exibidos na UI em `out/evidence/S18_G4/`.

**Fail fast**  
Se G4 falhar, o Console de Admin vira painel decorativo; S18 não pode ser declarada pronta.

---

#### 5.6 Gate S18_G5 — Saúde operacional refletida na UI

**Pergunta principal**  
A Visão Geral do Console de Admin reflete corretamente os sinais de health do backend e é rápida o suficiente para ser útil no dia a dia?

**Entradas**

- Mecanismo de health do backend (watchers, scorecards, endpoints).  
- Visão Geral implementada.  
- Cenários de teste simulando: tudo saudável, algumas fontes degradadas, casos em contestação, integrações falhando.

**Critérios de PASS**

- Para cada cenário, os números de fontes saudáveis/degradadas, casos estáveis/em atenção e status de integrações exibidos na UI coincidem com os sinais do backend.  
- **M1 (tempo de carregamento da Visão Geral)** medido e ≤ 1,5 s no ambiente de referência.  
- A UI usa linguagem de produto ("fontes em atenção", "casos em contestação"), não nomes de watchers ou flags internas.

**Evidências**

- `out/scorecards/S18_G5_health_mapping.json` com:  
  • valor de M1;  
  • lista de cenários executados e resultados.  
- Capturas/logs em `out/evidence/S18_G5/`.

---

#### 5.7 Gate S18_G6 — Experiência de operação end‑to‑end

**Pergunta principal**  
Um operador consegue usar o Console de Admin, de ponta a ponta, para entender o estado do Inspectah e investigar problemas usando apenas a UI?

**Entradas**

- Console de Admin completo em ambiente local/homolog.  
- Cenários end‑to‑end, por exemplo:  
  • “Existe alerta de fontes degradadas; identifique uma fonte problemática e descreva seu estado”;  
  • “Encontre um caso em contestação e explique seu estado atual e principais evidências”.

**Critérios de PASS**

- **M2** (tempo da jornada “do alerta à fonte”) medido e ≤ 1,0 s de tempo de UI.  
- **M5 = 1,0** — todas as telas de detalhe usadas nos cenários apresentam resumo + motivo principal.  
- **M6 = 1,0** — em todos os cenários testados, o operador chega a uma tela com contexto suficiente em até 2 cliques a partir da Visão Geral/listas.  
- Feedback qualitativo dos operadores de teste indica que a experiência é compreensível e que não há dependência de “segredo de bastidor” para operar.

**Evidências**

- `out/scorecards/S18_G6_metrics_and_demo.json` com:  
  • valores finais de M2, M5, M6;  
  • descrição dos cenários;  
  • resumo do feedback dos operadores.  
- Se possível, gravações de demo em `out/evidence/S18_G6/`.

---

#### 5.8 Gate S18_G7 — Observabilidade + CI da S18

**Pergunta principal**  
O Console de Admin está minimamente protegido contra regressões silenciosas via CI e observabilidade de frontend?

**Entradas**

- Workflows de CI com build/test de frontend.  
- Logging mínimo de erros de admin (na stack de observabilidade existente ou via logs estruturados/console em ambiente não‑dev).

**Critérios de PASS**

- Pipeline de CI oficial executa:  
  • build do front com rotas de admin;  
  • lint;  
  • pelo menos um teste que falharia se `/admin` quebrasse de forma grosseira.  
- Falhas relevantes em `/admin` (rota removida, componente chave quebrado) fazem a CI falhar.  
- Existe alguma forma de enxergar erros de admin em ambientes além do dev local (mesmo que simplificada).

**Evidências**

- `out/scorecards/S18_G7_ci_and_observability.json` com resumo dos jobs de CI e dos testes que cobrem admin.  
- Paths dos workflows relevantes documentados (ex.: `.github/workflows/_s18_admin_front.yml`).

---

#### 5.9 Gate S18_G8 — GO/NO‑GO da Sprint 18

**Pergunta principal**  
Considerando todos os gates e métricas, a Sprint 18 está pronta para ser integrada como parte estável do Inspectah?

**Entradas**

- Scorecards S18_G0…S18_G7.  
- `docs/sprint_18_overview.md` (wrap humano da sprint).  
- Valores finais de M1…M6.  
- Feedback curto do time (produto, engenharia, operação).

**Critérios de PASS**

- Todos os gates S18_G0…S18_G7 com status PASS.  
- Não há nenhum problema conhecido quecontradiga o espírito da S18 (ex.: painel decorativo, discrepâncias graves UI↔backend, backdoor de canetada aberta).  
- Débitos residuais são documentados e delegados explicitamente para S19/S20.

**Evidências**

- `out/scorecards/S18_G8_go_no_go.json` com:  
  • decisão `GO` ou `NO_GO`;  
  • valores finais de M1…M6;  
  • lista de riscos/débitos e sua destinação.  
- Opcional: `out/evidence/S18_G8/summary.json` com snapshot estruturado da sprint.

---

### 6. Como este capítulo se conecta com os próximos

- O **Capítulo 3** vai transformar cada gate em elementos concretos de repositório:  
  • scripts `bin/s18_g*_*.sh`;  
  • caminhos exatos de scorecards e evidências;  
  • fixtures e datasets de referência;  
  • filemap detalhado ligando tudo isso.

- O **Capítulo 4** vai descrever **como rodar** os gates na prática (ordem, comandos, cenários de demo) e trazer prompts para Codex quando fizer sentido.

A Sprint 18 só estará plenamente alinhada à DNA quando:

1. Todos os gates S18_G0…S18_G8 estiverem especificados (Cap. 2), mapeados para scripts/paths (Cap. 3) e com runbook de execução (Cap. 4);
2. As métricas M1…M6 forem medidas ao menos uma vez em ambiente controlado, com registros em scorecards;
3. O scorecard S18_G8 registrar um `GO` com base em evidências concretas, não em “parece bom”.

A partir daí, o Console de Admin deixa de ser apenas uma ideia ou uma coleção de telas e passa a ser um componente **verificável e auditável** do Inspectah, integrado ao mesmo regime de confiança que o restante do sistema.

