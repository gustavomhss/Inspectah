# Sprint 33 — Capítulo 3

## Bloco 2 — Backend OracleOps v1: domínio, serviços e API

Este bloco aprofunda a arquitetura de backend da Sprint 33 para o OracleOps v1. Se o Bloco 1 explicou as camadas conceituais, aqui o foco é: **quais módulos existem, o que cada um faz, como eles se conversam e quais invariantes estruturais precisam ser respeitados** no backend do Inspectah.

O objetivo é que, com este bloco na mão, alguém consiga:
- localizar o código de domínio e serviços da camada OracleOps;
- entender o fluxo de dados entre componentes, Incident, SLOs e cockpit;
- manter e evoluir o backend da S33 sem introduzir acoplamento desnecessário ou violações de responsabilidade.

---

### 3.2.1 Princípios de design do backend OracleOps

O backend da Sprint 33 segue alguns princípios explícitos:

1. **Separação clara entre domínio e infraestrutura.**  
   - O que é conceito de negócio da operação (Incident, componente monitorado, SLO, health summary) vive em módulos de domínio/serviço.
   - O que é transporte (FastAPI, ORM, clientes de observabilidade) vive em camadas de borda (API, adaptadores).

2. **Domínio de operação como “primeiro cidadão”, não utilitário.**  
   Incident, SLO e componente monitorado possuem modelos próprios, invariantes e testes. Não são apenas dicionários JSON transitando pela API.

3. **Uso de contratos estáveis para o cockpit.**  
   As respostas das rotas de cockpit são definidas em schemas/DTOs dedicados. O frontend nunca fala diretamente com modelos internos, o que permite refinar o domínio sem quebrar a UI a cada ajuste.

4. **Reuso consciente com outras partes do sistema.**  
   Sempre que fizer sentido, a camada OracleOps reutiliza informações do Console de Fontes, pipelines e Truth‑DB. Mas esse reuso ocorre via serviços claros, não via consultas ad‑hoc espalhadas.

---

### 3.2.2 Domínio de componentes monitorados

O domínio de componentes monitorados fornece a linguagem básica para dizer “sobre o que estamos operando na S33”. Ele se ancora no `components_map` definido pela sprint (G0) e expõe uma visão consistente para o restante do backend.

**Módulo sugerido:** `app/domain/ops_components.py`

**Responsabilidades principais:**
- Carregar e validar o `components_map` (por exemplo, arquivo YAML/JSON versionado em `programa 1/Epico 28/Sprint 33/s33_components_map.yaml`).
- Representar cada componente como um objeto de domínio com, por exemplo:
  - `component_id` (string estável);
  - `type` (enum: SOURCE, PIPELINE, API, WORKER, OTHER);
  - `criticality` (enum: CRITICAL, IMPORTANT, SUPPORTING);
  - metadados opcionais (por exemplo, links para dashboards default, nome humano, descrição curta);
- Oferecer funções de consulta, como:
  - `list_components()` — lista de todos os componentes do recorte;
  - `get_component(component_id)` — busca um componente específico;
  - `list_components_by_type(type)` — filtragem por tipo;
  - `list_critical_components()` — filtragem por criticidade.

**Invariantes:**
- Todo `component_id` do mapa é único.
- O módulo falha cedo (erro explícito) se encontrar componentes inválidos ou duplicados ao inicializar.
- Não é permitido criar componentes "on the fly" fora do mapa da S33; novos componentes entram pela atualização do mapa oficial e passam pelo gate G0.

---

### 3.2.3 Domínio de Incident

O domínio de Incident encapsula a modelagem de incidentes como entidade persistente e garante que o ciclo de vida e as ligações com componentes/SLOs sejam coerentes.

**Módulo sugerido:** `app/domain/incidents.py`

