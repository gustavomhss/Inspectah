# Sprint 21.1 – Capítulo 4 (v2)

Plano de Execução – Copiloto de Fontes em modo agente

---

## 1. Objetivo operacional da Sprint 21.1

Ao final da Sprint 21.1, em ambiente local, deve ser possível:

- abrir o Console de Fontes (admin),
- clicar no widget do **Copiloto de Fontes** no canto inferior direito,
- conversar em linguagem natural (ex.: “quero cadastrar globo.com como fonte de notícias gerais do Brasil”),
- ver o **formulário de fonte** sendo preenchido com sugestões do Copiloto (tipo, categoria, temas, info types, endpoint, nome, slug, descrição),
- revisar e editar qualquer campo,
- salvar a fonte com sucesso usando o fluxo padrão do Console de Fontes,
- consultar logs, scorecards e evidências da S21.1 para auditar o comportamento do agente.

Tudo isso com o Copiloto rodando em **modo agente**, usando ferramentas explícitas, sem criar fonte sozinho, com o humano como gate final, e com gates S21_1_G0…S21_1_G8 em GO, sem quebrar nenhum gate da S21.

Este capítulo transforma a visão dos Capítulos 1, 2 e 3 em um **roteiro executável** para o Codex e para devs humanos, mantendo alinhamento direto com a ontologia e o modelo de dados da S21.

---

## 2. Mapa de fases, gates e artefatos

A execução da S21.1 é organizada em fases, cada uma alinhada a um conjunto de gates e artefatos, formando um pipeline claro de construção e validação:

- **Fase 0 – Preparação de branch e ambiente**  
  Alinha o estado do repo e do ambiente com a S21. Nenhum gate direto, mas pré-requisito para S21_1_G0.

- **Fase 1 – Documentos, modo agente e segurança**  
  Concretiza docs da S21.1, modo agente e política de segurança. Alimenta diretamente S21_1_G0 e prepara S21_1_G5.

- **Fase 2 – Backend: API do Copiloto e serviços auxiliares**  
  Cria infraestrutura da API e serviços de sessão/arquivos. Prepara S21_1_G2, S21_1_G3 e S21_1_G4.

- **Fase 3 – Agente em modo agente e ferramentas**  
  Implementa núcleo do agente e ferramentas (form_state, arquivos, logging). Fecha S21_1_G2 e parte de S21_1_G5.

- **Fase 4 – Frontend: widget, chat e integração com formulário**  
  Entrega UX e sincronização chat↔form. Fecha S21_1_G1 e S21_1_G3.

- **Fase 5 – Upload e leitura de arquivos**  
  Implementa e valida fluxo de arquivos. Fecha S21_1_G4.

- **Fase 6 – Segurança e limites de escopo**  
  Reforça prompt-base, testes de segurança e limites. Fecha S21_1_G5.

- **Fase 7 – Cenários end-to-end guiados**  
  Prova de uso real com admins. Fecha S21_1_G6.

- **Fase 8 – Scorecard, evidências e GO/NO-GO**  
  Consolida scorecards, evidências e decisão de GO/NO-GO (S21_1_G7 e S21_1_G8), revalidando a S21.

Cada fase abaixo lista: arquivos-alvo, passos sugeridos, comandos de sanity e critérios de DONE, sempre referenciando os gates do Capítulo 2 e o filemap do Capítulo 3.

---

## 3. Fase 0 – Preparação de branch e ambiente

**Objetivo**  
Garantir uma base estável da S21 e um ambiente configurado antes de tocar na S21.1.

**Arquivos impactados**  
Nenhum novo; apenas sanidade.

**Passos (local)**

1. Atualizar o repositório e garantir S21 verde.

```bash
cd /Users/gustavoschneiter/Documents/Inspectah

git checkout main
git pull

source .venv/bin/activate
export PYTHONPATH=.

# sanity da S21
.venv/bin/python -m pytest tests/sources -q
bash bin/s21_all_gates.sh
```

2. Criar branch da Sprint 21.1.

```bash
git checkout -b feature/s21_1_copiloto_fontes
```

**Critério de DONE da Fase 0**

- Testes de `tests/sources` em verde.  
- `bin/s21_all_gates.sh` concluído com todos os gates da S21 em PASS.  
- Branch `feature/s21_1_copiloto_fontes` ativa.

**Relação com gates**  
Pré-requisito para todos os gates da S21.1 e para garantir que S21 continua íntegra.

