# Sprint 24 – Capítulo 2.2  
## Gates, Métricas e Definition of Done (DoD) – Versão v2 (State of the Art)

> Escopo: este subcapítulo define, de forma **rigorosa e operacional**, todos os critérios de **GO/NO_GO** da Sprint 24 (Debunker v0 + Humano-no-loop), mapeando **gates**, **checks objetivos**, **métricas mínimas** e **Definition of Done** em nível de sprint. Nada aqui é opinativo: cada item precisa ter **comando**, **artefato** e **ponto de verificação concreto**.

---

## 1. Visão geral dos gates da Sprint 24

A Sprint 24 terá a seguinte malha de gates principais:

- **S24_G0 – Scope & Baseline**  
  Confirmação de escopo, alinhamento com S23 e S25, e consolidação documental segundo o Sprint Playbook v2.

- **S24_G1 – Modelo de Domínio & Truth-DB Debunker**  
  Schema, migrations, entidades e invariantes do domínio do Debunker v0.

- **S24_G2 – Engine & APIs do Debunker v0**  
  Contratos de API, fluxo de criação/atualização de DebunkIssues e integração mínima com S23.

- **S24_G3 – UI & Fluxo Humano-no-loop**  
  Telas, usabilidade mínima, bloqueios contra “carimbo cego” e experiência do analista.

- **S24_G4 – Políticas de Decisão & Impacto em Estados de Verdade**  
  Como decisões do Debunker alteram (ou não) states de verdade e timelines.

- **S24_G5 – Observabilidade, Scorecards e Risco Operacional**  
  Logs, métricas, scorecards internos do Debunker v0 e alertas mínimos.

- **S24_G6 – Demo Integrada & GO/NO_GO Final da Sprint**  
  Execução de cenários ponta a ponta e decisão formal de GO da Sprint 24.

Cada gate:

- é executado por um **script único** em `bin/`;  
- grava um **scorecard JSON** em `out/scorecards/`;  
- produz **evidências** em `out/evidence/`;  
- é projetado para rodar tanto **localmente** quanto na **CI oficial**.

A seguir, detalhamos **por gate**: objetivos, comandos esperados, métricas mínimas e DoD específico.

---

## 2. Convenções obrigatórias (todos os gates S24_GX)

### 2.1 Estrutura de arquivos e scripts

Para **todo gate** da Sprint 24:

- Script executável em `bin/`:
  - Exemplo de naming:
    - `bin/s24_g0_scope_baseline.sh`
    - `bin/s24_g1_domain_db.sh`
    - `bin/s24_g2_debunker_engine.sh`
    - `bin/s24_g3_ui_debunker.sh`
    - `bin/s24_g4_truth_policy.sh`
    - `bin/s24_g5_observability.sh`
    - `bin/s24_g6_demo_and_orr.sh`
  - Requisitos do script:
    - `set -euo pipefail` no início;
    - logar início e fim do gate;  
    - terminar com **exit 0** somente em caso de GO;
    - qualquer falha relevante deve resultar em exit **≠ 0**.

- Scorecard JSON em `out/scorecards/`:
  - Nome canônico: `out/scorecards/S24_GX_<nome_gate>.json`, por exemplo:
    - `S24_G1_domain_db.json`;
    - `S24_G3_ui_debunker.json`;
  - Campos mínimos obrigatórios:
    ```json
    {
      "gate_id": "S24_G1",
      "name": "Domain & Truth-DB for Debunker v0",
      "status": "GO" | "NO_GO",
      "checks": [
        {
          "id": "DB-SCHEMA-01",
          "name": "Migrations aplicadas em banco limpo",
          "passed": true,
          "details": "pytest -m migrations_s24 ...",
          "evidence_path": "out/evidence/S24_G1_domain_db/migrations.log"
        }
      ],
      "metrics": {
        "tests_passed": 42,
        "tests_failed": 0,
        "scenario_count": 5
      },
      "timestamp": "2025-..",
      "git_sha": "<commit>",
      "review_board_scores": {
        "pearl": 9.8,
        "stonebraker": 9.9,
        "norvig": 9.7,
        "liang": 9.9
      }
    }
    ```

