# Sprint 21.2 — Capítulo 4 (Plano de Execução) — v2

Título interno: Copiloto de Fontes v2 — Execução em ondas, alinhada a S21 e S21.1

Este capítulo descreve, de forma operacional, como sair de um repositório onde S21 e S21.1 já estão estáveis e chegar ao estado final da Sprint 21.2 concluída, com todos os gates S21_2_G0…G8 em GO.

O plano é pensado para ser seguido tanto por desenvolvedores quanto pelo Codex, sempre com as seguintes regras:

- Nenhuma alteração da S21.2 pode quebrar S21 ou S21.1.
- Todo comportamento novo precisa ter correspondência em:
  - documentação (docs/),
  - código (app/, inspectah/, frontend/),
  - testes (tests/, frontend/__tests__/),
  - e pelo menos um gate S21_2_G* com scorecard e evidências.
- A experiência do admin com o Console + Copiloto precisa melhorar ou, no mínimo, permanecer estável em relação ao baseline S21 + S21.1.

Raiz local do projeto:

/Users/gustavoschneiter/Documents/Inspectah

Branch recomendada para a Sprint 21.2:

feature/s21_2_copiloto_fontes_v2

---

## 1. Pré-condições e sanidade inicial (Wave 0)

Objetivo: garantir que o ponto de partida é sólido antes de abrir a Sprint 21.2.

### 1.1 Estado mínimo do repositório

- main atualizado com o remoto.
- S21 em GO (todos os gates S21_G0…S21_G8 verdes, scorecards presentes).
- S21.1 em GO (todos os gates S21_1_G0…S21_1_G8 verdes, scorecards presentes).
- Sem modificações locais não intencionais (git status limpo, exceto artefatos em out/ e .pyc ignorados).

### 1.2 Ambiente de execução

- Virtualenv Python criado e ativado.
- PYTHONPATH=. exportado na sessão atual.
- Dependências Python instaladas (requirements do backend).
- Dependências do frontend instaladas (npm install já executado em frontend/inspectah-ui).

### 1.3 Sanidade S21 / S21.1

Antes de iniciar a 21.2, a equipe deve:

- Rodar pytest nos testes de fontes e agentes existentes para garantir que S21/S21.1 continuam íntegros.
- Rodar os scripts de gates S21 e S21.1 (all_gates) para validar que o estado GO é reproduzível na máquina local.

Resultado esperado da Wave 0:

- Ambiente pronto.
- main em estado conhecido.
- S21 e S21.1 confirmadas como GO.

---

## 2. Organização em ondas de trabalho

A execução da S21.2 é organizada em cinco waves principais, além da Wave 0:

- Wave 1 — Documentos v2 (ontologia, fluxos, FSM, segurança, scorecard).
- Wave 2 — Domínio de fontes v2 (refresh, tipo oficial aberta, status).
- Wave 3 — Copiloto v2 (agent, tools, FSM, safety).
- Wave 4 — Backend + Frontend (API, UI, UX).
- Wave 5 — Gates, evidências, scorecards, wrap e GO/NO_GO.

Cada wave tem:

- Objetivo claro.
- Arquivos-alvo (ligados ao filemap do Capítulo 3).
- Critérios de saída e gates associados.

---

## 3. Wave 1 — Documentos v2 (fundação da sprint)

Objetivo: estabilizar a visão da S21.2 em documentação antes de qualquer alteração de código.

### 3.1 Arquivos-alvo

- docs/sprint_21_2_capitulo_1.md
- docs/sprint_21_2_capitulo_2_gates.md
- docs/sprint_21_2_capitulo_3_filemap.md
- docs/sprint_21_2_ontologia_fontes_v2.md
- docs/sprint_21_2_fluxos_admin_fontes_v2.md
- docs/sprint_21_2_maquina_estados_copiloto.md
- docs/sprint_21_2_politica_seguranca_copiloto_v2.md
- docs/sprint_21_2_scorecard_copiloto_v2.md

### 3.2 Tarefas principais

