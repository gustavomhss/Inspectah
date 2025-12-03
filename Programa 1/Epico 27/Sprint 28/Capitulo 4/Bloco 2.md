# Inspectah — Sprint 28
## Capítulo 4 — Bloco 2
### Plano Detalhado por Gate (G0, G1, G2) — Do papel ao código

---

#### 4.2.1 Objetivo deste bloco

Este bloco desce o zoom da estratégia macro (Bloco 1) para um **plano tático fino** dos três primeiros gates da Sprint 28:

- **S28_G0 — Scope & Baseline**  
- **S28_G1 — Sources Model & Schema**  
- **S28_G2 — Admin API /admin/sources**

A missão aqui é transformar esses gates em **listas de tarefas concretas**, com:
- ordem de execução,  
- entregáveis claros,  
- comandos típicos,  
- evidências esperadas,  
- erros comuns a evitar.

A ideia é que qualquer dev/QA que entre no meio da sprint consiga entender **exatamente o que fazer** para levar G0, G1 e G2 de vermelho para verde.

---

#### 4.2.2 Gate S28_G0 — Scope & Baseline

**Pergunta que G0 responde:**
> “Estamos todos falando da mesma Sprint 28, com escopo, métricas, gates e filemap alinhados — e o repositório está pronto para receber o trabalho?”

##### 4.2.2.1 Tarefas concretas de G0

1. **Criar/validar os documentos principais da sprint**
   - Confirmar existência dos arquivos (nomes sugestivos, podem ser ajustados ao padrão real do repo):
     - `docs/sprint_28_cap_1_contexto_e_objetivos.md`  
     - `docs/sprint_28_cap_2_gates_metricas_dod.md`  
     - `docs/sprint_28_cap_3_arquitetura_filemap.md`  
     - `docs/sprint_28_cap_4_execucao_evidencias.md`
   - Checar se:
     - Cap. 1 referencia **Programa 1** e **Épico E27.1** explicitamente.  
     - Cap. 2 lista todos os gates S28_G0…S28_G7 e states-alvo SA-28-01…SA-28-05.  
     - Cap. 3 contém o filemap da sprint, coerente com o código esperado.  
     - Cap. 4 descreve estratégia de execução, plano por gate, CI, evidências.

2. **Criar/validar estrutura de evidências e scorecards**
   - Garantir que a árvore de diretórios mínima exista:
     - `out/evidence/`  
     - `out/scorecards/`
   - Não precisa estar cheia ainda, mas o repositório deve ter esses caminhos previstos (via `.gitkeep` ou equivalente, se o projeto tiver essa convenção).

3. **Configurar/validar branch da Sprint 28**
   - Criar branch, caso ainda não exista:
     - `git checkout -b feature/s28_sources_crud_onoff`
   - Verificar se está atualizada com `main` (ou branch base acordada).  
   - Registrar no Cap. 4 (ou no doc de planejamento geral) qual branch é a "oficial" da sprint.

4. **Conferir que o workflow de CI da sprint existe ou será criado**
   - Verificar presença (ou planejar criação) de:
     - `.github/workflows/s28-gates.yml`
   - Se ainda não existir, deixar anotado no Cap. 4 que será criado até a metade da sprint.

##### 4.2.2.2 Execução do script de G0

Script oficial:
- `bin/s28_g0_scope_and_baseline.sh`

O script deve:
- Verificar existência dos docs-chave (Cap. 1–4).  
- Opcionalmente, rodar uma checagem básica (ex.: lint de markdown ou verificação de headings).  
- Criar diretórios de evidência/scorecards se ainda não existirem.  
- Gerar scorecard JSON com status e observações.

Evidências:
- Pasta: `out/evidence/S28_G0_scope_and_baseline/`  
  - logs simples (ex.: `check_docs.log`).
- Scorecard: `out/scorecards/S28_G0_scope_and_baseline.json`

Erros comuns a evitar:
- Deixar G0 “aceitar qualquer coisa” (por exemplo, rodar mesmo com Cap. 2 incompleto).  
- Esquecer de referenciar E27.1 e Programa 1 nos docs, quebrando o fio narrativo do produto.

---

#### 4.2.3 Gate S28_G1 — Sources Model & Schema

**Pergunta que G1 responde:**
> “O modelo de fontes (`Source`) e o schema de banco estão consolidados, alinhados ao que a sprint promete, e protegidos por testes de invariantes?”

Esse gate é a **espinha dorsal** de toda a sprint. Sem ele, API, ingestão e console ficam sem chão.

