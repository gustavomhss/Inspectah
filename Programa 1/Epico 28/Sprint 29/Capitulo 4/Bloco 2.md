# Sprint 29 — Capítulo 4
## Bloco 2 — Execução detalhada da Wave 0 e Wave 1 (G0 e G1)

Este Bloco 2 desce o zoom da visão geral de waves (Bloco 1) para o nível **operacional e cirúrgico** da execução das duas primeiras waves da S29:

- **Wave 0 — Preparação & Baseline** → Gate S29_G0.  
- **Wave 1 — Domínio de fluxo de agentes (models, schemas, migrations)** → Gate S29_G1.

A meta é que, seguindo este bloco, a equipe consiga:

1. Abrir a branch de sprint em terreno limpo.  
2. Garantir que docs e filemap de S29 existem, fazem sentido e batem com a arquitetura.  
3. Implementar o núcleo de domínio de fluxo de agentes (models + schemas + migrations).  
4. Rodar G0 e G1 produzindo scorecards e evidências impecáveis.

---

### 1. Wave 0 — Preparação & Baseline (Gate S29_G0)

A Wave 0 garante que a Sprint 29 **começa em estado saneado**, sem lixo de sprints anteriores nem surpresa escondida em ambiente.

#### 1.1. Verificar estado do repositório e criar branch da sprint

Passos recomendados no terminal local:

```bash
cd /Users/gustavoschneiter/Documents/Inspectah
source .venv/bin/activate

# Garantir que estamos na main e atualizados
git checkout main
git pull --ff-only

# Criar branch da sprint 29
git checkout -b feature/programa1_s29_agent_flows_v1
```

Checagens manuais úteis após isso:

```bash
git status
```

Esperado:

- working tree limpo;  
- sem arquivos modificados não intencionais.

Se houver lixo (arquivos alterados de sprints anteriores), decidir conscientemente entre:

- commitar em outra branch;  
- descartar com `git restore` / `git clean`;  
- ou, em último caso, separar em PR próprio antes de abrir S29.

#### 1.2. Sanity de backend e frontend antes de mexer na S29

Antes de adicionar qualquer linha relacionada a S29, rodar um sanity global para evitar confundir débito antigo com bug novo.

Backend:

```bash
PYTHONPATH=. pytest
```

Frontend:

```bash
cd frontend/inspectah-ui
npm ci --prefer-offline
npm run lint
npm test
npm run build
cd ../..
```

Regras de ouro:

- Se algo quebrar aqui, **não culpar S29**: ainda não mexemos na sprint.  
- Registrar o problema (log, traceback) e decidir se a correção entra como pré‑trabalho da S29 ou como fix separado.

#### 1.3. Estrutura mínima de pastas e arquivos da S29

Criar (se ainda não existirem) as estruturas que a sprint vai ocupar. Isso evita caminhos mágicos aparecendo no meio do código:

```bash
# Backend – domínio de fluxos de agentes
mkdir -p app/agents/flows
: > app/agents/flows/__init__.py
: > app/agents/flows/models.py
: > app/agents/flows/schemas.py
: > app/agents/flows/validator.py
: > app/agents/flows/service.py
: > app/agents/flows/runtime_adapter.py

# Frontend – feature de fluxo de agentes
mkdir -p frontend/inspectah-ui/src/features/agent-flows
: > frontend/inspectah-ui/src/features/agent-flows/AgentFlowsPage.tsx
: > frontend/inspectah-ui/src/features/agent-flows/AgentFlowEditor.tsx
: > frontend/inspectah-ui/src/features/agent-flows/agentFlowsApi.ts
: > frontend/inspectah-ui/src/features/agent-flows/agentFlowsTypes.ts

# Evidências e scorecards de S29
mkdir -p out/evidence/S29_G0_scope_and_baseline
mkdir -p out/evidence/S29_G1_model_and_migrations
mkdir -p out/evidence/S29_G2_api_and_validator
mkdir -p out/evidence/S29_G3_ui_and_frontend_quality
mkdir -p out/evidence/S29_G4_runtime_and_observability
mkdir -p out/evidence/S29_G5_orr_and_bundle

mkdir -p out/scorecards
mkdir -p out/bundles
```

