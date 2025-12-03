# Sprint 29 — Capítulo 4
## Bloco 1 — Papel do Capítulo 4 e plano de execução em waves

Os três primeiros capítulos da Sprint 29 colocaram a base conceitual e estrutural:

- Capítulo 1 definiu o **porquê** da sprint (problema, objetivos, narrativa de sucesso, riscos, não‑metas).
- Capítulo 2 definiu **como vamos medir** se chegamos lá (gates S29_G0–G5, métricas, scorecards, GO/NO-GO).
- Capítulo 3 definiu **onde cada peça mora** na arquitetura e no filemap (backend, frontend, runtime, docs, scripts, evidências).

O Capítulo 4, e especificamente este Bloco 1, entra para responder a pergunta que falta:

> "Como saímos do repositório atual e chegamos, passo a passo, à Sprint 29 100% DONE, com todos os gates em PASS e um bundle de evidências respeitável?"

Este bloco define o papel do Capítulo 4 e o **plano de execução em waves**, que será detalhado nos blocos seguintes.

---

### 1. Papel do Capítulo 4 na Sprint 29

O Capítulo 4 não é uma repetição da arquitetura nem uma recapitulação dos gates. Ele funciona como um **roteiro operacional** de alta resolução:

- traduz o que já foi decidido (escopo, arquitetura, gates) em **tarefas sequenciadas**;
- define **waves de execução**, cada uma amarrada a um subconjunto de gates (G0–G5);
- descreve **comandos concretos** de backend e frontend (pytest, npm, scripts `bin/s29_*`);
- explicita **onde pousam as evidências** e como os scorecards devem ficar ao final de cada wave;
- consolida a **Definition of Done (DoD)** da sprint, ligando o estado técnico (código, testes, CI) ao estado de produto (fluxo configurável por domínio realmente funcionando).

Na prática, o Capítulo 4 é o documento que alguém abre quando pergunta: "tá, e agora, o que eu faço na prática para executar a S29 sem esquecer nada?".

---

### 2. Execução em waves: por que e como

A S29 mexe em quatro camadas ao mesmo tempo:

- domínio de fluxo de agentes (models, schemas, invariantes, serviço);
- API de admin (rotas, tratamento de erro, auth);
- UI de fluxo (página, editor, cliente de API, testes de front);
- runtime & observabilidade (adapter, pipeline, logs, evidências).

Atacar tudo isso de uma vez seria receita para caos. Por isso, o Capítulo 4 organiza a execução em **waves**: blocos de trabalho coesos, com foco claro, checkpoints e gates associados.

Os princípios das waves são:

1. **Cada wave tem um alvo técnico e um gate principal**  
   Por exemplo, a Wave 1 mira o domínio (models/schemas/migrations) e ancora no G1.

2. **Não acumular débito óbvio entre waves**  
   Antes de avançar para API ou UI, o núcleo de domínio precisa estar minimamente estável: migrations aplicam, testes de modelos passam, scorecard G1 está em PASS.

3. **Waves pequenas o suficiente para caber em ciclos curtos**  
   Nada de waves gigantes e nebulosas. Cada wave deve ser fechável em um intervalo razoável, com evidências claras.

4. **Gates como checkpoints formais**  
   Ao final de cada wave, o script do gate correspondente (`bin/s29_gX_*.sh`) é rodado e gera scorecard. Sem PASS, a wave não é considerada concluída.

---

### 3. Mapa das waves da Sprint 29

A S29 é decomposta em cinco waves principais:

1. **Wave 0 — Preparação & Baseline (G0)**  
   - Objetivo: garantir que a sprint começa em terreno firme.  
   - Atividades: criar/atualizar branch, configurar estrutura mínima de pastas/arquivos da S29, validar saúde básica de backend/frontend, verificar que docs e filemap da sprint existem e estão consistentes.  
   - Gate principal: `S29_G0_scope_and_baseline`.

