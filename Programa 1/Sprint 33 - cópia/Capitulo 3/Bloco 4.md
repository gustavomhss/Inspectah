# Sprint 33 — Capítulo 3

## Bloco 4 — Filemap da S33, integração com CI/Gates e trilha de evolução

Este bloco fecha o Capítulo 3 descendo a arquitetura do OracleOps v1 até o nível de filemap, integração com CI/gates e trilha de evolução. A ideia é que ele funcione como um **mapa operacional para pessoas que desenvolvem, revisam e mantêm o código da S33**:

- onde ficam os arquivos e diretórios relevantes;
- como os scripts de gates e o CI amarram a arquitetura na prática;
- quais são as extensões naturais dessa arquitetura nas próximas sprints.

A regra aqui é simples: **nenhuma peça importante da S33 deve ser “descoberta” por arqueologia de repositório**. Ela precisa aparecer neste filemap e estar conectada com os gates definidos no Capítulo 2.

---

### 3.4.1 Filemap lógico da Sprint 33

O filemap da S33 é organizado em cinco grupos principais:

1. **Documentação da sprint e de operação**  
2. **Backend OracleOps v1 (domínio, serviços e API)**  
3. **Frontend OracleOps Cockpit v1**  
4. **Gates, scorecards, evidências e observabilidade**  
5. **Scripts auxiliares e artefatos de evolução**

A seguir, cada grupo é detalhado.

---

### 3.4.2 Documentação da Sprint 33

Pasta atual da sprint:

- `programa 1/Epico 28/Sprint 33/Capitulo */Capitulo *.md` + blocos.

Anexos e artefatos (propostas já criadas como placeholders):

- `programa 1/Epico 28/Sprint 33/s33_scope_ops.md` — escopo operacional (G0).
- `programa 1/Epico 28/Sprint 33/s33_components_map.yaml` — mapa de componentes monitorados (G0/G1/G2).
- `programa 1/Epico 28/Sprint 33/s33_slos.md` — definição de SLOs (G3).
- `programa 1/Epico 28/Sprint 33/s33_incidents_lifecycle.md` — estados/transições de Incident (G1).
- `programa 1/Epico 28/Sprint 33/s33_incidents_learnings.md` — aprendizados/backlog de incidentes (G4/G5).
- Runbooks: `docs/runbooks/` com prefixo `S33_*.md` (cenários prioritários).

---

### 3.4.3 Backend OracleOps v1 — filemap e pontos de extensão (proposta)

Diretórios e arquivos principais no backend (a criar/adaptar):

- **Domínio de componentes monitorados**  
  - `app/ops/components.py`  
    - Carrega e valida `s33_components_map.yaml`.  
    - Expõe funções `list_components`, `get_component`, filtros por tipo/criticidade.

- **Domínio de Incident**  
  - `app/ops/incidents.py`  
    - Modelo `Incident`, enums de estado/severidade, invariantes de lifecycle.  
    - Funções `open_incident`, `transition_incident`, consultas agregadas.  
  - `migrations/versions/00xx_s33_ops_incidents_and_components.py`  
    - Migration da estrutura de Incident/componentes monitorados.

- **Domínio de SLOs**  
  - `app/ops/slos.py`  
    - Representação de SLOs da S33; integração com `s33_slos.md`.

- **Serviços de operação**  
  - `app/ops/health_summary.py`  
    - Consolida estados dos componentes (OK/degradado/falhando) com base em métricas, SLOs e incidentes.
  - `app/ops/slo_evaluator.py`  
    - Executa queries definidas em `ops_slos` na stack de observabilidade, produzindo estados de SLO.

- **API do OracleOps Cockpit**  
  - `app/api/ops_cockpit_routes.py`  
    - Endpoints `/api/ops/cockpit/overview`, `/components`, `/components/{id}`, `/incidents`, `/incidents/{id}`, `/slos`.
  - `app/schemas/ops_cockpit.py`  
    - DTOs para responses e requests do cockpit (`HealthOverviewResponse`, `ComponentSummary`, `IncidentSummary`, `SloStatus` etc.).

