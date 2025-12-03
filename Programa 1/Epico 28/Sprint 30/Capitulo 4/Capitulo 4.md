# Inspectah — Sprint 30 — Capítulo 4
## Execução, Cenários de Teste e Evidências da Sprint 30

Este capítulo transforma o escopo, a arquitetura e os gates da Sprint 30 em **plano de execução concreto**, com:
- fases de trabalho;
- tarefas por eixo (backend, frontend, scripts, observabilidade, integração);
- cenários de teste detalhados;
- checklist de evidências por gate e por métrica;
- ritual de ORR (Operational Readiness Review) em cima do bundle da sprint.

A ideia é simples: se alguém cair de paraquedas na S30 com este capítulo na mão, deve conseguir:
1. saber **em que ordem** atacar o trabalho;
2. saber **como provar** que o que foi implementado realmente funciona;
3. saber **quais arquivos e artefatos** precisam existir antes de chamar a sprint de DONE.

---

## 4.1 Fases de Execução da Sprint 30

A Sprint 30 é dividida em 5 fases práticas. Elas não precisam ser estritamente sequenciais, mas formam um backbone para organizar o trabalho.

### Fase 0 — Setup de sprint e G0

Objetivo: garantir que a sprint começa em terreno sólido.

Passos principais:
- Consolidar Capítulos 1–4 em `docs/sprint_30_*`.
- Alinhar o time de S30 com o Épico E28 (ler/relêr o doc do épico, revisar escopo da sprint).
- Implementar `bin/s30_g0_scope_and_alignment.sh`:
  - varredura de TODO/FIXME/TBD nos docs;
  - checagem de existência de arquivos de sprint;
  - checagem de referência ao doc de E28.
- Rodar G0 localmente e, em seguida, no CI (workflow `s30-gates`).

Saída esperada:
- Scorecard `out/scorecards/S30_G0_scope_and_alignment.json` com `status = PASS`;
- Pasta `out/evidence/S30_G0_scope_and_alignment/` com logs/textos de checagem.

### Fase 1 — Domínio de Fluxos v1.5 (backend + migrations)

Objetivo: estabilizar o modelo de Fluxos v1.5 e os templates.

Passos principais:
- Implementar entidades v1.5 em `app/flows/models.py`;
- Ajustar/introduzir `FlowTemplate`, `FlowOperationLog`, campos de estado/percentual de teste;
- Criar migration principal `0030_s30_flow_model_v15.py` e, se necessário, migration de seed de templates;
- Codificar `app/flows/service.py` com operações:
  - `create_flow_from_template`;
  - `set_flow_state` com regra de transição;
  - `replace_agent_for_step`;
  - `route_event_to_flow`;
  - `reprocess_items` (limitado);
- Implementar `app/flows/routing_policy.py` com política de roteamento para `noticia_texto`;
- Implementar `app/flows/execution_engine.py` com ciclo de execução básico e hooks para instrumentação.

Ligação com gates:
- Implementar e iterar `bin/s30_g1_flow_model_and_templates.sh` para validar:
  - migrations em banco vazio e banco com dados;
  - templates (`FlowTemplate`) obrigatórios;
  - topologias válidas.

Saídas esperadas:
- Scorecard `S30_G1_flow_model_and_templates.json` = PASS;
- Pasta `out/evidence/S30_G1_flow_model_and_templates/` com logs de migrations, relatório de templates e topologias.

### Fase 2 — Console de Fluxos (APIs + frontend)

Objetivo: tornar o fluxo de notícias‑pivô operável pelo Console.

Passos principais (backend):
- Implementar `app/api/flow_console_routes.py` com rotas:
  - listagem de fluxos;
  - detalhe de fluxo;
  - criação a partir de template;
  - transição de estado;
  - troca de agente;
  - execuções recentes + detalhe de execução;
  - reprocessamento limitado.
- Garantir autorização adequada (apenas Operador/Admin pode operar).

Passos principais (frontend):
- Criar módulo `src/features/flows/` com componentes previstos no Capítulo 3:
  - `FlowsListPage.tsx`;
  - `FlowDetailPage.tsx`;
  - `FlowExecutionDetailDrawer.tsx`;
  - `FlowCreateFromTemplateDialog.tsx`;
  - `FlowStateBadge.tsx` (+ `FlowOperationsBar.tsx` se adotado);
