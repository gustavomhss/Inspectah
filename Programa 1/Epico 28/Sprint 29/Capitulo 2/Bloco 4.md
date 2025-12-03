# Sprint 29 — Capítulo 2
## Bloco 4 — Gate S29_G2 (API de Admin & Validador de Fluxo) em detalhe

Se o S29_G1 garante que o fluxo de agentes configurável existe no modelo de dados, o **S29_G2 — API de Admin & Validador de Fluxo** garante que esse modelo é realmente utilizável e protegido na borda do sistema.

Este gate responde, na prática, a duas perguntas:

1. "O operador consegue, via API, criar, ler e atualizar fluxos de agentes por domínio de forma consistente?"
2. "O sistema impede, de maneira determinística, que fluxos inválidos ou perigosos sejam salvos?"

Este bloco detalha o objetivo, o script, os checks, as métricas, o scorecard e o critério de aprovação do S29_G2.

---

### 1. Objetivo do gate S29_G2

O S29_G2 tem dois objetivos centrais:

1. **Consolidar a API de administração de fluxos de agentes** como contrato estável para UI e automações.  
2. **Aplicar invariantes de fluxo** de forma explícita, testável e auditável, tanto para criação quanto para atualização de configurações.

Ele é o gate que transforma o modelo de dados em uma superfície de operação segura: a partir daqui, qualquer interação legítima com fluxos de agentes deve passar por essa API e pelo seu validador.

---

### 2. Script e responsabilidades

**Script sugerido:**  
`bin/s29_g2_api_and_validator.sh`

**Responsabilidades do script:**

1. Ativar o ambiente virtual e posicionar o diretório raiz do backend.  
2. Rodar os testes automatizados relativos à API de fluxos e ao validador de invariantes.  
3. Opcionalmente, rodar um conjunto de "smoke tests" adicionais (por exemplo, via `pytest -k agent_flow_api`).  
4. Gerar o scorecard JSON `S29_G2_api_and_validator.json` consolidando o resultado.

O script deve retornar exit code 0 apenas se todos os testes e checks passarem.

---

### 3. API de admin de fluxos: rotas e contratos

As rotas vivem em algo como `app/api/admin_agent_flows_routes.py`.

O S29_G2 espera, no mínimo, os seguintes endpoints:

1. `GET /admin/agent-flows`  
   Lista fluxos configurados, com suporte a filtros por domínio, paginação básica e, opcionalmente, busca textual.  
   Uso típico: UI listando quais domínios têm fluxo configurado.

2. `GET /admin/agent-flows/{flow_id}`  
   Retorna uma configuração de fluxo específica, incluindo a lista de passos.  
   Uso típico: detalhe antes de edição.

3. `GET /admin/agent-flows/by-domain/{domain_key}`  
   Retorna o fluxo ativo para um domínio.  
   Uso típico: UI de edição abre diretamente o fluxo certo ao selecionar o domínio.

4. `POST /admin/agent-flows`  
   Cria uma nova configuração de fluxo para um domínio ainda não configurado.  
   Regras básicas:
   - `domain_key` obrigatório;  
   - lista de passos obrigatória (não vazio);  
   - invariantes de fluxo aplicadas (ver seção 4).

5. `PUT /admin/agent-flows/{flow_id}`  
   Atualiza uma configuração existente.  
   Regras básicas:
   - preserva o `domain_key` (normalmente imutável);  
   - substitui ou reordena a lista de passos conforme input;  
   - aplica invariantes de fluxo sobre o conjunto final;  
   - registra `updated_at`, `updated_by` (quando disponível) e `change_reason`.

Os endpoints devem utilizar os schemas Pydantic (`AgentFlowConfigIn`, `AgentFlowConfigOut`, etc.) definidos no S29_G1.

---

### 4. Validador de invariantes de fluxo

O componente crítico deste gate é o módulo de validação, por exemplo `app/agents/flows/validator.py`.

Ele deve expor, no mínimo, uma função de alto nível do tipo:

```python
validate_agent_flow(domain_key: str, steps: list[AgentFlowStepIn]) -> None
```

ou equivalente, levantando exceções específicas em caso de violação de invariantes.

Invariantes mínimas que S29_G2 precisa garantir:

1. **Fluxo não pode ser vazio**  
   Se a lista de `steps` estiver vazia, a validação falha com erro explícito.

