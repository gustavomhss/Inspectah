# Sprint 21.1 – Capítulo 3 (v2)

Arquitetura e Filemap do Copiloto de Fontes em modo agente

---

## 1. Papel deste capítulo

Este capítulo descreve, com precisão cirúrgica, **como** o Copiloto de Fontes (Sprint 21.1) se encaixa na arquitetura do Inspectah e **onde** cada peça vive no repositório. Ele é o mapa oficial para o Codex e para qualquer dev que precise:

- entender a posição do Copiloto dentro do Console de Fontes (S21);
- saber quais arquivos criar/alterar no backend, frontend e camada de agentes;
- enxergar claramente o protocolo de modo agente (contratos de entrada/saída, ferramentas, limites);
- conectar a implementação aos gates, scorecards e evidências definidos no Capítulo 2.

Nada de lógica difusa: cada responsabilidade tem um lugar, cada lugar tem um arquivo, e cada arquivo está vinculado a um gate.

---

## 2. Visão geral da arquitetura

### 2.1. Contexto com a S21

A S21 já entregou o **Console de Fontes**:

- modelo de dados consolidado (`app/sources/models.py`, `migrations/0002_s21_sources_schema.py`, `0003_s21_sources_seed_examples.py`),
- serviços (`app/sources/service.py`, `app/sources/healthcheck.py`, `app/sources/validators.py`),
- rotas admin (`app/sources/routes_admin.py` + integração em `inspectah/api.py`),
- UI de admin de fontes (`frontend/inspectah-ui/src/modules/admin/pages/AdminSourceFormPage.tsx`, `AdminSourcesPage.tsx`, etc.),
- gates S21_G0…S21_G8 em GO.

A Sprint 21.1 **não mexe** nesses alicerces. Ela adiciona uma camada de inteligência assistida, ao lado do Console de Fontes, composta por:

- um widget de chat no frontend do admin,
- um backend de orquestração do Copiloto,
- um agente configurado em modo agente com ferramentas explícitas,
- scripts de gates e evidências para garantir qualidade.

### 2.2. Camadas envolvidas

1. **Frontend (Admin / Console de Fontes)**  
   - Exibe o widget do Copiloto de Fontes no canto inferior direito;  
   - mantém o formulário de fonte como fonte de verdade;  
   - aplica as ações sugeridas pelo agente ao estado do formulário e destaca visualmente os campos sugeridos.

2. **Backend (API de Copiloto + serviços auxiliares)**  
   - expõe endpoints para conversar com o Copiloto (`/admin/copiloto-fontes`),
   - recebe mensagens, snapshots de formulário e metadados,
   - lida com uploads de arquivo e extração de texto,
   - chama o agente em modo agente e devolve resposta + ações estruturadas.

3. **Camada de agentes (modo agente)**  
   - define o agente Copiloto de Fontes, seu prompt-base e ferramentas,
   - implementa o protocolo de entrada/saída,
   - garante que o agente só veja o que precisa (form_state, arquivos, contexto) e só possa agir via ferramentas declaradas.

4. **Infra de gates, scorecards e evidências**  
   - scripts `bin/s21_1_g*.sh` para gates S21_1_G0…S21_1_G8,
   - estrutura `out/scorecards/` e `out/evidence/` para registrar tudo.

### 2.3. Princípios de arquitetura

1. **Isolamento do agente**  
   O Copiloto de Fontes vive em módulos de agente dedicados. Ele conhece a ontologia S21 e a forma de um `form_state`, mas **não fala direto com o banco** e não chama rotas de criação de fonte. Toda operação persistente continua passando pelo fluxo padrão de admin.

2. **Formulário como verdade operacional**  
   O formulário de fonte é a verdade em tempo real. O agente só sugere patches; quem decide salvar é o humano via UI. O backend trata o Copiloto como um serviço de sugestão, não como atalho para criar fontes.

3. **Contratos claros e estáveis**  
   O protocolo frontend → backend e backend → agente é definido em JSON estável (tipado no front), com testes garantindo que mudanças sejam detectadas cedo.

