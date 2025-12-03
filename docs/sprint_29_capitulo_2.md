# Sprint 29 — Capítulo 2
# Gates, Métricas, Scorecards e Critérios de GO/NO-GO

## 1. Papel do Capítulo 2 na Sprint 29

O Capítulo 2 da Sprint 29 traduz o contexto e o problema (Capítulo 1) em **regras concretas de validação**:

- quais são os **gates** formais da sprint;
- que **checks objetivos** cada gate precisa executar;
- quais **métricas e evidências** precisam ser produzidas;
- quais **scorecards JSON** registram o resultado;
- como decidimos **GO/NO-GO** para a S29 como um todo.

A ideia é que qualquer pessoa consiga olhar para os gates da S29 e responder:

> "O que precisa estar verde para declararmos que o fluxo de agentes configurável v1 é real, seguro e operável?"

---

## 2. Visão geral dos gates da S29

A Sprint 29 terá, no mínimo, os seguintes gates formais:

- **S29_G0 — Scope & Baseline**  
  Verifica se o escopo, docs e filemap básicos da sprint existem e estão coerentes.

- **S29_G1 — Modelos, Schemas e Migrations (AgentFlowConfig)**  
  Garante que o modelo de fluxo de agentes está estável, migrado e coberto por testes mínimos.

- **S29_G2 — API de Admin & Validador de Fluxo**  
  Valida contratos da API `/admin/agent-flows` e invariantes de fluxo.

- **S29_G3 — UI & Frontend Quality (Agent Flows UI)**  
  Verifica a qualidade da UI de fluxo (lint, testes, build) e interações básicas.

- **S29_G4 — Runtime & Observabilidade de Fluxos**  
  Garante que ao menos um pipeline real usa o fluxo configurado e que logs/métricas mínimas existem.

- **S29_G5 — ORR & Bundle de Evidências da Sprint 29**  
  Valida a existência do bundle único de evidências e do resumo ORR da sprint.

Cada gate é implementado por um script `bin/s29_gX_*.sh`, gera evidência em `out/evidence/S29_GX_*` e um scorecard JSON em `out/scorecards/S29_GX_*.json`.

A S29 só pode ser considerada **GO** se **todos os gates obrigatórios (G0–G5)** estiverem verdes.

---

## 3. Gate S29_G0 — Scope & Baseline

**Objetivo**  
Garantir que a Sprint 29 tem uma base documental mínima e um filemap coerente antes de rodar qualquer gate técnico.

**Script sugerido**  
`bin/s29_g0_scope_and_baseline.sh`

**Checks principais**

1. **Presença dos documentos-chave da sprint**:
   - `docs/sprint_29_macro.md` (visão macro da S29);
   - `docs/sprint_29_capitulo_1.md` (ou blocos equivalentes reunidos);
   - `docs/sprint_29_capitulo_2.md` (este capítulo);
   - estrutura base para Capítulos 3 e 4 (`docs/sprint_29_capitulo_3*.md`, `docs/sprint_29_capitulo_4*.md`).

2. **Filemap mínimo de código para S29**:
   - diretório backend para fluxos de agentes, por exemplo: `app/agents/flows/` contendo pelo menos:
     - `models.py`;
     - `schemas.py`;
     - `validator.py`;
     - `runtime_adapter.py`;
   - diretório de rotas de admin para fluxos, ex.: `app/api/admin_agent_flows_routes.py`;
   - diretório frontend para UI de fluxos, ex.: `frontend/inspectah-ui/src/features/agent-flows/`.

3. **Presença de arquivos de configuração e caminhos de evidência**:
   - diretório `out/evidence/S29_G0_scope_and_baseline` criado (mesmo que vazio inicialmente);
   - diretório `out/scorecards/` existente (compartilhado com outras sprints) e acessível.

**Métricas / Saídas esperadas**

- Lista de arquivos/documents encontrados e verificados.
- Verificação de que nenhum caminho crítico da sprint está faltando.

