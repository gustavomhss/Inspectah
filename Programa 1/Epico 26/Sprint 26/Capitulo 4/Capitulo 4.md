# Sprint 26 — Capítulo 4.1 — Modelo de Waves da Sprint

> Arquivo: `docs/sprint_26/cap_4/sprint_26_cap_4_1_modelo_waves.md`
> Função: definir a cadência cirúrgica da execução da S26 em Waves W0–W3, alinhadas ao contrato de Programa/Épico (Cap.1), aos Gates (Cap.2) e ao filemap/invariantes (Cap.3), de forma que o Codex consiga operar sem freestyle.

---

## 1. Visão geral das Waves da S26

A Sprint 26 é a primeira sprint da esteira E26 (Design System & Consoles Inspectah Admin v1). O foco é construir a fundação operacional do design system e preparar o terreno para os consoles críticos (Fontes, Ingestão, Casos & Linha do Tempo).

Para isso, a execução será organizada em quatro waves principais:

- **W0 — Grounding & Sanity da Sprint**  
  Wave de entendimento, validação de contexto e checagens mínimas de sanidade. Nenhum código estrutural novo é introduzido.

- **W1 — Fundação de Design System & Filemap**  
  Wave que cria o esqueleto do Design System, organiza o filemap de frontend para consoles e ajusta scripts/gates basais.

- **W2 — Núcleo de Consoles & Fluxos Críticos**  
  Wave que implementa o núcleo funcional dos consoles prioritários (especialmente Console de Fontes e consolidação de estruturas para Ingestão e Casos).

- **W3 — UX de Casos, Hardening & Limpeza**  
  Wave que refina UX/flows (principalmente visão de casos/linha do tempo), endurece gates e limpa débitos mínimos ainda dentro da S26.

Cada wave tem:

- **Objetivo explícito**, em linguagem de contrato.  
- **Critérios de saída objetivos**, que se conectam a gates G0–G8.  
- **Relação clara com states-of-truth da sprint** (Cap.1.4) e com o filemap/invariantes (Cap.3.2/3.3).

As waves abaixo são a fonte oficial de cadência: qualquer Execution Matrix (Cap.4.2), Protocolo Codex (Cap.4.3) e Plano Operacional (Cap.4.4) deve referenciar W0–W3 exatamente como definidas aqui.

---

## 2. W0 — Grounding & Sanity

### 2.1 Objetivo

Garantir que **Codex e humanos entendem a S26** antes de tocar em código, e que o ambiente local/CI está minimamente saudável para começar.

Em termos de contrato:

- "Ao final da W0, é verdade que Codex tem um resumo consistente de Cap.1–3 e Cap.4.1, e que os scripts básicos de sanidade (G0) rodam green no estado atual do repo."

### 2.2 Escopo

- Leitura estruturada por Codex de:
  - Cap.1 (contexto, mapa Programa/Epico, states-of-truth da S26);
  - Cap.2 (lista de gates, métricas locais, scorecards);
  - Cap.3 (arquitetura, filemap, invariantes, plano de testes);
  - Cap.4.1 (este documento) como referência de cadência.
- Execução **somente** de comandos de inspeção/sanidade, sem tocar em arquivos de código:
  - `git status`, `ls` em pastas relevantes, leitura do filemap;
  - execução seca ou limitada de `bin/ci_local.sh`/gates mínimos, se já existirem.

### 2.3 Critérios de saída

W0 é considerada concluída quando:

1. Existe um **resumo estruturado** gerado pelo Codex contendo:
   - objetivos principais da S26 (referenciando Cap.1.1/1.4);
   - lista dos gates ativos na sprint (Cap.2.1);
   - visão dos componentes tocados (Cap.3.1) e filemap relevante (Cap.3.2);
   - recorte das waves (W0–W3) e sua função.
2. G0 (Ambiente & Repo) está em estado **GREEN** para o baseline atual, ou existe um registro explícito de blockers conhecidos que serão endereçados em tasks de W1.
3. Não há dúvidas abertas sobre escopo grosseiro da S26; qualquer ambiguidade relevante é registrada como risco/nota para Cap.6.

