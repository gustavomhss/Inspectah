# Sprint 33 — Capítulo 3

## Arquitetura, filemap e integração do OracleOps v1

Este capítulo descreve, em nível arquitetural, como a Sprint 33 materializa o OracleOps v1 dentro do Inspectah: quais componentes novos são introduzidos, quais componentes existentes são reutilizados, como eles se conectam e onde vivem no repositório. O objetivo é que uma pessoa lendo apenas este capítulo consiga:

- entender o desenho macro da camada de operação (cockpit, incidentes, SLOs, runbooks, evidência);
- localizar os arquivos e diretórios relevantes no código e na documentação;
- enxergar claramente as fronteiras com o restante do sistema (ingestão, agentes, Truth‑DB, System of Blocks, UI existente);
- evoluir a solução nas sprints seguintes sem precisar “redescobrir” a arquitetura da S33.

A Sprint 33 deliberadamente não cria um novo sistema à parte; ela insere uma camada de **OracleOps** sobre a base já estabelecida do Inspectah, respeitando a disciplina de módulos, scripts e pastas que o projeto consolidou ao longo das sprints anteriores.

---

## 3.1 Visão macro da arquitetura OracleOps na S33

Na visão macro, a arquitetura da S33 pode ser dividida em cinco camadas principais:

1. **Fontes, ingestão e pipelines existentes (camada de dados operacionais)**  
   A S33 não redesenha ingestão nem Truth‑DB; ela se apoia em:
   - o **Data Hub** e o **Console de Fontes**, responsáveis por registrar e acionar as fontes de dados (RSS, APIs oficiais, bases estruturadas);
   - os **pipelines de ingestão 2.0** que levam dados de fontes para estágios intermediários e, em alguns casos, até a Truth‑DB / System of Blocks;
   - a infraestrutura de filas, workers e jobs agendados que processam esses fluxos.
   É sobre esse plano de fundo que o OracleOps v1 passa a observar saúde, recência, latência e falhas.

2. **Camada de observabilidade e medições (métricas, logs, SLOs)**  
   A S33 usa a stack de observabilidade já presente no projeto (métricas, logs centralizados, dashboards) como fonte primária de verdade para:
   - calcular recência e latência de pipelines;
   - acompanhar taxas de erro em serviços internos;
   - alimentar a avaliação dos SLOs definidos na sprint.
   Novas consultas, dashboards e regras de alerta são adicionadas como **configurações** desta stack, não como um novo sistema paralelo.

3. **Camada de domínio de operação (Incident + Componentes + SLOs)**  
   Aqui vivem as entidades que dão linguagem à operação da S33:
   - o modelo de **Incident**, com estados, severidades, ligação a componentes e SLOs;
   - a representação de **componentes monitorados** (fontes, pipelines, APIs internas, workers), alinhada com o mapa de G0;
   - a representação de **SLOs**, com vínculos a componentes e métricas.
   Essa camada é implementada no backend do Inspectah, em módulos de domínio dedicados.

4. **Camada de serviços de operação (health summary, avaliação de SLO, orquestração de incidentes)**  
   Sobre o domínio, a S33 introduz serviços que:
   - agregam métricas e logs para produzir um **snapshot de saúde** do recorte da sprint (por exemplo, quantos componentes em "OK", "degradado", "falhando");
   - avaliam SLOs a partir de consultas definidas, produzindo estados como "dentro do alvo" / "violado" / "sem dados";
   - expõem operações de criação, atualização e consulta de incidentes, conectadas ao cockpit.

5. **Camada de experiência de operação (OracleOps Cockpit v1 + runbooks + evidência)**  
   Por fim, a S33 adiciona:
   - rotas e telas no **frontend** (`frontend/inspectah-ui`) para o OracleOps Cockpit v1 (overview, componentes, incidentes, SLOs);
   - integração de **runbooks** (documentos versionados) via links contextuais na UI;
   - links ou referências a **bundles de evidência** produzidos pelos scripts de gate, permitindo que operadores acessem rapidamente o material de ORR.

