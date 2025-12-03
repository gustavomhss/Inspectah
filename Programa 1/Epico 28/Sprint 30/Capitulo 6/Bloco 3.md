# Inspectah — Sprint 30 — Capítulo 6 — Bloco 3
## Tasks de Observabilidade, E2E, Gates, Bundle e CI (Eixo O/G)

Este bloco detalha as tasks do **Eixo O/G** da Sprint 30, responsáveis por transformar o fluxo‑pivô de notícias em algo **observável, testável de ponta a ponta e governado por gates automatizados**.

Aqui nasce o pacote que garante que a S30 não é “funcionou na minha máquina”, mas sim uma sprint com evidências reexecutáveis.

---

## 6.5 Tasks de Observabilidade (Métricas e Logs) — Eixo O/G

Estas tasks garantem que execuções de fluxo deixam um rastro claro de métricas e logs, alinhado às decisões do Cap. 5.2.4.

### O1 — Implementar módulo de instrumentação de fluxos

**Descrição**  
Criar `app/flows/instrumentation.py` com helpers para métricas e logs estruturados de fluxos.

**Inclui**
- funções como:
  - `record_flow_execution_started(flow, item, contexto)`;
  - `record_flow_execution_finished(execution, status, metrics)`;
  - `record_flow_step_execution_started(step, execution, contexto)`;
  - `record_flow_step_execution_finished(step_execution, status, metrics)`;
  - `record_flow_error(execution_or_step, error_class, details)`;
- emissão das métricas canônicas:
  - `inspectah_flow_executions_total{flow_id, tipo_entrada, status}`;
  - `inspectah_flow_executions_failure_total{flow_id, tipo_entrada, error_class}`;
  - `inspectah_flow_latency_seconds{flow_id, tipo_entrada}` (histograma ou equivalente);
- construção de logs estruturados com campos mínimos:
  - `flow_id`, `exec_fluxo_id`, `exec_etapa_id`, `item_id`, `tipo_entrada`, `status`, timestamps.

**Arquivos principais**
- `app/flows/instrumentation.py`

**Dependências**
- F1–F6 (modelos e engine definidos).

**Relação com gates**
- G4 — observabilidade de fluxos;
- G5 — cenário E2E usa essas métricas/logs como evidência.

---

### O2 — Integrar instrumentação à engine de execução

**Descrição**  
Conectar o módulo de instrumentação (`instrumentation.py`) à `FlowExecutionEngine`.

**Inclui**
- chamar `record_flow_execution_started` ao iniciar uma execução;
- chamar `record_flow_execution_finished` ao terminar (sucesso/falha/quase);
- chamar `record_flow_step_execution_started/finished` em cada etapa;
- em blocos de `try/except` de agentes, chamar `record_flow_error` quando ocorrerem erros;
- garantir que falhas na instrumentação não derrubam o fluxo (fail‑open controlado).

**Arquivos principais**
- `app/flows/execution_engine.py`
- `app/flows/instrumentation.py`

**Dependências**
- O1 implementada.

**Relação com gates**
- G4 — comprovação de que execuções emitem métricas e logs;
- G5 — execuções E2E já instrumentadas.

---

### O3 — Garantir naming e rótulos estáveis de métricas

**Descrição**  
Documentar e validar os nomes e labels das métricas de fluxo para que E28 inteiro possa depender delas.

**Inclui**
- doc curta (pode ser secção em Cap. 3 ou arquivo `docs/telemetria_fluxos_s30.md`) listando métricas e labels obrigatórios;
- se houver integração com Prometheus/Grafana ou stack similar, garantir que a configuração está alinhada;
- testes automatizados (ou script de verificação) que chequem pelo menos a presença das métricas básicas em uma execução de fluxo.

**Arquivos principais**
- `app/flows/instrumentation.py`;
- `docs/telemetria_fluxos_s30.md` (ou similar);
- teste em `tests/flows/test_instrumentation_metrics.py`.

**Dependências**
- O1, O2.

**Relação com gates**
- G4 — validação formal da telemetria;
- G5 — uso das métricas em evidências E2E.

---

## 6.6 Tasks de Cenário E2E — Fluxo de Notícias (Eixo O/G)

Estas tasks garantem que a S30 tenha um **cenário E2E reproduzível**, cobrindo ingestão → fluxo → console → métricas/logs.

### O4 — Preparar dataset sintético de notícias para E2E

**Descrição**  
Criar dataset representativo de notícias sintéticas para alimentar o cenário E2E da S30.

**Inclui**
- exemplos de notícias “normais” (sem problemas);
- exemplos com inconsistências ou ruídos propositalmente introduzidos;
- metadados mínimos (fonte, timestamp, tema) compatíveis com ingestão;
- formato esperável pelo pipeline de ingestão (por ex.: JSONL, CSV ou chamadas HTTP fake).