2. **Wave 1 — Domínio de fluxo de agentes (G1)**  
   - Objetivo: fazer com que o fluxo de agentes exista como **entidade de primeira classe** no backend.  
   - Atividades: implementar `AgentFlowConfig`/`AgentFlowStep` (models), schemas Pydantic de entrada/saída, migrations para novas tabelas, testes de modelos/schemas.  
   - Gate principal: `S29_G1_model_and_migrations`.

3. **Wave 2 — API de admin & Validador (G2)**  
   - Objetivo: expor o domínio de fluxo de forma segura e validada na borda do sistema.  
   - Atividades: finalizar `validator.py` com invariantes, integrar validador ao `service.py`, implementar rotas `/admin/agent-flows`, escrever testes de validador e de API.  
   - Gate principal: `S29_G2_api_and_validator`.

4. **Wave 3 — UI de fluxo de agentes (G3)**  
   - Objetivo: dar ao operador uma interface clara para ver e editar o fluxo por domínio.  
   - Atividades: implementar `AgentFlowsPage`, `AgentFlowEditor`, `agentFlowsApi`, tipos TS e testes de UI; integrar com router admin e design system.  
   - Gate principal: `S29_G3_ui_and_frontend_quality`.

5. **Wave 4 — Runtime & Observabilidade + ORR & Bundle (G4, G5)**  
   - Objetivo: colocar o fluxo configurável para valer no pipeline e amarrar a sprint com evidências.  
   - Atividades: implementar `runtime_adapter`, integrar com pipeline de ingestão, criar logs estruturados de execução de fluxo, validar comportamento em domínio piloto, consolidar ORR, gerar bundle de evidências.  
   - Gates principais: `S29_G4_runtime_and_observability` e `S29_G5_orr_and_bundle`.

Esse mapa de waves é a espinha dorsal do Capítulo 4: os blocos seguintes descem o zoom em cada wave.

---

### 4. Conexão entre waves, gates e DoD

Cada wave está diretamente ligada a um subconjunto de gates, e o conjunto completo das waves, quando todas em PASS, leva ao **DoD da Sprint 29**.

- Sem a Wave 0 sólida, a sprint começa em terreno instável (G0 em FAIL) e qualquer evidência posterior fica contaminada.
- Sem a Wave 1, G1 não fecha: não existe modelagem confiável de fluxo em banco, o que torna todo o resto gesso molhado.
- Sem a Wave 2, G2 não fecha: não há API de admin confiável nem validador, então qualquer UI vira casca oca.
- Sem a Wave 3, G3 não fecha: o operador não consegue configurar fluxos de forma segura; a funcionalidade fica restrita a APIs sem UX.
- Sem a Wave 4, G4 e G5 não fecham: o sistema não usa de fato os fluxos configurados no runtime, e a sprint não tem ORR/bundle consistentes.

O DoD da S29, no final do Capítulo 4, só será considerado atingido se:

1. Todas as waves foram executadas.  
2. Todos os gates S29_G0–S29_G5 estão em PASS, com scorecards e evidências nos diretórios esperados.  
3. Pelo menos um domínio piloto está rodando com fluxo de agentes configurável de ponta a ponta (admin → UI → runtime → logs).

---

### 5. O que vem nos próximos blocos do Capítulo 4

Com o papel do Capítulo 4 e o plano de waves estabelecidos, os blocos seguintes vão detalhar:

- **Bloco 2** — Wave 0 e Wave 1 em modo cirúrgico (branch, sanity, domínio, migrations, G1).  
- **Bloco 3** — Wave 2: validador, serviço, rotas de admin, testes e G2.  
- **Bloco 4** — Wave 3: UI de fluxo (página, editor, cliente de API, testes) e G3.  
- **Bloco 5** — Wave 4: runtime, observabilidade, ORR, bundle, integração com CI e Definition of Done completa.

Este Bloco 1 é, portanto, o mapa de navegação do Capítulo 4: mostra por que a execução foi dividida em waves, qual é a função de cada uma e como elas se encadeiam para levar a Sprint 29 até um estado de DONE incontestável.

