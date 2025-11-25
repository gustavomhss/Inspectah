# Sprint 21.2 — Capítulo 2 (Gates, Critérios e Validações) — v2

**Título interno:** Copiloto de Fontes v2 — Gates de Qualidade para Criação, Edição, Status, Refresh e Fontes Oficiais

Este capítulo define o **contrato de qualidade executável** da Sprint 21.2.

- Cada gate S21_2_G*:
  - Tem um objetivo claro.
  - Depende explicitamente de artefatos das S21/S21.1.
  - Possui critérios objetivos (sim/não, números, logs) — nada subjetivo.
  - Gera evidências em `out/evidence/S21_2_G*/` e um scorecard em `out/scorecards/S21_2_G*.json`.
- Todos os gates são invocáveis via scripts `bin/s21_2_g*.sh` e um orquestrador `bin/s21_2_all_gates.sh`.

A 21.2 **não reescreve** a S21/S21.1; ela se encaixa sobre elas, endurecendo o Console + Copiloto de Fontes até o nível exigido no Capítulo 1.

---

## 0. Convenções gerais da S21.2

- Prefixo de evidências: `out/evidence/S21_2_G*/`.
- Prefixo de scorecards: `out/scorecards/S21_2_G*.json`.
- Scripts de gates:
  - `bin/s21_2_g0_contexto.sh`
  - `bin/s21_2_g1_ontologia.sh`
  - `bin/s21_2_g2_fluxos_fsm.sh`
  - `bin/s21_2_g3_backend_api.sh`
  - `bin/s21_2_g4_frontend_ux.sh`
  - `bin/s21_2_g5_agent_tools.sh`
  - `bin/s21_2_g6_safety.sh`
  - `bin/s21_2_g7_scorecard_experiencia.sh`
  - `bin/s21_2_g8_go_no_go.sh`
  - `bin/s21_2_all_gates.sh` (orquestrador)

Cada script:

- Exporta `PYTHONPATH=.`.
- Roda os comandos relevantes.
- Consolida logs em `out/evidence/S21_2_G*/`.
- Atualiza o scorecard correspondente.
- Sai com `exit 0` apenas se o gate estiver **PASS**.

---

## S21_2_G0 — Contexto & Alinhamento com S21 / S21.1

**Objetivo:** Garantir que a S21.2 está construída **em cima** da S21 e S21.1, e não contra elas. Nenhum trabalho da 21.2 pode contradizer a base.

**Script:** `bin/s21_2_g0_contexto.sh`

**Entradas esperadas:**

- Gates S21_G0…S21_G8 em PASS/GO.
- Gates S21.1_G0…S21.1_G8 em PASS/GO.
- `docs/sprint_21_2_capitulo_1.md` presente e sem TODOs pendentes.

**Comportamento mínimo do script:**

1. Rodar sanidade das bases:
   - `.venv/bin/python -m pytest tests/sources -q`
   - `.venv/bin/python -m pytest tests/agents -q`
   - `bash bin/s21_all_gates.sh`
   - `bash bin/s21_1_all_gates.sh`
2. Verificar existência de `docs/sprint_21_2_capitulo_1.md`.
3. Gerar `out/evidence/S21_2_G0/summary.md` com um resumo de:
   - O que S21 faz hoje.
   - O que S21.1 faz hoje.
   - O que S21.2 pretende adicionar, sem reescrever comportamento.

**Critérios de aprovação:**

- Todos os comandos acima retornam exit 0.
- `summary.md` existe e menciona explicitamente:
  - Que a S21.2 **não** altera o modelo base de S21 além de refresh e tipo oficial.
  - Que a S21.2 **não** altera a essência do Copiloto da S21.1, apenas o aprofunda.

**Scorecard:** `out/scorecards/S21_2_G0_contexto.json`

Campos mínimos:

- `s21_all_gates_pass` (bool)
- `s21_1_all_gates_pass` (bool)
- `tests_sources_pass` (bool)
- `tests_agents_pass` (bool)
- `cap1_exists` (bool)
- `notes` (string)

