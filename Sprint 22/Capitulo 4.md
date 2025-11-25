# Inspectah — Sprint 22 — Capítulo 4 (v2)

## 1. Objetivo do Capítulo 4

Este capítulo é o manual de execução da Sprint 22. Ele transforma:

- a visão e o contexto (Capítulo 1),
- os gates e critérios de qualidade (Capítulo 2),
- e o filemap detalhado (Capítulo 3)

em uma linha do tempo operacional concreta: waves, tarefas, comandos, artefatos, branches, PRs, critérios de DONE e de GO/NO_GO.

A meta é simples e brutal: qualquer membro do Squad 2 deve conseguir, apenas com este capítulo em mãos, pegar um repo limpo do Inspectah e levar a S22 do zero até o ORR, sem improvisos, sem decisões obscuras e sem “magia de bastidor”.

---

## 2. Estrutura de execução da Sprint 22

A S22 será executada em waves curtas, com foco bem definido:

- Wave 0 — Grounding, setup e alinhamento (G0).  
- Wave 1 — Modelos, invariantes e migrations (G1 + parte de G4).  
- Wave 2 — FSM + serviços de domínio (G3 + parte de G2).  
- Wave 3 — API de ingestão + backend da UI de admin (restante de G2 + G5).  
- Wave 4 — Persistência detalhada, observabilidade e métricas (completar G4 + G6).  
- Wave 5 — Cenários end-to-end, evidências e ORR (G7 + G8).

Cada wave possui:

- objetivo claro;  
- tarefas de implementação;  
- comandos a rodar;  
- artefatos esperados (código, docs, scorecards, evidências);  
- critérios de DONE daquela wave.

No fim da sprint, todos os gates S22-G0…S22-G8 precisam estar em PASS para que o ORR decida GO.

---

## 3. Pré-condições gerais de execução

Antes de começar qualquer wave:

1) Ambiente local preparado

- Repositório do Inspectah clonado e atualizado:  
  - `git fetch origin`  
  - `git checkout main`  
  - `git pull origin main`  
- Virtualenv ativa e dependências instaladas:  
  - `cd /Users/<usuario>/Documents/Inspectah`  
  - `python3 -m venv .venv` (se ainda não existir)  
  - `source .venv/bin/activate`  
  - `python -m pip install --upgrade pip`  
  - `python -m pip install -r requirements.txt` (ajustar ao repo real).

2) Estado do git limpo ou com branch dedicado à S22

- Confirmar:  
  - `git status`  
- Se for iniciar a S22 a partir de main:  
  - `git checkout -b feature/s22-ingestion-2-0`

3) Sprint 21 consolidada

- Console de Fontes funcional;  
- modelos de Source estáveis;  
- sem TODOs críticos pendurados na S21.

4) Documentação base conhecida

- Leitura mínima de:  
  - `docs/sprint_22_capitulo_1_contexto.md`  
  - `docs/sprint_22_capitulo_2_gates.md`  
  - `docs/sprint_22_capitulo_3_filemap.md`

Se qualquer uma dessas pré-condições não estiver satisfeita, a sprint começa capenga.

---

## 4. Wave 0 — Grounding & DNA (S22-G0)

### 4.1. Objetivo

G0 garante que o Squad 2 está alinhado em três eixos:

- para que serve a S22;  
- o que ela explicitamente não vai fazer;  
- como ela se encaixa nas Sprints 21–25 e na Fase 2.

Sem G0 verde, o resto da execução vira gambiarra sofisticada.

### 4.2. Tarefas

1) Revisão conjunta de contexto

- Sessão de review (assíncrona ou síncrona) sobre:  
  - `docs/sprint_22_capitulo_1_contexto.md`  
  - `docs/sprint_22_capitulo_2_gates.md`  
  - `docs/sprint_22_capitulo_3_filemap.md`

2) Redação do resumo interno G0

- Editar/criar `docs/sprint_22_g0_summary.md` com:

  - 5–10 linhas sobre o objetivo da S22;  
  - lista explícita de fora de escopo (sem blockchain, sem reputação, sem Truth-DB, etc.);  
  - dependências de S21;  
  - frase clara sobre como S23, S24 e S25 vão usar a ingestão 2.0.

3) Check de entendimento do time

