# Inspectah — Sprint 30 — Capítulo 4 — Bloco 3
## Cenários de Teste por Gate (G0–G5) e Evidências Específicas da Sprint 30

Este bloco desce ao nível cirúrgico dos **cenários de teste por gate** da Sprint 30. A pergunta aqui é simples e implacável:

> “Que testes exatamente precisamos rodar, o que consideramos sucesso e qual evidência precisa ser guardada para cada gate?”

A resposta é organizada gate a gate (G0–G5), sempre com:
- objetivo do gate;
- cenários mínimos (e alguns de borda) que **devem** existir;
- critérios claros de aprovação/falha;
- evidências esperadas em `out/evidence/` e `out/scorecards/`.

---

## 4.3.1 Gate G0 — Escopo, Alinhamento e Higiene de Sprint

**Objetivo:** garantir que a Sprint 30 começa com terreno firme: docs completos, alinhamento com o Épico E28 e ausência de lixo óbvio (TODO/FIXME) em artefatos de sprint.

### Cenários de teste G0

1. **Existência de documentos obrigatórios da S30**  
   - Verificar se os arquivos a seguir existem e são legíveis:
     - `docs/sprint_30_cap_1_contexto_problemas_objetivos.md`;
     - `docs/sprint_30_cap_2_gates_metricas_dod.md`;
     - `docs/sprint_30_cap_3_arquitetura_filemap.md`;
     - `docs/sprint_30_cap_4_execucao_evidencias.md`.

2. **Varredura de TODO/FIXME/TBD**  
   - Rodar varredura textual (via `grep` ou script Python) sobre docs da S30 e, opcionalmente, sobre módulos críticos (`app/flows/*`, `flow_console_routes.py`, `features/flows/*`);
   - O gate só passa se não houver ocorrência de `TODO`, `FIXME` ou `TBD` não justificados.

3. **Alinhamento com o Épico E28**  
   - Ler (via script) e verificar que pelo menos um dos docs da S30 referencia explicitamente o doc de E28 (por path ou identificador);
   - Opcional: validar que o campo `epic` nos scorecards de G0 e G1 é `E28`.

### Critérios de aprovação G0

- Todos os quatro documentos de sprint existem e têm tamanho mínimo (não são cascas vazias);
- Zero ocorrências de `TODO`/`FIXME`/`TBD` em docs da S30;
- Referência explícita ao Épico E28 em pelo menos um documento da sprint;
- Script `bin/s30_g0_scope_and_alignment.sh` retorna código de saída 0.

### Evidências G0

- `out/scorecards/S30_G0_scope_and_alignment.json` com:
  - `status = "PASS"`;
  - campos com lista de arquivos verificados e contagem de TODO/FIXME;
- `out/evidence/S30_G0_scope_and_alignment/log.txt` com saída do script;
- Opcional: dump JSON com resultado da varredura de TODO/FIXME.

---

## 4.3.2 Gate G1 — Modelo de Fluxos v1.5 e Templates

**Objetivo:** garantir que o modelo v1.5 de fluxos, migrations e templates está consistente, aplicável e compatível com o estado pós‑S29.

### Cenários de teste G1

1. **Migrations em banco vazio**  
   - Subir banco limpo (local ou em container de teste);
   - Aplicar todas as migrations até S30;
   - Verificar que tabelas de fluxos (`Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`) existem com colunas esperadas.

2. **Migrations em banco pós‑S29**  
   - Restaurar dump representativo de banco pós‑S29;
   - Aplicar migrations de S30;
   - Garantir ausência de erro e integridade das tabelas.

3. **Seed/estado de templates**  
   - Verificar que `FlowTemplate` inclui um template ativo para notícias, ex.: `Fluxo_Noticias_Geral_v1`;
   - Checar que o template possui estrutura coerente: etapas com papéis esperados (interprete, classificador, analistas, debunkers, decision maker) e ordem válida.

4. **Validador de topologias de fluxo**  
   - Rodar função/CLI interna que verifica:
     - ausência de loops proibidos;
     - todas as etapas são alcançáveis;
     - existe decisão final (não termina em estado pendente).

### Critérios de aprovação G1

- Migrations aplicam limpo em **dois cenários**: banco vazio + banco pós‑S29;
- `FlowTemplate` de notícias existe, está ativo e é considerado válido pelo validador de topologias;
- Script `bin/s30_g1_flow_model_and_templates.sh` retorna código 0.