---

## 4. Fase 1 – Documentos, modo agente e segurança (S21_1_G0 + base S21_1_G5)

**Objetivo**  
Concretizar no repo os capítulos e documentos da S21.1, incluindo modo agente e política de segurança.

**Arquivos novos (docs)**

- `docs/sprint_21_1_capitulo_1.md`  
- `docs/sprint_21_1_capitulo_2_gates.md`  
- `docs/sprint_21_1_capitulo_3_filemap.md`  
- `docs/sprint_21_1_modo_agente_copiloto.md`  
- `docs/sprint_21_1_politica_seguranca_copiloto.md`  
- `docs/sprint_21_1_cenarios_copiloto_fontes.md`

**Passos sugeridos**

1. Criar os arquivos `docs/sprint_21_1_*.md` com base nos capítulos aprovados (1, 2 e 3) e nas seções de segurança e cenários.
2. Em `docs/sprint_21_1_modo_agente_copiloto.md`, garantir que estejam descritos:
   - prompt-base completo (com referências claras à ontologia e modelo de dados da S21),
   - lista de ferramentas do agente (nome, descrição, parâmetros, limites),
   - formato de entrada/saída (payloads JSON do protocolo),
   - exemplos de chamadas e respostas.
3. Em `docs/sprint_21_1_politica_seguranca_copiloto.md`, registrar:
   - o que o agente não pode fazer (sem criar fonte, sem opinar sobre verdade/fato, etc.),
   - como reage a pedidos fora de escopo,
   - postura diante de tentativas de prompt injection.
4. Em `docs/sprint_21_1_cenarios_copiloto_fontes.md`, listar os cenários que serão usados depois na Fase 7 (notícias, esportes, clima, fofoca etc.).

**Comandos de sanity**

```bash
git status
```

**Critério de DONE da Fase 1**

- Docs da S21.1 existentes, sem TODOs críticos, com modo agente e segurança claros.  
- Conteúdo suficiente para configurar o Copiloto em modo agente (Cap. 2 e Cap. 3 referenciáveis).

**Relação com gates**  
Base direta para S21_1_G0 (contexto/mode agent) e insumo de S21_1_G5 (segurança).

---

## 5. Fase 2 – Backend: API do Copiloto e serviços auxiliares (base para S21_1_G2, G3, G4)

**Objetivo**  
Criar a API do Copiloto e serviços de sessão/arquivos, respeitando o contrato JSON do Capítulo 3, ainda que com lógica stub.

**Arquivos novos/alterados**

- `inspectah/api.py` (ajuste)  
- `inspectah/routers/copiloto_fontes.py` (novo)  
- `inspectah/services/copiloto_sessions.py` (novo)  
- `inspectah/services/copiloto_files.py` (novo)

**Passos**

1. Ajustar `inspectah/api.py` para incluir o router do Copiloto com prefixo `/admin/copiloto-fontes`.
2. Criar `inspectah/routers/copiloto_fontes.py` com endpoints:
   - `POST /admin/copiloto-fontes/sessions` (criar sessão, opcional),
   - `POST /admin/copiloto-fontes/sessions/{session_id}/messages`,
   - `POST /admin/copiloto-fontes/sessions/{session_id}/files`,
   - (opcional) `GET` leve de debug.

   No início, os handlers podem retornar respostas stub, desde que respeitem o contrato de request/response.

3. Criar `inspectah/services/copiloto_sessions.py` com funções para:
   - criar e recuperar sessões,
   - registrar histórico mínimo de mensagens,
   - vincular arquivos à sessão.

4. Criar `inspectah/services/copiloto_files.py` com funções para:
   - armazenar arquivos (ex.: `out/copiloto_uploads/`),
   - expor metadados e caminho para leitura posterior.

**Comandos de sanity**

```bash
.venv/bin/python -m pytest tests -q  # tolerar falhas apenas se forem ligadas à falta de novos testes do copiloto
```

**Critério de DONE da Fase 2**

- Endpoints do Copiloto respondem com payloads JSON bem formados (mesmo stub);  
- Nenhuma regressão em endpoints existentes;
- Serviços de sessão/arquivos disponíveis para a camada de agente.

**Relação com gates**  
Base técnica para S21_1_G2 (modo agente), G3 (sync form) e G4 (arquivos).

---

## 6. Fase 3 – Agente em modo agente e ferramentas (S21_1_G2 + base S21_1_G5)

