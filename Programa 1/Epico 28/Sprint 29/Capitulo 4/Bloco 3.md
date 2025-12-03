# Sprint 29 — Capítulo 4
## Bloco 3 — Execução detalhada da Wave 2 (Validador & API de admin — G2)

Com a Wave 0 (baseline) e a Wave 1 (domínio de fluxo de agentes: models, schemas, migrations) estabilizadas, a Wave 2 é onde a Sprint 29 começa a **endurecer o cérebro do fluxo**:

- as invariantes deixam de ser só texto e viram código (`validator.py`);
- o serviço de domínio passa a aplicar essas invariantes (`service.py`);
- o mundo externo ganha uma porta estável e segura para manipular fluxos (`admin_agent_flows_routes.py`);
- o Gate S29_G2 garante que isso tudo está consistente, testado e observável.

Este Bloco 3 descreve a execução da Wave 2 em nível cirúrgico: arquivos, passos, comandos, evidências e scorecard.

---

### 1. Objetivos da Wave 2 e relação com G2

A Wave 2 tem quatro objetivos principais:

1. Implementar o **validador de invariantes de fluxo** em `app/agents/flows/validator.py`.  
2. Integrar esse validador ao serviço de domínio em `app/agents/flows/service.py`.  
3. Expor o domínio de fluxo via **API de admin** em `app/api/admin_agent_flows_routes.py`.  
4. Cobrir tudo com testes (validador + API) e consolidar o Gate S29_G2 com evidências e scorecard.

O Gate S29_G2 só é considerado PASS quando:

- as funções de criação/atualização de fluxo **sempre** passam pelo validador;  
- os endpoints de admin funcionam conforme especificado (casos felizes + erros de negócio);  
- erros de invariantes são retornados como HTTP 422 com `{code, message}` claros;  
- testes automatizados de validador e API passam;  
- evidências e scorecard correspondentes existem.

---

### 2. Implementação do validador em `app/agents/flows/validator.py`

O validador materializa as regras de negócio descritas no Capítulo 1/2 para fluxos de agentes.

#### 2.1. Estrutura básica do módulo

Passos sugeridos:

1. Definir a exceção de domínio usada para comunicar violações de invariantes:

   ```python
   class AgentFlowValidationError(Exception):
       def __init__(self, code: str, message: str):
           self.code = code
           self.message = message
           super().__init__(message)
   ```

2. Definir constantes ou helpers com o catálogo de papéis e regras por domínio, consumindo o que vier das sprints de Verdade & Interpretação (na S29, pode ser provisório, mas o design já deve assumir catálogo externo):

   ```python
   ALLOWED_FIRST_ROLES = {"INTERPRETER", "INGESTION_NORMALIZER"}

   REQUIRED_ROLES_BY_DOMAIN_PREFIX = {
       "news.politics": {"DEBUNKER", "DECISION_MAKER"},
   }
   ```

   Observação: se o catálogo estiver em outro módulo (por ex. `app/agents/catalog.py`), importar de lá em vez de duplicar.

3. Implementar a função pública principal:

   ```python
   from .schemas import AgentFlowStepIn

   def validate_agent_flow(domain_key: str, steps: list[AgentFlowStepIn]) -> None:
       ...  # invariantes abaixo
   ```

#### 2.2. Invariantes mínimas a implementar

A função `validate_agent_flow` deve, no mínimo, implementar as seguintes invariantes:

1. **Fluxo não vazio**  
   - Se `steps` estiver vazio → levantar `AgentFlowValidationError("FLOW_EMPTY", "Fluxo de agentes não pode ser vazio.")`.

2. **Primeiro papel permitido**  
   - Verificar o `agent_role` do primeiro step;  
   - se não estiver em `ALLOWED_FIRST_ROLES` → `AgentFlowValidationError("INVALID_FIRST_ROLE", "Primeiro papel do fluxo não é permitido para entrada.")`.

3. **Papéis obrigatórios por tipo de domínio**  
   - Determinar se o domínio é considerado sensível por prefixo (ou outra regra simples);  
   - se for, verificar presença dos papéis obrigatórios (por ex. `DEBUNKER` e `DECISION_MAKER`);  
   - ausência → `AgentFlowValidationError("MISSING_REQUIRED_ROLE", "Fluxo para domínio sensível deve incluir DEBUNKER e DECISION_MAKER.")`.

4. **`DECISION_MAKER` somente na última posição**  
   - Se houver `DECISION_MAKER` em qualquer posição diferente da última → `AgentFlowValidationError("DECISION_MAKER_NOT_LAST", "DECISION_MAKER só pode aparecer na última posição do fluxo.")`.

