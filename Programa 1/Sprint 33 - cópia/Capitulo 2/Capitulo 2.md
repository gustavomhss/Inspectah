# Sprint 33 — Capítulo 2

## Gates, Métricas, Invariantes e DoD da Sprint 33

Este capítulo define o sistema de gates, métricas, invariantes e critérios de aceite da Sprint 33. Ele traduz os objetivos e estados‑alvo descritos no Capítulo 1 em verificações concretas, binárias sempre que possível, que podem ser automatizadas via scripts e validadas em ORR. A S33 segue a filosofia consolidada no projeto: nenhuma sprint é "GO" porque alguém acha que está boa; ela é "GO" porque os gates passam, as evidências existem e os scorecards contam essa história de forma reprodutível.

A Sprint 33 introduz uma camada operacional (OracleOps Cockpit v1 + Fluxo de Incidentes v1) em cima de capacidades já existentes. Por isso, seus gates são organizados em torno de quatro eixos:

1. **Escopo e grounding de operação** (G0);
2. **Modelo de incidentes, domínio de operação e integridade de dados base** (G1);
3. **Cockpit de operação e experiência do operador** (G2);
4. **SLOs, observabilidade aplicada e sinais em produção** (G3);
5. **Runbooks, evidência de operação e aprendizado** (G4);
6. **ORR operacional da S33, integrando tudo acima** (G5).

Cada gate tem: propósito, entradas esperadas (docs, código, artefatos de observabilidade), forma de validação (scripts, checks manuais, sanitys) e um conjunto mínimo de métricas ou invariantes que precisam estar verdadeiros para a sprint avançar.

---

## 2.1 Visão geral dos gates da S33

- **G0 — Escopo e baseline de operação definidos**  
  Garante que o recorte da S33 está claramente identificado: quais fontes críticas, quais pipelines representativos, quais APIs internas e quais SLOs entram na rodada. Sem esse recorte fechado, qualquer conversa sobre cockpit ou incidentes vira genérica demais para ser operável.

- **G1 — Modelo de Incident e domínio de operação coerente**  
  Valida que incidentes existem como entidade de domínio, com ciclo de vida claro, invariantes básicas preservadas (por exemplo: um incidente não pode estar simultaneamente em dois estados incompatíveis, timestamps fazem sentido, severidades seguem enum padronizado) e que os dados associados ao domínio de operação (componentes monitorados, mapeamentos de fontes/pipelines/SLOs) estão consistentes.

- **G2 — OracleOps Cockpit v1 navegável e conectado**  
  Verifica se o cockpit está de fato utilizável: visão geral, navegação por fontes e pipelines do recorte, integração mínima com observabilidade externa e visualização de incidentes ativos/recentes. Não basta "ter rotas"; é necessário que um operador seja capaz de responder perguntas básicas a partir da UI.

- **G3 — SLOs e observabilidade aplicada para o recorte da sprint**  
  Confirma que o conjunto enxuto de SLOs definidos para a S33 está instrumentado, com métricas ligadas a dados reais, consultas verificadas, e pelo menos um subconjunto com alertas mínimos configurados. O gate olha para a ponte completa: SLO → métrica → observabilidade → cockpit.

- **G4 — Runbooks, bundles de evidência e fluxo de aprendizado**  
  Garante que os cenários de incidente priorizados têm runbooks claros, versionados, acessíveis a partir do cockpit e que existe pelo menos um incidente (real ou simulado) documentado de ponta a ponta com evidência consolidada. Também verifica se aprendizados relevantes foram capturados como entradas de backlog.

- **G5 — ORR operacional da S33 (integração)**  
  Gate final que integra os anteriores: a S33 só é "GO" se for possível conduzir uma mini‑ORR operacional na qual alguém, sem ser o autor do código, use o cockpit e o fluxo de incidentes para inspecionar o sistema, reagir a um cenário e localizar as evidências necessárias.

---

## 2.2 G0 — Escopo e baseline de operação definidos

**Propósito:** impedir que a S33 tente cobrir o Inspectah inteiro e acabe não garantindo operação decente de nada. G0 fecha o recorte da sprint e alinha todos os envolvidos sobre "o que é mundo" para esta rodada.

**Entradas esperadas:**
- Documento de escopo operacional da S33 (derivado do Capítulo 1), listando:
  - fontes críticas incluídas na sprint;  
  - pipelines representativos (ingestão → agentes → Truth‑DB) cobertos;  
  - APIs internas essenciais ao cockpit;  
  - SLOs da S33, com descrição mínima (métrica, limiar, janela);
- Mapa de componentes monitorados com identificadores estáveis (para uso em código, métricas, logs e UI).

