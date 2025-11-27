# 5.3 – Arquitetura & Filemap da Camada de Produto, Casos & Coleções – v2 extremo

Este 5.3 é o **mapa físico** da camada de produto do Cap. 5:

- onde vivem os **Casos Inspectah**, coleções temáticas e cockpit mínimo;
- como eles se conectam tecnicamente à Truth‑DB, Claims, Comitês e Evidências;
- quais módulos, arquivos e pastas formam a **“Case Layer”** (backend + UI + configs + scripts);
- como essa camada entra em CI, evidências e bundle da sprint.

Se o Cap. 5 é o rosto de Verdade & Interpretação, o 5.3 é o **esqueleto técnico** desse rosto: tudo que é produto precisa ter endereço, módulo responsável e caminho de auditoria.

Este subcapítulo é construído em cima de:
- personas e problemas P1–P5 do 5.1;  
- gates GP0–GP4 e métricas de produto do 5.2;  
- anatomia técnica e filemap base do Cap. 3 e Cap. 4.

---

## 5.3.1 – Visão em camadas: de Truth‑DB ao cockpit de casos

Para esta sprint, o Squad Verdade & Interpretação organiza a camada de produto em **seis blocos**, cada um com responsabilidades claras e lugar definido no repositório:

1. **Motor de Verdade (já mapeado em Cap. 3/4)**  
   Camadas S21–S25 que produzem Claims, Decisions e Truth:
   - `app/ingestion/` – fontes e ingestão 2.0;
   - `app/brain/` – interpretação e geração de `Claim`;
   - `app/committees/` – avaliações e decisões de comitê;
   - `app/debunker/` – issues e tarefas de contestação;
   - `app/truthdb/` – Truth‑DB, `TruthRecord` e `TruthChangeEvent`.

2. **Case Layer – Backend de Produto**  
   Módulo que junta motor de verdade + configs de casos para expor **Casos Inspectah e coleções** via APIs:
   - `app/cases/` (novo módulo descrito em 5.3.2).

3. **Cockpit de Casos – Frontend mínimo**  
   Rotas e componentes na UI para listar coleções, listar casos, ver detalhe de caso:
   - `frontend/inspectah-ui/src/routes/cases/` e componentes associados (5.3.3).

4. **Configs & Documentação de Casos/Coleções**  
   Arquivos versionados que definem modelo de caso, casos canônicos e coleções temáticas:
   - `docs/cases/` (5.3.4).

5. **Scripts de Curadoria & Métricas de Produto**  
   Utilitários que validam casos/coleções e calculam métricas GP1–GP4:
   - `bin/sXX_cases_*.sh` e helpers Python (5.3.5).

6. **Evidências de Produto**  
   Artefatos gerados (payloads, prints, relatórios) que provam o funcionamento da camada de produto:
   - `out/evidence/SXX_product_*/` (5.3.6).

O resto deste 5.3 desce camada a camada, definindo estrutura mínima, invariantes e pontos de integração.

---

## 5.3.2 – Case Layer (Backend de Produto) em `app/cases/`

A **Case Layer** é o backend da experiência de produto do Cap. 5. Ela **não reimplementa** lógica de Truth‑DB, Claims ou Comitês; ela **orquestra** essas camadas para materializar P1–P3:

- P1 – unidade de produto **Caso Inspectah** real;
- P2 – visão única de caso para Persona A;
- P3 – coleções temáticas para Persona B.

### 5.3.2.1 – Estrutura mínima do módulo `app/cases/`

Sugestão de filemap:

- `app/cases/__init__.py`  
  Inicialização do módulo (pode registrar rotas, dependências, etc.).

- `app/cases/domain.py`  
  Modelos de domínio (não necessariamente modelos de banco), por exemplo:
  - `CaseDefinition` – espelho do arquivo `docs/cases/case_*.yaml` (campos: `case_id`, título, resumo, claims, evidências, etc.);
  - `ResolvedCase` – Caso Inspectah depois de resolvido contra a Truth‑DB (com claims carregadas, truth atual, timeline montada, evidências resolvidas);
  - `CaseCollectionDefinition` – definição de coleção (`collection_id`, título, descrição, lista de `case_id`);
  - `ResolvedCollection` – coleção resolvida com detalhes dos casos.

