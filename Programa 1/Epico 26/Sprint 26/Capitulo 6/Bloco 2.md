# Inspectah — Sprint 26 (S26)
## Capítulo 6 — Bloco 6.2
### Dívidas Técnicas da Sprint 26

> Arquivo-alvo no repo: `docs/s26_cap_6_2_dividas_tecnicas.md`
>
> Função: registrar de forma estruturada as **dívidas técnicas geradas ou expostas** pela S26, com ID, risco, contexto, gates afetados e janela sugerida de ataque.  
> Regra: nada de “pendências vagas”. Cada dívida aqui precisa ser rastreável e cobravel.

Formato mínimo por dívida:

- **ID**: `S26-DT-XXX`  
- **Título curto**  
- **Descrição**  
- **Contexto de origem** (task/gate/capítulo)  
- **Gates afetados**  
- **Risco** (baixo/médio/alto, com frase)  
- **Tipo** (frontend / backend / ci & gates / docs & runbooks / UX & operação)  
- **Janela sugerida** (sprint/épico)  
- **Sinal de que saiu do controle** (indicadores práticos)

---

## 1. Dívidas Técnicas de Frontend / Design System

### S26-DT-001 — Cobertura parcial de componentes do Design System Admin v1

- **Título**  
  Cobertura incompleta de componentes admin v1 em `ui/admin`.

- **Descrição**  
  A S26 estabeleceu a base do Design System Inspectah Admin v1 (tokens, layout, componentes principais), mas nem todos os padrões usados historicamente em telas admin existentes foram migrados para dentro de `ui/admin`. Há componentes e padrões antigos ainda espalhados fora do design system.

- **Contexto de origem**  
  - Cap.3 (filemap de `ui/admin`);  
  - Tasks `S26-T-010` e `S26-T-011` (estrutura e tokens);  
  - Learnings 1.1 e 1.2 do Bloco 6.1.

- **Gates afetados**  
  - G1 (Design System Admin v1 estático);  
  - G3 (Frontend Quality & Regression), indiretamente.

- **Risco**  
  - **Médio**: enquanto parte dos padrões estiver fora do design system, mudanças de tema/UX terão que lidar com dois mundos em paralelo, aumentando custo de evolução e chance de regressões seletivas.

- **Tipo**  
  Frontend / design system.

- **Janela sugerida**  
  - S27–S29, junto com evolução de outros consoles admin;  
  - alinhar com épicos de "Admin Cockpit" no roadmap.

- **Sinal de que saiu do controle**  
  - Novas telas admin surgindo com CSS ad-hoc sem passar por `ui/admin`;  
  - regressões visuais frequentes em apenas um subconjunto de telas admin quando tokens são alterados.

---

### S26-DT-002 — Ausência de testes de regressão visual para consoles admin

- **Título**  
  Sem camada automatizada de regressão visual (visual tests) para admin v1 e Console de Fontes v2.

- **Descrição**  
  G1, G2 e G3 cobrem lint, build e testes funcionais, mas não há, ainda, uma camada de testes visuais automatizados (screenshots base vs atual) para detectar regressões de layout/estilo no admin.

- **Contexto de origem**  
  - Cap.2 (definição de gates);  
  - Cap.4.3 (plano de evidências sem suíte visual dedicada);  
  - Learnings 1.4 e 3.3 do Bloco 6.1.

- **Gates afetados**  
  - G1 (Design System Admin v1);  
  - G3 (Frontend Quality).

- **Risco**  
  - **Médio**: regressões visuais podem escapar em mudanças rápidas de tokens/estilos, especialmente em consoles críticos, afetando operação e confiabilidade percebida.

- **Tipo**  
  Frontend / qualidade.

- **Janela sugerida**  
  - S28–S30, de preferência junto com algum épico de "Quality & Observability Frontend".

- **Sinal de que saiu do controle**  
  - Reclamações recorrentes de operadores sobre "tela quebrada" após merges;  
  - hotfixes frequentes apenas para CSS/estilo em produção.

---

### S26-DT-003 — Organização inicial de testes de `features/sources` ainda limitada

- **Título**  
  Estrutura de testes do Console de Fontes v2 precisa ser ampliada.

- **Descrição**  
  Os testes cobrindo fluxos básicos (`S26-T-042`, G2) ainda são focados em caminhos felizes e cenários mais óbvios. Cenários de erro, estados intermediários e combinações de filtros/ordenadores ainda não estão plenamente representados.

- **Contexto de origem**  
  - G2 (sources console flows);  
  - Cap.5.1 (cenários E2E que exercitam só parte dos casos);  
  - Learnings 1.4 e 3.1.

