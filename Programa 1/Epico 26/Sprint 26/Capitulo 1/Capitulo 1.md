# Inspectah — Sprint 26 (S26) — Capítulo 1
## Contexto, Problemas a Resolver e Enquadramento no Programa 1

### 1. Visão Geral da Sprint

**Sprint:** S26  
**Programa:** Programa 1 — Consolidação & Consoles Full  
**Épicos foco:**  
- **E26 — Design System & Consoles Admin v1 (fundação visual e de interação)**  
- **E27 — Sources & Ingestion Ops v2.0 (primeiro recorte: CRUD & ON/OFF de fontes)**

**Objetivo macro da S26:**

Colocar o Inspectah em um novo patamar de operação interna ao **criar o Design System Inspectah Admin v1** e **reconstruir o Console de Fontes em cima desse design system**, já suportando **CRUD completo de fontes** e os fluxos básicos de **ativar/desativar fontes** de forma auditável.

S26 é a **primeira sprint do Programa 1**. Ela define o “chão” visual e operacional sobre o qual todas as próximas sprints (S27–S32) vão construir. Se S26 for mal feita, todo o Programa 1 vira um castelo em areia.

### 2. Squad Responsável (núcleo de S26)

Para S26, o núcleo responsável combina **execução cirúrgica**, **UI/UX impecável** e **disciplina de engenharia front-end**:

- **Andy Grove** — Chief Execution & Scope Surgeon  
  Responsável por manter S26 brutalmente focada: nada de escopo lateral fora do contrato, nada de “nice to have” que comprometa a entrega do núcleo.

- **Bret Victor** — Chief UI/UX & Interaction Architect  
  Responsável pela visão de interação, clareza de telas admin, hierarquia visual e princípios do Design System Admin v1.

- **Kent C. Dodds** — Lead Front-End & DX Architect  
  Responsável pela implementação sólida em React/TypeScript, padrões de componentes, ergonomia para desenvolvedores e testes.

- **Michael Stonebraker** — Truth-DB & Data Access Advisor  
  Responsável por garantir que o console de fontes reflita corretamente a realidade de dados e os invariantes de ingestão.

- **Gerald Weinberg** — Quality & Testing Architect  
  Responsável por assegurar que o design system e o console de fontes nasçam com testes, inspeção sistemática de defeitos e critérios de qualidade explícitos.

- **Karl Popper** — Falsification & Evidence Architect  
  Responsável por pressionar o squad a explicitar hipóteses, riscos e critérios de refutação (como saber se o design system está errado, confuso ou insuficiente).

- **Steve Jobs** — Product & Experience Curator  
  Responsável por manter a obsessão com simplicidade, consistência e prazer de uso para o operador, mesmo em um console técnico.

O Product Owner da sprint é você. Este capítulo explicita o contrato que esse squad precisa honrar em S26.

### 3. Contexto Atual do Produto (pós S25)

Na visão consolidada pós-S25, o Inspectah já possui:

- Backends e pipelines funcionando para ingestão, classificação e armazenamento de informação.  
- Consoles e telas admin criadas ao longo das sprints, porém **heterogêneos em estilo, componentes e padrões de interação**.  
- Uma visão clara, no Programa 1, de que precisamos chegar a um estado **v0.8 operável internamente**, com consoles coerentes, cockpit de casos e governança de verdade visível.

Porém, no estado atual:

- Cada console parece ter nascido de uma época e estilo diferente.  
- Operar **fontes** ainda exige conhecimento implícito, leitura de logs e, em alguns casos, uso de terminal para destravar situações.  
- Não existe um **Design System Admin** formalizado, versionado e tratável como ativo de produto.  
- A experiência de quem opera o sistema é frágil, inconsistente e difícil de documentar em runbooks repetíveis.

S26 responde diretamente a essa lacuna.

### 4. Problemas que S26 Precisa Resolver

#### 4.1 Problema 1 — Ausência de um Design System Admin consistente

Hoje:

- Componentes, tipografia, espaçamentos, estados de erro, loading e vazio variam de console para console.  
- Não há uma **biblioteca de componentes única** a partir da qual novos consoles devam ser construídos.  
- Cada dev “resolve” sua tela com soluções ad hoc, o que aumenta custo de manutenção e dificulta a evolução.

Consequências:

- Dificuldade para qualquer operador criar um **modelo mental único** de uso dos consoles.  
- A cada nova tela, o time re-discute padrões de UI, cores, espaçamento, etc.  
- Qualquer tentativa de melhorar a UX de forma global vira um projeto caro e de alto risco.

S26 precisa **criar o Design System Inspectah Admin v1** como um artefato concreto:

- Conjunto inicial de tokens (cores, tipografia, espaçamentos, bordas, sombras, estados).  
- Biblioteca mínima, porém sólida, de componentes para consoles admin (layout de página, navegação lateral, tabelas, filtros, formulários, modais, toasts, banners de estado, etc.).  
- Princípios explícitos de interação, acessibilidade mínima e legibilidade.

#### 4.2 Problema 2 — Console de Fontes frágil, inconsistente e pouco operável

Hoje, a gestão de fontes sofre com:

- Fluxo de **CRUD de fontes** pouco amigável ou parcialmente dependente de scripts/configs fora da UI.  
- Falta de clareza no que é obrigatório, qual o impacto de cada campo e como cada tipo de fonte se comporta.  
- Pontos de operação críticos (ativar, desativar, pausar, retomar) que não são claros ou não têm trilha auditável consistente.  
- Pobreza de feedback visual (erros pouco explicativos, falta de estados de confirmação, mensagens ambíguas).

Consequências:

- Medo de fazer alterações em fontes em produção.  
- Dependência de “guardião de conhecimento” para operações simples.  
- Maior risco de incidentes de ingestão por configuração equivocada ou mal compreendida.

S26 precisa **reconstruir o Console de Fontes em cima do novo design system** com as seguintes propriedades de base (detalhadas em Cap.2, mas já contextualizadas aqui):

- **CRUD completo** (criar, ler, atualizar, arquivar/desativar) para fontes.  
- Ações de **ON/OFF/pausa/retomada** claras, com mensagens de confirmação, efeitos previsíveis e logs de atividade.  
- Layout que respeite o modelo mental do operador (visualização da lista, filtros básicos, detalhamento da fonte, visão de impacto).  
- Campos obrigatórios e opcionais explícitos, com ajuda contextual para evitar erros básicos de configuração.

#### 4.3 Problema 3 — Falta de um “contrato visual” para as próximas sprints (S27–S32)

O Programa 1 depende de uma sequência de consoles robustos: Ingestão, Agentes/Fluxos, Debunker, Truth Console, Evidence Vault, Case Cockpit.

Se S26 não definir um **contrato visual e de interação sólido**, cada sprint futura terá de:

- Discutir e reinventar padrões básicos de UI.  
- Investir energia em alinhar expectativas entre design e engenharia.  
- Lidar com cicatrizes de decisões ruins tomadas em S26.

S26 precisa entregar um **Design System Admin v1 que seja:

- **Minimalista, mas completo o suficiente** para sustentar os consoles de S27–S32 sem precisar recomeçar.  
- Documentado (mesmo que em nível v1) em um formato que devs e designers consigam consumir com clareza.  
- Validado com pelo menos um console real (Fontes) operando em cima dele.

#### 4.4 Problema 4 — Operação pouco documentável e pouco treinável

No estado atual, mesmo que os consoles funcionem, é difícil:

- Escrever **runbooks** objetivos (passo a passo) para operadores novos.  
- Conduzir treinamento baseado em fluxos previsíveis e telas consolidadas.  
- Garantir que, diante de um incidente com fontes, qualquer operador treinado seja capaz de agir com segurança.

S26 precisa garantir que a combinação **Design System + Console de Fontes revisado** permita, ao final da sprint:

- Escrever um runbook enxuto, mas claro, para operação básica de fontes.  
- Criar material mínimo de onboarding (screens + descrição de fluxos) que não seja constrangedor.

### 5. Enquadramento de Escopo (In / Out) para S26

#### 5.1 Escopo “IN” — O que S26 obrigatoriamente cobre

Em alto nível (os detalhes de gates e filemap ficam para Cap.2 e Cap.3), S26 cobre:

1. **Definição e implementação do Design System Inspectah Admin v1**:
   - Tokens básicos (cores, tipografia, espaçamento, bordas, estados).  
   - Componentes nucleares para telas admin (layout, sidebar, header, tabela, formulário, modal, toast, banners de estado, botões primário/secundário/perigo, tags/badges).

2. **Refatoração do Console de Fontes** para usar o Design System Admin v1:
   - Lista de fontes com filtros básicos.  
   - Tela de detalhe/edição de fonte.  
   - Fluxos de criação/edição/exclusão/arquivamento controlados pela nova UI.  
   - Ações de ativar/desativar fontes com confirmação explícita.

3. **Alinhamento conceitual com E27 (Sources & Ingestion Ops v2.0)**:
   - Garantir que o modelo de dados de fontes que aparece na UI está coerente com o modelo de ingestão definido nas sprints de ingestão anteriores.  
   - Preparar terreno para que, em S27, possamos adicionar **histórico de ingestão e métricas** sem precisar re-arquitetar o console de fontes.

4. **Mínima base para runbooks de operação de fontes**:
   - A sprint precisa sair com um conjunto de fluxos claramente identificáveis que serão material de runbook em Cap.4.

#### 5.2 Escopo “OUT” — O que S26 explicitamente não cobre

