# Sprint 24 – Capítulo 1.2 (v2)
## Problema a resolver e hipóteses – Debunker v0 & Humano-no-Loop

> Squad responsável: Squad Verdade & Interpretação (Pearl, Stonebraker, Norvig, Percy + demais membros Inspectah)
> Escopo: Sprint 24 – Camada de contestação (Debunker v0) e fluxo humano‑no‑loop (HNL), preparando base estrutural para Sprint 25 (Governança de Verdade & Truth‑DB)

---

### 1. Formulação formal do problema central

Ao final da Sprint 23, o Inspectah é capaz de:

- Ingerir fontes diversas (notícias, dados oficiais, documentos, etc.) via pipeline 2.0 (S21–S22).
- Interpretar, classificar e estruturar essas entradas em **claims**, **eventos**, **timelines** e **metadados de risco/qualidade** (S23 – Comitês de Interpretação & Classificação).
- Expor essa informação em interfaces como **Timeline** e **X-Ray**, com algum nível de explicabilidade local.

Porém, falta um componente fundamental do produto: **uma camada institucionalizada de contestação**. Hoje, o Inspectah não possui um mecanismo oficial para responder às perguntas:

1. "O que acontece quando alguém (humano ou agente) desconfia de uma afirmação?"
2. "Como o sistema transforma conflito, dúvida ou falta de evidência em um processo estruturado, com começo, meio e fim?"
3. "Quem decide o que fazer com um claim problemático e como essa decisão é registrada, auditada e reutilizada?"

O problema central da Sprint 24 pode ser formulado assim:

> Projetar e implementar o **Debunker v0**, uma camada de contestação e revisão assistida por humanos (humano-no-loop), que transforma sinais de conflito/incerteza em **DebunkIssues** bem modeladas, conectadas às timelines e claims existentes, processadas por analistas humanos com apoio de comitês de agentes, gerando **DebunkDecisions** auditáveis, que servirão de entrada confiável para a Sprint 25 (governança de verdade e mudanças de estado na Truth‑DB).

Sem essa camada, o Inspectah é essencialmente um sistema de leitura/organização sofisticado, mas **não um sistema de verdade robusta**. Com ela, começamos a construir a capacidade institucional de dizer, com responsabilidade: "isso foi contestado, foi analisado e aqui está a decisão – e o porquê".

---

### 2. Desdobramento do problema em blocos conceituais

O problema central se decompõe em cinco blocos principais, que guiam o restante da Sprint 24:

1. **Detecção & Seleção de casos para contestação**  
   Como sair do universo de todos os claims/timelines e encontrar os casos que **merecem** virar issues formais de Debunker?

2. **Modelagem de DebunkIssue (unidade de contestação)**  
   Como representar, de forma rigorosa, "um caso em disputa" dentro do Inspectah?

3. **Fluxo humano-no-loop (HNL) e orquestração de trabalho**  
   Como transformar uma issue em uma sequência finita de passos para analistas humanos e, quando útil, para agentes?

4. **Modelagem de DebunkDecision (resultado do processo)**  
   Como capturar a decisão de forma estruturada, justificável e reutilizável por outros componentes (S25, UI, relatórios, APIs)?

5. **Integração com a Truth‑DB e preparação para Sprint 25**  
   Como garantir que o que a S24 produz seja consumível de forma simples, estável e robusta pela camada de governança da verdade (S25) e pelo restante do sistema?

Abaixo detalhamos cada bloco, com problemas específicos, hipóteses de solução e restrições.

---

### 3. Bloco 1 – Detecção & Seleção de casos para contestação

#### 3.1. Problema específico

Não é viável (nem desejável) transformar **todos** os claims e timelines em casos de Debunker. Isso levaria a:

- Explosão combinatória de issues irrelevantes.
- Paralisação dos analistas humanos.
- Diluição da atenção em casos de baixo impacto.

Precisamos de um mecanismo para **selecionar poucos casos, mas os casos certos**, que são:

- Tecnicamente desafiadores (conflito real entre fontes ou dados).
- Socialmente sensíveis (saúde, eleições, segurança, finanças públicas, etc.).
- Potencialmente danosos se tratados de forma leviana.

#### 3.2. Hipóteses de sinalização e triagem

H1.1 — **Sinais automáticos a partir de S23**  
Os comitês de interpretação e classificação (S23) já produzem sinais ricos. Podemos usar, entre outros:

- **Conflito entre fontes**: duas ou mais fontes fortes, com reputação alta, sustentando versões incompatíveis do mesmo fato.
- **Incerteza alta**: modelos e comitês retornando "não sei", "informação insuficiente" ou alta dispersão de respostas.
- **Alto risco temático**: categoria de conteúdo marcada como crítica (saúde, política, obras públicas, etc.).
- **Histórico de contestação**: claims ou timelines que já geraram issues anteriores.