- `app/cases/repository.py`  
  Responsável por:
  - ler arquivos de `docs/cases/` (cases/collections) e convertê‑los em `CaseDefinition` / `CaseCollectionDefinition`;
  - expor métodos como `list_case_definitions()`, `get_case_definition(case_id)`, `list_collections()`, `get_collection(collection_id)`;
  - validar estrutura mínima dos arquivos (campos presentes, tipos básicos) antes de passar para a camada de serviço.

- `app/cases/resolver.py`  
  Responsável por **ligar config ↔ Truth‑DB/Claims**:
  - dado um `CaseDefinition`, carregar Claims, TruthRecords, TruthChangeEvents, decisões de comitê e evidências relacionadas;
  - montar um `ResolvedCase` com:
    - claims centrais enriquecidas (texto, tipo, valores);
    - estado atual de truth (agregado a partir de Truth‑DB);
    - timeline sintetizada (subconjunto de eventos relevantes);
    - “slots” de evidências resolvidos (URLs, IDs, descrições);
  - expor funções como `resolve_case(case_id)` e `resolve_collection(collection_id)`.

- `app/cases/schemas.py`  
  Schemas (por exemplo, Pydantic) usados nos endpoints:
  - `CaseSummarySchema`, `CaseDetailSchema`, `CollectionSummarySchema`, `CollectionDetailSchema`;
  - importante: **não vazar estruturas internas** da Truth‑DB além do necessário; a API de produto deve ser mais amigável.

- `app/cases/routes.py` (ou `api.py`)  
  Endpoints oficiais da camada de casos/coleções:
  - `GET /api/cases` – lista de casos (resumo);
  - `GET /api/cases/{case_id}` – detalhe completo de caso (GP2);
  - `GET /api/collections` – lista coleções temáticas (GP3);
  - `GET /api/collections/{collection_id}` – detalhe de coleção + casos.

- `app/cases/errors.py` (opcional, mas recomendado)  
  Tipos de erro de produto (ex.: `CaseNotFound`, `CollectionNotFound`, `CaseDefinitionInvalid`) para padronizar respostas.

### 5.3.2.2 – Dependências explícitas com outros módulos

A Case Layer conversa com:

- `app/truthdb/`
  - funções de acesso a `TruthRecord` e `TruthChangeEvent` (por claim, por entidade, etc.);
  - invariantes já definidas no Cap. 3/4 (por exemplo, não podem existir dois FACT ativos simultâneos para a mesma claim).

- `app/brain/`
  - acesso a `Claim` e entidades relacionadas (`InterpretationUnit`, etc.).

- `app/committees/` e `app/debunker/`
  - leitura de `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue`, `DebunkTask` relevantes para o caso.

- módulo de evidências (se já existir, ex.: `app/evidence/`)
  - para resolver refs de evidência de `CaseDefinition` em URLs, paths, IDs.

A dependência é **de cima para baixo**: `app/cases/` consome esses módulos, mas eles não conhecem `app/cases/`. Isso evita acoplamento circular.

### 5.3.2.3 – Invariantes da Case Layer

- Não existe `CaseDefinition` sem tentativa de resolução em Truth‑DB – qualquer caso definido deve ser resolvível pela `Case Layer` (ou acusado como inválido).
- Nenhum endpoint de casos lê a Truth‑DB diretamente “no braço”: todo acesso passa por `resolver.py` ou helpers equivalentes.
- Os tipos expostos em `schemas.py` são **estáveis** dentro da sprint (mudanças quebram UI/consumidores, então devem ser controladas).

---

## 5.3.3 – Cockpit de Casos (Frontend mínimo) em `frontend/inspectah-ui/`

A UI desta sprint não é o produto final do Inspectah, mas precisa provar que:

- Casos Inspectah existem como entidade de primeira classe;
- há uma visão unificada de caso (GP2);
- coleções temáticas podem ser navegadas (GP3).