**Verificações e invariantes:**
- Cada fonte crítica do recorte tem um identificador único e está presente em:
  - console de fontes;
  - mapa de observabilidade (métricas/logs);
  - dicionário usado pelo cockpit.
- Para cada pipeline representativo, há definição clara de início e fim (o que conta como "pediu" e "entregou") para mensurar latência e sucesso.
- Para cada SLO da S33, existe pelo menos um rascunho de métrica concreta (nome de métrica ou consulta) mapeada.

**Critério de aceite:**
- G0 é "PASS" se o doc de escopo estiver completo, revisado pelo squad e não houver componentes "fantasmas" (citados em objetivos, mas ausentes do mapa de componentes e SLOs).  
- Qualquer ambiguidade relevante (por exemplo, dúvida sobre se uma fonte ou pipeline está ou não no recorte) gera "NO‑GO" até ser resolvida.

---

## 2.3 G1 — Modelo de Incident e domínio de operação coerente

**Propósito:** garantir que incidentes não são um improviso de UI, mas uma entidade de domínio sólida, com ciclo de vida claro e dados minimamente bem comportados. Sem isso, qualquer relatório ou aprendizado posterior vira areia movediça.

**Entradas esperadas:**
- Modelo de dados de Incident implementado (migrations aplicadas, schema documentado);
- Enumeração de estados possíveis e regras de transição (mesmo que em nível de doc);
- Lista de tipos de incidentes ou categorias associadas a componentes/SLOs;
- Testes unitários e/ou de integração cobrindo casos básicos de criação, transição de estados e leitura.

**Verificações e invariantes:**
- Um incidente não pode estar simultaneamente em dois estados incompatíveis (por exemplo, "aberto" e "concluído");
- Timestamps de criação e atualização seguem ordem lógica (sem regressões de tempo);
- Severidades pertencem a um conjunto finito bem definido (p.ex.: LOW, MEDIUM, HIGH, CRITICAL);
- Cada incidente do recorte da sprint está ligado a pelo menos um componente ou SLO relevante;
- A API (ou camada de acesso) de incidentes não permite estados inválidos ou transições proibidas.

**Critério de aceite:**
- G1 é "PASS" se todos os invariantes forem validados por testes automatizados e, em uma amostra manual, os incidentes criados se comportarem conforme o modelo esperado.  
- Inconsistências em ciclo de vida, estados "órfãos" ou ausência de ligação com componentes/SLOs geram "NO‑GO".

---

## 2.4 G2 — OracleOps Cockpit v1 navegável e conectado

**Propósito:** verificar que o cockpit não é apenas um conjunto de páginas técnicas, mas uma ferramenta que um operador consegue de fato usar para responder às perguntas básicas de operação.

**Entradas esperadas:**
- UI do OracleOps Cockpit implantada em ambiente de teste (ou dev estável), acessível com credenciais internas;
- Rotas e componentes implementados para overview, visualizações por fonte/pipeline e visão de incidentes;
- Integrações mínimas com observabilidade (links para dashboards, se aplicável).

**Verificações e invariantes:**
- A visão de overview exibe, sem erros, o estado das fontes e pipelines do recorte da S33;
- A navegação por fonte/pipeline funciona para todos os elementos do recorte (sem 404, sem placeholders vazios);
- Incidentes ativos/recentes aparecem de forma consistente na interface;
- Links para observabilidade levam a dashboards ou visualizações válidas (não quebradas);
- A UI é utilizável em condições realistas (sem depender de hacks temporários).

**Critério de aceite:**
- G2 é "PASS" se um operador designado (não necessariamente o desenvolvedor) conseguir, em sessão acompanhada, usar apenas o cockpit para:
  - identificar rapidamente se há algum componente em estado anômalo;
  - navegar até o detalhe de pelo menos uma fonte e um pipeline;
  - ver incidentes ativos ou recentes relacionados ao recorte.

---

## 2.5 G3 — SLOs e observabilidade aplicada para o recorte da sprint

**Propósito:** garantir que os SLOs definidos para a S33 saíram do papel e se tornaram objetos observáveis, com métricas reais e, em alguns casos, alertas acionáveis.

**Entradas esperadas:**
- Lista de SLOs priorizados da S33 (nome, métrica, limiar, janela de observação);
- Consultas de observabilidade (ou equivalentes) implementadas para cada SLO;
- Configurações de alerta mínimas para SLOs críticos;
- Integração do estado dos SLOs com o cockpit (mesmo que de forma resumida).