- Implementar hooks em `features/flows/api.ts` para consumir as APIs;
- Criar testes em `__tests__/flows_console.spec.tsx`.

Ligação com gates:
- Implementar `bin/s30_g2_flow_console_ops.sh` para:
  - rodar lint/build/test de frontend;
  - testar endpoints de API do console (curl/httpie) e validar respostas;
  - eventualmente rodar testes end‑to‑end básicos do console (opcional, se houver infra).

Saídas esperadas:
- Scorecard `S30_G2_flow_console_ops.json` = PASS;
- Pasta `out/evidence/S30_G2_flow_console_ops/` com logs de testes front, builds e curls.

### Fase 3 — Operações seguras, observabilidade e E2E

Objetivo: garantir que operar fluxos não é brincar com fósforo perto do galão de gasolina.

Passos principais:
- Endurecer `app/flows/service.py` com limites e regras de segurança para reprocessamento;
- Implementar `FlowOperationLog` e logging consistente em operações de fluxo;
- Desenvolver `app/flows/instrumentation.py` com métricas e logs estruturados;
- Integrar instrumentação à `FlowExecutionEngine`;
- Garfar/ajustar painéis de observabilidade para mostrar métricas do fluxo de notícias;
- Desenhar e codificar cenários E2E de fluxo de notícias em `bin/s30_g5_e2e_canonical_flow.sh`.

Ligação com gates:
- `bin/s30_g3_flow_operations_safety.sh` → operações críticas seguras;
- `bin/s30_g4_flow_observability.sh` → métricas e logs minimamente úteis;
- `bin/s30_g5_e2e_canonical_flow.sh` → cenário completo end‑to‑end do fluxo‑pivô de notícias.

Saídas esperadas:
- Scorecards `S30_G3_*`, `S30_G4_*`, `S30_G5_*` = PASS;
- Pastas respectivas em `out/evidence/` com logs de testes, dumps de métricas, capturas de console.

### Fase 4 — Métricas agregadas, bundle e ORR

Objetivo: consolidar tudo que a sprint fez em uma narrativa verificável.

Passos principais:
- Implementar `bin/s30_metrics_summary.sh` para colher inputs dos gates e gerar `S30_metrics_summary.json`;
- Implementar `bin/s30_bundle.sh` para empacotar scorecards + evidências + `S30_ORR_summary.txt` em `inspectah_s30_evidence_bundle.zip`;
- Rodar todo o workflow `.github/workflows/s30-gates.yml` em branch candidata ao merge;
- Realizar ORR em cima do bundle (ver seção 4.4).

Saídas esperadas:
- `S30_metrics_summary.json` com `status = PASS`;
- Bundle `inspectah_s30_evidence_bundle.zip` publicado como artifact de CI;
- Notas de ORR adicionadas em `docs/sprint_30_cap_4_execucao_evidencias.md` + `out/evidence/S30_ORR_summary.txt`.

---

## 4.2 Plano Detalhado de Execução (tarefas por eixo)

### 4.2.1 Eixo Backend — Fluxos & Orquestração

Tarefas principais:
1. Criar/ajustar models v1.5 em `app/flows/models.py`;
2. Escrever migrations `0030_s30_flow_model_v15.py` (+ seeds, se houver);
3. Implementar/ajustar `FlowTemplate` para notícias (`Fluxo_Noticias_Geral_v1`);
4. Implementar `FlowOperationLog` e uso consistente em operações administrativas;
5. Escrever `app/flows/routing_policy.py` com regras para `noticia_texto`;
6. Implementar/ajustar `FlowExecutionEngine` integrando com camada de agentes;
7. Ensinar `app/orchestration/dispatcher.py` a chamar `route_event_to_flow` para eventos de notícias;
8. Garantir testes de unidade/integrados para serviço de fluxo (idealmente em `tests/flows/test_service.py`).

### 4.2.2 Eixo Backend — APIs do Console

