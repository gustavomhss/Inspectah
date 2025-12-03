# Sprint 29 — Capítulo 4
# Execução, Evidências e DoD

## 1. Objetivo do Capítulo 4

O Capítulo 4 transforma o contexto (Cap. 1), os gates (Cap. 2) e a arquitetura/filemap (Cap. 3) de S29 em um **plano de execução concreto**, com:

- waves de implementação;
- sequência de tarefas técnicas;
- comandos padrão para backend, frontend e gates;
- estratégia de evidências e scorecards;
- critérios objetivos de Definition of Done (DoD) para a sprint.

A ideia é que qualquer pessoa da equipe consiga pegar este capítulo, abrir uma branch e conduzir a Sprint 29 **do zero até o GO final** sem precisar adivinhar passos.

---

## 2. Estratégia de execução por waves

A execução de S29 é organizada em cinco waves principais, cada uma com foco claro e entregáveis associados aos gates:

1. **Wave 0 — Preparação & Baseline**  
   - Configurar branch, docs e estrutura mínima (G0).  
   - Garantir que o repositório está em estado saudável para iniciar a sprint.

2. **Wave 1 — Domínio de fluxo de agentes (Modelos, Schemas, Migrations)**  
   - Implementar `app/agents/flows/` (models, schemas, validator esqueleto, service).  
   - Criar migrations.  
   - Garantir G1 verde.

3. **Wave 2 — API de admin & Validador de fluxo**  
   - Implementar rotas em `app/api/admin_agent_flows_routes.py`.  
   - Finalizar validador de invariantes.  
   - Cobrir com testes de domínio + API.  
   - Garantir G2 verde.

4. **Wave 3 — UI de fluxo de agentes (Frontend)**  
   - Implementar `src/features/agent-flows/` (página, editor, cliente de API, tipos, testes).  
   - Ajustar rotas e layout admin.  
   - Garantir G3 verde.

5. **Wave 4 — Runtime & Observabilidade + ORR & Bundle**  
   - Integrar adapter com pipeline de ingestão.  
   - Instrumentar logs mínimos.  
   - Fechar G4 (runtime) e G5 (ORR + evidências), preparando o GO.

As waves podem ter alguma sobreposição, mas o fluxo ideal evita avançar para UI antes de G1+G2 estarem minimamente estabilizados.

---

## 3. Wave 0 — Preparação & Baseline (G0)

### 3.1. Branch, ambiente e sanity inicial

1. Criar e trocar para a branch da sprint (nome sugerido):

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
source .venv/bin/activate

git checkout main
git pull --ff-only

git checkout -b feature/programa1_s29_agent_flows_v1
```

2. Sanity check rápido (backend + frontend):

```bash
# Backend — testes principais (ajustar escopo se necessário)
PYTHONPATH=. pytest

# Frontend — sanity padrão
cd frontend/inspectah-ui
npm ci --prefer-offline
npm run lint
npm test
npm run build
cd ../..
```

Qualquer falha aqui deve ser resolvida antes de seguir, para não misturar débito antigo com S29.

### 3.2. Documentos da sprint

Garantir criação (ou atualização) dos documentos:

- `docs/sprint_29_macro.md`;
- `docs/sprint_29_capitulo_1.md`;
- `docs/sprint_29_capitulo_2.md`;
- `docs/sprint_29_capitulo_3.md` (este filemap/arquitetura);
- `docs/sprint_29_capitulo_4.md` (este capítulo).

### 3.3. Estrutura base de código e evidências

Criar/confirmar estrutura mínima:

```bash
# Backend
mkdir -p app/agents/flows
.touch app/agents/flows/__init__.py
.touch app/agents/flows/models.py
.touch app/agents/flows/schemas.py
.touch app/agents/flows/validator.py
.touch app/agents/flows/service.py
.touch app/agents/flows/runtime_adapter.py

