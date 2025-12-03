# Sprint 29 — Capítulo 3
## Bloco 3 — Arquitetura de backend: API de admin de fluxos

Com a camada de domínio de fluxo de agentes definida no Bloco 2 (models, schemas, validator, service, runtime adapter), este Bloco 3 descreve **como o backend expõe esse domínio via API de administração**.

A API de admin é a superfície oficial pela qual o restante do sistema (UI, automações internas, integrações futuras) consegue:

- descobrir quais domínios têm fluxo configurado;
- ler o fluxo ativo de um domínio específico;
- criar um fluxo novo;
- atualizar um fluxo existente;
- receber erros explicativos quando invariantes são violadas.

---

### 1. Princípios de design da API de admin

Alguns princípios explícitos orientam a arquitetura da API de fluxos na S29:

1. **API fina, domínio gordo**  
   Rotas fazem pouco: validam input básico, chamam o serviço de domínio e traduzem exceções em respostas HTTP. Toda lógica de fluxo vive em `service.py` e `validator.py`.

2. **Contratos estáveis e tipados**  
   Os payloads seguem rigidamente os schemas Pydantic (`AgentFlowConfigIn`, `AgentFlowConfigOut`), com mapeamento 1:1 para tipos TypeScript do frontend.

3. **Mensagens de erro explicativas**  
   Violações de invariantes não aparecem como "400 genérico": a API responde com códigos de erro específicos (`code`) e mensagens legíveis (`message`), consumíveis pela UI.

4. **Reuso de infraestrutura de auth/admin**  
   A API de fluxos não inventa mecanismo novo de autenticação; ela pluga nas dependências padrão do console admin (usuários, permissões, auditoria básica).

5. **Preparada para extensões de governança**  
   O design já leva em conta que, no futuro, camadas adicionais (approvals, versionamento) podem ser adicionadas sem quebrar clientes atuais.

---

### 2. Localização e estrutura do módulo de rotas

O módulo principal de rotas de admin de fluxo mora em:

- `app/api/admin_agent_flows_routes.py`

Ele segue os padrões já estabelecidos para outros módulos de admin:

- uso de `APIRouter` com prefixo (`/admin/agent-flows`);
- dependência de autenticação (por ex.: `get_current_admin_user`);
- injeção de sessão de banco ou Unit of Work via dependências do FastAPI.

Exemplo de esqueleto (conceitual):

```python
router = APIRouter(prefix="/admin/agent-flows", tags=["agent-flows-admin"])


@router.get("/", response_model=list[AgentFlowConfigOut])
async def list_agent_flows(...):
    ...


@router.get("/by-domain/{domain_key}", response_model=AgentFlowConfigOut)
async def get_agent_flow_by_domain(domain_key: str, ...):
    ...


@router.post("/", response_model=AgentFlowConfigOut)
async def create_agent_flow(config_in: AgentFlowConfigIn, ...):
    ...


@router.put("/{flow_id}", response_model=AgentFlowConfigOut)
async def update_agent_flow(flow_id: str, config_in: AgentFlowConfigIn, ...):
    ...
```

A implementação real é mais detalhada, mas o padrão é sempre: input tipado → serviço → resposta tipada.

---

### 3. Endpoints e seus papéis

A API de admin de fluxos expõe, no mínimo, os seguintes endpoints:

1. `GET /admin/agent-flows`  
   Objetivo: listar fluxos existentes.

   Comportamento típico:
   - suporta filtros como `domain_key` (exato ou prefixo) e paginação;
   - retorna lista de `AgentFlowConfigOut` (sem necessidade de incluir todos os detalhes de steps, dependendo de volume; pode retornar apenas metadados e usar outro endpoint para detalhe).

2. `GET /admin/agent-flows/by-domain/{domain_key}`  
   Objetivo: obter fluxo ativo de um domínio.

   Comportamento:
   - se existir fluxo para `domain_key`, retorna `AgentFlowConfigOut` completo com steps;
   - se não existir, responde com `404` e payload estruturado, por exemplo:

   ```json
   {
     "code": "FLOW_NOT_FOUND",
     "message": "Nenhuma configuração de fluxo encontrada para o domínio 'news.politics.br'"
   }
   ```

3. `GET /admin/agent-flows/{flow_id}`  
   Objetivo: obter fluxo por ID.

   Comportamento:
   - usado principalmente pela UI ou ferramentas internas para detalhar um fluxo específico;
   - se não encontrar, responde com `404` análogo ao caso por domínio.

4. `POST /admin/agent-flows`  
   Objetivo: criar fluxo para um domínio ainda não configurado.

   Comportamento:
   - recebe `AgentFlowConfigIn`;
   - aplica validação de schema (Pydantic) e, em seguida, `validate_agent_flow` via `service.create_agent_flow`;
   - em caso de sucesso, retorna `AgentFlowConfigOut` com `201` (ou `200`, conforme padrão do projeto);
   - se o domínio já tiver fluxo, pode retornar erro específico:

   ```json
   {
     "code": "FLOW_ALREADY_EXISTS",
     "message": "O domínio 'news.politics.br' já possui um fluxo configurado."
   }
   ```

5. `PUT /admin/agent-flows/{flow_id}`  
   Objetivo: atualizar fluxo existente.

   Comportamento:
   - recebe `AgentFlowConfigIn` com nova lista de steps e, opcionalmente, `change_reason` (pode vir separado ou embutido);
   - impede troca arbitrária de `domain_key` (em geral, o domínio é imutável após criação);
   - aplica `validate_agent_flow` no conjunto proposto;
   - atualiza steps em transação única (removendo os antigos, criando novos, reindexando se necessário);
   - atualiza campos de auditoria (`updated_at`, `updated_by`, `change_reason`);
   - retorna `AgentFlowConfigOut` atualizado.