- Registrar, no final do `docs/sprint_22_g0_summary.md`, uma mini-tabela com:

  - membros do Squad 2;  
  - data em que confirmaram leitura/entendimento.

4) Execução do gate G0

```bash
cd /Users/<usuario>/Documents/Inspectah
source .venv/bin/activate
bash bin/s22_g0_grounding.sh
```

O script deve:

- validar presença dos docs chave;  
- gerar `out/scorecards/S22_G0_grounding.json`;  
- colocar evidências em `out/evidence/S22_G0_grounding/`.

### 4.3. DONE da Wave 0

- `S22_G0_grounding.json` com status `PASS`;  
- nenhum comentário aberto em `docs/sprint_22_g0_summary.md`;  
- time confortável em repetir em voz alta “o que é” e “o que não é” a S22.

---

## 5. Wave 1 — Modelos, invariantes e migrations (S22-G1 + base de S22-G4)

### 5.1. Objetivo

Modelar IngestionConfig e IngestionRun, formalizar invariantes e criar o schema de banco correspondente. Ao final da wave, o sistema sabe “o que é” uma ingestão em termos de dados, mesmo antes de ter lógica de execução.

### 5.2. Tarefas

1) Especificar modelos e invariantes (docs)

- Completar `docs/sprint_22_g1_modelos_e_invariantes.md` com:

  - descrição de `IngestionConfig` (campos, tipos, valores permitidos, relacionamento com Source);  
  - descrição de `IngestionRun`;  
  - lista numerada de invariantes (INV-1, INV-2, …), por exemplo:  
    - INV-1: `IngestionConfig.source_id` sempre referencia Source existente;  
    - INV-2: Source em estado DEPRECATED não pode ter modo AUTOMATIC;  
    - INV-3: IngestionRun encerrado só pode estar em {SUCCESS, PARTIAL_SUCCESS, FAIL};  
    - etc.

2) Implementar modelos em `app/ingestion/models.py`

- Adicionar classes/entidades para:  
  - `IngestionConfig`;  
  - `IngestionRun`;  
  - enums/constantes para modos e estados;  
- Garantir FKs e constraints mínimas em nível de ORM.

3) Criar migration de schema

- Implementar `db/migrations/022_sprint22_ingestion.sql` com os `CREATE TABLE`/`ALTER TABLE` necessários.  
- Rodar migration local em ambiente de desenvolvimento:

```bash
python -m scripts.db.migrate db/migrations/022_sprint22_ingestion.sql
```

(ajustar comando conforme padrão real do repo; Capítulo 4 assume que já existe tooling de migrations).

4) Implementar testes de modelos e invariantes

- Preencher `tests/ingestion/test_models_and_invariants.py` com casos de:

  - criação válida de IngestionConfig/IngestionRun;  
  - tentativas explícitas de violar invariantes (ex.: modo AUTOMATIC em fonte deprecada) e checar falhas;  
  - validação de estados permitidos de IngestionRun.

5) Atualizar sumário de invariantes

- No final de `docs/sprint_22_g1_modelos_e_invariantes.md`, registrar:

  - `invariants_defined_count = N`;  
  - `invariants_tested_count = M` (idealmente N);  
  - notas sobre eventuais invariantes ainda não testados.

6) Rodar gate G1

```bash
bash bin/s22_g1_models_and_invariants.sh
```

O script deve executar o arquivo de testes e gerar `S22_G1_models_and_invariants.json`.

### 5.3. DONE da Wave 1

- `db/migrations/022_sprint22_ingestion.sql` aplicada com sucesso localmente;  
- `tests/ingestion/test_models_and_invariants.py` passando;  
- `S22_G1_models_and_invariants.json` com status PASS;  
- invariantes principais descritos e cobertos por testes.

---

## 6. Wave 2 — FSM + serviços de domínio (S22-G3 + primeira camada de S22-G2)

### 6.1. Objetivo

Dar vida à ingestão 2.0 como máquina de estados e serviços de domínio, ainda sem API HTTP. A partir daqui, já é possível iniciar, completar e falhar ingestões via chamadas de função.

### 6.2. Tarefas

1) Especificar FSM em `docs/sprint_22_g3_maquina_de_estados.md`

