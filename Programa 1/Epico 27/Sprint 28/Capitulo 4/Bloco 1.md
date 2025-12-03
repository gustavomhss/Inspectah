# Inspectah — Sprint 28
## Capítulo 4 — Bloco 1
### Estratégia de Execução, Fases da Sprint e Organização de Trabalho

---

#### 4.1.1 Objetivo deste bloco

Este bloco responde, de forma operacional, às perguntas:

> “Como a Sprint 28 vai ser executada dia a dia?”  
> “Quem faz o quê, em que ordem, e como garantimos que nada crítico fique de fora?”

Ele não reespecifica o **QUE** (isso está nos Capítulos 1, 2 e 3), mas detalha **COMO** o time vai sair do zero até o GO, com:

- fases claras de execução,  
- sequência de estabilização dos gates,  
- organização de branch/PRs,  
- papéis e responsabilidades.

---

#### 4.1.2 Fases de execução da Sprint 28 (visão macro)

A Sprint 28 é quebrada em 5 fases, cada uma associada a um conjunto de gates e entregáveis:

1. **Fase 0 — Preparação & G0 (Fundação da sprint)**  
   - Consolidar documentação da sprint (Cap. 1–4).  
   - Criar/confirmar branch de trabalho.  
   - Garantir que estrutura de evidências e scorecards está pronta.  
   - Gate-alvo: **S28_G0_scope_and_baseline** em PASS.

2. **Fase 1 — Domínio & Schema (Backend Core) — G1**  
   - Consolidar modelo `Source`, enums e migrations.  
   - Garantir invariantes de domínio testadas.  
   - Gate-alvo: **S28_G1_sources_model_and_schema** em PASS.

3. **Fase 2 — Admin API & Ingestão 2.0 — G2 + G4**  
   - Implementar/ajustar rotas `/admin/sources`.  
   - Conectar o scheduler ao novo modelo (`mode` + `state`).  
   - Escrever testes de API e integração ON/OFF × ingestão.  
   - Gates-alvo: **S28_G2_sources_admin_api** e **S28_G4_sources_ingestion_integration** em PASS.

4. **Fase 3 — Console de Fontes v2 & UX — G3 + G6**  
   - Implementar/ajustar páginas, componentes e cliente de API no frontend.  
   - Escrever testes de UI/e2e.  
   - Rodar demo interna com operadores (G6).  
   - Gates-alvo: **S28_G3_sources_console_front** e **S28_G6_demo_internal** em PASS.

5. **Fase 4 — Sanidade de legado, ORR & GO/NO_GO — G5 + G7**  
   - Rodar gates de S21/S22 (fontes + ingestão) no código pós-S28.  
   - Consolidar scorecards, riscos e decisão final.  
   - Gates-alvo: **S28_G5_observability_and_legacy_sanity** e **S28_G7_go_no_go** em PASS, com `S28_overall.status = "GO"`.

A ordem de estabilização dos gates segue a dependência natural de arquitetura:

> **G0 → G1 → (G2, G4 em paralelo) → G3 → G5 → G6 → G7**

---

#### 4.1.3 Linha do tempo sugerida (sem datas rígidas)

Sem amarrar a datas específicas, o ritmo recomendado é:

- **Início da sprint**  
  - Focar em Fase 0 e Fase 1.  
  - Objetivo: documentos estáveis + modelo `Source` consolidado **antes** de sair codando API/console.

- **Terço inicial da sprint**  
  - Fase 1 encerrada (G1 em PASS).  
  - Backend pronto para receber API e ingestão.

- **Meio da sprint**  
  - Fase 2 em andamento forte (G2 + G4).  
  - Admin API funcional, testes de API escritos.  
  - Scheduler respeitando `mode` + `state`, com testes de integração rodando.

- **Terço final da sprint**  
  - Fase 3 (frontend + demo) e Fase 4 (legado + GO/NO_GO).  
  - Console de fontes v2 utilizável, testes de UI verdes.  
  - Demo feita, feedback capturado.  
  - Gates de legado rodados e S28_overall consolidado.

Esse plano reduz risco de chegar no final da sprint com UI semi-pronta, mas sem backend sólido ou ingestão quebrada.

---

#### 4.1.4 Organização de branches e PRs

##### Branch principal da sprint

- Nome sugerido:  
  - `feature/s28_sources_crud_onoff`

Essa branch é o "tronco" da sprint. Nada vai direto para `main` antes de S28_G7 = GO.

##### Sub-branches por foco (opcionais, mas recomendadas)

Para desacoplar um pouco o fluxo de trabalho entre pessoas, a sprint pode usar sub-branches que convergem em `feature/s28_sources_crud_onoff`:

- `feature/s28_backend_sources_model_api`  
  - Tudo relacionado a `Source`, enums, migrations, Admin API.  
  - Concentra Fase 1 + parte da Fase 2.

- `feature/s28_ingestion_onoff`  
  - Ajustes no scheduler, seleção de fontes elegíveis, testes de integração.  
  - Fase 2 focada em G4.

