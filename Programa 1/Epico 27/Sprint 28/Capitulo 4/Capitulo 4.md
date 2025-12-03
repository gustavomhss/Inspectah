# Inspectah — Sprint 28
## Capítulo 4 — Execução, Evidências e ORR da Sprint
### E27.1 — CRUD & ON/OFF de Fonte

---

## 4.1 Estratégia de execução da Sprint 28

A Sprint 28 mexe em uma parte sensível da operação (fontes + ON/OFF + ingestão). A execução precisa evitar retrabalho, conflitos entre backend e frontend e, principalmente, mudanças não testadas no scheduler.

A estratégia é organizada em **5 fases**, cada uma com saídas claras e gates associados:

1. **Fase 0 — Preparação & S28_G0**  
   - Garantir que Capítulos 1–4 da S28 existem, estão coerentes e linkados ao Programa 1 / Épico E27.1.  
   - Ajustar branch, CI e estrutura de evidências.  
   - Saída: S28_G0 em PASS.

2. **Fase 1 — Domínio & Schema (Backend Core) — S28_G1**  
   - Consolidar modelo `Source`, enums e migration.  
   - Escrever/ajustar testes de invariantes de domínio.  
   - Saída: S28_G1 em PASS, modelo estável para API/ingestão.

3. **Fase 2 — Admin API & Ingestão 2.0 — S28_G2 + S28_G4**  
   - Implementar/ajustar rotas `/admin/sources`.  
   - Atualizar scheduler para respeitar `mode` + `state`.  
   - Criar testes de API e de integração ON/OFF × ingestão.  
   - Saída: S28_G2 e S28_G4 em PASS.

4. **Fase 3 — Console de Fontes v2 & UX — S28_G3 + S28_G6**  
   - Implementar/ajustar páginas e componentes de frontend.  
   - Conectar com `adminSourcesApi`.  
   - Escrever testes de UI/e2e.  
   - Conduzir demo interna (G6) com operadores.  
   - Saída: S28_G3 e S28_G6 em PASS.

5. **Fase 4 — Sanidade de legado, ORR & GO/NO_GO — S28_G5 + S28_G7**  
   - Rodar gates de S21/S22 relevantes.  
   - Consolidar scorecards, riscos e decisão final.  
   - Saída: S28_G5 e S28_G7 em PASS, S28_overall em GO.

Fases podem ter alguma sobreposição (ex.: front começando design enquanto backend estabiliza modelo), mas a **ordem de estabilização de gates** deve respeitar a dependência:

> G0 → G1 → (G2, G4 em paralelo) → G3 → G5 → G6 → G7

---

## 4.2 Organização prática de trabalho (branch, PRs, donos de partes)

### 4.2.1 Branch e fluxo de Git

- Branch principal da sprint:  
  - `feature/s28_sources_crud_onoff`
- Regra:  
  - Todo trabalho de código/backend/frontend da S28 acontece nesta branch.  
  - Merges para `main` acontecem apenas após S28_G7 = GO.

Sugestão de sub-branches por área (se for útil):
- `feature/s28_backend_sources_model_api`  
- `feature/s28_ingestion_onoff`  
- `feature/s28_frontend_sources_console`

Essas sub-branches podem convergir na branch principal da sprint.

### 4.2.2 Donos e responsabilidades (papéis)

Sem amarrar a nomes reais, os papéis são:

- **Backend Owner (Sources & API)**  
  - Modelos `Source`, enums, migrations.  
  - Rotas `/admin/sources` e testes de API.  
  - Responsável direto por S28_G1 e S28_G2.

- **Backend Owner (Ingestão 2.0)**  
  - Scheduler, seleção de fontes elegíveis.  
  - Integração ON/OFF × `IngestionRun`.  
  - Responsável direto por S28_G4.

- **Frontend Owner (Console de Fontes v2)**  
  - Páginas e componentes da feature `sources`.  
  - Testes de UI/e2e.  
  - Responsável direto por S28_G3.

- **QA / ORR Owner**  
  - Execução dos scripts de gates.  
  - Organização de evidências e scorecards.  
  - Coordenação da demo (G6) e consolidação de S28_G7.