2. **Primeiro passo deve ser papel permitido como entrada**  
   O `agent_role` do passo de `position` mínima deve pertencer a um conjunto permitido, por exemplo `{INTERPRETER, INGESTION_NORMALIZER}`.  
   Caso contrário, erro explícito: "Primeiro passo do fluxo deve ser um papel de entrada válido".

3. **Domínios que exigem papéis obrigatórios**  
   Para determinados domínios (por exemplo, domínios marcados como sensíveis), o fluxo precisa obrigatoriamente conter determinados papéis, como `DEBUNKER` antes do `DECISION_MAKER`.  
   Ausência de papéis obrigatórios → erro explicando qual papel está faltando e por quê.

4. **`DECISION_MAKER` só no final**  
   Se o papel `DECISION_MAKER` aparecer em qualquer posição que não seja a última, a validação falha com mensagem clara.  
   Em alguns casos, pode ser aceito fluxo sem `DECISION_MAKER`, mas nunca com esse papel em posição intermediária.

5. **Posições consistentes e sem duplicidade**  
   O conjunto de `position` dos passos não pode conter duplicatas.  
   Idealmente, as posições formam uma sequência coerente (1, 2, 3…), mesmo que isso seja normalizado internamente.

6. **Papéis desconhecidos são rejeitados**  
   O `agent_role` de cada passo precisa pertencer ao catálogo de papéis conhecidos.  
   Papéis desconhecidos geram erro: "Papel de agente não reconhecido".

Essas invariantes precisam ser codificadas de forma clara, com erros específicos (por exemplo, classes de exceção próprias ou códigos de erro categorizados), e não apenas via asserts genéricos.

---

### 5. Testes automatizados esperados

Os testes de S29_G2 dividem-se em dois grupos principais:

1. **Testes do validador** (por exemplo, `tests/agents/test_agent_flow_validator.py`).  
2. **Testes da API** (por exemplo, `tests/agents/test_agent_flow_api.py`).

#### 5.1. Casos mínimos para o validador

Casos obrigatórios a serem cobertos:

1. **Fluxo válido básico**  
   - domínio comum;  
   - passos: `INTERPRETER` → `CLASSIFIER` → `DECISION_MAKER`;  
   - expectativa: validação passa sem erro.

2. **Fluxo vazio**  
   - lista de passos vazia;  
   - expectativa: erro do tipo "fluxo não pode ser vazio".

3. **Primeiro passo inválido**  
   - primeiro passo com papel não permitido como entrada (por exemplo, `DECISION_MAKER`);  
   - expectativa: erro claro sobre papel de entrada inválido.

4. **Domínio sensível sem `DEBUNKER`**  
   - domínio marcado como sensível;  
   - fluxo que nunca passa por `DEBUNKER`;  
   - expectativa: erro indicando que o papel `DEBUNKER` é obrigatório antes da decisão.

5. **`DECISION_MAKER` no meio do fluxo**  
   - fluxo onde `DECISION_MAKER` aparece no meio (por exemplo, passo 3 de 5);  
   - expectativa: erro indicando que `DECISION_MAKER` só pode aparecer no final.

6. **Posições duplicadas**  
   - dois passos com a mesma `position`;  
   - expectativa: erro de posição duplicada.

7. **Papel desconhecido**  
   - fluxo contendo um `agent_role` inexistente no catálogo;  
   - expectativa: erro de papel desconhecido.

#### 5.2. Casos mínimos para a API

Casos obrigatórios a serem cobertos:

1. **Criação de fluxo válido (`POST`)**  
   - envia payload válido;  
   - recebe `201`/`200` com corpo em formato `AgentFlowConfigOut`.

2. **Atualização de fluxo válido (`PUT`)**  
   - altera ordem ou adiciona passo mantendo invariantes;  
   - recebe `200` com configuração atualizada.

3. **Criação de fluxo inválido (ex.: fluxo vazio)**  
   - envia payload com lista de passos vazia;  
   - recebe `400`/`422` com mensagem clara.

4. **Atualização que viola invariantes (ex.: `DECISION_MAKER` no meio)**  
   - envia nova versão do fluxo que quebra regra;  
   - recebe erro com mensagem explícita da invariantes violada.

