# Sprint 29 — Capítulo 3
## Bloco 4 — Arquitetura de frontend: UI de fluxo de agentes

Com o domínio de fluxo de agentes e a API de admin bem definidos nos blocos anteriores, este Bloco 4 detalha **como o frontend do Inspectah expõe essa capacidade para o operador humano**.

A UI de fluxo de agentes é a ponte entre:

- decisões de produto e políticas editoriais ("para este domínio, quero fluxo mais rígido");
- contratos de backend (API de admin e invariantes);
- experiência prática de configurar, entender e revisar fluxos por domínio.

---

### 1. Princípios de design da UI de fluxo

A UI da S29 segue alguns princípios explícitos:

1. **Fluxo como linha do tempo legível**  
   O operador enxerga a sequência de papéis como uma linha de passos ordenados, não como um formulário genérico de JSON.

2. **Feedback imediato de validade**  
   O usuário não deve descobrir que o fluxo é inválido só após tentar salvar e receber um erro obscuro. A UI busca antecipar erros, e quando o backend recusa, apresenta mensagens claras.

3. **Simples na v1, poderosa no futuro**  
   Nesta v1, o foco é um editor linear simples, sem branching complexo, mas o layout e o código são projetados para suportar evoluções (condições, ramificações, versões) nas próximas fases do Épico E28.

4. **Alinhada ao design system do console admin (S26)**  
   A UI reutiliza componentes existentes (tabelas, botões, inputs, tooltips) para manter consistência visual e reduzir atrito de uso.

5. **Auditabilidade explícita**  
   Alterar fluxo não é um clique trivial; a UI exige uma justificativa (motivo da mudança) e exibe metadados básicos (quem alterou, quando, por quê).

---

### 2. Localização e estrutura da feature no frontend

A feature da Sprint 29 vive em:

- `frontend/inspectah-ui/src/features/agent-flows/`

Estrutura sugerida de arquivos:

- `AgentFlowsPage.tsx` — página principal da feature (entrada via menu admin).
- `AgentFlowEditor.tsx` — editor linear de fluxo para um domínio específico.
- `agentFlowsApi.ts` — cliente de API tipado para falar com os endpoints de backend.
- `agentFlowsTypes.ts` — tipos TypeScript que espelham `AgentFlowConfigIn/Out` e `AgentFlowStepIn/Out`.
- `agentFlowsHooks.ts` (opcional) — hooks como `useAgentFlow` e `useSaveAgentFlow`.
- `__tests__/AgentFlowEditor.test.tsx` — testes de UI da feature.

Essa organização evita espalhar lógica de fluxo por pastas genéricas e torna a feature encontrável.

---

### 3. `AgentFlowsPage.tsx` — página de entrada da feature

A `AgentFlowsPage` é a porta de entrada para a configuração de fluxos via UI. Responsabilidades principais:

1. **Seleção de domínio**  
   - renderizar um seletor de `domain_key` (dropdown, search box ou tabela filtrável);  
   - permitir escolher rapidamente domínios já configurados e domínios elegíveis.

2. **Visão geral de configuração**  
   - exibir lista de domínios com status (por exemplo, "configurado" / "não configurado" / "em revisão");  
   - mostrar metadados de fluxo (última atualização, responsável, resumo do número de passos).

3. **Entrada no editor**  
   - ao selecionar um domínio, abrir `AgentFlowEditor` embutido na página ou em rota filha (ex.: `/admin/agent-flows?domain=news.politics.br`).

A página utiliza `agentFlowsApi.ts` para listar fluxos existentes (`GET /admin/agent-flows`) e para verificar se um domínio possui fluxo ativo.

---

### 4. `AgentFlowEditor.tsx` — editor linear de fluxo

O `AgentFlowEditor` é o núcleo da UX da S29.

#### 4.1. Estado principal

Para um `domainKey` selecionado, o editor gerencia:

- estado de carregamento inicial do fluxo (`loading`, `error`);  
- estrutura de passos em memória (lista ordenada com `position`, `agent_role`, `params`);  
- metadados do fluxo (quem criou, quem atualizou, timestamps);  
- campo de justificativa da mudança (`changeReason`).

A fonte da verdade são os dados vindos de:

- `GET /admin/agent-flows/by-domain/{domain_key}` (quando fluxo existe);
- fallback para "fluxo novo" (quando não existe) com uma sugestão inicial de papéis (por exemplo, `INTERPRETER → CLASSIFIER → DECISION_MAKER`) apenas como rascunho local até salvar.

#### 4.2. Interações principais

O editor oferece, no mínimo:

1. **Adicionar passo**  
   - botão "Adicionar passo" que abre um pequeno formulário/linha;  
   - seleção de papel (`agent_role`) a partir de dropdown populado com catálogo de papéis;  
   - edição opcional de `params` via UI simples (campo JSON editável ou chave/valor, dependendo do escopo da S29).

2. **Remover passo**  
   - botão de remoção em cada linha;  
   - confirmação opcional para evitar exclusões acidentais.

3. **Reordenar passos**  
   - setas para mover passo para cima/baixo ou drag & drop simples;  
   - após reordenação, o estado local reindexa as `position`.

4. **Editar papel e parâmetros**  
   - dropdown de `agent_role` e campos de `params` editáveis;  
   - opcionalmente, destacar visualmente papéis especiais como `DECISION_MAKER` e `DEBUNKER`.

5. **Salvar fluxo**  
   - botão "Salvar" que:  
     - exige preenchimento de `changeReason` (campo obrigatório quando houver alterações);  
     - chama `updateAgentFlow` ou `createAgentFlow` via `agentFlowsApi`;
     - exibe indicador de loading durante a chamada;
     - na volta, mostra feedback de sucesso ou erros vindos do backend.