O fluxo conceitual é:

> fontes e pipelines produzem métricas/logs → observabilidade alimenta SLOs e health summary → domínio de Incident e componentes dá linguagem operacional → serviços expõem essa visão via API → o cockpit apresenta a visão, permite ação e aponta para runbooks e evidência.

---

## 3.2 Componentes e responsabilidades

Dentro dessa visão em camadas, a S33 introduz ou enfatiza alguns componentes principais no backend, frontend e camada de scripts.

### 3.2.1 Backend — domínio e serviços de operação

No backend (aplicação principal do Inspectah), a S33 organiza a camada OracleOps em torno de quatro blocos de código:

- **Domínio de componentes monitorados**  
  Módulo responsável por representar o recorte da S33 como objetos de domínio:
  - leitura do `components_map` definido nos docs da sprint;
  - exposição de uma API interna para obter a lista de componentes, tipos, criticidade e relações com SLOs;
  - garantias básicas de consistência de IDs.

- **Domínio de Incident**  
  Módulo que representa incidentes como entidades persistentes, com:
  - modelo de dados (campos, enums de estado e severidade);
  - regras de transição de estados (lifecycle);
  - validações de ligação com componentes e SLOs;
  - interfaces para criação, atualização e consulta.

- **Serviço de health summary**  
  Componente que:
  - consome métricas e/ou healthchecks de componentes do recorte;
  - aplica thresholds simples para classificar cada componente (OK, degradado, falhando);
  - consolida um snapshot de saúde para exibição no overview do cockpit.

- **Serviço de SLO evaluation**  
  Serviço que:
  - lê a definição dos SLOs da S33 (dos docs ou de um módulo de configuração);
  - executa consultas na stack de observabilidade;
  - produz um estado atual para cada SLO;
  - expõe essa informação para a API do cockpit.

Esses blocos residem em módulos do tipo `app/domain/ops_*.py` e `app/services/ops_*.py`, respeitando a organização de domínio já existente no projeto.

### 3.2.2 Backend — API do OracleOps Cockpit

A S33 adiciona rotas específicas da API para suportar o cockpit, por exemplo em um módulo como `app/api/ops_cockpit_routes.py`, com endpoints do tipo:

- `GET /api/ops/cockpit/overview` — retorna snapshot de saúde do recorte da S33 (componentes por estado, SLOs selecionados, contagem de incidentes ativos/recentes);
- `GET /api/ops/cockpit/components` — lista componentes monitorados, com tipo, criticidade e status agregado;
- `GET /api/ops/cockpit/components/{component_id}` — detalhe de um componente (inclui incidentes associados e links para observabilidade);
- `GET /api/ops/cockpit/incidents` — lista de incidentes filtrável por estado, severidade, componente;
- `POST /api/ops/cockpit/incidents` — criação de incidente;
- `PATCH /api/ops/cockpit/incidents/{incident_id}` — transições de estado e atualização de campos;
- `GET /api/ops/cockpit/slos` — estado atual dos SLOs da S33.

Os schemas dessas rotas são definidos em módulos de schemas/DTOs (por exemplo, `app/schemas/ops_cockpit.py`), de forma a manter contratos estáveis para o frontend.

### 3.2.3 Frontend — OracleOps Cockpit v1

No frontend, o OracleOps v1 é organizado como um "feature" isolado dentro da UI existente do Inspectah, por exemplo:

- `frontend/inspectah-ui/src/features/oracleops/` com:
  - `pages/OverviewPage.tsx` — visão geral de saúde;
  - `pages/ComponentDetailsPage.tsx` — detalhe de componentes;
  - `pages/IncidentsListPage.tsx` e `pages/IncidentDetailsPage.tsx`;
  - `components/SloSummaryPanel.tsx` — painel de SLOs;
  - `components/RunbookLinks.tsx` — seção de links de runbook.