5. **Leitura de fluxo por domínio existente**  
   - `GET /admin/agent-flows/by-domain/{domain_key}` para domínio com fluxo;  
   - recebe `200` com config e passos.

6. **Leitura de fluxo por domínio sem config**  
   - domínio sem fluxo ainda criado;  
   - resposta consistente (`404` ou payload que sinalize "não configurado"), documentada e testada.

---

### 6. Métricas e evidências do S29_G2

A execução de `bin/s29_g2_api_and_validator.sh` deve produzir:

- Log de testes de validação em `out/evidence/S29_G2_api_and_validator/validator_tests.log`.
- Log de testes de API em `out/evidence/S29_G2_api_and_validator/api_tests.log`.
- Amostras de respostas JSON:
  - `out/evidence/S29_G2_api_and_validator/example_success_response.json`;
  - `out/evidence/S29_G2_api_and_validator/example_error_response.json`.

Métricas a registrar no scorecard:

- `tests_run`: total de testes executados para esse gate (ou filtragem por marcador);  
- `tests_failed`: idealmente 0;  
- `invariants_covered`: lista de invariantes mapeadas explicitamente para casos de teste;  
- `example_success_response_path` e `example_error_response_path`.

---

### 7. Scorecard do S29_G2

O scorecard do gate fica em:

- `out/scorecards/S29_G2_api_and_validator.json`

Formato sugerido:

```json
{
  "gate_id": "S29_G2",
  "status": "PASS",
  "tests_run": 24,
  "tests_failed": 0,
  "invariants_covered": [
    "non_empty_flow",
    "valid_first_role",
    "required_roles_for_sensitive_domain",
    "decision_maker_last",
    "unique_positions",
    "known_roles_only"
  ],
  "evidence_paths": {
    "validator_tests_log": "out/evidence/S29_G2_api_and_validator/validator_tests.log",
    "api_tests_log": "out/evidence/S29_G2_api_and_validator/api_tests.log",
    "example_success_response": "out/evidence/S29_G2_api_and_validator/example_success_response.json",
    "example_error_response": "out/evidence/S29_G2_api_and_validator/example_error_response.json"
  },
  "timestamp": "2025-..-..T..:..:..Z",
  "notes": "APIs de fluxo e validador de invariantes cobertos por testes. Erros retornam mensagens claras."
}
```

Em caso de falha, `status` deve ser `"FAIL"` com `tests_failed > 0` ou com `invariants_covered` faltando itens essenciais, e `notes` deve explicar o que falta ou quebrou.

---

### 8. Critério de aprovação do S29_G2

O S29_G2 é considerado **aprovado (PASS)** se e somente se:

1. Todas as rotas de admin de fluxo (GET/POST/PUT) existirem e funcionarem conforme contrato.  
2. O validador de fluxo implementar, no mínimo, as invariantes definidas no Capítulo 1/Bloco 3 (não vazio, primeiro passo válido, papéis obrigatórios por domínio quando exigido, `DECISION_MAKER` no final, posições consistentes, papéis conhecidos).  
3. Os testes automatizados de API e validação executarem sem falhas.  
4. Os exemplos de respostas de sucesso e erro demonstrarem mensagens claras e consistentes.  
5. O script `bin/s29_g2_api_and_validator.sh` retornar exit code 0 e o scorecard registrar `status == "PASS"`.

Se qualquer uma dessas condições falhar, o gate é **FAIL** e a equipe não deve considerar segura a exposição da UI de fluxo nem a integração com o runtime em cima dessa API.

---

### 9. Importância do S29_G2 no contexto da S29

Na narrativa da Sprint 29, o S29_G2 é o momento em que o fluxo de agentes configurável deixa de ser apenas um par de tabelas e vira um **serviço**:

- o operador passa a ter um caminho suportado para criar e alterar fluxos;  
- o sistema passa a ter um guardião explícito de invariantes antes que qualquer fluxo chegue ao banco;
- a UI, na S29_G3, poderá confiar que suas operações irão falhar de maneira explicável quando algo estiver errado.

Sem um S29_G2 sólido, a sprint correria o risco de expor uma API que aceita praticamente qualquer coisa e empurra o problema para o runtime. Com o gate bem desenhado, a regra passa a ser: **fluxos inválidos morrem na porta**, com log, mensagem clara e scorecard mostrando que o contrato está sendo respeitado.

