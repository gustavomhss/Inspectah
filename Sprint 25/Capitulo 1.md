# Sprint 25 — Capítulo 1 (v2)
## Contexto, Problema, Objetivos e Escopo

> Versão v2 — Refinado pelo Squad Verdade & Interpretação, Stonebraker, Norvig, Pearl, Percy, Jobs & Conselho. Este capítulo ancora a Sprint 25 no plano macro do Inspectah e estabelece, em linguagem inequívoca, **o que precisa existir ao final da S25** em termos de verdade/fato, camadas, governança, operação e código humano.

---

### 1.1 Contexto: onde a Sprint 25 entra na história do Inspectah

Até o fim da S24, o Inspectah chegou a um patamar onde:

- **Fontes** são entidades de primeira classe, com cadastro, healthchecks e visão de saúde de ingestão (S21).
- **Ingestão 2.0** está em pé (S22): IngestionConfig, IngestionRun, métricas por fonte, painel de ingestão.
- **Interpretação e classificação (S23)** trouxeram ContentItem, InterpreterOutput, Claims, Comitês iniciais e rotas A/B/C por domínio — porém com um **desenho de Sistema de Camadas aquém do rigor exigido**.
- **Debunker v0 e Humano‑no‑loop (S24)** introduziram DebunkIssue, DebunkTask, DebunkDecision e o conceito de contestação estruturada, com fila humana e explicações mínimas.

O que ainda falta é o coração da coisa:

1. Uma **máquina de estados de verdade/fato (TruthState)** que responda, com clareza e trilha de auditoria:
   - em que estado de verdade cada claim está agora;  
   - como e por que ela saiu de estados anteriores;  
   - quais evidências, comitês, debunkers, humanos e políticas participaram da decisão.

2. Um **Sistema de Camadas de validação/interpretação/classificação redesenhado do zero**, com:
   - responsabilidades nítidas por camada;  
   - uso sistemático de Dossiês de Entidade/Caso + Context Service;  
   - defesas adversariais explícitas;  
   - agentes (cérebro) versionados, auditáveis e operáveis via Agent Studio.

3. Uma **governança de promoção/demover** que exista em:
   - modelo de dados (TruthRecord, TruthChangeEvent, PromotionPolicy),  
   - código de domínio legível,  
   - políticas declarativas versionadas,  
   - e telas do Console capazes de mostrar e operar isso com segurança.

A Sprint 25 é o ponto em que o Inspectah deixa de ser “só” um pipeline de ingestão + contestação e se torna, de fato, uma **máquina de verdade/fato v1.5**, preparada para a Fase 2 (Sistema de Blocos, ancoragem em blockchain, reputação avançada). Mesmo sem blockchain automático agora, tudo que nasce na S25 já deve ser **compatível com um futuro livro‑razão imutável**.

---

### 1.2 Problemas centrais que a S25 precisa resolver

#### 1.2.1 Verdade sem máquina de estados formal

Hoje o Inspectah tem rótulos de verdade espalhados (UI, enums, flags), mas não existe uma TruthState machine formal, com:

- conjunto bem definido de estados de verdade (por ex.: `UNDER_REVIEW`, `PROVISIONAL_TRUE`, `UNDER_DISPUTE`, `ESTABLISHED_FACT`, `RETRACTED`, `SUPERSEDED`…);
- transições permitidas entre esses estados, com pré‑condições claras;
- eventos formais que disparam transições (decisão de comitê, decisão de Debunker, decisão humana, nova evidência, mudança de política);
- trilha temporal de mudanças (quem/que camada/que política mudou o quê, quando e com base em quê).

Sem isso:

- não dá para explicar, de forma auditável, por que uma claim está em determinado estado hoje;
- não dá para simular “como teria sido” sob outra política;
- não dá para conectar a Truth‑DB com o futuro Sistema de Blocos de forma limpa.

**Hipótese 1:** uma TruthState machine explícita, implementada em dados (TruthRecord, TruthChangeEvent), código de domínio e políticas, resolve essa lacuna e cria o backbone de verdade/fato do Inspectah.

