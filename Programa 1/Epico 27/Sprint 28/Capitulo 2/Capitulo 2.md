# Inspectah — Sprint 28
## Capítulo 2 — Gates, Métricas e Definition of Done
### E27.1 — CRUD & ON/OFF de Fonte

---

## 2.1 Visão geral: o que significa “Sprint 28 em GO”

A Sprint 28 só é considerada **GO** se, ao final:

1. Todos os **gates S28_G0…S28_G7** estiverem em estado `PASS` com evidências e scorecards gerados.  
2. Os **estados-alvo** definidos no Cap. 1 forem verdadeiros na prática:
   - **SA-28-01** — API de admin de fontes sólida e estável.  
   - **SA-28-02** — Console de fontes v2 permite operar sem terminal.  
   - **SA-28-03** — ON/OFF conversa com Ingestão 2.0 de forma determinística.  
   - **SA-28-04** — Modelo de fonte consolidado, documentado e saneado.  
   - **SA-28-05** — Sanidade de legado S21/S22 preservada.
3. O repositório esteja em estado **sanitário**:
   - todos os testes relacionados à sprint passam localmente e no CI,  
   - scripts de gates são idempotentes e podem ser reexecutados sem efeitos colaterais estranhos,  
   - docs de Cap. 1–4 da S28 estão atualizados.

O Capítulo 2 traduz essa visão em **gates concretos, métricas e DoD** para que não haja ambiguidade sobre o que “GO” significa.

---

## 2.2 Lista de Gates da Sprint 28

### S28_G0 — Scope & Baseline

**Propósito**  
Garantir que a Sprint 28 começa com **escopo, contexto e artefatos mínimos** em ordem antes de qualquer implementação pesada.

**Script**  
`bin/s28_g0_scope_and_baseline.sh`

**Entradas esperadas**
- Documentos de sprint criados:
  - `docs/sprint_28_cap_1_contexto.md`  
  - `docs/sprint_28_cap_2_gates_metricas_dod.md`  
  - `docs/sprint_28_cap_3_arquitetura_filemap.md`  
  - `docs/sprint_28_cap_4_execucao_evidencias.md`
- Referência explícita ao Programa 1 e ao Épico E27.1.

**Critérios de PASS (DoD do gate)**
- Todos os arquivos acima existem e passam em checagens básicas (ex.: não vazios, header correto, versões identificadas).  
- O script confirma que:
  - há menção explícita a E27.1 e ao Programa 1,  
  - o filemap de alto nível da S28 está declarado no Cap. 3.  
- Scorecard `out/scorecards/S28_G0_scope_and_baseline.json` gerado com:
  - `status = "PASS"`,  
  - `doc_paths` listando os quatro capítulos,  
  - `notes` resumindo eventuais pendências menores (ex.: TODOs anotados, mas não bloqueantes).

**Falha (FAIL) se**
- Qualquer doc obrigatório faltar ou estiver vazio.  
- O escopo descrito não mencionar E27.1/Programa 1 ou entrar em contradição com o Roadmap.  
- O scorecard não for gerado.

---

### S28_G1 — Sources Model & Schema

**Propósito**  
Consolidar o **modelo de fonte** (domínio + DB) e garantir que o schema resultante está alinhado às invariantes definidas.

**Script**  
`bin/s28_g1_sources_model_and_schema.sh`

**Entradas esperadas**
- Código de modelos atualizado:
  - `app/sources/models.py`  
  - enums de estado, modo e criticidade.  
- Migrations de S28:
  - `migrations/versions/00xx_s28_sources_model_consolidation.py`
- Testes de domínio:
  - `tests/domain/test_sources_model_invariants.py`

**Critérios de PASS**
- `alembic upgrade head` (ou equivalente) executa sem erro, aplicando a migration de S28.  
- Dump de schema evidencia:
  - `Source` com campos esperados: `id`, `name`, `description`, `type`, `category`, `domain`, `config`, `credentials_ref` (se existir), `schedule`/`cadence`, `mode`, `criticality`, `state`, `state_changed_at`, `state_reason`, timestamps.  
  - Enums persistidos (`SourceState`, `SourceMode`, `SourceCriticality`).