- **Tech Lead / Sprint Owner**  
  - Garante alinhamento com Capítulos 1–3.  
  - Decide trade-offs de escopo (o que fica para E27.2/E27.3).  
  - Dá o veredito final (GO/NO_GO) com base nos scorecards.

---

## 4.3 Plano detalhado por gate (o que fazer, em que ordem, como evidenciar)

### 4.3.1 Gate S28_G0 — Scope & Baseline

**Objetivo prático**: sair com docs consolidados e ambiente minimamente preparado.

Passos:
1. Criar/validar arquivos:
   - `docs/sprint_28_cap_1_contexto.md`  
   - `docs/sprint_28_cap_2_gates_metricas_dod.md`  
   - `docs/sprint_28_cap_3_arquitetura_filemap.md`  
   - `docs/sprint_28_cap_4_execucao_evidencias.md` (este capítulo).
2. Garantir que Cap. 1 referencia explicitamente:  
   - Programa 1,  
   - Épico E27.1.
3. Conferir que Cap. 2 lista todos os gates G0…G7 e states-alvo SA-28-01…SA-28-05.  
4. Conferir que Cap. 3 descreve filemap e arquitetura conforme especificado (backend, ingestão, frontend, gates, CI, evidências).  
5. Rodar:
   - `bin/s28_g0_scope_and_baseline.sh`
6. Guardar evidências em:  
   - `out/evidence/S28_G0_scope_and_baseline/`  
   - `out/scorecards/S28_G0_scope_and_baseline.json`

### 4.3.2 Gate S28_G1 — Sources Model & Schema

Passos:
1. Implementar/ajustar `app/sources/models.py`:
   - Definir/confirmar entidade `Source` com todos os campos e enums.  
   - Garantir métodos auxiliares para transições de estado, se aplicável.
2. Implementar/ajustar migration:  
   - `migrations/versions/00xx_s28_sources_model_consolidation.py`
3. Ajustar/implementar testes de domínio:  
   - `tests/domain/test_sources_model_invariants.py`
4. Rodar localmente:
   - `alembic upgrade head` (ou comando equivalente).  
   - `pytest tests/domain/test_sources_model_invariants.py`
5. Rodar gate:
   - `bin/s28_g1_sources_model_and_schema.sh`
6. Evidências:
   - Logs de migration e testes → `out/evidence/S28_G1_sources_model_and_schema/`  
   - Scorecard JSON → `out/scorecards/S28_G1_sources_model_and_schema.json`

### 4.3.3 Gate S28_G2 — Admin API `/admin/sources`

Passos:
1. Implementar/ajustar rotas em `app/api/admin_sources_routes.py`.  
2. Implementar/ajustar schemas em `app/sources/schemas.py`.  
3. Escrever/atualizar testes de API:
   - `tests/api/test_admin_sources_crud_onoff.py`
4. Rodar localmente:
   - `pytest tests/api/test_admin_sources_crud_onoff.py`
5. Rodar gate:
   - `bin/s28_g2_sources_admin_api.sh`
6. Evidências:
   - Logs de testes → `out/evidence/S28_G2_sources_admin_api/`  
   - Scorecard → `out/scorecards/S28_G2_sources_admin_api.json`

### 4.3.4 Gate S28_G3 — Sources Console Front

Passos:
1. Implementar/ajustar estrutura da feature em `frontend/inspectah-ui/src/features/sources/`:
   - Páginas:  
     - `pages/SourcesListPage.tsx`  
     - `pages/SourceFormPage.tsx`  
   - Componentes:  
     - `components/SourceListTable.tsx`  
     - `components/SourceStateBadge.tsx`  
     - `components/SourceActionsMenu.tsx`  
   - API client:  
     - `api/adminSourcesApi.ts`
2. Escrever testes de UI/e2e:
   - `frontend/inspectah-ui/tests/sources/sources_console_onoff.spec.ts`
3. Rodar localmente:
   - `cd frontend/inspectah-ui`  
   - `npm test` (ou target específico)  
   - `npm run build`
4. Rodar gate:
   - `bin/s28_g3_sources_console_front.sh`
5. Evidências:
   - Logs de test/build → `out/evidence/S28_G3_sources_console_front/`  
   - Scorecard → `out/scorecards/S28_G3_sources_console_front.json`

