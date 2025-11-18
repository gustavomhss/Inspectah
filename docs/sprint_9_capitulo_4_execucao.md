# Inspectah – Sprint 9  
## Capítulo 4 — Plano de Execução Orientado a Gates (Roteiro Cirúrgico) — v2

---

### 0. One‑liner oficial do Capítulo 4

“Este capítulo é o roteiro cirúrgico da Sprint 9: uma sequência finita de fases, cada uma amarrada a gates T0–T8, que leva do estado atual (S8 concluída) até o produto interno v0 da Inspectah S9 em GO, sem deixar nenhuma invariante solta.”

Aqui não tem filosofia: só **como executar**, em **que ordem**, **em quais arquivos**, **com quais gates**. Se alguma fase não fecha seus gates ou seu DoD, a sprint está automaticamente em **NO‑GO** até ser corrigida.

---

### 1. Invariantes globais da Sprint 9 (fio condutor)

As invariantes da S9 (Cap. 1) são o fio condutor de todo o plano:

1) **Inv1 — nenhuma resposta sem trilha completa de evidência**  
   Para qualquer resposta da S9, principalmente nos cenários oficiais C1–C3:
   - existe um `QueryLog` com ID estável;  
   - existe um `EvidenceBundle` com `id == bundle_id` referenciado pelo log;  
   - existe um `UserResponse` com `id == user_response_id` e referências coerentes ao log/bundle.

2) **Inv2 — nenhum cenário oficial usando fonte única**  
   - Para qualquer execução dos cenários oficiais C1, C2, C3, o bundle utilizado tem `meta.num_sources >= 2`.

3) **Inv3 — nenhuma decisão GPT fora do bundle**  
   - Toda decisão passa por prompts especializados que usam apenas `EvidenceBundle` + query;  
   - não há consultas externas nem “atalhos” ao GPT fora de `app/gpt_client/client.py`.

4) **Inv4 — nenhum erro crítico silencioso**  
   - Falhas relevantes em fontes, pipeline, GPT ou rotas são sempre logadas/metricadas e visíveis para Admin/User, não escondidas.

O restante deste capítulo explica **como cada fase** empurra essas invariantes de "definidas" (Cap. 1) para "provadas" (via gates T0–T8, Cap. 2 + arquitetura do Cap. 3).

---

### 2. Cockpit da Sprint 9 — visão 30 segundos

Tabela de navegação rápida por fase:

| Fase | Objetivo principal | Gates foco | Invariantes foco | Arquivos‑chave | Comandos típicos |
|------|--------------------|-----------|------------------|----------------|------------------|
| 0 | Setup, T0, proteger S8 | T0 (+ S8 T* ) | Inv1–Inv4 (no plano) | `docs/sprint_9_capitulo_*.md`, `bin/s9_t0_scope_and_alignment.sh` | `PYTHONPATH=. bin/s9_t0_scope_and_alignment.sh` |
| 1 | Core S9 (triplo QueryLog→Bundle→UserResponse) | T1, T2/T3 mínimos | Inv1 (principal), Inv2 (parcial), Inv4 (básico) | `app/core/*`, `tests/s9_t2_unit_contracts`, `tests/s9_t3_property` | `bin/s9_t1_static_quality.sh`, `bin/s9_t2_unit_and_contracts.sh`, `bin/s9_t3_property_and_edge_cases.sh` |
| 2 | Admin v1 (multi‑fonte e status) | T2, T3 | Inv2 (principal), Inv4 (erros de fonte) | `app/admin/*`, fixtures S9 | `bin/s9_t2_unit_and_contracts.sh`, `bin/s9_t3_property_and_edge_cases.sh` |
| 3 | User v1 (experiência C1–C3) | T2, T3 | Inv1 (user‑facing), Inv2 (via bundles), Inv4 (mensagens) | `app/user/*` | `bin/s9_t2_unit_and_contracts.sh`, `bin/s9_t3_property_and_edge_cases.sh` |
| 4 | GPT specialized engine | T2, T3 (contratos) | Inv3 (principal), Inv1/Inv2 (consistência) | `app/gpt_client/*`, `app/core/pipeline.py` | `bin/s9_t2_unit_and_contracts.sh`, `bin/s9_t3_property_and_edge_cases.sh` |
| 5 | Observabilidade & evidência S9 | Pré‑T5/T6 | Inv4 (principal), Inv1/Inv2 (trilha) | `app/observability/metrics_s9.py`, hooks em `routes.py`, `storage.py` | testes unitários + comandos T5/T6 em dry‑run |
| 6 | Fixtures, goldens, T4–T6 completos | T4, T5, T6 | Inv1–Inv4 (fechadas para C1–C3) | `tests/fixtures/s9_*`, `tests/goldens/s9_*`, `tests/s9_t4_golden_flows`, `bin/s9_t4..6` | `bin/s9_t4_golden_flows.sh`, `bin/s9_t5_perf_and_limits.sh`, `bin/s9_t6_logs_and_evidence.sh` |
| 7 | CI da S9, T7 e T8 | T7, T8 | Inv1–Inv4 (automatizadas) | `bin/s9_ci.sh`, `bin/s9_t7_ci_pipeline.sh`, `bin/s9_t8_go_no_go.sh`, `.github/workflows/s9-ci.yml`, `docs/sprint_9_summary.md` | `bin/s9_t7_ci_pipeline.sh`, `bin/s9_t8_go_no_go.sh` |
| 8 | Demo humana + checklist final | (usa T4–T6) | Inv1–Inv4 (validadas na prática) | `docs/sprint_9_summary.md`, `docs/sprint_9_cenarios_demo.md` | scripts de demo + consultas via Admin/User |