**Scorecard**

- Arquivo: `out/scorecards/S29_G0_scope_and_baseline.json`
- Campos mínimos sugeridos:
  - `gate_id`: "S29_G0";
  - `status`: `PASS` | `FAIL`;
  - `missing_docs`: lista de docs ausentes;
  - `missing_paths`: lista de pastas/arquivos obrigatórios ausentes;
  - `timestamp`;
  - `notes`.

**Critério de aprovação (PASS)**

- Todos os documentos e caminhos obrigatórios existem;
- Não há entradas em `missing_docs` e `missing_paths`;
- `status == "PASS"`.

---

## 4. Gate S29_G1 — Modelos, Schemas e Migrations

**Objetivo**  
Garantir que o modelo de configuração de fluxo (`AgentFlowConfig`, `AgentFlowStep`) está:

- corretamente modelado;
- refletido em migrations;
- coberto por testes mínimos;
- coerente com as definições do Capítulo 1.

**Script sugerido**  
`bin/s29_g1_model_and_migrations.sh`

**Checks principais**

1. **Modelos definidos** em `app/agents/flows/models.py`:
   - `AgentFlowConfig` com campos: `id`, `domain_key`, metadados de auditoria (`created_at`, `created_by`, `updated_at`, `updated_by`, `change_reason`);
   - `AgentFlowStep` com campos: `id`, referência à config, `position`, `agent_role`, `params` (JSON ou similar).

2. **Schemas Pydantic** em `app/agents/flows/schemas.py` para:
   - entrada (`AgentFlowConfigIn`, `AgentFlowStepIn`);
   - saída (`AgentFlowConfigOut`, com passos embutidos).

3. **Migrations criadas e aplicáveis**:
   - arquivo `migrations/versions/00xx_s29_agent_flows.py` (nome pode variar, mas tag clara de S29);
   - comando `alembic upgrade head` (ou equivalente) executa sem erro.

4. **Testes de modelo**:
   - testes em `tests/agents/test_agent_flow_models.py` cobrindo:
     - criação básica de `AgentFlowConfig` + `AgentFlowStep`;
     - unicidade de `position` por `AgentFlowConfig`;
     - integridade de foreign key entre `AgentFlowConfig` e `AgentFlowStep`.

**Métricas / Saídas esperadas**

- Status da execução das migrations (PASS/FAIL);
- Número de testes executados para modelos de fluxo;
- Número de falhas (idealmente 0);
- Confirmação de que o schema gerado bate com o esperado (ex.: snapshot de DDL em evidência).

**Scorecard**

- Arquivo: `out/scorecards/S29_G1_model_and_migrations.json`
- Campos mínimos sugeridos:
  - `gate_id`: "S29_G1";
  - `status`: `PASS` | `FAIL`;
  - `tests_run`: número de testes;
  - `tests_failed`: número de falhas;
  - `migrations_applied`: `true` | `false`;
  - `ddl_snapshot_path`: caminho para arquivo com DDL capturado (opcional, como evidência extra);
  - `timestamp`;
  - `notes`.

**Critério de aprovação (PASS)**

- Tests de modelos e migrations executam sem falhas;
- Migrations aplicam em um banco limpo e em um banco já migrado até S28;
- Não há inconsistências gritantes entre modelos e schema real.

---

## 5. Gate S29_G2 — API de Admin & Validador de Fluxo

**Objetivo**  
Validar a camada de API que expõe e manipula fluxos de agentes, bem como o validador de invariantes.

**Script sugerido**  
`bin/s29_g2_api_and_validator.sh`

**Checks principais**

1. **Rotas FastAPI para admin de fluxos** em `app/api/admin_agent_flows_routes.py`:
   - `GET /admin/agent-flows` (lista fluxos por domínio);
   - `GET /admin/agent-flows/{flow_id}` (detalhe);
   - `GET /admin/agent-flows/by-domain/{domain_key}` (fluxo ativo de um domínio);
   - `POST /admin/agent-flows` (criação);
   - `PUT /admin/agent-flows/{flow_id}` (atualização).

