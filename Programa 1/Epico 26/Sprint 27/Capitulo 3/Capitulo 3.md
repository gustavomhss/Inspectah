# Inspectah — Sprint 27 (S27)
## Capítulo 3 — Arquitetura & Filemap

> Arquivo-alvo no repo: `docs/s27_cap_3_arquitetura_e_filemap.md`
>
> Função: descrever **como o código, scripts, APIs e docs da S27 se organizam no repositório**, conectando-os diretamente aos estados-alvo do Cap.1 e aos gates do Cap.2. Este capítulo é o mapa para o Codex e para qualquer dev que precise saber *onde* trabalhar e *onde* olhar evidências.

---

## 1. Objetivo do Capítulo 3 na S27

O Capítulo 3 da S27 tem três missões principais:

1. Desenhar a **arquitetura lógica** envolvida na consolidação do Admin v1 para Fontes, Ingestão 2.0 e Debunker (frontend + backend + docs).  
2. Definir um **filemap explícito** que diga onde vivem:
   - componentes de Admin v1,  
   - telas e features dos consoles,  
   - scripts de gates,  
   - testes,  
   - docs e runbooks.  
3. Amarrar essa arquitetura/filemap diretamente a:
   - estados-alvo da S27 (Cap.1 Bloco 3),  
   - gates G0–G6 (Cap.2),  
   - plano de execução (Cap.4) e ORR (Cap.5).

Se Cap.1 responde "*porquê*" e Cap.2 responde "*como vamos verificar*", Cap.3 responde **"onde tudo isso mora no código"**.

---

## 2. Visão arquitetural de alto nível da S27

### 2.1 Blocos principais na S27

A S27 toca, em essência, quatro blocos macro da arquitetura Inspectah:

1. **Frontend Admin v1**  
   - Camada de UI interna para operadores e Truth Ops.  
   - Fornece layout padrão, componentes e experiências coerentes para consoles admin (Fontes, Ingestão, Debunker).

2. **Consoles Admin (Fontes, Ingestão, Debunker)**  
   - Módulos de feature do frontend que constroem telas reais em cima de Admin v1.  
   - Orquestram navegação, filtros, estados e ações.

3. **APIs & Contratos de Backend**  
   - Serviços HTTP/REST usados pelos consoles admin para ler estado, executar ações e registrar decisões.  
   - Incluem modelos, rotas e validações associadas.

4. **Infra de Qualidade & Operação**  
   - Scripts de gates (`bin/s27_g*_*.sh`),  
   - testes de front e API,  
   - scorecards e evidências,  
   - docs, guias e runbooks.

### 2.2 Diagrama conceitual (em palavras)

- **Admin v1** (tokens + layout + componentes) vive em `frontend/inspectah-ui/ui/admin/`.  
- **Consoles** consomem Admin v1 via `features/sources`, `features/ingestion`, `features/debunker`.  
- **APIs** vivem em `app/api/` (ou estrutura equivalente), com modelos em `app/models/` e esquemas em `app/schemas/`.  
- **Gates** vivem em `bin/s27_g*_*.sh`, testam as peças acima e escrevem scorecards em `out/scorecards/` + evidências em `out/evidence/`.  
- **Docs** vivem em `docs/` (Cap.1–Cap.6, guias, runbooks).  
- Um **bundle final** (`out/bundles/inspectah_s27_evidence_bundle.zip`) empacota os resultados.

A S27 não cria uma nova arquitetura; ela **alinha e consolida** as peças existentes ao redor do Admin v1.

---

## 3. Filemap macro — onde vive o quê

> Nota: caminhos podem ser ajustados à realidade do repo, mas a ideia é que o Cap.3 sirva como referência canônica a ser seguida.

### 3.1 Frontend Admin v1

- **Design System Admin v1**  
  - `frontend/inspectah-ui/ui/admin/`
    - `layout/` — componentes de shell admin (`AdminShell`, `AdminHeader`, `AdminSidebar`, `AdminContent`).  
    - `components/` — botões, tabelas, badges, alerts, inputs, cards, etc.  
    - `theme/` — tokens de cor, tipografia, espaçamentos e temas de estado (erro, warning, ok).  
    - `hooks/` (se existirem) — hooks específicos de Admin (ex.: controle de sidebar, estados globais admin).

