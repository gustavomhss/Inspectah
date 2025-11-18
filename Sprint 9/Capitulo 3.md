# Inspectah — Sprint 9  
## Capítulo 3 — Arquitetura, Filemap, Contratos e Amarração com Gates (v2)

---

### 0. Propósito e relação com Cap. 1 e Cap. 2

O Capítulo 3 traduz o **Capítulo 1** (visão, invariantes, objetivos) e o **Capítulo 2** (gates T0–T8) em **arquitetura concreta + mapa de arquivos**.

Ele responde:

- **Onde** cada parte da Sprint 9 vive no código e nos dados?  
- **Quais módulos** implementam Admin v1, User v1, GPT especializado, trilha de evidência e observabilidade mínima?  
- **Como** cada gate T0–T8 se ancora em componentes específicos?

Este capítulo é o elo Cap.1 ↔ Cap.2 ↔ código:

- Cap. 1 define **invariantes globais** (Inv1–Inv4) e objetivos de produto;  
- Cap. 2 define **gates leoninos** que provam essas invariantes;  
- Cap. 3 define **camadas, módulos e arquivos** que cada gate toca.

---

### 1. Mapa rápido — camadas, invariantes e gates

Invariantes globais da S9 (Cap. 1):

- **Inv1** — nenhuma resposta sem trilha completa de evidência (QueryLog ↔ EvidenceBundle ↔ UserResponse).  
- **Inv2** — nenhum cenário oficial usando fonte única (sempre `meta.num_sources >= 2`).  
- **Inv3** — nenhuma decisão GPT fora do bundle.  
- **Inv4** — nenhum erro crítico silencioso.

Camadas principais da S9 e o que cada uma guarda:

- **Core (app/core/)** — guardião primário de **Inv1** e co‑guardião de **Inv2**.  
- **Admin (app/admin/)** — guardião primário de **Inv2** (múltiplas fontes ativas) e co‑guardião de **Inv4** (erros de fonte não silenciosos).  
- **User (app/user/)** — guardião da experiência que reflete **Inv1–Inv4** para o usuário (principalmente mensagens claras e acesso à evidência).  
- **GPT Engine (app/gpt_client/)** — guardião primário de **Inv3** e co‑guardião de estabilidade para T5.  
- **Observabilidade (app/observability/, out/evidence/)** — guardião primário de **Inv4**, reforçando Inv1/Inv2.  
- **Gates & CI (bin/, tests/, .github/)** — guardam a execução mecânica de **T0–T8**.

Visão gate → camadas principais:

- **T0**: docs (Cap. 1–4) + mapeamento invariantes/gates (este capítulo).  
- **T1**: todo código tocado por S9 (Core, Admin, User, GPT, Obs, scripts/gates).  
- **T2**: Core + Admin + User + GPT (mockado).  
- **T3**: Core + Admin + User + GPT (bordas).  
- **T4**: Core + Admin + User + GPT + fixtures/goldens.  
- **T5**: User + Core + GPT + Obs (métricas, carga, estabilidade).  
- **T6**: Core + Obs (artefatos out/evidence/ e logs), com Admin/User garantindo visibilidade.  
- **T7**: bin/, .github/workflows/ (CI executando T1–T6).  
- **T8**: bin/ + docs/sprint_9_summary.md consolidando tudo.

---

### 2. Visão arquitetural em camadas (sem quebrar a S8)

A S9 **não recria** a arquitetura; ela estende a base estruturada pela S8.

- Tudo que é **infra básica de Inspectah** (setup de app, servidor HTTP, configs genéricas, partes do Core já validadas na S8) continua sob a "guarda" da S8.  
- A S9 adiciona/ajusta **camadas de produto interno v0**: Admin v1, User v1, GPT especializado por tipo, observabilidade mínima de produto e novos gates.

Camadas:

1. **Core (Domínio & Pipeline)**  
   Modelos, pipeline QueryLog → EvidenceBundle → GPT → UserResponse, persistência de evidência.

2. **Admin v1**  
   Operador gerencia fontes, status e ingestão, garantindo ≥ 2 fontes por tipo de pergunta oficial.

3. **User v1**  
   Usuário interno faz perguntas (C1–C3) e recebe respostas explicáveis com evidência.

4. **GPT Decision Engine**  
   Prompts especializados, client bundle‑only, configuração determinística.

5. **Observabilidade & Evidência**  
   Métricas, logs, evidências em disco, ganchos para T5/T6.

