# Sprint 24 — Capítulo 3 (macro) v2  
Arquitetura & Filemap da Camada de Contestação (Debunker v0 + Humano-no-Loop)

---

## 3.0 Visão Geral da Arquitetura da S24

### 3.0.1 Papel da S24 na máquina de verdade do Inspectah

A Sprint 24 materializa a **camada de contestação** do Inspectah — o Debunker v0 com humano-no-loop — posicionada entre a camada de interpretação/classificação (S23) e a camada de governança/Truth-DB (S25).

O pipeline lógico completo fica assim:

1. **S21–S22 — Ingestão 2.0 por Fonte**  
   Fontes são cadastradas, normalizadas e executadas. O sistema produz **ingest runs**, **eventos brutos normalizados** e **evidências primárias** (documentos, links, datasets) associados a casos/temas.

2. **S23 — Interpretação & Classificação**  
   Comités de agentes convertem o conteúdo ingressado em **claims estruturados** (TruthClaims provisórios) com metadados de contexto, risco e confiabilidade. Saída principal para a S24:
   - Claims marcados como **controversos**, **de alto impacto** ou **com conflito de evidências**,  
   - Sinais de incerteza de modelo (disagreement dos comitês, baixa confiança, etc.),  
   - Histórico de evidências utilizadas para sustentar/contestar cada claim.

3. **S24 — Contestação (Debunker v0 + humano-no-loop)**  
   A S24 recebe claims e timelines suspeitas ou de alto impacto e as transforma em **DebunkIssues**. Cada issue é decomposta em **rounds** e **tasks**, trabalhadas por:
   - comitês de agentes especializados em checagem (Debunker Agents),  
   - revisores humanos (human-no-loop) quando necessário,  
   - pipelines de coleta/validação de evidências suplementares.  
   A S24 **não grava verdade final**, mas produz **DebunkOutcomes** que recomendam mudanças de estado de verdade e documentam o porquê.

4. **S25 — Governança da Verdade & Truth-DB**  
   Com base nos DebunkOutcomes e nas evidências anexadas, a S25 promove/rebaixa states de TruthRecords no Truth-DB: UNDER_REVIEW → PROVISIONAL → ESTABLISHED_FACT → UNDER_DISPUTE → RETRACTED, etc. Toda alteração de estado é registrada como TruthChangeEvent com links para DebunkIssues, evidências e logs decisórios.

A S24 é, portanto, **a camada de briga intelectual formalizada**: onde claims são desafiados, testados, fatiados em perguntas específicas e respondidos com rigor, e onde o sistema garante que nenhuma verdade “sensível” seja promovida sem passar por uma arena de contestação bem especificada.

---

## 3.1 Blocos de Domínio e Responsabilidades

### 3.1.1 Entidades principais da S24

A arquitetura da S24 se organiza em torno dos seguintes blocos de domínio (modelos de dados e conceitos de negócio):

1. **DebunkIssue**  
   - Representa um **caso de contestação** aberto contra um ou mais claims/timelines.  
   - Sempre vinculado a pelo menos um **TruthClaim** vindo da S23 e, opcionalmente, a um **TruthRecord/Timeline** já existente (quando a contestação é sobre algo previamente estabelecido na S25).  
   - Campos principais (conceituais, detalhamento em S24 Cap 3.x.x de dados):
     - `issue_id` (ID estável),  
     - `source_type` (claim, timeline, external_report, user_flag, etc.),  
     - `linked_claim_ids[]`,  
     - `linked_timeline_ids[]`,  
     - `risk_level` (low/medium/high/critical),  
     - `status` (OPEN, IN_REVIEW, AWAITING_HUMAN, RESOLVED, ESCALATED),  
     - `created_by` (agent committee vs humano),  
     - timestamps e metadados de origem.