5. **Posições únicas e coerentes**  
   - Verificar se não há duplicata de `position` dentro do fluxo;  
   - se houver → `AgentFlowValidationError("DUPLICATE_POSITIONS", "Duas ou mais etapas possuem a mesma posição no fluxo.")`.

6. **Papéis conhecidos**  
   - Verificar cada `agent_role` contra o catálogo de papéis;  
   - papel desconhecido → `AgentFlowValidationError("UNKNOWN_ROLE", "Papel de agente desconhecido: ...")`.

Estas invariantes podem ser implementadas em funções auxiliares para manter a clareza:

```python
def _ensure_not_empty(steps: list[AgentFlowStepIn]) -> None: ...

def _ensure_valid_first_role(steps: list[AgentFlowStepIn]) -> None: ...

def _ensure_required_roles(domain_key: str, steps: list[AgentFlowStepIn]) -> None: ...

def _ensure_decision_maker_last(steps: list[AgentFlowStepIn]) -> None: ...

def _ensure_unique_positions(steps: list[AgentFlowStepIn]) -> None: ...

def _ensure_known_roles(steps: list[AgentFlowStepIn]) -> None: ...
```

A função `validate_agent_flow` orquestra essas verificações em sequência.

#### 2.3. Compatibilidade futura

Mesmo que S29 implemente apenas invariantes de v1, o código deve ser organizado de forma que seja fácil adicionar invariantes específicas por domínio ou tipo de fluxo nas próximas iterações do Épico E28 (E28.2, E28.3 etc.), sem precisar reescrever tudo.

---

### 3. Integração do validador no serviço em `app/agents/flows/service.py`

O serviço é o lugar onde as operações de alto nível acontecem (criar, atualizar, buscar). A Wave 2 garante que **nenhuma operação que mude o fluxo escapa do validador**.

#### 3.1. Pontos de entrada a proteger

Funções típicas que devem obrigatoriamente chamar o validador:

- `create_agent_flow(config_in: AgentFlowConfigIn, actor: str | None) -> AgentFlowConfig`;  
- `update_agent_flow(flow_id: str, config_in: AgentFlowConfigIn, actor: str | None) -> AgentFlowConfig`.

Fluxo recomendado para `create_agent_flow`:

1. Extrair `domain_key` e lista de `steps` do `config_in`.  
2. Chamar `validate_agent_flow(domain_key, config_in.steps)`.  
3. Verificar se já existe fluxo ativo para o `domain_key` (regra de negócio: permitir ou não múltiplos).  
4. Criar `AgentFlowConfig` + `AgentFlowStep`s em transação única.  
5. Preencher campos de auditoria (`created_at`, `created_by`, `updated_at`, `updated_by`, `change_reason`).

Fluxo recomendado para `update_agent_flow`:

1. Carregar `AgentFlowConfig` existente pelo `flow_id`.  
2. Checar consistência de domínio (em geral, não permitir trocar `domain_key`).  
3. Chamar `validate_agent_flow(existing.domain_key, config_in.steps)`.  
4. Substituir steps antigos pelo novo conjunto (removendo e recriando ou atualizando em lote).  
5. Atualizar auditoria (`updated_at`, `updated_by`, `change_reason`).

Se `validate_agent_flow` levantar `AgentFlowValidationError`, o serviço **não deve capturar** essas exceções silenciosamente: elas precisam subir até a camada de API para virar erro HTTP 422.

#### 3.2. Erros de domínio adicionais

Além de `AgentFlowValidationError`, o serviço pode definir erros específicos, por exemplo:

```python
class AgentFlowDomainError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)
```

Exemplo de uso:

- tentar criar fluxo para domínio que já possui fluxo ativo → `AgentFlowDomainError("FLOW_ALREADY_EXISTS", ...)`.

Esses erros serão mapeados para `HTTP 400` ou `409` pela camada de API.

---

### 4. Implementação da API de admin em `app/api/admin_agent_flows_routes.py`

Com domínio e validador prontos, a próxima etapa da Wave 2 é expor a funcionalidade via API de admin.

#### 4.1. Estrutura do módulo de rotas

Seguindo o padrão do projeto, o módulo pode ser estruturado como:

```python
from fastapi import APIRouter, Depends
from .dependencies import get_current_admin_user
from app.agents.flows.schemas import AgentFlowConfigIn, AgentFlowConfigOut
from app.agents.flows import service
from app.agents.flows.validator import AgentFlowValidationError
from app.agents.flows.errors import AgentFlowDomainError  # se existir

router = APIRouter(prefix="/admin/agent-flows", tags=["agent-flows-admin"])
```

A autenticação é feita via `get_current_admin_user` ou equivalente, conforme o padrão da API admin.