##### 4.2.3.1 Tarefas concretas de G1

1. **Modelar/ajustar entidade `Source`**
   - Arquivo: `app/sources/models.py`
   - Verificar/implementar:
     - Campos básicos: `id`, `name`, `slug` (se existir), `description`.  
     - Campos de classificação: `type`, `category`, `domain`.  
     - Configuração técnica: `config` (JSON/objeto), `credentials_ref`, `mode`, `cadence/schedule`.  
     - Criticidade: `criticality`.  
     - Ciclo de vida: `state`, `state_changed_at`, `state_reason`.  
     - Metadados: `created_at`, `updated_at`.
   - Garantir que enums `SourceState`, `SourceMode` e `SourceCriticality` existem e são usados de forma consistente.

2. **Definir invariantes de domínio explícitas**
   - Em métodos da própria classe `Source` ou em serviços auxiliares, garantir regras como:
     - Transições permitidas/proibidas de `state`.  
     - Campos obrigatórios por tipo de fonte (ex.: URL para `news_rss`).  
     - Defaults sensatos para `criticality`, `mode`, etc.

3. **Criar/ajustar migration da S28**
   - Arquivo: `migrations/versions/00xx_s28_sources_model_consolidation.py`
   - A migration deve:
     - Adicionar campos novos (`criticality`, `state_reason`, etc.) quando ainda não existirem.  
     - Ajustar tipos/constraints de campos existentes (por exemplo, tornar `state` NOT NULL).  
     - Atribuir defaults aos dados já existentes (evitar `NULL` inesperado).  
     - Ser reversível, se isso fizer parte do padrão do projeto.

4. **Escrever/ajustar testes de domínio**
   - Arquivo: `tests/domain/test_sources_model_invariants.py`
   - Casos mínimos:
     - Criar `Source` válido com cada tipo suportado.  
     - Tentar criar fontes inválidas (falta de campos obrigatórios, config inconsistente).  
     - Transições de estado permitidas (`ACTIVE → DISABLED`, `DISABLED → ACTIVE`, `ACTIVE → DEPRECATED`).  
     - Transições proibidas (`DEPRECATED → ACTIVE`, etc.).

##### 4.2.3.2 Ordem recomendada de trabalho para G1

1. Ajustar modelo `Source` + enums.  
2. Escrever/ajustar testes de invariantes, mesmo que inicialmente falhem.  
3. Criar/ajustar migration para alinhar schema com o modelo.  
4. Rodar migrations localmente (db dev).  
5. Rodar `pytest tests/domain/test_sources_model_invariants.py`.  
6. Só depois disso rodar `bin/s28_g1_sources_model_and_schema.sh`.

##### 4.2.3.3 Script e evidências de G1

Script oficial:
- `bin/s28_g1_sources_model_and_schema.sh`

O script deve:
- Garantir ambiente pronto (ex.: `export PYTHONPATH=.`).  
- Rodar migrations (ou ao menos checar que estão consistentes).  
- Rodar testes de domínio.  
- Registrar logs em `out/evidence/S28_G1_sources_model_and_schema/`.  
- Gerar `out/scorecards/S28_G1_sources_model_and_schema.json` com:
  - `gate_id`,  
  - `status`,  
  - resumo dos testes rodados,  
  - eventuais observações.

Erros comuns a evitar:
- Ajustar o modelo sem atualizar as migrations (ou vice-versa).  
- Adicionar campos no banco sem refletir nos schemas/API/console.  
- Esquecer de testar transições proibidas de estado.

---

#### 4.2.4 Gate S28_G2 — Admin API `/admin/sources`

**Pergunta que G2 responde:**
> “A API de administração de fontes (CRUD & ON/OFF) está estável, coerente com o domínio e adequadamente testada?”

Se G1 é a espinha dorsal, G2 é o **sistema circulatório**: é por aqui que toda operação passa.

##### 4.2.4.1 Tarefas concretas de G2

1. **Implementar/ajustar rotas em `admin_sources_routes`**
   - Arquivo: `app/api/admin_sources_routes.py`
   - Endpoints esperados (contrato conceitual):
     - `GET /admin/sources` — lista paginada com filtros.  
     - `GET /admin/sources/{source_id}` — detalhe da fonte.  
     - `POST /admin/sources` — criação.  
     - `PUT /admin/sources/{source_id}` — edição.  
     - `POST /admin/sources/{source_id}/activate` — ativar.  
     - `POST /admin/sources/{source_id}/disable` — desativar.  
     - `POST /admin/sources/{source_id}/deprecate` — deprecar.