2. **DebunkRound**  
   - Um issue pode passar por vários **rounds** de verificação. Cada round é um ciclo de perguntas/respostas:  
     "Dado o estado atual da evidência, este claim se sustenta?"  
   - Campos principais:
     - `round_id`, `issue_id`,  
     - `round_type` (AUTO_AGENT_ONLY, AUTO_PLUS_HUMAN, HUMAN_ONLY),  
     - `round_status` (PENDING, RUNNING, WAITING_FOR_HUMAN, COMPLETED),  
     - métricas de confiança/convergência dos agentes (ex.: spread de opiniões, variação de scoring entre comitês).

3. **DebunkTask**  
   - Unidade atômica de trabalho dentro de um round:  
     "Verifique se esta estatística está correta na fonte X",  
     "Confirme a data deste evento",  
     "Leia o relatório oficial Y e diga se ele suporta a afirmação".  
   - Pode ser atribuída a:
     - um agente automático (LLM),  
     - um revisor humano,  
     - ou uma combinação (agente propõe, humano revisa).  
   - Campos principais:
     - `task_id`, `round_id`, `task_type` (FACT_CHECK, SOURCE_COMPARE, CONSISTENCY_CHECK, etc.),  
     - `assigned_to` (agent_id ou human_id),  
     - `task_payload` (prompt estruturado, links para evidências, parâmetros),  
     - `task_result` (resposta estruturada, conclusão, score),  
     - `task_status` (PENDING, RUNNING, NEEDS_HUMAN_REVIEW, DONE, DISCARDED).

4. **DebunkOutcome**  
   - A saída consolidada de um issue, após um ou mais rounds:  
     "Claim confirmado", "Claim parcialmente verdadeiro", "Claim rejeitado", "Informação insuficiente".  
   - É **o insumo oficial** para a S25.  
   - Campos principais:
     - `outcome_id`, `issue_id`,  
     - `outcome_type` (CONFIRMED, PARTIALLY_TRUE, FALSE, INSUFFICIENT_DATA, INCONCLUSIVE),  
     - `recommended_truth_state_change` (ex.: PROVISIONAL→ESTABLISHED_FACT, ESTABLISHED_FACT→UNDER_DISPUTE, etc.),  
     - `confidence_score` (0–1 ou escala calibrada),  
     - `explanation` (texto estruturado, referencia a evidências),  
     - `linked_evidence_snapshot_id`.

5. **EvidenceSnapshot**  
   - Congela o **conjunto de evidências** relevantes que sustentaram o resultado de um issue/round:  
     fontes utilizadas, versões dos documentos, links para datasets, prints importantes, etc.  
   - Importante para garantir que, se a fonte mudar no futuro, continuemos sabendo **em qual estado do mundo** a decisão foi tomada.

6. **DebunkAuditTrail**  
   - Registro de **toda ação relevante** no ciclo de contestação:
     - quem abriu o issue,  
     - quem aprovou cada round,  
     - decisões tomadas pelos agentes,  
     - alterações manuais,  
     - motivos de escalonamento/fechamento.  
   - É o "log forense" da S24, projetado para ser fácil de consultar pela S25, pelo Squad de Governança e, mais tarde, por auditorias externas.

### 3.1.2 Serviços e camadas lógicas

Sobre esses blocos de domínio, a arquitetura da S24 é organizada em camadas:

1. **Camada de API Debunker (HTTP/REST)**  
   - Exposta via app FastAPI existente (`inspectah.api`).  
   - Rotas principais (conceituais, detalhes de path/método virão em subcapítulos 3.2/3.3):
     - `POST /debunk/issues` — abrir novo issue,  
     - `GET /debunk/issues/{issue_id}` — consultar estado completo,  
     - `POST /debunk/issues/{issue_id}/rounds` — abrir novo round,  
     - `POST /debunk/tasks/{task_id}/human-response` — humano registra resposta,  
     - `GET /debunk/issues?status=...` — listagens para painel,  
     - endpoints de consulta de EvidenceSnapshot/AuditTrail.