#### 4.2. Endpoints principais

Implementar, no mínimo, os endpoints:

1. `GET /admin/agent-flows` — listar fluxos (com filtros básicos).  
2. `GET /admin/agent-flows/by-domain/{domain_key}` — obter fluxo por domínio (404 quando não existe).  
3. `GET /admin/agent-flows/{flow_id}` — obter fluxo por ID.  
4. `POST /admin/agent-flows` — criar fluxo novo.  
5. `PUT /admin/agent-flows/{flow_id}` — atualizar fluxo existente.

Todos os endpoints de leitura retornam `AgentFlowConfigOut` ou lista dele. Os de escrita recebem `AgentFlowConfigIn`.

#### 4.3. Tratamento de erros e mapeamento para HTTP

A Wave 2 precisa garantir um padrão consistente de tratamento de erro, em especial para invariantes de fluxo.

Padrão sugerido:

- `AgentFlowValidationError` → HTTP 422 com payload `{ "code": ..., "message": ... }`.  
- `AgentFlowDomainError` (por ex., fluxo duplicado) → HTTP 400 ou 409 com payload semelhante.  
- fluxo não encontrado → HTTP 404 com payload `{ "code": "FLOW_NOT_FOUND", "message": ... }`.

Pode‑se centralizar o mapeamento em helpers:

```python
from fastapi import HTTPException


def _handle_validation_error(exc: AgentFlowValidationError) -> None:
    raise HTTPException(
        status_code=422,
        detail={"code": exc.code, "message": exc.message},
    )


def _handle_domain_error(exc: AgentFlowDomainError) -> None:
    raise HTTPException(
        status_code=400,  # ou 409, dependendo da semântica
        detail={"code": exc.code, "message": exc.message},
    )
```

Uso nas rotas:

```python
@router.post("/", response_model=AgentFlowConfigOut)
async def create_agent_flow(config_in: AgentFlowConfigIn, current_user = Depends(get_current_admin_user)):
    try:
        flow = service.create_agent_flow(config_in, actor=current_user.email)
    except AgentFlowValidationError as exc:
        _handle_validation_error(exc)
    except AgentFlowDomainError as exc:
        _handle_domain_error(exc)
    return flow
```

Essa abordagem mantém a lógica de domínio no serviço/validador, deixando a API apenas traduzir erros para HTTP.

#### 4.4. Logging na camada de API

A Wave 2 também deve introduzir logs mínimos na API admin, registrando:

- criação de fluxo (domínio, flow_id, actor, change_reason);  
- atualização de fluxo (domínio, flow_id, actor, change_reason);  
- falhas de validação (domain_key, código de erro, actor).

Esses logs podem ser salvos com um logger específico (`agent_flows_admin`) e servirão como insumo para evidências de G2 e para depuração.

---

### 5. Testes automatizados da Wave 2

A Wave 2 depende fortemente de uma boa bateria de testes, divididos em camada de domínio (validador) e API.

#### 5.1. Testes de validador: `tests/agents/test_agent_flow_validator.py`

Casos sugeridos:

1. **Fluxo válido simples**  
   - `INTERPRETER → CLASSIFIER → DECISION_MAKER` em domínio não sensível;  
   - `validate_agent_flow` não levanta exceção.

2. **Fluxo vazio**  
   - `steps = []`;  
   - erro `FLOW_EMPTY`.

3. **Primeiro papel inválido**  
   - fluxo começando com papel não permitido;  
   - erro `INVALID_FIRST_ROLE`.

4. **Domínio sensível sem DEBUNKER**  
   - domínio sensível (por ex. `news.politics.br`) sem `DEBUNKER`;  
   - erro `MISSING_REQUIRED_ROLE`.

5. **DECISION_MAKER no meio**  
   - `INTERPRETER → DECISION_MAKER → CLASSIFIER`;  
   - erro `DECISION_MAKER_NOT_LAST`.

6. **Posições duplicadas**  
   - dois passos com `position = 1`;  
   - erro `DUPLICATE_POSITIONS`.

7. **Papel desconhecido**  
   - `agent_role = "ALIEN_OVERLORD"`;  
   - erro `UNKNOWN_ROLE`.

Os testes devem verificar tanto o `code` quanto o `message` da exceção.

#### 5.2. Testes de API: `tests/agents/test_agent_flow_api.py`

Casos sugeridos:

1. **Criação de fluxo válida**  
   - `POST /admin/agent-flows` com payload válido;  
   - resposta 200/201 com `AgentFlowConfigOut` coerente.

2. **Atualização de fluxo válida**  
   - fluxo já existente;  
   - `PUT /admin/agent-flows/{flow_id}` com alterações válidas;  
   - resposta 200 com dados atualizados.