### 5.3.3.1 – Rotas e páginas principais

Filemap proposto:

- Diretório base de rotas:
  - `frontend/inspectah-ui/src/routes/cases/`

- Páginas:
  - `CasesListPage.tsx`
    - rota: `/cases`
    - consome `GET /api/cases`;
    - exibe tabelas/cards com: título, tema, status de truth agregado, link para detalhe;
    - permite filtros simples (por tema, estado de truth, entidade chave).

  - `CaseDetailPage.tsx`
    - rota: `/cases/:caseId`
    - consome `GET /api/cases/{case_id}`;
    - exibe:
      - título e resumo do caso;
      - painel compacto de status de truth (FACT/CONTESTED/etc. + microexplicação);
      - lista de claims centrais (texto, tipo, valores);
      - timeline simplificada (component `CaseTimeline`);
      - lista de evidências principais com links (`EvidenceLink`);
    - esse é o ponto focal para Persona A.

  - `CollectionsListPage.tsx`
    - rota: `/collections`
    - consome `GET /api/collections`;
    - exibe lista de coleções (título, descrição, nº de casos).

  - `CollectionDetailPage.tsx`
    - rota: `/collections/:collectionId`
    - consome `GET /api/collections/{collection_id}`;
    - exibe descrição da coleção + cards (`CaseCard`) para cada caso.

### 5.3.3.2 – Componentes compartilhados

Diretório sugerido:
- `frontend/inspectah-ui/src/components/cases/`

Componentes mínimos:

- `CaseCard.tsx`
  - exibe título, resumo curto, tema, status de truth (badge) e link para `/cases/:caseId`.

- `CaseTimeline.tsx`
  - recebe estrutura de timeline (do schema de backend) e renderiza eventos em ordem cronológica:
    - data/hora;
    - de/para estado de truth;
    - resumo da mudança (ex.: “Decisão de comitê: claim marcada como FACT”).

- `EvidenceLink.tsx`
  - wrapper para links de evidência, com ícone indicando tipo (dataset, documento, notícia original).

- `CollectionCard.tsx` (opcional)
  - usado em `CollectionsListPage` para exibir coleções.

### 5.3.3.3 – Navegação e integrações

- O menu principal do cockpit ganha uma seção “Casos” com links para `/cases` e `/collections`.
- A UI **não** fala diretamente com modules internos de Truth‑DB; sempre consome as APIs de `app/cases/`.
- Para facilitar demos (Cap. 5.4), a UI pode receber `caseId` e `collectionId` via query params para ir direto a casos/coleções canônicos.

Invariantes de UI desta sprint:

- Qualquer Caso Inspectah canônico do GP1 deve ser acessível via `/cases/:caseId`.
- Qualquer coleção definida em `docs/cases/collections.yaml` deve aparecer em `/collections`.

---

## 5.3.4 – Config & Documentação de Casos/Coleções em `docs/cases/`

Para honrar GP1–GP3 e os invariantes do 5.1, Casos Inspectah e coleções precisam ser **dados versionados**, não “lendas orais”. O diretório canônico para isso é:

- `docs/cases/`

### 5.3.4.1 – Arquivos principais

- `docs/cases/case_model.md`
  - explica o modelo de Caso Inspectah para esta fase:
    - campos obrigatórios;  
    - relação com Claims, TruthRecords, evidências;  
    - exemplos concretos (ex.: um caso econômico, um caso dados oficiais vs discurso).

- `docs/cases/case_<slug>.yaml` (um arquivo por caso canônico)
  - campos típicos:
    - `case_id`: string única, estável;  
    - `title`: título legível;  
    - `summary`: resumo curto, foco na narrativa;  
    - `theme`: tag de tema principal;  
    - `claims`: lista de objetos com refs para Claims (ID, tipo, descrição resumida);  
    - `evidences`: lista de refs de evidência (tipo, origem, ID/URL interna);  
    - `committee_decisions`: IDs/refs para decisões relevantes;  
    - `debunk_issues`: IDs/refs para issues/tarefas principais;  
    - `truth_focus`: lista de IDs de TruthRecords/Events relevantes ou critérios para selecioná‑los.