---

#### 1.2.2 Sistema de Camadas frágil e pouco contratual (débito técnico da S23)

O desenho atual da S23 para o fluxo intérprete → classifier → comitês → Debunker → humano → decisão tem problemas estruturais:

- fronteiras frouxas entre camadas: responsabilidades se sobrepondo;
- uso de contexto de Entidade/Caso pouco sistemático (contexto às vezes entra, às vezes não, sem contrato claro);
- pouca integração com o ThreatModel (flood narrativo, fontes capturadas, prompt injection, operador malicioso);
- “cérebro” dos agentes (instruções, KB, ferramentas) não tratado como entidade de primeira classe, com versionamento, testes e rollback operáveis via Agent Studio;
- reruns e reprocessamentos sem trilha clara do conjunto {versão de agente, versão de política, versão de pipeline} usado em cada decisão.

**Hipótese 2:** redesenhar o Sistema de Camadas com base nos Capítulos 0, 0.5, Adendo 0.A, Adendo 0.5.A e Cap. 7 — e implementá‑lo com código legível, auditável e fácil de manter por humanos — permite:

- ter uma arquitetura de camadas modular, com contratos e invariantes por camada;
- garantir uso consistente do Context Service e dos Dossiês de Entidade/Caso;
- encaixar o ThreatModel na prática (pluralidade de comitês, Debunker orientado a risco, humano‑no‑loop bem posicionado);
- operar e evoluir essas camadas via Console/Agent Studio sem medo de “quebrar tudo”.

---

#### 1.2.3 Governança de promoção/demover implícita e pouco auditável

Hoje, as regras de promoção e rebaixamento de claims a estados de verdade estão espalhadas em prompts, heurísticas ad‑hoc, branches de código e intuição. Isso torna difícil:

- revisar a política de verdade (por exemplo, endurecer domínios sensíveis) sem risco de efeito colateral imprevisível;
- auditar se uma decisão histórica foi coerente com a política vigente na época;
- simular o impacto de uma nova política em cima de um histórico de decisões.

**Hipótese 3:** formalizar uma `PromotionPolicy` versionada e declarativa (por domínio/tipo de claim), suportada por código de domínio simples e bem testado, permite:

- evoluir a política de verdade/fato de forma controlada;
- ligar cada TruthRecord a uma versão específica de política (explicável);
- rodar “simulações” de novas políticas em ambiente de teste usando histórico real.

---

#### 1.2.4 Código opaco e difícil de manter é risco de verdade

Um risco transversal: se o código que implementa a máquina de verdade, o Sistema de Camadas, o Context Service e o Console for um monstro só compreensível por IA, o Inspectah se torna tão opaco quanto as narrativas que ele tenta desmontar.

A Sprint 25 assume como princípio estruturante:

> **Todo código gerado/alterado nesta sprint deve ser legível, auditável e facilmente mantido por humanos competentes, sem abrir mão de rigor, qualidade ou segurança.**

Isso significa:

- módulos pequenos, nomes claros, funções coesas;
- type hints/contratos explícitos, comentários cirúrgicos explicando o porquê das decisões não óbvias;
- testes cobrindo pontos críticos (estado de verdade, políticas, camadas, incidentes);
- zero lógica de negócio crítica enterrada apenas em prompts.

Esse princípio precisa aparecer, de forma concreta, nos artefatos da S25 (filemap, padrões de código, revisões e gates).

---

### 1.3 Objetivos da Sprint 25 (OKRs locais)

Ao final da S25, queremos ser capazes de olhar para o repositório, APIs, Console e documentação e responder “sim” para perguntas concretas. Os objetivos abaixo traduzem isso.

#### O1 — TruthState machine formal, implementada e visível

- Existe um modelo de `TruthState` bem definido, com:
  - estados nomeados e descritos,  
  - transições permitidas e proibidas,  
  - invariantes formais.