Tarefas principais:
1. Criar `app/api/flow_console_routes.py` com rotas descritas no Capítulo 3;
2. Escrever schemas em `app/flows/schemas.py` para suportar todas as rotas;
3. Amarrar rotas a `service.py` (nada de lógica de domínio nas rotas);
4. Garantir cobertura de testes em `tests/api/test_flow_console_routes.py` (ou similar).

### 4.2.3 Eixo Frontend — Console de Fluxos

Tarefas principais:
1. Criar estrutura de pasta `src/features/flows/`;
2. Implementar `FlowsListPage.tsx` com filtros, tabela e navegação;
3. Implementar `FlowDetailPage.tsx` com diagrama de etapas e operações;
4. Implementar `FlowExecutionDetailDrawer.tsx` com timeline de execução;
5. Implementar `FlowCreateFromTemplateDialog.tsx`;
6. Implementar `FlowStateBadge.tsx` (+ `FlowOperationsBar.tsx`, se adotado);
7. Criar `features/flows/api.ts` com hooks de dados;
8. Escrever testes em `__tests__/flows_console.spec.tsx` garantindo fluxo básico.

### 4.2.4 Eixo Observabilidade & E2E

Tarefas principais:
1. Implementar `app/flows/instrumentation.py` com helpers de métricas/logs;
2. Plugá‑los em `FlowExecutionEngine` e nos pontos de rota/serviço necessários;
3. Configurar (ou ajustar) painel de telemetria para fluxo de notícias;
4. Codificar script `bin/s30_g4_flow_observability.sh` (coleta/validação de métricas/logs);
5. Desenhar dataset de notícias sintéticas para cenário E2E;
6. Implementar `bin/s30_g5_e2e_canonical_flow.sh` para rodar cenário end‑to‑end;
7. Capturar evidências visuais (prints, export de métricas) para pasta `out/evidence/S30_G5_*`.

### 4.2.5 Eixo Gates, Métricas e Bundle

Tarefas principais:
1. Implementar todos os scripts `bin/s30_g*.sh` conforme Capítulo 2;
2. Criar workflow `.github/workflows/s30-gates.yml` com jobs `setup`, `gates-core`, `gates-e2e`, `metrics-and-bundle`;
3. Implementar `bin/s30_metrics_summary.sh` (consolidação de métricas de sprint);
4. Implementar `bin/s30_bundle.sh` (empacotamento de evidências e scorecards);
5. Rodar workflow completo e iterar até todos os gates/métricas estarem em PASS.

---

## 4.3 Cenários de Teste Detalhados por Gate

### G1 — Modelo de Fluxo & Templates

Cenários de teste mínimos:
- Criar banco de teste vazio → aplicar migrations até S30 → verificar sucesso;
- Criar banco com dump de estado pós‑S29 → aplicar migrations de S30 → verificar sucesso;
- Validar templates:
  - `Fluxo_Noticias_Geral_v1` existe, está ativo, possui estrutura coerente (etapas obrigatórias com papéis corretos);
  - rodar validador de topologias (sem loops proibidos, sem etapas órfãs, com decisão final).

Evidências esperadas:
- Logs de migrations em `out/evidence/S30_G1_*`;
- Arquivo JSON/YAML de relatório de templates/topologias válidas.

### G2 — Console de Fluxos

Cenários de teste mínimos:
- Backend:
  - `GET /api/flows` retorna lista com filtros aplicados corretamente;
  - `GET /api/flows/{id}` retorna dados completos do fluxo;
  - `POST /api/flows/from_template` cria fluxo novo e popula `Flow` + `FlowStep`s;
  - `POST /api/flows/{id}/state` respeita regras de transição e retorna erro para transições proibidas;
  - `GET /api/flows/{id}/executions` lista execuções recentes.

- Frontend:
  - `FlowsListPage` exibe fluxos e responde a filtro por `tipo_entrada`;
  - `FlowDetailPage` exibe steps em ordem, estado e ações corretas;
  - `FlowCreateFromTemplateDialog` dispara chamada correta e navega para o novo fluxo;
  - `FlowExecutionDetailDrawer` mostra timeline coerente com dados simulados.

