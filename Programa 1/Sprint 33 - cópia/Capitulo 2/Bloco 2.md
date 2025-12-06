# Sprint 33 — Capítulo 2

## Bloco 2 — Gates G0 e G1: Escopo, grounding e domínio de operação

Este bloco detalha os dois primeiros gates da Sprint 33 — **G0 (Escopo e baseline de operação definidos)** e **G1 (Modelo de Incident e domínio de operação coerente)** — no nível em que eles podem ser implementados como scripts, scorecards e rituais de revisão, sem espaço para ambiguidade. A ideia é que qualquer pessoa que leia este bloco consiga, a partir dele, escrever os binários de gate, os testes, os scorecards JSON e o checklist de ORR correspondentes.

G0 e G1 cumprem um papel de "fundação" da sprint: eles não olham ainda para telas do cockpit, gráficos de SLO ou runbooks; eles garantem que:

1. Sabemos **exatamente sobre que pedaço do mundo** a S33 falará (recorte de fontes, pipelines, APIs e SLOs);
2. Temos uma **gramática operacional mínima** na forma de um modelo de Incident coerente, com ciclo de vida, severidades e vínculo com componentes monitorados.

Sem esses dois gates sólidos, qualquer esforço em cockpit, SLO e runbooks fica construído sobre areia.

---

### 2.2.1 G0 — Escopo e baseline de operação definidos (detalhado)

**Pergunta que G0 responde:**
> "Todos concordam, de forma explícita e verificável, sobre _qual pedaço da operação_ a S33 quer tornar operável?"

#### Artefatos formais de G0

G0 se ancora em três artefatos principais:

1. **Documento de escopo operacional da S33** (por exemplo, `programa 1/Epico 28/Sprint 33/s33_scope_ops.md`), contendo:
   - Lista de **fontes críticas** cobertas (com identificadores estáveis, ex.: `source_id` ou slug);
   - Lista de **pipelines representativos** (por exemplo, `pipeline_ingest_ibge_truthdb`, `pipeline_ingest_rss_governo_agents`), com definição clara de início e fim (o que conta como "processado");
   - Lista de **APIs internas essenciais** ao recorte (por exemplo, `/api/ops/cockpit`, `/api/data/query_critica`);
   - Lista de **SLOs da S33** (ver `programa 1/Epico 28/Sprint 33/s33_slos.md`), cada um com:
     - nome curto (`s33_slo_ingest_recency_ibge`);
     - métrica base (por exemplo, `recency_seconds{source="ibge"}`);
     - limiar (ex.: `<= 3600s`);
     - janela de observação (ex.: 1h sliding window);
     - tipo de SLO (recência, latência, disponibilidade etc.).

2. **Mapa de componentes monitorados** (por exemplo, `programa 1/Epico 28/Sprint 33/s33_components_map.yaml`), com uma coleção de entradas que amarram:
   - `component_id` estável (usado em código, métricas, logs e UI);
   - tipo (`source`, `pipeline`, `api`, `worker` etc.);
   - relação com fontes/pipelines/APIs e SLOs;
   - tags de criticidade (ex.: `critical`, `important`, `nice_to_have`).

3. **Scorecard de G0** (por exemplo, `out/scorecards/S33_G0_scope_and_baseline.json`), contendo o resultado da execução do gate (PASS/NO_GO) e uma visão sintética das checagens realizadas.

#### Invariantes de G0

Para que G0 seja considerado "PASS", as seguintes invariantes precisam ser verdadeiras:

- **Inv‑G0‑1 — Correspondência 1:1 entre recorte e mapa de componentes.**  
  Toda fonte, pipeline ou API mencionada no doc de escopo está presente no mapa de componentes. Não existem fontes "fantasmas" (mencionadas em objetivos, mas ausentes no mapa) nem componentes no mapa que não estejam em nenhum lugar do escopo da S33.