- Pasta de evidências em `out/evidence/`:
  - Ex.: `out/evidence/S24_G2_debunker_engine/`
  - Deve conter **logs, dumps, snapshots, respostas de API** ou qualquer material que permita auditar a execução do gate.

### 2.2 Critérios gerais de GO (aplicáveis a todos os gates)

Um gate **só pode** ser declarado GO se as seguintes condições forem verdadeiras:

1. **Scorecard existe e tem status="GO"**.
2. Todos os **checks obrigatórios** do gate estão com `passed = true`.
3. Existem evidências em `out/evidence/S24_GX_*` apontadas pelos checks.
4. Os comandos registrados no scorecard **rodaram sem erro** durante o gate.
5. Para gates com revisão humana (S24_G0, S24_G5, S24_G6), a média das notas da review board ≥ **9.5/10** e nenhum revisor marcou objeção crítica.

Qualquer desvio em **(1–4)** implica **NO_GO automático**, independentemente de “sensações” da equipe.

---

## 3. Gate S24_G0 – Scope & Baseline

### 3.1 Objetivo

Garantir que a Sprint 24 começa com:

- escopo e recortes **claros e documentados**;
- dependências com S23 e S25 explicitadas;
- alinhamento com o **Sprint Playbook v2 (6×4 docs)**;
- aprovação formal do Squad Verdade & Interpretação + conselho.

### 3.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g0_scope_baseline.sh
```

### 3.3 Checks obrigatórios (mínimo)

1. **DOC-STRUCT-01 – Estrutura 6×4 presente**  
   - Verifica se todos os **capítulos macro (1–6)** existem e, para cada um, os **4 subcapítulos** estão presentes em `docs/sprint_24/` (ou path equivalente descrito no Capítulo 1):
     - `cap_1_1_contexto.md`, `cap_1_2_gates.md`, `cap_1_3_arquitetura_filemap.md`, `cap_1_4_execucao.md`;
     - ... até `cap_6_4_execucao.md`.
   - DoD: script lista os arquivos esperados, verifica sua existência e falha se algum estiver faltando.

2. **DOC-CONTENT-02 – Ausência de TODOs bloqueantes**  
   - Grep automático para trechos como `TODO`, `WIP`, `TBD` nos docs da sprint;  
   - O gate falha se encontrar TODOs **sem tag explícita de “pós-S24”**. Ex.: `TODO(S25)` pode ser aceito.

3. **SCOPE-LINK-03 – Alinhamento com S23 e S25**  
   - No documento macro da Sprint 24, deve existir seção:
     - “Dependências concretas de S23” (classes, tabelas, APIs, estados);
     - “Entregas que alimentam S25” (TruthChangeEvents, métricas, DebunkDecisions etc.).  
   - O script faz uma checagem simples (grep/regex) por headings e listas obrigatórias.

4. **REVIEW-BOARD-04 – Aprovação mínima do conselho**  
   - O gate lê um arquivo de review, por exemplo `out/reviews/S24_G0_scope_review.json`, contendo as notas de:
     - Pearl, Stonebraker, Norvig, Percy, PO, etc. (como personas virtuais).
   - Critério:
     - média geral ≥ 9.5;
     - nenhuma nota < 9.0;
     - nenhum revisor marcou `blocker = true`.

### 3.4 Métricas esperadas

- `doc_files_present`: quantidade de arquivos esperados vs. encontrados.
- `todo_blockers`: número de TODOs não marcados como pós-S24 (deve ser 0).
- `dependencies_declared`: número de itens em Dependências de S23 e Entregas para S25.
- `review_board_avg`: média das notas do conselho.

### 3.5 DoD S24_G0

- Toda a estrutura documental da Sprint 24 existe e está coerente com o **Sprint Playbook v2**;
- Escopo, dependências e entregas inter-sprint estão claramente descritos;
- Conselho e Squad Verdade & Interpretação assinaram o baseline;
- Qualquer ambiguidade relevante foi transformada em **risco explicitado** ou **débito técnico registrado**.

---

## 4. Gate S24_G1 – Modelo de Domínio & Truth-DB do Debunker

### 4.1 Objetivo

Garantir que o **núcleo de dados** do Debunker v0 está:

- modelado de forma consistente com o macro da S24;  
- preparado para crescer (S25+) sem bagunça;
- validado por invariantes mínimas automatizadas.

### 4.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g1_domain_db.sh
```