- A máquina de estados está implementada em:
  - modelos de dados (por exemplo, `TruthRecord`, `TruthChangeEvent`, campos adequados em Claims/Cases),
  - código de domínio (funções pequenas que aplicam transições válidas, rejeitam inválidas e registram eventos),
  - testes automatizados cobrindo cenários típicos e de borda.
- O Console admin permite ver, para uma claim/caso:
  - estado atual de verdade,
  - histórico de mudanças (timeline de TruthChangeEvents),
  - quem/qual camada/qual política influenciou cada mudança.

#### O2 — PromotionPolicy versionada, declarativa e auditável

- Existe uma entidade/conceito `PromotionPolicy` versionado, armazenado em formato declarativo (ex.: YAML/JSON) + interpretado por código simples.
- Para cada domínio/tipo de claim, a política define:
  - requisitos mínimos de fontes (diversidade, confiabilidade),
  - sinais obrigatórios de comitê/Debunker/humano,
  - thresholds de TruthScore, incerteza e conflito,
  - condições de impedimento (ex.: alta disputa, histórico de reversão).
- Em qualquer TruthRecord, é possível responder:
  - “qual política estava em vigor quando esta promoção/demover aconteceu?”
  - “esta decisão foi compatível com essa política?”
- O Console permite:
  - listar políticas e versões,
  - ver diffs entre versões,
  - simular, em ambiente de teste, o impacto de uma nova política.

#### O3 — Sistema de Camadas redesenhado, integrado a Entidade/Caso e ThreatModel

- O pipeline de camadas S23/S25 está:
  - reespecificado em Cap. 0, 0.5, Adendos 0.A, 0.5.A, 7;
  - implementado com código modular, contratos claros e uso obrigatório do Context Service em domínios críticos;
  - integrando Dossiês de Entidade/Caso como insumo padrão para comitês/Debunker;
  - protegido por defesas adversariais mínimas (pluralidade de comitês, sinais de flood, etc.).
- O Console expõe a **ThoughtTrace** (linha de camadas) e a **DecisionTrace** para cada claim importante.

#### O4 — ThreatModel mínimo em pé, com métricas e gates

- O modelo de ameaças do Cap. 7 está refletido em:
  - estrutura de Fonte (reputação, diversidade),
  - métricas de concentração de fonte, flood narrativo, reversões e incidentes,
  - lógica simples de Debunker orientado a risco.
- Existem scripts e scorecards para gates adversariais (ex.: `S25_G7_threat_model_coverage`, `S25_G8_adversarial_resilience_smoke`).
- Pelo menos um conjunto de cenários adversariais está documentado e executado em ORR (flood, virada sem evidência, círculo de citações, etc.).

#### O5 — Console & Agent Studio prontos para operar Verdade/Fato v1.5

- Telas mínimas implementadas:
  - drill‑down de Claim com ThoughtTrace + DecisionTrace + Dossiês de Entidade/Caso;
  - Agent Studio com visão de contexto, KB, ferramentas, papel da camada e versões de agente;
  - tela de incidentes focada em problemas de verdade/governança;
  - UX de segurança com RBAC e two‑man rule para ações críticas.
- O código de frontend/back (Console/Agent Studio) respeita rigorosamente o princípio de código humano: componentes pequenos, tipos explícitos, APIs versionadas, logs estruturados.

#### O6 — Preparação forte para Fase 2 (Sistema de Blocos & ancoragem)

- Estruturas de Truth‑DB e logs de decisão (TruthRecords, DecisionRecords, etc.)
  - têm IDs estáveis e bem definidos;
  - têm pontos de ancoragem planejados (hashes, agregações) para futura integração com blocos e blockchain.
- Nenhuma decisão arquitetural de S25 impede ou encarece de forma absurda a futura Fase 2.

---

### 1.4 Escopo IN, fora de escopo e dependências

#### 1.4.1 Escopo IN da Sprint 25

1) **TruthState machine & Truth‑DB v1.5**

- definição formal de estados e transições;
- implementação de modelos (TruthRecord, TruthChangeEvent, DecisionRecord ou equivalente);
- integração com Claims/Cases e com a UI admin para visualização mínima.

