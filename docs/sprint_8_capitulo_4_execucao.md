# Inspectah – Sprint 8 (Capítulo 4)
## Plano de Execução Orientado a Gates – Roteiro Cirúrgico para o Codex (v2)

---

### 0. One‑liner oficial do Capítulo 4

> **“O Capítulo 4 v2 é o roteiro cirúrgico da Sprint 8: uma sequência de passos concretos para o Codex, amarrados por invariantes globais e pelos gates T0–T8, que leva do repositório atual até Admin v0, Usuário v0 e o fluxo Inspectah → Evidências → GPT → Resposta em GO.”**

Aqui não tem filosofia: só o **como fazer na prática**, em qual ordem, em quais arquivos, com quais invariantes globais.

---

### 1. Invariantes globais da Sprint 8

Estes invariantes devem ser verdadeiros **em todo ponto onde os gates forem rodados**. Se algum for violado, a sprint está em NO‑GO até corrigir.

1. **Nenhuma query de demo sem rastro completo**
   - Para qualquer query usada nos 3 cenários oficiais:
     - existe um `QueryLog` em `out/evidence/s8_queries`;
     - existe um `EvidenceBundle` em `out/evidence/s8_bundles` com `id == evidence_bundle_id` do log;
     - existe uma resposta GPT associada (`gpt_response_ref`) em `out/evidence/s8_responses` (ou equivalente).

2. **Nenhum golden usando dados fora de fixture**
   - Todos os testes em `tests/s8_t4_golden_flows` utilizam **apenas** fixtures em `tests/fixtures/s8_*` e/ou storage local preenchido a partir delas.
   - É proibido depender de endpoints externos ou dados "mágicos".

3. **Nenhum uso de GPT fora do client único**
   - Qualquer chamada de modelo passa por `app/gpt_client/client.py::run_query`.
   - Scripts de teste ou handlers não podem conversar direto com o modelo.

4. **Nenhum código relevante fora do filemap da S8**
   - Qualquer módulo novo de core/UI/Admin/Usuário deve viver em `app/...` conforme Cap. 3 v2.
   - Scripts de gates vivem em `bin/` e não escondem lógica de negócio.

5. **Nenhuma mudança que quebre T0–T3 ignorada**
   - Qualquer alteração em Cap. 1–3, modelos ou contratos exige reexecutar pelo menos T0–T3.

Os gates, especialmente T4–T6, são construídos para detectar automaticamente violações desses invariantes.

---

### 2. Fases da execução (timeline objetiva)

A timeline continua em 7 fases, mas agora com foco em **tarefas atômicas** para o Codex.

- **Fase 0 – Preparação e higiene** → T0
- **Fase 1 – Núcleo de domínio e pipeline core** → T1, T2, T3
- **Fase 2 – GPT client e contrato de resposta** → integra core + GPT
- **Fase 3 – Camada Admin e ingestão mínima** → abastece dados das demos
- **Fase 4 – Camada Usuário e experiência de consulta** → expõe `/user/query`
- **Fase 5 – Goldens, performance e rastreabilidade** → T4, T5, T6
- **Fase 6 – CI e GO/NO‑GO** → T7, T8

Em cada fase: 
- **Entrada:** o que já precisa existir/estar verde.
- **Saída:** o que muda no repo + quais gates podem rodar.
- **Checklist cirúrgico:** lista de ações para o Codex.

---

### 3. Fase 0 – Preparação (T0 e esqueleto de projeto)

**Entrada:** repo atual da Inspectah com DNA/Sprints já presentes.

**Saída:** docs da S8 presentes, árvore mínima criada, T0 em PASS.

#### 3.1. Ações para o Codex

1. Verificar/garantir docs
   - Confirmar presença dos arquivos:
     - `docs/sprint_8_capitulo_1.md`
     - `docs/sprint_8_capitulo_2_gates.md`
     - `docs/sprint_8_capitulo_3_arquitetura.md`
     - `docs/sprint_8_cenarios_demo.md`
   - Se faltar algum, criar stub copiando a versão aprovada deste projeto.

2. Criar/ajustar árvore mínima
   - Garantir existência de:
     - `app/admin/`, `app/user/`, `app/core/`, `app/gpt_client/`
     - `tests/`, `tests/fixtures/`, `tests/goldens/`
     - `bin/`, `out/evidence/`, `out/scorecards/`