### 3.2 Consoles Admin — Fontes, Ingestão, Debunker

- **Console de Fontes v2**  
  - `frontend/inspectah-ui/features/sources/`
    - `pages/` — telas principais (listagem de fontes, detalhe, criação/edição).  
    - `components/` — componentes específicos de fontes (ex.: formulário de config).  
    - `hooks/` — lógica de dados (fetch, mutations) usando APIs de fontes.  
    - `types/` — tipos locais, se necessário.

- **Console de Ingestão 2.0**  
  - `frontend/inspectah-ui/features/ingestion/`
    - `pages/` — visão geral da ingestão, detalhe por fonte, fila de jobs.  
    - `components/` — cards de estado de ingestão, listas de runs, gráficos simples (se houver).  
    - `hooks/` — consumo de `/api/ingestion/*`.  
    - `types/` — tipos relacionados a estados de ingestão.

- **Console do Debunker**  
  - `frontend/inspectah-ui/features/debunker/`
    - `pages/` — listagem de disputas, detalhe do caso.  
    - `components/` — visualização de evidências, painéis de decisão, timelines.  
    - `hooks/` — consumo de `/api/debunker/*`.  
    - `types/` — tipos para casos, estados, severidade, etc.

Em todos esses módulos, o uso de Admin v1 deve ser visível nos imports (por exemplo: `import { AdminShell } from "ui/admin/layout/AdminShell"`).

### 3.3 Backend — APIs & Modelos usados pelos consoles

- **APIs**  
  - `app/api/sources_routes.py` (ou arquivo equivalente para rotas de fontes).  
  - `app/api/ingestion_routes.py` (ingestão).  
  - `app/api/debunker_routes.py` (debunker).

- **Modelos & Schemas**  
  - `app/models/sources.py`, `app/schemas/sources.py`  
  - `app/models/ingestion.py`, `app/schemas/ingestion.py`  
  - `app/models/debunker.py`, `app/schemas/debunker.py`

- **Tests de API/contrato**  
  - `tests/api/test_admin_sources_contracts.py`  
  - `tests/api/test_admin_ingestion_contracts.py`  
  - `tests/api/test_admin_debunker_contracts.py`

G4 (Cap.2 Bloco 3) deve apontar para esses caminhos.

### 3.4 Gates & Scripts de verificação

- **Scripts da S27**  
  - `bin/s27_g0_env_repo.sh`  
  - `bin/s27_g1_admin_design_system.sh`  
  - `bin/s27_g2_admin_flows.sh`  
  - `bin/s27_g3_front_quality_admin.sh`  
  - `bin/s27_g4_admin_contracts.sh`  
  - `bin/s27_g5_docs_runbooks.sh`  
  - `bin/s27_g6_orr_bundle.sh`

- **Scorecards**  
  - `out/scorecards/S27_G0_scope_and_env.json`  
  - `out/scorecards/S27_G1_admin_design_system.json`  
  - `out/scorecards/S27_G2_admin_flows.json`  
  - `out/scorecards/S27_G3_front_quality_admin.json`  
  - `out/scorecards/S27_G4_admin_contracts.json`  
  - `out/scorecards/S27_G5_docs_runbooks.json`  
  - `out/scorecards/S27_G6_orr_summary.json`

- **Evidências**  
  - `out/evidence/S27_G0_env_repo/`  
  - `out/evidence/S27_G1_admin_design_system/`  
  - `out/evidence/S27_G2_admin_flows/`  
  - `out/evidence/S27_G3_front_quality_admin/`  
  - `out/evidence/S27_G4_admin_contracts/`  
  - `out/evidence/S27_G5_docs_runbooks/`  
  - `out/evidence/S27_G6_orr/`

### 3.5 Docs & Runbooks