- Descrever:

  - estados: PENDING, RUNNING, SUCCESS, PARTIAL_SUCCESS, FAIL (e quaisquer extras necessários);  
  - eventos: START, COMPLETE, FAIL, TIMEOUT, REPROCESS;  
  - tabela de transições (estado atual × evento → próximo estado);  
  - política de timeout (como um run em RUNNING vira FAIL por TIMEOUT).

2) Implementar FSM em `app/ingestion/state_machine.py`

- Criar função central, por exemplo:

  - `transition(run, event) -> new_state`  
- Garantir que qualquer transição ilegal gere exceção clara.

3) Implementar serviços de domínio em `app/ingestion/services.py`

- Implementar funções como:

  - `start_ingestion_run(source_id, trigger_origin)`  
  - `complete_ingestion_run(run_id, items_processed, metadata)`  
  - `fail_ingestion_run(run_id, error)`  
  - `toggle_ingestion_mode(source_id, new_mode)`  
  - `reprocess_run(run_id)`

- Cada função deve:

  - checar invariantes (G1);  
  - chamar `state_machine.transition`;  
  - persistir mudanças via `repository.py`;  
  - registrar logs/métricas básicos (integração inicial com observability.py).

4) Implementar erros específicos em `app/ingestion/errors.py`

- Criar exceções dedicadas (ex.: `FonteDesabilitadaError`, `ModoIncompativelError`, `RunEmAndamentoError`).  
- Usar essas exceções em `services.py` em vez de genéricos.

5) Implementar testes de FSM e serviços

- Em `tests/ingestion/test_state_machine.py`:

  - testar todas as transições válidas;  
  - testar tentativas de transição ilegal;  
  - testar comportamento de timeout simulado.

- Em `tests/ingestion/test_service_contracts.py` (parte domínio):

  - testar `start/complete/fail/reprocess` diretamente nos serviços;  
  - garantir lançamento de exceções específicas quando invariantes forem violados.

6) Rodar gate G3

```bash
bash bin/s22_g3_state_machine.sh
```

7) Rodar gate G2 (domínio, parte 1)

```bash
bash bin/s22_g2_service_contracts.sh
```

Nesta etapa, o script de G2 pode focar apenas em testes de serviços de domínio; os testes HTTP virão na Wave 3.

### 6.3. DONE da Wave 2

- FSM especificada, implementada e testada;  
- serviços de domínio de ingestão funcionais;  
- `S22_G3_state_machine.json` em PASS;  
- `S22_G2_service_contracts.json` já registrando PASS para os testes de domínio.

---

## 7. Wave 3 — API de ingestão + backend da UI de admin (completar S22-G2 + S22-G5)

### 7.1. Objetivo

Expor a ingestão 2.0 via HTTP e permitir que o admin consiga operar ingestões pela interface: ver estado, histórico e acionar ingestão manual.

### 7.2. Tarefas

1) Finalizar `docs/sprint_22_g2_contratos_de_servico.md`

- Descrever rotas e contratos de forma definitiva, incluindo:

  - URL, método, payload, resposta de sucesso, códigos de erro;  
  - exemplos de requests/responses.

2) Implementar API em `app/api/ingestion/routes.py`

- Implementar endpoints:

  - `POST /admin/ingestion/{source_id}/run`  
  - `POST /admin/ingestion/{source_id}/toggle-mode`  
  - `GET /admin/ingestion/{source_id}/runs`  
  - `GET /admin/ingestion/runs/{run_id}`

- Usar `schemas.py` para validação de entrada/saída.  
- Traduzir exceções de `errors.py` em respostas HTTP padronizadas.

3) Implementar backend da UI de admin em `app/admin/ingestion/`

- Em `views.py`:

  - adicionar view de lista de fontes com colunas de ingestão;  
  - adicionar view de detalhe de fonte exibindo histórico de runs;  
  - implementar ação de acionar ingestão manual.

- Em `adapters.py`:

  - mapear modelos de domínio para estruturas amigáveis à UI (labels de estados, etc.).

4) Validar fluxos da UI conforme `docs/sprint_22_g5_admin_ui.md`

- Garantir que, em no máximo 3 cliques, é possível:

  - descobrir se ingestão está ligada/desligada;  
  - saber o modo;  
  - ver última execução e estado.