2. **Camada de Orquestração Debunker**  
   - Serviços internos que sabem **quais tasks criar, quando escalar para humano**, como combinar resultados dos agentes em um DebunkOutcome.  
   - Regras definidas em colaboração estreita com Percy (comitês de agentes) e Pearl (modelo de verdade).  
   - Implementada como **serviços de domínio** (classes/funções puras + adaptadores para banco/filas) para manter testabilidade.

3. **Camada de Acesso a Dados (Truth-DB / Debunk-DB)**  
   - Usa o mesmo stack do backend atual: SQLModel + SQLAlchemy + Postgres.  
   - Tabelas específicas da S24 são isoladas por prefixo (`debunk_...`) e com chaves estrangeiras claras para claims/timelines/TruthRecords.  
   - Design orientado a **queries reais** (Norvig + Stonebraker):
     - listar issues por estado, risco, fonte, claim, timeline,  
     - verificar histórico de outcomes para um claim,  
     - observar quais DebunkTasks foram mais usados para alterar estados de verdade.

4. **Camada de Integração com S23 e S25**  
   - Entrada: eventos/outputs da S23 que disparam criação de DebunkIssues.  
   - Saída: DebunkOutcomes notificados para a S25 via API interna/bus de eventos.  
   - Mantida **sem acoplamento circular**: S23 e S25 só falam com S24 via contratos estáveis.

5. **Camada de Telemetria & Logs**  
   - Todo caminho da contestação é logado:
     - criação de issue,  
     - criação/fechamento de round,  
     - execução de task,  
     - geração de outcome,  
     - chamadas ao Debunker pelos comitês de S23 e pelos módulos da S25.  
   - Métricas serão conectadas aos gates de S24 (G3/G4) e à observabilidade global.

---

## 3.2 Arquitetura de Frontend para a S24

### 3.2.1 Princípios de UI/UX para Debunker v0

O frontend da S24 precisa atender a três perfis de uso:

1. **Analista humano (Debunker/Humano-no-loop)**  
   - Enxerga uma **fila de issues** priorizada por risco/urgência.  
   - Consegue mergulhar num issue, ver claims relacionados, evidências, rounds e tasks abertas.  
   - Consegue registrar decisões/respostas humanas de forma guiada (sem texto livre caótico e sem forçar leitura de tudo).

2. **Admin/PO/Curador**  
   - Enxerga **painéis de saúde** da contestação: quantos issues abertos, quantos resolvidos, SLA por risco, gargalos, etc.  
   - Enxerga a relação entre DebunkIssues e estados de verdade (quantas verdades foram alteradas com base em DebunkOutcomes, por tipo, tema, fonte…).

3. **Outros módulos do Inspectah (Timeline/XRay, Consulta)**  
   - Precisam mostrar sinalizações visuais de que determinado claim/timeline está ou foi alvo de contestação:
     - badges em timelines,  
     - links "ver histórico de contestação" no XRay,  
     - aviso na consulta: "Esta informação foi contestada em X issues".

### 3.2.2 Principais páginas e componentes

No **frontend/inspectah-ui**, a arquitetura de S24 será organizada em torno de um módulo dedicado, por exemplo `src/modules/debunk/`:

1. **Páginas**
   - `DebunkDashboardPage`  
     - Lista issues por estado/risco, gráficos de throughput e SLA, filtros por tema/fonte/caso.  
   - `DebunkIssueDetailPage`  
     - Visão 360º de um issue: claims vinculados, timeline relevante, rounds, tasks, outcomes, audit trail.  
     - Painel para interação humano-no-loop (responder tasks, aprovar rounds, marcar necessidade de mais evidência).
   - `DebunkQueuePage` (opcional, pode ser parte do dashboard)
     - Fila de issues esperando atribuição ou revisão humana.

2. **Componentes**
   - `DebunkIssueList` — lista issues com filtros, paginação e indicadores de risco.  
   - `DebunkIssueHeader` — resumo de issue (status, risco, fonte, claims relacionados).  
   - `DebunkRoundsTimeline` — linha do tempo dos rounds do issue.  
   - `DebunkTasksPanel` — painel para execução de tasks (com views específicas para human e agent outputs).  
   - `EvidenceSnapshotViewer` — viewer de evidências congeladas.  
   - `DebunkAuditTrailLog` — histórico linear de eventos de contestação.