Evidências esperadas:
- Logs de testes e coverage em `out/evidence/S30_G2_*`;
- Capturas (ou snapshots) de UI armazenadas na mesma pasta.

### G3 — Operações Seguras

Cenários de teste mínimos:
- Tentar reprocessamento sem limites (ex.: grande range de tempo) → operação negada com erro claro;
- Reprocessamento com limites aceitáveis → operação aceita, logs em `FlowOperationLog`, execuções registradas;
- Pausar fluxo ativo → verificar (com inserções de notícias sintéticas) que novos eventos deixam de entrar nesse fluxo;
- Retomar fluxo pausado → verificar que novos eventos voltam a utilizar o fluxo;
- Verificar logs de operação com campos completos (`flow_id`, `user_id`, `operacao`, `resultado`).

Evidências esperadas:
- Logs de API de reprocessamento, pausa, retomada em `out/evidence/S30_G3_*`;
- Dump de `FlowOperationLog` para cenários de teste.

### G4 — Observabilidade de Fluxos

Cenários de teste mínimos:
- Rodar uma bateria de execuções de notícias via scripts de teste;
- Coletar métricas e verificar:
  - `inspectah_flow_executions_total` > 0 para fluxo‑pivô;
  - `inspectah_flow_executions_success_total` > 0;
  - `inspectah_flow_executions_failure_total` reflete pelo menos um caso de erro simulado;
  - `inspectah_flow_latency_seconds` contendo amostras;
- Verificar logs estruturados:
  - filtrando por `flow_id` + `exec_fluxo_id` é possível reconstruir jornadas completas;
  - campos obrigatórios sempre presentes.

Evidências esperadas:
- Export de métricas (arquivo texto ou JSON) em `out/evidence/S30_G4_*`;
- Exemplos de logs estruturados com jornadas completas de execução.

### G5 — Cenário E2E do Fluxo de Notícias

Cenário principal:
- Configurar fontes de notícias mínimas (feed(s) de teste);
- Garantir que `Fluxo_Noticias_Geral_v1` está ativo para `noticia_texto`;
- Injetar lote de notícias sintéticas (ex.: 20–50 itens) via ingestão;
- Verificar que:
  - ingestão cria eventos `IngestionEvent` com `tipo_entrada = noticia_texto`;
  - dispatcher chama `route_event_to_flow` corretamente;
  - mesmas notícias geram `FlowExecution`s com status `concluido`;
  - `FlowStepExecution`s registram execução de cada etapa (interprete, classificador, analistas, debunkers, decision maker);
  - execuções aparecem no Console de Fluxos (lista e detalhe);
  - métricas e logs refletem as execuções.

Variantes:
- Introduzir algumas notícias com payload problemático para testar caminhos de erro;
- Introduzir pausa e retomada do fluxo durante a bateria de testes, verificando comportamento consistente.

Evidências esperadas:
- Scripts/dados de teste em `out/evidence/S30_G5_*`;
- Prints do Console mostrando execuções;
- Consultas de métricas/logs relacionados ao cenário.

---

## 4.4 Ritual de ORR da Sprint 30

O ORR (Operational Readiness Review) da S30 é um ritual rápido, mas disciplinado, feito em cima do estado final do repositório e do bundle de evidências.

Passos recomendados:

1. **Conferir CI**  
   - Garantir que o workflow `.github/workflows/s30-gates.yml` rodou com sucesso na branch candidata ao merge.

2. **Verificar scorecards**  
   - Baixar `out/scorecards/` (ou extrair do bundle) e checar:
     - todos `S30_G*_*.json` com `status = PASS`;
     - `S30_metrics_summary.json` com `status = PASS`;
     - métricas‑chave atendendo aos thresholds do Capítulo 2.

3. **Navegar evidências E2E**  
   - Entrar em `out/evidence/S30_G5_e2e_canonical_flow/` e verificar:
     - inputs de teste;
     - prints/capturas do Console;
     - evidências de que a jornada ingestão → fluxo → decisão está saudável.

4. **Ler resumo de ORR**  
   - Abrir `out/evidence/S30_ORR_summary.txt` e verificar se:
     - descreve brevemente o que foi feito na sprint;
     - aponta riscos residuais e dívidas claras, se houver;
     - conecta resultado com o contrato de E28.

