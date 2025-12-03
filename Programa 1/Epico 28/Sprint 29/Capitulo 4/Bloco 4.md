# Sprint 29 — Capítulo 4
## Bloco 4 — Execução detalhada da Wave 3 (UI de fluxo de agentes — G3)

Com a Wave 2 concluída e o Gate S29_G2 em PASS, a Sprint 29 já tem:

- domínio de fluxo de agentes bem definido (models, schemas, migrations, serviço);
- invariantes de fluxo codificadas no validador;
- API de admin funcional e protegida por autenticação, com tratamento limpo de erros.

A Wave 3 é o momento de **colocar isso na mão do humano**: criar uma UI de fluxo de agentes que permita a operadores admin:

- enxergar rapidamente o estado de configuração por domínio;
- editar o fluxo (adicionar/remover/reordenar passos, ajustar papéis e parâmetros);
- salvar alterações com justificativa e receber feedback claro em caso de erro.

O Gate S29_G3 garante que essa UI não é uma casca improvisada, mas uma feature integrada, testada e alinhada ao design system.

---

### 1. Objetivos da Wave 3 e relação com G3

A Wave 3 tem quatro objetivos principais:

1. Implementar tipos, cliente de API e (opcionalmente) hooks da feature de fluxo de agentes no frontend.  
2. Implementar a página principal (`AgentFlowsPage`) e o editor (`AgentFlowEditor`).  
3. Integrar a feature ao router e layout admin, com entrada de menu e navegação coerente.  
4. Garantir qualidade mínima via lint, testes e build, consolidando o Gate S29_G3.

O Gate S29_G3 é considerado PASS quando:

- o frontend compila (build) e passa nos linters e testes;  
- a UI de fluxo consegue conversar com a API de admin, em ambiente de teste/local, para pelo menos um domínio;  
- erros de invariantes retornados pelo backend são exibidos de forma compreensível;  
- as evidências e o scorecard de G3 existem e refletem esse estado.

---

### 2. Implementação de tipos e cliente de API

A base da feature de UI da Wave 3 é a camada de tipos e cliente HTTP que conversa com a API de admin implementada na Wave 2.

#### 2.1. Tipos TypeScript — `agentFlowsTypes.ts`

Em `frontend/inspectah-ui/src/features/agent-flows/agentFlowsTypes.ts`, definir os tipos que espelham os schemas Pydantic usados pelo backend:

- `AgentFlowStep` — equivalente ao `AgentFlowStepOut`:
  - `id: string`;
  - `position: number`;
  - `agentRole: string`;
  - `params?: Record<string, unknown> | null`.

- `AgentFlowConfig` — equivalente ao `AgentFlowConfigOut`:
  - `id: string`;
  - `domainKey: string`;
  - `steps: AgentFlowStep[]`;
  - `createdAt: string`;
  - `createdBy?: string | null`;
  - `updatedAt: string`;
  - `updatedBy?: string | null`;
  - `changeReason?: string | null`.

- `AgentFlowStepForm` / `AgentFlowConfigForm` — estruturas usadas apenas no formulário:
  - `AgentFlowStepForm`: `position`, `agentRole`, `params`;
  - `AgentFlowConfigForm`: `domainKey`, `steps: AgentFlowStepForm[]`, `changeReason: string`.

A ideia é ter um tipo voltado para exibição (`AgentFlowConfig`) e outro para edição (`AgentFlowConfigForm`), sem misturar conceitos.

#### 2.2. Cliente de API — `agentFlowsApi.ts`

Em `frontend/inspectah-ui/src/features/agent-flows/agentFlowsApi.ts`, implementar funções que encapsulam as chamadas HTTP para a API de admin:

- `listAgentFlows(params?)` → `GET /admin/agent-flows`;
- `getAgentFlowByDomain(domainKey)` → `GET /admin/agent-flows/by-domain/{domain_key}`;
- `createAgentFlow(payload: AgentFlowConfigForm)` → `POST /admin/agent-flows`;
- `updateAgentFlow(flowId, payload: AgentFlowConfigForm)` → `PUT /admin/agent-flows/{flow_id}`.

Pontos críticos:

1. **Normalização de erros**  
   - A API retorna detalhes de erro no formato `{ code, message }` em `detail`.  
   - O cliente deve capturar isso e transformá‑lo em uma estrutura de erro amigável:

     ```ts
     export class AgentFlowApiError extends Error {
       code: string;

       constructor(code: string, message: string) {
         super(message);
         this.code = code;
       }
     }
     ```

   - Em `catch`, extrair `detail.code` e `detail.message` do erro HTTP e levantar `AgentFlowApiError`.

2. **Alinhamento com tipos**  
   - Respostas de sucesso devem ser diretamente tipadas como `AgentFlowConfig`.  
   - A transformação de nomes de campos (snake_case → camelCase) deve ser consistente com o resto do projeto.

Opcionalmente, extrair a lógica genérica de normalização de erros para utilitário compartilhado se já existir padrão no console.

#### 2.3. Hooks auxiliares (opcionais) — `agentFlowsHooks.ts`

Para reduzir o acoplamento entre componentes e chamadas HTTP, criar hooks como:

- `useAgentFlow(domainKey)` — cuida de:
  - carregar o fluxo com `getAgentFlowByDomain`;
  - expor estados `loading`, `error`, `data`;
  - lidar com o caso 404 (domínio sem fluxo) retornando `data = null`.

- `useSaveAgentFlow(domainKey)` — encapsula a lógica de criar vs atualizar:
  - recebe `form: AgentFlowConfigForm`;  
  - escolhe `createAgentFlow` ou `updateAgentFlow` com base na presença de `flowId`;  
  - expõe estados `saving`, `error`, `onSuccess`.

Esses hooks tornam o `AgentFlowEditor` mais focado em UX e menos em detalhes de requisição.

---

### 3. Implementação da página principal — `AgentFlowsPage.tsx`

A `AgentFlowsPage` é a porta de entrada da feature no console admin.

Responsabilidades principais:

1. **Listar domínios e status de fluxo**  
   - Usar `listAgentFlows` para exibir uma tabela simples com colunas como: domínio, número de passos, última atualização, responsável.  
   - Opcionalmente, permitir filtro por prefixo de domínio (ex.: `news.`, `markets.`).

2. **Permitir seleção/navegação até o editor**  
   - Ao clicar em um domínio, abrir o editor de fluxo daquele domínio.  
   - O padrão pode ser:
     - usar query param (`/admin/agent-flows?domain=news.politics.br`); ou
     - rota filha (`/admin/agent-flows/:domainKey`).

3. **Espelhar estado de configuração**  
   - Indicar visualmente se um domínio está:
     - sem fluxo configurado;  
     - com fluxo configurado;  
     - potencialmente com fluxo em revisão/alterado recentemente.

A página deve usar componentes do design system (tabela, toolbar, filtros) para manter consistência com o resto do console.

---

### 4. Implementação do editor — `AgentFlowEditor.tsx`

O `AgentFlowEditor` é o núcleo de UX da Wave 3.

#### 4.1. Ciclo de vida e estado

Para um `domainKey` recebido via props ou router, o editor deve:

1. Carregar o fluxo existente com `useAgentFlow(domainKey)` (ou chamada direta à API).  
2. Tratar três estados de carregamento:
   - `loading` (spinner/skeleton);
   - `notFound` (domínio sem fluxo ainda, mostrar sugestão de fluxo inicial);  
   - `loaded` (fluxo existente, mostrar passos atuais).

3. Manter no estado local:
   - lista de passos (`AgentFlowStepForm[]`), com `position`, `agentRole`, `params`;  
   - metadados em exibição somente leitura (última atualização, responsável, etc.);  
   - campo de justificativa de mudança (`changeReason`), obrigatório ao salvar.

#### 4.2. Edição da lista de passos

O editor deve permitir ao operador:

1. **Adicionar passo**  
   - botão "Adicionar passo";  
   - abre linha nova com seleção de `agentRole` e edição de `params` (pode começar como JSON simplificado);  
   - atribui `position` automaticamente no final da lista.

2. **Remover passo**  
   - ícone/botão de remoção em cada linha;  
   - opcionalmente, confirmação para evitar remoção acidental.