3. **Hooks & Clients**
   - `useDebunkIssues` — busca e pagina issues.  
   - `useDebunkIssueDetail` — carrega issue + rounds + tasks + outcomes.  
   - `useDebunkActions` — funções para criar rounds, responder tasks, fechar issue.  
   - Client HTTP dedicado: `debunkClient.ts` com funções tipadas mapeando a API Debunker.

4. **Integração com Timeline/XRay/Consulta**
   - `TimelineXRay` passa a exibir badges/links quando um claim/timeline tiver issues associados.  
   - `ConsultationPage` pode exibir, junto da resposta, um indicativo de contestação: ex.: "Esta resposta foi contestada em N issues" com link para DebunkIssueDetail.

---

## 3.3 Arquitetura de Backend para a S24

### 3.3.1 Serviços principais no backend

No backend Python/FastAPI, a S24 será implementada como um conjunto de módulos coesos, sob um namespace claro (por exemplo `inspectah.debunk`), com os seguintes serviços principais:

1. **DebunkIssueService**  
   - Criação de issues (via eventos da S23, flags de usuário, revisões internas).  
   - Atualização de status, vinculação/desvinculação de claims/timelines.  
   - Orquestração de abertura de rounds iniciais.

2. **DebunkRoundService**  
   - Criação/fechamento de rounds.  
   - Definição do conjunto de tasks para cada round, com base em templates de checagem e no tipo de claim.

3. **DebunkTaskService**  
   - Criação, atribuição e atualização de tasks.  
   - Integração com comitês de agentes (orquestrados pela S23/Percy) e com o fluxo humano.  
   - Persistência de resultados estruturados.

4. **DebunkOutcomeService**  
   - Consolidação de rounds/tasks em um outcome final.  
   - Geração de recomendação de alteração de estado para a S25.  
   - Criação de EvidenceSnapshot correspondente.

5. **DebunkAuditService**  
   - Registro de todos os eventos relevantes da S24.  
   - APIs para consulta de logs por issue/claim/timeline.

### 3.3.2 Contratos com S23 e S25 (sem acoplamento circular)

1. **Entrada S23 → S24**  
   - S23 expõe uma API ou publica eventos como: `claim_flagged_for_debunk`.  
   - Cada evento contém:
     - `claim_id`,  
     - motivo da flag (alto impacto, conflito de evidências, baixa confiança, etc.),  
     - links para evidências usadas,  
     - dados mínimos do caso/timeline.
   - A S24 **não lê diretamente** tabelas internas de classificação da S23: consome apenas contratos estáveis.

2. **Saída S24 → S25**  
   - S24 emite **DebunkOutcomes** via API interna ou eventos, por exemplo: `debunk_outcome_ready`.  
   - Cada outcome traz:
     - `outcome_id`, `issue_id`,  
     - `outcome_type`, `confidence_score`,  
     - `recommended_truth_state_change`,  
     - `linked_evidence_snapshot_id`.  
   - S25 decide se acata totalmente, parcialmente ou rejeita a recomendação, sempre registrando a decisão e o vínculo com o outcome.

### 3.3.3 Integração com Truth-DB

A S24 **não escreve diretamente** no Truth-DB principal (blocos de verdade):

- Ela apenas **lê** algumas informações (claims, timelines, estados atuais) para contextualizar a contestação.  
- E produz artefatos (DebunkIssues, DebunkOutcomes, EvidenceSnapshots) que serão consumidos pela S25 para promover/rebaixar estados de TruthRecords.

Isso garante:

- **Separação de responsabilidades**: contestar ≠ decidir a verdade final.  
- Possibilidade de múltiplos outcomes para o mesmo claim ao longo do tempo.  
- Camada de governança (S25) capaz de revisar decisões passadas sem reescrever o histórico da S24.

---