4. **Modo agente de primeira classe**  
   O Copiloto é desenhado desde o início para rodar em modo agente, com um conjunto pequeno de ferramentas e logs estruturados de uso. Fica pronto para ser orquestrado em fluxos futuros (por exemplo, revisão em lote de fontes) sem reescrever a lógica central.

5. **Nenhuma regressão na S21**  
   Scripts e docs da S21 continuam rodando após a S21.1; mudanças são aditivas e compatíveis.

---

## 3. Filemap – Documentação

Toda a documentação da Sprint 21.1 fica em `docs/`, espelhando o padrão da S21.

- `docs/sprint_21_1_capitulo_1.md`  
  Visão, contexto, escopo e objetivos do Copiloto de Fontes.

- `docs/sprint_21_1_capitulo_2_gates.md`  
  Gates S21_1_G0…S21_1_G8, métricas, critérios de PASS/FAIL e DoD.

- `docs/sprint_21_1_capitulo_3_filemap.md`  
  Este capítulo: arquitetura e filemap.

- `docs/sprint_21_1_capitulo_4_execucao.md`  
  Plano de execução: ordem de implementação, comandos, checklists e relação gate↔arquivo.

- `docs/sprint_21_1_modo_agente_copiloto.md`  
  Especificação do modo agente do Copiloto:
  - prompt-base consolidado (incluindo ontologia S21, modelo de dados, limites),
  - lista de ferramentas e seus contratos,
  - exemplos de chamadas,
  - cenários de recusa.

- `docs/sprint_21_1_cenarios_copiloto_fontes.md`  
  Cenários end-to-end da S21.1 (G6): notícias, esportes, clima, fofoca, etc.

- `docs/sprint_21_1_politica_seguranca_copiloto.md`  
  Política de segurança: limites de escopo, proteção contra prompt injection, regras de confirmação humana.

- `docs/sprint_21_1_scorecard_copiloto_fontes.md`  
  Scorecard textual da sprint (G7): métricas, percepção, riscos.

- `docs/sprint_21_1_wrap_execucao.md`  
  Wrap executivo da Sprint 21.1 (G8): status dos gates, entregas, riscos, próximos passos (especialmente S22+).

---

## 4. Backend – API e serviços

### 4.1. Routers e endpoints

- `inspectah/api.py`  
  Inclui o router do Copiloto de Fontes:

  - import: `from inspectah.routers.copiloto_fontes import router as copiloto_fontes_router`;
  - inclusão: `app.include_router(copiloto_fontes_router, prefix="/admin/copiloto-fontes", tags=["admin-copiloto-fontes"])`.

- `inspectah/routers/copiloto_fontes.py`  
  Router FastAPI para o Copiloto, com endpoints típicos:

  - `POST /admin/copiloto-fontes/sessions` – (opcional) cria sessão de chat, devolve `session_id`;  
  - `POST /admin/copiloto-fontes/sessions/{session_id}/messages` – recebe mensagem do admin + snapshot do formulário + metadados e chama o agente;  
  - `POST /admin/copiloto-fontes/sessions/{session_id}/files` – recebe upload de arquivo e registra metadados (retorna `file_id` para o agente usar);  
  - (opcional) `GET /admin/copiloto-fontes/sessions/{session_id}` – inspeção leve de sessão (debug/admin).

Essas rotas **não** criam fontes nem alteram `sources`; elas apenas conversam com o agente e devolvem ações sugeridas.

### 4.2. Serviços auxiliares

- `inspectah/services/copiloto_sessions.py`  
  Serviço para gerenciar sessões de chat do Copiloto (em memória ou via SQLite/arquivo), com funções como:

  - `create_session(user_id, context)`;  
  - `get_session(session_id)`;  
  - `append_message(session_id, role, content)`;  
  - `attach_file(session_id, file_id, metadata)`.

- `inspectah/services/copiloto_files.py`  
  Serviço para lidar com arquivos:

  - armazenamento temporário (disco ou memória);  
  - extração de texto (PDF + texto plano, pelo menos);  
  - sanitização básica (limites de tamanho, remoção de binário inútil).

### 4.3. Integração com a S21 (sem tocar no DB)

O Copiloto não altera nada em `app/sources/service.py` nem `app/sources/models.py`. Quando precisa conhecer tipos/categorias/temas:

- lê da documentação (ontologia S21 + modelo de dados),
- ou consome endpoints de leitura já existentes (ex.: listar tipos/temas, se houver),
- mas nunca chama diretamente funções de criação de fonte.

Persistência de fontes continua sendo feita via rotas `app/sources/routes_admin.py`, acionadas apenas pelo formulário.

---

## 5. Camada de agentes – Copiloto em modo agente

### 5.1. Estrutura de arquivos

- `inspectah/agents/__init__.py`  
  Registro de agentes disponíveis (incluindo o Copiloto de Fontes).

- `inspectah/agents/s21_1_copiloto_fontes.py`  
  Implementação central do agente Copiloto de Fontes:

  - função `get_copiloto_agent()` que monta o agente com o prompt-base da S21.1;  
  - registro das ferramentas autorizadas;  
  - função `run_copiloto_interaction(session, user_message, form_state, files)` que:
    - monta o contexto de chamada;  
    - invoca o agente em modo agente;  
    - traduz a resposta do agente em `assistant_message` + `actions` estruturadas (ver protocolo no item 7).

- `inspectah/agents/tools/form_state.py`  
  Ferramentas para interpretar o `form_state`, com funções para:

  - validar o snapshot recebido do front;  
  - normalizar temas/info_types;  
  - mapear entre enums/códigos internos e valores textuais que o agente entende.

- `inspectah/agents/tools/file_reader.py`  
  Ferramenta para o agente ler conteúdo de arquivos anexados, com limites e normalização.

- `inspectah/agents/tools/logging.py`  
  Ferramenta de logging para registrar uso de ferramentas, eventos críticos e decisões importantes do Copiloto (sem dados sensíveis).

### 5.2. Limites do agente

O agente só consegue:

- ler `form_state` via ferramenta dedicada;
- ler conteúdo já extraído de arquivos (não pode sair batendo na internet);
- propor ações de patch de formulário (set_field, mark_suggested, clear_field, etc.);
- registrar logs internos.

Ele **não** consegue:

- criar/alterar fontes no DB;  
- chamar rotas de admin diretamente;  
- acessar outros subsistemas do Inspectah (Debunker, Timeline, etc.).

---

## 6. Frontend – UI do Copiloto e integração com o formulário

### 6.1. Componentes do widget

Sob `frontend/inspectah-ui/src/modules/admin/`:

- `components/CopilotoWidget.tsx`  
  - botão flutuante no canto inferior direito;  
  - controla abrir/fechar painel de chat;  
  - respeita feature flag no front.

- `components/CopilotoChatPanel.tsx`  
  - painel principal de chat;  
  - lista de mensagens (`CopilotoMessageList`);  
  - barra de entrada (`CopilotoInputBar`);  
  - componente de anexos (`CopilotoFileAttachment`);  
  - botão de “Novo chat”.

- `components/CopilotoMessageList.tsx`  
  - renderização da linha do tempo de mensagens;  
  - diferencia visualmente mensagens do admin e do Copiloto.

- `components/CopilotoInputBar.tsx`  
  - input de texto;  
  - botão de enviar;  
  - atalho para anexar arquivo.

- `components/CopilotoFileAttachment.tsx`  
  - upload de arquivos;  
  - exibição de anexos ativos na sessão;  
  - feedback de limites.

### 6.2. Hooks e integração com formulário

- `hooks/useCopilotoAgent.ts`  
  Hook responsável por:

  - gerenciar `session_id` (criar nova sessão ou reaproveitar a atual);  
  - enviar mensagens para o backend (`copilotoClient`);  
  - receber `assistant_message` + `actions`;  
  - expor callbacks para aplicar `actions` ao formulário.

- `hooks/useFonteFormState.ts` (ou equivalente existente)  
  Estendido para suportar patches do Copiloto:

  - aplica `set_field`/`clear_field`;  
  - marca campos como `suggestedBy: "copiloto"` para visual;  
  - garante que edições manuais do admin tenham precedência.