#### 4.3. UX para erros de validação

Quando o backend retorna um erro de validação (`HTTP 422` com `code` de `AgentFlowValidationError`), o editor deve:

- exibir mensagem clara no topo ou em toast (ex.: "Fluxo inválido: DECISION_MAKER só pode aparecer no final.");
- opcionalmente, destacar a linha/posição problemática (por exemplo, pintar o passo com erro);
- não perder o estado atual do formulário (o usuário corrige e tenta novamente).

Esse comportamento exige que o `agentFlowsApi` preserve o `code` e o `message` vindos do backend.

---

### 5. `agentFlowsApi.ts` — cliente de API da feature

O módulo `agentFlowsApi.ts` encapsula o diálogo com o backend:

Funções típicas:

- `listAgentFlows(params)`: usa `GET /admin/agent-flows` para buscar configs para a tabela da página principal.
- `getAgentFlowByDomain(domainKey)`: usa `GET /admin/agent-flows/by-domain/{domain_key}`.
- `createAgentFlow(payload)`: usa `POST /admin/agent-flows`.
- `updateAgentFlow(flowId, payload)`: usa `PUT /admin/agent-flows/{flow_id}`.

Esse módulo também é responsável por:

- mapear o payload do backend para tipos TS definidos em `agentFlowsTypes.ts`;
- converter erros HTTP (`HTTP 422` com `detail.code`) em objetos de erro mais amigáveis para a UI;
- manter a base URL e headers de autenticação de acordo com a infraestrutura do console admin.

Exemplo conceitual de tratamento de erro:

```ts
try {
  const res = await httpClient.put<AgentFlowConfigOut>(`/admin/agent-flows/${flowId}`, payload);
  return res.data;
} catch (err) {
  const apiError = normalizeApiError(err);
  // apiError.detail?.code, apiError.detail?.message
  throw new AgentFlowApiError(apiError.detail?.code, apiError.detail?.message);
}
```

Assim, o `AgentFlowEditor` pode distinguir facilmente entre erros de rede, de autenticação e de invariantes de fluxo.

---

### 6. `agentFlowsTypes.ts` e hooks auxiliares

`agentFlowsTypes.ts` declara tipos TS alinhados aos schemas Pydantic:

- `AgentFlowStep` — espelha `AgentFlowStepOut`.
- `AgentFlowConfig` — espelha `AgentFlowConfigOut`.
- `AgentFlowConfigForm` — espelha `AgentFlowConfigIn` + `changeReason`.

Hooks em `agentFlowsHooks.ts` (opcional, mas recomendado) podem encapsular padrões de uso:

- `useAgentFlow(domainKey)` — carrega o fluxo, gerencia loading/erro, expõe métodos para atualizar o estado local.
- `useSaveAgentFlow(domainKey)` — orquestra `create` vs `update`, incluindo tratamento de `changeReason` e feedback de sucesso.

Isso reduz acoplamento entre o `AgentFlowEditor` e detalhes de chamada de API.

---

### 7. Integração com o router e o layout admin

A UI de fluxo é integrada ao router principal do console admin, adicionando rota(s):

- `/admin/agent-flows` → `AgentFlowsPage`.

Opcionalmente, o domínio pode ser endereçado via query param ou rota filha:

- `/admin/agent-flows?domain=news.politics.br`;
- `/admin/agent-flows/:domainKey`.

A página utiliza o layout padrão admin (sidebar, header, breadcrumbs) e adiciona uma entrada de menu, por exemplo "Fluxos de agentes" ou equivalente, sob a seção de configurações avançadas.

---

### 8. Testes de UI da feature

Os testes de UI em `__tests__/AgentFlowEditor.test.tsx` cobrem os fluxos críticos:

1. **Renderização de fluxo existente**  
   - simula `getAgentFlowByDomain` retornando fluxo com 3 passos;  
   - verifica que a UI renderiza os passos na ordem correta.

2. **Criação de fluxo novo**  
   - simula domínio sem fluxo;  
   - usuário adiciona alguns passos e clica em "Salvar";  
   - teste verifica que `createAgentFlow` foi chamado com payload coerente.

3. **Atualização com invariantes violadas**  
   - simula backend retornando erro `DECISION_MAKER_NOT_LAST`;  
   - teste verifica que a mensagem correta aparece para o usuário.

4. **Edição de `changeReason` obrigatória**  
   - usuário tenta salvar alterações sem justificar;  
   - teste verifica que a UI bloqueia o envio e destaca o campo de justificativa.

Esses testes complementam os gates S29_G2 e S29_G3, garantindo que a UI de fato usa a API como pretendido e respeita os contratos.

---

### 9. Amarração do Bloco 4

Este Bloco 4 fixa a arquitetura da UI de fluxo de agentes:

- a feature vive em `src/features/agent-flows/`, com página, editor, cliente de API, tipos e testes bem separados;
- `AgentFlowsPage` organiza a entrada e a visão macro por domínio;
- `AgentFlowEditor` oferece um editor linear, simples e auditável para o fluxo;
- `agentFlowsApi` e `agentFlowsTypes` garantem tipagem e tratamento de erro decente;
- testes de UI verificam que as interações críticas funcionam e que as mensagens de erro fazem sentido.

Com domínio (Bloco 2), API (Bloco 3) e UI (Bloco 4) bem desenhados, o próximo bloco do Capítulo 3 pode descrever a **integração de runtime e observabilidade**, fechando o ciclo "configuração → execução → evidência" que a S29 precisa entregar.