# Sprint 24 – Capítulo 3.2 – Gates & Métricas da Arquitetura de Verdade, Contestação e Humano‑no‑Loop (v2)

## 1. Objetivo do subcapítulo 3.2

Este subcapítulo define, de forma exaustiva e operacional, **todos os gates, métricas e critérios de GO/NO‑GO** relacionados à **arquitetura da S24**:

- Debunker v0 (com humano‑no‑loop).
- Pipeline de contestação (do input até a decisão final).
- Integrações com S23 (interpretação/classificação), S25 (Truth‑DB & Governança de Verdade) e com a UI de timeline/xray (S19).

Nada da arquitetura é considerado "aceito" até que **todos os gates abaixo** estejam implementados, evidenciados e com scorecards verificados. Este documento serve como **contrato de qualidade** entre o Squad Verdade & Interpretação e o restante da organização.

---

## 2. Visão Geral dos Gates de Arquitetura da S24

A arquitetura da S24 é avaliada em três eixos principais:

1. **Modelo conceitual de contestação e Debunker v0**  
   - Como representamos casos de contestação, estados, transições e papéis (debunker, proponente, revisores humanos, comitês de agentes, etc.).

2. **Topologia técnica (serviços, filas, storage, Truth‑DB)**  
   - Como os componentes se conectam, como os dados fluem e como garantimos auditabilidade, reprocesso e isolamento de falha.

3. **Superfície de uso (APIs, UI, hooks para agentes)**  
   - Como S24 é usada pelas outras sprints, por operadores humanos e pelos próprios agentes.

Cada eixo é materializado em **gates de arquitetura** (G24‑3.2‑XX) com:

- Descrição clara do que está sendo cobrado.  
- Evidências obrigatórias.  
- Métricas associadas, quando aplicável.  
- Critério de GO/NO‑GO binário.

---

## 3. Lista de Gates de Arquitetura – S24 (G24‑3.2‑XX)

### G24‑3.2‑01 – Modelo de Estados de Contestação & Verdade alinhado ao Squad

**Meta**: ter um **modelo formal de estados** para contestação e verdade, aprovado pelo Squad Verdade & Interpretação (Pearl, Stonebraker, Norvig, Percy) e consistente com S23 e S25.

**Requisitos mínimos**:

- Tabela/diagrama de estados para contestação: por exemplo, `OPEN`, `UNDER_REVIEW_AI`, `WAITING_HUMAN`, `DECIDED`, `ESCALATED`, `CLOSED`.  
- Tabela/diagrama de estados de verdade afetados por S24: por exemplo, `UNDER_REVIEW`, `PROVISIONAL`, `ESTABLISHED_FACT`, `UNDER_DISPUTE`, `RETRACTED`.  
- Definição explícita das transições permitidas entre estados, com requisitos de evidência para cada transição.  
- Ligação clara entre eventos de contestação e `TruthChangeEvents` da S25.

**Evidências obrigatórias**:

- Documento de modelo de estados (mermaid, diagrama UML ou similar).  
- Tabelas/tipos no modelo de dados refletindo esses estados (ex.: enums ou colunas bem definidas).  
- Comentários de revisão aprovados pelo Squad Verdade & Interpretação.

**Critério de GO**: nenhum endpoint, job ou UI de S24 pode usar estados "ad hoc" fora desta tabela. Qualquer uso deve bater 1:1 com o modelo.

---

### G24‑3.2‑02 – Arquitetura de Componentes de S24 isolada e reprocessável

**Meta**: garantir que o Debunker v0 e o pipeline de contestação sejam **componentes isolados**, com fronteiras claras e capacidade de reprocesso.

**Requisitos**:

- Diagrama de componentes mostrando:
  - Serviço/API de contestação.  
  - Módulo Debunker v0 (comite de agents + humano‑no‑loop).  
  - Truth‑DB / camada de persistência de contestação.  
  - Integração com S23 (feed de claims/eventos) e S25 (TruthChangeEvents).  
- Cada componente expõe **interfaces claras** (APIs, filas, contratos de dados) e tem fronteiras de responsabilidade descritas.  
- Reprocesso: possibilidade de reexecutar decisões de Debunker para um caso (ou lote) sem quebrar integridade da timeline de verdade.

**Evidências**:

- Diagrama de componentes (arquitetura lógica e, se necessário, física).  
- Arquivo de contrato de interfaces (ex.: `docs/interfaces/s24_contestation_api.md`).  
- Descrição de fluxo de reprocesso com exemplos.

**Critério de GO**: qualquer pessoa do Squad consegue, olhando o diagrama + docs, explicar o fluxo de ponta a ponta sem "buracos".

---

### G24‑3.2‑03 – Modelo de Dados de Contestação & Debunker compatível com Truth‑DB