- `pytest tests/domain/test_sources_model_invariants.py` passa, cobrindo invariantes como:
  - transições de estado permitidas e proibidas (`ACTIVE → DISABLED`, `DISABLED → ACTIVE`, `ACTIVE → DEPRECATED`, bloqueio de `DEPRECATED → ACTIVE`),  
  - validações de campos obrigatórios por `SourceType` (ex.: RSS exige URL).
- Scorecard `out/scorecards/S28_G1_sources_model_and_schema.json` gerado com:
  - `status`,  
  - `schema_checks` (lista de asserts feitos),  
  - `invariants_covered` (lista textual de invariantes testadas).

**Falha (FAIL) se**
- Migrations falham ou deixam o schema em estado inconsistente.  
- Alguma invariante crítica de estado não estiver coberta por testes.  
- Campos combinados no modelo não baterem com o esperado para E27.1.

---

### S28_G2 — Admin API `/admin/sources` (CRUD & ON/OFF)

**Propósito**  
Garantir que a **API de admin** de fontes é estável, validada e coerente com o modelo consolidado.

**Script**  
`bin/s28_g2_sources_admin_api.sh`

**Entradas esperadas**
- Implementação/ajuste de rotas em `app/api/admin_sources_routes.py`.  
- Schemas em `app/sources/schemas.py`.  
- Testes de API em `tests/api/test_admin_sources_crud_onoff.py`.

**Critérios de PASS**
- Execução de `pytest tests/api/test_admin_sources_crud_onoff.py` sem falhas.  
- Cobertura mínima dos cenários:
  - criar fonte válida,  
  - listar fontes com filtros (tipo, estado, categoria, domínio, modo, criticidade),  
  - detalhar fonte específica,  
  - editar campos permitidos,  
  - transições de estado válidas (`activate`, `disable`, `deprecate`),  
  - tentativas de transições proibidas resultando em `409`,  
  - validações de payload incompleto/malformado resultando em `400`,  
  - fontes inexistentes retornando `404`.
- Contrato de OpenAPI atualizado (via geração automática ou verificação de arquivo), com rotas e schemas corretos.  
- Scorecard `out/scorecards/S28_G2_sources_admin_api.json` incluindo:
  - `status`,  
  - `covered_endpoints`,  
  - `error_handling_covered` (tipos de erros testados).

**Falha (FAIL) se**
- Qualquer cenário canônico (cadastro, edição, ON/OFF) não estiver coberto por teste.  
- A API permitir colocar `Source` em estado ilegal (ex.: `DEPRECATED → ACTIVE`).  
- OpenAPI não refletir o contrato real.

---

### S28_G3 — Sources Console Front (Console de Fontes v2)

**Propósito**  
Assegurar que o **console de fontes v2** está funcional, coerente com o Design System Admin v1 e cobre fluxos principais de operação.

**Script**  
`bin/s28_g3_sources_console_front.sh`

**Entradas esperadas**
- Páginas e componentes:
  - `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`  
  - `.../SourceFormPage.tsx`  
  - `.../components/SourceListTable.tsx`  
  - `.../SourceStateBadge.tsx`  
  - `.../SourceActionsMenu.tsx`
- API client:
  - `frontend/inspectah-ui/src/features/sources/api/adminSourcesApi.ts`
- Testes de UI:
  - `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`

**Critérios de PASS**
- `npm test` e `npm run build` passam na pasta do frontend.  
- Testes de UI cobrem, ao menos:
  - fluxo de criação de fonte (caso A),  
  - fluxo de desativação/reativação (caso B/C),  
  - validações de formulário (ex.: URL obrigatória),  
  - estados vazios (lista sem fontes) e de erro (API indisponível).
- Verificação básica de uso do Design System Admin v1:
  - imports seguem padrão (ex.: componentes de tabela, botões, badges),  
  - não há criação de "mini design system paralelo" dentro de fontes.
- Scorecard `out/scorecards/S28_G3_sources_console_front.json` com:
  - `status`,  
  - `flows_covered`,  
  - `ds_violations` (lista vazia ou itens documentados como exceções temporárias).

**Falha (FAIL) se**
- Build do frontend falhar.  
- Fluxos críticos de UI (casos A–D) não forem automatizados ou estiverem quebrados.  
- Console de fontes exigir intervenção manual via terminal para completar alguma operação padrão.

---

### S28_G4 — Sources × Ingestão 2.0 (ON/OFF Integration)

**Propósito**  
Provar que o **estado da fonte** (`ACTIVE`/`DISABLED`) regula o comportamento da **Ingestão 2.0** de forma determinística.