Para manter foco e proteger a sprint contra inchaço, S26 NÃO cobre:

1. **Design System público (UI externa)** — S26 foca exclusivamente no **Design System Admin**, voltado para consoles internos.  
2. **Consolidação completa de todos os consoles admin existentes** — apenas o Console de Fontes será migrado nesta sprint; Ingestão, Debunker, Truth Console, Evidence Vault e Case Cockpit entram em sprints futuras (S27–S32).  
3. **Métricas avançadas de ingestão, healthscore completo e dashboards complexos** — isso é assunto primário de S27 e seguintes.  
4. **Simulação de políticas de verdade, Debunker v1 completo, Evidence Vault e Case Cockpit** — pertencem a E29–E32, tratados em sprints posteriores.  
5. **Theming avançado (dark mode, múltiplos temas, customização por usuário)** — S26 define um tema padrão sólido; suporte a temas adicionais é dívida consciente para futuro.

### 6. Dependências, Premissas e Restrições

#### 6.1 Dependências técnicas

- **Código-base atual dos consoles admin** precisa estar estável e compilando em main (ou branch base da sprint).  
- A pipeline de build e testes de frontend (S18/S20) precisa estar funcional para permitir feedback rápido nas mudanças de UI.  
- Precisamos ter clareza sobre o **modelo de dados de fontes** atual (campos, invariantes, tipos de fonte) para não criar uma UI que mente sobre a realidade.

#### 6.2 Premissas de produto e operação

- Operadores de fontes continuarão sendo, no curto prazo, um público técnico (analistas/engenheiros de dados, produto, engenharia) — não precisamos otimizar para usuário leigo nesta sprint, mas precisamos otimizar para **clareza, previsibilidade e estabilidade**.  
- S26 não tenta “reinventar” a semântica de fontes; ela respeita as decisões de modelo de dados já tomadas e melhora a forma de operá-las.

#### 6.3 Restrições de escopo e qualidade

- Nenhum componente visual crítico do console de fontes deve permanecer fora do novo design system — o objetivo é **zero componentes “órfãos”** na tela principal de fontes após S26.  
- Toda introdução de novos componentes deve ser acompanhada de **pelo menos um nível básico de teste** (snapshot, unitário ou de interação, conforme definido em Cap.2 e Cap.3).  
- Modificações em endpoints ou modelos de backend devem ser mínimas, apenas quando estritamente necessárias para viabilizar a UI ou corrigir inconsistências.

### 7. Personas e Casos Canônicos que Guiam S26

Para manter foco no que realmente importa, S26 será guiada por um conjunto mínimo de personas e casos canônicos:

- **Persona 1 — Operador de Fontes (Admin Técnico)**  
  Responsável por cadastrar novas fontes, ajustar cadências, pausar/retomar fontes problemáticas e responder a incidentes de ingestão.

- **Persona 2 — Analista de Ingestão**  
  Consome o console de fontes como ponto de partida para entender por que determinado dado está (ou não está) chegando ao sistema.

- **Persona 3 — Engenheiro de Plataforma / SRE interno**  
  Usa o console de fontes como uma das peças do quebra-cabeça em incidentes, e precisa confiar que a UI não mente sobre o estado do sistema.

Casos canônicos (que serão detalhados em Cap.4):

1. Cadastrar uma nova fonte de notícias oficial e colocá-la em operação.  
2. Pausar uma fonte problemática após detecção de erro recorrente.  
3. Revisar configuração de uma fonte antiga, ajustando parâmetros críticos sem quebrar ingestão.  
4. Auditar rapidamente quem alterou uma fonte e quando, durante um incidente.

### 8. Critérios de Sucesso (Visão Qualitativa)

Os critérios formais de sucesso (gates, métricas e DoD) serão detalhados no **Capítulo 2**. Do ponto de vista deste Capítulo 1, consideramos S26 bem-sucedida se, ao final da sprint, as seguintes afirmações forem verdadeiras em espírito:

1. Qualquer membro do time consegue reconhecer, em segundos, que o Console de Fontes e futuros consoles fazem parte de um **mesmo universo visual coerente**.  
2. Um operador técnico consegue aprender, em menos de 30 minutos de onboarding guiado, a **cadastrar, ativar, pausar e revisar fontes** usando apenas a UI.  
3. O squad consegue apontar, black-on-white, qual é o **Design System Inspectah Admin v1** (documento, pasta, componentes) e como ele será estendido nas próximas sprints.  
4. O trabalho feito em S26 reduz, não aumenta, a inércia para implementar Ingestão, Debunker, Truth Console, Evidence Vault e Case Cockpit nas sprints seguintes.

Este Capítulo 1 define o **porquê** e o **que** de S26. Os próximos capítulos (2–4) vão transformar esse contexto em gates, filemap e plano de execução brutalmente concreto.