3. **Erro de validação — DECISION_MAKER_NOT_LAST**  
   - `PUT` com fluxo inválido;  
   - resposta 422 com `detail.code == "DECISION_MAKER_NOT_LAST"`.

4. **Domínio sem fluxo configurado**  
   - `GET /admin/agent-flows/by-domain/{domain_key}` para domínio desconhecido;  
   - resposta 404 com `detail.code == "FLOW_NOT_FOUND"`.

5. **Fluxo duplicado**  
   - tentar criar fluxo para domínio que já possui fluxo;  
   - resposta 400/409 com `detail.code == "FLOW_ALREADY_EXISTS"`.

6. **Autenticação**  
   - chamada sem credenciais (ou com credenciais inválidas) → 401/403 conforme padrão global.

Os testes de API podem usar client de teste do FastAPI e fixtures de banco de dados em memória ou de teste.

---

### 6. Script do Gate S29_G2: `bin/s29_g2_api_and_validator.sh`

O Gate S29_G2 orquestra as verificações da Wave 2 e produz evidências e scorecard.

#### 6.1. Responsabilidades do script

1. Rodar testes de validador e API.  
2. Registrar logs de execução dos testes em diretório próprio de evidência.  
3. Opcionalmente, capturar exemplos de respostas de sucesso e erro da API.  
4. Gerar scorecard JSON com status final.

#### 6.2. Estrutura sugerida (conceitual)

Diretórios:

- `out/evidence/S29_G2_api_and_validator/validator_tests.log`;  
- `out/evidence/S29_G2_api_and_validator/api_tests.log`;  
- `out/evidence/S29_G2_api_and_validator/example_success_response.json`;  
- `out/evidence/S29_G2_api_and_validator/example_error_response.json`.

Scorecard:

- `out/scorecards/S29_G2_api_and_validator.json`.

Pseudo‑bash da parte crítica:

```bash
EVIDENCE_DIR="out/evidence/S29_G2_api_and_validator"
SCORECARD="out/scorecards/S29_G2_api_and_validator.json"
mkdir -p "$EVIDENCE_DIR"

# Testes de validador
PYTHONPATH=. pytest tests/agents/test_agent_flow_validator.py \
  | tee "$EVIDENCE_DIR/validator_tests.log"
VALIDATOR_STATUS=$?

# Testes de API
PYTHONPATH=. pytest tests/agents/test_agent_flow_api.py \
  | tee "$EVIDENCE_DIR/api_tests.log"
API_STATUS=$?

STATUS="PASS"
if [ "$VALIDATOR_STATUS" -ne 0 ] || [ "$API_STATUS" -ne 0 ]; then
  STATUS="FAIL"
fi

cat > "$SCORECARD" <<EOF
{
  "gate_id": "S29_G2",
  "status": "$STATUS",
  "checks": {
    "validator_tests_log": "${EVIDENCE_DIR}/validator_tests.log",
    "api_tests_log": "${EVIDENCE_DIR}/api_tests.log"
  },
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "notes": "Validador e API de admin de fluxos executados na Wave 2."
}
EOF

if [ "$STATUS" != "PASS" ]; then
  exit 1
fi
```

Rodar o gate:

```bash
bin/s29_g2_api_and_validator.sh
```

O PR da Sprint 29 não deve avançar para Wave 3 enquanto este gate não estiver em PASS.

---

### 7. Amarração da Wave 2 e preparação para Wave 3

Ao final da Wave 2, com G2 em PASS, a Sprint 29 deve estar no seguinte estado:

1. **Domínio de fluxo de agentes completo na camada de backend**  
   - models, schemas e migrations implementados e testados (Wave 1);  
   - validador de invariantes implementado;  
   - serviço de domínio chamando o validador em todas as operações de escrita.

2. **API de admin funcional e segura**  
   - endpoints `/admin/agent-flows` implementados;  
   - erros de invariantes e de domínio retornados em formato claro (422/400/404 com `{code, message}`);  
   - autenticação/admin integrada.

3. **Testes e evidências robustos**  
   - testes de validador e API cobrindo casos felizes e de erro;  
   - logs de testes salvos em `out/evidence/S29_G2_api_and_validator/`;  
   - scorecard S29_G2 com `status = PASS`.

Com isso, a Wave 3 (UI de fluxo de agentes) pode começar em terreno sólido: o frontend passa a consumir uma API que realmente impõe invariantes de fluxo, em vez de confiar em validações frágeis no cliente. O próximo bloco do Capítulo 4 descreve exatamente como orquestrar essa Wave 3 até o Gate S29_G3 ficar verde.