**Pontos de extensão futuros:**
- novos tipos de componente podem ser adicionados ampliando enums e mapeamentos em `ops_components`;
- novos campos em Incident podem surgir como migrations adicionais e ajustes em `incidents.py`;
- novos SLOs entram por `s33_slos.md` ou versões futuras (`s34_slos.md`), preservando a interface de `ops_slos`.

---

### 3.4.4 Frontend OracleOps Cockpit v1 — filemap e composição (proposta)

Diretório base da feature:

- `frontend/inspectah-ui/src/features/oracleops/`

Arquivos principais:

- `frontend/inspectah-ui/src/features/oracleops/routes.ts`  
  Definição das rotas internas do cockpit, por exemplo:
  - `/ops/cockpit/overview`
  - `/ops/cockpit/components/:componentId`
  - `/ops/cockpit/incidents`
  - `/ops/cockpit/incidents/:incidentId`

- `frontend/inspectah-ui/src/features/oracleops/api/opsCockpitClient.ts`  
  Cliente HTTP para os endpoints de backend (`fetchOverview`, `fetchComponents`, `fetchComponentDetails`, `fetchIncidents`, `fetchIncidentDetails`, `fetchSlos`, `createIncident`, `updateIncident`).

- Páginas:
  - `pages/OverviewPage.tsx`  
    - Visão geral de saúde, SLOs e incidentes ativos.
  - `pages/ComponentDetailsPage.tsx`  
    - Detalhes de componente, estado, incidentes e runbooks.
  - `pages/IncidentsListPage.tsx`  
    - Lista de incidentes com filtros.
  - `pages/IncidentDetailsPage.tsx`  
    - Detalhe de incidente, timeline, SLOs relacionados, links de evidência.

- Componentes de apoio:
  - `components/SloSummaryPanel.tsx`
  - `components/ComponentHealthTable.tsx`
  - `components/IncidentBadge.tsx`
  - `components/RunbookLinks.tsx`

**Integração com o resto da UI:**
- O módulo `oracleops` é plugado no roteador principal do frontend, provavelmente via uma entrada em `src/routes.tsx` ou equivalente, adicionando uma seção "Operação" ou "Ops" no menu interno.

---

### 3.4.5 Gates, scorecards e evidências — caminhos padrão

A S33 segue o padrão consolidado de gates, scorecards e evidências:

**Scripts de gates (em `bin/`):**

- `bin/s33_g0_scope_and_baseline.sh`  
  - Valida `s33_scope_ops.md` e `s33_components_map.yaml`; gera `S33_G0_scope_and_baseline.json`.

- `bin/s33_g1_incidents_domain.sh`  
  - Roda testes de domínio de Incident; valida invariantes de lifecycle e ligações com componentes/SLOs.

- `bin/s33_g2_cockpit_sanity.sh`  
  - Sanity de endpoints de cockpit (overview, components, incidents, slos); valida alinhamento com `components_map`.

- `bin/s33_g3_slos_sanity.sh`  
  - Executa queries de SLOs e verifica se todas retornam dados consistentes.

- `bin/s33_g4_runbooks_and_evidence.sh`  
  - Verifica presença de runbooks e bundles de evidência; checa estrutura mínima.

- `bin/s33_g5_orr_operacional.sh`  
  - Orquestra (ou no mínimo registra) a execução da ORR operacional: roteiros, tempos, resultados.

**Scorecards (em `out/scorecards/`):**

- `out/scorecards/S33_G0_scope_and_baseline.json`
- `out/scorecards/S33_G1_incidents_domain.json`
- `out/scorecards/S33_G2_cockpit_ui.json`
- `out/scorecards/S33_G3_slos_and_observability.json`
- `out/scorecards/S33_G4_runbooks_and_evidence.json`
- `out/scorecards/S33_G5_orr_operacional.json`

**Evidências (em `out/evidence/`):**