2. **Validador de invariantes** em `app/agents/flows/validator.py`:
   - regra de fluxo não vazio;
   - regra de primeiro passo com papel permitido;
   - regras mínimas de papéis obrigatórios por domínio (quando configurado);
   - proibição de `DECISION_MAKER` em posições intermediárias;
   - checagem de posições duplicadas ou inválidas.

3. **Testes automatizados** em `tests/agents/test_agent_flow_validator.py` e `tests/agents/test_agent_flow_api.py` cobrindo:
   - criação de fluxo válido → `201`/`200` com payload coerente;
   - criação/atualização de fluxo inválido → código de erro adequado (`400`/`422`) com mensagem explicativa;
   - leitura de fluxo por domínio existente/inexistente;
   - caso de domínio sem fluxo explícito, retornando sinalização clara (ex.: `404` ou payload específico) e/ou fallback.

**Métricas / Saídas esperadas**

- Número de testes de API e validação executados;
- Número de falhas;
- Lista de invariantes cobertas pelos testes (para rastreabilidade);
- Amostras de respostas JSON de sucesso e erro (em evidência).

**Scorecard**

- Arquivo: `out/scorecards/S29_G2_api_and_validator.json`
- Campos mínimos sugeridos:
  - `gate_id`: "S29_G2";
  - `status`: `PASS` | `FAIL`;
  - `tests_run`: número de testes;
  - `tests_failed`: número de falhas;
  - `invariants_covered`: lista de IDs/nomes de invariantes testadas;
  - `example_success_response_path`;
  - `example_error_response_path`;
  - `timestamp`;
  - `notes`.

**Critério de aprovação (PASS)**

- 0 testes falhando;
- Todas as invariantes mínimas listadas no Capítulo 1 aparecem em `invariants_covered`;
- APIs retornam códigos e mensagens consistentes, sem brechas óbvias.

---

## 6. Gate S29_G3 — UI & Frontend Quality (Agent Flows UI)

**Objetivo**  
Assegurar que a interface de configuração de fluxo de agentes:

- existe;
- funciona para o domínio piloto;
- respeita padrões básicos de qualidade de frontend (lint, testes, build).

**Script sugerido**  
`bin/s29_g3_ui_and_frontend_quality.sh`

**Checks principais**

1. **Presença da feature de UI** em `frontend/inspectah-ui/src/features/agent-flows/`:
   - `AgentFlowsPage.tsx` (listagem por domínio);
   - `AgentFlowEditor.tsx` (editor linear de fluxo);
   - `agentFlowsApi.ts` (cliente da API);
   - tipos em `agentFlowsTypes.ts`.

2. **Qualidade básica de frontend**:
   - `npm run lint` e `npm test` passam sem erros;
   - `npm run build` finaliza com sucesso.

3. **Testes de UI específicos da feature**:
   - testes em `__tests__/AgentFlowEditor.test.tsx` cobrindo:
     - renderização do fluxo para um domínio piloto;
     - adição de um passo ao fluxo;
     - reordenação de passos;
     - tratamento de erro de validação (exibição de mensagem de invariantes violadas).

4. **Evidência de fluxo real configurado via UI**:
   - script ou instrução que demonstre, em dev, a configuração do fluxo de um domínio piloto pela UI;
   - captura (screenshot ou descrição estruturada) incluída em evidência.

**Métricas / Saídas esperadas**

- Status do lint/test/build;
- Número de testes específicos de UI para fluxos de agentes;
- Evidência de interação real (fluxo sendo criado/ajustado para domínio piloto).

**Scorecard**