1. Revisar os documentos existentes de S21 e S21.1, garantindo que:
   - A ontologia de fontes original (S21) está clara e pode ser estendida.
   - O comportamento atual do Copiloto v1 (S21.1) está corretamente descrito.
2. Atualizar/produzir os documentos da S21.2, garantindo que:
   - refresh_interval está definido conceitualmente (intervalos, expectativas, limitações).
   - o tipo de fonte oficial aberta está claramente descrito (escopo, exemplos, limites).
   - os fluxos admin (criação, edição, status) contemplam os novos campos e status.
   - a máquina de estados do Copiloto está desenhada por tipo de fonte (notícias, clima/esportes, fofoca, oficial aberta).
   - a política de segurança v2 incorpora as novas regras (principalmente em torno de oficiais abertas e operações sensíveis).
   - o scorecard v2 define M1–M4, baseline e metas.

### 3.3 Critérios de saída (Wave 1)

- Todos os arquivos citados em 3.1 existem e refletem a visão atual de S21.2.
- Não há inconsistências óbvias entre docs S21, S21.1 e S21.2.
- É possível ligar cada gate S21_2_G* a um subconjunto claro de documentos.

Gates relacionados:

- S21_2_G0 (Contexto) — verificação de completude do contexto e do vínculo com S21/S21.1.
- S21_2_G1 (Ontologia/Modelo) — garantido inicialmente apenas em nível de documentação.

---

## 4. Wave 2 — Domínio de fontes v2 (refresh, tipo oficial, status)

Objetivo: adaptar o domínio de fontes à ontologia v2, sem ainda alterar o comportamento do Copiloto ou da UI.

### 4.1 Arquivos-alvo

- app/sources/models.py
- app/sources/schemas.py
- app/sources/service.py
- app/sources/validators.py
- app/sources/status.py (caso extraído)
- tests/sources/test_domain_model.py
- tests/sources/test_s21_2_refresh_and_official_type.py
- tests/sources/test_s21_2_status_transitions.py

### 4.2 Tarefas principais

1. Refresh interval:
   - Adicionar o campo refresh_interval ao modelo de Source em models.py.
   - Expor refresh_interval em schemas.py (criação, atualização, leitura).
   - Implementar defaults e validações em service.py (incluindo limites de intervalo e combinações válidas com tipo de fonte).

2. Tipo de fonte oficial aberta:
   - Adicionar o valor de enum para fonte oficial aberta em models.py (ou status/type dedicado).
   - Expor esse tipo em schemas.py e integrá-lo em validators.py.
   - Ajustar service.py para tratar esse tipo de forma uniforme e previsível.

3. Máquina de status:
   - Consolidar estados em status.py (ou em models.py, se o projeto já seguir esse padrão): PENDING, ACTIVE, SUSPENDED, DISABLED, etc.
   - Definir transições válidas e helpers de domínio (por exemplo, can_transition(from_status, to_status)).
   - Ajustar service.py para usar essa tabela de transições, evitando lógica dispersa.

4. Testes de domínio:
   - Estender tests/sources/test_domain_model.py para cobrir refresh_interval e tipo oficial.
   - Implementar tests/sources/test_s21_2_refresh_and_official_type.py.
   - Implementar tests/sources/test_s21_2_status_transitions.py para garantir a correção da máquina de status.

### 4.3 Critérios de saída (Wave 2)

- pytest tests/sources -q em PASS.
- refresh_interval e tipo oficial aberta plenamente integrados ao domínio.
- Máquina de status clara, sem transições silenciosamente inválidas.

Gates relacionados:

- S21_2_G1 (Ontologia/Modelo) — agora validado também em código e testes.
- S21_2_G2 (Fluxos/Status de fonte) — parcialmente atendido via domínio.

---

## 5. Wave 3 — Copiloto v2 (agent, tools, FSM, safety)

Objetivo: evoluir o Copiloto para a versão v2, com fluxos guiados por tipo de fonte, suporte a refresh, edição e status, e reforço de segurança.

### 5.1 Arquivos-alvo

