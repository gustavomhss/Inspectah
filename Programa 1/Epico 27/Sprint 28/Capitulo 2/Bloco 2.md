# Inspectah — Sprint 28
## Capítulo 2 — Bloco 2
### Gates S28_G0, S28_G1 e S28_G2 (Scope, Modelo & API de Admin)

---

#### 2.2.1 Gate S28_G0 — Scope & Baseline

**Objetivo do gate**  
Garantir que a Sprint 28 não comece “no improviso”. Antes de tocar código, o projeto precisa ter:
- contexto,  
- escopo,  
- filemap macro,  
- ligação explícita com o Programa 1 e o Épico E27.1 documentadas.

Este gate é a trava contra “sprint que saiu codando e depois tenta escrever a história”.

**Script oficial**  
`bin/s28_g0_scope_and_baseline.sh`

**Responsabilidades do script**
1. Verificar a existência e integridade dos quatro capítulos macro da sprint:
   - `docs/sprint_28_cap_1_contexto.md`  
   - `docs/sprint_28_cap_2_gates_metricas_dod.md`  
   - `docs/sprint_28_cap_3_arquitetura_filemap.md`  
   - `docs/sprint_28_cap_4_execucao_evidencias.md`
2. Validar itens mínimos dentro dos arquivos (checagens simples, porém objetivas):
   - Cap. 1 menciona explicitamente **Programa 1** e **Épico E27.1**.  
   - Cap. 2 lista todos os gates S28_G0…S28_G7.  
   - Cap. 3 contém um filemap de alto nível, com caminhos de backend, frontend, testes, scripts e evidências.  
   - Cap. 4 referencia os scripts de gates e a organização de evidências.
3. Gerar o scorecard do gate:
   - `out/scorecards/S28_G0_scope_and_baseline.json`

**Campos mínimos do scorecard S28_G0**
- `gate_id`: "S28_G0_scope_and_baseline"  
- `status`: "PASS" | "FAIL"  
- `docs_present`: lista booleana para cada capítulo  
- `program_and_epic_linked`: boolean (se Programa 1 e E27.1 estão explicitamente referenciados)  
- `notes`: texto curto com qualquer ressalva não-bloqueante

**Critérios de PASS**
- Todos os quatro capítulos existem, não estão vazios e têm headers coerentes com a sprint.  
- As referências a Programa 1 e E27.1 estão claras (sem dúvida sobre encaixe no roadmap).  
- O filemap macro da S28 já está descrito no Cap. 3 (mesmo que detalhes finos sejam refinados depois).  
- Scorecard JSON foi gerado e salvo no caminho esperado.

**Critérios de FAIL**
- Ausência de qualquer um dos docs obrigatórios.  
- Docs presentes, porém vazios ou com conteúdo genérico que poderia pertencer a qualquer sprint.  
- Falta de referência explícita ao Programa 1/E27.1.  
- Falha na geração do scorecard.

**Impacto do FAIL**
- A sprint **não deve iniciar implementação** de modelo/API/console antes de S28_G0 estar em PASS.  
- Se for detectado FAIL após início de implementação, o time precisa corrigir os docs imediatamente e reexecutar o gate — caso contrário, o risco de desvio de escopo cresce exponencialmente.

---

#### 2.2.2 Gate S28_G1 — Sources Model & Schema

**Objetivo do gate**  
Consolidar o modelo de fonte (`Source` + enums + entidades relacionadas) e garantir que o banco de dados reflita esse modelo com invariantes fortes de domínio.

Este gate é o alicerce: se o modelo estiver torto, API, console e ingestão sofrerão efeitos cascata.

**Script oficial**  
`bin/s28_g1_sources_model_and_schema.sh`

**Arquivos de referência (entrada esperada)**
- **Domínio / modelos**  
  - `app/sources/models.py`  
    - `class Source(Base)`  
    - `class SourceType(Base)`  
    - enums `SourceState`, `SourceMode`, `SourceCriticality`.