Use esta tabela como painel de cockpit antes de abrir o terminal.

---

### 3. Fase 0 — Setup, T0 e proteção da base S8

**Objetivo:** começar a Sprint 9 com base limpa, docs consolidados, filemap alinhado e S8 preservada.

**Invariantes foco da fase:**
- Inv1–Inv4 no plano (definidas e mapeadas), ainda não provadas em execução.

**Entradas:**
- Branch da sprint criada;  
- repositório íntegro;  
- S8 concluída/verde.

**Saídas:**
- Docs S9 no repo;  
- filemap mínimo da S9 criado;  
- T0 PASS;  
- S8 revalidada.

Passos:

1) Confirmar docs da S9 no repositório
   - Verificar em `docs/`:
     - `sprint_9_capitulo_1.md`  
     - `sprint_9_capitulo_2_gates.md`  
     - `sprint_9_capitulo_3_arquitetura.md`  
     - `sprint_9_capitulo_4_execucao.md` (este capítulo)  
     - `sprint_9_cenarios_demo.md` (cenários C1–C3 reais ou inspirados em casos reais).
   - Se algum estiver só no canva, primeiro passo é trazê‑lo para o repo.

2) Garantir filemap físico mínimo (Cap. 3)
   - Verificar existência de diretórios principais (`app/core`, `app/admin`, `app/user`, `app/gpt_client`, `app/observability`, `tests`, `tests/fixtures`, `tests/goldens`, `bin`, `out/evidence`, `out/scorecards`, `.github/workflows`).
   - Criar diretórios faltantes, mantendo compatibilidade com S8.

3) Implementar/ajustar `bin/s9_t0_scope_and_alignment.sh`
   - Checa docs e diretórios;  
   - gera `out/evidence/S9_T0_scope/summary.json`;  
   - gera `out/scorecards/S9_T0_scope.json` com `status`.

4) Rodar T0
   - `PYTHONPATH=. bin/s9_t0_scope_and_alignment.sh` → esperado `status: "PASS"`.

5) Proteger S8
   - Rodar suíte principal/gate final da S8;  
   - corrigir qualquer regressão antes de seguir.

**DoD da Fase 0 (só acaba quando):**
- T0 está em PASS;  
- todos os capítulos da S9 e `sprint_9_cenarios_demo.md` estão versionados em `docs/`;  
- diretórios do filemap S9 existem;  
- S8 foi reexecutada com sucesso.

---

### 4. Fase 1 — Core S9: domínio, pipeline e trilha de evidência

**Objetivo:** consolidar o núcleo da S9 no Core, garantindo que a criação do triplo QueryLog → EvidenceBundle → UserResponse é estável e testável.