- **Inv‑G0‑2 — Identificadores estáveis e consistentes.**  
  Para cada componente do recorte, o `component_id` usado no mapa coincide com os identificadores usados na:
  - configuração do Console de Fontes;
  - configuração de jobs/pipelines (ex.: nomes de filas, jobs);
  - labels/chaves de métricas na stack de observabilidade;
  - modelos/constantes usados pelo cockpit.

- **Inv‑G0‑3 — SLOs com métrica base mapeada.**  
  Para cada SLO listado na S33, existe ao menos uma linha de mapeamento do tipo:
  ```
  slo_id: s33_slo_ingest_recency_ibge
  metric: recency_seconds{source="ibge"}
  window: 1h
  target: "<= 3600"
  ```
  Não é suficiente um SLO descrito em texto sem métrica base definida.

- **Inv‑G0‑4 — Alinhamento com Programas/E28.**  
  O recorte não contradiz decisões maiores de programa/épico: por exemplo, não inclui componentes explicitamente marcados como fora do escopo de E28 ou descontinuados em sprints anteriores.

#### Execução de G0 (script + revisão)

G0 é composto por duas camadas:

1. **Validação automatizada** (script, por exemplo `bin/s33_g0_scope_and_baseline.sh`):
   - Carrega `s33_scope_ops.md` e `s33_components_map.yaml` (via parser simples ou checklist semi‑automatizado);
   - Checa consistência mínima (componentes citados em um arquivo existem no outro, ausência de duplicatas, formatação válida);
   - Verifica a presença de métrica base para cada SLO;
   - Gera um `S33_G0_scope_and_baseline.json` com resultado e checklist.

2. **Revisão curta em dupla** (ritual):
   - Pelo menos uma pessoa de Ops e uma de Engenharia revisam o recorte e confirmam que ele é realista para a sprint;
   - Qualquer dúvida sobre inclusão/exclusão de componentes gera ajuste no doc antes de marcar o gate como PASS.

**Saída de G0:** gate marcado como PASS/NO_GO, scorecard salvo, e recorte congelado (mudanças posteriores precisam ser tratadas como change request, justificadas e documentadas).

---

### 2.2.2 G1 — Modelo de Incident e domínio de operação coerente (detalhado)

**Pergunta que G1 responde:**
> "Temos uma entidade Incident sólida, capaz de representar a realidade operacional da S33 sem contradições nem gambiarras?"

#### Artefatos formais de G1

G1 se ancora em quatro elementos principais:

1. **Modelo de dados de Incident**, com migrations aplicadas (por exemplo, `migrations/versions/xxxx_s33_incident_model.py`), incluindo campos como:
   - `id` (identificador único);
   - `state` (enum de estados);
   - `severity` (enum de severidade);
   - `title`, `description`;
   - `components` relacionados (lista de `component_id`);
   - `slo_ids` relacionados (quando aplicável);
   - timestamps (`created_at`, `updated_at`, `resolved_at` etc.);
   - metadados adicionais (ex.: `created_by`, `last_updated_by`).

2. **Definição explícita de estados e transições**, em doc (por exemplo, `programa 1/Epico 28/Sprint 33/s33_incidents_lifecycle.md`) ou em código:
   - Estados possíveis (e.g.: `OPEN`, `TRIAGE`, `MITIGATED`, `RESOLVED`, `POSTMORTEM_PENDING`, `CLOSED`);
   - Regras de transição (por exemplo, `OPEN → TRIAGE → MITIGATED → RESOLVED → POSTMORTEM_PENDING → CLOSED` e transições laterais permitidas/negadas);
   - quem pode realizar cada transição (tipicamente por papel, mas aqui pode ser simplificado).

3. **Enumeração de severidades e categorias**, também documentada (ex.: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), com exemplos de uso ligados ao recorte da S33.

4. **Testes automatizados** (por exemplo, `tests/domain/test_incidents_model.py`), cobrindo:
   - criação de incidentes válidos;
   - tentativa de criação inválida (campos obrigatórios ausentes, estado inválido etc.);
   - sequências de transição de estado válidas e inválidas;
   - ligação coerente com componentes e SLOs.