H1.2 — **Sinais explícitos de usuário interno**  
Analistas internos (ou operadores) podem sinalizar manualmente que um claim/timeline merece contestação, disparando uma DebunkIssue com motivo explícito.

H1.3 — **Limites de volume por domínio**  
Para evitar explosão de casos, definimos cotas/limites por domínio e por janela de tempo (ex.: até N issues novas por semana em determinado domínio), priorizando casos com score de risco maior.

#### 3.3. Resultado esperado do Bloco 1

- Definição de um **modelo de scoring/ranking de candidatos** a DebunkIssue, usando sinais de S23 + marcações manuais.
- Contrato claro: "quando um claim/timeline cruza determinado limiar, vira um candidato forte a issue".
- Primeiro conjunto de **queries e APIs internas** que retornam "fila de candidatos" para Debunker v0.

---

### 4. Bloco 2 – Modelagem de DebunkIssue (unidade de contestação)

#### 4.1. Problema específico

Sem um modelo de dados rigoroso, "issue de contestação" vira um texto solto, impossível de automatizar e difícil de auditar. Precisamos de uma unidade mínima de trabalho, parecida com um "ticket de disputa de verdade", que seja:

- Fortemente conectado à Truth‑DB (claims, timelines, evidências).
- Legível por humanos e agentes.
- **Versionável**, com histórico de alterações.

#### 4.2. Estrutura conceitual proposta

Uma **DebunkIssue** deve responder, no mínimo:

1. **Contexto alvo**
   - ID de claim principal (ou grupo de claims correlatos).
   - ID(s) de timeline(s) impactadas.
   - Domínio/escopo (ex.: obras públicas, políticas públicas, saúde, etc.).

2. **Pergunta central de contestação**
   - Formulação clara, em linguagem natural disciplinada, por exemplo:
     - "É verdadeiro que a obra X foi concluída em 2022 com custo total de R$ Y?"
     - "É verdadeiro que o indicador Z caiu 10% em relação ao ano anterior?"
   - Essa pergunta deve ser curta, verificável e suscetível a resposta com base em evidências tangíveis.

3. **Motivo da contestação**
   - Conflito entre fontes.
   - Falta de evidência forte.
   - Suspeita de manipulação ou cherry‑picking.
   - Ambiguidade semântica na formulação do claim original.
   - Solicitação explícita de usuário/analista.

4. **Sinais e metadados iniciais**
   - Score de risco.
   - Score de incerteza.
   - Tags temáticas (saúde, orçamento público, clima, etc.).
   - Origem do disparo (automático S23 vs. manual analista).

5. **Estado da issue**
   - OPEN → EM_ANALISE → PENDING_ADDITIONAL_EVIDENCE → READY_FOR_DECISION → CLOSED.
   - Cada transição gerando um evento independente, ligado à linha do tempo da issue.

#### 4.3. Hipóteses de modelagem

H2.1 — **Uma pergunta bem formulada reduz 50% do ruído**  
Ao forçar a DebunkIssue a conter uma pergunta clara e verificável, reduzimos ambiguidade, retrabalho e divergência entre analistas.

H2.2 — **Acoplamento forte com a Truth‑DB simplifica S25**  
Ao sempre referenciar claims/timelines por ID, evitamos duplicidade conceptual. S25 passa a consumir DebunkDecisions diretamente sobre objetos já conhecidos.

H2.3 — **Estados simples, porém rigorosos**  
Uma máquina de estados pequena, porém bem definida, é preferível a um workflow hipercomplexo difícil de generalizar. A riqueza vem dos metadados e evidências, não do número de estados.

---

### 5. Bloco 3 – Fluxo Humano-no-Loop (HNL) & orquestração

#### 5.1. Problema específico

Mesmo com boa triagem (Bloco 1) e boa modelagem de issue (Bloco 2), o Debunker v0 não funciona se **não houver um fluxo concreto para analistas humanos trabalharem**.

Perguntas a responder:

- Quem recebe quais issues e com base em quê?
- O que exatamente um analista vê ao abrir uma issue?
- Que ações ele pode executar?
- Quando consideramos que o trabalho humano está "suficientemente completo" para uma decisão ser tomada?

#### 5.2. Elementos do fluxo HNL

1. **Fila e atribuição**
   - Issues são enfileiradas com base em:
     - score de risco;
     - recência;
     - domínio de expertise.
   - Atribuição pode ser:
     - manual (PO ou líder de squad);
     - automática (regras simples: "issues de obras públicas vão para analista de obras públicas").

2. **Workspace da issue**
   Ao abrir uma DebunkIssue, o analista precisa ver, em um único lugar:

   - Pergunta central.
   - Claim/timeline e contexto direto (trechos de texto, eventos associados).
   - Evidências já ligadas àquele claim (fontes, datas, tipo de evidência).
   - Histórico de decisões preliminares de comitês de S23.
   - Notas ou comentários anteriores sobre aquela issue.