Gate PASS apenas se todos os bool forem `true`.

---

## S21_2_G1 — Ontologia, Modelo de Dados e Tipos (incluindo Fontes Oficiais Abertas)

**Objetivo:** Fixar no código e na documentação a ontologia de fontes pós-21.2, incluindo:

- Campo de **refresh interval** como cidadão de primeira classe.
- Tipo formal para **fonte oficial aberta**.

**Script:** `bin/s21_2_g1_ontologia.sh`

**Entradas esperadas:**

- G0 em PASS.
- Modelo atual de S21 funcionando (sem regressão).

**Comportamento mínimo do script:**

1. Verificar docs:
   - `docs/sprint_21_modelo_dados_fontes.md` atualizado.
   - `docs/sprint_21_2_ontologia_fontes_v2.md` presente.
2. Conferir schema e migrations:
   - Aplicar migrations em um DB limpo de teste:
     - `.venv/bin/python -m inspectah.migrations.apply_s21_2_model --db out/databases/s21_2_sources_test.sqlite` (nome ilustrativo).
   - Extrair snapshot de schema (via PRAGMA ou script Python) e salvar em `out/evidence/S21_2_G1/schema_snapshot.sql`.
3. Validar seeds:
   - Rodar script que inicializa seeds e garante existência de pelo menos 1 fonte oficial aberta.
4. Gerar `out/evidence/S21_2_G1/modelo_dados_diff.md` com diff semântico entre o modelo de S21 e o modelo pós-21.2 (o que entrou, o que mudou).

**Critérios de aprovação:**

- Campo `refresh_interval` (ou equivalente) existe e está:
  - No modelo (`app/sources/models.py`).
  - Nos schemas (`app/sources/schemas.py`).
  - No service (`app/sources/service.py`).
- Tipo de fonte oficial aberta existe na ontologia (enum ou constante) e está documentado.
- Seeds incluem pelo menos uma fonte oficial aberta de exemplo.
- Os docs listados mencionam esses elementos de forma consistente.

**Scorecard:** `out/scorecards/S21_2_G1_ontologia.json`

Campos sugeridos:

- `refresh_interval_in_model` (bool)
- `refresh_interval_in_schemas` (bool)
- `official_open_type_defined` (bool)
- `official_open_seed_exists` (bool)
- `docs_aligned` (bool)
- `notes` (string)

PASS apenas se todos os bool forem `true`.

---

## S21_2_G2 — Fluxos Admin & Máquina de Estados (Fonte + Conversa)

**Objetivo:** Garantir que os fluxos de **criação**, **edição** e **mudança de status** de fontes, bem como a máquina de estados conversacional do Copiloto, estão desenhados, documentados e coerentes com o código.

**Script:** `bin/s21_2_g2_fluxos_fsm.sh`

**Entradas esperadas:**

- G1 em PASS.

**Comportamento mínimo do script:**

1. Verificar existência e integridade de docs:
   - `docs/sprint_21_2_fluxos_admin_fontes_v2.md`.
   - `docs/sprint_21_2_maquina_estados_copiloto.md`.
2. Rodar um script Python que leia:
   - A máquina de estados declarada no doc (por ex., em formato tabela ou JSON embutido).
   - Os estados/transições implementados no agente (`inspectah/agents/s21_1_copiloto_fontes.py` ou módulo v2).
   - As transições de status implementadas no domínio de fontes.
   - E compare, gerando `out/evidence/S21_2_G2/fsm_vs_code_report.md`.

**Critérios de aprovação:**

- Todos os estados documentados da conversa existem no código.
- Não existem estados “fantasma” no código sem representação no doc.
- Transições de status de fonte (pendente, ativa, suspensa, desativada) documentadas e implementadas casam 1:1.

**Scorecard:** `out/scorecards/S21_2_G2_fluxos.json`

Campos:

- `flows_doc_present` (bool)
- `fsm_doc_present` (bool)
- `fsm_matches_code` (bool)
- `status_transitions_match_code` (bool)
- `notes` (string)

PASS apenas se todos forem `true`.

---

## S21_2_G3 — Backend & APIs (Console + Copiloto v2)

**Objetivo:** Garantir que as APIs de fontes e do Copiloto suportam, de fato, o escopo da 21.2: criação, edição, status, refresh, fontes oficiais abertas e `agent_mode`.

**Script:** `bin/s21_2_g3_backend_api.sh`

**Entradas esperadas:**

- G2 em PASS.

**Comportamento mínimo do script:**

1. Rodar testes focados em fontes e Copiloto:
   - `.venv/bin/python -m pytest tests/sources -q`
   - `.venv/bin/python -m pytest tests/agents -k 's21_1 or s21_2' -q`
2. Rodar um script de introspecção da API (ou testes de contrato) que gere:
   - `out/evidence/S21_2_G3/api_contract_sources.json`.
   - `out/evidence/S21_2_G3/api_contract_copiloto.json`.
3. Validar programaticamente que:
   - Endpoints de fontes aceitam e retornam `refresh_interval` e tipo oficial aberta.
   - Endpoints de update permitem edição dos campos principais.
   - Endpoints de mudança de status existem e respeitam as transições válidas.
   - Endpoints do Copiloto aceitam `agent_mode` e retornam actions compatíveis com criação/edição.

**Critérios de aprovação:**

- Testes de `tests/sources` e subconjunto relevante de `tests/agents` passam.
- Contrato de API reflete os novos campos (refresh, tipo oficial) e o `agent_mode`.

**Scorecard:** `out/scorecards/S21_2_G3_backend.json`

Campos:

- `tests_sources_pass` (bool)
- `tests_agents_pass` (bool)
- `sources_api_supports_refresh_and_official` (bool)
- `sources_api_supports_edit_and_status` (bool)
- `copiloto_api_supports_agent_mode` (bool)
- `notes` (string)

PASS apenas se todos forem `true`.

---

## S21_2_G4 — Frontend & UX (Console + Copiloto v2)

**Objetivo:** Verificar que a UI entrega a experiência descrita no Capítulo 1: Copiloto obrigatório na criação, edição assistida, ciclo de status visível, refresh claro, tipo oficial presente.

**Script:** `bin/s21_2_g4_frontend_ux.sh`

**Entradas esperadas:**

- G3 em PASS.

**Comportamento mínimo do script:**

1. Rodar qualidade padrão de frontend:
   - `cd frontend/inspectah-ui`
   - `npm run lint`
   - `npm test`
   - `npm run build`
2. Rodar um teste automatizado (por ex., Playwright ou test script React Testing Library) que:
   - Abre tela de **Nova Fonte** e verifica:
     - Copiloto aberto automaticamente.
     - Botão de criar desabilitado antes de interação com o Copiloto.
     - Presença de descrições curtas em campos-chave.
   - Abre tela de **Detalhe de Fonte** e verifica:
     - Copiloto visível com contexto da fonte.
     - Controles de edição de campos principais.
     - Controles de mudança de status.
   - Verifica presença do toggle **modo agente** e seu reflexo visual.
3. Gerar `out/evidence/S21_2_G4/ux_checklist.md` com marcação explícita de cada item.

**Critérios de aprovação:**

- Lint/test/build em verde.
- Todos os itens do checklist marcados como ok.

**Scorecard:** `out/scorecards/S21_2_G4_frontend.json`

Campos:

- `frontend_lint_pass` (bool)
- `frontend_tests_pass` (bool)
- `frontend_build_pass` (bool)
- `new_source_ux_ok` (bool)
- `edit_source_ux_ok` (bool)
- `copiloto_widget_ok` (bool)
- `notes` (string)

PASS apenas se todos forem `true`.

---