### 4.3 Entidades mínimas esperadas (conceituais)

- `DebunkIssue` – caso aberto para contestar um claim/timeline.
- `DebunkIssueEvent` – linha do tempo interna do issue (abertura, atribuição, comentários, anexos, etc.).
- `DebunkDecision` – decisão final (ou parcial) do Debunker, humana ou híbrida.
- `DebunkEvidenceLink` – vínculo entre issue/claim/timeline e evidências (documentos, notícias, dados).
- `ReviewerAssignment` – quem está responsável por revisar o caso (analista, comitê etc.).

O gate **não impõe** nomes físicos das tabelas, mas exige que haja **mapeamento explícito** entre essas entidades conceituais e o schema físico.

### 4.4 Checks obrigatórios

1. **DB-MIGRATION-01 – Migrations aplicáveis em banco limpo**  
   - Script cria um banco de teste (por exemplo, SQLite ou PostgreSQL em container) e aplica todas as migrations da Sprint 24.  
   - Falha se qualquer migration quebrar, estiver em ordem inconsistente ou depender de estado prévio não documentado.

2. **DB-SCHEMA-02 – Tabelas centrais presentes**  
   - Script obtém um dump de schema (via `sqlalchemy`, `
 .schema`, `SHOW TABLES`, etc.) e verifica presença de tabelas que implementem as entidades conceituais listadas.  
   - O scorecard relaciona entidades lógicas → tabelas físicas.

3. **DB-INVARIANTS-03 – Invariantes básicas testadas**  
   - Execução de um conjunto mínimo de testes (por exemplo `pytest -m debunker_domain`) que verificam invariantes como:  
     - não é possível criar `DebunkDecision` sem `DebunkIssue` associado;  
     - estados de issue pertencem a um conjunto finito (OPEN, IN_REVIEW, RESOLVED, ESCALATED...);  
     - transições inválidas de estado disparam erro.

4. **DB-QUERY-04 – Consultabilidade operacional básica**  
   - Testes que respondem três perguntas reais:
     - “Quais issues abertas existem para um claim X?”;
     - “Quais decisões já foram tomadas para um claim X nos últimos N dias?”;
     - “Quais issues estão atribuídas ao analista Y e em qual estado?”.
   - Os testes devem estar versionados e referenciados no scorecard.

### 4.5 Métricas esperadas

- `migrations_applied`: número de migrations aplicadas com sucesso.
- `domain_tests_passed` / `domain_tests_failed`.
- `sample_queries_ok`: quantidade de consultas de exemplo que passaram.
- `schema_warnings`: número de avisos de possíveis problemas de modelagem (deve ser 0 ou explicitamente justificado).

### 4.6 DoD S24_G1

- Migrations rodando em banco limpo, sem passos manuais obscuros;
- Entidades centrais do Debunker v0 representadas no DB de forma alinhada ao macro;
- Invariantes básicas protegidas por testes automatizados;
- Consultas principais usadas em S24 (e pré-S25) já funcionam e são relativamente eficientes.

---

## 5. Gate S24_G2 – Engine & APIs do Debunker v0

### 5.1 Objetivo

Garantir que o Debunker v0:

- expõe **APIs estáveis** para criação, atualização, decisão e consulta de issues;
- possui uma **engine de priorização** coerente com a política definida na sprint;  
- integra minimamente com a saída de S23.