**Meta**: garantir que o modelo de dados de S24 não vire um silo, mas sim um **subconjunto bem integrado ao Truth‑DB**.

**Requisitos**:

- Definição de entidades centrais (ex.: `ContestationCase`, `DebunkerReview`, `HumanDecision`, `ContestEvidenceLink`, `ContestationOutcome`).  
- Cada entidade tem chaves claras para se ligar a:
  - Claims/eventos de S23.  
  - TruthRecords/TruthChangeEvents de S25.  
  - Timelines/cases de S19.
- Definição de índices mínimos para consultas típicas (por claim, por usuário, por período, por estado, por tipo de contestação).

**Evidências**:

- Diagrama ER ou equivalente.  
- Esquemas de tabelas/coleções em arquivo de migração ou schema central.  
- Lista de queries canônicas que devem performar bem (ex.: "todas as contestações abertas para este claim nos últimos 90 dias").

**Critério de GO**: o modelo passa por revisão de Stonebraker e Norvig e é declarado "apto" para produção v0 sem gambiarras estruturais.

---

### G24‑3.2‑04 – Arquitetura de Humano‑no‑Loop integrada e verificável

**Meta**: garantir que o papel do humano no Debunker v0 seja **primeira classe** na arquitetura, não um remendo em cima da automação.

**Requisitos**:

- Representação explícita de tarefas humanas: fila de decisões, estados da tarefa, quem decidiu o quê e quando.  
- Hooks para UI de analistas (painel de Debunker) com estados bem definidos (ex.: "em análise", "precisa de mais evidência", "decidido").  
- Registro obrigatório de justificativa humana para decisões que mudam estado de verdade ou encerram contestação.  
- Capacidade de auditar: listar todas as decisões humanas que afetaram um claim/timeline.

**Evidências**:

- Diagrama de fluxo humano‑no‑loop com entradas e saídas.  
- Modelo de dados com tabelas/campos de auditoria (quem, quando, o quê, por quê).  
- Descrição de uma "trilha de auditoria" completa para pelo menos 2 casos de exemplo.

**Critério de GO**: qualquer decisão humana relevante deixa rastro completo (sem campos opcionais críticos) e é recuperável via Truth‑DB/consulta de auditoria.

---

### G24‑3.2‑05 – Integração com S23 (Interpretation & Classification Layer)

**Meta**: garantir que o Debunker v0 enxergue o **contexto interpretado** dos claims/eventos, e não apenas o texto bruto.

**Requisitos**:

- Definição de contrato de dados entre S23 e S24 (ex.: `InterpretedClaim`, `EntityMap`, `RiskScore`, `ClassificationLabels`).  
- Mapeamento de quais atributos S24 consome diretamente (ex.: tipo de claim, domínio, entidades envolvidas, risco).  
- Política clara de fallback quando S23 não estiver disponível ou não tiver interpretado ainda.

**Evidências**:

- Documento de contrato S23→S24.  
- Exemplo real (ou simulado) de payload completo trafegando no fluxo.  
- Testes de contrato (mesmo que iniciais) garantindo compatibilidade.

**Critério de GO**: S24 nunca depende de "chutar" o tipo de claim; sempre recebe um pacote interpretado ou sabe lidar com ausência de forma controlada.

---

### G24‑3.2‑06 – Integração com S25 (Truth‑DB & Governança de Verdade)

**Meta**: garantir que qualquer decisão do Debunker v0 e do humano‑no‑loop seja **refletida de forma estruturada** no Truth‑DB.

**Requisitos**:

- Uso consistente de `TruthChangeEvents` para qualquer mudança de estado de verdade causada por S24.  
- Definição de como outcomes de contestação (ex.: `UPHOLD`, `OVERTURN`, `PARTIAL`) se traduzem em mudança de estado da verdade.  
- Nenhuma escrita direta em tabelas centrais de verdade (TruthRecords) sem passar pelo mecanismo de eventos.

**Evidências**:

- Mapeamento S24→S25: tabela de "outcome de contestação" → "evento de verdade".  
- Diagrama de fluxo de eventos do ponto de vista de S25.  
- Exemplo completo de caso de contestação afetando uma timeline em S19 (com o conjunto de eventos registrado).

**Critério de GO**: qualquer auditor consegue reconstruir o histórico de verdade olhando apenas para os eventos; S24 não cria atalhos opacos.

---

### G24‑3.2‑07 – Arquitetura de Logs, Métricas e Observabilidade mínima

**Meta**: garantir que a arquitetura de S24 já nasça com **observabilidade suficiente** para detectar abuso, erro e regressão.

**Requisitos**:

- Definição mínima de métricas:
  - Número de contestações por dia, por domínio.  
  - Tempo médio até primeira resposta automática (Debunker).  
  - Tempo médio até decisão humana final.  
  - Percentual de decisões automáticas revertidas por humano.  
  - Percentual de contestações procedentes vs improcedentes.