- Atualizar o doc com prints (ou links) e observações de UX.

5) Implementar testes de API e UI backend

- Completar `tests/ingestion/test_service_contracts.py` com testes HTTP;  
- Completar `tests/ingestion/test_admin_ui_flows.py` com cenários de navegação backend.

6) Rodar gate G2 completo

```bash
bash bin/s22_g2_service_contracts.sh
```

7) Rodar gate G5

```bash
bash bin/s22_g5_admin_ui.sh
```

### 7.3. DONE da Wave 3

- Endpoints HTTP implementados, cobertos por testes, respeitando contratos;  
- UI de admin navegável, fluxos básicos funcionando;  
- `S22_G2_service_contracts.json` e `S22_G5_admin_ui.json` com status PASS.

---

## 8. Wave 4 — Persistência detalhada, observabilidade e métricas (fechar S22-G4 + S22-G6)

### 8.1. Objetivo

Completar a história de dados brutos e observabilidade: onde os dados ingeridos vivem, como são encontrados, e como medir saúde da ingestão.

### 8.2. Tarefas

1) Fechar decisão de persistência de dados brutos

- Em `docs/sprint_22_g4_persistencia_e_dados_brutos.md`, registrar decisão final:

  - DB (tabela `ingestion_raw_data`) vs arquivos (`data/ingestion_raw/...`);  
  - trade-offs;  
  - impacto na futura Truth-DB.

2) Implementar persistência em `app/ingestion/repository.py`

- Funções para:

  - salvar payload bruto associado a um run;  
  - recuperar dados brutos a partir de run_id;  
  - consultas por fonte e intervalo de tempo.

3) Ajustar migration se necessário

- Atualizar `db/migrations/022_sprint22_ingestion.sql` se decidida tabela extra;  
- reprovisionar banco em ambiente de teste.

4) Implementar testes de persistência

- Preencher `tests/ingestion/test_persistence.py` com casos de:

  - criar run + salvar payload;  
  - encontrar runs por fonte/período;  
  - navegar run → dados brutos.

5) Implementar métricas em `metrics/ingestion_s22.py`

- Definir counters/gauges/histograms:  
  - `ingestion_runs_total{source_id, status}`  
  - `ingestion_latency_ms_bucket{source_id}`  
  - `ingestion_last_success_timestamp{source_id}`  
  - etc.

- Integrar chamadas de métricas em `app/ingestion/observability.py` e `services.py`.

6) Configurar painel em `dashboards/ingestion_s22_overview.json`

- Incluir gráficos/tabelas para:

  - runs por fonte;  
  - taxa de sucesso/falha;  
  - fontes sem runs recentes;  
  - latência de ingestão.

7) Implementar testes de observabilidade

- Preencher `tests/ingestion/test_observability.py` com cenários:

  - execução de runs gera métricas esperadas;  
  - falhas aparecem na contagem de erros;  
  - fontes sem runs recentes podem ser detectadas programaticamente.

8) Rodar G4

```bash
bash bin/s22_g4_persistence.sh
```

9) Rodar G6

```bash
bash bin/s22_g6_observability.sh
```

### 8.3. DONE da Wave 4

- Modelo de persistência estável e documentado;  
- testes de persistência e observabilidade passando;  
- `S22_G4_persistence.json` e `S22_G6_observability.json` com status PASS.

---

## 9. Wave 5 — Cenários E2E, evidências e ORR (S22-G7 + S22-G8)

### 9.1. Objetivo

Provar que a ingestão 2.0 funciona na prática, em fontes reais/realistas, e consolidar a sprint para ORR com evidências, scorecards e wrap humano.

### 9.2. Tarefas

1) Detalhar cenários em `docs/sprint_22_g7_cenarios_e_runbook.md`

- Definir ao menos 3 cenários:

  - C1 — Fonte `news_rss` (ex.: um feed público de notícias).  
  - C2 — Fonte `data_api` (ex.: endpoint da API de dados abertos do IBGE).  
  - C3 — Fonte de outro tipo relevante (ex.: feed de preços demo).

- Para cada cenário, documentar:

  - fonte;  
  - como cadastrar/configurar;  
  - como acionar ingestão (manual/automática);  
  - o que esperar ver na UI;  
  - como inspecionar dados brutos e métricas.