- Arquivo: `out/scorecards/S29_G3_ui_and_frontend_quality.json`
- Campos mínimos sugeridos:
  - `gate_id`: "S29_G3";
  - `status`: `PASS` | `FAIL`;
  - `lint_status`: `PASS` | `FAIL`;
  - `test_status`: `PASS` | `FAIL`;
  - `build_status`: `PASS` | `FAIL`;
  - `ui_tests_run` / `ui_tests_failed`;
  - `pilot_domain`: chave do domínio usado como exemplo;
  - `screenshot_path` ou `ui_demo_notes_path`;
  - `timestamp`;
  - `notes`.

**Critério de aprovação (PASS)**

- Lint, testes e build do frontend passam;
- Existe evidência clara de um fluxo de domínio real sendo configurado via UI;
- Nenhum teste da feature de fluxos falha.

---

## 7. Gate S29_G4 — Runtime & Observabilidade de Fluxos

**Objetivo**  
Garantir que o runtime do Inspectah realmente consome o fluxo configurado para, pelo menos, um domínio piloto, e que há observabilidade mínima sobre isso.

**Script sugerido**  
`bin/s29_g4_runtime_and_observability.sh`

**Checks principais**

1. **Adapter de runtime** em `app/agents/flows/runtime_adapter.py`:
   - função pública `get_agent_flow_for_domain(domain_key: str)`;
   - tratamento de caso com fluxo configurado;
   - tratamento de caso sem fluxo configurado (fallback controlado + log/flag).

2. **Integração com pipeline de ingestão/agentes**:
   - pelo menos um pipeline real (ex.: notícias de política) chama `get_agent_flow_for_domain` para obter a sequência de papéis;
   - existe um teste ou script de demonstração que processa um item de domínio piloto e mostra o fluxo sendo respeitado.

3. **Logs estruturados** de execução de fluxo:
   - logs em logger dedicado (ex.: `agent_flows_runtime`) registrando:
     - domínio;
     - identificador do item;
     - sequência de papéis executados;
     - uso de fallback, quando ocorrer.

4. **Métricas mínimas**:
   - contador de usos de fallback (ex.: `agent_flow_fallback_total` ou equivalente);
   - contador de fluxos ativos por domínio (mesmo que apenas em logs estruturados).

**Métricas / Saídas esperadas**

- Execução bem-sucedida de um cenário end‑to‑end para domínio piloto;
- Logs coletados em `out/evidence/S29_G4_runtime_and_observability`;
- Estatísticas mínimas sobre uso de fallback.

**Scorecard**

- Arquivo: `out/scorecards/S29_G4_runtime_and_observability.json`
- Campos mínimos sugeridos:
  - `gate_id`: "S29_G4";
  - `status`: `PASS` | `FAIL`;
  - `pilot_domain`: chave do domínio usado no teste end‑to‑end;
  - `runtime_smoke_test_status`: `PASS` | `FAIL`;
  - `fallback_used`: `true` | `false` (no teste principal) e, se sim, por quê;
  - `logs_sample_path`: caminho para arquivo com amostra de logs estruturados;
  - `metrics_sample_path`: caminho para amostra de métricas (se houver);
  - `timestamp`;
  - `notes`.

**Critério de aprovação (PASS)**

- Cenário end‑to‑end do domínio piloto executa sem erro;
- Logs mostram a sequência de papéis de fluxo sendo respeitada;
- Fallback, se usado em algum cenário, é explícito e explicado.

---

## 8. Gate S29_G5 — ORR & Bundle de Evidências da S29

**Objetivo**  
Consolidar a sprint em um pacote auditável e garantir que o conselho consiga revisar S29 de forma objetiva.

**Script sugerido**  
`bin/s29_g5_orr_and_bundle.sh`

**Checks principais**

1. **Bundle de evidências** da sprint:
   - arquivo `out/bundles/inspectah_s29_evidence_bundle.zip` contendo:
     - subpastas `S29_G0_*` até `S29_G4_*` de `out/evidence/`;
     - todos os scorecards `S29_G*_*.json` de `out/scorecards/`;
     - amostras de logs/métricas relevantes.