**Invariantes foco da fase:**
- Inv1: parcialmente provada (triplo criado e persistido);  
- Inv2: iniciada (meta.num_sources presente e usada);  
- Inv4: iniciada (erros básicos não silenciosos no pipeline).

**Entradas:**
- T0 PASS;  
- filemap pronto.

**Saídas:**
- Core S9 implementado;  
- T1 PASS;  
- T2/T3 mínimos PASS focados em Core.

Arquivos‑chave:

- `app/core/query_types.py`  
- `app/core/models.py`  
- `app/core/query_parser.py`  
- `app/core/search_internal.py`  
- `app/core/evidence_bundle_builder.py`  
- `app/core/pipeline.py`  
- `app/core/storage.py`

Passos principais:

1) Ajustar modelos (Cap. 3)
   - Garantir que entidades centrais refletem o Cap. 3;  
   - `QueryLog` referencia `bundle_id` e `user_response_id`;  
   - `EvidenceBundle.meta.num_sources` é obrigatório.

2) Confirmar pipeline
   - `query_parser.py`: User DTO → QuerySpec/InfoType;  
   - `search_internal.py`: busca dados por InfoType;  
   - `evidence_bundle_builder.py`: monta bundles válidos;  
   - `pipeline.py`: orquestra QueryLog → bundle → GPT (mockado nesta fase) → UserResponse; persiste tudo.

3) Storage S9
   - `storage.py`: grava logs/bundles/respostas de S9 em `out/evidence/s9_logs/`, `s9_bundles/`, `s9_responses/`.

4) T1 — Static quality
   - Implementar `bin/s9_t1_static_quality.sh` conforme Cap. 2 (compileall, 0 TODO/FIXME, scanner de segredos);  
   - rodar `PYTHONPATH=. bin/s9_t1_static_quality.sh`.

5) T2/T3 mínimos
   - Criar `tests/s9_t2_unit_contracts/` e `tests/s9_t3_property/`;  
   - escrever testes mínimos para:  
     - criação do triplo QueryLog/Bundle/UserResponse;  
     - validação de `meta.num_sources`;  
     - casos de dados insuficientes/divergência/out‑of‑scope básicos (mock GPT).  
   - rodar `bin/s9_t2_unit_and_contracts.sh` e `bin/s9_t3_property_and_edge_cases.sh`.

**DoD da Fase 1:**
- T1, T2, T3 estão em PASS;  
- funções centrais do Core criam e persistem o triplo corretamente;  
- `meta.num_sources` é usado pelo bundle builder;  
- há testes cobrindo os caminhos principais do Core.

---

### 5. Fase 2 — Admin v1: múltiplas fontes e visão de operador

**Objetivo:** entregar um Admin v1 funcional que permita gerenciar fontes e status, garantindo multi‑fonte para C1–C3.

**Invariantes foco da fase:**
- Inv2: fortemente reforçada (Admin garante ≥ 2 fontes ativas por tipo);  
- Inv4: reforçada (erros de fonte visíveis via status).

**Entradas:**
- Core S9 estável;  
- T1–T3 mínimos passando.

**Saídas:**
- Admin v1 implementado;  
- T2/T3 PASS cobrindo fluxos de Admin.

Arquivos‑chave:

- `app/admin/schemas.py`  
- `app/admin/service.py`  
- `app/admin/routes.py`  
- `app/admin/validators.py`  
- `tests/fixtures/s9_*`

Passos principais:

1) DTOs e serviço de Admin
   - `schemas.py`: DTOs para fontes e status;  
   - `service.py`: criar/editar/ativar/desativar fontes; manter `SourceStatus`; garantir ≥ 2 fontes por InfoType para cenários C1–C3.

2) Rotas de Admin
   - `routes.py`: endpoints para listar/gerir fontes e ver status/erros recentes.

3) Fixtures iniciais
   - Iniciar fixtures em `tests/fixtures/s9_preco_medio/`, `s9_comparacao/`, `s9_checagem_factual/` para alimentar Admin.

4) Testes T2/T3
   - T2: contratos de Admin (criação/edição/status, multi‑fonte garantido);  
   - T3: bordas de Admin (fonte inválida, fonte fora do ar, fontes insuficientes).