### 4.3.5 Gate S28_G4 — Integração ON/OFF × Ingestão 2.0

Passos:
1. Ajustar scheduler em `app/ingestion/scheduler.py` (ou serviço equivalente):
   - Incluir filtros por `Source.mode` e `Source.state` ao selecionar fontes automáticas.
2. Implementar testes de integração:
   - `tests/integration/test_sources_ingestion_onoff.py`  
   - Usar Admin API para criar fonte e mudar estado; usar função de scheduler de teste para rodar ciclo.
3. Rodar localmente:
   - `pytest tests/integration/test_sources_ingestion_onoff.py`
4. Rodar gate:
   - `bin/s28_g4_sources_ingestion_integration.sh`
5. Evidências:
   - Logs de testes, eventuais dumps de `IngestionRun` → `out/evidence/S28_G4_sources_ingestion_integration/`  
   - Scorecard → `out/scorecards/S28_G4_sources_ingestion_integration.json`

### 4.3.6 Gate S28_G5 — Observability & Legacy Sanity (S21/S22)

Passos:
1. Identificar scripts de S21/S22 relevantes para fontes/ingestão (exemplos):
   - `bin/s21_g1_sources_domain.sh`  
   - `bin/s21_g2_sources_api.sh`  
   - `bin/s22_g1_ingestion_core.sh`  
   - `bin/s22_g2_ingestion_metrics.sh`
2. Rodar esses scripts com o código já contendo mudanças de S28.  
3. Verificar regressões (falhas novas) e corrigi-las dentro da sprint.  
4. Rodar gate:
   - `bin/s28_g5_observability_and_legacy_sanity.sh`
5. Evidências:
   - Logs de execução dos scripts de S21/S22 → `out/evidence/S28_G5_observability_and_legacy_sanity/`  
   - Scorecard → `out/scorecards/S28_G5_observability_and_legacy_sanity.json`

### 4.3.7 Gate S28_G6 — Demo Interna & UX

Passos:
1. Subir ambiente (local ou staging):
   - Backend com migrations aplicadas.  
   - Frontend buildado/rodando.  
   - Ingestão 2.0 com modo de teste disponível.
2. Conduzir demo seguindo roteiro A–D:
   - Criar fonte nova (Caso A).  
   - Desativar fonte problemática (Caso B).  
   - Reativar após manutenção (Caso C).  
   - Editar fonte (Caso D).  
   - Testar lista vazia e erro de API.
3. Registrar participantes, feedback e followups para backlog.  
4. Rodar gate:
   - `bin/s28_g6_demo_internal.sh` (pode gerar scorecard via script ou via pequeno utilitário Python)
5. Evidências:
   - Notas da demo (markdown ou texto) → `out/evidence/S28_G6_demo_internal/demo_notes.md`  
   - Capturas de tela opcionais → `out/evidence/S28_G6_demo_internal/screenshots/`  
   - Scorecard → `out/scorecards/S28_G6_demo_internal.json`

### 4.3.8 Gate S28_G7 — GO/NO_GO Final

Passos:
1. Confirmar presença de todos os scorecards de G0…G6 em `out/scorecards/`.  
2. Rodar script:
   - `bin/s28_g7_go_no_go.sh`
3. Script deve:
   - Ler scorecards.  
   - Validar que todos têm `status = "PASS"`.  
   - Gerar `out/scorecards/S28_overall.json` com `status = "GO"` ou `"NO_GO"`, riscos e donos da decisão.
4. Em caso de NO_GO:
   - Registrar claramente os motivos e o plano para corrigir.  
   - Evitar merge das mudanças de S28 em `main` até resolver.

---

## 4.4 Execução local — comandos e checklists práticos

### 4.4.1 Setup mínimo backend