O objetivo aqui **não é** implementar nada ainda, mas garantir que os caminhos de filemap definidos no Cap. 3 já existem fisicamente.

#### 1.4. Documentos da Sprint 29

Conferir (ou criar) os docs principais:

- `docs/sprint_29_macro.md` — visão macro da sprint.  
- `docs/sprint_29_capitulo_1.md` — contexto, objetivos, riscos.  
- `docs/sprint_29_capitulo_2.md` — gates, métricas, scorecards.  
- `docs/sprint_29_capitulo_3.md` — arquitetura e filemap.  
- `docs/sprint_29_capitulo_4.md` — este capítulo (execução & evidências).

O Gate S29_G0 deve checar **existência** e **consistência mínima** desses documentos.

#### 1.5. Implementar script do Gate S29_G0

Script sugerido: `bin/s29_g0_scope_and_baseline.sh`.

Responsabilidades do script:

1. Verificar que os docs de S29 existem.  
2. Verificar que as pastas de evidência/scorecards/bundles de S29 existem.  
3. Opcional: rodar um sanity muito leve (por ex. listar testes, checar versão de Python/NPM).  
4. Gerar arquivo de log com o resultado das verificações.  
5. Emitir scorecard JSON com `status` `PASS` ou `FAIL`.

Exemplo conceitual da última parte do script (pseudo‑bash):

```bash
EVIDENCE_DIR="out/evidence/S29_G0_scope_and_baseline"
SCORECARD="out/scorecards/S29_G0_scope_and_baseline.json"
mkdir -p "$EVIDENCE_DIR"

# ... fazer verificações e registrar em "$EVIDENCE_DIR/docs_check.txt" ...

STATUS="PASS"  # ou "FAIL" se faltou algo

cat > "$SCORECARD" <<EOF
{
  "gate_id": "S29_G0",
  "status": "$STATUS",
  "checks": {
    "docs_present": true,
    "filemap_dirs_present": true
  },
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "notes": "Baseline verificada para S29."
}
EOF

if [ "$STATUS" != "PASS" ]; then
  exit 1
fi
```

Rodar o gate:

```bash
bin/s29_g0_scope_and_baseline.sh
```

Saídas esperadas:

- `out/evidence/S29_G0_scope_and_baseline/docs_check.txt` com uma lista das verificações realizadas.  
- `out/scorecards/S29_G0_scope_and_baseline.json` com `"status": "PASS"`.

Só avançar para Wave 1 se G0 estiver verde.

---

### 2. Wave 1 — Domínio de fluxo de agentes (Gate S29_G1)

Com a baseline garantida, a Wave 1 é onde a S29 **começa a criar valor de verdade** no código: o fluxo de agentes passa a existir como entidade de domínio, com modelos, schemas e migrations.

#### 2.1. Implementar modelos em `app/agents/flows/models.py`

Objetivo: introduzir duas entidades principais:

- `AgentFlowConfig` — a configuração de fluxo por domínio.  
- `AgentFlowStep` — cada passo dentro de um fluxo.

Pontos de atenção no design (resumindo Cap. 3 Bloco 2):

- `AgentFlowConfig`:
  - `id` (PK),
  - `domain_key` (string, indexada),
  - `created_at`, `created_by`,
  - `updated_at`, `updated_by`,
  - `change_reason`,
  - `is_active` (opcional, mas recomendado),
  - relacionamento `steps` (1:N).

- `AgentFlowStep`:
  - `id` (PK),
  - `flow_id` (FK para `AgentFlowConfig`),
  - `position` (inteiro, indexado, único por `flow_id`),
  - `agent_role` (string/enum para papel de agente),
  - `params` (JSON/JSONB ou equivalente).

Regras a garantir no nível de modelo/migração:

- constraint de unicidade em `(flow_id, position)`;  
- `domain_key` não nulo nem vazio;  
- `created_at`/`updated_at` com defaults sensatos.

#### 2.2. Implementar schemas Pydantic em `app/agents/flows/schemas.py`

Criar schemas alinhados aos contratos da API e da UI:

- Entrada:
  - `AgentFlowStepIn` → `position`, `agent_role`, `params?`.  
  - `AgentFlowConfigIn` → `domain_key`, `steps: list[AgentFlowStepIn]`.