**Objetivo**  
Implementar o agente Copiloto de Fontes em modo agente, suas ferramentas e testes de modo agente, conectando router → agente.

**Arquivos novos/alterados**

- `inspectah/agents/__init__.py`  
- `inspectah/agents/s21_1_copiloto_fontes.py`  
- `inspectah/agents/tools/form_state.py`  
- `inspectah/agents/tools/file_reader.py`  
- `inspectah/agents/tools/logging.py`  
- `tests/agents/test_s21_1_copiloto_mode_agent.py`

**Passos**

1. Em `inspectah/agents/s21_1_copiloto_fontes.py`, implementar:
   - `get_copiloto_agent(config)` lendo docs da S21.1 para montar o prompt-base;
   - registro das ferramentas (`tool_read_form_state`, `tool_suggest_field_values`, `tool_read_file_content`, `tool_log_interaction`);
   - `run_copiloto_interaction(...)` que recebe `session_id`, `user_message`, `form_state`, `files` e devolve `assistant_message` + `actions`.

2. Em `inspectah/agents/tools/form_state.py`, implementar funções para:
   - validar/normalizar `form_state`;
   - mapear tipos/categorias/temas para a ontologia S21;
   - garantir que o agente não veja campos fora do contexto de fonte.

3. Em `inspectah/agents/tools/file_reader.py`, conectar com `copiloto_files` para obter conteúdo textual (com limites e tratamento de erro).

4. Em `inspectah/agents/tools/logging.py`, criar logging estruturado de uso de ferramentas.

5. Ajustar `inspectah/routers/copiloto_fontes.py` para chamar `run_copiloto_interaction` ao receber mensagens.

6. Criar `tests/agents/test_s21_1_copiloto_mode_agent.py` com testes de:
   - criação do agente;
   - chamada de exemplo com `form_state` mínimo;
   - resposta no formato esperado (mensagem + actions).

**Comandos de sanity**

```bash
.venv/bin/python -m pytest tests/agents/test_s21_1_copiloto_mode_agent.py -q
```

**Critério de DONE da Fase 3**

- Agente configurado em modo agente com ferramentas explícitas;  
- Router do Copiloto devolve ações estruturadas coerentes;
- Testes de modo agente passando.

**Relação com gates**  
Fecha S21_1_G2 (modo agente) e prepara S21_1_G5 (segurança).

---

## 7. Fase 4 – Frontend: widget, chat e sincronização com formulário (S21_1_G1 + S21_1_G3)

**Objetivo**  
Entregar a experiência visual do Copiloto e conectá-la ao formulário de fonte.

**Arquivos novos/alterados**

- `frontend/inspectah-ui/src/modules/admin/components/CopilotoWidget.tsx`  
- `frontend/inspectah-ui/src/modules/admin/components/CopilotoChatPanel.tsx`  
- `frontend/inspectah-ui/src/modules/admin/components/CopilotoMessageList.tsx`  
- `frontend/inspectah-ui/src/modules/admin/components/CopilotoInputBar.tsx`  
- `frontend/inspectah-ui/src/modules/admin/components/CopilotoFileAttachment.tsx`  
- `frontend/inspectah-ui/src/modules/admin/hooks/useCopilotoAgent.ts`  
- `frontend/inspectah-ui/src/modules/admin/hooks/useFonteFormState.ts` (ou equivalente)  
- `frontend/inspectah-ui/src/modules/admin/api/copilotoClient.ts`  
- `frontend/inspectah-ui/src/modules/admin/pages/AdminSourceFormPage.tsx` (ajuste)  
- possivelmente `AdminSourcesPage.tsx` (exibir widget também)

**Passos**

1. Implementar `copilotoClient.ts` com funções tipadas para `sendMessage` e `uploadFile` seguindo o protocolo JSON.
2. Implementar `useCopilotoAgent.ts` para gerenciar sessão, enviar mensagens, receber respostas e expor `actions`.
3. Estender `useFonteFormState.ts` para aplicar ações (`set_field`, `clear_field`, `mark_suggested`) e manter flags de sugestão.
4. Implementar UI do widget (botão flutuante) e painel de chat, garantindo que o formulário permaneça visível e utilizável.
5. Integrar o widget em `AdminSourceFormPage.tsx`, passando `form_state` e callbacks apropriados.
6. Criar testes de frontend básicos para widget e painel (renderização, abertura/fechamento, envio de mensagem).

**Comandos de sanity**