**Responsabilidades principais:**
- Definir a classe/ORM/modelo `Incident` com campos:
  - `id` (identificador único);
  - `state` (enum, por ex.: OPEN, TRIAGE, MITIGATED, RESOLVED, POSTMORTEM_PENDING, CLOSED);
  - `severity` (enum: LOW, MEDIUM, HIGH, CRITICAL);
  - `title`, `description`;
  - `component_ids` (lista de `component_id` vindos de `ops_components`);
  - `slo_ids` (lista opcional de SLOs relacionados);
  - timestamps (`created_at`, `updated_at`, `resolved_at`, `closed_at`);
  - campos de autoria (`created_by`, `last_updated_by`).
- Implementar funções de domínio como:
  - `open_incident(...)` — criação de incidente em estado inicial;
  - `transition_incident(incident, new_state, actor)` — mudança de estado com validação;
  - `link_incident_to_slo(incident, slo_id)` — vínculo com SLOs;
  - consultas agregadas (por exemplo, `count_active_by_severity()`).

**Invariantes:**
- Transições de estado obedecem ao lifecycle definido (`programa 1/Epico 28/Sprint 33/s33_incidents_lifecycle.md`).
- `component_ids` referem‑se sempre a componentes existentes em `ops_components`.
- `created_at <= updated_at <= resolved_at <= closed_at` (quando campos presentes).

**Integrações:**
- Exposto para serviços e API, mas sem dependência direta de frameworks HTTP.
- Pode expor eventos de domínio (por exemplo, evento "incident_opened") que alimentam logs ou métricas.

---

### 3.2.4 Domínio de SLOs e avaliação

Embora parte da lógica de SLO viva na stack de observabilidade, a S33 recomenda uma representação mínima de SLO no backend para facilitar integração com Incident e cockpit.

**Módulo sugerido:** `app/domain/ops_slos.py`

**Responsabilidades principais:**
- Carregar a definição de SLOs da S33 a partir de `programa 1/Epico 28/Sprint 33/s33_slos.md` ou configuração equivalente.
- Representar cada SLO como objeto de domínio com, por exemplo:
  - `slo_id` (string estável);
  - `description` (string);
  - `metric` (identificador da métrica base);
  - `query` (expressão usada na observabilidade);
  - `target` (objeto que represente o target, ex.: tipo + valor);
  - `window` (janela de observação);
  - `component_ids` associados.
- Expor funções como:
  - `list_slos()`;
  - `get_slo(slo_id)`;
  - `list_slos_by_component(component_id)`.

**Módulo sugerido de serviço:** `app/services/ops_slo_evaluator.py`

**Responsabilidades do serviço de avaliação:**
- Executar consultas na stack de observabilidade com base em `query` e `window` de cada SLO.
- Produzir um estado atual para cada SLO (por exemplo: `OK`, `VIOLATED`, `NO_DATA`, `UNKNOWN`).
- Calcular metadados como:
  - percentual de tempo cumprindo o SLO na janela;
  - valor atual da métrica relacionada.

**Invariantes:**
- Nenhum SLO existente na lista da S33 fica sem `query` ou `metric` associada.
- Falhas ao avaliar um SLO (erro de query, ausência de dados) retornam estado consistente (por exemplo, `NO_DATA`) e são logadas.

---

### 3.2.5 Serviço de health summary

O serviço de health summary é o responsável por transformar um conjunto de sinais brutos (métricas, logs, estados de incidentes) em um snapshot de saúde amigável para o cockpit.

**Módulo sugerido:** `app/services/ops_health_summary.py`

**Responsabilidades principais:**
- Consultar `ops_components` para obter a lista de componentes do recorte da S33.
- Para cada componente, aplicar uma função de classificação de estado com base em:
  - métricas disponíveis (erros, latência, recência);
  - SLOs associados (por exemplo, se um SLO crítico está violado, o componente não pode ser considerado "OK");
  - incidentes ativos relacionados.
- Produzir um objeto agregado de snapshot, por exemplo:
  - contagem de componentes por estado (OK/degradado/falhando);
  - lista de componentes em estado diferente de "OK";
  - resumo de incidentes ativos.