## S21_2_G5 — Agente, Modo Agente e Tools do Copiloto

**Objetivo:** Garantir que o agente do Copiloto v2 realmente implementa o fluxo guiado, respeita o `agent_mode` e usa tools de domínio para criar/editar/status/refresh, sem “magia negra” escondida.

**Script:** `bin/s21_2_g5_agent_tools.sh`

**Entradas esperadas:**

- G4 em PASS.

**Comportamento mínimo do script:**

1. Rodar testes de agente:
   - `.venv/bin/python -m pytest tests/agents -k 's21_1 or s21_2' -q`
2. Rodar um conjunto de cenários automatizados (ou semi-automatizados) que simulem mensagens ao Copiloto e gravem:
   - Pelo menos 2 cenários de criação (notícias e oficial aberta).
   - Pelo menos 2 cenários de edição (ajuste de refresh, mudança de temas/endpoint).
   - Pelo menos 1 cenário de mudança de status.
   - Em ambos os `agent_mode = on` e `off`.
3. Gravar os logs desses cenários em `out/evidence/S21_2_G5/agent_scenarios.log`.
4. Rodar um script de verificação de FSM vs docs (pode reaproveitar o do G2) focado no agente.

**Critérios de aprovação:**

- Testes de agente passam.
- Logs de cenário mostram claramente:
  - Uso de tools de domínio (form_state, leitura de fonte, logging).
  - Respeito ao `agent_mode` (respostas mais proativas em on, mais conservadoras em off).
  - Presença de planos de alteração antes de ações de edição/status.

**Scorecard:** `out/scorecards/S21_2_G5_agent.json`

Campos:

- `tests_agents_pass` (bool)
- `agent_mode_respected` (bool)
- `create_flows_ok` (bool)
- `edit_flows_ok` (bool)
- `status_flows_ok` (bool)
- `notes` (string)

PASS apenas se todos forem `true`.

---

## S21_2_G6 — Segurança, Escopo e Safety

**Objetivo:** Blindar o Copiloto de Fontes v2 contra abusos, confusões e escapes de escopo, com foco especial em fontes oficiais e em operações destrutivas (desativar/remover/aprovar sem critério).

**Script:** `bin/s21_2_g6_safety.sh`

**Entradas esperadas:**

- G5 em PASS.

**Comportamento mínimo do script:**

1. Verificar docs de segurança:
   - `docs/sprint_21_1_politica_seguranca_copiloto.md`.
   - `docs/sprint_21_2_politica_seguranca_copiloto_v2.md`.
2. Rodar testes de safety:
   - `.venv/bin/python -m pytest tests/agents -k 's21_1_copiloto_safety or s21_2_copiloto_safety' -q`
3. Extrair amostras de logs de decisões sensíveis e salvar em `out/evidence/S21_2_G6/logging_sample.log`.

**Critérios de aprovação:**

- Testes de safety passam.
- As políticas de segurança deixam explícito que o Copiloto:
  - Atua apenas no domínio de fontes.
  - Não decide verdade/fato.
  - Não manipula usuários, casos, timelines.
  - Trata fontes oficiais com cuidado: pode ajudar no cadastro, mas não promete ingestão/validação de conteúdo.
- Logs de exemplo mostram registro de decisões como:
  - sugestões de mudança de status,
  - propostas de desativação,
  - interações com fontes oficiais.

**Scorecard:** `out/scorecards/S21_2_G6_safety.json`

Campos:

- `safety_tests_pass` (bool)
- `scope_enforced` (bool)
- `sensitive_decisions_logged` (bool)
- `notes` (string)

PASS apenas se todos forem `true`.

---

## S21_2_G7 — Scorecard de Experiência Ponta-a-Ponta (Admin)

**Objetivo:** Medir, na prática, se a experiência do admin com Console + Copiloto v2 bate com a visão do Capítulo 1 — principalmente em criação, edição, status, refresh e fontes oficiais abertas.

**Script:** `bin/s21_2_g7_scorecard_experiencia.sh`