### Evidências G1

- `out/scorecards/S30_G1_flow_model_and_templates.json` com `status = "PASS"`;
- `out/evidence/S30_G1_flow_model_and_templates/migrations_empty_db.log`;
- `out/evidence/S30_G1_flow_model_and_templates/migrations_post_s29.log`;
- `out/evidence/S30_G1_flow_model_and_templates/templates_report.json` com lista e validação de templates.

---

## 4.3.3 Gate G2 — Console de Fluxos (APIs + Frontend)

**Objetivo:** comprovar que o Console de Fluxos funciona como cockpit básico de operação para o fluxo de notícias‑pivô, tanto no backend quanto na UI.

### Cenários de teste G2 — Backend (APIs)

1. **Listagem de fluxos**  
   - `GET /api/flows` sem filtros → retorna lista não vazia com fluxos existentes;
   - `GET /api/flows?tipo_entrada=noticia_texto` → filtra corretamente;
   - `GET /api/flows?estado=ativo` → lista apenas fluxos ativos.

2. **Detalhe de fluxo**  
   - `GET /api/flows/{flow_id}` → retorna metadados completos + lista de `FlowStep`s em ordem;
   - verificar integridade: IDs, tipos de etapa, roles e bindings coerentes.

3. **Criação a partir de template**  
   - `POST /api/flows/from_template` com template de notícias → cria novo fluxo;
   - verificar que `Flow` e `FlowStep`s foram persistidos corretamente;
   - resposta inclui ID do novo fluxo.

4. **Mudança de estado**  
   - `POST /api/flows/{flow_id}/state` com transição `draft → em_teste` → sucesso;
   - `em_teste → ativo` → sucesso;
   - tentativa de `ativo → draft` → falha com erro de domínio;
   - operações registradas em `FlowOperationLog`.

5. **Execuções e reprocessamento (nível API)**  
   - `GET /api/flows/{flow_id}/executions` retorna execuções recentes;
   - `GET /api/flows/{flow_id}/executions/{execution_id}` dá timeline completa;
   - `POST /api/flows/{flow_id}/reprocess` com critério aceitável dispara reprocessamento;
   - reprocessamento que excede limites é recusado com mensagem clara.

### Cenários de teste G2 — Frontend (UI)

1. **Lista de fluxos**  
   - `FlowsListPage` renderiza tabela de fluxos com filtros funcionais;
   - clicar em linha leva a `FlowDetailPage` correta.

2. **Detalhe de fluxo**  
   - `FlowDetailPage` mostra estado via `FlowStateBadge`, etapas e ações possíveis;
   - ações exibidas/ocultadas conforme estado (ex.: não mostrar "Marcar como ativo" para fluxo já ativo).

3. **Criação de fluxo**  
   - `FlowCreateFromTemplateDialog` permite selecionar template e preencher parâmetros;
   - ao confirmar, chama API e redireciona para detalhe do fluxo criado;
   - erros de backend aparecem como mensagens visíveis.

4. **Execução e jornada**  
   - Tabela de execuções recentes é exibida com status/duração;
   - ao clicar em uma execução, abre `FlowExecutionDetailDrawer` com timeline;
   - links "Ver logs"/"Ver métricas" apontam para URLs coerentes (mesmo que ambiente de telemetria seja stub).

### Critérios de aprovação G2

- Todos os cenários descritos acima executam sem erro;
- Console de Fluxos é capaz de:
  - criar fluxo de notícias a partir de template;
  - mudar estado desse fluxo;
  - listar execuções de teste;
  - mostrar jornada de uma execução;
- Script `bin/s30_g2_flow_console_ops.sh` retorna código 0.

### Evidências G2

- `out/scorecards/S30_G2_flow_console_ops.json` com `status = "PASS"`;
- `out/evidence/S30_G2_flow_console_ops/api_calls.log` (ou similar) com chamadas de teste;
- `out/evidence/S30_G2_flow_console_ops/frontend_tests.log` com saída de testes de UI;
- opcional: snapshots/capturas de tela do Console em cenários chave.

---

## 4.3.4 Gate G3 — Operações Seguras de Fluxo