```bash
cd frontend/inspectah-ui
npm install  # se necessário
npm run lint
npm test
npm run build
```

**Critério de DONE da Fase 4**

- Widget visível nas telas relevantes;  
- Chat funcional, enviando mensagens para o backend e recebendo respostas;  
- Formulário sendo atualizado por `actions` do Copiloto;  
- Lint/test/build do front em verde.

**Relação com gates**  
Fecha S21_1_G1 (UX) e S21_1_G3 (sincronização chat↔formulário).

---

## 8. Fase 5 – Upload e leitura de arquivos (S21_1_G4)

**Objetivo**  
Permitir que o admin anexe arquivos no chat e que o Copiloto use o conteúdo para sugerir campos.

**Arquivos impactados**

- `inspectah/services/copiloto_files.py`  
- `inspectah/agents/tools/file_reader.py`  
- `inspectah/agents/s21_1_copiloto_fontes.py` (integração)  
- `frontend/inspectah-ui/src/modules/admin/components/CopilotoFileAttachment.tsx`  
- `frontend/inspectah-ui/src/modules/admin/hooks/useCopilotoAgent.ts`  
- `tests/agents/test_s21_1_copiloto_mode_agent.py` (ampliado)  
- `tests/agents/test_s21_1_copiloto_files.py` (novo, recomendado)

**Passos**

1. Finalizar fluxo de upload (front/back) e registrar `file_id` na sessão.
2. Implementar extração de texto em `file_reader.py` para PDF e texto plano, com limites.
3. Integrar no agente (via `tool_read_file_content`), fazendo o conteúdo alimentar `tool_suggest_field_values`.
4. Criar testes cobrindo upload, leitura de conteúdo e uso desse conteúdo nas sugestões.

**Comandos de sanity**

```bash
.venv/bin/python -m pytest tests/agents -q
```

**Critério de DONE da Fase 5**

- Arquivos anexados via chat influenciam sugestões do Copiloto;  
- Testes de agentes (incluindo arquivos) em verde.

**Relação com gates**  
Fecha S21_1_G4 (arquivos).

---

## 9. Fase 6 – Segurança e limites de escopo (S21_1_G5)

**Objetivo**  
Blindar o Copiloto contra uso indevido, reforçando limites de escopo e comportamento seguro.

**Arquivos impactados**

- `docs/sprint_21_1_politica_seguranca_copiloto.md`  
- `docs/sprint_21_1_modo_agente_copiloto.md`  
- `inspectah/agents/s21_1_copiloto_fontes.py` (prompt-base)  
- `tests/agents/test_s21_1_copiloto_safety.py`

**Passos**

1. Revisar e ajustar prompt-base para reforçar regras de segurança (sem criar fonte, escopo restrito, recusa de perguntas sobre verdade/fato, etc.).
2. Criar/ajustar `tests/agents/test_s21_1_copiloto_safety.py` com cenários de prompt injection, pedidos para burlar validações e inputs fora de domínio.
3. Ajustar a implementação até que os testes passem, garantindo respostas seguras e consistentes.

**Comandos de sanity**

```bash
.venv/bin/python -m pytest tests/agents/test_s21_1_copiloto_safety.py -q
```

**Critério de DONE da Fase 6**

- Agente recusa corretamente operações proibidas;  
- Testes de segurança em verde;  
- Docs de segurança e modo agente sincronizados com o comportamento real.

**Relação com gates**  
Fecha S21_1_G5 (segurança).

---

## 10. Fase 7 – Cenários end-to-end guiados (S21_1_G6)

**Objetivo**  
Validar, na prática, que admins conseguem cadastrar fontes reais apenas conversando com o Copiloto + revisando o formulário.

**Arquivos impactados**

- `docs/sprint_21_1_cenarios_copiloto_fontes.md`  
- `scripts/s21_1_run_cenario_*.py` (opcional)  
- `out/evidence/S21_1_G6_cenarios/` (gerado)

**Passos**

1. Detalhar no doc cada cenário (notícias gerais, esportes, clima, fofoca, outro tipo Fase 1) com:
   - frase inicial de intenção;  
   - passos esperados do agente;  
   - estado final esperado da fonte.

2. Executar os cenários manualmente via UI (admin + Copiloto) e/ou via scripts que simulam chamadas HTTP para o backend.

3. Registrar logs de sessão (mensagens trocadas) e dumps de fontes criadas em `out/evidence/S21_1_G6_cenarios/`.

