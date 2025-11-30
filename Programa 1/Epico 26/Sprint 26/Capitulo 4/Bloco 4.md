# Inspectah — Sprint 26 (S26)
## Capítulo 4 — Bloco 4.4
### Plano Operacional & Tasks da Sprint 26

> Arquivo-alvo no repo: `docs/s26_cap_4_4_plano_operacional_e_tasks.md`
>
> Função: transformar waves, filemap, gates e plano de evidências em um **plano operacional concreto**, organizado em tasks `S26-T-XXX`. Este bloco é o “como exatamente executar” a S26, tanto para humanos quanto para Codex, sem espaço para freestyle.

---

## 1. Convenções de Tasks da S26

Cada task segue a convenção:

- **ID**: `S26-T-XXX` (ex.: `S26-T-012`).
- **Wave**: `W0`, `W1`, `W2` ou `W3` (Cap.4.1).
- **Categoria**: `frontend`, `backend`, `ci`, `docs`, `gates`, `ops`.
- **Descrição**: verbo no infinitivo + objeto claro (o que fazer).
- **Artefatos**: arquivos/pastas a tocar (Cap.3) + scripts/gates (Cap.2) + pasta de evidências (Cap.4.3).
- **Gates**: quais gates S26 a task influencia direta ou indiretamente.
- **Dependências**: tasks ou estados que precisam estar prontos antes.

Exemplo de formato no `.md`:

```text
- ID: S26-T-010
  Wave: W1
  Categoria: frontend
  Descrição: criar esqueleto do Design System Admin v1 em ui/admin
  Artefatos:
    - frontend/inspectah-ui/src/ui/admin/**
    - bin/s26_g1_design_system_static.sh
    - out/evidence/S26_G1_design_system_static/
  Gates: [G0, G1, G3]
  Dependências: [S26-T-001]
```

O restante deste bloco lista as **tasks principais** da S26, organizadas por wave, e encerra com checklists de fechamento por wave.

---

## 2. Tasks da Wave W0 — Grounding & Sanidade

### S26-T-001 — Consolidar resumo de S26 (Grounding)

- Wave: W0  
- Categoria: docs  
- Descrição: consolidar resumo estruturado da S26 (Cap.1–3 + Cap.4.1) em doc de grounding.  
- Artefatos:  
  - `docs/s26_cap_0_notas_de_grounding.md` (ou equivalente);  
  - leitura de `inspectah_sprint_26_cap_1_*.md`, `inspectah_sprint_26_cap_2_*.md`, `inspectah_sprint_26_cap_3_*.md`, `docs/s26_cap_4_1_plano_de_waves.md`.  
- Gates: [G0] (contexto para scripts, sem impacto numérico direto).  
- Dependências: nenhuma.

### S26-T-002 — Verificar estado inicial do repo para S26

- Wave: W0  
- Categoria: ops  
- Descrição: inspecionar estrutura atual do repo e confirmar presença mínima de pastas S26.  
- Artefatos:  
  - comandos: `git status`, `ls -R docs/`, `ls -R frontend/inspectah-ui/src/`, `ls -R app/`;  
  - registro em `docs/s26_cap_0_notas_de_grounding.md`.  
- Gates: [G0].  
- Dependências: [S26-T-001].

### S26-T-003 — Rodar primeira fotografia de G0 (Scope & Baseline)

- Wave: W0  
- Categoria: gates/ci  
- Descrição: rodar `bin/s26_g0_scope_and_baseline.sh` no estado inicial do repo e guardar logs como baseline.  
- Artefatos:  
  - `bin/s26_g0_scope_and_baseline.sh`;  
  - `out/evidence/S26_G0_scope_and_baseline/g0_scope_and_baseline.log`;  
  - `out/scorecards/S26_G0_scope_and_baseline.json`.  
- Gates: [G0].  
- Dependências: [S26-T-002].

---

## 3. Tasks da Wave W1 — Fundação de Design System & Filemap

### S26-T-010 — Criar esqueleto de `ui/admin` (Design System Admin v1)

- Wave: W1  
- Categoria: frontend  
- Descrição: criar a árvore base do Design System Admin v1 conforme Cap.3.2.  
- Artefatos:  
  - `frontend/inspectah-ui/src/ui/admin/tokens/` (arquivos vazios ou mínimos: `colors.ts`, `typography.ts`, `spacing.ts`, `radius.ts`, `shadows.ts`, `zIndex.ts`, `index.ts`);  
  - `frontend/inspectah-ui/src/ui/admin/layout/` (`AdminShell.tsx`, `AdminSidebar.tsx`, `AdminHeader.tsx`, `AdminContent.tsx`, `SidebarNavItem.tsx`, `index.ts`);  
  - `frontend/inspectah-ui/src/ui/admin/components/` (`Button.tsx`, `Input.tsx`, `Select.tsx`, `Table.tsx`, `Badge.tsx`, `Modal.tsx`, `Toast.tsx`, `Banner.tsx`, `FormField.tsx`, `index.ts`);  
  - `frontend/inspectah-ui/src/ui/admin/hooks/` (se necessário) + `index.ts`;  
  - `frontend/inspectah-ui/src/ui/admin/index.ts`.  