**Objetivo:** garantir que operações de alto impacto (especialmente reprocessamento e mudança de estado) são seguras, auditáveis e previsíveis.

### Cenários de teste G3

1. **Reprocessamento dentro de limites**  
   - Configurar fluxo de notícias com execuções anteriores armazenadas;
   - Chamar `reprocess_items` (via API/CLI) com critério moderado (ex.: N itens, janela pequena de tempo);
   - Verificar que novas execuções são criadas para os itens visados;
   - Verificar registro de `FlowOperationLog` com parâmetros do reprocessamento.

2. **Reprocessamento fora de limites**  
   - Tentar reprocessar grande volume (ex.: sem filtros ou com intervalo de meses);
   - Sistema deve recusar com erro de domínio (ex.: `reprocessamento_excessivo`);
   - Operação registrada em `FlowOperationLog` como `resultado = erro`.

3. **Pausar fluxo ativo**  
   - Dado fluxo em estado `ativo` com ingestão de notícias acontecendo;
   - Executar `set_flow_state` para `pausado`;
   - Injetar novas notícias de teste via ingestão;
   - Verificar que nenhum novo `FlowExecution` é criado para o fluxo pausado;
   - Verificar log de operação com `operacao = set_state` e `novo_estado = pausado`.

4. **Retomar fluxo pausado**  
   - De estado `pausado`, voltar a `ativo` via API/console;
   - Injetar novas notícias de teste;
   - Verificar que execuções voltam a ser criadas normalmente.

5. **Auditoria de operações**  
   - Consultar `FlowOperationLog` e confirmar:
     - existência de registros para todas as operações de teste (state/reprocess/replace_agent);
     - presença de `user_id` (ou identificador lógico de origem), `operacao`, `payload`, `resultado` e timestamp.

### Critérios de aprovação G3

- Reprocessamentos fora de limites **não** são executados e retornam erro claro;
- Reprocessamentos dentro de limites geram execuções corretas e logs de operação;
- Estados de fluxo impactam de fato o roteamento (pausar/retomar funciona na prática);
- `FlowOperationLog` cobre todas as operações críticas;
- Script `bin/s30_g3_flow_operations_safety.sh` retorna código 0.

### Evidências G3

- `out/scorecards/S30_G3_flow_operations_safety.json` com `status = "PASS"`;
- `out/evidence/S30_G3_flow_operations_safety/reprocess_ok.log`;
- `out/evidence/S30_G3_flow_operations_safety/reprocess_too_big.log`;
- `out/evidence/S30_G3_flow_operations_safety/flow_state_pause_resume.log`;
- dumps ou consultas de `FlowOperationLog` usados nos testes.

---

## 4.3.5 Gate G4 — Observabilidade de Fluxos

**Objetivo:** provar que o fluxo de notícias‑pivô não é uma caixa‑preta: execuções e problemas aparecem em métricas e logs estruturados.

### Cenários de teste G4

1. **Execuções de sucesso geram métricas**  
   - Rodar bateria de execuções de teste de notícias (via scripts ou ingestão);
   - Consultar o backend de métricas (ou endpoint de export) e verificar que:
     - `inspectah_flow_executions_total{flow_id=..., status="success"}` > 0;
     - `inspectah_flow_executions_success_total{flow_id=...}` > 0;
     - `inspectah_flow_latency_seconds{flow_id=...}` tem amostras.

2. **Execuções com erro geram métricas de falha**  
   - Injetar algumas notícias problemáticas para provocar erros de etapa;
   - Verificar métricas:
     - `inspectah_flow_executions_failure_total{flow_id=..., error_class=...}` > 0.

3. **Logs estruturados com IDs de correlação**  
   - Filtrar logs por `flow_id` do fluxo de notícias;
   - Selecionar uma execução específica (`exec_fluxo_id`);
   - Garantir que é possível reconstruir a jornada de etapas via logs contendo:
     - `exec_fluxo_id`, `exec_etapa_id`, `item_id`, `tipo_entrada`, `status`;
   - Pelo menos um cenário deve demonstrar passo a passo a jornada completa.

4. **Painel de observabilidade mínimo**  
   - Abrir painel de métricas (mesmo que em ambiente de test) e verificar:
     - gráfico de execuções ao longo do tempo;
     - indicador de taxa de erro;
     - algum indicador de latência.

### Critérios de aprovação G4