**Arquivos principais**
- `data/s30_e2e_noticias_sinteticas.jsonl` (ou similar);
- doc curta explicando o dataset em `docs/s30_e2e_dataset.md`.

**Dependências**
- conhecimento do formato de entrada da ingestão;
- F1–F3 (para saber como fluxos enxergam tipo_entrada).

**Relação com gates**
- G5 — insumo principal do teste E2E.

---

### O5 — Escrever script E2E de fluxo de notícias (`bin/s30_g5_e2e_canonical_flow.sh`)

**Descrição**  
Criar script que executa o cenário E2E canônico da S30.

**Inclui**
- subir stack mínima (banco, API, eventualmente fila/worker);
- garantir que existe um fluxo ativo para `noticia_texto` baseado no template da S30;
- injetar dataset sintético de notícias via caminho de ingestão definido (CLI, script HTTP, etc.);
- aguardar processamento (polling ou espera fixa baseada em configuração);
- verificar que execuções de fluxo foram criadas (mínimo N execuções);
- coletar evidências:
  - logs relevantes;
  - dumps de tabelas de execução de fluxo (ou queries selecionadas);
  - snapshots de métricas;
- armazenar tudo em `out/evidence/S30_G5_e2e_canonical_flow/`.

**Arquivos principais**
- `bin/s30_g5_e2e_canonical_flow.sh`
- `out/evidence/S30_G5_e2e_canonical_flow/*` (gerado).

**Dependências**
- F1–F6 (fluxos operacionais);
- O1–O4 (instrumentação + dataset);
- integração básica com ingestão disponível.

**Relação com gates**
- G5 — é o próprio gate E2E.

---

### O6 — Documentar cenário E2E e resultado esperado

**Descrição**  
Documentar o cenário E2E de forma legível para humanos e reaproveitável por sprints futuras.

**Inclui**
- descrição de entrada (dataset), trajetória esperada e resultado esperado;
- mapeamento entre passos do script e partes da arquitetura (ingestão, fluxos, console, telemetria);
- exemplo de execução com prints ou descrições de console/requests;
- link explícito para o diretório de evidências.

**Arquivos principais**
- `docs/sprint_30_e2e_fluxo_noticias.md`

**Dependências**
- O4, O5.

**Relação com gates**
- G5 — documentação do gate E2E;
- ORR — material de apoio para revisão operacional.

---

## 6.7 Tasks de Gates, Scorecards e Bundle — Eixo O/G

Estas tasks criam a camada de governança automatizada: scripts de gate, scorecards, resumo de métricas e bundle de evidências.

### O7 — Implementar scripts de gates G0–G4 (`bin/s30_g*.sh`)

**Descrição**  
Criar scripts shell que verificam aspectos críticos da S30 e geram scorecards JSON em `out/scorecards/`.

**Inclui** (mínimo):
- `bin/s30_g0_scope_and_alignment.sh`  
  - verifica presença e consistência de docs (Cap. 1–3);
  - garante ausência de TODO/FIXME críticos nos docs;
  - gera `out/scorecards/S30_G0_scope_and_alignment.json`.

- `bin/s30_g1_flow_model_and_templates.sh`  
  - verifica existência de `app/flows/models.py` com campos esperados;
  - checa aplicação bem‑sucedida de `0030_s30_flow_model_v15.py` em ambiente de teste;
  - valida template canônico de notícias (via função interna);
  - gera `S30_G1_flow_model_and_templates.json`.

- `bin/s30_g2_flow_console_ops.sh`  
  - roda testes de API e frontend do Console de Fluxos;
  - pode utilizar suite dedicada de testes (`pytest -k flows_console` + `npm test flows`);
  - gera `S30_G2_flow_console_ops.json`.

- `bin/s30_g3_flow_operations_safety.sh`  
  - testa cenários de mudança de estado inválida (esperando erro controlado);
  - testa reprocessamento acima dos limites (esperando recusa segura);
  - garante registro em `FlowOperationLog`;
  - gera `S30_G3_flow_operations_safety.json`.

- `bin/s30_g4_flow_observability.sh`  
  - executa uma ou mais execuções de fluxo;
  - verifica a existência de métricas e logs obrigatórios;
  - gera `S30_G4_flow_observability.json`.

**Arquivos principais**
- `bin/s30_g0_scope_and_alignment.sh`
- `bin/s30_g1_flow_model_and_templates.sh`
- `bin/s30_g2_flow_console_ops.sh`
- `bin/s30_g3_flow_operations_safety.sh`
- `bin/s30_g4_flow_observability.sh`
- `out/scorecards/S30_G*.json` (gerados)