5) Rodar gates
   - `PYTHONPATH=. bin/s9_t2_unit_and_contracts.sh`;  
   - `PYTHONPATH=. bin/s9_t3_property_and_edge_cases.sh`.

**DoD da Fase 2:**
- Admin v1 permite, via API, cadastrar/editar/ativar/desativar fontes;  
- existem rotas para visualizar status e erros;  
- é possível, a partir de fixtures, configurar ≥ 2 fontes por tipo para C1–C3;  
- T2/T3 PASS com testes cobrindo fluxos de Admin.

---

### 6. Fase 3 — User v1: experiência de consulta C1–C3

**Objetivo:** entregar a experiência de User v1 para C1–C3, com respostas explicáveis e aderentes às invariantes.

**Invariantes foco da fase:**
- Inv1: provada do ponto de vista do usuário (respostas sempre vêm com evidência);  
- Inv2: refletida em UI (informação sobre múltiplas fontes, quando fizer sentido);  
- Inv4: reforçada (mensagens claras em casos de erro/bordas).

**Entradas:**
- Core + Admin v1 estáveis.

**Saídas:**
- rotas de User v1 prontas para C1–C3;  
- T2/T3 PASS cobrindo caminhos felizes e bordas de User.

Arquivos‑chave:

- `app/user/schemas.py`  
- `app/user/view_models.py`  
- `app/user/routes.py`

Passos principais:

1) DTOs de User v1
   - `UserQueryRequest`: texto, tipo, parâmetros;  
   - `UserQueryResponse`: texto principal, resumo estruturado (valor, intervalo, nº fontes, confiança), evidências principais, mensagens de erro.

2) View‑models
   - Helpers em `view_models.py` para mapear `UserResponse` → `UserQueryResponse`.

3) Rotas User
   - Endpoint principal: valida request, chama `pipeline.run_pipeline`, devolve DTO;  
   - garantir mensagens adequadas para dados insuficientes, fora de escopo, erros de fonte.

4) Testes T2/T3
   - T2: caminhos felizes C1–C3 (Admin + Core + User);  
   - T3: mensagens e comportamento em bordas.

5) Rodar gates
   - `PYTHONPATH=. bin/s9_t2_unit_and_contracts.sh`;  
   - `PYTHONPATH=. bin/s9_t3_property_and_edge_cases.sh`.

**DoD da Fase 3:**
- Usuário interno consegue executar C1–C3 via User v1;  
- respostas contêm resumo estruturado coerente e referências de evidência;  
- mensagens para bordas estão implementadas e testadas;  
- T2/T3 PASS cobrindo User v1.

---

### 7. Fase 4 — GPT especializado e estabilidade

**Objetivo:** ligar o GPT Decision Engine real da S9 (prompts especializados + client determinístico) e garantir que ele respeita Inv3 e suporta estabilidade para T5.

**Invariantes foco da fase:**
- Inv3: implementada (todas as decisões via bundle‑only + prompts especializados);  
- Inv1/Inv2: consistência com bundles confirmada;  
- preparação para estabilidade de respostas (base para T5).

**Entradas:**
- Core + Admin + User com GPT mockado.

**Saídas:**
- GPT Engine real plugado;  
- T2/T3 PASS com contratos de GPT bem definidos.

Arquivos‑chave:

- `app/gpt_client/prompts.py`  
- `app/gpt_client/client.py`  
- `app/core/pipeline.py`

Passos principais:

1) Prompts especializados
   - `build_price_prompt`, `build_comparison_prompt`, `build_fact_prompt`:  
     - usam apenas `EvidenceBundle` + query;  
     - descrevem formato de `summary_structured`;  
     - instruem o modelo sobre como reagir a dados insuficientes/divergência/fora de escopo.

2) Client determinístico
   - `run_query(info_type, bundle, query_spec)`:  
     - escolhe prompt;  
     - aplica configuração determinística;  
     - parseia resposta em estrutura consumível.

3) Ajuste do pipeline
   - `pipeline.py` usa apenas `gpt_client.run_query`;  
   - nenhuma chamada direta a GPT em outros módulos.

4) Testes T2/T3 com mocks
   - T2/T3 continuam mockando GPT, testando contratos de entrada/saída.