- `out/evidence/S33_G0_scope_and_baseline/`
- `out/evidence/S33_G1_incidents_domain/`
- `out/evidence/S33_G2_cockpit_ui/`
- `out/evidence/S33_G3_slos_and_observability/`
- `out/evidence/S33_G4_incidents/` (bundles de incidente)
- `out/evidence/S33_G5_orr_operacional/` (materiais de ORR: roteiros, logs, prints, notas)

Esses caminhos são importantes tanto para execução local quanto para CI, e devem ser estáveis para futuras sprints que queiram comparar evolução.

---

### 3.4.6 Integração com CI e ORR automatizada

No nível de CI/GitHub Actions, a S33 se integra como mais uma etapa do pipeline de sprints do Inspectah. Um workflow típico pode incluir um job específico para S33, por exemplo:

- `.github/workflows/s33-gates.yml`

Este workflow:
- prepara o ambiente (instala dependências, aplica migrations);
- roda os scripts de gate na ordem G0 → G4;
- agrega os scorecards em uma visão única de ORR (scripts e/or job separado);
- publica artefatos (bundles de evidência, scorecards) como artifacts do CI.

Além disso:
- Os jobs de frontend incluem build e testes que garantem que o cockpit não quebra a UI existente;
- Os jobs de backend incluem testes focados em domínio de Incident e serviços de operação.

A ORR operacional (G5) pode não ser totalmente automatizada, mas o script `bin/s33_g5_orr_operacional.sh` deve ao menos:
- registrar data/hora, branch e commit utilizados na ORR;
- armazenar um resumo em `out/evidence/S33_G5_orr_operacional/`;
- atualizar o scorecard `S33_G5_orr_operacional.json` com o resultado da sessão.

---

### 3.4.7 Trilhas de evolução a partir da S33

Do ponto de vista arquitetural, o filemap e a integração com gates/CI aqui descritos preparam o terreno para evoluções futuras do OracleOps. Alguns caminhos naturais são:

1. **Ampliação do recorte de operação**  
   - Novas fontes e pipelines entram pelo `components_map` de sprints futuras (por exemplo, `s34_components_map.yaml`), reaproveitando a mesma infraestrutura de `ops_components` e `ops_health_summary`.

2. **Motor de SLOs mais genérico**  
   - O modelo de SLOs e o `ops_slo_evaluator` podem ser generalizados para suportar múltiplos recortes e janelas, sem perder compatibilidade com o formato usado na S33.

3. **Incidentes multi‑sprint**  
   - O domínio de Incident pode ser estendido para cobrir casos que atravessam mais de uma sprint, mantendo compatibilidade com migrations e modelos iniciados na S33.

4. **Integração com produtos externos (Programa 4)**  
   - Dados e estados de OracleOps podem ser expostos em APIs ou webhooks específicos, permitindo que consoles externos ou painéis públicos (quando apropriados) consumam estado de operação.

5. **Automação de ORR e simulações**  
   - A infraestrutura de `out/evidence/S33_G*` e de scorecards prepara o caminho para simulações automáticas mais avançadas (por exemplo, incidentes sintéticos recorrentes para testar o sistema).

---

### 3.4.8 Regra de ouro do filemap: código, docs, gates e CI alinhados

A regra de ouro deste bloco é: **código, documentação, scripts de gate e CI precisam contar a mesma história**.

- Se um componente aparece no cockpit, ele deve aparecer em `s33_components_map.yaml` e em `ops_components`.
- Se um SLO é citado em docs ou na UI, ele precisa existir em `s33_slos.md` e ser avaliado por `ops_slo_evaluator`.
- Se um runbook é sugerido no incidente, ele precisa existir em `docs/s33/runbooks/`.
- Se um gate é mencionado no Capítulo 2, deve haver script em `bin/`, scorecard em `out/scorecards/` e evidência em `out/evidence/`.
- O CI deve rodar os mesmos scripts que os devs executam localmente.

Este filemap não é apenas um inventário; é o contrato implícito que garante que a arquitetura descrita nos capítulos 1–3 exista de fato no repositório. Quebrar esse contrato significa introduzir dívida de arquitetura e confusão operacional — exatamente o que a S33 foi desenhada para combater.