## 3.4 Filemap Macro da Sprint 24 (S24)

### 3.4.1 Backend – Estrutura proposta

No repositório `Inspectah/` (backend Python), a S24 introduz/atualiza os seguintes caminhos lógicos (nomes exatos podem ser refinados nos subcapítulos 3.3/3.4 da sprint):

- `inspectah/debunk/__init__.py`  
- `inspectah/debunk/models.py`  
  - Modelos SQLModel para: DebunkIssue, DebunkRound, DebunkTask, DebunkOutcome, EvidenceSnapshot, DebunkAuditTrail.
- `inspectah/debunk/schemas.py`  
  - Pydantic models para input/output das rotas de Debunker.  
- `inspectah/debunk/services/issue_service.py`  
- `inspectah/debunk/services/round_service.py`  
- `inspectah/debunk/services/task_service.py`  
- `inspectah/debunk/services/outcome_service.py`  
- `inspectah/debunk/services/audit_service.py`  
- `inspectah/routers/debunk.py`  
  - Rotas HTTP para o Debunker v0, montadas em `inspectah.api`.
- `inspectah/integration/s23_bridge.py` (ou similar)  
  - Adapta outputs/eventos da S23 em chamadas/inputs da S24.  
- `inspectah/integration/s25_bridge.py` (ou similar)  
  - Converte DebunkOutcomes em mensagens compreensíveis pela S25.
- `alembic/versions/s24_*.py`  
  - Migrações de banco específicas da S24.

**Testes backend** (exemplos de organização):

- `tests/debunk/test_debunk_models.py`  
- `tests/debunk/test_debunk_services.py`  
- `tests/debunk/test_debunk_api.py`  
- `tests/debunk/test_debunk_integration_s23.py`  
- `tests/debunk/test_debunk_integration_s25.py`

### 3.4.2 Frontend – Estrutura proposta

No repositório `frontend/inspectah-ui/`:

- `src/modules/debunk/`  
  - `pages/DebunkDashboardPage.tsx`  
  - `pages/DebunkIssueDetailPage.tsx`  
  - `components/DebunkIssueList.tsx`  
  - `components/DebunkIssueHeader.tsx`  
  - `components/DebunkRoundsTimeline.tsx`  
  - `components/DebunkTasksPanel.tsx`  
  - `components/EvidenceSnapshotViewer.tsx`  
  - `components/DebunkAuditTrailLog.tsx`  
  - `hooks/useDebunkIssues.ts`  
  - `hooks/useDebunkIssueDetail.ts`  
  - `hooks/useDebunkActions.ts`  
  - `api/debunkClient.ts`

Integrações com outros módulos:

- `src/modules/timeline/pages/TimelineXRayPage.tsx`  
  - Exibe badges de contestação e links para DebunkIssueDetailPage.  
- `src/modules/consult/pages/ConsultationPage.tsx`  
  - Exibe indicativos de contestação na resposta.

**Testes frontend** (exemplos):

- `src/__tests__/debunk/DebunkDashboardPage.test.tsx`  
- `src/__tests__/debunk/DebunkIssueDetailPage.test.tsx`  
- `src/__tests__/debunk/DebunkIntegrationWithTimeline.test.tsx`  
- `src/__tests__/debunk/DebunkIntegrationWithConsultation.test.tsx`

### 3.4.3 Scripts & CI relacionados à S24

No repositório raiz `Inspectah/`:

- `bin/s24_g0_env_repo.sh`  
  - Garante ambiente consistente para a sprint (deps backend/frontend, variáveis, etc.).
- `bin/s24_g1_schema_truth_db.sh`  
  - Valida migrações relacionadas a Debunk-DB/Truth-DB (sem quebrar sprints anteriores).
- `bin/s24_g2_apis_debunk.sh`  
  - Roda testes de API do Debunker, incluindo contratos com S23/S25 mockados.
- `bin/s24_g3_front_debunk_quality.sh`  
  - Lint + tests + build mínimo do módulo de Debunker no frontend.
