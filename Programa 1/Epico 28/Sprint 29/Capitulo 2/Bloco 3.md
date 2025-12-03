# Sprint 29 — Capítulo 2
## Bloco 3 — Gate S29_G1 (Modelos, Schemas e Migrations) em detalhe

O **S29_G1 — Modelos, Schemas e Migrations (AgentFlowConfig)** é o gate que transforma a ideia de “fluxo de agentes configurável por domínio” em **entidades reais de banco e código**. Ele responde à pergunta:

> "O cérebro configurável de fluxo de agentes existe de verdade no modelo de dados, ou ainda está só nos slides?"

Este bloco detalha objetivo, script, checks, métricas, scorecard e critério de aprovação do S29_G1.

---

### 1. Objetivo do gate S29_G1

O objetivo do S29_G1 é garantir que a Sprint 29 possui uma **base de dados coerente** para fluxos de agentes, cobrindo:

1. Modelos de domínio para:
   - configuração de fluxo (`AgentFlowConfig`),
   - passos de fluxo (`AgentFlowStep`).
2. Schemas Pydantic alinhados com esses modelos.
3. Migrations criadas e aplicáveis, que levam o banco do estado pré‑S29 até o estado em que fluxos configuráveis existem.
4. Testes mínimos assegurando que essa modelagem não é apenas teórica.

Se o S29_G1 falha, tudo que vem depois (API, UI, runtime) fica com um chão instável.

---

### 2. Script e responsabilidades

**Script sugerido:**  
`bin/s29_g1_model_and_migrations.sh`

**Responsabilidades do script:**

1. Ativar o ambiente virtual e posicionar o diretório raiz do projeto.
2. Rodar os testes relativos aos modelos/schemas de fluxo de agentes.
3. Rodar as migrations até o `head` (ou equivalente) em uma base de teste.
4. Opcionalmente, capturar o DDL das tabelas relevantes como evidência.
5. Gerar o scorecard JSON `S29_G1_model_and_migrations.json` com o resultado consolidado.

O script deve retornar exit code **0** apenas se todos os passos forem bem‑sucedidos.

---

### 3. Modelos de domínio esperados

Os modelos de domínio residem em algo como `app/agents/flows/models.py`.

#### 3.1. `AgentFlowConfig`

Campos mínimos esperados:

- `id`: identificador único da configuração de fluxo (chave primária);
- `domain_key`: chave estável do domínio ao qual este fluxo pertence;
- `created_at`: timestamp de criação;
- `created_by`: identificador do usuário/sistema que criou (quando aplicável);
- `updated_at`: timestamp da última atualização;
- `updated_by`: identificador do usuário/sistema responsável pela última atualização;
- `change_reason`: texto curto explicando motivo da alteração mais recente;
- (opcional) campos auxiliares como `is_active` ou `version_tag`, se forem necessários para E28.2/E28.3.

Essa entidade representa o "cabeçalho" de um fluxo: o que existe por domínio, quem mexeu, quando e por quê.

#### 3.2. `AgentFlowStep`

Campos mínimos esperados:

- `id`: identificador do passo (chave primária);
- `flow_id`: referência para `AgentFlowConfig` (chave estrangeira);
- `position`: posição ordinal do passo no fluxo (1, 2, 3…);
- `agent_role`: papel do agente neste passo (enum/string validada com catálogo);
- `params`: campo estruturado (JSON ou similar) para parâmetros adicionais (comitê, thresholds, flags etc.).

Requisitos:

- unicidade de `(flow_id, position)` para evitar duas etapas na mesma posição;
- constraints de integridade referencial entre `AgentFlowStep` e `AgentFlowConfig`.

---

### 4. Schemas Pydantic esperados

Os schemas ficam, por exemplo, em `app/agents/flows/schemas.py`.

Mínimo esperado:

- **Entrada (criação/atualização)**:
  - `AgentFlowStepIn` — descreve um passo com `position`, `agent_role`, `params`;
  - `AgentFlowConfigIn` — associa `domain_key` a uma lista de passos (`steps: List[AgentFlowStepIn]`).

- **Saída (respostas da API)**:
  - `AgentFlowStepOut` — passo com `id`, `position`, `agent_role`, `params`;
  - `AgentFlowConfigOut` — config com `id`, `domain_key`, metadados de auditoria e `steps: List[AgentFlowStepOut]`.

Esses schemas precisam:

- estar alinhados com os modelos ORM/SQLAlchemy (ou equivalente);
- ser utilizados nas rotas de admin de fluxo (que serão validadas em G2);
- refletir as invariantes básicas (por exemplo, `domain_key` não nulo, lista de passos não vazia em criação).

---

### 5. Migrations e compatibilidade de banco

O S29_G1 também garante que o banco conhece o novo mundo de fluxos de agentes.

#### 5.1. Migrations

Esperado um arquivo de migration em algo como:

- `migrations/versions/00xx_s29_agent_flows.py`

Responsabilidades dessa migration:

- criar tabela de configs (`agent_flow_configs` ou nome semelhante);
- criar tabela de steps (`agent_flow_steps`);
- definir chaves primárias, foreign keys e índices básicos (por exemplo, índice em `domain_key`, índice composto em `(flow_id, position)`).