**Dependências**
- F1–F6, C1–C5, O1–O3;
- docs de sprint (Cap. 1–3) já em estado avançado.

**Relação com gates**
- G0–G4 — estes scripts **são** os gates.

---

### O8 — Implementar script de métricas agregadas (`bin/s30_metrics_summary.sh`)

**Descrição**  
Criar script que lê scorecards dos gates e gera `S30_metrics_summary.json`, consolidando o estado da sprint.

**Inclui**
- leitura de `out/scorecards/S30_G*.json` (pelo menos G0–G5);
- agregação de status:
  - se qualquer gate crítico estiver `FAIL`, `status` global deve ser `FAIL`;
- cálculo ou extração de métricas relevantes (ex.: número de testes, tempo de execução dos gates, etc.);
- gravação de `out/scorecards/S30_metrics_summary.json`.

**Arquivos principais**
- `bin/s30_metrics_summary.sh`
- `out/scorecards/S30_metrics_summary.json`

**Dependências**
- O7 (gates G0–G4) e O5 (G5) implementados.

**Relação com gates**
- usado no ORR para decisão GO/NO‑GO;
- parte do checklist binário do Cap. 4.

---

### O9 — Implementar script de bundle de evidências (`bin/s30_bundle.sh`)

**Descrição**  
Criar script que monta `out/bundles/inspectah_s30_evidence_bundle.zip` com scorecards, evidências de gates e resumo de ORR.

**Inclui**
- inclusão de:
  - `out/scorecards/S30_G0_*.json` … `S30_G5_*.json`;
  - `out/scorecards/S30_metrics_summary.json`;
  - todas as pastas `out/evidence/S30_G*/` (G0–G5);
  - `out/evidence/S30_ORR_summary.txt` (mesmo que inicialmente stub, depois preenchido no ORR);
- verificação de que todos os caminhos existem antes de zipar;
- criação idempotente do zip (sobrescrevendo arquivo anterior, se houver).

**Arquivos principais**
- `bin/s30_bundle.sh`
- `out/bundles/inspectah_s30_evidence_bundle.zip`

**Dependências**
- O7 (gates), O8 (metrics summary), O5/O6 (evidências de G5);
- T20/T21 para preenchimento final de `S30_ORR_summary.txt`.

**Relação com gates**
- ORR — o bundle é insumo principal;
- auditorias futuras da sprint.

---

## 6.8 Task de CI — Workflow da Sprint 30 (Eixo O/G)

### O10 — Criar/ajustar workflow de CI da S30 (`.github/workflows/s30-gates.yml`)

**Descrição**  
Configurar workflow de CI responsável por executar os gates da S30, gerar métricas summary e bundle, e expor o estado da sprint via GitHub Actions.

**Inclui**
- jobs típicos:
  - `setup` — checkout, cache, ambiente Python/Node, migrations em banco temporário;
  - `gates` — execução de `bin/s30_g0_*.sh` até `bin/s30_g5_e2e_canonical_flow.sh`;
  - `metrics_summary` — execução de `bin/s30_metrics_summary.sh`;
  - `bundle` — execução de `bin/s30_bundle.sh`;
- upload de `out/bundles/inspectah_s30_evidence_bundle.zip` como artifact;
- configuração de falha da pipeline caso qualquer script de gate ou metrics summary retorne erro;
- tags ou nomes de workflow claros (ex.: `[S30] Gates & ORR Evidence`).

**Arquivos principais**
- `.github/workflows/s30-gates.yml`

**Dependências**
- O7–O9 implementados e rodando localmente;
- infraestrutura de CI do repositório já configurada.

**Relação com gates**
- garante que gates são aplicados de forma reprodutível e automatizada;
- é ponto de entrada do ORR (a partir da execução mais recente do workflow).

---

## 6.9 Amarração do Eixo O/G com a Decisão de GO

Com as tasks O1–O10 concluídas, a Sprint 30 ganha:
- telemetria mínima obrigatória de fluxos (métricas + logs) em produção;
- cenário E2E reprodutível de fluxo de notícias, com evidências guardadas;
- gates e scorecards que sintetizam o estado da sprint de forma binária;
- bundle único de evidências que permite reauditar a sprint no futuro;
- CI que roda tudo isso de forma consistente a cada alteração relevante.

No Capítulo 6, o Eixo O/G é o que transforma a S30 de “mais uma feature grande” em **unidade auditável de evolução do sistema de fluxos do Inspectah**.

O Bloco 4 completa o capítulo com as tasks de governança, ORR, backlog e checklist final de GO (Eixo Gv).