### 5.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g2_debunker_engine.sh
```

### 5.3 Endpoints mínimos (conceituais)

- `POST /debunker/issues` – criar DebunkIssue;
- `PATCH /debunker/issues/{id}` – atualizar status, adicionar comentários, anexar evidências;
- `POST /debunker/issues/{id}/decision` – registrar decisão;
- `GET /debunker/issues` – listar issues filtrando por estado, origem, prioridade;
- `GET /debunker/issues/{id}` – detalhar um issue.

### 5.4 Checks obrigatórios

1. **API-CONTRACT-01 – Contratos de request/response tipados**  
   - Todas as rotas do Debunker v0 precisam usar modelos Pydantic (ou equivalentes) para request e response.  
   - O gate roda testes que validam:
     - ausência de `dict` ou `Any` soltos em interfaces públicas;  
     - documentação de campos obrigatórios/opcionais.

2. **API-TESTS-02 – Testes automatizados de cenário feliz e de erro**  
   - Pelo menos 1 teste “feliz” e 1 teste de erro por endpoint crítico:  
     - `201` na criação correta de issue;  
     - `400/422` quando payload inválido;  
     - `404` quando ID não existe;  
     - etc.

3. **ENGINE-PRIORITY-03 – Regras de priorização verificadas**  
   - Testes que criam múltiplos issues com atributos diferentes (urgência, impacto, fonte, tipo de claim) e verificam ordem de prioridade retornada.

4. **S23-INTEGRATION-04 – Integração mínima com camada de Interpretação (S23)**  
   - Pelo menos um teste automatizado que:
     - cria um claim/timeline de exemplo no formato produzido pela S23;  
     - aciona a criação de DebunkIssue com base nesses dados;  
     - verifica se as referências (IDs, tipos de claim, contexto) são preservadas.

### 5.5 Métricas esperadas

- `api_tests_passed` / `api_tests_failed`.
- `priority_scenarios_ok`: número de cenários de priorização que passaram.
- `s23_integration_cases`: número de casos de integração testados.
- `avg_response_time_ms`: latência média de respostas em ambiente de teste (opcional, mas recomendável).

### 5.6 DoD S24_G2

- Engine de Debunker v0 com contratos de API claros, testados e estáveis;
- Prioridade de issues coerente com regras da sprint, não “na intuição”;
- Capacidade de receber issues a partir da camada de interpretação (S23) sem mapeamentos improvisados.

---

## 6. Gate S24_G3 – UI & Fluxo Humano-no-loop

### 6.1 Objetivo

Garantir que a UI do Debunker v0:

- oferece um fluxo utilizável para analistas humanos;  
- impede “carimbo automático” de saídas de IA;  
- registra as ações humanas de forma clara e auditável.

### 6.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g3_ui_debunker.sh
```

### 6.3 Fluxos mínimos que precisam estar cobertos

1. Abrir painel de Debunker com lista de issues.
2. Entrar no detalhe de um issue (claim/timeline, evidências, histórico).
3. Registrar análise e rationale do analista.
4. Tomar decisão (confirmar, rejeitar, pedir mais evidência, escalonar).
5. Ver histórico de decisões e estados do issue.

### 6.4 Checks obrigatórios

1. **UI-FLOW-01 – Fluxos críticos com testes automatizados**  
   - Suíte de testes (Vitest + Testing Library, Cypress ou outra ferramenta) que:
     - abre tela de lista;
     - abre issue específico;
     - preenche rationale;
     - aplica decisão;
     - verifica estado final na UI.

2. **UI-GUARD-02 – Bloqueios contra decisão “sem leitura”**  
   - Pelo menos um teste garantindo que o botão de decisão:
     - começa desativado;
     - só é habilitado depois de o usuário realizar ações mínimas (ex.: rolar evidências até certo ponto, marcar um checkbox “Li as evidências principais”, preencher campo de rationale).

3. **UI-FEEDBACK-03 – Feedback pós-decisão**  
   - Testes que validam a presença de mensagens claras pós-decisão:
     - estado do issue;
     - link para timeline/claim impactado;
     - indicação de que a decisão ficará registrada no Truth-DB.

4. **UI-PERF-04 – Limite mínimo de performance**  
   - Em ambiente de teste com dados sintéticos moderados, o tempo para carregar a tela de detalhe de issue deve estar abaixo de um limite (por exemplo, < 2s).  
   - O gate registra a medição em um arquivo de evidência.

### 6.5 Métricas esperadas

- `ui_flow_tests_passed` / `ui_flow_tests_failed`.
- `guardrails_violations`: quantas tentativas de clicar em decisão sem atender pré-condições foram corretamente bloqueadas.
- `avg_issue_detail_load_ms`: tempo médio para carregar tela de detalhe.

### 6.6 DoD S24_G3

- Analista humano consegue usar a UI do Debunker para trabalhar casos reais;
- Não há caminho “feliz” que permita decisão sem rationale ou sem leitura mínima de evidências;
- O fluxo de ponta a ponta (da lista à decisão) é funcional e auditável.

---

## 7. Gate S24_G4 – Políticas de Decisão & Impacto em Estados de Verdade