6. **Gates & CI**  
   Scripts em `bin/`, suites em `tests/`, workflow `s9-ci.yml`.

Regras de convivência com S8:

- Não remover nem quebrar contratos que a S8 criou (por exemplo, caminhos já usados em S8 para bundles/fixtures).  
- Ao refatorar qualquer módulo compartilhado (ex.: `app/core/pipeline.py`), garantir que os testes e gates da S8 permaneçam verdes.  
- Qualquer alteração estrutural que impacte S8 deve ser documentada em `docs/sprint_9_summary.md` como decisão consciente.

---

### 3. Tipos de pergunta e fluxo C1–C3

Tipos oficiais:

1. **C1 — Preço médio (agregação simples)**  
2. **C2 — Comparação simples (ex.: onde está mais barato)**  
3. **C3 — Checagem factual simples (fato público básico)**

Fluxo comum (por tipo):

`User v1 (rota HTTP) → QueryParser → Core Pipeline → EvidenceBundle → GPT Prompt especializado → GPT Client → UserResponse + Summary → Persistência (QueryLog + Bundle + Resposta) → Observabilidade (métricas + logs)`

Gates que exercitam esse fluxo:

- **T2**: unidade/contratos por módulo.  
- **T3**: propriedades/bordas.  
- **T4**: goldens de C1–C3.  
- **T5**: latência, estabilidade, throughput.  
- **T6**: integridade de trilha.

---

### 4. Modelo de domínio — entidades centrais da S9

Local principal: `app/core/models.py` (estendendo a base da S8).

Guardam diretamente **Inv1** e ajudam na **Inv2**.

Entidades centrais:

1. **InfoType / QueryType**  
   Local sugerido: `app/core/query_types.py`  
   - representa tipos de pergunta (C1, C2, C3);  
   - usado para roteamento, métricas e goldens.

2. **Source**  
   - `id`, `name`, `info_type`, `config`, `is_active`.  
   - conecta Admin v1 aos fluxos C1–C3.

3. **SourceStatus**  
   - `source_id`, `last_run_at`, `last_run_status`, `items_ingested_recent`, `last_error_summary`.  
   - base para telas de status de Admin (Inv4).

4. **QueryLog**  
   - `id`, `timestamp`, `user_input`, `info_type`, `scenario_tag` (C1–C3),  
   - referências para `bundle_id` e `user_response_id`,  
   - flags de erro.  
   - é o pilar inicial de **Inv1**.

5. **EvidenceBundle**  
   - `id`, `info_type`, `sources_meta`, `items`, `meta`.  
   - `meta.num_sources` é obrigatório (Inv2).  
   - `sources_meta` descreve cada fonte usada (nome, peso, qualidade, etc.).

6. **BundleItem**  
   - um item de evidência (por exemplo, um preço em determinada fonte, ou um trecho factual).

7. **UserResponse**  
   - `id`, `query_log_id`, `answer_text`,  
   - `summary_structured` (valor, intervalo, período, nº de fontes, confiança, etc.),  
   - `confidence`, `limitations`, `raw_gpt_payload` (opcional);  
   - fecha a ponta da **Inv1**.

Gates que dependem fortemente desses modelos:

- **T2**: valida contratos e criação do triplo QueryLog/Bundle/UserResponse.  
- **T3**: garante comportamento correto com dados insuficientes/divergentes.  
- **T4**: assegura que goldens estão em cima de entidades consistentes.  
- **T6**: audita a integridade da trilha nos artefatos reais.

---

### 5. Core — pipeline de consulta e evidência

Diretório: `app/core/`

Arquivos principais:

- `query_types.py` — enums InfoType/QueryType para C1, C2, C3.  
- `models.py` — entidades de domínio (vide acima).  
- `query_parser.py` — transforma `UserQueryRequest` em `QuerySpec`/`InfoType`.  
- `search_internal.py` — busca dados em fontes ativas para um tipo de pergunta.  
- `evidence_bundle_builder.py` — junta dados em `EvidenceBundle` com `meta.num_sources >= 2` nos cenários oficiais.  
- `pipeline.py` — orquestra o fluxo completo:  
  - cria `QueryLog`;  
  - chama search + bundle builder;  
  - delega decisão ao GPT Engine;  
  - cria/persiste `UserResponse`;  
  - retorna DTO para User v1.  
- `storage.py` — persistência em disco (JSON) em `out/evidence/` (logs, bundles, responses).

Amarração com gates (Cap. 2):

