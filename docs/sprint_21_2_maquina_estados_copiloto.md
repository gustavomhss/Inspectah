# Sprint 21.2 — Máquina de Estados do Copiloto de Fontes v2

FSM conversacional que guia criação, edição e status de fontes. Esta FSM estende o comportamento da S21.1 (chat + tools) sem alterar o contrato base de entrada/saída: mensagens + snapshot de formulário + actions estruturadas para a UI.

## 1. Estados principais (criação)

1. **escolher_tipo**
   - Objetivo: identificar tipo da fonte (notícias, clima/esportes/fofoca, oficial aberta).
   - Entradas típicas: pergunta “que tipo de fonte vamos cadastrar?”.
   - Saída: define `source_type` no session state e avança.

2. **coletar_dados_iniciais**
   - Pergunta o que o admin já sabe: URL base, descrição, temas, info_types.
   - Pode usar file_reader se arquivos foram enviados.

3. **preencher_lacunas**
   - Sugere campos ausentes (endpoint, formatos, auth, refresh_interval) conforme o tipo.
   - Usa heurísticas específicas: notícias (RSS/HTML), clima/esportes (API/RSS), oficial aberta (HTML/PDF/CSV manual).

4. **revisar**
   - Consolida ações de preenchimento (actions de `fill_form`), destacando campos sugeridos.
   - Garante que refresh_interval está presente.

5. **pronto_para_salvar**
   - Devolve lista de ações a serem confirmadas na UI; reforça que salvar é humano.
   - Em `agent_mode=on`, pode propor valores default; em `off`, apenas orienta.

## 2. Estados principais (edição)

1. **carregar_fonte_existente**
   - Usa tool `source_reader` para snapshot do `source_id` atual.
   - Valida se o tipo está suportado.

2. **planejar_update**
   - Admin pede ajustes (temas, endpoint, refresh, descrição).
   - Tool `update_planner` produz antes/depois e ações de `propose_update`.

3. **revisar_update**
   - Mensagem resume diff, pede confirmação e sinaliza campos críticos.
   - Respeita `agent_mode` (on: mais sugestões; off: apenas lista mudanças pedidas).

4. **pronto_para_salvar_update**
   - Actions estruturadas para UI aplicar via endpoint de update após aprovação humana.

## 3. Estados principais (status)

1. **planejar_status**
   - Lê estado atual e intenção (aprovar/ativar, suspender, desativar, reativar).
   - Consulta tabela de transições do domínio; se inválida, recusa e explica.

2. **revisar_status**
   - Usa `status_planner` para gerar action `propose_status_change` com justificativa.
   - Em `agent_mode=on`, sugere motivo padronizado; em `off`, pede motivo ao admin.

3. **pronto_para_alterar_status**
   - Retorna plano para UI; execução real ocorre apenas após confirmação.

## 4. Transições válidas (alto nível)

- escolher_tipo → coletar_dados_iniciais (sempre).
- coletar_dados_iniciais → preencher_lacunas (quando já há dados mínimos).
- preencher_lacunas → revisar (quando campos obrigatórios cobertos ou agent sugere defaults).
- revisar → pronto_para_salvar (quando admin sinaliza seguir ou agent_mode on preenche com confirmação).
- carregar_fonte_existente → planejar_update (snapshot carregado).
- planejar_update → revisar_update → pronto_para_salvar_update (quando diff existe).
- planejar_status → revisar_status → pronto_para_alterar_status (quando transição é permitida).
- Qualquer estado pode voltar para coletar_dados_iniciais/preencher_lacunas se o admin trouxer novas informações.

## 5. Variação por tipo de fonte

- **Notícias**: sugere RSS ou página HTML principal; refresh_interval alinhado a frequência de atualização do site; enfatiza temas/info_types.
- **Clima/Esportes/Fofoca**: sugere endpoint API/RSS e parâmetros; reforça info_types; refresh_interval tende a ser menor que notícias.
- **Oficial aberta**: foca em órgão emissor, página oficial, formato disponível; não promete scraping automático; refresh_interval conservador.

## 6. Restrições e segurança aplicadas na FSM

- Nunca aplicar criação/edição/status automaticamente; sempre devolver actions para a UI.
- Fora de escopo (verdades/fatos, Debunker, timelines, usuários) → recusa imediata e mantém estado.
- Logs críticos: transições de status e tratamento de oficiais abertas devem registrar decisão e motivo via tool de logging.

## 7. Sincronização com session/agent_mode

- `agent_mode=on`: mais proativo (preenche campos faltantes, sugere refresh), mas sempre com confirmação humana.
- `agent_mode=off`: atua como consultor, não executa tools destrutivas automaticamente, pede mais confirmação textual.
- A sessão persiste estado da FSM, tipo da fonte, agent_mode e source_id (quando em edição) para reanexar na UI.

## 8. Traço com testes/gates

- test_s21_1_copiloto_mode_agent.py: garante compatibilidade de modo agente.
- test_s21_2_copiloto_flows.py: percorre trilhas de criação/edição/status.
- test_s21_2_copiloto_safety.py: valida recusas e limites de escopo.
- G2/G5/G6 avaliam aderência entre esta FSM e o código.
