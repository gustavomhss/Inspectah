# Sprint 29 — Capítulo 3
## Bloco 2 — Arquitetura de backend: domínio de fluxo de agentes

Este Bloco 2 detalha a **camada de domínio de fluxo de agentes** no backend, que é o coração técnico da S29. É aqui que o conceito de "fluxo de agentes por domínio" ganha forma como:

- modelos de banco;
- contratos Pydantic;
- regras de validação (invariantes);
- operações de serviço de alto nível.

Os blocos seguintes vão se apoiar diretamente nesse desenho para falar de API, UI e runtime.

---

### 1. Princípios de design da camada de domínio

Antes de abrir arquivo por arquivo, a S29 assume alguns princípios explícitos para a camada de domínio de fluxo de agentes:

1. **Fluxo como entidade de primeira classe**  
   `AgentFlowConfig` e `AgentFlowStep` não são tabelas auxiliares: são peças centrais do modelo de verdade/decisão do Inspectah. O design evita tratá-las como "config genérica" sem semântica.

2. **Separação clara entre persistência, contrato e regras de negócio**  
   - Persistência vive em `models.py` (ORM/SQL).  
   - Contratos de entrada/saída vivem em `schemas.py` (Pydantic).  
   - Regras de negócio (invariantes, criação/atualização) vivem em `validator.py` e `service.py`.

3. **Catálogo de papéis externo**  
   A lista de papéis (`INTERPRETER`, `CLASSIFIER`, `DEBUNKER`, `DECISION_MAKER`, etc.) vem das sprints de Verdade & Interpretação. O domínio de fluxo **consome** esse catálogo, não o redefine.

4. **Auditoria acoplada ao domínio**  
   Campos `created_by`, `updated_by`, `change_reason` são parte do modelo, não um afterthought: fluxo sem rastro mínimo de quem mexeu é considerado incompleto.

5. **Preparado para evolução, mas simples na v1**  
   O design deve comportar naturalmente E28.2/E28.3 (histórico rico, versionamento, branching), sem carregar essa complexidade agora.

---

### 2. Módulo `app/agents/flows/models.py`

Este módulo define as entidades de banco que representam fluxos de agentes.

#### 2.1. `AgentFlowConfig`

Responsabilidade: representar uma configuração de fluxo associada a um domínio.

Campos mínimos recomendados:

- `id`: chave primária (UUID ou inteiro, conforme padrão do projeto).
- `domain_key`: string não nula, indexada, identificando o domínio (ex.: `news.politics.br`).
- `created_at`: timestamp de criação.
- `created_by`: identificador do ator (usuário/sistema) que criou a configuração (pode ser `NULL` em primeiro momento, mas o campo existe).
- `updated_at`: timestamp da última atualização.
- `updated_by`: identificador do ator que fez a última alteração.
- `change_reason`: texto curto com a justificativa (ex.: "endurecer fluxo para período eleitoral").
- `is_active`: boolean opcional; por padrão `true` para o fluxo atual.

Relacionamentos:

- `steps`: relação 1:N com `AgentFlowStep`, ordenada por `position`.

Índices sugeridos:

- índice em `domain_key` (busca por domínio é caso comum);
- índice opcional em `(domain_key, is_active)` se for abrir espaço para versões futuras.

#### 2.2. `AgentFlowStep`

Responsabilidade: representar um passo individual dentro de um fluxo.

Campos mínimos recomendados:

- `id`: chave primária.
- `flow_id`: FK para `AgentFlowConfig.id`.
- `position`: inteiro representando a ordem no fluxo (1, 2, 3…).
- `agent_role`: string ou enum mapeando para o catálogo de papéis.
- `params`: JSON/BLOB para parâmetros adicionais (detalhes de comitês, thresholds etc.).

Restrições e índices:

- constraint de unicidade em `(flow_id, position)`;
- índice em `(flow_id, position)` para facilitar ordenação;
- FK `flow_id` com `ON DELETE CASCADE` (remover config remove steps associados).

Essas entidades juntas formam a "coluna vertebral" armazenada dos fluxos de agentes.

---

### 3. Módulo `app/agents/flows/schemas.py`

Este módulo define os contratos de entrada e saída para fluxos de agentes, usando Pydantic.

#### 3.1. Schemas de entrada

- `AgentFlowStepIn`  
  Campos:
  - `position: int` — posição desejada (pode ser normalizada pelo serviço se necessário);
  - `agent_role: str` — papel, validado contra catálogo externo;
  - `params: dict[str, Any] | None` — parâmetros opcionais.