- Gates: [G0, G1, G3].  
- Dependências: [S26-T-003].

### S26-T-011 — Definir tokens base de design admin

- Wave: W1  
- Categoria: frontend  
- Descrição: implementar tokens base de cores, tipografia e spacing em `ui/admin/tokens`.  
- Artefatos:  
  - `frontend/inspectah-ui/src/ui/admin/tokens/colors.ts`;  
  - `frontend/inspectah-ui/src/ui/admin/tokens/typography.ts`;  
  - `frontend/inspectah-ui/src/ui/admin/tokens/spacing.ts`;  
  - `frontend/inspectah-ui/src/ui/admin/tokens/index.ts`.  
- Gates: [G1, G3].  
- Dependências: [S26-T-010].

### S26-T-012 — Esqueleto de `features/sources` (Console de Fontes v2)

- Wave: W1  
- Categoria: frontend  
- Descrição: criar estrutura base do Console de Fontes v2 conforme Cap.3.3.  
- Artefatos:  
  - `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`;  
  - `frontend/inspectah-ui/src/features/sources/pages/SourceEditPage.tsx`;  
  - `frontend/inspectah-ui/src/features/sources/components/SourcesTable.tsx`;  
  - `frontend/inspectah-ui/src/features/sources/components/SourceForm.tsx`;  
  - `frontend/inspectah-ui/src/features/sources/components/SourceStatusBadge.tsx`;  
  - `frontend/inspectah-ui/src/features/sources/api/sourcesApi.ts`;  
  - `frontend/inspectah-ui/src/features/sources/types/Source.ts`;  
  - `frontend/inspectah-ui/src/features/sources/index.ts`.  
- Gates: [G0, G2, G3].  
- Dependências: [S26-T-010].

### S26-T-013 — Ajustar scripts de gates S26 para novo filemap

- Wave: W1  
- Categoria: gates/ci  
- Descrição: ajustar scripts `bin/s26_g0_*.sh`, `bin/s26_g1_*.sh`, `bin/s26_g2_*.sh`, `bin/s26_g3_*.sh` para reconhecer `ui/admin` e `features/sources`.  
- Artefatos:  
  - `bin/s26_g0_scope_and_baseline.sh`;  
  - `bin/s26_g1_design_system_static.sh`;  
  - `bin/s26_g2_sources_console_flows.sh`;  
  - `bin/s26_g3_frontend_quality.sh`;  
  - evidências: `out/evidence/S26_G0*/`, `S26_G1*/`, `S26_G2*/`, `S26_G3*/`.  
- Gates: [G0, G1, G2, G3].  
- Dependências: [S26-T-010, S26-T-012].

### S26-T-014 — Validar G0/G1/G3 com estrutura nova

- Wave: W1  
- Categoria: gates/ci  
- Descrição: rodar G0, G1 e G3 após criação do filemap para validar integridade mínima.  
- Artefatos:  
  - logs em `out/evidence/S26_G0*/`, `S26_G1*/`, `S26_G3*/`;  
  - scorecards `S26_G0*.json`, `S26_G1*.json`, `S26_G3*.json`.  
- Gates: [G0, G1, G3].  
- Dependências: [S26-T-011, S26-T-012, S26-T-013].

---

## 4. Tasks da Wave W2 — Console de Fontes v2 & Contratos de Fontes

### S26-T-030 — Implementar `SourcesListPage` com Design System Admin v1

- Wave: W2  
- Categoria: frontend  
- Descrição: implementar `SourcesListPage` usando `AdminShell`, `AdminHeader`, `AdminContent` e `SourcesTable`.  
- Artefatos:  
  - `frontend/inspectah-ui/src/features/sources/pages/SourcesListPage.tsx`;  
  - imports de `@/ui/admin`.  
- Gates: [G2, G3].  
- Dependências: [S26-T-011, S26-T-012, S26-T-014].

### S26-T-031 — Implementar `SourceEditPage` + `SourceForm`

- Wave: W2  
- Categoria: frontend  
- Descrição: implementar `SourceEditPage` e `SourceForm` com componentes do design system, incluindo validações básicas.  
- Artefatos:  
  - `frontend/inspectah-ui/src/features/sources/pages/SourceEditPage.tsx`;  
  - `frontend/inspectah-ui/src/features/sources/components/SourceForm.tsx`.  
- Gates: [G2, G3].  
- Dependências: [S26-T-011, S26-T-012].

