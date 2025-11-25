# Sprint 21.2 — Arquitetura do Copiloto GPT v3.2 (Agente GPT)

## 0. "Powered by ChatGPT"
- O Copiloto é um agente LLM especializado, **powered by ChatGPT**, usando o mesmo cliente LLM já adotado em outros módulos (padrão `inspectah/normalizer/client_ai.py`).
- Entrada do agente GPT:
  - contexto estruturado da sessão (create/edit/status), form_state, source_id, agent_mode, histórico curto;
  - resultados de tools determinísticas (form_state validator, heurísticas, status_planner, update_planner, file_reader);
  - instruções de sistema rígidas (persona, escopo, proibições).
- Saída do agente GPT:
  - texto natural em português, técnico-amigável;
  - lista de ACTIONS estruturadas para o front aplicar no formulário/controles;
  - nunca aplica efeitos reais; confirmação é humana.

## 1. Camadas da arquitetura

### Camada 1 — Context Builder
- Snapshot JSON: operação (create/edit/status), form_state normalizado, source_id, agent_mode, histórico curto de mensagens, metadados (URL detectada, tipo inferido, candidatos de feed).
- Alimenta o prompt do GPT.

### Camada 2 — Tools determinísticas
- form_state: normaliza/valida conforme ontologia S21/S21.2.
- source_reader: lê fonte existente e converte para form_state.
- status_planner: planeja transições válidas de status (sem aplicar).
- update_planner: diffs antes/depois para edição.
- file_reader: extrai trechos básicos de anexos.
- source_heuristics: extrai URLs, infere tipo provável, sugere endpoint e candidatos de feed (rss, rss.xml, feed, feeds, rss/ultimas), temas/info_types e refresh_interval por tipo.

### Camada 3 — LLM Orchestrator (Agente GPT)
- System prompt forte (persona Copiloto GPT, escopo fontes incluindo data_api, safety).
- Prompt = system + context + history + user.
- Resposta sempre no contrato message + actions; em falha, mensagem amigável e zero actions.

### Camada 4 — FSM de conversa
- Estados: INTRO, DISCOVER, CONSULTOR, AUTOFILL, ASK_MISSING, REVIEW, STATUS_PLANNING, EDITAR_EXISTENTE, DONE.
- CONSULTOR responde dúvidas conceituais/táticas (ex.: o que é endpoint, como achar RSS) antes de retomar o preenchimento.
- Fluxo tolera entrada rica e evita etapas redundantes.

### Camada 5 — Segurança do agente
- Escopo estrito: cadastro/edição/status de fontes.
- Recusar fora de domínio/prompt injection.
- Nunca afirmar aplicação automática; confirmação é humana.

## 2. Contrato de resposta para o frontend
Formato padrão retornado pelo backend (compatível com `assistant_message` legado):

```json
{
  "session_id": "...",
  "message": "texto natural para o admin",
  "assistant_message": "texto natural (backcompat)",
  "actions": [
    {"type": "SET_FIELD", "field": "endpoint", "value": "https://..."},
    {"type": "SUGGEST_FIELD", "field": "themes", "value": ["politica", "economia"]},
    {"type": "FOCUS_FIELD", "field": "endpoint"},
    {"type": "PLAN_STATUS", "from": "PROPOSED", "to": "ACTIVE", "reason": "aprovar"}
  ]
}
```

## 3. Modo Consultor GPT
- Agente pode permanecer alguns turnos apenas respondendo dúvidas e sugerindo estratégias práticas (procurar RSS/feed no código, testar /rss, /feed, buscar páginas de API/Dados Abertos), sem pressionar o preenchimento.
- Depois volta ao fluxo de AUTOFILL/ASK_MISSING/REVIEW quando houver dados novos.

## 4. Observabilidade básica
- Registrar chamadas de tools e decisões críticas (status_planner, update_planner) em logging do agente, sem dados sensíveis.
- Evidências de safety e planos de status/edição continuam em `out/evidence/S21_2_G*` via scripts de gate.