Essa feature consome a API do backend, respeitando os contratos de `ops_cockpit_routes.py`, e se integra à navegação principal via rotas dedicadas (por exemplo, `/ops/cockpit/...`).

### 3.2.4 Scripts de gates e ferramentas auxiliares

Por fim, a S33 adiciona (ou especializa) scripts em `bin/` para cada gate:

- `bin/s33_g0_scope_and_baseline.sh` — validação de escopo e map de componentes;
- `bin/s33_g1_incidents_domain.sh` — testes de domínio de Incident;
- `bin/s33_g2_cockpit_sanity.sh` — sanity de endpoints e payloads do cockpit;
- `bin/s33_g3_slos_sanity.sh` — sanity de SLOs e consultas de observabilidade;
- `bin/s33_g4_runbooks_and_evidence.sh` — verificação de runbooks e bundles;
- `bin/s33_g5_orr_operacional.sh` — orquestração (ou, pelo menos, checklist) da ORR operacional.

Esses scripts geram evidências em `out/evidence/S33_G*/` e scorecards em `out/scorecards/S33_G*.json`, seguindo o padrão do projeto.

---

## 3.3 Filemap detalhado da Sprint 33

Esta seção lista os principais caminhos e arquivos associados à S33 no repositório atual. Onde o artefato ainda não existe, está marcado como **proposta** para implementação pelo Planner/ACE.

### 3.3.1 Documentação da sprint

- `programa 1/Epico 28/Sprint 33/Capitulo 1/Capitulo 1.md` — contexto, problemas, objetivos, escopo.
- `programa 1/Epico 28/Sprint 33/Capitulo 2/Capitulo 2.md` — gates, métricas, invariantes, DoD.
- `programa 1/Epico 28/Sprint 33/Capitulo 3/Capitulo 3.md` — este capítulo (arquitetura e filemap).
- `programa 1/Epico 28/Sprint 33/Capitulo 4/Capitulo 4.md` — execução, evidências, plano operacional.
- `programa 1/Epico 28/Sprint 33/Capitulo 5/Capitulo 5.md` — ORR, runbooks, flags, rollback.
- `programa 1/Epico 28/Sprint 33/Capitulo 6/Capitulo 6.md` — learnings, dívidas, impacto.
- **Proposta**: `programa 1/Epico 28/Sprint 33/s33_components_map.yaml` (mapa de componentes monitorados), `s33_slos.md` (SLOs), `s33_incidents_lifecycle.md` (lifecycle de incidentes) e `s33_incidents_learnings.md` (aprendizados) se optarmos por versionar esses anexos.

### 3.3.2 Backend — domínio, serviços e API (proposta alinhada ao stack atual)

- **Proposta** criar módulo `app/ops/`:
  - `app/ops/components.py` — domínio de componentes monitorados (carrega e expõe `components_map`).
  - `app/ops/incidents.py` — domínio de Incident (modelo, regras de transição, validações).
  - `app/ops/slos.py` — representação de SLOs da S33 (quando modelados em código).
  - `app/ops/health_summary.py` — agregação de métricas para snapshot de saúde.
  - `app/ops/slo_evaluator.py` — avaliação de SLOs via consultas em observabilidade.
  - `app/api/ops_cockpit_routes.py` — rotas HTTP para o OracleOps Cockpit v1.
  - `app/schemas/ops_cockpit.py` — schemas/DTOs das respostas de API do cockpit.
- **Migration proposta**: `migrations/versions/00xx_s33_ops_incidents_and_components.py` para Incident + componentes monitorados.

### 3.3.3 Frontend — OracleOps Cockpit (proposta)