- Logs estruturados para cada etapa crítica (recebimento da contestação, atribuição ao Debunker, decisão de comitê, decisão humana, publicação de evento de verdade).  
- Integração básica com o stack de observabilidade do Inspectah (S18/S19/Sxx já definidos).

**Evidências**:

- Lista de métricas + nomes canônicos (ex.: `inspectah_s24_contestations_total`).  
- Exemplo de logs estruturados de um caso completo.  
- Painel inicial ou consulta padrão que mostre, em ambiente de teste, algumas dessas métricas.

**Critério de GO**: é possível responder perguntas básicas de saúde do Debunker v0 usando apenas as métricas/logs definidos aqui, sem "logs soltos".

---

### G24‑3.2‑08 – APIs de Contestação e Debunker v0 versionadas e documentadas

**Meta**: garantir que a superfície pública de S24 (APIs) seja **clara, estável e documentada**, evitando acoplamento frágil com futuros produtos.

**Requisitos**:

- API para:
  - Criar nova contestação (usuário final ou operador).  
  - Listar contestações de um claim/timeline.  
  - Buscar detalhes de um caso.  
  - Registrar decisões humanas.  
- Versionamento explícito (ex.: `/api/v1/contestation/...`).  
- Documentação em formato OpenAPI ou equivalente.

**Evidências**:

- Spec OpenAPI ou similar com todos os endpoints expostos.  
- Exemplo de chamadas HTTP completas (curl/httpie) de ponta a ponta.  
- Confirmação dos squads que consomem essas APIs (timeline/xray, console admin) de que a superfície é suficiente para a v0.

**Critério de GO**: nenhum consumidor precisa "adivinhar" campo ou endpoint; tudo está descrito na spec.

---

### G24‑3.2‑09 – Proteções Mínimas contra Abuso e Uso Malicioso

**Meta**: garantir que a arquitetura preveja **limites e salvaguardas** contra uso malicioso da contestação (spam, DDoS, flooding de casos).

**Requisitos**:

- Política de rate‑limit para criação de contestações por usuário/IP/fonte.  
- Sinalização de casos suspeitos (ex.: muitas contestações vazias ou mal formadas).  
- Capacidade de bloquear temporariamente contestações para uma fonte/usuário em caso de abuso.  
- Registros de quem aplicou bloqueios e por quê (auditoria).

**Evidências**:

- Documento de política de abuso.  
- Fluxo arquitetural mostrando onde o rate‑limit e bloqueios são aplicados.  
- Cenários de exemplo (simulados) onde a proteção entra em ação.

**Critério de GO**: não é possível derrubar o Debunker com uma chuva de contestações simples sem que as proteções sejam ativadas.

---

### G24‑3.2‑10 – Simplicidade operacional e caminho claro de evolução

**Meta**: garantir que a arquitetura de S24 seja **enxuta o suficiente** para v0, mas com caminho óbvio de evolução.

**Requisitos**:

- Limitar o número de componentes obrigatórios na v0 (evitar micro‑serviços desnecessários).  
- Documentar explicitamente quais partes são "escalares" (podem ser replicadas, shardadas, etc.) e quais são centralizadas.  
- Listar 3–5 melhorias futuras planejadas (ex.: reputação de fontes, comitês especializados por domínio, automação maior na decisão final), sem implementá‑las agora.

**Evidências**:

- Diagrama anotado com "v0" vs "futuro".  
- Seção no doc de arquitetura com o mapa de evolução.  
- Avaliação do Squad de que v0 é "small enough to win" e "big enough to matter".

**Critério de GO**: a arquitetura não trava a evolução, mas também não tenta resolver S30 antes da S24.

---

## 4. Métricas Globais de Arquitetura – S24 (acima dos gates individuais)

Além das métricas específicas por gate, a S24 herda métricas globais de arquitetura que devem estar **pelo menos parcialmente instrumentadas** já na v0:

1. **Tempo médio de ciclo de contestação (end‑to‑end)**  
   - Da criação da contestação até a decisão final registrada no Truth‑DB.  
   - Meta inicial: ter números estáveis e monitoráveis, mesmo que ainda não otimizados.

2. **Cobertura de trilha de auditoria**  
   - Percentual de decisões de verdade impactadas por S24 que possuem uma trilha de auditoria completa (eventos + decisões humanas + justificativas).  
   - Meta v0: 100% das decisões que mudam estado de verdade precisam ter trilha completa.

3. **Taxa de inconsistências entre S24 e S25**  
   - Número de casos em que a contestação diz uma coisa e o estado final de verdade diz outra, sem evento explicando.  
   - Meta v0: 0 inconsistências conhecidas.