2. **Alinhar os schemas (DTOs) usados pela API**
   - Arquivo: `app/sources/schemas.py`
   - Estruturas típicas:
     - `SourceCreate` — payload de criação.  
     - `SourceUpdate` — payload de atualização.  
     - `SourceListItem` — resposta da listagem.  
     - `SourceDetail` — resposta detalhada.
   - Garantir que os campos expostos batem com o modelo `Source` (sem vazar detalhes desnecessários, como internals de ORM).

3. **Implementar regras de negócio na API**
   - As rotas de mudança de estado devem:
     - Verificar se a transição é permitida (usando funções do domínio).  
     - Atualizar `state`, `state_changed_at`, `state_reason`.  
     - Retornar `409 Conflict` em casos proibidos.  
   - A rota de criação deve:
     - Validar campos obrigatórios.  
     - Validar consistência básica de `config` com `type`.

4. **Escrever/ajustar testes de API**
   - Arquivo: `tests/api/test_admin_sources_crud_onoff.py`
   - Casos mínimos:
     - Criar fonte válida, ler na listagem e detalhe.  
     - Editar campos permitidos e verificar persistência.  
     - Ativar, desativar, deprecar fonte com respostas corretas.  
     - Erros 400 (payload inválido), 404 (source inexistente), 409 (transição proibida).

5. **Validar OpenAPI**
   - Garantir que o schema OpenAPI (ex.: `/docs` do FastAPI) reflita as rotas & DTOs.  
   - Não precisa ser gate separado, mas é verificação importante na rotina.

##### 4.2.4.2 Ordem recomendada de trabalho para G2

1. Confirmar G1 em PASS (ou pelo menos modelo `Source` estável).  
2. Ajustar/implementar rotas de leitura (`GET /admin/sources`, `GET /admin/sources/{id}`).  
3. Implementar criação/edição (`POST`, `PUT`).  
4. Implementar ON/OFF/DEPRECATE com uso de invariantes de domínio.  
5. Escrever/ajustar testes de API cobrindo todos os cenários.  
6. Rodar `pytest tests/api/test_admin_sources_crud_onoff.py` localmente.  
7. Rodar `bin/s28_g2_sources_admin_api.sh`.

##### 4.2.4.3 Script e evidências de G2

Script oficial:
- `bin/s28_g2_sources_admin_api.sh`

O script deve:
- Ativar o ambiente Python.  
- Rodar somente os testes relevantes de API (ou suite maior se desejado).  
- Escrever logs de execução em:  
  - `out/evidence/S28_G2_sources_admin_api/tests.log` (por exemplo).  
- Gerar scorecard em:  
  - `out/scorecards/S28_G2_sources_admin_api.json`

Campos sugeridos no scorecard:
- `gate_id`: "S28_G2_sources_admin_api"  
- `status`: "PASS" | "FAIL"  
- `tests_run`: lista ou resumo (ex.: `tests/api/test_admin_sources_crud_onoff.py`).  
- `error_summary`: vazio em caso de PASS; resumo em caso de FAIL.

Erros comuns a evitar:
- Tratar mudança de estado como simples update em campo, sem passar por invariantes de domínio.  
- Expor campos demais ou de menos nas respostas (tornando o console difícil de usar).  
- Deixar o teste de API frágil a detalhes irrelevantes (por exemplo, ordem de campos na resposta, se o framework não garantir isso).

---

#### 4.2.5 Encadeamento entre G0, G1 e G2

Depois de destrinchar os três gates, o fluxo ideal fica:

1. **G0** monta o palco: docs prontos, branch criada, estrutura de evidências/scorecards definida.  
2. **G1** constrói o chão: modelo `Source` e schema de banco sólidos e testados.  
3. **G2** abre a porta de operação: Admin API coerente com o domínio, pronta para ser usada pelo console e pelos testes de integração.

Sem G0, a sprint não tem narrativa nem lugar para guardar provas.  
Sem G1, qualquer API é um castelo de cartas.  
Sem G2, o console vira fachada e a ingestão não tem como ser operada de forma controlada.

---

Com este Bloco 2, o Capítulo 4 da Sprint 28 ganha um plano tático de alta resolução para os gates iniciais G0, G1 e G2 — de tarefas concretas ao formato de evidências — deixando o terreno pronto para os próximos blocos cobrirem G3–G4, G5–G7, comandos locais e uso do CI na decisão final de GO/NO_GO.