### 2.4 Gates relacionados

- **G0 — Ambiente & Repo**:  
  W0 deve deixar claro se G0 já pode ser rodado integralmente ou se depende de tasks de W1.

W0 **não** aprova features; apenas libera o tabuleiro para execução segura.

---

## 3. W1 — Fundação de Design System & Filemap

### 3.1 Objetivo

Construir a **fundação técnica e estrutural** para o Design System Inspectah Admin v1 e organizar o filemap de frontend/console de forma alinhada ao Cap.3, sem ainda entregar experiência final de usuário.

Contrato em linguagem de verdade:

- "Ao final da W1, é verdade que o Design System tem estrutura mínima criada (pastas, tokens base, componentes skeleton) e que o filemap de frontend da S26 está alinhado ao `sprint_26_cap_3_2_filemap.md`, com scripts de CI/Gates capazes de enxergar e validar esse layout."

### 3.2 Escopo

- Criação/ajuste das pastas de Design System no frontend, seguindo o filemap do Cap.3.2.
- Definição inicial de tokens base (cores, tipografia, spacing) em nível de código, sem ainda consolidar todos os componentes finais.
- Ajustes em scripts de CI/local (`bin/ci_local.sh`, scripts de gates S26 específicos) necessários para rodar com o novo layout.
- Atualizações mínimas em docs de desenvolvimento frontend (se existirem) para refletir o novo filemap.

### 3.3 Critérios de saída

W1 é concluída quando:

1. O filemap previsto em Cap.3.2 está **materializado** no repo:
   - pastas e arquivos principais existem;
   - não há divergências estruturais relevantes.
2. Existem componentes/tokens base do Design System prontos o suficiente para que W2 possa construir consoles em cima deles (mesmo que ainda não estejam visualmente polidos).
3. Scripts de G0/G2/G3 conseguem rodar sem quebrar por causa do novo layout (mesmo que ainda acusem falta de implementação em partes do código).

### 3.4 Gates relacionados

- **G0 — Ambiente & Repo** (rodando contra a nova estrutura).  
- **G2 — Domain Core / Backend** (se houver ajustes mínimos de contratos/DTOs para sustentar o design system).  
- **G3 — Front/UI / APIs externas** (lint/build/tests mínimos do frontend com o novo filemap).

W1 prepara o terreno para W2: depois dela, consoles podem ser implementados em cima de uma base coerente.

---

## 4. W2 — Núcleo de Consoles & Fluxos Críticos

### 4.1 Objetivo

Entregar o **núcleo funcional dos consoles alvo da S26**, priorizando aqueles que destravam Programas/Épicos mais fundamentais (por exemplo, Console de Fontes e estruturas de suporte para Ingestão e Casos).

Contrato em linguagem de verdade:

- "Ao final da W2, é verdade que existe um fluxo funcional mínimo para operar consoles base (pelo menos Fontes e um recorte inicial de Ingestão/Casos), com rotas ligadas ao backend, estados mínimos funcionais na UI e validações essenciais passando em G2/G3/G4 conforme definido em Cap.2."

### 4.2 Escopo

- Implementação dos fluxos mínimos nos consoles prioritários definidos em Cap.1/Cap.3:
  - ex.: listar fontes, cadastrar/editar fonte, visualizar status de ingestão básico, abrir visão inicial de casos.
- Conexão desses consoles com endpoints de backend já existentes ou planejados em Cap.3.2.
- Criação de testes de UI/API mínimos que cubram o caminho feliz dos fluxos críticos.

### 4.3 Critérios de saída

W2 é concluída quando:

1. Os consoles definidos como alvo da S26 têm **fluxos básicos navegáveis** ponta a ponta (mesmo que visualmente simples):
   - usuário consegue executar as principais ações previstas no contrato da sprint;
   - erros críticos retornam feedback mínimo útil.
2. Os gates diretamente ligados a esses fluxos estão em estado **GREEN** (ou existe justificativa explícita e encaminhamento registrado em Cap.6 para qualquer exceção pontual).
3. Não há blockers estruturais para que W3 refine UX, performance e hardening.