**Script**  
`bin/s28_g4_sources_ingestion_integration.sh`

**Entradas esperadas**
- Ajustes em `app/ingestion/scheduler.py` (ou equivalente).  
- Testes de integração em `tests/integration/test_sources_ingestion_onoff.py`.

**Critérios de PASS**
- Os testes de integração cobrem, no mínimo, três cenários:
  - **Cenário 1** — Fonte `ACTIVE` e `AUTO` é ingerida periodicamente (com `IngestionRun` aparecendo).  
  - **Cenário 2** — Desativar a fonte (`DISABLED`) via API/console faz com que novos `IngestionRun` parem de ser criados.  
  - **Cenário 3** — Reativar a fonte (`ACTIVE`) faz a ingestão voltar a ocorrer.
- Logs de teste explicitam a sequência de operações (criação, state change, ingestões observadas).  
- Scorecard `out/scorecards/S28_G4_sources_ingestion_integration.json` inclui:
  - `status`,  
  - `scenarios`,  
  - `evidence_paths` (logs, prints de `IngestionRun`).

**Falha (FAIL) se**
- Houver qualquer cenário em que fonte `DISABLED` continue a ser ingerida.  
- Houver necessidade de "tarefas manuais adicionais" para que ON/OFF funcione (isso indica que o contrato ainda não é normativo).

---

### S28_G5 — Observability & Legacy Sanity (S21/S22)

**Propósito**  
Preservar **confiabilidade** e evitar regressões em funcionalidades existentes de fontes e ingestão (S21/S22).

**Script**  
`bin/s28_g5_observability_and_legacy_sanity.sh`

**Entradas esperadas**
- Scripts de gates anteriores relacionados a fontes/ingestão, por exemplo:
  - `bin/s21_g1_sources_domain.sh`  
  - `bin/s21_g2_sources_api.sh`  
  - `bin/s22_g1_ingestion_core.sh`  
  - `bin/s22_g2_ingestion_metrics.sh`
- Configurações de observabilidade mínimas (logs, métricas) configuradas previamente.

**Critérios de PASS**
- Todos os gates de S21/S22 considerados relevantes executam com `PASS`.  
- Logs de execução demonstram que as rotinas antigas ainda funcionam com o novo modelo de `Source`.  
- Não há degradação óbvia em métricas básicas (ex.: ingestões falhando em massa após mudanças de S28).  
- Scorecard `out/scorecards/S28_G5_observability_and_legacy_sanity.json` com:
  - `status`,  
  - `legacy_gates_run` (lista),  
  - `regressions_detected` (lista vazia ou itens anotados como bugs a serem corrigidos **antes** do GO).

**Falha (FAIL) se**
- Algum gate crítico de S21/S22 falhar por causa de mudanças na S28.  
- Houver regressão sem plano de correção dentro da própria sprint.

---

### S28_G6 — Demo Interna & UX

**Propósito**  
Validar, com olhos humanos, que o que foi entregue é **operável de verdade**, não apenas tecnicamente correto.

**Script**  
`bin/s28_g6_demo_internal.sh`

**Entradas esperadas**
- Roteiro de demo definido em doc (por exemplo, no Cap. 4).  
- Ambiente local ou de staging com backend e frontend rodando.

**Critérios de PASS**
- Execução bem-sucedida de um roteiro mínimo contendo, no mínimo:
  - Caso A: cadastro de nova fonte RSS de notícias.  
  - Caso B: desativação de fonte problemática e observação de parada de ingestão.  
  - Caso C: reativação de fonte após período de manutenção.  
- Registro da demo em forma de:
  - vídeo curto ou sequência de screenshots,  
  - notas de UX (o que ficou claro, o que ainda gera atrito, sugestões futuras).
- Scorecard `out/scorecards/S28_G6_demo_internal.json` com:
  - `status`,  
  - `scenarios_demoed`,  
  - `ux_feedback_summary` (texto curto),  
  - `followup_items` (itens que serão levados para backlog de sprints futuras).

**Falha (FAIL) se**
- Algum cenário canônico da demo não puder ser concluído pela UI.  
- A demo revelar bloqueios graves de usabilidade que inviabilizam operação real.

---

### S28_G7 — GO/NO_GO Final

**Propósito**  
Consolidar a decisão final da Sprint 28, com base em evidências dos gates anteriores.