### S26-T-032 — Implementar `SourceStatusBadge` e integração com `Badge`

- Wave: W2  
- Categoria: frontend  
- Descrição: implementar `SourceStatusBadge` usando `Badge` de `@/ui/admin` para refletir estados de fonte.  
- Artefatos:  
  - `frontend/inspectah-ui/src/features/sources/components/SourceStatusBadge.tsx`;  
  - ajustes em `ui/admin/components/Badge.tsx` se necessário.  
- Gates: [G1, G2, G3].  
- Dependências: [S26-T-011, S26-T-012].

### S26-T-033 — Implementar `sourcesApi.ts` (client de API de fontes)

- Wave: W2  
- Categoria: frontend/backend  
- Descrição: implementar funções tipadas em `sourcesApi.ts` para listar, criar, editar e mudar status de fontes.  
- Artefatos:  
  - `frontend/inspectah-ui/src/features/sources/api/sourcesApi.ts`;  
  - `frontend/inspectah-ui/src/features/sources/types/Source.ts`.  
- Gates: [G2, G4].  
- Dependências: [S26-T-012, S26-T-040].

### S26-T-040 — Ajustar rotas e schemas de fontes no backend

- Wave: W2  
- Categoria: backend  
- Descrição: garantir que `app/sources/models.py`, `schemas.py` e `routes.py` expõem os contratos esperados pelo Console de Fontes v2.  
- Artefatos:  
  - `app/sources/models.py`;  
  - `app/sources/schemas.py`;  
  - `app/sources/routes.py` (ou `routers/sources.py`).  
- Gates: [G2, G4].  
- Dependências: [S26-T-014].

### S26-T-041 — Criar/ajustar testes de API de fontes (`test_sources_console.py`)

- Wave: W2  
- Categoria: backend/tests  
- Descrição: escrever testes de API cobrindo fluxos do Console de Fontes v2 (listar, criar, editar, ativar, desativar, arquivar).  
- Artefatos:  
  - `tests/api/test_sources_console.py`;  
  - logs em `out/evidence/S26_G4_sources_api_contracts/`.  
- Gates: [G4].  
- Dependências: [S26-T-040].

### S26-T-042 — Criar/ajustar testes de flows do Console de Fontes (G2)

- Wave: W2  
- Categoria: frontend/tests  
- Descrição: criar testes automatizados (unit/integration/e2e) cobrindo os fluxos básicos do Console de Fontes v2.  
- Artefatos:  
  - arquivos de teste em `frontend/inspectah-ui/src/features/sources/__tests__/` ou equivalente;  
  - logs em `out/evidence/S26_G2_sources_console_flows/`.  
- Gates: [G2].  
- Dependências: [S26-T-030, S26-T-031, S26-T-033].

### S26-T-043 — Validar G2 e G4 em conjunto

- Wave: W2  
- Categoria: gates/ci  
- Descrição: rodar `bin/s26_g2_sources_console_flows.sh` e `bin/s26_g4_sources_api_contracts.sh` e registrar evidências.  
- Artefatos:  
  - `out/evidence/S26_G2_sources_console_flows/*`;  
  - `out/evidence/S26_G4_sources_api_contracts/*`;  
  - scorecards `S26_G2*.json`, `S26_G4*.json`.  
- Gates: [G2, G4].  
- Dependências: [S26-T-041, S26-T-042].

---

## 5. Tasks da Wave W3 — Hardening, UX mínima & Evidências finais

### S26-T-050 — Refinar UX do Console de Fontes v2

- Wave: W3  
- Categoria: frontend  
- Descrição: aplicar melhorias de UX acordadas (mensagens de erro, estados vazios, loaders, detalhes de usabilidade) dentro do escopo de S26.  
- Artefatos:  
  - ajustes em `SourcesListPage.tsx`, `SourceEditPage.tsx`, `SourcesTable.tsx`, `SourceForm.tsx`;  
  - opcionalmente, notas de UX em `out/evidence/S26_G3_frontend_quality/ux_notes_*.md`.  
- Gates: [G2, G3].  
- Dependências: [S26-T-030, S26-T-031, S26-T-042].

### S26-T-051 — Escrever guia do Design System Admin v1

- Wave: W3  
- Categoria: docs  
- Descrição: documentar o Design System Admin v1 (objetivo, organização, como usar, exemplos).  
- Artefatos:  
  - `docs/design_system_admin_v1.md`;  
  - logs de verificação em `out/evidence/S26_G5_docs_and_runbooks/g5_docs_check.log`.  
- Gates: [G5].  
- Dependências: [S26-T-010, S26-T-011, S26-T-014].

### S26-T-052 — Escrever runbook de operação de fontes