- **Migrations**  
  - `migrations/versions/00xx_s28_sources_model_consolidation.py`  
    - Ajustes em colunas existentes.  
    - Criação de novos campos (ex.: `criticality`, `state_reason`, `domain`, `category`, etc.).

- **Testes de domínio**  
  - `tests/domain/test_sources_model_invariants.py`

**Responsabilidades do script**
1. Rodar migrations:  
   - `alembic upgrade head` (ou pipeline equivalente)  
   - Validar que não há erro na aplicação da migration de S28.
2. Verificar o schema resultante (ex.: via introspecção ou dump):  
   - `Source` contém todos os campos definidos no Cap. 1/3:  
     - identidade: `id`, `name`, `description`,  
     - classificação: `type`, `category`, `domain`,  
     - operação: `config`, `credentials_ref` (se existir), `schedule`/`cadence`, `mode`,  
     - risco: `criticality`,  
     - ciclo de vida: `state`, `state_changed_at`, `state_reason`, timestamps.  
   - enums são persistidos de forma consistente.
3. Rodar testes de domínio:  
   - `pytest tests/domain/test_sources_model_invariants.py`
4. Gerar scorecard:  
   - `out/scorecards/S28_G1_sources_model_and_schema.json`

**Invariantes que devem estar cobertas em teste** (exemplos)  
Não exaustivo, mas mínimo aceitável:
- Transições de estado permitidas:  
  - `ACTIVE → DISABLED`  
  - `DISABLED → ACTIVE`  
  - `ACTIVE → DEPRECATED`
- Transições proibidas:  
  - `DEPRECATED → ACTIVE`  
  - qualquer sequência que viole regras de negócio (ex.: pular de `DISABLED` para `DEPRECATED` sem certos critérios, se especificado assim).  
- Validações específicas por tipo de fonte:  
  - `news_rss` exige URL válida,  
  - `http_json` exige endpoint + método,  
  - etc. (o suficiente para impedir fontes “meio configuradas”).

**Campos mínimos do scorecard S28_G1**
- `gate_id`: "S28_G1_sources_model_and_schema"  
- `status`: "PASS" | "FAIL"  
- `migrations_applied`: true/false  
- `schema_checks`: lista textual das checagens realizadas  
- `invariants_covered`: lista das invariantes garantidas por teste  
- `open_issues`: lista de qualquer divergência não-bloqueante (idealmente vazia)

**Critérios de PASS**
- Migrations aplicadas com sucesso, sem erros.  
- Dump de schema compatível com o modelo descrito no Cap. 1/3.  
- Suite `test_sources_model_invariants.py` em PASS.  
- Scorecard JSON presente e bem formado.

**Critérios de FAIL**
- Erro na aplicação de migrations.  
- Campos essenciais ausentes ou com tipo incorreto.  
- Invariantes críticas de estado sem teste automatizado.  
- Scorecard ausente ou com `status = "FAIL"`.

**Impacto do FAIL**
- Bloqueia S28_G2 e S28_G3: ninguém deve fortalecer API/console em cima de um modelo de domínio instável.  
- Gate deve ser tratado como **prioridade máxima** até ficar verde.

---

#### 2.2.3 Gate S28_G2 — Admin API `/admin/sources` (CRUD & ON/OFF)

**Objetivo do gate**  
Assegurar que a API de admin de fontes é:
- completa para as operações planejadas (CRUD & ON/OFF),  
- correta em termos de validação e erros,  
- coerente com o modelo consolidado em S28_G1,  
- visível e estável via OpenAPI.

**Script oficial**  
`bin/s28_g2_sources_admin_api.sh`

**Arquivos de referência (entrada esperada)**
- **Rotas de admin**  
  - `app/api/admin_sources_routes.py`

- **Schemas (DTOs)**  
  - `app/sources/schemas.py`  
    - `SourceCreate`, `SourceUpdate`, `SourceDetail`, `SourceListItem`, etc.