**Entradas esperadas:**

- G6 em PASS.

**Comportamento mínimo do script:**

1. Guiar (ou automatizar parcialmente) a execução de cenários manuais:
   - C1: Criar fonte de notícias com Copiloto em modo agente.
   - C2: Criar fonte de clima/esportes.
   - C3: Criar fonte oficial aberta (ex.: IBGE ou similar).
   - C4: Editar fonte (ajustando refresh + temas).
   - C5: Aprovar uma fonte inicialmente pendente.
   - C6: Suspender e reativar uma fonte.
2. Coletar para cada cenário:
   - Tempo aproximado.
   - Se foi necessário burlar o Copiloto (fazer via formulário manual por limitação dele).
   - Problemas de UX ou coerência encontrados.
3. Consolidar em:
   - `out/evidence/S21_2_G7/cenarios_execucao.md` (tabela C1–C6).
   - `docs/sprint_21_2_scorecard_copiloto_v2.md` com as métricas abaixo.

**Métricas mínimas (Cap. 1):**

- **M1**: % de cenários concluídos usando o Copiloto **sem fallback manual pesado** (meta: >= 0.9).
- **M2**: Tempo médio para cadastrar fonte de notícias com Copiloto (comparado a um baseline manual da S21, meta: não piorar e, idealmente, melhorar).
- **M3**: % de operações de status realizadas com Copiloto (meta: >= 0.8 nos cenários C5/C6).
- **M4**: % de fontes criadas/alteradas com refresh configurado corretamente (meta: 1.0).

**Scorecard:** `out/scorecards/S21_2_G7_scorecard.json`

Campos:

- `m1_success_without_fallback` (float 0–1)
- `m2_avg_time_create_news` (float)
- `m3_status_with_copiloto` (float 0–1)
- `m4_refresh_configured_ratio` (float 0–1)
- `meets_thresholds` (bool)
- `notes` (string)

PASS apenas se `meets_thresholds = true` e todas as metas forem atingidas.

---

## S21_2_G8 — GO/NO_GO da Sprint 21.2

**Objetivo:** Tomar a decisão final de GO/NO_GO da Sprint 21.2 com base em **dados** (gates, scorecards e experiência).

**Script:** `bin/s21_2_g8_go_no_go.sh`

**Entradas esperadas:**

- S21_2_G0…G7 em PASS.

**Comportamento mínimo do script:**

1. Ler todos os scorecards `out/scorecards/S21_2_G*.json`.
2. Verificar se todos os gates estão em PASS e, quando houver métricas, se `meets_thresholds = true`.
3. Gerar:
   - `out/scorecards/S21_2_G8_go_no_go.json` com:
     - `decision`: "GO" ou "NO_GO".
     - `all_gates_pass`: bool.
     - `reason`: texto curto.
   - `out/evidence/S21_2_G8_go_no_go/MANIFEST.json` listando os scorecards considerados.
4. Atualizar wrap humano em `docs/sprint_21_2_wrap_execucao.md` com tabela Gate × Status, resumo e recomendação.

**Critérios de aprovação:**

- `decision = "GO"`.
- `all_gates_pass = true`.
- Wrap humano reflete a decisão e aponta riscos remanescentes claramente.

---

## Encerramento do Capítulo 2 (v2)

Com estes gates, a Sprint 21.2 ganha uma barra de qualidade concreta:

- Nada entra sem estar amarrado a um gate, evidências e scorecard.
- A experiência do admin com o Copiloto de Fontes v2 é medida, não apenas “sentida”.
- S21 e S21.1 continuam sendo base estável; a 21.2 só é GO se **apertar os parafusos** do Console + Copiloto sem introduzir regressões.

O Capítulo 3 deve agora mapear estes gates para um filemap detalhado (docs, código, scripts, testes) e o Capítulo 4 deve transformar isso em um plano de execução reprodutível (comandos, ordem, spans de trabalho).