- **T2**: testa contratos do pipeline, incluindo criação do triplo e chamadas ao GPT (mockado).  
- **T3**: testa propriedades de pipeline: dados insuficientes, divergência, erros de fonte, fora de escopo.  
- **T4**: executa pipeline completo nos cenários C1–C3 e compara com goldens.  
- **T5**: mede latência e estabilidade do pipeline sob carga.  
- **T6**: inspeciona artefatos gerados por pipeline (QueryLog, bundles, responses) para garantir Inv1/Inv2.

---

### 6. Camada Admin v1

Diretório: `app/admin/`

Arquivos:

- `schemas.py` — DTOs para requests/responses de Admin (fonte, status, ingestão).  
- `service.py` — lógica de:
  - criar/editar/ativar/desativar fontes;  
  - atualizar e ler `SourceStatus`;  
  - garantir, nos ambientes de demo, **≥ 2 fontes ativas por InfoType** usado pela S9;  
  - usar fixtures e ingestores da S9 quando apropriado.
- `routes.py` — rotas HTTP (ou equivalentes) para:
  - listar fontes;  
  - criar/editar/ativar/desativar fontes;  
  - visualizar status e erros recentes.  
- `validators.py` — validações centralizadas (URLs, campos obrigatórios, ranges, etc.).

Função arquitetural:

- Implementar Admin v1 como descrito no Cap. 1;  
- Garantir **Inv2** (multi‑fonte) e apoiar **Inv4** (erros de fonte visíveis, não silenciosos).

Gates que dependem fortemente de Admin:

- **T2**: contratos de service/validators (cadastro/edição/status).  
- **T3**: comportamentos com erro de fonte e dados insuficientes originados na Admin.  
- **T4**: execução de cenários C1–C3 via Admin para preparar goldens.  
- **T6**: verificação de que fontes quebradas aparecem de forma rastreável.

---

### 7. Camada User v1

Diretório: `app/user/`

Arquivos:

- `schemas.py` — DTOs:
  - `UserQueryRequest`: texto, tipo de pergunta (C1–C3), parâmetros adicionais;  
  - `UserQueryResponse`: texto principal, resumo estruturado, evidências principais, confiança, mensagens de erro.
- `view_models.py` — transforma `UserResponse` em DTO consistente; garante que sempre existam campos esperados no resumo estruturado.
- `routes.py` — rotas HTTP de User v1:
  - endpoint de pergunta/resposta;  
  - integração com pipeline central;  
  - feedback de estado (buscando dados, resposta pronta, dados insuficientes, erro de fonte, fora de escopo).

Função arquitetural:

- Implementar a experiência de User v1 descrita no Cap. 1 para C1–C3;  
- Tornar visíveis as invariantes Inv1–Inv4 para o usuário (mensagens claras, acesso a evidências, confiança).

Gates que dependem fortemente de User:

- **T2**: DTOs e caminhos felizes por tipo de pergunta.  
- **T3**: mensagens adequadas em bordas (dados insuficientes, fora de escopo, erros de fonte).  
- **T4**: goldens de fluxo completo (Admin → User).  
- **T5**: latência, estabilidade e throughput da User API.  
- **T6**: coerência entre UserResponse e bundles/QueryLogs.

---

### 8. GPT Decision Engine — prompts e client

Diretório: `app/gpt_client/`

Arquivos:

- `prompts.py` — construtores de prompt:
  - `build_price_prompt(bundle, query_spec)` (C1);  
  - `build_comparison_prompt(bundle, query_spec)` (C2);  
  - `build_fact_prompt(bundle, query_spec)` (C3);  
  - todos usam **exclusivamente** dados do `EvidenceBundle` + query (Inv3).

- `client.py` — interface única `run_query(info_type, bundle, query_spec)`:
  - escolhe o prompt correto;  
  - aplica configuração determinística (temperatura baixa, seed, etc.);  
  - converte resposta bruta em estrutura compatível com `UserResponse` ou payload intermediário;  
  - não realiza chamadas de rede fora das permitidas (por exemplo, sem web scraping ou consultas extras).

Função arquitetural:

- Implementar a **Inv3**: nenhuma decisão GPT fora do bundle;  
- Contribuir para estabilidade de T5 (respostas consistentes entre runs).

Gates que dependem fortemente do GPT Engine:

- **T2**: contratos de entrada/saída (via mocks).  
- **T3**: comportamento sob divergência de fontes e dados insuficientes (sem inventar fatos).  
- **T4**: respostas goldens coerentes com bundles.  
- **T5**: estabilidade entre diversas execuções.

---