- **Gates afetados**  
  - G2 (diretamente);  
  - G3 (indiretamente, se falhas passam sem serem capturadas).

- **Risco**  
  - **Médio**: bugs comportamentais menos óbvios (combinações de filtros, paginação, ações em lote) podem escapar até a operação.

- **Tipo**  
  Frontend / testes de fluxo.

- **Janela sugerida**  
  - S27–S28, principalmente se o console de fontes ganhar novas features.

- **Sinal de que saiu do controle**  
  - Bugs de fluxo em fontes retornando mais de uma vez;  
  - necessidade de corrigir comportamento em produção sem teste correspondente sendo adicionado.

---

## 2. Dívidas Técnicas de Backend / Contratos

### S26-DT-004 — Formalização incompleta do contrato de `Source` em schema único

- **Título**  
  Modelo de `Source` carece de fonte de verdade plenamente centralizada.

- **Descrição**  
  Apesar de `Source.ts` e `app/sources/schemas.py` estarem alinhados o suficiente para S26, ainda não há um schema único (ex.: OpenAPI/JSON Schema) gerando ambos de forma sistemática. Mudanças futuras podem divergir novamente.

- **Contexto de origem**  
  - G4 (sources API contracts);  
  - Learnings 1.3 do Bloco 6.1.

- **Gates afetados**  
  - G4 diretamente;  
  - G2 indiretamente (já que a UI depende dos contratos).

- **Risco**  
  - **Alto**: contratos divergentes em fontes podem danificar configuração de ingestão e gerar bugs silenciosos (fonte aparentemente configurada, mas com campo crítico ausente ou incorreto).

- **Tipo**  
  Backend / contratos / modelo de domínio.

- **Janela sugerida**  
  - S27–S29, em conjunto com trabalhos de API e ingestão 2.0.

- **Sinal de que saiu do controle**  
  - necessidade de "gambiarras" de parsing no frontend para entender payloads;  
  - erros recorrentes de validação de schema em G4.

---

### S26-DT-005 — Logs e rastreabilidade de mudanças de fonte ainda básicos

- **Título**  
  Histórico de alterações em fontes pouco estruturado.

- **Descrição**  
  S26 melhora a UI e os fluxos de fontes, mas o registro de mudanças (quem alterou o quê, quando) ainda é superficial ou distribuído em logs genéricos. Para incidentes I1–I4, um histórico mais estruturado facilitaria investigação e rollback manual de configuração.

- **Contexto de origem**  
  - Cap.5.3 (runbook de fontes e incidentes);  
  - Learnings 3.2 e 3.3.

- **Gates afetados**  
  - Nenhum gate S26 diretamente, mas impacta futuros gates de auditabilidade / segurança.

- **Risco**  
  - **Médio**: em incidentes graves, pode ser difícil reconstruir rapidamente a sequência de alterações que levaram ao problema.

- **Tipo**  
  Backend / auditabilidade / observabilidade.

- **Janela sugerida**  
  - S30–S32, potencialmente junto com epics de Truth-DB / Evidence Vault para fontes.

- **Sinal de que saiu do controle**  
  - investigações pós-incidente demoradas;  
  - necessidade de "ler logs brutos" para entender mudanças de fonte.

---

## 3. Dívidas Técnicas de CI, Gates & Evidências

### S26-DT-006 — Scripts de gates ainda sem camada de testes próprios

- **Título**  
  Scripts `bin/s26_g*` sem suíte de auto-teste.

- **Descrição**  
  Os scripts de gates (G0–G6) da S26 são peças críticas, mas ainda não possuem testes dedicados (ex.: rodar com mocks, verificar parsing de scorecards, comportamento de falha). Bugs neles podem invalidar a confiança nos resultados de CI.

- **Contexto de origem**  
  - Cap.2 (gates S26);  
  - Cap.4.3/4.4 (plano de evidências e tasks de gates);  
  - Lessons processuais sobre gates como "cerca elétrica".

- **Gates afetados**  
  - Todos (G0–G6), pelo papel meta.

- **Risco**  
  - **Médio**: um bug num script pode marcar falsa segurança (GO onde deveria ser NO-GO) ou travar CI por motivos artificiais.

- **Tipo**  
  CI & gates.

- **Janela sugerida**  
  - S28–S30, atrelado a um épico de "Quality of Gates".

- **Sinal de que saiu do controle**  
  - necessidade constante de rodar scripts manualmente para "entender o que aconteceu";  
  - divergência entre o que desenvolvedores veem localmente e o que CI reporta.

---

### S26-DT-007 — Ausência de scorecards agregados por domínio (Admin/Fontes)

- **Título**  
  Scorecards ainda muito gate-centrados, pouco domínio-centrados.