**Invariantes:**
- O health summary nunca "inventa" componentes; ele opera exclusivamente sobre o catálogo definido em `ops_components`.
- Em caso de ausência de dados (métricas indisponíveis, falha na consulta), o serviço deve preferir um estado conservador (por exemplo, marcar como "desconhecido" ou "degradado", e não "OK") e registrar logs.

---

### 3.2.6 API do OracleOps Cockpit

A API do OracleOps é o ponto de contato oficial entre backend e cockpit. Ela deve ser magra, previsível e alinhada com os domínios descritos acima.

**Módulo sugerido:** `app/api/ops_cockpit_routes.py`

**Endpoints principais (exemplos):**

- `GET /api/ops/cockpit/overview`
  - Usa `ops_health_summary` e `ops_slo_evaluator` para retornar:
    - contagem de componentes por estado;
    - lista resumida de componentes problemáticos;
    - estado dos principais SLOs da S33;
    - contagem de incidentes ativos por severidade.

- `GET /api/ops/cockpit/components`
  - Usa `ops_components` e, opcionalmente, `ops_health_summary` para listar componentes com tipo, criticidade e estado agregado.

- `GET /api/ops/cockpit/components/{component_id}`
  - Usa `ops_components`, `ops_health_summary` e `incidents` para detalhar um componente, incluindo:
    - metadados (nome, tipo, criticidade, links para dashboards);
    - estado atual (OK/degradado/falhando);
    - incidentes ativos/recentes relacionados;
    - SLOs associados e seu estado.

- `GET /api/ops/cockpit/incidents`
  - Usa domínio de `Incident` para listar incidentes, com filtros por estado, severidade, componente.

- `POST /api/ops/cockpit/incidents`
  - Cria um novo incidente usando funções de domínio (`open_incident`), validando componentes e severidade.

- `PATCH /api/ops/cockpit/incidents/{incident_id}`
  - Faz transições de estado e atualizações parciais, respeitando invariantes do lifecycle.

- `GET /api/ops/cockpit/slos`
  - Usa `ops_slo_evaluator` para retornar o estado atual dos SLOs da S33, possivelmente filtrável por componente.

**Schemas/DTOs sugeridos:** `app/schemas/ops_cockpit.py`

- Definem estruturas como `HealthOverviewResponse`, `ComponentSummary`, `IncidentSummary`, `IncidentDetails`, `SloStatus`.
- Garantem que a API não vaze diretamente a estrutura interna do ORM ou de domínio.

**Invariantes de API:**
- As rotas nunca retornam IDs de componentes ou SLOs que não constem em `ops_components`/`ops_slos`.
- Erros de domínio (por exemplo, tentativa de transição inválida de incidente) são traduzidos em códigos HTTP adequados (4xx) com mensagens claras.
- Campos opcionais (por exemplo, `slo_ids` de incidente) seguem contratos estáveis, não mudando de tipo ao longo da sprint.

---

### 3.2.7 Relação do backend OracleOps com gates e ORR

O desenho de backend não existe isolado: ele é usado diretamente pelos gates e pela ORR operacional da S33.

- Os scripts de gate G0–G3 podem se apoiar em funções de domínio/serviço para evitar duplicação de lógica (por exemplo, scripts de sanity chamando internamente `ops_components` ou `ops_slo_evaluator`).
- O cockpit consome exatamente as rotas descritas neste bloco; qualquer mudança significativa nesses contratos deve ser refletida nos docs da S33 e, idealmente, passar por novo gate.
- Durante a ORR (G5), o facilitador e o operador estão, na prática, exercitando o desenho descrito aqui: se alguma etapa exigir acesso direto ao banco ou consultas paralelas fora da API, é um sinal de que a arquitetura está com vazios que precisam ser preenchidos.

Este bloco deve ser usado como referência de implementação e revisão para todo código backend associado ao OracleOps v1 na Sprint 33. Divergências entre o que está descrito aqui e o que existe no código ou nos scorecards de gate devem ser tratadas como bugs de especificação ou de implementação — e corrigidas antes da sprint ser declarada "GO" em ORR.