### 9. Observabilidade & Evidências (concreto para T5/T6)

Diretório sugerido: `app/observability/metrics_s9.py` + integração em rotas/pipeline.

#### 9.1 Métricas mínimas e labels

Mínimo de métricas (nomes ilustrativos):

- `inspectah_s9_user_queries_total{info_type, outcome}`  
  - `info_type ∈ {C1, C2, C3}`;  
  - `outcome ∈ {success, insufficient_data, out_of_scope, source_error, unexpected_error}`.

- `inspectah_s9_user_latency_seconds{info_type}`  
  - histograma ou summary com buckets adequados para medir p50/p95 (por ex. [0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]).

- `inspectah_s9_admin_actions_total{action}`  
  - `action ∈ {create_source, update_source, activate_source, deactivate_source, run_ingest}`.

- `inspectah_s9_errors_total{route, kind}`  
  - `route ∈ {admin, user, core}`,  
  - `kind ∈ {validation, source_failure, pipeline_failure, gpt_failure, unknown}`.

Ganchos obrigatórios:

- `app/user/routes.py`  
  - incrementa `user_queries_total` com labels corretas para cada request;  
  - observa latência total da API (para `user_latency_seconds`);  
  - registra erros inesperados em `errors_total` com `route="user"`.

- `app/admin/routes.py`  
  - incrementa `admin_actions_total` conforme ação;  
  - registra erros em `errors_total` com `route="admin"`.

- `app/core/pipeline.py`  
  - em caso de falha de fonte/pipeline, garante que `errors_total` seja atualizado com `route="core"` e `kind` adequado.

Essas métricas atendem diretamente ao que T5/T6 precisam medir (latência, volume, taxa de erro, tipos de erro).

#### 9.2 Evidência em disco (out/evidence/)

Responsável: `app/core/storage.py` + scripts auxiliares em `scripts/`.

Paths padrão da S9:

- `out/evidence/s9_logs/` — logs estruturados de QueryLog e execução.  
- `out/evidence/s9_bundles/` — bundles JSON da S9.  
- `out/evidence/s9_responses/` — respostas `UserResponse` da S9.  
- `out/evidence/S9_TN_*/` — evidências específicas de cada gate T0–T8 (resumo + manifestos).

Gates:

- **T5**: lê métricas para avaliar p95 e taxa de erro por cenário C1–C3; pode exportar snapshots em `out/evidence/S9_T5_perf_and_limits/`.  
- **T6**: percorre `QueryLog` → `EvidenceBundle` → `UserResponse` em `s9_logs/`, `s9_bundles/`, `s9_responses/` para garantir Inv1–Inv2–Inv4.

---

### 10. Testes, suites e amarração por gate

Diretório base: `tests/`

#### 10.1 Gate → diretórios/módulos principais

- **T2 — Unit & Contracts**  
  - Diretório: `tests/s9_t2_unit_contracts/`  
  - Foca em:  
    - `app/core/models.py`, `app/core/query_parser.py`, `app/core/pipeline.py`, `app/core/storage.py`;  
    - `app/admin/schemas.py`, `app/admin/service.py`, `app/admin/validators.py`;  
    - `app/user/schemas.py`, `app/user/view_models.py`, `app/user/routes.py` (caminhos felizes);  
    - `app/gpt_client/client.py` (mockado) e `app/gpt_client/prompts.py`.

- **T3 — Property & Edge Cases**  
  - Diretório: `tests/s9_t3_property/`  
  - Foca em:  
    - pipeline em cenários de dados insuficientes, divergência, erro de fonte, fora de escopo;  
    - integração Admin + Core + User nesses casos;  
    - comportamento do GPT Engine com bundles problemáticos (sempre via mocks).

- **T4 — Golden Flows**  
  - Diretório: `tests/s9_t4_golden_flows/`  
  - Foca em:  
    - C1–C3 completos: Admin (configura fontes) → ingestão → User → comparação com goldens.

- **T5 — Perf & Limits**  
  - Pode usar: `scripts/s9_perf_runner.py` (opcional)  
  - Foca em:  
    - rotas de User v1 sob carga;  
    - pipeline + GPT Engine em execução repetida;  
    - leitura de métricas (via endpoints ou client interno);  
    - geração de summary com p50/p95, taxa de erro, estabilidade.

- **T6 — Logs & Evidence Integrity**  
  - Pode usar: `scripts/s9_evidence_auditor.py` (opcional)  
  - Foca em:  
    - traversal de QueryLog → Bundle → UserResponse;  
    - verificação de `meta.num_sources >= 2`;  
    - ausência de erros silenciosos.