- `frontend/inspectah-ui/src/features/oracleops/pages/OverviewPage.tsx`;
- `frontend/inspectah-ui/src/features/oracleops/pages/ComponentDetailsPage.tsx`;
- `frontend/inspectah-ui/src/features/oracleops/pages/IncidentsListPage.tsx`;
- `frontend/inspectah-ui/src/features/oracleops/pages/IncidentDetailsPage.tsx`;
- `frontend/inspectah-ui/src/features/oracleops/components/SloSummaryPanel.tsx`;
- `frontend/inspectah-ui/src/features/oracleops/components/RunbookLinks.tsx`;
- `frontend/inspectah-ui/src/features/oracleops/routes.ts` — definição das rotas do cockpit;
- `frontend/inspectah-ui/src/features/oracleops/api/opsCockpitClient.ts` — cliente HTTP para a API de cockpit.

### 3.3.4 Gates, scorecards e evidências (nomes propostos)

- `bin/s33_g0_scope_and_baseline.sh`;
- `bin/s33_g1_incidents_domain.sh`;
- `bin/s33_g2_cockpit_sanity.sh`;
- `bin/s33_g3_slos_sanity.sh`;
- `bin/s33_g4_runbooks_and_evidence.sh`;
- `bin/s33_g5_orr_operacional.sh`;
- `out/scorecards/S33_G0_scope_and_baseline.json`;
- `out/scorecards/S33_G1_incidents_domain.json`;
- `out/scorecards/S33_G2_cockpit_ui.json`;
- `out/scorecards/S33_G3_slos_and_observability.json`;
- `out/scorecards/S33_G4_runbooks_and_evidence.json`;
- `out/scorecards/S33_G5_orr_operacional.json`;
- `out/evidence/S33_G0_scope_and_baseline/`;
- `out/evidence/S33_G1_incidents_domain/`;
- `out/evidence/S33_G2_cockpit_ui/`;
- `out/evidence/S33_G3_slos_and_observability/`;
- `out/evidence/S33_G4_incidents/` (bundles de incidente);
- `out/evidence/S33_G5_orr_operacional/` (materiais da ORR operacional).

### 3.3.5 Configuração de observabilidade e alertas (proposta)

- `observability/dashboards/s33_oracleops_overview.json` — dashboard principal do recorte da S33;
- `observability/dashboards/s33_slos_*.json` — dashboards específicos de SLOs (quando versionados em arquivo);
- `observability/alerts/s33_slos_rules.yaml` — regras de alerta para SLOs críticos da sprint.

---

## 3.4 Integração com o restante do Inspectah e evolução futura

A arquitetura desenhada para a S33 é intencionalmente **incremental** e **não intrusiva** em relação ao núcleo do Inspectah:

- o OracleOps v1 funciona como uma **lente** sobre componentes existentes (ingestão, agentes, Truth‑DB, System of Blocks), não como uma camada que os substitui;
- o modelo de Incident e o mapa de componentes são pensados para crescer gradualmente: novos componentes e SLOs podem ser incorporados nas sprints seguintes sem quebrar contratos existentes;
- o cockpit é construído como um "feature" isolado na UI, permitindo evolução independente do restante do frontend;
- scripts de gate, scorecards e evidências seguem o padrão consolidado do projeto, o que facilita comparações entre sprints e reaproveitamento de automações.

Do ponto de vista de roadmap, a S33 estabelece uma base arquitetural que permite, nas próximas sprints:

- ampliar o recorte de fontes e pipelines cobertos pelo OracleOps;
- enriquecer o modelo de Incident com mais campos e integrações (por exemplo, com sistemas externos de alerta ou trilhas de auditoria mais finas);
- evoluir a avaliação de SLOs para um motor mais genérico, se necessário;
- conectar a camada OracleOps a produtos externos do Programa 4 (consoles públicos, status embutido em páginas de caso, modos de transparência).

Este capítulo deve ser tratado como referência canônica para qualquer trabalho estrutural relacionado à S33: mudanças significativas em filemap, contratos de API ou desenho de componentes devem ser refletidas aqui, mantendo o documento alinhado com o código e evitando divergência entre a arquitetura "no papel" e a arquitetura viva do Inspectah.