- `docs/cases/collections.yaml`
  - define coleções temáticas:
    - `collection_id`;  
    - `title`;  
    - `description`;  
    - `theme_tag` (opcional, para agrupar coleções);  
    - `cases`: lista de `case_id`.

- `docs/cases/README.md`
  - guia rápido para curadores:
    - como criar/editar um caso;  
    - como criar/editar coleções;  
    - como rodar scripts de checagem/metrics;  
    - como garantir que as mudanças aparecem na UI.

### 5.3.4.2 – Invariantes de config

- Nenhum `case_<slug>.yaml` pode ser mergeado sem passar pelos checks de integridade (`bin/sXX_cases_check.sh`).
- Todos os `case_id` definidos em `case_*.yaml` precisam ser únicos.
- Todo `case_id` referenciado em `collections.yaml` deve existir em algum `case_*.yaml`.
- Qualquer alteração em `docs/cases/` deve ser tratada como mudança relevante de produto: revisada e, idealmente, ligada a casos de uso reais.

---

## 5.3.5 – Scripts de Curadoria & Métricas em `bin/`

Para suportar GP1–GP4, a sprint precisa de scripts que:

- validem a integridade de casos/coleções;
- ajudem na curadoria interna;
- calculem métricas de produto.

### 5.3.5.1 – Scripts mínimos sugeridos

- `bin/sXX_cases_check.sh`
  - invoca um módulo Python (ex.: `python -m app.cases.cli check`);
  - tarefas:
    - abrir todos os `docs/cases/case_*.yaml` e `collections.yaml`;
    - validar schema (campos obrigatórios, tipos);
    - verificar se todos os IDs referenciados (Claims, TruthRecords, etc.) existem na base;
    - checar consistência de coleções (sem `case_id` inexistente);
    - escrever relatório em `out/evidence/SXX_cases_check/report.json`.

- `bin/sXX_cases_metrics.sh`
  - calcula métricas de produto definidas em 5.2 (GP4), por exemplo:
    - `N_casos_canonicos`;  
    - `N_temas_com_colecao`;  
    - `coverage_casos_em_colecoes`;  
    - distribuição de estados de truth em casos canônicos.
  - grava saída em `out/evidence/SXX_product_metrics/metrics.json`.

- `bin/sXX_cases_demo.sh`
  - script de apoio às demos do 5.4:
    - prepara ambiente (semente de dados necessária);
    - chama endpoints de casos/coleções para os casos canônicos;
    - imprime no terminal ou salva em arquivos as URLs e respostas usadas nas demos.

- `bin/sXX_cases_seed.sh` (opcional)
  - prepara dados mínimos (Claims, TruthRecords, etc.) para suportar os casos canônicos em ambientes de dev/demo.

### 5.3.5.2 – Integração com módulos Python

É recomendável ter um CLI leve em Python para orquestrar lógica de checagem/métricas:

- `app/cases/cli.py`
  - comandos:
    - `check` – rotina principal usada por `sXX_cases_check.sh`;
    - `metrics` – rotina principal usada por `sXX_cases_metrics.sh`.

Esse CLI aproveita **exatamente a mesma lógica** de `repository.py` e `resolver.py`, evitando duplicação.

---

## 5.3.6 – Evidências de Produto em `out/evidence/`

Para que GP1–GP4 sejam auditáveis, a sprint precisa gerar evidências consistentes para a camada de produto. O 5.3 define onde essas evidências vivem:

- `out/evidence/SXX_product_cases/`
  - exemplos de payload de `GET /api/cases/:id` (JSON);
  - dumps de representações de `ResolvedCase` (para auditoria);
  - capturas de tela da `CaseDetailPage` (se forem versionadas como arquivos).

- `out/evidence/SXX_product_collections/`
  - payloads de `GET /api/collections` e `GET /api/collections/:id`;
  - prints/capturas de `CollectionsListPage` e `CollectionDetailPage`.