2) Preparar fixtures em `data/s22_scenarios/`

- Preencher YAMLs com configurações de fontes para os cenários.

3) Implementar testes E2E em `tests/ingestion/test_e2e_scenarios_s22.py`

- Automatizar tanto quanto possível;  
- Para partes que dependam de fatores externos, registrar no teste instruções para execução manual + coleta de evidências.

4) Rodar G7

```bash
bash bin/s22_g7_e2e_scenarios.sh
```

- Geração de `out/scorecards/S22_G7_e2e_scenarios.json`;  
- evidências em `out/evidence/S22_G7_e2e_scenarios/`.

5) Consolidar ORR da S22 (G8)

- Preencher `docs/sprint_22_orr_summary.md` com:

  - objetivo da S22;  
  - descrição concisa da solução de ingestão 2.0;  
  - estado de cada gate;  
  - riscos residuais;  
  - próximos passos (entrada em S23, S24, S25).

- Rodar script de ORR:

```bash
bash bin/s22_g8_orr.sh
```

- Isso deve gerar `out/scorecards/S22_G8_orr.json`;  
- e `out/evidence/S22_orr/MANIFEST.json` referenciando todas as evidências da sprint.

### 9.3. DONE da Wave 5

- `S22_G7_e2e_scenarios.json` e `S22_G8_orr.json` em PASS;  
- `docs/sprint_22_orr_summary.md` completo;  
- `MANIFEST.json` em `out/evidence/S22_orr/` apontando para todos os diretórios de evidências.

---

## 10. Integração com CI e fluxo de PR

### 10.1. Workflow de CI dedicado à S22

Criar `.github/workflows/s22-gates.yml` com um job que:

- roda `bin/s22_all_gates.sh` em um ambiente limpo;  
- publica `out/scorecards/` como artefatos de CI;  
- opcionalmente, publica subset de `out/evidence/`.

### 10.2. Gatilhos de CI

Configurar o workflow para executar quando PRs modificarem arquivos em:

- `app/ingestion/**`  
- `app/api/ingestion/**`  
- `app/admin/ingestion/**`  
- `docs/sprint_22_*`  
- `db/migrations/022_sprint22_ingestion.sql`  
- `tests/ingestion/**`  
- `metrics/ingestion_s22.py`  
- `dashboards/ingestion_s22_overview.json`

### 10.3. Estratégia de branches e PRs

Sugestão:

- Branch principal da sprint: `feature/s22-ingestion-2-0`;  
- Branches menores por wave ou gate:  
  - `feature/s22-g1-models-invariants`  
  - `feature/s22-g3-fsm-services`  
  - etc.

Cada PR deve:

- citar explicitamente quais gates toca;  
- anexar (ou referenciar) scorecards relevantes;  
- mencionar evidências principais (prints, runbooks, etc.).

---

## 11. Check de encerramento da Sprint 22

Ao final da sprint, antes de declarar vitória, executar a sequência:

```bash
cd /Users/<usuario>/Documents/Inspectah
source .venv/bin/activate
bash bin/s22_all_gates.sh
```

Checar:

- todos os scorecards S22_G0…S22_G7 com status PASS;  
- `S22_G8_orr.json` com decisão `GO`;  
- `docs/sprint_22_orr_summary.md` consistente com o estado real do código e das evidências.

Se qualquer gate estiver em FAIL, o Capítulo 2 indica onde está o problema; este Capítulo 4 indica como voltar e corrigir.

---

## 12. Definição de sucesso do Capítulo 4 (v2)

O Capítulo 4 (v2) é considerado perfeito o bastante para a S22 se:

- o Squad 2 conseguir executar a sprint do zero ao ORR apenas seguindo este documento;  
- cada gate tiver uma trilha completa: doc → código → teste → script → scorecard → evidências;  
- não houver decisões “mágicas” não documentadas sobre onde colocar código, como rodar validações ou como coletar evidências.

Na prática: se um engenheiro novo no Inspectah conseguir, em alguns dias, chegar sozinho a `S22_G8_orr.json` com decisão GO, então este Capítulo 4 cumpriu sua missão e a Sprint 22 não é apenas uma feature — é um padrão de execução para as próximas sprints do projeto.