- `bin/s24_g4_e2e_debunk_flow.sh`  
  - Cenários ponta-a-ponta: claim controverso da S23 → DebunkIssue → DebunkRound/Tasks → DebunkOutcome → notificação para S25.

Workflows GitHub Actions correspondentes:

- `.github/workflows/_s24_debunk.yml`  
  - Orquestra os gates S24_G0…S24_G4, gera scorecards em `out/scorecards/S24_G*_*.json` e evidências em `out/evidence/S24_G*/`.

---

## 3.5 Decisões travadas e fora de escopo da S24

### 3.5.1 Decisões travadas

1. **S24 não escreve no blockchain, nem em ancoragens externas** — Toda imutabilidade forte continua sendo responsabilidade da camada de Truth-DB & sistema de blocos (Fase 2 / futuro). A S24 foca em modelar contestação de forma limpa e auditável dentro do banco relacional.

2. **S24 não decide verdade final** — Ela recomenda mudanças de estado, mas a decisão canônica fica na S25.

3. **Arquitetura baseada em serviços coesos e testáveis** — Nada de lógica crítica misturada em handlers de rota. Toda regra de negócio relevante vive em serviços de domínio, testados em isolamento.

4. **Contratos com S23/S25 são estáveis e documentados** — S24 assume inputs/outputs claros; qualquer mudança em S23/S25 tem que respeitar esses contratos (ou passar por uma versão nova de contrato, nunca por quebra silenciosa).

5. **Telemetria obrigatória em todos os eventos-chave de contestação** — Nenhum DebunkOutcome é válido sem AuditTrail e EvidenceSnapshot associados.

### 3.5.2 Fora de escopo imediato (S24)

1. **Mecanismos avançados de reputação de revisores/analistas** — Podem ser considerados em sprints futuras, mas não são pré-requisito para o Debunker v0.

2. **Gamificação ou UI avançada para comunidade externa** — S24 atende principalmente analistas internos e a camada de governança; comunidade vem depois.

3. **Automação sofisticada baseada em múltiplos LLMs de vendors diferentes** — S24 assume um pipeline de agentes já definido em S23 e foca na orquestração de tasks/rounds.

4. **Contestação multi-cadeia ou integração com outros registries de verdade** — Fica explícito como tema de Fase 2.

---

## 3.6 Como os subcapítulos 3.1–3.4 detalharão esta arquitetura

Para fechar o Capítulo 3 macro, mapeamos o papel de cada subcapítulo da S24 dentro do Sprint Playbook v2:

- **3.1 (Subcapítulo 1 — Contexto & problemas a resolver da arquitetura)**  
  - Vai descer um nível para explicar: quais dores concretas da contestação estamos resolvendo, quais cenários críticos devem ser suportados pela arquitetura (fake news de alto impacto, estatística suspeita em dado oficial, contradições crônicas entre fontes, etc.).

- **3.2 (Subcapítulo 2 — Gates & métricas da arquitetura)**  
  - Vai ligar a arquitetura aos gates S24_G*, definindo quais invariantes de arquitetura são checados, quais contratos de API são validados automaticamente, quais métricas de throughput/latência/erro a arquitetura tem que sustentar.

- **3.3 (Subcapítulo 3 — Filemap detalhado)**  
  - Vai transformar o filemap macro em lista concreta de arquivos, módulos, nomes de rotas, DTOs, schemas e testes, no estilo "clone & build" das sprints anteriores.

- **3.4 (Subcapítulo 4 — Execução & evidências de arquitetura)**  
  - Vai traduzir esta visão em plano de execução: passos concretos de implementação, ordem de criação de arquivos, comandos de validação, exemplos de cenários e como capturar evidências no `out/evidence/S24_G*/`.

Com isso, o Capítulo 3 macro da S24 entrega a visão completa da **Arquitetura & Filemap da Camada de Contestação**, pronta para ser detalhada e executada nos subcapítulos, mantendo o nível máximo de excelência exigido pelo Sprint Playbook v2.