# Frontend
mkdir -p frontend/inspectah-ui/src/features/agent-flows
.touch frontend/inspectah-ui/src/features/agent-flows/AgentFlowsPage.tsx
.touch frontend/inspectah-ui/src/features/agent-flows/AgentFlowEditor.tsx
.touch frontend/inspectah-ui/src/features/agent-flows/agentFlowsApi.ts
.touch frontend/inspectah-ui/src/features/agent-flows/agentFlowsTypes.ts

# Evidências e scorecards
mkdir -p out/evidence/S29_G0_scope_and_baseline
mkdir -p out/evidence/S29_G1_model_and_migrations
mkdir -p out/evidence/S29_G2_api_and_validator
mkdir -p out/evidence/S29_G3_ui_and_frontend_quality
mkdir -p out/evidence/S29_G4_runtime_and_observability
mkdir -p out/evidence/S29_G5_orr_and_bundle

mkdir -p out/scorecards
mkdir -p out/bundles
```

### 3.4. Executar gate G0

Implementar e rodar o script:

```bash
bin/s29_g0_scope_and_baseline.sh
```

Saídas esperadas:

- `out/evidence/S29_G0_scope_and_baseline/docs_check.txt`;
- `out/evidence/S29_G0_scope_and_baseline/filemap_check.txt`;
- `out/scorecards/S29_G0_scope_and_baseline.json` com `"status": "PASS"`.

Se `status` for `FAIL`, ajustar docs/filemap até o G0 ficar verde.

---

## 4. Wave 1 — Domínio de fluxo de agentes (G1)

### 4.1. Implementação de modelos e schemas

1. Implementar `AgentFlowConfig` e `AgentFlowStep` em `app/agents/flows/models.py`, conforme Cap. 3 Bloco 2.

2. Implementar schemas Pydantic em `app/agents/flows/schemas.py`:

- `AgentFlowStepIn`, `AgentFlowConfigIn`;
- `AgentFlowStepOut`, `AgentFlowConfigOut`.

### 4.2. Migrations

Criar migration para as tabelas de fluxo, seguindo padrão do projeto (Alembic, por exemplo):

```bash
alembic revision -m "S29: agent flows" --autogenerate
# Confirma o conteúdo gerado em migrations/versions/00xx_s29_agent_flows.py
alembic upgrade head
```

Registrar logs:

- `out/evidence/S29_G1_model_and_migrations/migrations.log`;
- opcionalmente, `ddl_snapshot.sql` com DDL das tabelas.

### 4.3. Testes de modelos/schemas

Criar testes em `tests/agents/test_agent_flow_models.py` e, se útil, em `tests/agents/test_agent_flow_schemas.py`, cobrindo:

- criação básica de fluxo com múltiplos steps;
- integridade de relacionamento `AgentFlowConfig` ↔ `AgentFlowStep`;
- unicidade de `(flow_id, position)`;
- serialização via `AgentFlowConfigOut`.

Rodar testes filtrados ou gerais:

```bash
PYTHONPATH=. pytest tests/agents/test_agent_flow_models.py
```

### 4.4. Executar gate G1

Implementar e rodar:

```bash
bin/s29_g1_model_and_migrations.sh
```

Saídas esperadas:

- `out/evidence/S29_G1_model_and_migrations/tests.log`;
- `out/evidence/S29_G1_model_and_migrations/migrations.log`;
- `out/evidence/S29_G1_model_and_migrations/ddl_snapshot.sql` (opcional);
- `out/scorecards/S29_G1_model_and_migrations.json` com `"status": "PASS"`.

Qualquer falha deve ser tratada antes de avançar para Wave 2.

---

## 5. Wave 2 — API de admin & Validador (G2)

### 5.1. Implementar validador de invariantes

Completar `app/agents/flows/validator.py` com:

- tipo `AgentFlowValidationError` (código + mensagem);
- função `validate_agent_flow(domain_key: str, steps: list[AgentFlowStepIn])` implementando invariantes:
  - fluxo não vazio;
  - primeiro papel permitido (conjunto de entrada válido);
  - papéis obrigatórios para domínios sensíveis (ex.: `DEBUNKER` antes de `DECISION_MAKER`);
  - `DECISION_MAKER` apenas na última posição;
  - ausência de posições duplicadas;
  - papéis conhecidos e alinhados ao catálogo.

### 5.2. Integrar validador ao serviço

Em `app/agents/flows/service.py`:

- chamar `validate_agent_flow` em `create_agent_flow` e `update_agent_flow` antes de persistir;
- propagar `AgentFlowValidationError` sem engolir;
- garantir preenchimento adequado de campos de auditoria.

### 5.3. Implementar rotas de admin

Em `app/api/admin_agent_flows_routes.py`:

- `GET /admin/agent-flows`;
- `GET /admin/agent-flows/{flow_id}`;
- `GET /admin/agent-flows/by-domain/{domain_key}`;
- `POST /admin/agent-flows`;
- `PUT /admin/agent-flows/{flow_id}`.

Integração com auth:

- uso de dependências padrão (`get_current_admin_user`).

Tratamento de erro:

- converter `AgentFlowValidationError` em `HTTPException(422, detail={code, message})`;
- tratar erros de domínio como fluxo duplicado (`FLOW_ALREADY_EXISTS`) com `400/409`.

### 5.4. Testes de validador e API

Em `tests/agents/test_agent_flow_validator.py`:

- casos de fluxo válido;
- fluxo vazio;
- primeiro papel inválido;
- domínio sensível sem `DEBUNKER`;
- `DECISION_MAKER` no meio;
- posições duplicadas;
- papel desconhecido.

Em `tests/agents/test_agent_flow_api.py`:

- criação de fluxo válido (`POST`);
- atualização válida (`PUT`);
- erros de validação (422 com códigos distintos);
- domínio sem fluxo (404 controlado);
- fluxo duplicado (400/409 com código `FLOW_ALREADY_EXISTS`).

Executar testes:

```bash
PYTHONPATH=. pytest tests/agents/test_agent_flow_validator.py
PYTHONPATH=. pytest tests/agents/test_agent_flow_api.py
```

### 5.5. Executar gate G2

Rodar:

```bash
bin/s29_g2_api_and_validator.sh
```

Saídas esperadas:

- `out/evidence/S29_G2_api_and_validator/validator_tests.log`;
- `out/evidence/S29_G2_api_and_validator/api_tests.log`;
- `out/evidence/S29_G2_api_and_validator/example_success_response.json`;
- `out/evidence/S29_G2_api_and_validator/example_error_response.json`;
- `out/scorecards/S29_G2_api_and_validator.json` com `"status": "PASS"`.

---

## 6. Wave 3 — UI de fluxo de agentes (G3)

### 6.1. Implementar tipos, cliente de API e hooks

Em `frontend/inspectah-ui/src/features/agent-flows/agentFlowsTypes.ts`:

- definir tipos alinhados aos schemas Pydantic (`AgentFlowStep`, `AgentFlowConfig`, `AgentFlowConfigForm`).

Em `agentFlowsApi.ts`:

- `listAgentFlows`;
- `getAgentFlowByDomain`;
- `createAgentFlow`;
- `updateAgentFlow`;
- normalizar erros da API em objetos com `code` e `message`.

Opcionalmente, em `agentFlowsHooks.ts`:

- `useAgentFlow(domainKey)`;
- `useSaveAgentFlow(domainKey)`.

### 6.2. Implementar página e editor

Em `AgentFlowsPage.tsx`:

- integrar com router admin (`/admin/agent-flows`);
- listar domínios com status de fluxo;
- permitir selecionar um domínio e abrir editor.

Em `AgentFlowEditor.tsx`:

- carregar fluxo existente ou preparar estado inicial;
- renderizar lista de passos com capacidade de adicionar, remover, reordenar e editar papéis/params;
- exigir `changeReason` ao salvar;
- tratar erros de validação (exibindo mensagens claras e destacando linhas problemáticas quando possível).

### 6.3. Ajustes de roteamento e design system

- adicionar entrada no menu admin para "Fluxos de agentes";
- garantir uso de componentes do design system (botões, inputs, alertas);
- manter responsividade básica (não quebrar em resoluções menores).

### 6.4. Testes de front

Em `frontend/inspectah-ui/src/features/agent-flows/__tests__/AgentFlowEditor.test.tsx`:

- carregar fluxo existente e renderizar passos na ordem correta;
- criar novo fluxo e verificar chamada correta de `createAgentFlow`;
- simular erro `DECISION_MAKER_NOT_LAST` e verificar mensagem exibida;
- bloquear save sem `changeReason` e destacar o campo.

Rodar pipeline de qualidade do frontend:

```bash
cd frontend/inspectah-ui
npm run lint
npm test
npm run build
cd ../..
```

### 6.5. Executar gate G3

Rodar:

```bash
bin/s29_g3_ui_and_frontend_quality.sh
```

Saídas esperadas:

- `out/evidence/S29_G3_ui_and_frontend_quality/lint.log`;
- `out/evidence/S29_G3_ui_and_frontend_quality/test.log`;
- `out/evidence/S29_G3_ui_and_frontend_quality/build.log`;
- capturas ou descrições mínimas da UI em ação (opcional, mas recomendado);
- `out/scorecards/S29_G3_ui_and_frontend_quality.json` com `"status": "PASS"`.

---

## 7. Wave 4 — Runtime, Observabilidade e ORR (G4, G5)

### 7.1. Integração de runtime

Em `app/agents/flows/runtime_adapter.py`:

- implementar `get_agent_flow_for_domain(domain_key)` retornando `AgentFlowRuntimePlan`;
- tratar casos com config encontrada e sem config (fallback padrão).

No pipeline de ingestão/agentes (por exemplo, `app/ingestion/pipeline.py`):

- obter `domain_key` do item;
- chamar `get_agent_flow_for_domain(domain_key)`;
- executar agentes na ordem definida em `steps` do plano;
- manter compatibilidade com modelo anterior na fase de transição.

### 7.2. Logs e métricas

Adicionar logs estruturados:

- logger `agent_flows_runtime` registrando:
  - `domain_key`;
  - `item_id` ou identificador equivalente;
  - `flow_id` (quando houver);
  - lista de papéis executados;
  - flag de fallback.

Futuras integrações com métricas podem contar eventos como "uso de fallback" e "fluxos executados por domínio".

### 7.3. Testes de runtime

Criar testes opcionais em `tests/agents/test_agent_flow_runtime_adapter.py` cobrindo:

- domínio com fluxo configurado → plano correto;
- domínio sem fluxo → plano de fallback com flag apropriada;
- logs emitidos em nível esperado.

### 7.4. Executar gate G4

Rodar:

```bash
bin/s29_g4_runtime_and_observability.sh
```

Saídas esperadas:

- `out/evidence/S29_G4_runtime_and_observability/runtime_tests.log`;
- `out/evidence/S29_G4_runtime_and_observability/runtime_logs_sample.txt`;
- `out/scorecards/S29_G4_runtime_and_observability.json` com `"status": "PASS"`.

### 7.5. ORR e bundle de evidências (G5)

Preparar `docs/sprint_29_orr_summary.md` com:

- resumo do escopo entregue;
- estado de cada gate (G0–G4);
- decisões relevantes;
- riscos remanescentes e recomendações.

Implementar e rodar:

```bash
bin/s29_g5_orr_and_bundle.sh
```

Responsabilidades do script:

- verificar que todos os scorecards G0–G4 existem e estão em `"PASS"`;
- agregar evidências relevantes em `out/bundles/inspectah_s29_evidence_bundle.zip`;
- gerar scorecard final `out/scorecards/S29_G5_orr_and_bundle.json` com `"status": "PASS"`.

---

## 8. Integração com CI/GitHub Actions

Opcionalmente, alinhar S29 com um workflow dedicado, por exemplo:

- `.github/workflows/s29-gates.yml`

Esse workflow pode:

- ser disparado em PRs da branch `feature/programa1_s29_agent_flows_v1`;
- rodar, no mínimo:
  - `bin/s29_g0_scope_and_baseline.sh`;
  - `bin/s29_g1_model_and_migrations.sh`;
  - `bin/s29_g2_api_and_validator.sh`;
  - `bin/s29_g3_ui_and_frontend_quality.sh`;
  - `bin/s29_g4_runtime_and_observability.sh`;
  - `bin/s29_g5_orr_and_bundle.sh` (ou só no merge, dependendo da estratégia).

Critério: PR não deve ser mergeado se qualquer gate da S29 estiver em `FAIL`.

---

## 9. Definition of Done (DoD) da Sprint 29

A Sprint 29 é considerada **DONE** quando todos os itens a seguir forem verdadeiros:

1. **Domínio & dados**  
   - Tabelas de fluxo (`AgentFlowConfig`, `AgentFlowStep`) existem, com migrations aplicadas e testadas em banco limpo e banco migrado.  
   - Schemas Pydantic de entrada/saída implementados e usados pela API.

2. **Validador & API**  
   - `validate_agent_flow` implementa todas as invariantes definidas no Cap. 1/2.  
   - API de admin (`/admin/agent-flows`) exposta com endpoints GET/POST/PUT funcionando e cobertos por testes.  
   - Erros de invariantes retornam `422` com `code` + `message` claros.

3. **UI de fluxo de agentes**  
   - Página e editor implementados em `src/features/agent-flows/`.  
   - Operador consegue visualizar e editar fluxo de um domínio piloto.  
   - `changeReason` é exigido para salvar alterações.  
   - UI trata erros de validação exibindo mensagens compreensíveis.

4. **Runtime & observabilidade**  
   - Pipeline de ingestão consome `get_agent_flow_for_domain(domain_key)` para pelo menos um domínio piloto.  
   - Fluxo configurado é respeitado em ambiente de teste/local.  
   - Logs estruturados registram execuções de fluxo e uso de fallback.

5. **Gates e evidências**  
   - `bin/s29_g0_scope_and_baseline.sh` retorna sucesso e scorecard `PASS`.  
   - `bin/s29_g1_model_and_migrations.sh` retorna sucesso e scorecard `PASS`.  
   - `bin/s29_g2_api_and_validator.sh` retorna sucesso e scorecard `PASS`.  
   - `bin/s29_g3_ui_and_frontend_quality.sh` retorna sucesso e scorecard `PASS`.  
   - `bin/s29_g4_runtime_and_observability.sh` retorna sucesso e scorecard `PASS`.  
   - `bin/s29_g5_orr_and_bundle.sh` retorna sucesso e scorecard `PASS`.  
   - `out/bundles/inspectah_s29_evidence_bundle.zip` existe e contém evidências mínimas para revisão.

6. **Código & qualidade**  
   - Testes relevantes (backend + frontend) passam localmente e no CI.  
   - Linters e build do frontend passam.  
   - Não há TODOs ou marcadores temporários em código central da S29.

7. **Git & PR**  
   - Branch `feature/programa1_s29_agent_flows_v1` está atualizada com `main`.  
   - PR final da Sprint 29 aprovado pela revisão técnica.  
   - Merge realizado com mensagem clara (ex.: `feat: S29 agent flows v1`).

---

## 10. Encerramento da Sprint 29

Com o DoD atendido e os gates em `PASS`, os passos finais são:

1. Garantir que `docs/sprint_29_orr_summary.md` esteja atualizado com:
   - visão geral do que foi entregue;
   - estado dos gates;
   - limitações conhecidas;
   - recomendações para próximas sprints do Épico E28.

2. Registrar, no repositório, um apontador para o bundle de evidências:
   - path de `out/bundles/inspectah_s29_evidence_bundle.zip`;
   - hash (opcional) do arquivo para verificação futura.

3. Atualizar o roadmap do Épico E28, marcando S29 como concluída e preparando terreno para as próximas iterações de fluxo (E28.2/E28.3), caso já estejam planejadas.

A partir daí, a Sprint 29 cumpre seu papel: entregar um **fluxo de agentes configurável por domínio**, com domínio, API, UI, runtime e evidências alinhados, pronto para ser refinado e expandido em sprints futuras sem precisar reabrir fundações.