No diretório raiz do projeto (`Inspectah/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Migrations
alembic upgrade head
```

### 4.4.2 Setup mínimo frontend

```bash
cd frontend/inspectah-ui
npm install
npm run build
npm test   # ou comando equivalente configurado
```

### 4.4.3 Rodar testes específicos da S28

Backend:

```bash
# Domínio
pytest tests/domain/test_sources_model_invariants.py

# API
pytest tests/api/test_admin_sources_crud_onoff.py

# Integração ON/OFF
pytest tests/integration/test_sources_ingestion_onoff.py
```

Frontend:

```bash
cd frontend/inspectah-ui
npm run test:sources   # se existir target; caso contrário, npm test com filtro
```

### 4.4.4 Rodar todos os gates localmente

Na raiz do projeto:

```bash
bin/s28_g0_scope_and_baseline.sh
bin/s28_g1_sources_model_and_schema.sh
bin/s28_g2_sources_admin_api.sh
bin/s28_g3_sources_console_front.sh
bin/s28_g4_sources_ingestion_integration.sh
bin/s28_g5_observability_and_legacy_sanity.sh
bin/s28_g6_demo_internal.sh   # em ambiente com UI disponível
bin/s28_g7_go_no_go.sh
```

Checklist rápido de sanidade antes de abrir PR:
- [ ] Todos os scripts de gates rodaram em PASS localmente.  
- [ ] `out/evidence/S28_G*/**` preenchido com logs relevantes.  
- [ ] `out/scorecards/S28_G*.json` e `S28_overall.json` presentes.  
- [ ] Capítulos 1–4 atualizados e coerentes.

---

## 4.5 CI & ORR — como usar o workflow da S28

### 4.5.1 Execução via GitHub Actions

No GitHub, usar o workflow `.github/workflows/s28-gates.yml` para validação em ambiente CI:

- Disparo manual (workflow_dispatch) quando:
  - um grande conjunto de mudanças da S28 for concluído;  
  - antes de pedir revisão final;  
  - antes de marcar a sprint como encerrada.

- Em PRs:  
  - opcionalmente, configurar para rodar S28_G1–G4 em PRs que toquem backend/front de fontes;  
  - manter G5–G7 mais para execuções completas (branch principal da sprint).

### 4.5.2 Uso do resultado do CI na decisão GO/NO_GO

- Se o workflow falhar:
  - corrigir o gate correspondente, reexecutar localmente e no CI.  
  - NÃO considerar S28 como concluída enquanto houver gates em FAIL.  
- Se o workflow passar com todos os gates em PASS:
  - usar `S28_overall.json` + logs de CI como base objetiva para o ORR da sprint.  
  - registrar no histórico da sprint (docs) o commit/sha correspondente ao build que passou.

---

## 4.6 Checklist final da Sprint 28 (pré-GO)

Antes de cravar GO em S28, o Sprint Owner deve percorrer este checklist:

1. **Gates & scorecards**  
   - [ ] G0–G7 em PASS.  
   - [ ] `out/scorecards/S28_overall.json` com `status = "GO"`.  
   - [ ] Riscos P0/P1 mitigados; apenas P2 remanescentes, devidamente descritos.

2. **Modelo & API**  
   - [ ] `Source` consolidada com campos e enums conforme Cap. 3.  
   - [ ] `/admin/sources` operante com CRUD & ON/OFF e testes em PASS.  
   - [ ] OpenAPI refletindo rotas e schemas atuais.

3. **Ingestão 2.0**  
   - [ ] Scheduler respeita `mode` + `state`.  
   - [ ] Testes de integração ON/OFF em PASS.  
   - [ ] Não há casos conhecidos de fonte `DISABLED` sendo ingerida.

4. **Console de Fontes v2**  
   - [ ] Fluxos A–D funcionam via UI sem gambiarras.  
   - [ ] Testes de UI em PASS.  
   - [ ] Demo interna realizada, feedback capturado.

5. **Legado & observabilidade**  
   - [ ] Scripts relevantes de S21/S22 passaram em ambiente com S28.  
   - [ ] Não foram introduzidas regressões críticas.  
   - [ ] Qualquer alteração inevitável está documentada.

6. **Docs & evidências**  
   - [ ] Capítulos 1–4 revisados, sem divergência em relação ao código.  
   - [ ] Evidências organizadas em `out/evidence/S28_G*/**`.  
   - [ ] Resultado de CI (workflow s28-gates) anexado ou referenciado.

Com este Capítulo 4, a Sprint 28 ganha um plano de execução e um roteiro de evidências **reproduzível, auditável e pronto para ORR**. A partir daqui, o Codex/implementadores podem executar a sprint com clareza de ordem, critérios de sucesso e forma de comprovar que tudo foi de fato entregue.