- **Testes de API**  
  - `tests/api/test_admin_sources_crud_onoff.py`

**Rotas mínimas esperadas na API**
- `GET /admin/sources`  
  - Lista de fontes com filtros: `type`, `state`, `category`, `domain`, `mode`, `criticality`, além de paginação.
- `GET /admin/sources/{source_id}`  
  - Detalhe completo de uma fonte.  
- `POST /admin/sources`  
  - Criação de fonte, com validações fortes de payload.  
- `PUT /admin/sources/{source_id}`  
  - Edição de campos permitidos (restrições claras para fontes `DEPRECATED`).
- `POST /admin/sources/{source_id}/activate`  
- `POST /admin/sources/{source_id}/disable`  
- `POST /admin/sources/{source_id}/deprecate`

**Responsabilidades do script**
1. Executar os testes de API:  
   - `pytest tests/api/test_admin_sources_crud_onoff.py`
2. Opcionalmente, validar documentação de OpenAPI:  
   - por exemplo, executando um comando que gera/extrai o schema e checando se as rotas acima estão presentes.  
3. Gerar scorecard:  
   - `out/scorecards/S28_G2_sources_admin_api.json`

**Cenários que devem estar cobertos em teste**
- **CRUD básico**  
  - Criar fonte válida.  
  - Listar fontes com e sem filtros.  
  - Detalhar fonte existente.  
  - Editar campos permitidos em fonte ativa.  
- **Transições de estado válidas**  
  - `ACTIVE → DISABLED` (via `/disable`).  
  - `DISABLED → ACTIVE` (via `/activate`).  
  - `ACTIVE → DEPRECATED` (via `/deprecate`).
- **Transições de estado proibidas**  
  - Tentar `DEPRECATED → ACTIVE` → `409 Conflict`.  
  - Qualquer outra transição explicitamente vetada pelas regras de domínio.  
- **Erros esperados**  
  - `400 Bad Request` para payload inválido (campos faltando, valores inválidos, combinações impossíveis).  
  - `404 Not Found` para `source_id` inexistente.  
  - `409 Conflict` para transições ilegais.

**Campos mínimos do scorecard S28_G2**
- `gate_id`: "S28_G2_sources_admin_api"  
- `status`: "PASS" | "FAIL"  
- `covered_endpoints`: lista de rotas testadas  
- `error_handling_covered`: lista de tipos de erro validados (400/404/409)  
- `open_issues`: lista de problemas menores (casos não cobertos, TODOs não-críticos)

**Critérios de PASS**
- Testes de API em PASS.  
- Todos os endpoints principais de CRUD & ON/OFF implementados e cobertos.  
- Erros tratados com códigos HTTP adequados, sem ambiguidade.  
- OpenAPI atualizado e coerente com o comportamento real da API.  
- Scorecard JSON presente e consistente.

**Critérios de FAIL**
- Falha em qualquer teste de cenário canônico (casos A–D mapeados no Cap. 1).  
- Endpoint ausente ou com comportamento divergente do especificado.  
- API permitindo colocar `Source` em estado ilegal sem bloquear via `409`.  
- Falta de documentação ou inconsistência relevante no OpenAPI.

**Impacto do FAIL**
- Bloqueia S28_G3 (console) e S28_G4 (integração com ingestão), já que o frontend e os testes de integração dependem de uma API de admin previsível.  
- Enquanto S28_G2 estiver em FAIL, qualquer trabalho adicional no console deve ser tratado como experimental, não como pronto para operação.

---

Com estes três gates detalhados (G0, G1 e G2), o Bloco 2 do Capítulo 2 fixa o alicerce de qualidade para **escopo, modelo de domínio e API de admin**. Os próximos blocos aprofundam os gates de frontend (G3), integração com Ingestão 2.0 (G4), sanidade de legado (G5), demo/UX (G6) e decisão final GO/NO_GO (G7).