- **Descrição**  
  Os scorecards de S26 são por gate (G0–G6), o que é ótimo para CI, mas ainda não há visão consolidada por domínio (Admin, Fontes) que ajude a responder: "como está a saúde geral de Admin? E de Fontes?".

- **Contexto de origem**  
  - Cap.2 e Cap.5.2 (ORR);  
  - Learnings processuais sobre ORR.

- **Gates afetados**  
  - G6 potencialmente (bundle/ORR), se vier a agregar.

- **Risco**  
  - **Baixo a médio**: leitura de saúde de domínio depende de juntar várias peças manualmente; perdemos visibilidade macro.

- **Tipo**  
  CI & métricas.

- **Janela sugerida**  
  - S29–S31, talvez junto com épicos de Observabilidade.

- **Sinal de que saiu do controle**  
  - discussões recorrentes em ORR do tipo "ninguém sabe dizer se Admin como um todo está saudável".

---

## 4. Dívidas Técnicas de Docs, UX & Operação

### S26-DT-008 — Runbook de fontes v1 ainda sem exemplos completos por tipo de fonte

- **Título**  
  Runbook de fontes carece de exemplos específicos por tipo (RSS, API, dataset).

- **Descrição**  
  O `runbook_operacao_fontes_v1.md` define fluxos F1–F4 e incidentes I1–I4, mas ainda pode estar genérico demais para tipos de fontes diferentes. Operadores podem precisar de guidance mais concreto, especialmente para APIs mais complexas.

- **Contexto de origem**  
  - Cap.5.3 (runbooks);  
  - Learnings 3.1 e 3.2.

- **Gates afetados**  
  - G5 (Docs & Runbooks).

- **Risco**  
  - **Médio**: operadores podem cometer erros de configuração por falta de exemplos, aumentando a frequência de incidentes I1–I4.

- **Tipo**  
  Docs & operação.

- **Janela sugerida**  
  - S27–S28, em paralelo com ampliação de tipos de fontes suportadas.

- **Sinal de que saiu do controle**  
  - on-call recorrente pedindo ajuda a dev para configurar fontes específicas;  
  - incidentes repetidos com o mesmo tipo de fonte.

---

### S26-DT-009 — Material de treinamento para operadores ainda implícito

- **Título**  
  Ausência de material de onboarding explícito para uso do Console de Fontes v2.

- **Descrição**  
  A S26 cria runbooks e cenários E2E, mas não há ainda um material simples de onboarding (doc ou walkthrough) voltado para novos operadores, explicando o console em linguagem não-técnica.

- **Contexto de origem**  
  - Cap.5.1 e Cap.5.3;  
  - Learnings 3.1, 3.2 e 3.4.

- **Gates afetados**  
  - Nenhum diretamente; mas G5 pode futuramente incorporar isso.

- **Risco**  
  - **Baixo a médio**: curva de aprendizado mais lenta para novos operadores; dependência maior de transferência oral de conhecimento.

- **Tipo**  
  Docs & UX de operação.

- **Janela sugerida**  
  - S28–S30, potencialmente junto com rollout mais amplo do console.

- **Sinal de que saiu do controle**  
  - alta variabilidade no uso do console entre operadores;  
  - muitos erros operacionais nos primeiros dias de entrada de novos membros.

---

## 5. Como gerenciar e acompanhar estas dívidas

- Cada `S26-DT-XXX` deve ser registrada também em sistema de tracking (issue/épico), com link para este doc e para os artefatos relevantes (código, logs, incidentes).  
- Planejamentos de sprints futuras (S27+) devem consultar explicitamente este bloco para puxar dívidas a serem atacadas, priorizando:
  - riscos **altos** e dívidas que impactam dominios críticos (fontes, ingestão, Truth-DB, Debunker);  
  - dívidas que fortaleçam gates estruturais (G2, G3, G4, G5, G6).
- Revisões de programa (Ex.: checkpoints de Programa 1) devem verificar se as dívidas mais antigas continuam justificadas ou se estão virando "déficit estrutural".

---

## 6. Síntese do Bloco 6.2

O Bloco 6.2 tira as dívidas técnicas da S26 do campo do "depois a gente vê" e coloca em uma lista estruturada, com:

- IDs (`S26-DT-001` a `S26-DT-009`) que podem ser referenciados em issues, PRs e reuniões;  
- ligações claras com gates, capítulos e learnings;  
- avaliação de risco e janela sugerida;  
- sinais práticos de quando cada dívida começa a doer demais.

Na prática, isso permite que S27–S65 negociem conscientemente **quais dívidas carregar** e **quais quitar**, em vez de descobrir, tarde demais, que o cheque especial técnico estourou.