3. **Reordenar passos**  
   - setas para mover passo para cima/baixo;  
   - após reordenar, reindexar o campo `position` localmente;  
   - outras UX (drag & drop) podem ser deixadas para iterações futuras.

4. **Editar papel e parâmetros**  
   - `agentRole` como dropdown alimentado por enum/catálogo (para evitar valores inválidos);  
   - `params` como campo de texto JSON ou formulário de chave/valor, dependendo do escopo da S29 (v1 pode ser campo de texto com validação básica).

#### 4.3. Salvamento, erros e feedback

Ao clicar em "Salvar":

1. Verificar que `changeReason` foi preenchido.  
   - Se não estiver, bloquear envio e destacar o campo com mensagem clara.

2. Montar `AgentFlowConfigForm` com:
   - `domainKey`;  
   - `steps` (ordenados por `position`);  
   - `changeReason`.

3. Chamar `useSaveAgentFlow(domainKey)` ou a função API correspondente.

Tratamento de erros:

- Se a API lançar `AgentFlowApiError`, exibir a mensagem retornada (`message`) e, quando possível, mapear `code` para mensagem mais amigável (ex.: `DECISION_MAKER_NOT_LAST` → "O DECISION_MAKER precisa ser o último passo.").  
- Não limpar o formulário em caso de erro; permitir que o usuário ajuste e tente novamente.

Feedback de sucesso:

- Mostrar notificação de sucesso (toast ou banner) indicando que o fluxo do domínio foi atualizado;  
- atualizar metadados exibidos (última atualização, responsável).

---

### 5. Integração com router e layout admin

Para que a feature seja acessível, é necessário integrá‑la ao router e ao layout do console admin.

#### 5.1. Router

No arquivo principal de rotas do frontend admin (por exemplo, `src/routes/adminRoutes.tsx`):

- adicionar rota para a página de fluxos:

  ```tsx
  <Route path="/admin/agent-flows" element={<AgentFlowsPage />} />
  ```

- opcionalmente, permitir domínios via query/params, por exemplo:

  ```tsx
  <Route path="/admin/agent-flows/:domainKey" element={<AgentFlowsPage />} />
  ```

#### 5.2. Menu e navegação

No componente de sidebar/menu admin:

- adicionar entrada do tipo "Fluxos de agentes" (ou nome acordado), apontando para `/admin/agent-flows`;
- posicionar o item em seção coerente com outras configurações avançadas do sistema.

O objetivo é que qualquer admin consiga encontrar a feature sem precisar de instruções especiais.

---

### 6. Qualidade de frontend: lint, testes, build

A Wave 3 precisa garantir que a introdução da feature não degrada a qualidade do frontend.

#### 6.1. Testes de UI — `__tests__/AgentFlowEditor.test.tsx`

Em `frontend/inspectah-ui/src/features/agent-flows/__tests__/AgentFlowEditor.test.tsx`, criar testes que cubram:

1. **Renderização de fluxo existente**  
   - mock de `getAgentFlowByDomain` retornando fluxo com alguns passos;  
   - assert de que os passos aparecem na ordem correta.

2. **Criação de fluxo em domínio sem config**  
   - mock de 404 para `getAgentFlowByDomain`;  
   - o editor inicializa com esqueleto de passos;  
   - ao salvar, `createAgentFlow` é chamado com payload esperado.

3. **Erro de invariantes**  
   - mock de `updateAgentFlow` lançando `AgentFlowApiError("DECISION_MAKER_NOT_LAST", ...)`;  
   - assert de que mensagem correta aparece na tela;
   - o estado do formulário é preservado para correção.

4. **Obrigatoriedade de changeReason**  
   - usuário tenta salvar sem justificar;  
   - a ação é bloqueada;  
   - campo de justificativa é marcado como obrigatório.

#### 6.2. Pipeline local de qualidade

Rodar o pipeline padrão de qualidade do frontend:

```bash
cd frontend/inspectah-ui
npm run lint
npm test
npm run build
cd ../..
```

Os logs dessas execuções serão capturados como evidência de G3.

---