4. **Estabilidade arquitetural**  
   - Número de mudanças estruturais de schema ou de contratos de API exigidas após o GO da S24.  
   - Meta: minimizar mudanças "quebradoras" na v0.

Essas métricas são detalhadas e refinadas no Capítulo 2 (Gates & DoD da Sprint), mas aqui ficam registradas como **guia arquitetural obrigatório** para qualquer decisão em S24.

---

## 5. Critérios de GO/NO‑GO de Arquitetura para a S24

A S24 só pode ser considerada **GO** do ponto de vista arquitetural se:

1. **Todos os gates G24‑3.2‑01…G24‑3.2‑10 estiverem com evidências completas** e scorecards em estado PASS/GO.  
2. O Squad Verdade & Interpretação validar que:
   - O modelo conceitual de contestação + verdade está coerente com S23 e S25.  
   - O modelo de dados é consistente com o Truth‑DB e não cria um silo paralelo.  
   - A arquitetura de humano‑no‑loop é de primeira classe (não remendo).  
   - A superfície de APIs e integrações é suficiente para v0.
3. Não existam **"atalhos" não documentados** (writes diretos, scripts avulsos) que bypassem os componentes oficiais.

Qualquer gate em estado FAIL implica **NO‑GO arquitetural** da S24, independentemente de outros capítulos estarem verdes.

---

## 6. Riscos Arquiteturais e Como os Gates 3.2 os Mitigam

### 6.1 Risco: Debunker v0 virar um silo paralelo de verdade

- **Sintoma**: decisões de contestação não sincronizadas com Truth‑DB, dois "mundos" de verdade.  
- **Mitigação**: G24‑3.2‑03 e G24‑3.2‑06 garantem modelo de dados integrado e uso obrigatório de eventos de verdade.

### 6.2 Risco: Humano‑no‑loop ser apenas uma nota de rodapé

- **Sintoma**: decisões humanas importantes sem registro, interface improvisada, ausência de trilha de auditoria.  
- **Mitigação**: G24‑3.2‑04 obriga modelagem explícita de tarefas humanas e rastro completo.

### 6.3 Risco: Arquitetura complexa demais para v0

- **Sintoma**: excesso de serviços, filas, dependências; dificuldade de operar.  
- **Mitigação**: G24‑3.2‑02 e G24‑3.2‑10 exigem simplicidade operacional e um caminho de evolução controlado.

### 6.4 Risco: Sistema vulnerável a abuso ou flood de contestações

- **Sintoma**: Debunker sobrecarregado, filas incontroláveis, degradação de serviço.  
- **Mitigação**: G24‑3.2‑07 e G24‑3.2‑09 exigem métricas de saúde e proteções básicas.

### 6.5 Risco: Acoplamento frágil com S23, S25 e UI

- **Sintoma**: qualquer pequena mudança em S23/S25 quebra S24; UI precisa "adivinhar" campos.  
- **Mitigação**: G24‑3.2‑05, G24‑3.2‑06 e G24‑3.2‑08 forçam contratos explícitos, versionamento e documentação.

---

## 7. Evidências Esperadas por Tipo

Além das evidências específicas por gate, a S24 deve produzir, para a arquitetura:

- **Diagramas**:
  - Estados de contestação e de verdade.  
  - Componentes e fluxo de dados.  
  - Fluxo humano‑no‑loop.

- **Contratos**:
  - Interfaces S23→S24, S24→S25, S24→UI.  
  - Especificações de APIs públicas de contestação.

- **Schemas**:
  - Entidades centrais no Truth‑DB relacionadas à contestação e Debunker.  
  - Índices e constraints relevantes.

- **Cenários de referência**:
  - Pelo menos 3 exemplos completos de fluxo de contestação (procedente, improcedente, parcialmente procedente) passando pela arquitetura inteira.

Essas evidências se conectam diretamente aos Capítulos 4.x (Execução) e 5.x (Validação & Evidências), mas são definidas aqui como **requisitos mínimos de arquitetura**.

---

## 8. Alinhamento com Outras Sprints e Capítulos

- **S23**: fornece claims e interpretações; qualquer mudança no contrato de saída de S23 deve ser refletida nos gates G24‑3.2‑05 e G24‑3.2‑03.  
- **S25**: consome os eventos de verdade produzidos por S24; G24‑3.2‑06 é o contrato de casamento entre contestação e verdade.  
- **S19 (Timeline & XRay)**: consome o estado de contestação para exibir o "raio‑X da verdade"; a arquitetura de S24 deve expor dados suficientes via APIs/queries para que o usuário veja não apenas o estado atual, mas também o porquê.

O Capítulo 3.2 funciona como **ponte de qualidade** entre arquitetura e os capítulos de Execução & Evidências. Ninguém deveria implementar ou commitar código de S24 sem que estes gates estejam claros e aprovados.