#### 5.2. Cenários de aplicação

O gate deve validar que a migration aplica com sucesso em dois cenários:

1. Banco recém‑criado (do zero até `head`).
2. Banco já migrado até S28, recebendo apenas as mudanças de S29.

Em ambos, `alembic upgrade head` (ou equivalente) precisa completar sem erros, e as tabelas novas devem existir com a estrutura esperada.

---

### 6. Testes automatizados de modelos/schemas

Os testes de S29_G1 moram, por exemplo, em `tests/agents/test_agent_flow_models.py`.

Casos mínimos que o gate espera ver cobertos:

1. **Criação básica de fluxo**:
   - criar um `AgentFlowConfig` com `domain_key` válido;
   - anexar três `AgentFlowStep` com posições 1, 2, 3;
   - confirmar que o relacionamento está OK e que todos os passos pertencem ao fluxo.

2. **Unicidade de posição**:
   - tentar criar dois `AgentFlowStep` com a mesma `position` para o mesmo fluxo;
   - garantir que o sistema rejeita isso (via constraint ou validação de domínio).

3. **Serialização com schemas**:
   - instanciar um `AgentFlowConfig` com passos;
   - passá‑lo por `AgentFlowConfigOut`;
   - validar que o payload de saída bate com o formato esperado (campos presentes, tipos corretos).

4. **Migração de round‑trip básica**:
   - criar fluxo e passos via ORM após migrations aplicadas;
   - buscar de volta e conferir consistência dos dados.

Esses testes garantem que não estamos apenas criando tabelas por criar: estamos validando a linha completa **modelo → migration → uso básico**.

---

### 7. Métricas e evidências do S29_G1

Ao rodar `bin/s29_g1_model_and_migrations.sh`, esperamos gerar evidências como:

- Log de execução de testes em `out/evidence/S29_G1_model_and_migrations/tests.log`;
- Log de migrations em `out/evidence/S29_G1_model_and_migrations/migrations.log`;
- (Opcional) Snapshot de DDL das tabelas em `out/evidence/S29_G1_model_and_migrations/ddl_snapshot.sql` ou similar.

Métricas básicas a registrar no scorecard:

- `tests_run`: quantidade de testes relacionados a modelos/schemas;
- `tests_failed`: quantos falharam (idealmente 0);
- `migrations_applied`: boolean indicando se o upgrade completou;
- possivelmente, tamanho/linhas do DDL para ajudar inspeções futuras.

---

### 8. Scorecard do S29_G1

O scorecard deste gate fica em:

- `out/scorecards/S29_G1_model_and_migrations.json`

Formato sugerido:

```json
{
  "gate_id": "S29_G1",
  "status": "PASS",
  "tests_run": 12,
  "tests_failed": 0,
  "migrations_applied": true,
  "evidence_paths": {
    "tests_log": "out/evidence/S29_G1_model_and_migrations/tests.log",
    "migrations_log": "out/evidence/S29_G1_model_and_migrations/migrations.log",
    "ddl_snapshot": "out/evidence/S29_G1_model_and_migrations/ddl_snapshot.sql"
  },
  "timestamp": "2025-..-..T..:..:..Z",
  "notes": "Modelos e migrations de AgentFlowConfig/AgentFlowStep aplicados com sucesso."
}
```

Em caso de falha, `status` deve ser `"FAIL"` e `tests_failed > 0` ou `migrations_applied == false`, com `notes` explicando o motivo.

---

### 9. Critério de aprovação do S29_G1

O S29_G1 é considerado **aprovado (PASS)** se e somente se:

1. Os modelos `AgentFlowConfig` e `AgentFlowStep` existem e cobrem, no mínimo, os campos essenciais (domínio, passos, auditoria básica, params).
2. Os schemas Pydantic de entrada e saída estão implementados e alinhados com os modelos.
3. As migrations de S29 aplicam com sucesso em banco de teste (do zero e desde S28).
4. Os testes automatizados de modelos/schemas executam sem falhas.
5. O script `bin/s29_g1_model_and_migrations.sh` retorna exit code 0 **e** o scorecard `S29_G1_model_and_migrations.json` registra `status == "PASS"`.

Se qualquer uma dessas condições falhar, o gate é **FAIL** e a equipe não deveria prosseguir para G2 (API e validador) sem antes corrigir a modelagem.

---

### 10. Importância do S29_G1 no contexto da sprint

O S29_G1 é onde o fluxo de agentes configurável deixa de ser um diagrama em markdown e passa a existir como:

- tabelas reais em banco;
- entidades de domínio no backend;
- contrato explícito para as APIs futuras.

Sem esse gate sólido, todo o resto vira gesso molhado: a API ficaria em cima de um modelo instável, a UI estaria configurando um objeto frágil, e o runtime dependeria de estruturas que podem mudar de forma não controlada.

Ao tratar o S29_G1 como peça obrigatória (e não como formalidade), a Sprint 29 garante que, quando alguém falar em "fluxo de agentes por domínio", isso significa **algo que o banco, o código e os testes reconhecem como entidade de primeira classe**, não apenas um conceito na cabeça da equipe.