### 7.1 Objetivo

Assegurar que as decisões do Debunker v0:

- são mapeadas para estados de verdade de forma **determinística e explicável**;  
- não causam efeitos colaterais imprevisíveis;  
- deixam rastro adequado para a camada de Governança de Verdade (S25).

### 7.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g4_truth_policy.sh
```

### 7.3 Mapeamento decisão → efeito (conceitual)

Exemplos (não exaustivos):

- `CONFIRM_CLAIM` → claim passa de `PROVISIONAL` para `ESTABLISHED_FACT`, com registro de TruthChangeEvent;
- `REJECT_CLAIM` → claim passa para `REJECTED` ou timeline anota evento de retratação;
- `FLAG_FOR_REVIEW` → claim permanece em `UNDER_REVIEW`, com escopo de análise ampliado;
- `NEED_MORE_EVIDENCE` → issue volta para estado `OPEN` com checklist de evidências faltantes.

### 7.4 Checks obrigatórios

1. **POLICY-TABLE-01 – Tabela de políticas versionada**  
   - Deve existir uma tabela (YAML/JSON/Python) com mapeamento explícito `DecisionType → efeito` em estados de verdade e timelines.  
   - O script de gate valida a presença dessa tabela e sua consistência (sem decisões “soltas”).

2. **E2E-SCENARIOS-02 – Cenários ponta a ponta testados**  
   - Pelo menos 3 cenários completos, modelando casos reais da Sprint 24:
     - exemplo de obra pública;
     - exemplo de dado oficial vs. fonte alternativa;
     - exemplo de notícia potencialmente falsa.  
   - Cada cenário:
     - começa em um state inicial de claim/timeline;
     - passa pelo Debunker v0 (com interação simulada de humano, se for o caso);
     - termina em um state final esperado;
     - registra TruthChangeEvents (ou equivalente) no DB.

3. **NO-CASCADE-03 – Proteção contra efeito dominó indevido**  
   - Teste que prova que uma decisão em um caso **não** altera estados de claims/timelines não relacionados, a menos que haja regra explícita de propagação.

4. **TRACEABILITY-04 – Rastreabilidade de decisão**  
   - Testes que verificam que, dado um TruthChangeEvent, é possível:
     - encontrar o DebunkIssue que originou a mudança;
     - recuperar quem decidiu, quando e com base em quais evidências.

### 7.5 Métricas esperadas

- `policy_entries_count`: quantidade de decisões mapeadas na tabela de políticas.
- `e2e_scenarios_passed` / `e2e_scenarios_failed`.
- `unintended_cascades`: número de cascatas não intencionais detectadas (deve ser 0).

### 7.6 DoD S24_G4

- Toda decisão do Debunker mapeia para efeitos definidos em estados de verdade/timelines;
- Cenários chave de uso do Debunker estão cobertos por testes ponta a ponta;
- Há rastreabilidade forte entre decisão, justificativa e mudança de estado.

---

## 8. Gate S24_G5 – Observabilidade, Scorecards e Risco Operacional

### 8.1 Objetivo

Garantir que o Debunker v0 é observável o suficiente para que:

- problemas não passem despercebidos;  
- métricas de qualidade e carga existam;  
- scorecards internos possam evoluir para políticas mais rígidas em S25.

### 8.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g5_observability.sh
```

### 8.3 Checks obrigatórios

1. **LOG-STRUCT-01 – Logs estruturados para ações críticas**  
   - Verifica que ações como `issue_created`, `issue_state_changed`, `decision_applied`, `integration_error` são logadas com campos mínimos padronizados (`issue_id`, `claim_id`, `actor_type`, `action`, `timestamp`).

2. **METRICS-02 – Métricas mínimas expostas**  
   - Métricas essenciais (via Prometheus, JSON, ou outro mecanismo):
     - número de issues abertas por tipo/estado;
     - tempo médio entre abertura e decisão;
     - taxa de override humano vs sugestão da IA.

3. **INTERNAL-SCORECARDS-03 – Scorecards internos gerados**  
   - A partir de um dataset sintético de Sprint 24, o Debunker gera scorecards internos contendo, por exemplo:
     - distribuição de tipos de decisão;
     - taxa de decisões revertidas;
     - volume de issues reabertas.