5) Rodar gates
   - `bin/s9_t2_unit_and_contracts.sh`;  
   - `bin/s9_t3_property_and_edge_cases.sh`.

**DoD da Fase 4:**
- GPT Engine real está implementado (prompts + client);  
- pipeline chama unicamente o client;  
- T2/T3 PASS com contratos de GPT cobrindo C1–C3 e bordas.

---

### 8. Fase 5 — Observabilidade & evidências S9 (T5/T6‑ready)

**Objetivo:** instalar a camada de observabilidade da S9 (métricas + logs + evidência em disco) de forma compatível com T5 e T6.

**Invariantes foco da fase:**
- Inv4: fortemente reforçada (erros nunca silenciosos);  
- Inv1/Inv2: trilha de evidência consolidada em disco + métricas.

**Entradas:**
- Core + Admin + User + GPT estáveis.

**Saídas:**
- métricas S9 expostas;  
- paths de evidência S9 consolidados;  
- mecanismo concreto para T5 ler métricas;  
- base pronta para T6 auditar trilhas.

Arquivos‑chave:

- `app/observability/metrics_s9.py`  
- ganchos em `app/user/routes.py`, `app/admin/routes.py`, `app/core/pipeline.py`  
- `app/core/storage.py`  
- (opcional) `scripts/s9_perf_runner.py`, `scripts/s9_evidence_auditor.py`

Passos principais:

1) Implementar métricas S9
   - Em `metrics_s9.py`, expor:
     - `inspectah_s9_user_queries_total{info_type, outcome}`;  
     - `inspectah_s9_user_latency_seconds{info_type}`;  
     - `inspectah_s9_admin_actions_total{action}`;  
     - `inspectah_s9_errors_total{route, kind}`.

2) Instalar ganchos
   - `user/routes.py`: atualizar contadores de query, latência e erros;  
   - `admin/routes.py`: atualizar contadores de ações;  
   - `core/pipeline.py`: registrar erros de pipeline/fonte/GPT em `errors_total`.

3) Confirmar paths de evidência
   - `storage.py`: grava QueryLog, bundles e respostas de S9 em `out/evidence/s9_logs/`, `s9_bundles/`, `s9_responses/`.

4) Definir como T5 lê métricas
   - Escolher um mecanismo explícito (e documentar):  
     - via endpoint `/metrics` da aplicação (com Prometheus‑style output); **ou**  
     - via cliente interno que lê o registrador de métricas do processo;  
   - se usar endpoint, documentar a rota em Cap. 3/4 e em `docs/sprint_9_cenarios_demo.md`;  
   - se usar cliente interno, implementar helper em `metrics_s9.py` ou `scripts/s9_perf_runner.py` que retorna p50/p95 e contadores.

**Pré‑condição explícita para Fase 6/T5:**
- Não rodar T5 enquanto **não houver** caminho definido e implementado para leitura de métricas (endpoint ou client interno) com acesso a `user_latency_seconds` e `user_queries_total`.

**DoD da Fase 5:**
- Métricas S9 existem e são atualizadas por Admin/User/Core;  
- arquivos de evidência S9 são gravados nos diretórios padrão;  
- existe uma função/caminho claro para T5 ler as métricas necessárias;  
- Inv4 está visivelmente instrumentada (erros relevantes aumentam `errors_total`).

---

### 9. Fase 6 — Fixtures, goldens e gates T4–T6 completos

**Objetivo:** consolidar fixtures/goldens para C1–C3, executar gates T4–T6 completos com métricas e auditoria de evidência, provando Inv1–Inv4 na prática.

**Invariantes foco da fase:**
- Inv1–Inv4: fechadas para os cenários oficiais C1–C3.

**Entradas:**
- Fase 5 concluída (observabilidade pronta e mecanismo de leitura de métricas operante).

**Saídas:**
- fixtures/goldens consistentes para C1–C3 (inspirados em casos reais de mercado);  
- T4, T5, T6 PASS com evidências completas.

Arquivos‑chave:

- `tests/fixtures/s9_preco_medio/`  
- `tests/fixtures/s9_comparacao/`  
- `tests/fixtures/s9_checagem_factual/`  
- `tests/goldens/s9_preco_medio.json`  
- `tests/goldens/s9_comparacao_simples.json`  
- `tests/goldens/s9_checagem_factual.json`  
- `tests/s9_t4_golden_flows/`  
- `bin/s9_t4_golden_flows.sh`  
- `bin/s9_t5_perf_and_limits.sh`  
- `bin/s9_t6_logs_and_evidence.sh`  
- `docs/sprint_9_cenarios_demo.md`

Passos principais:

1) Fixtures consistentes e realistas
   - Construir fixtures de forma que cada cenário oficial use naturalmente ≥ 2 fontes;  
   - inspirar‑se em casos reais de mercado (ex.: preços médios em regiões/bairros plausíveis, comparações que reflitam situações comuns);  
   - documentar, em `docs/sprint_9_cenarios_demo.md`, a origem/inspiração de cada cenário e por que ele é relevante.

2) Goldens C1–C3
   - Executar Admin → ingestão → User para cada cenário C1–C3;  
   - capturar respostas e salvar em `tests/goldens/s9_*.json` com regras claras de normalização (ignorando IDs/timestamps).

3) Tests de golden flows (T4)
   - `tests/s9_t4_golden_flows/`: testes que:  
     - preparam fontes/fixtures via Admin;  
     - executam User v1;  
     - comparam respostas com goldens.
   - `bin/s9_t4_golden_flows.sh`: orquestra esses testes e gera summary/scorecard.

4) Performance & estabilidade (T5)
   - `bin/s9_t5_perf_and_limits.sh`:  
     - usa `scripts/s9_perf_runner.py` ou equivalente para rodar cargas controladas C1–C3;  
     - obtém p50/p95 e taxa de erro a partir do mecanismo definido na Fase 5 (endpoint `/metrics` ou client interno);  
     - avalia estabilidade de `summary_structured` entre runs;  
     - escreve summary/scorecard com metas numéricas do Cap. 2.

5) Logs & evidência (T6)
   - `bin/s9_t6_logs_and_evidence.sh`:  
     - reconstrói C1–C3 (Admin→User);  
     - percorre QueryLog → bundle → UserResponse em `s9_logs/`, `s9_bundles/`, `s9_responses/`;  
     - valida `meta.num_sources >= 2`, trilha completa, ausência de erros silenciosos;  
     - registra tudo em summary/scorecard.

6) Rodar T4–T6
   - `PYTHONPATH=. bin/s9_t4_golden_flows.sh`;  
   - `PYTHONPATH=. bin/s9_t5_perf_and_limits.sh`;  
   - `PYTHONPATH=. bin/s9_t6_logs_and_evidence.sh`.

**Pré‑condições explícitas para rodar T4–T6:**
- Fase 5 concluída (métricas e evidências S9 estão funcionando);  
- `docs/sprint_9_cenarios_demo.md` descreve claramente C1–C3 e seus dados/fixtures;  
- Admin v1 consegue preparar fontes/fixtures para C1–C3 sem intervenção manual extra.

**DoD da Fase 6:**
- Fixtures/goldens de C1–C3 existem e representam cenários realistas;  
- T4 PASS (goldens coerentes com a implementação);  
- T5 PASS (metas de latência/erro/estabilidade atendidas);  
- T6 PASS (Inv1–Inv4 provadas nos cenários oficiais).

---

### 10. Fase 7 — CI da S9, T7 e T8 (GO/NO‑GO)

**Objetivo:** garantir que T1–T6 rodem automaticamente em CI (T7) e consolidar GO/NO‑GO da S9 (T8).

**Invariantes foco da fase:**
- Inv1–Inv4: mantidas no tempo via CI;  
- decisão GO/NO_GO da S9 formalizada.

**Entradas:**
- T0–T6 PASS localmente;  
- fixtures/goldens em ordem.

**Saídas:**
- workflow S9‑CI rodando em PR/push;  
- T7 PASS;  
- T8 com decisão GO/NO_GO registrada;  
- resumo da S9 documentado.

Arquivos‑chave:

- `bin/s9_ci.sh`  
- `bin/s9_t7_ci_pipeline.sh`  
- `bin/s9_t8_go_no_go.sh`  
- `.github/workflows/s9-ci.yml`  
- `docs/sprint_9_summary.md`