- inspectah/agents/s21_1_copiloto_fontes.py
- inspectah/agents/copiloto_fontes_fsm.py
- inspectah/agents/tools/form_state.py
- inspectah/agents/tools/file_reader.py
- inspectah/agents/tools/logging.py
- inspectah/agents/tools/source_reader.py
- inspectah/agents/tools/status_planner.py
- inspectah/agents/tools/update_planner.py
- docs/sprint_21_2_maquina_estados_copiloto.md
- docs/sprint_21_2_politica_seguranca_copiloto_v2.md
- tests/agents/test_s21_1_copiloto_mode_agent.py
- tests/agents/test_s21_2_copiloto_flows.py
- tests/agents/test_s21_2_copiloto_safety.py

### 5.2 Tarefas principais

1. FSM do Copiloto:
   - Implementar copilot_fontes_fsm.py com estados como: escolher_tipo, coletar_dados, preencher_lacunas, revisar, pronto_para_salvar, editar_existente, planejar_status, etc.
   - Garantir que a FSM contempla fluxos distintos por tipo de fonte (notícias, clima/esportes, fofoca, oficial aberta).

2. Tools de domínio:
   - Evoluir form_state.py para trabalhar com a ontologia v2 (campos, tipos, refresh).
   - Manter file_reader.py e logging.py consistentes com a política de segurança.
   - Implementar source_reader.py para leitura de fontes existentes (edição).
   - Implementar status_planner.py e update_planner.py para criação de planos de alteração de status e edição, sempre passados ao admin para confirmação.

3. Agent principal v2:
   - Evoluir s21_1_copiloto_fontes.py para orquestrar a FSM e as tools.
   - Garantir respeito ao agent_mode on/off.
   - Gerar ações estruturadas para criação, edição e status, sem aplicar alterações sem confirmação do admin.
   - Encapsular a lógica de safety, mantendo o escopo limitado a cadastro/edição de fontes.

4. Segurança v2:
   - Implementar regras descritas em sprint_21_2_politica_seguranca_copiloto_v2.md.
   - Bloquear tópicos fora de escopo (verdades/fatos, Debunker, casos, timelines, etc.).
   - Tratar fontes oficiais abertas com mensagens e limites adequados.

5. Testes de agente:
   - Ajustar test_s21_1_copiloto_mode_agent.py conforme interface final.
   - Implementar test_s21_2_copiloto_flows.py com cenários representativos.
   - Implementar test_s21_2_copiloto_safety.py cobrindo principais riscos.

### 5.3 Critérios de saída (Wave 3)

- pytest tests/agents -q em PASS.
- FSM e tools alinhados aos docs.
- agent_mode on/off funcionando conforme especificação.
- Comportamento de segurança v2 validado por testes.

Gates relacionados:

- S21_2_G2 (FSM) — agora plenamente coberto.
- S21_2_G5 (Agent/Tools).
- S21_2_G6 (Safety).

---

## 6. Wave 4 — Backend + Frontend (API, UI, UX)

Objetivo: conectar o domínio e o Copiloto v2 à API e à interface de admin, garantindo a experiência desejada de criação/edição de fontes.

### 6.1 Arquivos-alvo de backend

- inspectah/api.py
- inspectah/routers/copiloto_fontes.py
- inspectah/services/copiloto_sessions.py
- inspectah/services/copiloto_files.py

### 6.2 Arquivos-alvo de frontend

- frontend/inspectah-ui/src/core/api/api-types.ts
- frontend/inspectah-ui/src/core/api/http-client.ts
- frontend/inspectah-ui/src/modules/admin/api/index.ts
- frontend/inspectah-ui/src/modules/admin/api/copilotoClient.ts

- frontend/inspectah-ui/src/modules/admin/pages/AdminSourcesPage.tsx
- frontend/inspectah-ui/src/modules/admin/pages/AdminSourceFormPage.tsx
- frontend/inspectah-ui/src/modules/admin/pages/AdminSourceDetailPage.tsx
- frontend/inspectah-ui/src/modules/admin/pages/AdminOverviewPage.tsx

- frontend/inspectah-ui/src/modules/admin/components/SourceStatusBadge.tsx
- frontend/inspectah-ui/src/modules/admin/components/SourcesTable.tsx