2. **Documento ORR** da S29:
   - `docs/sprint_29_orr_summary.md` com, no mínimo:
     - resumo do objetivo da sprint;
     - status de cada gate (G0–G5);
     - links/caminhos para scorecards e evidências;
     - avaliação qualitativa (forças, riscos residuais, recomendações).

3. **Integridade dos scorecards**:
   - todos os arquivos `S29_G*_*.json` existem;
   - todos possuem `status` definido (PASS/FAIL) e timestamp.

**Métricas / Saídas esperadas**

- Bundle `.zip` gerado com tamanho e conteúdo esperados;
- ORR S29 completo e referenciando corretamente os caminhos;
- Resumo legível para o conselho decidir GO/NO-GO.

**Scorecard**

- Arquivo: `out/scorecards/S29_G5_orr_and_bundle.json`
- Campos mínimos sugeridos:
  - `gate_id`: "S29_G5";
  - `status`: `PASS` | `FAIL`;
  - `bundle_path`: caminho para o arquivo `.zip`;
  - `orr_doc_path`: caminho para `sprint_29_orr_summary.md`;
  - `scorecards_found`: lista de IDs de gates com scorecards válidos;
  - `timestamp`;
  - `notes`.

**Critério de aprovação (PASS)**

- Bundle gerado com todos os diretórios de evidência e scorecards;
- Documento ORR completo e coerente com o que foi de fato executado;
- Nenhum gate obrigatório da S29 sem scorecard correspondente.

---

## 9. Critérios de GO/NO-GO da Sprint 29

A decisão final sobre a Sprint 29 deve considerar tanto o resultado dos gates quanto a avaliação qualitativa do conselho.

**Requisitos mínimos para GO:**

1. **Todos os gates G0–G5 com `status == PASS`**.
2. **Fluxo de agentes configurável v1 operando em pelo menos um domínio piloto**, com:
   - configuração em banco via `AgentFlowConfig`;
   - edição possível via UI;
   - uso efetivo no runtime;
   - invariantes mínimas ativadas.
3. **Rastro mínimo de auditoria** para alterações de fluxo no domínio piloto.
4. **Conselho técnico** avaliando, no documento ORR, que:
   - o modelo de fluxo é sólido o suficiente para suportar E28.2/E28.3;
   - não há riscos estruturais óbvios que inviabilizem evoluções futuras;
   - o resultado atende aos objetivos de produto descritos no Capítulo 1.

**Motivos típicos para NO-GO (mesmo com gates verdes):**

- Modelo de fluxo considerado frágil ou mal dimensionado pelo conselho;
- Integração com runtime ainda muito "de laboratório", sem confiança para expansão;
- Invariantes de fluxo consideradas insuficientes para domínios sensíveis.

Nesses casos, o ORR deve registrar claramente:

- quais ajustes são exigidos para um GO condicional;
- qual o plano para tratar esses ajustes (hotfix pós-sprint, mini-sprint adicional, etc.).

---

## 10. Amarração do Capítulo 2

O Capítulo 2 da Sprint 29 fixa o "contrato de teste" da sprint:

- define **o que precisa ser medido** (modelo, API, UI, runtime, bundle);
- define **como será medido** (scripts, caminhos de evidência, scorecards JSON);
- define **quando consideramos que a sprint realmente entregou o que prometeu**.

Com isso, os próximos capítulos (Arquitetura & Filemap, Execução & Evidências) podem ser escritos já sabendo **quais gates precisam ser alimentados**. A Sprint 29 deixa de ser uma lista solta de tarefas e passa a ser um conjunto de compromissos verificáveis:

> "Só existe E28 v1 de verdade se todos esses gates estiverem verdes e se, na prática, pelo menos um domínio real estiver operando com fluxo de agentes configurável, visível e auditável."