### 7. Script do Gate S29_G3: `bin/s29_g3_ui_and_frontend_quality.sh`

O Gate S29_G3 consolida a execução da Wave 3, garantindo que a feature de UI está saudável.

#### 7.1. Responsabilidades do script

1. Rodar `npm run lint`, `npm test` e `npm run build` para o frontend, com foco especial na feature de fluxos, mas sem quebrar o padrão global.  
2. Salvar logs dessas execuções no diretório de evidências de G3.  
3. Opcionalmente, registrar um snapshot textual da UI (por exemplo, logs de testes que comprovem a existência de componentes do fluxo).  
4. Gerar scorecard JSON com o status final.

#### 7.2. Estrutura sugerida (conceitual)

Diretórios de evidências:

- `out/evidence/S29_G3_ui_and_frontend_quality/lint.log`;  
- `out/evidence/S29_G3_ui_and_frontend_quality/test.log`;  
- `out/evidence/S29_G3_ui_and_frontend_quality/build.log`.

Scorecard:

- `out/scorecards/S29_G3_ui_and_frontend_quality.json`.

Pseudo‑bash:

```bash
EVIDENCE_DIR="out/evidence/S29_G3_ui_and_frontend_quality"
SCORECARD="out/scorecards/S29_G3_ui_and_frontend_quality.json"
mkdir -p "$EVIDENCE_DIR"

cd frontend/inspectah-ui

npm run lint | tee "../${EVIDENCE_DIR}/lint.log"
LINT_STATUS=${PIPESTATUS[0]}

npm test | tee "../${EVIDENCE_DIR}/test.log"
TEST_STATUS=${PIPESTATUS[0]}

npm run build | tee "../${EVIDENCE_DIR}/build.log"
BUILD_STATUS=${PIPESTATUS[0]}

cd ../..

STATUS="PASS"
if [ "$LINT_STATUS" -ne 0 ] || [ "$TEST_STATUS" -ne 0 ] || [ "$BUILD_STATUS" -ne 0 ]; then
  STATUS="FAIL"
fi

cat > "$SCORECARD" <<EOF
{
  "gate_id": "S29_G3",
  "status": "$STATUS",
  "checks": {
    "lint_log": "${EVIDENCE_DIR}/lint.log",
    "test_log": "${EVIDENCE_DIR}/test.log",
    "build_log": "${EVIDENCE_DIR}/build.log"
  },
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "notes": "UI de fluxo de agentes e qualidade de frontend executadas na Wave 3."
}
EOF

if [ "$STATUS" != "PASS" ]; then
  exit 1
fi
```

Rodar o gate:

```bash
bin/s29_g3_ui_and_frontend_quality.sh
```

Se `STATUS` vier como `FAIL`, a Wave 3 não está concluída — é necessário corrigir o problema (lint, teste ou build) antes de seguir para Wave 4.

---

### 8. Estado esperado ao final da Wave 3

Com a execução da Wave 3 completada e G3 em PASS, a Sprint 29 deve estar em um estado em que:

1. **A UI de fluxo de agentes existe e é utilizável**  
   - Há uma entrada no menu admin para "Fluxos de agentes";  
   - `AgentFlowsPage` lista domínios e permite escolher um para edição;  
   - `AgentFlowEditor` permite editar, salvar e visualizar fluxos de um domínio piloto.

2. **A UI conversa corretamente com a API de admin**  
   - Criações/atualizações de fluxo batem na API implementada na Wave 2;  
   - erros de invariantes aparecem para o usuário com mensagens compreensíveis;  
   - campo de justificativa de mudança é exigido para salvar.

3. **Qualidade de frontend está preservada**  
   - `npm run lint`, `npm test` e `npm run build` passam;  
   - não há warnings críticos introduzidos pela feature;  
   - os testes de `AgentFlowEditor` cobrem cenários principais (criação, edição, erro, justificativa).

Com esse cenário, a Wave 4 (runtime & observabilidade + ORR & bundle) pode começar, conectando o que o operador configurou na UI com o que o pipeline do Inspectah de fato faz com cada item de informação em produção/piloto. Esse encaixe é o foco do Bloco 5 do Capítulo 4.