- frontend/inspectah-ui/src/modules/admin/hooks/useCopilotoAgent.ts
- frontend/inspectah-ui/src/modules/admin/components/CopilotoWidget.tsx
- frontend/inspectah-ui/src/modules/admin/components/CopilotoChatPanel.tsx
- frontend/inspectah-ui/src/modules/admin/components/CopilotoMessageList.tsx
- frontend/inspectah-ui/src/modules/admin/components/CopilotoInputBar.tsx
- frontend/inspectah-ui/src/modules/admin/components/CopilotoFileAttachment.tsx

- Tests de frontend (por exemplo):
  - frontend/inspectah-ui/src/modules/admin/__tests__/AdminSourceFormPage.test.tsx
  - frontend/inspectah-ui/src/modules/admin/__tests__/AdminSourceDetailPage.test.tsx
  - frontend/inspectah-ui/src/modules/admin/__tests__/CopilotoWidget.test.tsx

### 6.3 Tarefas principais

1. Backend:
   - Garantir que copilot_fontes_router está registrado em inspectah/api.py.
   - Ajustar copilot_fontes.py para suportar agent_mode, sessões ligadas a fontes existentes e retorno de actions estruturadas.
   - Ajustar copiloto_sessions.py e copiloto_files.py para armazenar metadados suficientes (tipo de fonte, agent_mode, source_id quando aplicável).

2. API types e client:
   - Atualizar api-types.ts para refletir:
     - campos de fonte (refresh_interval, tipo oficial aberta);
     - payloads do Copiloto (session_id, messages, actions, agent_mode).
   - Ajustar http-client.ts para upload de arquivos com multipart/form-data.
   - Ajustar copilotoclient.ts para expor funções necessárias ao fluxo do widget (criar sessão, enviar mensagem, anexar arquivos, recuperar estado).

3. Telas de admin e widget:
   - AdminSourceFormPage.tsx:
     - Abrir o Copiloto automaticamente ao iniciar criação de uma nova fonte.
     - Tornar obrigatória ao menos uma interação com o Copiloto antes de habilitar o botão de cadastro.
     - Exibir labels e descrições breves para campos-chave (tipo, temas, info_types, endpoint, refresh_interval, status inicial).
   - AdminSourceDetailPage.tsx:
     - Integrar o Copiloto em modo edição (com source_id).
     - Permitir edição assistida de campos (temas, endpoint, refresh, etc.).
     - Expor controles de status (aprovar, suspender, desativar, reativar), com suporte do Copiloto na justificativa/plano.
   - AdminSourcesPage.tsx e SourcesTable.tsx:
     - Exibir tipo de fonte, status atual e refresh_interval.
     - Oferecer filtros simples por tipo/status.
   - CopilotoWidget, useCopilotoAgent e componentes:
     - Refletir agent_mode (toggle visível e comportamento distinto).
     - Aplicar actions recebidas do backend ao formulário, com destaque visual e possibilidade de revisão pelo admin.

4. Testes de frontend:
   - Garantir cobertura para:
     - fluxo de criação com Copiloto obrigatório;
     - fluxo de edição com Copiloto e mudança de status;
     - comportamento do agent_mode on/off;
     - exibição de tipo de fonte, status e refresh na listagem.

### 6.4 Critérios de saída (Wave 4)

- npm run lint, npm test, npm run build em PASS em frontend/inspectah-ui.
- pytest tests/sources -q e pytest tests/agents -q continuam em PASS.
- Fluxos manuais (via browser) de criação/edição de fonte com o Copiloto v2 funcionam conforme especificação de S21.2.

Gates relacionados:

- S21_2_G3 (Backend API).
- S21_2_G4 (Frontend/UX).
- Contribuição para S21_2_G7 (experiência ponta-a-ponta).

---

## 7. Wave 5 — Gates, evidências, scorecards, wrap e GO/NO_GO

Objetivo: consolidar a Sprint 21.2 em termos de gates S21_2_G0…G8, artefatos de evidência e decisão GO/NO_GO.

### 7.1 Scripts de gates

Confirmar existência e correção dos scripts:

- bin/s21_2_g0_contexto.sh
- bin/s21_2_g1_ontologia.sh
- bin/s21_2_g2_fluxos_fsm.sh
- bin/s21_2_g3_backend_api.sh
- bin/s21_2_g4_frontend_ux.sh
- bin/s21_2_g5_agent_tools.sh
- bin/s21_2_g6_safety.sh
- bin/s21_2_g7_scorecard_experiencia.sh
- bin/s21_2_g8_go_no_go.sh

- bin/s21_2_all_gates.sh

Cada script deve:

- Exportar PYTHONPATH=.
- Executar os comandos definidos no Capítulo 2 (pytest, npm, scripts auxiliares).
- Emitir evidências em out/evidence/S21_2_G*/.
- Preencher scorecards em out/scorecards/S21_2_G*.json.

### 7.2 Execução final de testes e gates

1. Testes unitários/integrados:
   - pytest tests/sources -q.
   - pytest tests/agents -q.

2. Frontend:
   - cd frontend/inspectah-ui.
   - npm run lint.
   - npm test.
   - npm run build.

3. Gates consolidados:
   - bin/s21_all_gates.sh.
   - bin/s21_1_all_gates.sh.
   - bin/s21_2_all_gates.sh.

### 7.3 Scorecards e wrap

- Preencher docs/sprint_21_2_scorecard_copiloto_v2.md com:
  - métricas observadas (M1–M4);
  - comparação com baseline (S21/S21.1);
  - análise de trade-offs, se houver.
- Preencher docs/sprint_21_2_wrap_execucao.md com:
  - tabela Gate × Status (S21_2_G0…G8);
  - resumo da experiência do admin com o Copiloto v2;
  - riscos, limitações e itens para futuras sprints (21.3, 22, etc.);
  - recomendação explícita GO/NO_GO.

### 7.4 Decisão GO/NO_GO

- Executar bin/s21_2_g8_go_no_go.sh.
- Verificar out/scorecards/S21_2_G8_go_no_go.json:
  - decision deve ser "GO".
  - all_gates_pass deve ser true.

Critério final da Sprint 21.2:

- S21, S21.1 e S21.2 com all_gates verdes.
- Documentação atualizada.
- Experiência do admin com o Console de Fontes + Copiloto v2 validada e registrada.

---

## 8. Hand-off para S22+ (integração futura)

Objetivo: garantir que o resultado da Sprint 21.2 é claramente utilizável pelas próximas sprints (ingestão contínua, Debunker, timeline).

### 8.1 Contratos de integração

- Revisar/atualizar docs/sprint_21_contratos_s22_s25.md para incluir:
  - APIs do Console de Fontes v2 de que S22 (ingestão), S23 (classificação), S24 (Debunker) e S25 (governança) podem depender;
  - como o refresh_interval e o tipo oficial aberta devem ser respeitados pelos pipelines de ingestão;
  - que o Copiloto é uma ferramenta de apoio ao admin, não uma fonte de verdade/fato — a responsabilização segue humana.

### 8.2 Checklist para squads futuros

- Em docs/sprint_21_2_wrap_execucao.md, incluir uma seção "Para S22+" com:
  - APIs consideradas estáveis;
  - limites claros do Copiloto (o que ele faz e o que não faz);
  - recomendações de extensão (como adicionar novos tipos de fonte e fluxos sem quebrar a arquitetura atual).

### 8.3 Estado final comunicado

- Registrar, em resumo executivo, que:
  - S21 entrega o Console de Fontes estável.
  - S21.1 entrega o Copiloto v1 integrado.
  - S21.2 entrega o Copiloto v2 endurecido (refresh, tipo oficial aberta, edição, status, agent_mode), com scorecards de experiência positivos e alinhamento total com a visão de produto do Inspectah.

Com este plano de execução v2, a Sprint 21.2 deixa de ser somente uma especificação conceitual do Copiloto de Fontes v2 e se torna um roteiro operacional completo: cada wave tem objetivo, arquivos, testes, gates e critérios claros de conclusão, garantindo um avanço seguro e auditável para as próximas sprints.
