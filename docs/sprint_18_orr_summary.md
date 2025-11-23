# Sprint 18 – Console de Admin / Painel de Operação

## Objetivo

A Sprint 18 teve como objetivo colocar em produção o **Console de Admin** do Inspectah, um cockpit de operação dentro da mesma SPA usada pelos usuários finais. O foco é leitura: uma visão geral da saúde do sistema, listagens de Fontes e Casos/Temas e links rápidos para evidências, sempre a partir de **estados consolidados** da Truth-DB / Sistema de Blocos.  
Nenhuma mutação é feita via Console de Admin nesta sprint: o recorte é puramente read-heavy, para que um operador consiga, em menos de 1 minuto, entender a situação de fontes degradadas, casos em atenção e problemas operacionais sem ter que abrir logs ou scorecards brutos.

Funcionalidades explicitamente fora de escopo da S18 (empurradas para sprints seguintes):

- Timeline detalhada / “raio-X” por caso (S19).
- Tuning de parâmetros avançados / knobs operacionais (S19/S20).
- Autenticação/autorização completa e perfis de acesso (S20).

Nesta sprint, o objetivo é ter um cockpit **funcional, navegável e confiável**, ainda que sem todo o acabamento visual ou features avançadas de governança.

## Estado dos gates S18_G0…S18_G8

A Sprint 18 define nove gates principais:

- S18_G0 – Scope e sanidade da sprint.
- S18_G1 – Arquitetura front + API de admin (presença e wiring).
- S18_G2 – Jornadas de UX de admin (Operador/Curador/PO).
- S18_G3 – Qualidade de frontend (lint, testes, build).
- S18_G4 – Coerência UI ↔ backend (cobertura de Fontes/Casos).
- S18_G5 – Health mapping (Visão Geral vs /admin/health).
- S18_G6 – Métricas e demo end-to-end (alerta → fonte / alerta → caso).
- S18_G7 – CI e observabilidade mínima plugada.
- S18_G8 – GO/NO-GO da sprint.

Resultado da execução oficial:

- `PYTHONPATH=. bash bin/s18_all.sh` executou **G0…G7** em sequência, todos com status **PASS**, gerando scorecards em `out/scorecards/S18_G*.json` e evidências em `out/evidence/S18_G*/`.
- `PYTHONPATH=. bash bin/s18_g8_go_no_go.sh` produziu `out/scorecards/S18_G8_go_no_go.json` com:

```json
{
  "gate_id": "S18_G8",
  "status": "PASS",
  "decision": "GO",
  "metrics": {
    "M3": 1.0,
    "M4": 1.0,
    "M1": 0.0279,
    "M2": 0.0378,
    "M5": 1.0,
    "M6": 1.0
  },
  "details": {
    "failures": []
  }
}
```

Interpretação de alto nível:

* M3 (cobertura de fontes na UI) = 1.0: tudo que importa no recorte da S18 está visível no Console de Admin.
* M4 (cobertura de casos/temas) = 1.0: mesma ideia, mas do lado de casos.
* M5 (profundidade de explicação) = 1.0: os casos exibidos trazem contexto e explicação suficiente para não obrigar o operador a caçar detalhes brutos diretamente.
* M6 (evidência em ≤ 2 cliques) = 1.0: o caminho tela → evidência está dentro da regra de até dois passos.
* M1 ≈ 0,028 s e M2 ≈ 0,038 s: tempos de resposta medidos nos cenários de health e “alerta → fonte/caso” estão muito abaixo de qualquer SLA razoável para o recorte atual.

Com todos os gates G0…G7 em PASS e decisão **GO** em G8, a S18 está operacionalmente aprovada.

## Entregas principais

### Backend (admin)

* Módulo de admin em `app/admin/` expandido para suportar o Console de Admin, com leitura a partir de estados consolidados (storage + snapshots da S12).

* Schemas Pydantic de admin para fontes, casos e health agregada.

* Endpoints FastAPI registrados em `inspectah/api.py`:

  * `GET /admin/sources`
  * `GET /admin/sources/{id}`
  * `GET /admin/cases`
  * `GET /admin/cases/{id}`
  * `GET /admin/health`

* Lógica de agregação de health que usa `list_admin_sources()` e `list_admin_cases()` como fonte de verdade para a visão de cockpit.

* Testes dedicados em `tests/admin/test_admin_endpoints.py` cobrindo listagem de fontes, listagem+detalhe de casos, health e cenários 404 básicos; todos passando com `PYTHONPATH=. python3 -m pytest tests/admin/test_admin_endpoints.py`.

### Frontend (Console de Admin)

* SPA em `frontend/inspectah-ui` estendida com namespace de admin.

* Tipos e cliente de API em `src/types/admin.ts` e `src/api/admin/index.ts`.

* Páginas:

  * `AdminLayout`
  * `AdminOverviewPage` (Visão Geral / health)
  * `AdminSourcesPage` / `AdminSourceDetailPage`
  * `AdminCasesPage` / `AdminCaseDetailPage`

* Componentes em `src/components/admin/` para cards de health, tabelas de fontes/casos, badges de status/risco e estados de loading/erro/empty.

* Rotas de admin integradas em `src/App.tsx`, com navegação `/admin`, `/admin/sources`, `/admin/sources/:id`, `/admin/cases`, `/admin/cases/:id`.

* Testes de frontend em `src/__tests__/admin/AdminPages.test.tsx` com Vitest + MSW, exercitando overview e fontes; `npm run lint`, `npm run test -- --watch=false` e `npm run build` passando.

### Gates e CI

* Scripts da S18 criados em `bin/`:

  * `s18_g0_scope.sh` … `s18_g7_ci_and_observability.sh`
  * `s18_g8_go_no_go.sh`
  * `s18_all.sh` (orquestrador G0…G7)

* Scorecards da S18 em `out/scorecards/S18_G*.json`.

* Evidências em `out/evidence/S18_G*/` (openapi snapshot, logs de build/test, snapshots UI↔backend, cenários de jornada, resumos de CI).

* Workflow de CI `_s18_admin_front.yml` em `.github/workflows/`, rodando `bin/s18_g3_front_quality.sh` e publicando artefatos, com G7 validando essa integração.

## Riscos, limitações e débitos empurrados

* Avisos de Pydantic V1→V2 (validators/config) aparecem na suíte, mas são **warnings**, não erros. A migração completa para o estilo V2 é tratada como débito técnico fora do escopo da S18.
* Admin ainda é somente leitura: qualquer necessidade de reconfiguração de fontes, tuning de parâmetros ou gestão de usuários será tratada em sprints futuras (S19/S20).
* O Console de Admin ainda não traz a timeline completa de blocos nem visualizações avançadas; isso faz parte do roadmap posterior para “raio-X” detalhado e modo forense.

## Conclusão

A Sprint 18 entrega um **Console de Admin funcional, testado e medido**, com backend e frontend integrados, gates completos e decisão GO automatizada.
Operadores e curadores passam a ter um ponto único de observação da saúde do Inspectah, com métricas M1…M6 cobertas no recorte definido, preparando o terreno para as próximas sprints focadas em timeline detalhada, tuning e governança avançada.

```