- `AgentFlowConfigIn`  
  Campos:
  - `domain_key: str` — domínio alvo do fluxo;
  - `steps: list[AgentFlowStepIn]` — lista não vazia de passos.

Validações de nível schema (além da validação de domínio em `validator.py`):

- `domain_key` não pode ser string vazia;
- `steps` não pode ser lista vazia (invariantes mais complexas ficam no validador, mas o Pydantic já barra o óbvio).

#### 3.2. Schemas de saída

- `AgentFlowStepOut`  
  Campos:
  - `id`;
  - `position`;
  - `agent_role`;
  - `params`.

- `AgentFlowConfigOut`  
  Campos:
  - `id`;
  - `domain_key`;
  - `steps: list[AgentFlowStepOut>`;
  - `created_at` / `created_by`;
  - `updated_at` / `updated_by`;
  - `change_reason`.

Esses schemas alimentam diretamente as rotas de admin (`S29_G2`) e o cliente de API no frontend (`agentFlowsApi.ts`).

---

### 4. Módulo `app/agents/flows/validator.py`

Este módulo implementa as **invariantes de fluxo** descritas no Capítulo 1/Capítulo 2. Ele é o guardião conceitual que decide se um conjunto de passos pode ou não ser considerado um fluxo válido.

#### 4.1. Interface principal

Assinatura recomendada:

```python
def validate_agent_flow(domain_key: str, steps: list[AgentFlowStepIn]) -> None:
    ...
```

Comportamento:

- não retorna valor em caso de sucesso;
- levanta exceções específicas em caso de violação de invariantes.

Opcionalmente, pode retornar uma estrutura normalizada (por exemplo, passos com posições reindexadas), mas a versão v1 pode apenas validar.

#### 4.2. Exceções e códigos de erro

Definir uma exceção de domínio, por exemplo:

```python
class AgentFlowValidationError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
```

Códigos possíveis (`code`):

- `"FLOW_EMPTY"` — fluxo vazio;
- `"INVALID_FIRST_ROLE"` — papel inicial não permitido;
- `"MISSING_REQUIRED_ROLE"` — papel obrigatório ausente para domínio sensível;
- `"DECISION_MAKER_NOT_LAST"` — `DECISION_MAKER` em posição intermediária;
- `"DUPLICATE_POSITIONS"` — posições duplicadas;
- `"UNKNOWN_ROLE"` — papel desconhecido.

Esses códigos são importantes para a API traduzi‑los em respostas HTTP e para a UI exibir mensagens específicas.

#### 4.3. Invariantes implementadas

O validador deve, no mínimo, implementar:

1. **Fluxo não vazio**  
   - Se `steps` estiver vazio → `FLOW_EMPTY`.

2. **Primeiro papel permitido**  
   - Ex.: conjunto permitido `{"INTERPRETER", "INGESTION_NORMALIZER"}`;
   - Se o primeiro `agent_role` não estiver no conjunto → `INVALID_FIRST_ROLE`.

3. **Papéis obrigatórios por tipo de domínio**  
   - Exemplo: domínios marcados como "sensíveis" precisam conter `DEBUNKER` antes de `DECISION_MAKER`;
   - Implementado via tabela de regras por prefixo de domínio ou flag no catálogo;
   - Ausência → `MISSING_REQUIRED_ROLE` com mensagem explicando.

4. **`DECISION_MAKER` somente na última posição**  
   - Se `DECISION_MAKER` aparecer em qualquer posição diferente da última → `DECISION_MAKER_NOT_LAST`.

5. **Posições coerentes e sem duplicação**  
   - Verificar se os `position` são únicos dentro do fluxo;
   - Em caso de duplicata → `DUPLICATE_POSITIONS`.

6. **Papéis conhecidos**  
   - Verificar cada `agent_role` contra catálogo de papéis;
   - Papel desconhecido → `UNKNOWN_ROLE`.

A lógica de domínio sensível e catálogo de papéis pode residir em módulo compartilhado (por exemplo, `app/agents/catalog.py`), que o validador consome.

---

### 5. Módulo `app/agents/flows/service.py`

O serviço de fluxo encapsula operações de alto nível, combinando modelo + validação + auditoria. Isso evita que rotas ou outros componentes dupliquem lógica.

#### 5.1. Funções principais

Sugestão de interface:

```python
from .schemas import AgentFlowConfigIn, AgentFlowConfigOut


def create_agent_flow(config_in: AgentFlowConfigIn, actor: str | None = None) -> AgentFlowConfig:
    """Cria um fluxo para um domínio ainda não configurado."""


def update_agent_flow(flow_id: str, config_in: AgentFlowConfigIn, actor: str | None = None) -> AgentFlowConfig:
    """Atualiza um fluxo existente, preservando domain_key e aplicando invariantes."""


def get_agent_flow_by_domain(domain_key: str) -> AgentFlowConfig | None:
    """Retorna a config ativa para um domínio, se existir."""
```

Comportamento esperado:

- `create_agent_flow`:
  - chama `validate_agent_flow(domain_key, steps)`;
  - cria `AgentFlowConfig` + `AgentFlowStep` em transação única;
  - preenche `created_at`, `created_by`, `updated_at`, `updated_by`, `change_reason` (quando disponível);
  - lança erro específico se o domínio já tiver fluxo existente (regra de negócio a definir: permitir múltiplas versões ativas ou não).

- `update_agent_flow`:
  - carrega `AgentFlowConfig` existente;
  - opcionalmente, verifica se `domain_key` do `config_in` bate com o existente (ou ignora o campo de entrada para evitar confusão);
  - aplica `validate_agent_flow` ao conjunto de passos proposto;
  - substitui steps antigos pelo novo conjunto (ou faz diff inteligente, se desejado);
  - atualiza campos de auditoria;
  - persiste em transação única.

- `get_agent_flow_by_domain`:
  - consulta por `domain_key` (e `is_active == true`, se esse campo existir);
  - retorna config com steps eager loaded ou `None` se não houver configuração.

#### 5.2. Auditoria mínima

O serviço é o lugar onde se garante que os campos de auditoria são sempre preenchidos quando possível:

- `actor` vem de contexto de auth (ex.: `current_user.email`);
- `change_reason` vem do payload recebido da UI (campo obrigatório ao salvar);
- se `actor` for `None` (operações de sistema), o campo pode registrar um identificador padrão (ex.: `"system"`).

---

### 6. Módulo `app/agents/flows/runtime_adapter.py` (parte de domínio)

Embora o runtime seja assunto mais direto do Bloco 4, parte da função do adapter é ainda "domínio" — ele traduz a config salvos em modelo para um plano de execução.

Interface sugerida:

```python
class AgentFlowRuntimePlan(BaseModel):
    domain_key: str
    flow_id: str | None
    steps: list[str]  # lista de agent_role na ordem a ser executada


def get_agent_flow_for_domain(domain_key: str) -> AgentFlowRuntimePlan:
    ...
```

Comportamento em alto nível:

- tenta buscar `AgentFlowConfig` via `get_agent_flow_by_domain`;
- se encontrar:
  - monta `steps` com base em `AgentFlowStep` ordenados por `position`;
  - retorna `AgentFlowRuntimePlan` com `flow_id` preenchido;
- se não encontrar:
  - monta plano usando fluxo padrão global (definido em config);
  - retorna `AgentFlowRuntimePlan` com `flow_id = None` e flag de fallback registrada em log (detalhado no Bloco 4).

Esse módulo é a ponte conceitual entre "fluxo como config" e "fluxo como sequência de papéis executados".

---

### 7. Testes unitários do domínio

A camada de domínio deve ser coberta por testes focados em comportamento, em arquivos como:

- `tests/agents/test_agent_flow_models.py`;
- `tests/agents/test_agent_flow_validator.py`;
- `tests/agents/test_agent_flow_service.py` (opcional mas altamente recomendado).

Casos mínimos:

- criar config com múltiplos steps e verificar consistência em banco;
- tentativa de criar fluxo com posições duplicadas falhando conforme esperado;
- validação rejeitando fluxos vazios, papéis inválidos, ausência de `DEBUNKER` em domínio sensível etc.;
- serviço criando e atualizando fluxos com auditoria preenchida.

Esses testes alimentam diretamente o **Gate S29_G1** e parte do **S29_G2**, como descrito no Capítulo 2.

---

### 8. Amarração do Bloco 2

Este Bloco 2 fixa o desenho interno da camada de domínio de fluxo de agentes:

- onde os fluxos vivem (`models.py`),
- como são expostos e consumidos (`schemas.py`),
- como são protegidos por regras (`validator.py`),
- como são manipulados de forma transacional e auditável (`service.py`),
- e como começam a conversar com o runtime (`runtime_adapter.py`).

Com essa base estabelecida, o Bloco 3 do Capítulo 3 pode descer para a **arquitetura da API de admin de fluxos**, mostrando como o resto do mundo conversa com esse domínio sem quebrar invariantes nem precisar conhecer detalhes internos desnecessários.