Fixtures e goldens:

- Fixtures:  
  - `tests/fixtures/s9_preco_medio/`  
  - `tests/fixtures/s9_comparacao/`  
  - `tests/fixtures/s9_checagem_factual/`

- Goldens:  
  - `tests/goldens/s9_preco_medio.json`  
  - `tests/goldens/s9_comparacao_simples.json`  
  - `tests/goldens/s9_checagem_factual.json`

---

### 11. Scripts de gates e CI

Diretório: `bin/`

Scripts principais da S9:

- `s9_t0_scope_and_alignment.sh`  
- `s9_t1_static_quality.sh`  
- `s9_t2_unit_and_contracts.sh`  
- `s9_t3_property_and_edge_cases.sh`  
- `s9_t4_golden_flows.sh`  
- `s9_t5_perf_and_limits.sh`  
- `s9_t6_logs_and_evidence.sh`  
- `s9_t7_ci_pipeline.sh`  
- `s9_t8_go_no_go.sh`  
- `s9_ci.sh` (orquestrador T1–T6)

Cada script:

- resolve a raiz (`git rev-parse --show-toplevel`);  
- faz `cd` para a raiz;  
- força `NET=0`;  
- chama os testes/ferramentas apropriados de acordo com Cap. 2;  
- grava summary + scorecard;  
- sai com código 0 apenas em caso de `status = "PASS"`.

Workflow de CI:

- `.github/workflows/s9-ci.yml`  
  - configura Python + `.venv`;  
  - exporta `NET=0`;  
  - executa `bin/s9_ci.sh` com `PYTHONPATH=.`;  
  - é marcado como obrigatório para merges em `main`.

---

### 12. Filemap da Sprint 9

Resumo dos caminhos principais introduzidos/tocados pela S9:

```text
/docs
  sprint_9_capitulo_1.md
  sprint_9_capitulo_2_gates.md
  sprint_9_capitulo_3_arquitetura.md
  sprint_9_capitulo_4_execucao.md
  sprint_9_cenarios_demo.md
  sprint_9_summary.md

/app
  /core
    models.py
    query_types.py
    query_parser.py
    search_internal.py
    evidence_bundle_builder.py
    pipeline.py
    storage.py

  /admin
    __init__.py
    schemas.py
    service.py
    routes.py
    validators.py

  /user
    __init__.py
    schemas.py
    view_models.py
    routes.py

  /gpt_client
    __init__.py
    prompts.py
    client.py

  /observability
    __init__.py
    metrics_s9.py

/tests
  /s9_t2_unit_contracts
  /s9_t3_property
  /s9_t4_golden_flows

  /fixtures
    /s9_preco_medio
    /s9_comparacao
    /s9_checagem_factual

  /goldens
    s9_preco_medio.json
    s9_comparacao_simples.json
    s9_checagem_factual.json

/scripts
  s9_perf_runner.py
  s9_evidence_auditor.py

/bin
  s9_t0_scope_and_alignment.sh
  s9_t1_static_quality.sh
  s9_t2_unit_and_contracts.sh
  s9_t3_property_and_edge_cases.sh
  s9_t4_golden_flows.sh
  s9_t5_perf_and_limits.sh
  s9_t6_logs_and_evidence.sh
  s9_t7_ci_pipeline.sh
  s9_t8_go_no_go.sh
  s9_ci.sh

/.github/workflows
  s9-ci.yml
```

Este filemap é o **contrato físico** da Sprint 9: qualquer novo arquivo relevante deve ser adicionado aqui ou documentado no Cap. 4; qualquer remoção que afete S8/S9 precisa ser tratada como decisão consciente.

---

### 13. Handshake com Capítulo 4 (Execução)

O Capítulo 4 usará esta arquitetura e este filemap para:

- fatiar o trabalho em fases (core, Admin, User, GPT, observabilidade, gates);  
- encaixar cada fase em um subconjunto de gates (por exemplo, core + T2/T3, depois goldens + T4, depois perf+obs + T5/T6 etc.);  
- descrever o roteiro de demo de produto v0 da S9 (C1–C3) referenciando explicitamente as rotas, DTOs, métricas e artefatos definidos aqui.

Se houver divergência entre o que for implementado e este Capítulo 3, o correto é **atualizar conscientemente este capítulo** e, se necessário, o Capítulo 1/2 — nunca deixar a arquitetura real se afastar silenciosamente da arquitetura declarada.