- `feature/s28_frontend_sources_console`  
  - Implementação do console de fontes v2 e testes de UI.  
  - Fase 3.

Fluxo sugerido:
1. Cada sub-branch evolui com commits pequenos e PRs internos.  
2. Quando um conjunto está estável, é feito merge na branch principal da sprint.  
3. A branch principal é a base para rodar os gates e o workflow de CI.

##### Política de PRs

- PRs devem:
  - referenciar explicitamente gates ou partes da sprint (ex.: "S28_G2 — Admin API"),  
  - incluir link para evidências locais (logs de teste, prints de UI, etc.),  
  - ser pequenos o suficiente para revisão real, não dumps gigantes.

- Merges na branch da sprint só após:
  - testes relevantes em PASS localmente,  
  - revisão de pelo menos uma outra pessoa (ou do "Tech Lead"),  
  - ausência de violações óbvias de arquitetura (ver Cap. 3).

---

#### 4.1.5 Papéis e responsabilidades dentro da sprint

Sem atrelar a nomes, a S28 assume alguns papéis claros. Uma mesma pessoa pode acumular mais de um papel, mas os **chapéus conceituais** são diferentes.

##### Backend Owner — Domínio & Admin API

Responsabilidades:
- Modelar e manter `Source`, enums e migrations (`app/sources/models.py`, `migrations/versions/...`).  
- Implementar e estabilizar rotas `/admin/sources` (`app/api/admin_sources_routes.py`).  
- Escrever e manter testes de domínio e API (`tests/domain/...`, `tests/api/...`).  
- Garantir gates **S28_G1** e **S28_G2** verdes.

##### Backend Owner — Ingestão 2.0

Responsabilidades:
- Ajustar o scheduler e serviços de ingestão (`app/ingestion/scheduler.py` e adjacentes).  
- Garantir que critérios de elegibilidade (`mode`, `state`, filtros de S22) estão corretos.  
- Escrever testes de integração ON/OFF (`tests/integration/test_sources_ingestion_onoff.py`).  
- Garantir gate **S28_G4** verde.

##### Frontend Owner — Console de Fontes v2

Responsabilidades:
- Implementar/ajustar páginas e componentes (`SourcesListPage`, `SourceFormPage`, `SourceListTable`, `SourceStateBadge`, `SourceActionsMenu`).  
- Conectar o console ao `adminSourcesApi`.  
- Escrever/ajustar testes de UI/e2e (`frontend/inspectah-ui/tests/sources/...`).  
- Garantir gate **S28_G3** verde.

##### QA / ORR Owner — Gates, Evidências & Demo

Responsabilidades:
- Orquestrar execução dos scripts `bin/s28_gX_*.sh`.  
- Garantir que `out/evidence/S28_G*/**` e `out/scorecards/S28_G*.json` estão organizados.  
- Ajudar a preparar e conduzir a demo interna (G6), registrando feedback.  
- Consolidar `S28_overall.json` e coordenar documentação de resultados.

##### Tech Lead / Sprint Owner — Coesão & Decisão

Responsabilidades:
- Proteger a sprint contra escopo extra não planejado (gold plating fora de hora).  
- Tomar decisões de trade-off (o que empurrar para E27.2/E27.3).  
- Revisar se o que foi implementado bate com Cap. 1–3.  
- Dar o veredito final GO/NO_GO em S28_G7, com base em evidências.

---

#### 4.1.6 Regras de ouro da execução da Sprint 28

Para manter a sprint saudável e alinhada ao resto do projeto Inspectah, algumas regras simples valem como "lei":

1. **Nenhum gate em vermelho é ignorado**  
   - Falha em qualquer `bin/s28_gX_*.sh` é, por definição, um bloqueio.  
   - O time corrige a causa-raiz, não o script.

2. **Nenhuma mutação de fonte fora da Admin API**  
   - Mesmo em teste/manual, mudanças relevantes em fontes devem passar pela API.  
   - Isso garante que invariantes e logs sejam sempre respeitados.

3. **Frontend nunca implementa regra de negócio sozinho**  
   - Validação extra para UX é bem-vinda, mas a regra "real" mora no backend.  
   - Se houver divergência, backend vence.

4. **Ingestão não ignora `state` e `mode` por nenhum motivo**  
   - Se uma fonte `DISABLED` for ingerida, isso é bug crítico.  
   - S28 só é GO quando esse risco estiver controlado por código e testes.

5. **Docs acompanham o código, não ficam defasados**  
   - Mudou algo estrutural em modelo/API/console/gates?  
   - Atualiza Cap. 1–4 antes de declarar gate em PASS.

---

Com este Bloco 1, o Capítulo 4 da Sprint 28 ganha uma base sólida de execução: fases bem definidas, linha do tempo, organização de branches, papéis claros e regras de ouro que orientam o dia a dia da sprint. Os próximos blocos podem agora descer para o nível de plano por gate, comandos concretos, uso de CI e checklists de GO/NO_GO.