- Wave: W3  
- Categoria: docs  
- Descrição: produzir runbook operacional para o Console de Fontes v2 (como usar, cuidados, cenários comuns).  
- Artefatos:  
  - `docs/runbook_operacao_fontes_v1.md`;  
  - logs de verificação em `out/evidence/S26_G5_docs_and_runbooks/g5_docs_check.log`.  
- Gates: [G5].  
- Dependências: [S26-T-030 a T-043].

### S26-T-053 — Rodar G5 (Documentação & Runbooks)

- Wave: W3  
- Categoria: gates/ci  
- Descrição: rodar `bin/s26_g5_docs_and_runbooks.sh` após finalização de docs.  
- Artefatos:  
  - `out/evidence/S26_G5_docs_and_runbooks/*`;  
  - `out/scorecards/S26_G5_docs_and_runbooks.json`.  
- Gates: [G5].  
- Dependências: [S26-T-051, S26-T-052].

### S26-T-054 — Rodar `s26-gates` completo e gerar bundle (G6)

- Wave: W3  
- Categoria: gates/ci  
- Descrição: executar sequência G0–G6 na branch de release e gerar bundle final de evidências.  
- Artefatos:  
  - logs em `out/evidence/S26_G0*/` … `S26_G6*/`;  
  - `out/scorecards/S26_G0*.json` … `S26_G6*.json`;  
  - `out/bundles/inspectah_s26_evidence_bundle.zip`;  
  - `out/evidence/S26_G6_orr_bundle/g6_bundle_sha256.txt`.  
- Gates: [G0, G1, G2, G3, G4, G5, G6].  
- Dependências: [S26-T-014, S26-T-043, S26-T-053].

### S26-T-055 — Registrar ORR local da S26 (GO/NO-GO)

- Wave: W3  
- Categoria: docs/ops  
- Descrição: conduzir ORR local com base nos scorecards e evidências e registrar o veredito.  
- Artefatos:  
  - `docs/s26_cap_5_orr_local_summary.md`;  
  - referência ao bundle `inspectah_s26_evidence_bundle.zip`.  
- Gates: [G6] (e resultado final da sprint).  
- Dependências: [S26-T-054].

### S26-T-056 — Registrar débitos e gaps da S26

- Wave: W3  
- Categoria: docs  
- Descrição: consolidar débitos técnicos, gaps funcionais e aprendizados em doc de lições aprendidas.  
- Artefatos:  
  - `docs/s26_cap_6_lessons_learned_e_gaps.md`;  
  - referências cruzadas para tasks não concluídas, se houver.  
- Gates: (não bloqueia GO, mas influencia planejamento futuro).  
- Dependências: [S26-T-055].

---

## 6. Checklists de Encerramento por Wave

### W0 — Grounding & Sanidade

- [ ] `S26-T-001` concluída (notas de grounding salvas).  
- [ ] `S26-T-002` concluída (estado inicial do repo documentado).  
- [ ] `S26-T-003` executada (G0 baseline rodado, scorecard + evidências presentes).

### W1 — Fundação de Design System & Filemap

- [ ] `S26-T-010` a `S26-T-014` concluídas.  
- [ ] Filemap de `ui/admin` e `features/sources` igual ao descrito em Cap.3.2/3.3.  
- [ ] G0/G1/G3 executam até o fim, mesmo que com falhas de implementação já mapeadas para W2/W3.

### W2 — Console de Fontes v2 & Contratos de Fontes

- [ ] `S26-T-030` a `S26-T-043` concluídas.  
- [ ] Fluxos básicos do Console de Fontes v2 navegáveis (lista/criar/editar/ativar/desativar/arquivar).  
- [ ] G2 e G4 em estado GREEN ou com falhas explícitas e plano de correção previsto em W3.

### W3 — Hardening, UX mínima & Evidências finais

- [ ] `S26-T-050` a `S26-T-056` concluídas.  
- [ ] G0–G6 em estado GREEN.  
- [ ] Bundle `inspectah_s26_evidence_bundle.zip` gerado e hash registrado.  
- [ ] ORR local da S26 registrado como GO/NO-GO em `s26_cap_5_orr_local_summary.md`.  
- [ ] Débitos/gaps anotados em `s26_cap_6_lessons_learned_e_gaps.md`.

---

## 7. Síntese do Bloco 4.4

O Bloco 4.4 amarra toda a S26 em um **roteiro executável**:

- tasks com IDs claras, ligadas a waves, categorias, artefatos, gates e evidências;  
- checklists de encerramento por wave, garantindo cadência W0 → W1 → W2 → W3;  
- ligação direta entre Cap.1–3 (o que queremos), Cap.2 (como medimos), Cap.4.1–4.3 (como executamos e evidenciamos) e Cap.5–6 (como julgamos e aprendemos).

A partir deste plano, Codex e humanos conseguem executar a S26 de forma disciplinada, auditável e alinhada com o padrão de excelência do Programa 1.