#### Invariantes de G1

Para G1 ser considerado "PASS", os seguintes invariantes precisam ser seguidos:

- **Inv‑G1‑1 — Ciclo de vida acíclico e bem definido.**  
  O grafo de estados de Incident não tem loops não intencionais (por exemplo, não é possível ir de `CLOSED` de volta para `OPEN` sem uma ação explícita de reabertura, se essa for permitida). Estados terminais são claramente marcados.

- **Inv‑G1‑2 — Severidades finitas e bem exemplificadas.**  
  O conjunto de severidades é finito, pequeno e está documentado com exemplos práticos ligados ao recorte da S33 (por exemplo, quando uma falha em fonte oficial crítica é `HIGH` vs `CRITICAL`).

- **Inv‑G1‑3 — Ligação com componentes monitorados.**  
  Todo incidente relacionado ao recorte da S33 está ligado a pelo menos um `component_id` presente no mapa de componentes de G0. Não existem incidentes referindo‑se a componentes inexistentes ou nomes soltos em texto.

- **Inv‑G1‑4 — Ligação com SLOs quando aplicável.**  
  Para incidentes cujo gatilho é uma violação de SLO, o `slo_id` correspondente está registrado no incidente.

- **Inv‑G1‑5 — Timestamps consistentes.**  
  `created_at <= updated_at <= resolved_at <= closed_at` (quando presentes). Nenhum incidente apresenta regressão de tempo.

#### Execução de G1 (script + testes)

G1 é verificado em duas camadas complementares:

1. **Testes automatizados de domínio**:
   - Rodando, por exemplo, via `pytest` ou script dedicado `bin/s33_g1_incidents_domain.sh`;
   - Validando criação, transições e invariantes de timestamps/severidades;
   - Reprovando casos de estados inválidos ou de incidentes sem ligação com componentes relevantes.

2. **Inspeção manual estruturada**:
   - Criação de uma pequena amostra de incidentes de teste (por exemplo, 3–5 incidentes cobrindo diferentes severidades e estados finais), usando os componentes e SLOs do recorte;
   - Revisão em dupla (Ops + Engenharia) para confirmar que a representação é natural e útil: título, descrição, componentes, severidade e estados fazem sentido para o tipo de problema.

**Scorecard de G1:**

Um arquivo como `out/scorecards/S33_G1_incidents_domain.json` registra:

- Resultado global (PASS/NO_GO);
- Número de testes automatizados executados e quantos falharam;
- Lista dos invariantes checados com `true/false`;
- Referências para os docs de lifecycle e enums.

G1 só é marcado como "PASS" quando os testes passam, as invariantes são verdadeiras e a amostra manual é considerada representativa e confortável pelos papéis envolvidos.

---

### 2.2.3 Relação entre G0 e G1 com os demais gates

G0 e G1 formam o "alicerce semântico" da S33. A partir deles:

- G2 (cockpit) depende do mapa de componentes e de incidents coerentes para exibir algo que não seja ruído;
- G3 (SLOs) depende da lista de SLOs, métricas e ligações com componentes e incidentes para ser mais que um gráfico bonitinho;
- G4 (runbooks e evidência) depende de incidents bem modelados para ancorar bundles e aprendizado;
- G5 (ORR operacional) só faz sentido se escopo, componentes e incidentes tiverem sido solidificados por G0 e G1.

Este bloco deve ser tomado como referência direta pelo time que implementará os scripts de gate (`bin/s33_g0_*.sh`, `bin/s33_g1_*.sh`), os scorecards e as pastas de evidência (`out/evidence/S33_G0_*`, `out/evidence/S33_G1_*`). Qualquer divergência entre esses artefatos e este texto precisa ser tratada como bug de especificação e corrigida antes da sprint ser tratada como "GO" em ORR.