- `out/evidence/SXX_product_metrics/`
  - `metrics.json` com métricas de produto calculadas pelo script;
  - opcionalmente CSVs/graficos gerados em notebooks.

- `out/evidence/SXX_cases_check/`
  - `report.json` gerado por `sXX_cases_check.sh`, indicando inconsistências (se houver).

- `out/evidence/SXX_cases_demo/`
  - logs de execução de `sXX_cases_demo.sh`;
  - scripts/roteiros de demonstração ligados a 5.4.

Esses diretórios passam a ser incluídos (ou referenciados) no bundle de evidências da sprint, conforme Cap. 4.4.

---

## 5.3.7 – Integração com CI e Gates (GP0–GP4 + G0–G8)

O 5.3 também define **como** a camada de produto entra em CI, para que GP1–GP4 não sejam “verificados a olho”.

### 5.3.7.1 – PRs e branch da sprint

No workflow principal da sprint (ex.: `.github/workflows/sXX_gates.yml`):

- Em PR:
  - rodar `bin/sXX_cases_check.sh` quando houver mudanças em `docs/cases/` ou `app/cases/` ou `frontend/inspectah-ui/src/**`;
  - falhar o PR se o check acusar inconsistências (IDs quebrados, coleções com casos inexistentes).

- Em push na branch da sprint:
  - além dos gates técnicos (G0–G6), rodar `bin/sXX_cases_metrics.sh`;  
  - publicar `metrics.json` e `report.json` como artefatos do workflow.

### 5.3.7.2 – Pipelines de release / G7 / G8

- No pipeline de release (staging):
  - garantir que a UI de casos/coleções compila e responde ao mínimo de testes (smoke tests);
  - rodar `sXX_cases_check.sh` + `sXX_cases_metrics.sh` contra a base de staging;
  - incluir os artefatos em `out/` no bundle da sprint.

- Em G7 (ORR):
  - o relatório passa a incluir uma seção “Camada de Produto (Cap. 5)” com:
    - resumo do estado de GP1–GP4;  
    - métricas de produto relevantes;  
    - links para casos/coleções canônicos.

- Em G8 (GO/NO‑GO):
  - a decisão final considera explicitamente se os Casos Inspectah canônicos existem, são navegáveis, têm coleções e métricas;  
  - se a camada de produto falhar completamente, a sprint pode ser tecnicamente forte, mas **não entrega o Mínimo Produto de Verdade** esperado.

---

## 5.3.8 – Invariantes de Arquitetura & Filemap de Produto

Para evitar deriva e bagunça, o 5.3 estabelece invariantes que o squad deve preservar:

1. **Centralização em `app/cases/`**  
   - Qualquer endpoint ou lógica relacionada a casos/coleções deve passar por este módulo.
   - Não é permitido “montar caso” diretamente em rotas improvisadas ou scripts isolados.

2. **Casos & Coleções sempre versionados em `docs/cases/`**  
   - Não existe Caso Inspectah canônico sem arquivo em `docs/cases/`.
   - Não existe coleção temática sem entrada em `collections.yaml`.

3. **UI de casos/coleções só consome APIs de `app/cases/`**  
   - Componentes React nunca acessam diretamente a Truth‑DB ou outras tabelas internas.

4. **Scripts de produto vivem em `bin/` e escrevem em `out/`**  
   - Checagens, métricas e demos de produto sempre usam scripts/CLIs formais, nunca comandos ad‑hoc escondidos em README.

5. **Bundle de sprint inclui artefatos de produto**  
   - Nenhuma demo “mágica”: tudo que foi mostrado em demonstrações oficiais deve ser reconstituível a partir de `docs/cases/`, `app/cases/`, UI e evidências em `out/`.

Com esse 5.3 v2 extremo, o Cap. 5 ganha um esqueleto técnico claro: sabe‑se exatamente **onde** vivem casos, coleções e cockpit, **como** eles se ligam à Truth‑DB e **como** essa camada entra no pipeline de execução, CI e evidências da sprint. O 5.4, a partir daqui, consegue escrever um runbook de execução & evidências de produto em cima de uma arquitetura sólida e auditável.