- Atualizações nas páginas:

  - `pages/AdminSourceFormPage.tsx`  
    Integra o widget do Copiloto com o formulário de nova fonte. Passa `form_state` e callbacks para o hook `useCopilotoAgent`.  
  - `pages/AdminSourcesPage.tsx`  
    Exibe o widget para que o admin possa iniciar o processo de cadastro a partir da lista (opcional).  
  - `pages/AdminSourceDetailPage.tsx`  
    Opcionalmente integra o Copiloto para ajustes de fontes existentes (se for escopo da S21.1; se não, fica explicitamente fora de escopo no Capítulo 4).

### 6.3. Cliente de API do Copiloto

- `api/copilotoClient.ts`  
  Funções para falar com o backend:

  - `sendMessage({ sessionId, userMessage, formState, metadata })`;  
  - `uploadFile({ sessionId, file })`;  
  - tipagens TypeScript para request/response, alinhadas com o protocolo JSON do backend.

---

## 7. Protocolo de modo agente (contratos JSON)

### 7.1. Payload frontend → backend

Estrutura base (JSON) do request ao endpoint `/admin/copiloto-fontes/sessions/{session_id}/messages`:

```json
{
  "session_id": "uuid-aleatorio",
  "user_message": "quero cadastrar globo.com como fonte de notícias gerais do Brasil",
  "form_state": {
    "type": null,
    "category": null,
    "themes": [],
    "info_types": [],
    "endpoint": null,
    "slug": null,
    "name": null,
    "description": null
  },
  "metadata": {
    "mode": "create",
    "source_id": null,
    "page": "AdminSourceForm"
  },
  "files": [
    {"file_id": "file-1", "filename": "doc-api-globo.pdf", "content_type": "application/pdf"}
  ]
}
```

### 7.2. Payload backend → frontend

Resposta típica do backend ao front:

```json
{
  "assistant_message": "Vou te ajudar a modelar essa fonte. Começo definindo tipo, categoria e alguns temas padrão.",
  "actions": [
    {"type": "set_field", "field": "type", "value": "news_rss"},
    {"type": "set_field", "field": "category", "value": "Noticias"},
    {"type": "set_field", "field": "themes", "value": ["politica", "economia", "brasil"]},
    {"type": "set_field", "field": "endpoint", "value": "https://oglobo.globo.com/rss.xml"},
    {"type": "set_field", "field": "name", "value": "Globo.com – Notícias gerais"},
    {"type": "set_field", "field": "slug", "value": "globo_com_noticias"},
    {"type": "mark_suggested", "fields": ["type", "category", "themes", "endpoint", "name", "slug"]}
  ]
}
```

O front aplica as ações ao estado do formulário e realça campos marcados em `mark_suggested`.

### 7.3. Ferramentas expostas ao agente

O agente opera sobre esse protocolo via um conjunto pequeno de ferramentas, por exemplo:

- `tool_read_form_state(form_state)` – valida e normaliza o snapshot do formulário;  
- `tool_read_file_content(file_id)` – devolve texto extraído de um arquivo anexado;  
- `tool_suggest_field_values(contexto)` – gera lista de ações estruturadas (`set_field`, `clear_field`, `mark_suggested`);  
- `tool_log_interaction(event)` – registra eventos relevantes (para evidências e debug).

Os contratos dessas ferramentas (parâmetros e retornos) são descritos em `docs/sprint_21_1_modo_agente_copiloto.md` e tipados em módulos Python/TypeScript.

---

## 8. Scripts de gates e estrutura de evidências

### 8.1. Scripts em `bin/`

No padrão da S21, a S21.1 ganha seu próprio conjunto de scripts:

- `bin/s21_1_all_gates.sh`  
  Orquestra S21_1_G0…S21_1_G7 em sequência.

- `bin/s21_1_g0_contexto.sh`  
  Verifica docs centrais (ontologia S21, modelo de dados, modo agente, política de segurança) e gera scorecard G0.

- `bin/s21_1_g1_ux_widget.sh`  
  Roda testes de frontend relevantes (lint/test/build + testes do widget) e gera scorecard G1.

- `bin/s21_1_g2_agent_mode.sh`  
  Roda `pytest tests/agents/test_s21_1_copiloto_mode_agent.py` e gera scorecard G2.