**Verificações e invariantes:**
- Para cada SLO, existe pelo menos uma consulta que pode ser executada para verificar seu cumprimento em uma janela de tempo recente;
- Para os SLOs com alerta, é possível simular (ou observar) uma violação e ver o alerta disparar pelos canais acordados;
- O cockpit exibe o estado atual (dentro/fora) de pelo menos um subconjunto representativo dos SLOs;
- Não existem SLOs “fantasmas” na lista, sem métrica associada.

**Critério de aceite:**
- G3 é "PASS" se, em ORR, for possível percorrer SLO por SLO da lista da S33 e demonstrar como cada um é observado na prática.  
- SLOs sem métrica associada ou sem forma de verificação prática derrubam o gate.

---

## 2.6 G4 — Runbooks, bundles de evidência e fluxo de aprendizado

**Propósito:** assegurar que a resposta a incidentes não é só boa vontade, mas um processo repetível com documentação útil e evidência reaproveitável.

**Entradas esperadas:**
- Catálogo mínimo de runbooks para cenários priorizados na S33;
- Localização padronizada dos runbooks no repositório;
- Integração de runbooks com o cockpit (links contextuais);
- Pelo menos um bundle de evidência de incidente (real ou simulado) completo;
- Registro de aprendizados/itens de backlog derivados de incidentes.

**Verificações e invariantes:**
- Para cada cenário prioritário, existe um runbook com: pré‑condições, passos, comandos, critérios de sucesso/falha;
- Os runbooks podem ser encontrados tanto navegando pelo repositório quanto via links a partir do cockpit;
- O bundle de evidência inclui, no mínimo: timeline de incidente, referências a logs/dashboards e uma nota de pós‑mortem;
- Pelo menos um aprendizado relevante se materializou em item de backlog ou ajuste concreto (por exemplo, mudança de métrica, ajuste de alerta, melhoria em UI).

**Critério de aceite:**
- G4 é "PASS" se, em uma simulação guiada, for possível escolher um incidente do recorte, seguir o runbook correspondente, localizar o bundle de evidência e apontar os aprendizados registrados.  
- Falta de runbook, evidência incompleta ou aprendizado não capturado gera "NO‑GO".

---

## 2.7 G5 — ORR operacional da Sprint 33 (integração)

**Propósito:** validar, de ponta a ponta, que a combinação de cockpit, incidentes, SLOs, runbooks e evidências produz uma experiência de operação que faça sentido para alguém de fora da implementação direta.

**Entradas esperadas:**
- Todos os gates anteriores (G0–G4) marcados como "PASS";
- Ambiente de teste estável com cockpit e fluxo de incidentes funcionando;
- Roteiro de ORR operacional definido (cenário, papéis, checklist).

**Verificações e invariantes:**
- Uma pessoa que não implementou diretamente a S33 consegue, seguindo o roteiro de ORR, usar o cockpit para:
  - inspecionar o estado do recorte da sprint;
  - identificar um incidente (real ou simulado);
  - seguir o fluxo de incidentes até um estado estável;
  - localizar e interpretar o bundle de evidência;
  - apontar SLOs relevantes e seu estado atual.

**Critério de aceite:**
- G5 é "PASS" se a ORR operacional for concluída dentro de um tempo razoável, sem depender de "atalhos" proibidos (acesso direto a bancos, scripts obscuros, conhecimento não documentado).  
- Se a ORR revelar dependência excessiva de conhecimento tácito ou buracos graves no fluxo, o gate é "NO‑GO" e a sprint precisa voltar para correção.

---

## 2.8 DoD global da Sprint 33

A Sprint 33 é considerada "DONE/GO" quando, e somente quando:

1. Todos os gates G0–G5 estão marcados como "PASS", com scorecards preenchidos e armazenados no padrão do projeto.
2. O OracleOps Cockpit v1 está implantado em ambiente acordado, cobrindo o recorte da sprint, e foi validado por pelo menos uma ORR operacional.
3. O modelo de Incident está implementado, testado e utilizado em pelo menos um incidente real ou simulado documentado.
4. O conjunto de SLOs da S33 está instrumentado, observável e, em parte, visível no cockpit.
5. Os runbooks priorizados e pelo menos um bundle de evidência de incidente estão presentes, versionados e integrados ao fluxo de operação.
6. Os aprendizados da sprint (incluindo falhas dos gates, se houver) foram capturados como itens de backlog ou ajustes concretos, evitando que os mesmos buracos reapareçam nas próximas sprints.

Esse DoD não substitui o detalhamento por tarefa ou por componente, mas estabelece a linha‑de‑chegada mínima para que a S33 possa ser considerada entregue com o nível de rigor e excelência que o Épico E28 exige.