### 4.4 Gates relacionados

Dependendo do recorte final de S26, W2 deve impactar principalmente:

- **G2 — Domain Core / Backend** (funcionalidade core por trás dos consoles).  
- **G3 — Front/UI / APIs externas** (consoles rodando, build/testes front).  
- **G4 — Agents & Flows** (se houver qualquer fluxo de agente/automatização ligado aos consoles tocados).

---

## 5. W3 — UX de Casos, Hardening & Limpeza

### 5.1 Objetivo

Refinar a experiência de uso (especialmente em Casos/Linha do Tempo), endurecer a solução entregue em W1–W2 e limpar débitos mínimos que comprometeriam o uso real das features da S26.

Contrato em linguagem de verdade:

- "Ao final da W3, é verdade que os consoles alvo da S26 estão utilizáveis em contexto realista (mesmo que ainda em beta interno), com UX minimamente decente para Casos/Linha do Tempo, gates críticos verdes e sem débitos grosseiros deixados para trás sem registro."

### 5.2 Escopo

- Ajustes de UX e feedback de interface nos consoles críticos (especialmente Casos & Linha do Tempo de Casos), dentro do recorte de S26.
- Hardening de fluxos: tratamento de erros, estados vazios, respostas lentas, bordas óbvias.
- Limpeza de débitos mínimos ainda abordáveis dentro da sprint (ex.: TODOs pontuais, logs ruidosos, warnings triviais na build) — sempre limitado pelo contrato de tempo da S26.

### 5.3 Critérios de saída

W3 é concluída quando:

1. Os consoles alvo da S26 podem ser usados em um **cenário de validação end-to-end** sem fricções inaceitáveis (detalhado em Cap.5.1).
2. Os gates de UX/Frontend/Flows relevantes (especialmente G3, possivelmente G4) estão **GREEN**.
3. Débitos que não cabem na W3 estão registrados em Cap.6.2 como tech_debt/gap, com recomendação de encaixe em sprints futuras.

### 5.4 Gates relacionados

- **G3 — Front/UI / APIs externas** (UX e estabilidade de consoles).  
- **G4 — Agents & Flows** (se houver automações ligadas ao uso dos consoles).  
- **G8 — ORR Local & Evidence Bundle** (na medida em que W3 produz evidências finais para Cap.5).

---

## 6. Relação com Execution Matrix, Protocolo Codex e Plano Operacional

- O **Bloco 4.2 — Execution Matrix** detalhará, por wave, a associação entre:
  - tasks (`S26-T-XXX`),
  - paths autorizados (derivados do Cap.3.2),
  - gates a serem rodados e
  - comandos/scripts canônicos.
- O **Bloco 4.3 — Protocolo Codex** traduzirá W0–W3 em prompts e instruções específicas para o Codex operar, sempre respeitando:
  - ordem W0 → W1 → W2 → W3;
  - limites de paths e comandos;
  - necessidade de evidências após cada conjunto de tasks.
- O **Bloco 4.4 — Plano Operacional** consolidará as tasks atômicas da sprint, cada uma apontando para:
  - wave correspondente,
  - categoria (backend/frontend/infra/tests/docs/gates),
  - artefatos esperados,
  - gates associados,
  - states-of-truth e evidências.

---

## Wrap W3 — Status rápido

- G0–G3 rodando localmente em `feature/programa1_s26_admin_v1` (GO) após integração real do Console de Fontes v2.
- Console de Fontes v2 navegável em `/admin/sources` com listagem, criação/edição e mudança de estado operando com backend; testes RTL/MSW cobrem fluxos básicos.
- Warnings de act removidos nos testes, mantendo logs limpos para G2/G3.
- Próximas waves de documentação: consolidar runbook/ORR (Cap.5) e dívidas (Cap.6) antes do bundle final (G5/G6).

Este Bloco 4.1 é, portanto, o **guia de cadência oficial** da S26: qualquer divergência entre execução real e este modelo de waves deve ser tratada como exceção, registrada em Cap.6 e considerada na avaliação de GO/NO-GO da sprint.