- `bin/s21_1_g3_sync_form.sh`  
  Roda testes de integração chat↔formulário, gera scorecard G3.

- `bin/s21_1_g4_files.sh`  
  Roda testes de upload/extração de arquivos, gera scorecard G4.

- `bin/s21_1_g5_safety.sh`  
  Roda `pytest tests/agents/test_s21_1_copiloto_safety.py`, gera scorecard G5.

- `bin/s21_1_g6_cenarios.sh`  
  Executa cenários e2e descritos em `docs/sprint_21_1_cenarios_copiloto_fontes.md` (via scripts ou chamadas HTTP), gera scorecard G6.

- `bin/s21_1_g7_scorecard.sh`  
  Consolida métricas, gera `out/scorecards/S21_1_G7_scorecard.json`.

- `bin/s21_1_g8_go_no_go.sh`  
  Lê scorecards G0…G7, aplica regra de decisão e grava `out/scorecards/S21_1_G8_go_no_go.json`.

### 8.2. Estrutura em `out/`

Scorecards:

- `out/scorecards/S21_1_G0_contexto.json`  
- `out/scorecards/S21_1_G1_ux_widget.json`  
- `out/scorecards/S21_1_G2_agent_mode.json`  
- `out/scorecards/S21_1_G3_sync_form.json`  
- `out/scorecards/S21_1_G4_files.json`  
- `out/scorecards/S21_1_G5_safety.json`  
- `out/scorecards/S21_1_G6_cenarios.json`  
- `out/scorecards/S21_1_G7_scorecard.json`  
- `out/scorecards/S21_1_G8_go_no_go.json`

Evidências (exemplos):

- `out/evidence/S21_1_G0_contexto/MANIFEST.json`  
- `out/evidence/S21_1_G1_ux/screens/*.png` e `notes.md`  
- `out/evidence/S21_1_G2_agent_mode/tests.log` e `tools_manifest.json`  
- `out/evidence/S21_1_G3_sync/tests.log` e `ux_notes.md`  
- `out/evidence/S21_1_G4_files/tests.log` e `sample_extractions.txt`  
- `out/evidence/S21_1_G5_safety/tests.log` e `prompt_safety_excerpt.txt`  
- `out/evidence/S21_1_G6_cenarios/session_logs/*.md` e `sources_created.json`  
- `out/evidence/S21_1_G7_scorecard/MANIFEST.json`  
- `out/evidence/S21_1_G8_go_no_go/MANIFEST.json`

---

## 9. Integração com a S21 e garantias de sanidade

### 9.1. Módulos reaproveitados

- `app/sources/*`  
  Continuam responsáveis por modelo, serviço, healthcheck e validação de fontes.

- `frontend/inspectah-ui/src/modules/admin/pages/AdminSourceFormPage.tsx`  
  Permanece sendo a UI principal de cadastro de fontes; o Copiloto apenas sugere patches.

- `docs/sprint_21_*`  
  Servem como base para o prompt-base do Copiloto e para a lógica de temas/info_types.

### 9.2. Teste de regressão mínima

Após a implementação da S21.1, o `bin/s21_all_gates.sh` continua rodando com todos os gates da S21 em PASS. Qualquer alteração que quebre o Console de Fontes é considerada regressão e deve ser corrigida antes do GO da S21.1.

---

## 10. Síntese

O Capítulo 3 da Sprint 21.1 fixa o seguinte quadro:

- **Documentos** organizam visão, modo agente, cenários, segurança, scorecard e wrap.  
- **Backend** oferece um router específico do Copiloto e serviços auxiliares (sessões e arquivos), sem desviar do fluxo padrão de fontes.  
- **Camada de agentes** encapsula o Copiloto em modo agente, com ferramentas explícitas e limites rígidos.  
- **Frontend** adiciona um widget de chat ao Console de Fontes e sincroniza sugestões com o formulário sem tirar o controle do humano.  
- **Gates e evidências** amarram tudo em scripts, scorecards e pastas bem definidas em `out/`.

Com esse filemap, a Sprint 21.1 tem uma rota de implementação clara e alinhada com o DNA do Inspectah: assistente forte, modo agente real, verdade sempre auditável e nenhuma “mágica” escondida atrás do chat.