4. Garantir que pelo menos uma pessoa fora do squad 21.1 execute ao menos um cenário completo (feedback anotado no scorecard).

**Comandos de sanity (exemplos)**

```bash
# Exemplo de execução de script de cenário (se implementado)
python scripts/s21_1_run_cenario_1_noticias.py > out/evidence/S21_1_G6_cenarios/cenario_1.log
```

**Critério de DONE da Fase 7**

- Todos os cenários documentados executados com sucesso;  
- Logs e fontes criadas armazenados em evidência;  
- Feedback externo registrado em `docs/sprint_21_1_scorecard_copiloto_fontes.md`.

**Relação com gates**  
Fecha S21_1_G6 (cenários guiados).

---

## 11. Fase 8 – Scorecard, evidências e GO/NO-GO (S21_1_G0…G8)

**Objetivo**  
Consolidar tudo em scorecards, evidências e script de decisão GO/NO-GO, revalidando também a S21.

**Arquivos novos/alterados**

- `bin/s21_1_all_gates.sh`  
- `bin/s21_1_g0_contexto.sh`  
- `bin/s21_1_g1_ux_widget.sh`  
- `bin/s21_1_g2_agent_mode.sh`  
- `bin/s21_1_g3_sync_form.sh`  
- `bin/s21_1_g4_files.sh`  
- `bin/s21_1_g5_safety.sh`  
- `bin/s21_1_g6_cenarios.sh`  
- `bin/s21_1_g7_scorecard.sh`  
- `bin/s21_1_g8_go_no_go.sh`  
- `docs/sprint_21_1_scorecard_copiloto_fontes.md`  
- `docs/sprint_21_1_wrap_execucao.md`  
- `out/scorecards/S21_1_G*_*.json` (gerados)  
- `out/evidence/S21_1_G*_*/` (gerados)

**Passos**

1. Implementar scripts `bin/s21_1_gX_*.sh`, cada um rodando os comandos de validação da sua fase e escrevendo scorecards + evidências.
2. Implementar `bin/s21_1_all_gates.sh` para orquestrar G0…G7.
3. Implementar `bin/s21_1_g8_go_no_go.sh` para ler scorecards anteriores e produzir decisão final.
4. Preencher `docs/sprint_21_1_scorecard_copiloto_fontes.md` com métricas (M1–M5 do Cap. 2) e análise qualitativa.
5. Preencher `docs/sprint_21_1_wrap_execucao.md` com resumo executivo, riscos restantes e ponte para S22.

**Comandos de sanity**

```bash
# testes gerais
.venv/bin/python -m pytest tests -q

# gates da S21.1
bash bin/s21_1_all_gates.sh
bash bin/s21_1_g8_go_no_go.sh

# revalidar S21
bash bin/s21_all_gates.sh
```

**Critério de DONE da Fase 8**

- `bin/s21_1_all_gates.sh` com todos os gates G0…G7 em PASS;  
- `bin/s21_1_g8_go_no_go.sh` gerando decisão GO em `S21_1_G8_go_no_go.json`;  
- Scorecard textual e wrap da S21.1 completos;  
- `bin/s21_all_gates.sh` permanecendo verde após as mudanças.

**Relação com gates**  
Fecha S21_1_G7 (scorecard) e S21_1_G8 (GO/NO-GO), garantindo que a S21 siga íntegra.

---

## 12. Encerramento da Sprint 21.1

A Sprint 21.1 é considerada **DONE e GO** quando:

1. O Copiloto de Fontes funciona em modo agente no admin, com widget, chat, leitura de arquivos e sincronização com o formulário de fontes.
2. Admins conseguem cadastrar fontes reais dos tipos da Fase 1 apenas conversando com o Copiloto e revisando o formulário.
3. Todos os gates S21_1_G0…S21_1_G8 estão em PASS (ou PASS_WITH_RISKS com mitigação clara e aceita) e registrados em `out/scorecards/`.
4. Os gates da S21 continuam em GO após integração (nenhuma regressão do Console de Fontes).
5. Scorecard e wrap da S21.1 descrevem claramente o estado final e apontam para os próximos passos (S22 e além).

Com este plano v2, a execução da Sprint 21.1 deixa de ser um conjunto de "tarefas soltas" e vira um pipeline disciplinado: cada fase tem dono, arquivos, comandos, gates e evidências, mantendo o Copiloto de Fontes alinhado ao DNA do Inspectah e pronto para o modo agente agora e na evolução futura.