5. **Check de percepção do squad**  
   - Coletar (ou revisar) notas do squad para a pergunta "o Console de Fluxos é, hoje, cockpit de operação para notícias?" e garantir notas ≥ 9.9/10;
   - Se alguma nota < 9.9 ocorre, discutir gaps e documentar como dívida de épico.

6. **Decisão de GO/NO-GO**  
   - Com base em scorecards, métricas, evidências e percepção do squad, o conselho do Programa 1 decide por GO ou NO-GO para a S30.

Resultado esperado de um ORR bem-sucedido:
- PR da S30 elegível para merge;
- Estado do E28 atualizável para refletir que o fluxo‑pivô de notícias é operável.

---

## 4.5 Checklist de Evidências da Sprint 30

Para não depender de memória humana, este checklist resume tudo que precisa existir ao finalizar a sprint.

### Documentos
- [ ] `docs/sprint_30_cap_1_contexto_problemas_objetivos.md` completo, sem TODO/FIXME.
- [ ] `docs/sprint_30_cap_2_gates_metricas_dod.md` completo, sem TODO/FIXME.
- [ ] `docs/sprint_30_cap_3_arquitetura_filemap.md` completo, sem TODO/FIXME.
- [ ] `docs/sprint_30_cap_4_execucao_evidencias.md` (este capítulo) atualizado com resultados e notas de ORR.

### Scripts e workflows
- [ ] Todos os scripts `bin/s30_g*.sh` implementados, executáveis e versionados.
- [ ] `bin/s30_metrics_summary.sh` implementado e funcional.
- [ ] `bin/s30_bundle.sh` implementado e funcional.
- [ ] `.github/workflows/s30-gates.yml` criado e rodando.

### Scorecards
- [ ] `out/scorecards/S30_G0_scope_and_alignment.json` com `status = PASS`.
- [ ] `out/scorecards/S30_G1_flow_model_and_templates.json` com `status = PASS`.
- [ ] `out/scorecards/S30_G2_flow_console_ops.json` com `status = PASS`.
- [ ] `out/scorecards/S30_G3_flow_operations_safety.json` com `status = PASS`.
- [ ] `out/scorecards/S30_G4_flow_observability.json` com `status = PASS`.
- [ ] `out/scorecards/S30_G5_e2e_canonical_flow.json` com `status = PASS`.
- [ ] `out/scorecards/S30_metrics_summary.json` com `status = PASS`.

### Evidências
- [ ] Pastas `out/evidence/S30_G0_*` ... `S30_G5_*` presentes com conteúdo coerente.
- [ ] `out/evidence/S30_ORR_summary.txt` presente e preenchido.
- [ ] `out/bundles/inspectah_s30_evidence_bundle.zip` gerado e anexado a pelo menos uma execução de CI.

### Estado de repositório e PR
- [ ] Nenhum TODO/FIXME em código e docs da S30.
- [ ] Nenhuma alteração não comitada relacionada à sprint.
- [ ] PR da S30 com descrição clara (objetivos, escopo, link para docs e bundle).

---

## 4.6 Fechamento da Sprint 30 no contexto de E28

Se todos os itens anteriores forem verdade, a Sprint 30 pode ser considerada **entregue**. Isso significa, no contexto do Épico E28:

- existe um fluxo‑pivô de notícias configurável e operável via Console;
- estados de fluxo (`draft`, `em_teste`, `ativo`, `pausado`) são respeitados pelo sistema de roteamento;
- execuções de fluxo geram trilhas de logs e métricas suficientes para operar 24/7;
- o cockpit de fluxos (para notícias) é real, não slide.

As próximas sprints do E28 (S31–S35) podem, a partir daqui, tratar o que S30 produziu como **infraestrutura de operação de fluxo**: é em cima dela que entram generalizações para outros tipos de fluxo, integração mais profunda com Debunker, Truth‑DB e casos, e expansão de observabilidade e ferramentas de replay.

Este Capítulo 4, portanto, é o contrato de execução da S30: se ele estiver cumprido, o épico avança; se não, ele é o mapa de onde a sprint precisa voltar para fechar as brechas.