2) **PromotionPolicy & Governança de verdade**

- definição do metamodelo de políticas (estrutura declarativa + engine de avaliação);
- implementação de ao menos uma política global/por domínio, em ambiente dev/experimentação;
- integração com a máquina de estados e com o Console (visualização, simulação, futura troca controlada).

3) **Redesenho e implementação do Sistema de Camadas (débito S23)**

- aplicar Cap. 0, 0.5, 0.A, 0.5.A, 7 para refazer o fluxo de camadas;
- garantir uso coerente de Entidade/Caso + Context Service;
- expor o pipeline no Console via ThoughtTrace/DecisionTrace;
- manter o código das camadas legível, modular e bem testado.

4) **ThreatModel mínimo implementado**

- implementar sinais/métricas de:
  - concentração de fonte,
  - flood narrativo,
  - reversões sistêmicas,
  - dependência em políticas/agentes;
- criar e rodar scripts de teste adversarial para ORR.

5) **Console & Agent Studio focados em verdade/governança**

- telas e endpoints necessários para:
  - inspecionar claims, estados de verdade e histórico;
  - ajustar agentes de camadas (instruções, KB, ferramentas) com testes/regressão;
  - registrar e tratar incidentes ligados a decisões de verdade;
  - aplicar guardrails de segurança (RBAC, two‑man rule, auditoria).

Em todos esses itens, o requisito transversal é: **código legível, auditável e de fácil manutenção por humanos**, sem concessão de qualidade ou segurança.

---

#### 1.4.2 Fora de escopo (OUT explícito)

- Implementação do Sistema de Blocos completo (blocos, sub‑blocos, componentes, ancoragem automática em blockchain, reputação avançada, bonds, mecanismos econômicos);
- UI pública rica para usuários finais (timeline de verdade com design elaborado, narrativa amigável, export público em massa) — a S25 foca em visão admin/dev;
- sistema de reputação robusto para fontes, usuários e agentes (além de campos/sinais básicos necessários ao ThreatModel);
- internacionalização completa (multi‑idioma, multi‑jurisdição legal) das políticas de verdade;
- refatorações amplas em partes do frontend/backend não tocadas diretamente pela S25.

---

#### 1.4.3 Dependências e riscos

**Dependência 1 — Estabilidade dos artefatos S23/S24.**

- modelos e APIs de S23 (Claims, CommitteeDecision, etc.) e S24 (DebunkIssue, DebunkDecision, filas humanas) precisam estar minimamente estáveis;
- alterações profundas nessas bases durante a S25 podem forçar rework pesado.

**Dependência 2 — Qualidade do redesign do Sistema de Camadas (Cap. 0/0.5/0.A/0.5.A/7).**

- se o redesign não for implementado fielmente (contratos, contexto, threat model), a Truth‑DB fica dependente de um pipeline inconsistente.

**Dependência 3 — Console & Agent Studio como ferramentas reais, não mock.**

- a governança de verdade depende de telas e APIs realmente usáveis por operadores humanos; mock ou protótipo vazio não é suficiente;
- risco de subestimar esforço de UX/engenharia e terminar com um console bonito, porém inútil.

**Dependência 4 — Custo, latência e limites de LLM.**

- S25 empilha Context Service + comitês + Debunker + ThreatModel; se não houver:
  - limites por tipo de operação,
  - caching inteligente,
  - modos de execução (full vs light),
  o sistema pode ficar lento/caro demais para uso real.

Mitigações e detalhes de validação (gates, métricas, scripts, scorecards, ORR) serão descritos e amarrados nos Capítulos 2 (Gates & Validação), 3 (Arquitetura & Filemap) e 4 (Execução & Evidências). Este Capítulo 1 é a âncora de contexto: diz **por que** a S25 existe, **que problemas resolve**, **o que precisa estar verdadeiro no final** e **sob quais restrições de código humano e governança** tudo isso deve acontecer.