Passos principais:

1) Orquestrador de CI da S9
   - `bin/s9_ci.sh` roda T1–T6 em ordem, falhando se qualquer gate falhar.

2) Gate T7
   - `bin/s9_t7_ci_pipeline.sh` chama `bin/s9_ci.sh`, registra gates e status em summary/scorecard.

3) Workflow `s9-ci.yml`
   - Configura Python + `.venv`;  
   - exporta `NET=0`;  
   - executa `bin/s9_ci.sh` em push/PR para branches alvo;  
   - é configurado como obrigatório para merges em `main`.

4) Resumo da Sprint 9
   - `docs/sprint_9_summary.md`:  
     - objetivo da S9;  
     - quadro gates T0–T8 com status;  
     - entregáveis principais (Admin v1, User v1, GPT Engine, Obs S9, goldens, CI);  
     - limitações e recomendações para S10–S12;  
     - referência explícita às evidências T4–T6.

5) Gate T8
   - `bin/s9_t8_go_no_go.sh`:  
     - lê scorecards S9_T0…S9_T7;  
     - aplica regras do Cap. 2 (qualquer FAIL → NO_GO);  
     - verifica presença/consistência de `docs/sprint_9_summary.md`;  
     - escreve summary/scorecard com `decision: GO|NO_GO`.

6) Rodar T7 e T8
   - `PYTHONPATH=. bin/s9_t7_ci_pipeline.sh`;  
   - `PYTHONPATH=. bin/s9_t8_go_no_go.sh`.

**Pré‑condições explícitas para T7/T8:**
- T1–T6 PASS localmente;  
- workflow `s9-ci.yml` existente e referenciando `bin/s9_ci.sh`;  
- `docs/sprint_9_summary.md` criado pelo menos em rascunho antes de rodar T8.

**DoD da Fase 7:**
- CI S9‑CI rodando em PR/push;  
- T7 em PASS;  
- T8 em PASS com decisão `GO` (ou `NO_GO` documentado com motivos claros);  
- resumo da S9 descreve estado final e próximos passos.

---

### 11. Fase 8 — Roteiro de demo e checklist final

**Objetivo:** preparar o roteiro de demo humano da S9, usando exatamente os caminhos que T4–T6 exercitam, e fechar um checklist final de produto interno v0.

**Invariantes foco da fase:**
- Inv1–Inv4: validadas na prática sob olhos humanos, não só pela pipeline.

**Entradas:**
- T0–T8 PASS;  
- S9 tecnicamente concluída.

**Saídas:**
- demo reproduzível da S9;  
- checklist final aderente ao Cap. 1;  
- `docs/sprint_9_summary.md` atualizado.

Passos principais:

1) Roteiro de demo C1–C3
   - Usar `docs/sprint_9_cenarios_demo.md` como script;  
   - para cada cenário:  
     - operador usa Admin v1 para verificar/preparar fontes;  
     - se necessário, roda ingestão apropriada;  
     - usuário interno usa User v1 para fazer a pergunta;  
     - examinam resposta, resumo estruturado, evidências, métricas (via UI ou painel existente).

2) Checklist final (Cap. 1)
   - Verificar, um a um, os objetivos da S9 e invariantes Inv1–Inv4;  
   - apontar, para cada item, o gate/evidência que prova o atendimento;  
   - listar dívidas técnicas/funcionais empurradas para S10–S12.

3) Atualizar `docs/sprint_9_summary.md`
   - Incluir roteiro de demo e checklist como seções finais ou anexos;  
   - registrar a decisão final de T8 e recomendações para as próximas sprints.

**DoD da Fase 8:**
- Demo C1–C3 foi executada ao vivo ao menos uma vez sem falhas;  
- checklist final marca explicitamente Inv1–Inv4 como atendidas, com links para evidências;  
- resumo da S9 está completo e alinhado com Cap. 1–3–4.

Quando esta fase estiver concluída, a Sprint 9 está pronta para ser usada como produto interno v0 do Inspectah, e o Cap. 4 terá cumprido seu papel: ser o roteiro de execução que encaixa perfeitamente nos gates do Cap. 2, ancorado na arquitetura do Cap. 3 e nas invariantes do Cap. 1.