4. **ALERTS-04 – Alertas mínimos configurados**  
   - Pelo menos um alerta simples, como:
     - “fila de issues abertas acima de X”;
     - “tempo médio para decisão acima de Y minutos”.
   - O gate deve simular condição de alerta e registrar sua ativação.

### 8.4 Métricas esperadas

- `log_samples_checked`: quantidade de registros de log inspecionados.
- `metrics_ok`: número de métricas obrigatórias encontradas.
- `internal_scorecards_generated`: quantidade de scorecards internos gerados.
- `alerts_triggered_in_test`: quantos alertas foram disparados durante o teste.

### 8.5 DoD S24_G5

- Logs estruturados permitem entender o que está acontecendo no Debunker sem “adivinhação”;
- Métricas básicas de qualidade e carga existem e podem ser consultadas facilmente;
- Scorecards internos pavimentam a estrada para políticas mais rígidas em S25;
- Pelo menos um mecanismo simples de alerta está funcionando.

---

## 9. Gate S24_G6 – Demo Integrada & GO/NO_GO Final

### 9.1 Objetivo

Consolidar a Sprint 24, demonstrando, de ponta a ponta, que:

- o Debunker v0 funciona em cenários reais da sprint;  
- o humano-no-loop está operacional;  
- o impacto em estados de verdade é explícito e auditável.

### 9.2 Comando padrão do gate

```bash
export PYTHONPATH=.
bash bin/s24_g6_demo_and_orr.sh
```

### 9.3 Roteiro de demo versionado

- Documento em `docs/sprint_24/demo_s24.md` (exemplo) contendo:
  - passos para subir serviços (backend, frontend, DB);  
  - comandos para popular dados de exemplo da Sprint 24;  
  - sequência de ações na UI;
  - resultados esperados em cada etapa.

### 9.4 Checks obrigatórios

1. **DEMO-SCENARIOS-01 – Cenários oficiais executados**  
   - Execução automatizada (na medida do possível) dos cenários oficiais de demo:  
     - ex.: 3–5 casos de uso representativos da Sprint 24.

2. **EVIDENCE-LINK-02 – Evidência visível na UI & DB**  
   - Para pelo menos um caso de demo, o gate valida que:
     - a timeline no frontend reflete decisão do Debunker;  
     - o DB contém os registros de TruthChangeEvent correspondentes.

3. **REVIEW-BOARD-03 – Notas de demo e ORR**  
   - O scorecard S24_G6 deve registrar:
     - notas de todos os revisores de demo;
     - decisão final de GO/NO_GO da Sprint 24.
   - Critério: média ≥ 9.9 e nenhuma objeção crítica.

4. **LIMITATIONS-04 – Registro de limitações de v0**  
   - Documento/tabela com limitações e débitos da Sprint 24 (“o que este Debunker ainda não faz, por design”).  
   - O gate falha se essa lista não existir ou estiver vazia.

### 9.5 Métricas esperadas

- `demo_scenarios_executed` / `demo_scenarios_failed`.
- `review_board_avg_demo`: média das notas da demo.
- `limitations_count`: número de limitações documentadas (não é 0; transparência é mandatória).

### 9.6 DoD S24_G6 / DoD da Sprint 24

A Sprint 24 é considerada **GO global** somente se:

- Todos os gates S24_G0…S24_G6 estiverem com scorecard `status = "GO"`;
- Todos os artefatos obrigatórios (docs, scripts, testes, scorecards, evidências) estiverem versionados;
- Demo integrada mostrou, na prática, o Debunker v0 funcionando ponta a ponta;
- As limitações do v0 foram documentadas e são aceitáveis para seguir para S25;
- O conselho e o Squad Verdade & Interpretação assinam, explicitamente, que o sistema é seguro o bastante para ser a base das próximas camadas de governança de verdade.

---

**Este Capítulo 2.2 passa a ser o contrato formal de gates, métricas e DoD da Sprint 24.**  
Qualquer ajuste futuro deve ser feito via PR de documentação, com revisão explícita do Squad Verdade & Interpretação e do conselho, mantendo sempre o espírito: **decisões baseadas em artefatos objetivos, rastreáveis e alinhados ao modelo de verdade do Inspectah.**