- **Capítulos da S27**  
  - `docs/s27_cap_1_*.md` — contexto, problema, estados-alvo, escopo.  
  - `docs/s27_cap_2_*.md` — gates, métricas, ORR.  
  - `docs/s27_cap_3_arquitetura_e_filemap.md` — este doc.  
  - `docs/s27_cap_4_execucao_e_evidencias.md` — plano de execução.  
  - `docs/s27_cap_5_orr_local_summary.md` — ORR.  
  - `docs/s27_cap_6_learnings_dividas_roadmap.md` — aprendizados, dívidas, ajustes.

- **Guia Admin & Runbooks**  
  - `docs/guia_consoles_admin_v1_1.md`  
  - `docs/runbook_operacao_fontes_vX.md`  
  - `docs/runbook_operacao_ingestao_vX.md`  
  - `docs/runbook_operacao_debunker_vX.md`

---

## 4. Ligações entre arquitetura/filemap e gates da S27

Cada gate do Cap.2 "enxerga" uma parte específica do filemap:

- **G0**  
  - Lê: `docs/s27_cap_1_*.md`, `docs/s27_cap_2_*.md`.  
  - Verifica sanidade do repo e ambiente.

- **G1**  
  - Lê: `frontend/inspectah-ui/ui/admin/*`, `features/sources/*`, `features/ingestion/*`, `features/debunker/*`.  
  - Garante adesão ao Admin v1.

- **G2**  
  - Lê: testes E2E/integração em `tests/e2e/admin_flows/*` (ou equivalente) + front admin.  
  - Exercita fluxos de operadores.

- **G3**  
  - Lê: todo `frontend/inspectah-ui/` via `npm run lint`, `npm test`, `npm run build`.

- **G4**  
  - Lê: `app/api/*_routes.py`, `app/models/*`, `app/schemas/*`, `tests/api/test_admin_*`.  
  - Verifica contratos de API.

- **G5**  
  - Lê: `docs/guia_consoles_admin_v1_1.md`, runbooks.  
  - Garante que docs existem e são minimamente estruturados.

- **G6**  
  - Lê: todos os scorecards em `out/scorecards/`, docs Cap.5, evidências em `out/evidence/`.  
  - Gera o bundle final em `out/bundles/inspectah_s27_evidence_bundle.zip`.

Esta tabela de ligação deve ser usada em Cap.4 para definir tasks e em Cap.5 para planejar o ORR.

---

## 5. Considerações de acoplamento, limites e riscos arquiteturais

Alguns cuidados arquiteturais específicos da S27:

1. **Admin v1 como dependência estável**  
   - `ui/admin` deve ser tratada como "biblioteca interna"; mudanças grandes exigem coordenação.  
   - Evitar que consoles definam estilos/layouts que deveriam morar em Admin v1.

2. **Consoles como camadas finas sobre Admin v1**  
   - `features/sources`, `features/ingestion`, `features/debunker` devem focar em lógica de negócio e composição de tela, não em reinventar layout.

3. **APIs com contratos explícitos**  
   - Modelos e esquemas usados pelos consoles admin devem estar bem definidos;  
   - mudanças de contrato exigem atualização simultânea de testes G4 e, se necessário, de G2.

4. **Scripts & CI**  
   - Os scripts `bin/s27_g*_*.sh` devem ser idempotentes e rodar tanto local quanto em CI (quando a S27 for integrada ao pipeline padrão).  
   - Logs precisam ser claros o suficiente para análise rapidinha durante o ORR.

---

## 6. Como este capítulo guia o Capítulo 4 e o Codex

Cap.3 serve como **plano de coordenadas** para o Cap.4 e para o Codex:

- Cada task de execução (S27-T-XXX) em Cap.4 deve apontar para um ou mais paths deste filemap.  
- Qualquer alteração em arquitetura/filemap feita durante a sprint deve ser refletida neste capítulo (e, idealmente, aprovada pelo squad).  
- O Codex, ao gerar código, testes ou scripts, deve sempre conferir se está escrevendo nos caminhos mapeados aqui e se está respeitando os limites de cada módulo.

Com este Capítulo 3, a S27 deixa de ser só um conjunto de intenções e gates e passa a ter um **mapa físico** dentro do repositório, que pode ser seguido, auditado e evoluído sem adivinhação.