3. **Ações do analista**
   - Solicitar mais evidência (para outra equipe ou fonte específica).
   - Registrar observações qualitativas (ex.: "fonte A contradiz fonte B, mas B parece usar dado mais recente").
   - Pedir um parecer adicional de comitê de agentes (Debunker Assistant Committee).
   - Propor uma **recomendação de decisão** (sem ainda torná‑la final).

4. **Interação com agentes (Debunker Assistant Committee)**
   - Com base em guidelines definidas por Percy, o analista pode invocar comitês especializados para:
     - resumir corpus de evidências;
     - apontar inconsistências lógicas;
     - sugerir estados de confiança em cada hipótese;
     - gerar contrafactuais ou cenários alternativos.
   - Todas as interações com agentes devem ser logadas como parte da trilha da issue.

5. **Encerramento da análise humana**
   - Uma issue só é elegível para DebunkDecision quando:
     - todas as evidências relevantes foram anexadas ou justificadamente descartadas;
     - o analista (ou time) escreveu uma síntese do caso;
     - não há pendências abertas registradas.

#### 5.3. Hipóteses sobre o fluxo HNL

H3.1 — **Um workspace unificado reduz drasticamente a carga cognitiva do analista**  
Ao evitar que o analista precise “caçar” evidências em múltiplas telas/sistemas, aumentamos velocidade e qualidade.

H3.2 — **Agentes como assistentes, não juízes**  
Os comitês LLM servem para organizar, apontar inconsistências e sugerir caminhos; a decisão final continua humana na S24.

H3.3 — **Controle de estados da issue evita zumbis**  
Issues que ficam eternamente em EM_ANALISE ou PENDING_ADDITIONAL_EVIDENCE são problemas de governança e devem ser sinalizadas em métricas (lead time, aging, etc.).

---

### 6. Bloco 4 – Modelagem de DebunkDecision (saída do processo)

#### 6.1. Problema específico

A Sprint 24 não altera estados de verdade globais (isso é foco da S25), mas **precisa produzir decisões sólidas**, pois elas serão os tijolos de base da governança.

Se a DebunkDecision for mal modelada, a S25 será obrigada a reabrir todos os casos para entender o que aconteceu.

#### 6.2. Componentes de uma DebunkDecision

Uma **DebunkDecision** precisa conter, no mínimo:

1. **Metadados básicos**
   - ID da issue.
   - Data/hora da decisão.
   - Responsável (analista, time, comitê).

2. **Conclusão estruturada**
   - Tipo de conclusão, por exemplo:
     - CLAIM_NAO_SUPORTADO;
     - CLAIM_POUCO_SUPORTADO;
     - CLAIM_PLAUSIVEL_MAS_INCOMPLETO;
     - CLAIM_BEM_SUPORTADO;
     - DADOS_INCONCLUSIVOS.
   - Nível de confiança (baixa/média/alta) ou score numérico.

3. **Justificativa textual disciplinada**
   - Parágrafo(s) que respondem diretamente à pergunta da issue, citando evidências específicas (referências a IDs de evidência, não apenas texto solto).

4. **Referências explícitas a evidências**
   - Lista de evidências chave, com tipo (documento oficial, notícia, dataset, etc.), fonte, data, link e ID interno.

5. **Incertezas remanescentes e limitações**
   - Quais aspectos ainda estão em aberto?
   - Que tipo de nova evidência poderia mudar a decisão?

6. **Efeitos esperados sobre o estado de verdade (para S25)**
   - Campo estruturado que indique "intenção" para S25, por exemplo:
     - SUGERE_REBAIXAR;
     - SUGERE_PROMOVER;
     - MANTER_ESTADO_ATUAL;
     - MARCAR_COMO_EM_DISPUTA_PERMANENTE.

#### 6.3. Hipóteses de desenho

H4.1 — **Taxonomia curta de conclusões > longa lista de códigos obscuros**  
Uma lista enxuta de tipos de decisão, bem documentada, facilita consistência entre analistas e entendimento por outras partes do sistema.

H4.2 — **Justificativas sempre acopladas a evidência identificável**  
Nada de "parece que" sem link para evidência. A DebunkDecision precisa ser ancorada em objetos da Truth‑DB.

H4.3 — **Campo de intenção para S25 evita reinterpretações ad hoc**  
Ao explicitar o efeito desejado sobre o estado de verdade, S25 consegue aplicar regras mais claras, sem reabrir o caso do zero.

---

### 7. Bloco 5 – Integração com Truth‑DB e preparação para S25

#### 7.1. Problema específico

A S24 não pode produzir uma ilha. DebunkIssues e DebunkDecisions precisam viver dentro da arquitetura maior do Inspectah, especialmente:

- Truth‑DB (modelo de dados, partições, índices, histórico).
- APIs de consulta (para UI, relatórios, integrações futuras).
- Sistema de Blocos (Fase 2), que exigirá trilhas de auditoria fortes.

#### 7.2. Requisitos de integração

1. **Endereçamento estável**  
   - DebunkIssues e DebunkDecisions devem referenciar claims, timelines e evidências por IDs estáveis definidos por Stonebraker.

2. **Histórico imutável**  
   - Uma vez fechada, uma DebunkDecision não deve ser alterada; qualquer mudança gera uma nova issue ou uma nova decisão, com encadeamento claro.

3. **Consultabilidade**  
   - APIs devem permitir consultas do tipo:
     - "Liste todas as issues abertas para esta timeline.";
     - "Quais decisões já foram tomadas sobre este claim nos últimos 5 anos?";
     - "Quais issues foram fechadas como CLAIM_NAO_SUPORTADO, mas sem evidência oficial?".

4. **Preparação para ancoragem externa**  
   - Mesmo sem blockchain agora, a estrutura deve facilitar, no futuro, gerar "blocos" de decisões e issues para ancoragem em sistemas externos, sem precisar refatorar totalmente o modelo.

#### 7.3. Hipóteses de integração

H5.1 — **Truth‑DB como fonte de verdade única para estado + trilha de contestação**  
Ao tratar DebunkIssues e DebunkDecisions como cidadãos de primeira classe na Truth‑DB, evitamos criar silos (por exemplo, logs paralelos de contestação).

H5.2 — **APIs bem desenhadas reduzem atrito entre squads**  
UI, ingestão e futuras features podem evoluir independentemente se a camada de verdade/contestação expõe contratos estáveis.

---

### 8. Anti-problemas e fronteiras de escopo da Sprint 24

Para manter a Sprint 24 focada e executável, o Squad Verdade & Interpretação define explicitamente o que **não** será feito agora:

1. **Sem sistema de reputação completo**  
   - Nada de pontuação persistente de usuários, staking, slashing ou gamificação de contestação nesta fase.

2. **Sem comunidade aberta**  
   - A Sprint 24 foca em analistas internos / operadores de confiança. A abertura para comunidade (crowdsourcing de contestação) é tema futuro.

3. **Sem blockchain ou âncoras on‑chain**  
   - Toda a ancoragem permanece interna (Truth‑DB, logs, evidências). Ancoragem externa é tratada como fase futura.

4. **Sem reescrever o pipeline de interpretação (S23)**  
   - A S24 consome sinais da S23 e pode sugerir ajustes, mas não refatora o pipeline inteiro.

5. **Sem tentar cobrir todos os domínios de uma vez**  
   - A sprint escolhe um conjunto de domínios piloto (ex.: obras públicas + políticas públicas selecionadas + um conjunto limitado de notícias) para teste profundo.

---

### 9. Hipóteses globais da Sprint 24 (consolidadas)

HGlobal‑1 — **Um Debunker v0 bem modelado em poucos domínios é suficiente para provar o conceito** e justificar expansão posterior.

HGlobal‑2 — **Issues e decisões explicitamente modeladas (DebunkIssue + DebunkDecision) reduzem drasticamente ambiguidade** e permitem que S25 se concentre em regras de transição de verdade, não em arqueologia de casos.

HGlobal‑3 — **Humano-no-loop obrigatório em casos de alto risco é superior a automação total prematura**, equilibrando qualidade e escalabilidade.

HGlobal‑4 — **Trilha de auditoria rica (evidências + justificativas + estados) é mais valiosa do que velocidade pura**: Inspectah é um sistema de verdade confiável, não apenas um agregador de notícias.

HGlobal‑5 — **Ao tratar contestação como cidadão de primeira classe (dados + APIs + UI), criamos a base para produtos futuros** (dashboards de disputa, relatórios de controvérsias, alertas regulatórios, etc.).

---

### 10. Resultado esperado deste sub‑capítulo 1.2

Ao final deste Capítulo 1.2 (v2), o Squad Verdade & Interpretação tem:

- Uma decomposição precisa do problema central da Sprint 24 em cinco blocos de trabalho conceitual.
- Hipóteses claras para cada bloco, prontas para serem traduzidas em **gates (Cap. 2)**, **arquitetura & filemap (Cap. 3)** e **plano de execução (Cap. 4)**.
- Uma fronteira de escopo bem definida, evitando que a Sprint 24 tente abraçar Fase 2 (blockchain, reputação, comunidade aberta) antes da hora.

Os próximos documentos (1.3 – filemap conceitual, 1.4 – visão de execução macro) vão tomar este capítulo como referência obrigatória, garantindo que cada artefato da Sprint 24 responda, direta e explicitamente, aos problemas e hipóteses descritos aqui.