Todos esses endpoints se apoiam nos schemas do módulo `schemas.py` e no serviço do módulo `service.py`.

---

### 4. Integração com autenticação e autorização

A API de admin de fluxos é parte do console administrativo do Inspectah e, portanto, é protegida por:

- **autenticação** padrão do backend (tokens, sessões, etc.);
- **autorização** que exige perfil de admin (ou role equivalente) para criar/editar fluxos.

Na S29, o requisito mínimo é reaproveitar o guard já utilizado por outras rotas admin, algo como:

```python
current_user = Depends(get_current_admin_user)
```

Num futuro próximo, especialmente para domínios sensíveis, podem ser adicionadas regras mais finas, como:

- permissões específicas por domínio ou família de domínios;
- necessidade de dupla aprovação para alterações em certos fluxos.

A arquitetura da S29 não implementa essas regras complexas, mas deixa espaço para elas sem quebrar a API.

---

### 5. Tratamento de erros e mapeamento de exceções

Erros de validação de fluxo não podem aparecer para a UI como traços genéricos de stack. O fluxo é:

1. `validator.py` levanta `AgentFlowValidationError(code, message)`.  
2. `service.py` não engole esses erros; os propaga para a camada de API.  
3. O módulo de rotas tem um handler central que converte essas exceções em respostas HTTP.

Exemplo conceitual:

```python
from fastapi import HTTPException


def _handle_agent_flow_error(exc: AgentFlowValidationError) -> NoReturn:
    raise HTTPException(
        status_code=422,
        detail={"code": exc.code, "message": exc.message},
    )
```

Nas rotas:

```python
try:
    flow = service.create_agent_flow(config_in, actor=current_user.email)
except AgentFlowValidationError as exc:
    _handle_agent_flow_error(exc)
```

Outros erros de domínio (como `FLOW_ALREADY_EXISTS`) podem ser representados por exceções específicas (por exemplo, `AgentFlowDomainError`) com mapeamentos para `400` ou `409`.

Esse padrão garante que:

- a UI consegue distinguir tipos diferentes de falhas;
- logs de backend registram claramente qual invariantes foi violada;
- o comportamento é previsível para testes automatizados.

---

### 6. Padrões de logging na API de admin

A API de fluxos registra eventos importantes para auditoria e depuração.

Eventos logados incluem:

- criação de fluxo:
  - domínio, `flow_id`, `created_by`, `change_reason`;
- atualização de fluxo:
  - domínio, `flow_id`, `updated_by`, `change_reason` (antes/depois se necessário);
- falhas de validação:
  - `domain_key`, `code` de erro, opcionalmente amostra truncada de steps enviados.

O logger pode ser algo como `agent_flows_admin`, com nível ajustado para evitar vazamento de informação sensível em ambientes de produção.

Esses logs alimentam evidências da S29 (especialmente G2 e G5), além de ajudar a explicar por que certos fluxos não chegaram a ser salvos.

---

### 7. Testes da API (visão arquitetural)

Embora os detalhes estejam no Capítulo 2 (Bloco 4), do ponto de vista de arquitetura é importante fixar quais comportamentos **devem existir** para que a API seja considerada bem desenhada:

- testes de criação e atualização feliz (200/201 com payload coerente);
- testes de erros por invariantes violadas (vários códigos de `AgentFlowValidationError` mapeados para 422);
- testes de domínio sem fluxo (`GET /by-domain/{domain_key}` retornando 404 controlado);
- testes de erros de domínio (por ex., tentativa de criar fluxo duplicado) retornando 400/409 com código específico;
- testes de autenticação (acesso sem credenciais → 401/403, conforme padrão global).

A arquitetura prevê que esses testes morem em `tests/agents/test_agent_flow_api.py` e usem os próprios contratos da API, sem acessar diretamente `service.py` ou `validator.py`.

---

### 8. Versionamento e compatibilidade futura

A API de admin da S29 é pensada como **v1 do endpoint de fluxo de agentes**. Para evitar dores futuras:

- os paths são pensados de forma genérica (`/admin/agent-flows`), sem detalhes de versão embutidos na URL;
- a evolução futura pode introduzir um prefixo de versão (por ex., `/admin/v2/agent-flows`) caso seja necessário mudar radicalmente o contrato;
- campos opcionais são tratados com cuidado para permitir adição posterior sem quebrar clientes (por ex., campos extras em `AgentFlowConfigOut`).

A S29 não implementa múltiplas versões, mas não se fecha a essa possibilidade.

---

### 9. Amarração do Bloco 3

Este Bloco 3 fixa como a camada de domínio de fluxo de agentes é exposta ao mundo via API de admin:

- onde moram as rotas (`app/api/admin_agent_flows_routes.py`);
- quais endpoints existem e para quê;
- como a API se integra com autenticação e autorização de admin;
- como erros de domínio são traduzidos em respostas HTTP limpas e tipadas;
- como logs e testes completam o quadro.

Com isso, o Capítulo 3 já tem duas peças principais bem definidas (domínio e API). No próximo bloco, a arquitetura da UI de fluxo de agentes vai completar o caminho até o operador humano, permitindo que as decisões de produto feitas no Capítulo 1 se transformem em configurações aplicadas, rastreáveis e respeitadas pelo runtime.