3. Implementar `bin/s8_t0_scope_and_alignment.sh`
   - Script deve:
     - checar presença dos docs acima;
     - opcional: conferir hashes simples (ou ao menos tamanhos não zero);
     - checar existência dos diretórios base;
     - escrever `out/evidence/S8_T0_scope/summary.json`;
     - escrever `out/scorecards/S8_T0_scope.json` com `status: PASS|FAIL`.

4. Rodar T0
   - `PYTHONPATH=. bin/s8_t0_scope_and_alignment.sh` deve sair com `0`.

**Gate:** T0 em PASS.

---

### 4. Fase 1 – Núcleo de domínio e pipeline core (T1, T2, T3)

**Entrada:** T0 PASS, árvore criada.

**Saída:** core implementado (sem GPT real), T1–T3 PASS.

#### 4.1. Passo 1 – Modelos e storage lógico

Arquivos alvo:
- `app/core/models.py`
- `app/core/storage.py`

Ações cirúrgicas:

1. Criar modelos em `models.py`
   - Implementar classes/data classes para `Source`, `SourceConfig`, `SourceStatus`, `Item`, `EvidenceItemRef`, `EvidenceBundle`, `QueryLog` exatamente como no Cap. 3 v2.

2. Implementar storage mínimo em `storage.py`
   - Funções obrigatórias (assinaturas sugeridas):
     - `save_source(source: Source) -> None`
     - `get_source(source_id: str) -> Optional[Source]`
     - `save_item(item: Item) -> None`
     - `list_items_by_filter(...) -> list[Item]` (parâmetros definidos para S8)
     - `save_evidence_bundle(bundle: EvidenceBundle) -> None`
     - `load_evidence_bundle(bundle_id: str) -> EvidenceBundle`
     - `save_query_log(log: QueryLog) -> None`
     - `load_query_log(query_id: str) -> QueryLog`
   - Implementar em cima de arquivos JSON em `out/evidence/s8_*`.

#### 4.2. Passo 2 – Parsing, busca e bundles

Arquivos alvo:
- `app/core/query_parser.py`
- `app/core/search_internal.py`
- `app/core/evidence_bundle_builder.py`

Ações:

1. `query_parser.py`
   - Implementar `parse_query(user_query: str) -> ParsedQuery` com regras determinísticas (regex/listas) para:
     - classificar query em `agregacao_simples`, `comparacao_simples`, `checagem_factual_simples`, `fora_de_escopo`;
     - extrair entidades mínimas (produto/cidade/pessoa/caso), conforme descrito no Cap. 3.

2. `search_internal.py`
   - Implementar `search_internal(parsed: ParsedQuery) -> list[Item]` usando `storage.list_items_by_filter`.
   - Respeitar limites simples de datas/locais conforme fixtures.

3. `evidence_bundle_builder.py`
   - Implementar `build_evidence_bundle(parsed, items) -> EvidenceBundle`:
     - limitar itens por fonte a `N_max_por_fonte` (constante);
     - popular `query_filters` e `items_by_source`;
     - chamar `storage.save_evidence_bundle`.

#### 4.3. Passo 3 – Pipeline e logging

Arquivos alvo:
- `app/core/pipeline.py`

Ações:

1. Implementar `run_pipeline(user_query: str) -> UserResponse` em 3 passos internos (por enquanto com GPT stub):
   - `parsed = parse_query(user_query)`
   - `items = search_internal(parsed)`
   - `bundle = build_evidence_bundle(parsed, items)`
   - `gpt_answer = stub_gpt_answer(bundle, user_query)` (stub temporário nesta fase)
   - `response = build_user_response(bundle, gpt_answer)`
   - `log_query(...)` grava `QueryLog`.

2. Implementar `log_query(...)` usando `storage.save_query_log`.

**Invariante reforçado nesta fase:** toda execução de `run_pipeline` que chegue até o fim deve gerar **sempre** um `QueryLog` e, se `status == "ok"`, um `EvidenceBundle` persistido.

#### 4.4. Passo 4 – Testes e gates T1, T2, T3

Arquivos alvo:
- `tests/s8_t2_unit_contracts/…`
- `tests/s8_t3_property/…`
- `bin/s8_t1_static_quality.sh`
- `bin/s8_t2_unit_and_contracts.sh`
- `bin/s8_t3_property_and_edge_cases.sh`

Ações:

1. Implementar T1
   - `s8_t1_static_quality.sh` roda:
     - `python -m compileall app`
     - lint/format (`ruff`/`flake8` + `black` ou equivalente)
     - scan simples de segredos.