- Saída:
  - `AgentFlowStepOut` → `id`, `position`, `agent_role`, `params`.  
  - `AgentFlowConfigOut` → `id`, `domain_key`, metadados (`created_at`, `created_by`, `updated_at`, `updated_by`, `change_reason`), `steps`.

Validações básicas de schema (sem roubar o papel do `validator.py`):

- `domain_key` não pode ser string vazia;  
- `steps` deve ser lista não vazia (para o caso mais comum);  
- tipos corretos (inteiros, strings etc.).

#### 2.3. Criar migration para as tabelas de fluxo

Usando o mecanismo oficial do projeto (Alembic ou equivalente), gerar uma migration introduzindo as novas tabelas.

Exemplo (ajustar para a realidade do projeto):

```bash
alembic revision -m "S29: agent flows" --autogenerate
```

Depois, revisar o arquivo gerado em `migrations/versions/00xx_s29_agent_flows.py` para garantir:

- criação das tabelas `agent_flow_configs` e `agent_flow_steps` (nomes ilustrativos);  
- colunas e tipos corretos;  
- FK `flow_id` com `ON DELETE CASCADE`;  
- índices em `domain_key` e `(flow_id, position)`;  
- constraint de unicidade em `(flow_id, position)`.

Aplicar migration em banco local:

```bash
alembic upgrade head
```

Salvar logs de execução em:

- `out/evidence/S29_G1_model_and_migrations/migrations.log`.

Opcional, mas recomendado:

- exportar DDL das tabelas novas para `out/evidence/S29_G1_model_and_migrations/ddl_snapshot.sql`.

#### 2.4. Testes de modelos e schemas

Criar testes em `tests/agents/test_agent_flow_models.py` para garantir que o domínio básico se comporta como esperado.

Casos sugeridos:

1. **Criação simples de fluxo**  
   - criar manualmente uma instância de `AgentFlowConfig` com steps;  
   - commitar/flush no banco;  
   - recarregar e verificar:
     - `domain_key` correto;
     - steps presentes e ordenáveis por `position`.

2. **Unicidade de posição**  
   - tentar criar dois `AgentFlowStep` com a mesma `(flow_id, position)`;  
   - verificar erro esperado (IntegrityError).

3. **Serialização via schemas**  
   - carregar uma config real de banco;  
   - convertê-la em `AgentFlowConfigOut`;  
   - verificar que os campos esperados estão presentes e corretos.

Rodar os testes:

```bash
PYTHONPATH=. pytest tests/agents/test_agent_flow_models.py
```

Se for criado um teste específico de schemas (`test_agent_flow_schemas.py`), rodar também.

#### 2.5. Implementar script do Gate S29_G1

Script sugerido: `bin/s29_g1_model_and_migrations.sh`.

Responsabilidades:

1. Garantir que migrations estão atualizadas e aplicadas (ou rodar uma sequência segura de `alembic upgrade` em ambiente de teste).  
2. Rodar testes específicos de modelos/schemas de fluxo.  
3. Registrar logs em `out/evidence/S29_G1_model_and_migrations/`.  
4. Gerar scorecard `out/scorecards/S29_G1_model_and_migrations.json` com `status` (`PASS`/`FAIL`).

Exemplo conceitual (pseudo‑bash da parte final):

```bash
EVIDENCE_DIR="out/evidence/S29_G1_model_and_migrations"
SCORECARD="out/scorecards/S29_G1_model_and_migrations.json"
mkdir -p "$EVIDENCE_DIR"

# Rodar testes de modelos
PYTHONPATH=. pytest tests/agents/test_agent_flow_models.py \
  | tee "$EVIDENCE_DIR/tests.log"

TEST_STATUS=$?

STATUS="PASS"
if [ "$TEST_STATUS" -ne 0 ]; then
  STATUS="FAIL"
fi

cat > "$SCORECARD" <<EOF
{
  "gate_id": "S29_G1",
  "status": "$STATUS",
  "tests_log": "$EVIDENCE_DIR/tests.log",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "notes": "Modelos, schemas e migrations de fluxo de agentes executados."

}