**Script**  
`bin/s28_g7_go_no_go.sh`

**Entradas esperadas**
- Scorecards de S28_G0 a S28_G6.  
- Notas de risco e pendências registradas.

**Critérios de PASS**
- Todos os gates G0–G6 com `status = "PASS"`.  
- Geração de `out/scorecards/S28_overall.json` contendo:
  - `status` geral (`GO` ou `NO_GO`),  
  - lista de gates com status,  
  - resumo dos estados-alvo atingidos,  
  - avaliação de risco (P0/P1/P2) com plano claro para qualquer item remanescente (P2 somente, sem impacto em operação básica).  
- Assinatura (explícita ou implícita) da liderança técnica do squad e, se aplicável, de quem responde pelo Programa 1.

**Falha (FAIL) se**
- Houver qualquer gate anterior em `FAIL`.  
- Houver riscos P0/P1 sem plano resolutivo dentro da própria sprint.

---

## 2.3 Métricas-chave da Sprint 28

Além dos gates binários, a Sprint 28 acompanha algumas métricas qualitativas/quantitativas:

1. **Cobertura de testes**  
   - Domínio de fontes (`tests/domain/...`): cobertura das invariantes principais.  
   - API de admin (`tests/api/...`): cobertura de casos felizes, inválidos e de erro.  
   - Integração ON/OFF × Ingestão (`tests/integration/...`).  
   - UI (tests de console): fluxos A–D (casos canônicos) cobertos.

2. **Tempo de operação de ON/OFF (percepção operacional)**  
   - Medida qualitativa: durante a demo e testes internos, qual a percepção do operador sobre:
     - rapidez,  
     - previsibilidade,  
     - clareza do efeito de desligar/ligar fonte.

3. **Número de regressões de legado (S21/S22)**  
   - Ideal: zero.  
   - Se aparecer, deve ser tratado como bug crítico dentro da sprint.

4. **Feedback de UX do console de fontes v2**  
   - Coletado no G6, resumido em 3 perguntas:
     - “O que ficou ótimo?”  
     - “O que ainda dói?”  
     - “O que é inaceitável para operação real?”

Essas métricas não substituem os gates, mas ajudam a calibrar qualidade e orientar sprints seguintes.

---

## 2.4 Definition of Done (DoD) global da Sprint 28

A Sprint 28 é considerada **DONE** somente se todas as condições abaixo forem verdadeiras:

1. **Gates**  
   - S28_G0…S28_G7 em `PASS`.  
   - `out/scorecards/S28_overall.json` com `status = "GO"`.

2. **Domínio & DB**  
   - Modelo de `Source` consolidado, com enums e campos conforme especificado.  
   - Migrations aplicadas e documentadas, sem pendências de dados órfãos ou campos ilegais.

3. **API**  
   - `/admin/sources` oferece CRUD & ON/OFF completo, validado por testes e OpenAPI.  
   - Não há rotas "secretas" ou inconsistentes usadas apenas por scripts internos.

4. **Console de Fontes v2**  
   - Fluxos canônicos (A–D) funcionam integralmente pela UI.  
   - Console usa componentes do Design System Admin v1, sem criar um espaço visual alienígena.

5. **ON/OFF × Ingestão 2.0**  
   - ON/OFF de fonte é normativo: não há divergência entre estado de fonte e comportamento do scheduler.  
   - Casos de teste e logs provam o comportamento esperado.

6. **Sanidade de legado**  
   - Gates relevantes de S21/S22 em PASS.  
   - Nenhuma regressão crítica introduzida por S28.

7. **Documentação & evidências**  
   - Cap. 1–4 da Sprint 28 atualizados e coerentes com o código.  
   - Evidências de gates organizadas em `out/evidence/S28_G*/**`.  
   - Scorecards em `out/scorecards/S28_G*.json` e `S28_overall.json` presentes e consistentes.

8. **Backlog & ganchos futuros**  
   - Descobertas fora de escopo foram registradas e roteadas para E27.2/E27.3/E29–E32.  
   - Não ficou nada crítico "pendurado" sem dono ou sem épico relacionado.

---

Com este Capítulo 2, a Sprint 28 ganha um conjunto de **regras de validação explícitas**: não basta “parecer pronto” — cada aspecto central (modelo, API, console, ON/OFF, legado) precisa passar por um gate verificável, com evidência concreta e decisão formalizada em scorecards.