2. Implementar testes T2
   - Em `tests/s8_t2_unit_contracts/`, criar testes diretos para:
     - `parse_query`
     - `search_internal`
     - `build_evidence_bundle`
     - `run_pipeline` com GPT stub.

3. Implementar testes T3
   - Em `tests/s8_t3_property/`, criar cenários de:
     - `dados_insuficientes`;
     - conflito extremo de fontes;
     - `fora_de_escopo`.

4. Criar scripts T2/T3
   - `s8_t2_unit_and_contracts.sh` → `pytest tests/s8_t2_unit_contracts`
   - `s8_t3_property_and_edge_cases.sh` → `pytest tests/s8_t3_property`

**Gates:** T1, T2, T3 em PASS.

---

### 5. Fase 2 – GPT client e contrato de resposta

**Entrada:** T1–T3 PASS com GPT stub.

**Saída:** GPT client implementado, pipeline chamando `run_query`, formato de resposta estável.

#### 5.1. Prompts de verdade local

Arquivo alvo:
- `app/gpt_client/prompts.py`

Ações:

1. Definir template principal de prompt:
   - instruir o modelo a **usar somente** o evidence bundle fornecido;
   - definir formato de resposta estruturada (campos de `summary_structured` + flags);
   - explicar como responder em caso de falta de dados, conflitos, fora de escopo.

#### 5.2. Client único do GPT

Arquivo alvo:
- `app/gpt_client/client.py`

Ações:

1. Implementar `run_query(bundle, user_query, query_type) -> GptAnswer`:
   - montar prompt a partir de `bundle` + `user_query` + `query_type`;
   - chamar o modelo (no ambiente local, Codex pode ficar em mock);
   - parsear retorno para `GptAnswer` com:
     - `answer_text: str`
     - `summary_structured: dict`
     - `confidence_flags: dict`.

2. Garantir que **nenhum outro código** chama GPT diretamente.

#### 5.3. Integrar pipeline

Arquivo alvo:
- `app/core/pipeline.py`

Ações:

1. Substituir `stub_gpt_answer` por `gpt_client.run_query`.
2. Adaptar `build_user_response` para usar `GptAnswer.summary_structured`.
3. Ajustar `QueryLog` para guardar referência a `GptAnswer` (`gpt_response_ref`).

#### 5.4. Ajustar testes para mocks

Ações:

1. T2/T3 continuam com mocks de `run_query` (sem depender de modelo real).
2. Preparar utilidades de mock para T4/T5 (podem alternar entre GPT real e simulado).

**Invariante:** nenhuma chamada ao GPT fora de `gpt_client.run_query`.

---

### 6. Fase 3 – Camada Admin e ingestão mínima

**Entrada:** core e GPT client prontos, T1–T3 PASS.

**Saída:** Admin v0 funcional, fontes e dados suficientes para os 3 cenários.

#### 6.1. Handlers Admin

Arquivos alvo:
- `app/admin/routes.py`
- `app/admin/schemas.py`
- `app/admin/service.py`

Ações:

1. Definir DTOs em `schemas.py` para:
   - criação/edição de fonte;
   - resultado de teste de fonte;
   - status de fonte.

2. Implementar handlers em `routes.py`:
   - `POST /admin/sources` → cria/atualiza `Source` via `service.py` + `storage.save_source`;
   - `POST /admin/sources/{source_id}/test` → chama conector em dry‑run e retorna `sample_items`;
   - `GET /admin/sources/{source_id}/status` → lê `SourceStatus` do storage.

3. Implementar lógica em `service.py` para:
   - validar tipos suportados na S8;
   - atualizar `SourceConfig` e `SourceStatus`.

#### 6.2. Conectores mínimos e ingestão

Ações:

1. Implementar conectores simples (podem ser funções em `service.py` ou módulo à parte) para:
   - fonte de preços (usando fixtures ou arquivo JSON);
   - fonte de notícias/decisões (idem).

2. Implementar função de ingestão mínima que:
   - lê de fixture/arquivo;
   - cria `Item` com `payload` normalizado;
   - chama `storage.save_item` e atualiza `SourceStatus`.

#### 6.3. Fixtures alinhadas com Admin

Ações:

1. Ajustar `tests/fixtures/s8_preco_medio`, `s8_comparacao`, `s8_checagem_factual` para refletir o formato de `Item.payload`.