- Métricas de sucesso, falha e latência estão presentes para o fluxo‑pivô;
- Logs estruturados permitem reconstruir pelo menos uma jornada completa de execução;
- Script `bin/s30_g4_flow_observability.sh` retorna código 0.

### Evidências G4

- `out/scorecards/S30_G4_flow_observability.json` com `status = "PASS"`;
- `out/evidence/S30_G4_flow_observability/metrics_dump.txt` ou `.json` com snapshot de métricas;
- `out/evidence/S30_G4_flow_observability/logs_sample.json` com logs estruturados de uma jornada completa;
- opcional: export/screenshot de painel de métricas.

---

## 4.3.6 Gate G5 — Cenário E2E do Fluxo de Notícias

**Objetivo:** validar, ponta a ponta, que o fluxo‑pivô de notícias funciona “de verdade”: da ingestão à execução de agentes e visualização no Console.

### Cenário E2E principal G5

1. **Preparação de ambiente**  
   - Subir ambiente com backend, ingestão, banco migrado até S30 e Console;
   - Garantir que `Fluxo_Noticias_Geral_v1` (ou equivalente) está configurado e em estado `ativo`.

2. **Ingestão de notícias sintéticas**  
   - Preparar dataset de 20–50 notícias sintéticas cobrindo casos:
     - notícias triviais (happy path);
     - notícias com conteúdo que provoca ao menos um erro controlado em etapa;
   - Injetar essas notícias via mecanismo oficial de ingestão (feed, API ou script que simula fonte).

3. **Roteamento e execução de fluxo**  
   - Confirmar que cada notícia ingerida gera um `IngestionEvent` com `tipo_entrada = noticia_texto`;
   - Verificar que o dispatcher chama `route_event_to_flow` para esses eventos;
   - Verificar criação de `FlowExecution`s para o fluxo de notícias;
   - Verificar que cada execução percorre as etapas configuradas (interpreter → classifier → analistas → debunkers → decision maker), gerando `FlowStepExecution`s.

4. **Visualização no Console**  
   - Usar o Console de Fluxos para:
     - listar o fluxo de notícias;
     - ver execuções recentes na `FlowDetailPage`;
     - abrir `FlowExecutionDetailDrawer` para uma execução específica e conferir timeline.

5. **Telemetria E2E**  
   - Confirmar que as execuções realizadas durante o teste aparecem nas métricas de fluxos;
   - Confirmar presença de logs estruturados com IDs de correlação para pelo menos uma execução de teste.

### Variantes E2E recomendadas

- **Variante com pausa e retomada:**  
  - durante a bateria de ingestão, pausar o fluxo;
  - verificar interrupção de execuções novas;
  - retomar fluxo;
  - verificar retomada de execuções.

- **Variante com tráfego em teste:**  
  - configurar fluxo adicional em `em_teste` com `percentual_teste` > 0;
  - verificar que parte das notícias é roteada para o fluxo em teste, respeitando aproximadamente o percentual configurado.

### Critérios de aprovação G5

- Pelo menos 1 cenário E2E completo (ingestão → fluxo → console → métricas/logs) executado com sucesso;
- Pelo menos 1 variante com erro controlado e/ou pausa/retomada validada;
- Script `bin/s30_g5_e2e_canonical_flow.sh` retorna código 0.

### Evidências G5

- `out/scorecards/S30_G5_e2e_canonical_flow.json` com `status = "PASS"`;
- `out/evidence/S30_G5_e2e_canonical_flow/dataset_noticias.json` (ou equivalente);
- `out/evidence/S30_G5_e2e_canonical_flow/e2e_run.log` com passos e resultados do script;
- `out/evidence/S30_G5_e2e_canonical_flow/console_screenshots/` com capturas do Console (lista de fluxos, detalhe, execuções);
- `out/evidence/S30_G5_e2e_canonical_flow/metrics_and_logs_snapshot.*` com referências de métricas/logs.

---

Com esse Bloco 3, o Capítulo 4 passa a dizer, sem ambiguidade, **como cada gate deve ser testado e qual evidência precisa existir** para que a Sprint 30 seja considerada GO. O Bloco 4 fecha o capítulo amarrando o ritual de ORR e o checklist binário de evidências que diferencia “parece pronto” de “está pronto de verdade”.