**Saída da Fase 3:** é possível registrar fontes e popular itens de teste que o core consegue consumir.

---

### 7. Fase 4 – Camada Usuário e experiência de consulta

**Entrada:** Admin v0 funcional, core+GPT prontos.

**Saída:** `/user/query` funcionando, proto‑UI opcional, rota pronta para demos.

#### 7.1. Handler `/user/query`

Arquivos alvo:
- `app/user/routes.py`
- `app/user/schemas.py`
- `app/user/view_models.py`

Ações:

1. Definir DTO de entrada/saída em `schemas.py` conforme Cap. 3 v2.
2. Implementar handler em `routes.py` que:
   - valida `query`;
   - chama `pipeline.run_pipeline(query)`;
   - transforma resultado em DTO de saída (incluindo `status`).

3. `view_models.py` pode conter helpers para montar estruturas de UI (cards, listas etc.).

#### 7.2. Proto‑UI / experiência de demo

Opcional mas recomendado:

1. Criar três "quadros" de demo (podem ser rotas simples, páginas ou até scripts de terminal):
   - Preço médio → roda uma query típica e mostra resposta + resumo + botão "Ver evidências";
   - Comparação → idem;
   - Checagem factual → idem.

2. Storyboard mínimo (para operador humano):
   - **Passo 1:** abrir tela Admin, cadastrar fontes, rodar "Testar";
   - **Passo 2:** rodar ingestão (separado ou embutido); verificar status;
   - **Passo 3:** abrir tela Usuário, enviar query; observar resposta e resumo;
   - **Passo 4:** clicar/ver link de evidências; checar itens e fontes usados.

**Essa experiência deve ser a mesma que T4/T5 automatizam via testes.**

---

### 8. Fase 5 – Goldens, performance e rastreabilidade (T4, T5, T6)

**Entrada:** fluxos Admin/Usuário/core/GPT funcionando para os 3 cenários.

**Saída:** goldens criados, T4–T6 PASS.

#### 8.1. Goldens dos 3 cenários (T4)

Arquivos alvo:
- `tests/goldens/s8_preco_medio.json`
- `tests/goldens/s8_comparacao_simples.json`
- `tests/goldens/s8_checagem_factual.json`
- `tests/s8_t4_golden_flows/…`

Ações:

1. Executar manualmente os 3 cenários em ambiente controlado.
2. Capturar saída JSON do endpoint `/user/query` (ou da camada imediatamente abaixo).
3. Salvar como goldens, limpando campos não determinísticos (ids, timestamps, etc.) ou marcando-os como toleráveis.
4. Implementar testes T4 que:
   - preparam dados/fixtures;
   - chamam Admin/ingestão se necessário;
   - chamam `/user/query`;
   - comparam com goldens (ignorando apenas campos marcados).

#### 8.2. Performance (T5)

Arquivo alvo:
- `bin/s8_t5_perf_and_limits.sh`

Ações:

1. Script deve:
   - rodar cada cenário N vezes (5–10);
   - medir tempo total da requisição (pelo menos do handler em diante);
   - calcular p50/p95 por cenário;
   - medir tamanho médio dos bundles.
2. Escrever `out/evidence/S8_T5_perf/summary.json` com métricas.

#### 8.3. Rastreabilidade (T6)

Arquivo alvo:
- `bin/s8_t6_logs_and_evidence.sh`

Ações:

1. Script deve:
   - varrer `out/evidence/s8_queries`;
   - para cada `query_id` usada nos cenários oficiais, verificar `evidence_bundle_id` e `gpt_response_ref`;
   - conferir existência de arquivos correspondentes em `s8_bundles` e `s8_responses`;
   - checar consistência básica (contagem de itens, fontes etc.).
2. Escrever `out/evidence/S8_T6_logs_evidence/summary.json` e scorecard.

**Gates:** T4, T5, T6 em PASS **e** invariantes globais 1–3 mantidos.

---

### 9. Fase 6 – CI e GO/NO‑GO (T7, T8)

**Entrada:** T0–T6 PASS localmente.

**Saída:** CI reproduzível e T8 com decisão GO/NO‑GO.

#### 9.1. Script agregador CI

Arquivo alvo:
- `bin/s8_ci.sh`

Ações:

1. Implementar script que roda, em ordem:
   - `bin/s8_t1_static_quality.sh`
   - `bin/s8_t2_unit_and_contracts.sh`
   - `bin/s8_t3_property_and_edge_cases.sh`
   - `bin/s8_t4_golden_flows.sh`
   - `bin/s8_t5_perf_and_limits.sh`
   - `bin/s8_t6_logs_and_evidence.sh`
2. Propagar exit code ≠ 0 se qualquer gate falhar.

#### 9.2. Workflow de CI remoto (T7)

Arquivo alvo:
- `.github/workflows/s8-ci.yml`
- `bin/s8_t7_ci_pipeline.sh`

Ações:

1. Criar workflow que:
   - roda em PRs/commits relevantes;
   - instala dependências;
   - executa `bin/s8_ci.sh`.
   - expõe ambiente `NET=0` e parte de uma venv local (`.venv`) para reaproveitar os scripts dos gates.
2. Implementar `s8_t7_ci_pipeline.sh` que:
   - roda `bin/s8_ci.sh` localmente;
   - escreve `out/evidence/S8_T7_ci/summary.json` + scorecard T7.

#### 9.3. GO/NO‑GO (T8)

Arquivo alvo:
- `bin/s8_t8_go_no_go.sh`

Ações:

1. Implementar script que:
   - lê scorecards `S8_T0_scope.json` … `S8_T7_ci.json`;
   - se qualquer tiver `status != "PASS"`, gera `decision: "NO_GO"`;
   - se todos estiverem `"PASS"`, gera `decision: "GO"`;
   - grava `out/evidence/S8_T8_go_no_go/summary.json` + `out/scorecards/S8_T8_go_no_go.json`.

**Gate:** T7 PASS, T8 com decisão consistente.

---

### 10. Fio contínuo até Truth‑DB e blockchain (olho em S10–S12)

Durante a execução da S8, o Codex deve manter explícito que:

1. `Item`, `EvidenceBundle` e `QueryLog` já são **proto‑entidades** da futura Truth‑DB.
   - `Item` ≈ evento bruto;
   - `EvidenceBundle` ≈ conjunto de evidências usado para decidir um fato;
   - `QueryLog` ≈ histórico de consultas e decisões.

2. Paths e formatos escolhidos em S8 não podem inviabilizar:
   - adicionar campos como `block_id`, `fact_id`, `version_id` em S10;
   - registrar blocos “lacrados” em blockchain em S11;
   - abrir threads de contestação em S12.

3. Qualquer decisão de implementação que afete esses modelos deve ser anotada (ex.: em um `docs/sprint_8_decisoes_arquitetura.md`) para guiar as Sprints 10–12.

---

### 11. Checklist final da Sprint 8

Antes de declarar a Sprint 8 concluída, o time deve verificar, de forma binária:

1. Gates
   - T0–T7 com `status: "PASS"` e evidências presentes.
   - T8 com `decision: "GO"`.

2. Demos
   - Os 3 cenários oficiais rodam:
     - via scripts (T4/T5);
     - via fluxo humano (Admin → ingestão → Usuário → evidências).

3. Rastreabilidade
   - Para cada query de demo existe log + bundle + resposta rastreáveis.

4. Anti‑alucinação (escopo da S8)
   - Evidências usadas nas demos vêm **apenas** de fixtures/storage local;
   - Prompts de GPT deixam claro o uso exclusivo do bundle.

5. Documentação
   - Cap. 1–4 em versões finais; qualquer desvio anotado.

Se qualquer ponto acima estiver em dúvida, a Sprint 8 é tratada como **NO‑GO** até correção, reexecução dos gates relevantes e atualização dos scorecards.

---

### 12. Barra de qualidade do Capítulo 4 v2

O Cap. 4 v2 só é considerado cumprido se:

- o Codex conseguir, a partir dele, gerar um plano de trabalho de terminal (comandos/conteúdo de arquivos) sem perguntar “por onde começar”; 
- os gates T0–T8 puderem ser implementados **sem inventar novas estruturas** fora do Cap. 3;
- qualquer novo membro de time conseguir ler Cap. 1–4 e entender a história completa da Sprint 8: o que ela entrega, como é validada, onde mora cada coisa e como isso prepara terreno para Truth‑DB e blockchain.

Esse capítulo é, oficialmente, o **roteiro de execução da Sprint 8**. Tudo que for feito em S8 deve apontar de volta para ele, para o Cap. 3 (arquitetura) e para o Cap. 2 (gates), fechando o ciclo com o Cap. 1 (visão).
