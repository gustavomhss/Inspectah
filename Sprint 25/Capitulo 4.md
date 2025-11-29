# Sprint 25 — Capítulo 4 (v2)
## Execução Hardcore, Waves, Evidências e Rotina de Trabalho

> Versão v2 — Refinado pelo Squad Verdade & Interpretação com revisão pesada de Stonebraker, Norvig, Pearl, Percy, Victor, Jobs e Conselho. Este capítulo é a **Ferrari operacional** da S25: um plano de execução sofisticado, porém simples, objetivo, seguro e viável, sempre com uma regra de ouro:
>
> **Todo código produzido na S25 deve ser legível, auditável e facilmente mantido por humanos competentes. Nenhum "bicho de 7 cabeças" que só IA entende.**

---

### 4.1 Princípios operacionais da Sprint 25

A S25 mexe no coração da verdade do Inspectah. Para não explodir o paciente na mesa, a execução segue cinco princípios explícitos:

1. **Sofisticação por camadas, não por complexidade acidental**  
   - Modelos e serviços de domínio pequenos, combináveis, com tipos claros.  
   - Nada de mega-orquestradores impenetráveis.

2. **Simplicidade como critério de aceite**  
   - Se uma regra de verdade/política só pode ser explicada via diagrama de 20 passos, ela precisa ser redesenhada.  
   - O revisor humano precisa conseguir recontar a lógica em 1–2 parágrafos.

3. **Objetividade na aferição**  
   - Tudo passa pelos gates e scorecards de Cap. 2.  
   - Sem "acho que está bom"; só métricas, testes, evidências.

4. **Segurança como default**  
   - Preferir falhar travando a promover verdade frágil.  
   - Categoria "domínios sensíveis" (política, saúde etc.) sempre sob fluxos endurecidos.

5. **Perfeição pragmática**  
   - Perfeição = o sistema se comporta bem **hoje**, e o código é
     fácil de evoluir **amanhã**.  
   - Nada de gambiarras "temporárias" sem registro em scorecard.

Esses princípios guiam decisões de execução, refator, priorização e trade-offs ao longo da sprint.

---

### 4.2 Modo de trabalho: trilha dupla Domínio ↔ Operação

Para não virar uma sprint de "paper bonito" sem lastro, a S25 segue duas trilhas paralelas, sincronizadas diariamente:

- **Trilha Domínio (backend/core)**  
  Foca em modelos, serviços, invariantes e testes dos domínios:
  - `truth`, `policies`, `layers`, `context`, `threatmodel`, `agents`, `incidents`.

- **Trilha Operação (console/infra/gates)**  
  Foca em:
  - Console & Agent Studio,
  - scripts `bin/s25_*`,
  - linters/CI,
  - evidências & scorecards.

Regra: nenhuma entrega de domínio é considerada "pronta" enquanto:

- não tiver testes mínimos,
- não tiver caminhos de observabilidade (logs, traces, outputs),
- não tiver pelo menos um script de gate tocando o que foi feito.

---

### 4.3 Branches, PRs e disciplina de mudança

**Branches base:**

- `main` — linha estável.
- `feature/s25_truth_v1_5` — tronco da Sprint 25.

**Branches temáticas (exemplos):**

- `feature/s25_truthstate_core` — Truth‑DB & TruthState.
- `feature/s25_policies_engine` — PromotionPolicy.
- `feature/s25_layers_context` — Sistema de Camadas + Context Service.
- `feature/s25_threatmodel_metrics` — ThreatModel & métricas.
- `feature/s25_console_agent_studio` — Console & Agent Studio.
- `feature/s25_incidents_governance` — Incidentes / Governança.
- `chore/s25_gates_and_ci` — scripts S25_G*, linters, ajustes de CI.

**Regras duras:**

- Nada direto em `main`.
- Toda mudança relevante ligada a um gate deve mencionar o gate no título/descrição da PR.
- PRs só entram em `feature/s25_truth_v1_5` com:
  - testes locais rodados;
  - pelo menos um script de gate relevante executado (`bin/s25_gX_*`);
  - apontamento para evidências (`out/evidence/S25_GX_*`).

**Revisão humana:**

- Toda PR S25 precisa de pelo menos 1 revisor focado em **legibilidade** de código.
- Qualquer trecho que "parece brilhante demais" precisa ser simplificado ou bem documentado.

---

### 4.4 Waves da Sprint 25 — visão geral

A execução é organizada em quatro waves, cada uma ligada a um conjunto de gates:

- **Wave 0 — Baseline & infraestrutura**  
  - Gate alvo: S25_G0.  
  - Objetivo: repo limpo, docs presentes, filemap mínimo criado, ci_local OK.

- **Wave 1 — Núcleo de Verdade & Políticas**  
  - Gates alvo: S25_G1, S25_G2.  
  - Objetivo: Truth‑DB + PromotionPolicy funcionando end‑to‑end em dev.

- **Wave 2 — Camadas, Contexto e ThreatModel**  
  - Gates alvo: S25_G3, S25_G5, preparação de S25_G7.  
  - Objetivo: pipeline de camadas redesenhado e conectado a Dossiês e sinais.

- **Wave 3 — Console, Agent Studio, Incidentes, Código Humano & ORR**  
  - Gates alvo: S25_G4, S25_G6, S25_G7, S25_G8.  
  - Objetivo: operação humana plena + verificação de código humano + ORR final.

Cada wave termina com um pequeno "mini‑ORR" interno (checklist rápido):

- gates-alvo em GO ou GO_WITH_RISKS aceitável,
- scorecards e evidências presentes,
- docs atualizados.

---

### 4.5 Wave 0 — Baseline & setup (S25_G0)

**Objetivo:** ter um terreno firme para construir a S25.

**Passos concretos:**

1. Criar branch `feature/s25_truth_v1_5` a partir de `main`.
2. Garantir que os capítulos da S25 (0, 0.A, 0.5, 0.5.A, 1, 2, 3, 4, 7) estão em `docs/` com nomes estáveis.
3. Criar diretórios mínimos, se não existirem:
   - `app/truth/`, `app/policies/`, `app/layers/`, `app/context/`, `app/threatmodel/`, `app/agents/`, `app/incidents/`;
   - `out/scorecards/`, `out/evidence/`;
   - `configs/promotion_policies/`, `configs/threatmodel/`.
4. Implementar `bin/s25_g0_scope_and_baseline.sh` para:
   - verificar presença de docs;
   - validar estrutura de diretórios;
   - rodar smoke test (ex.: `pytest -q` em subset + lint rápido se já existir).
5. Rodar `bin/s25_g0_scope_and_baseline.sh` e inspecionar scorecard:
   - `out/scorecards/S25_G0_scope_and_baseline.json`;
   - evidências em `out/evidence/S25_G0_scope_and_baseline/`.
6. Abrir PR `S25: baseline & filemap` e mergear em `feature/s25_truth_v1_5`.

**Saída esperada:** Gate S25_G0 = GO; repo preparado; nenhum "esqueleto" gigante já criado — apenas cascas mínimas.

---

### 4.6 Wave 1 — Núcleo de Verdade & Políticas (S25_G1, S25_G2)

Wave 1 constrói o motor de Verdade/Fato v1.5 em dois eixos: Truth‑DB e PromotionPolicy.

#### 4.6.1 Execução — Truth‑DB & TruthState (S25_G1)

Branch: `feature/s25_truthstate_core`.

**Objetivo técnico:** ter `TruthRecord`, `TruthChangeEvent`, `DecisionRecord` funcionando com transições testadas e visíveis via API.

Passos:

1. **Modelagem de estados**  
   - Implementar `TruthState` em `app/truth/enums.py` com docstring clara por estado.

2. **Modelos & migrações**  
   - Implementar `TruthRecord`, `TruthChangeEvent`, `DecisionRecord` em `app/truth/models.py`.
   - Criar migração `XXXX_s25_truth_models.py` com criação/alteração de tabelas.

3. **Serviços de domínio**  
   - Em `app/truth/service.py`, implementar:
     - `apply_transition(truth_record, recommendation)`;
     - `get_timeline(truth_record_id)`;
     - verificações de invariantes (sem side effect obscuro).

4. **APIs admin/dev**  
   - Implementar `app/truth/api.py` com endpoints de leitura (GET de records/timelines).

5. **Testes**  
   - `tests/truth/test_truth_transitions.py` para cenários normais;
   - `tests/truth/test_truth_invariants.py` para tentativas de transições inválidas.

6. **Gate S25_G1**  
   - Criar `bin/s25_g1_truthstate_machine.sh` rodando migração + testes;
   - Gerar `S25_G1_truthstate_machine.json` e evidências.

**Critério de saída da parte Truth‑DB:** Gate S25_G1 = GO, testes cobrindo transições críticas, código limpo e comentado.

#### 4.6.2 Execução — PromotionPolicy & Engine (S25_G2)

Branch: `feature/s25_policies_engine`.

**Objetivo técnico:** ter uma engine de política simples, declarativa e auditável.

Passos:

1. **Modelos**  
   - Implementar `PromotionPolicy` e `PromotionPolicyVersion` em `app/policies/models.py`.

2. **Schema & validação**  
   - Criar `app/policies/schema.py` com schemas de YAML/JSON.

3. **Engine pura**  
   - Implementar `evaluate_policy(policy_def, ctx)` em `app/policies/engine.py`, sem dependências de infra.

4. **Context builder**  
   - Implementar `PolicyEvaluationContext` e builder em `app/policies/context_builder.py`.

5. **Configuração de políticas**  
   - Criar `configs/promotion_policies/global_default.yaml` + um exemplo de domínio sensível.

6. **Integração com Truth‑DB**  
   - Ajustar `truth.service.apply_transition` para registrar `policy_id`/`policy_version`.

7. **Testes e simulações**  
   - `tests/policies/test_policy_engine.py` para cenários básicos;
   - `tests/policies/test_policy_simulation.py` com simulações.

8. **Gate S25_G2**  
   - `bin/s25_g2_promotion_policy.sh` para validar schemas, rodar testes e simulações.

Critério de saída Wave 1: S25_G1 e S25_G2 = GO; já é possível aplicar política a claims de teste e ver TruthState mudar.

---

### 4.7 Wave 2 — Camadas, Contexto e ThreatModel (S25_G3, S25_G5, preparação S25_G7)

Wave 2 faz a ponte entre ingestão, contexto, políticas e sinais de ameaça.

#### 4.7.1 Execução — Sistema de Camadas & Context Service (S25_G3)

Branch: `feature/s25_layers_context`.

Passos:

1. **Modelos de trace**  
   - Implementar `LayerExecution` e `LayersTrace` em `app/layers/models.py`.

2. **Orquestrador de pipeline**  
   - Em `app/layers/orchestrator.py`, expor funções do tipo:
     - `run_standard_pipeline(claim_id)`;
     - `run_hardened_pipeline(claim_id)` para domínios sensíveis.

3. **Router de domínios**  
   - `app/layers/router.py` mapeando claim_type/domain → pipeline.

4. **Context Service**  
   - Implementar `ContextDossier` e `context.service` com funções como:
     - `build_entity_dossier(entity_id, window)`;
     - `build_case_dossier(case_id, window)`.

5. **Integração com Truth‑DB & Policies**  
   - Pipeline constrói `PolicyEvaluationContext` e chama engine de políticas; depois chama `truth.service.apply_transition`.

6. **Integração com Debunker/Humano (S24)**  
   - Adaptar entradas/saídas para registrar decisões de debunker/humano dentro de `LayersTrace`.

7. **Testes end‑to‑end**  
   - `tests/layers/test_pipeline_end_to_end.py` com casos simples e de conflito;
   - `tests/context/test_context_dossiers.py` para dossiês.

8. **Gate S25_G3**  
   - `bin/s25_g3_layers_pipeline_integrated.sh` rodando testes e produzindo exemplos de ThoughtTrace/DecisionTrace nas evidências.

#### 4.7.2 Execução — ThreatModel & Métricas (S25_G5)

Branch: `feature/s25_threatmodel_metrics`.

Passos:

1. Implementar `ThreatSignal` e `ThreatMetricSnapshot` em `app/threatmodel/models.py`.
2. Implementar funções de métricas em `app/threatmodel/computations.py`.
3. Implementar `app/threatmodel/service.py` para orquestrar cálculos.
4. Criar `configs/threatmodel/thresholds.yaml`.
5. Criar testes em `tests/threatmodel/test_metrics_basic.py`.
6. Criar `bin/s25_g5_threatmodel_signals_and_metrics.sh`.

#### 4.7.3 Preparação — Cenários adversariais (S25_G7)

1. Escrever `docs/sprint_25_threat_scenarios.md` com cenários descritos.
2. Implementar `app/threatmodel/test_scenarios.py`.
3. Criar skeleton de `bin/s25_g7_threat_model_coverage.sh`.

Saída Wave 2: S25_G3 e S25_G5 = GO; S25_G7 com skeleton funcional.

---

### 4.8 Wave 3 — Console, Agent Studio, Incidentes, Código Humano & ORR

Wave 3 conecta tudo com humano na ponta e garante qualidade do código e visão adversarial.

#### 4.8.1 Execução — Console & Agent Studio (S25_G4)

Branch: `feature/s25_console_agent_studio`.

Passos:

1. **Truth Console**  
   - Implementar `TruthRecordPage` (drill‑down completo).  
   - Componentes: TruthTimeline, ThoughtTraceView, DecisionTraceView.

2. **Agent Studio**  
   - `AgentStudioPage` com sidebar de agentes;  
   - editor de versão (instruções, tools, params) + uploader de KB;  
   - runner de testes/regressões ligado a `AgentTestRun`.

3. **Incidentes & Threat Dashboard**  
   - Páginas de incidentes (lista/detalhe) ligadas ao backend;  
   - Threat Dashboard com cards de métricas chave.

4. **Integração API**  
   - Implementar clientes `src/api/truth.ts`, `src/api/agents.ts`, `src/api/incidents.ts`, `src/api/threat.ts`.

5. **Gate S25_G4**  
   - `bin/s25_g4_console_and_agent_studio.sh` rodando testes/build do front e scripts de cenários manuais guiados (ex.: usar Playwright ou scripts HTTP).

#### 4.8.2 Execução — Código humano (S25_G6)

Branch: `chore/s25_gates_and_ci`.

Passos:

1. Configurar/ajustar linters e typecheckers (Python + TS).
2. Criar `docs/sprint_25_code_review_checklist.md` com critérios de legibilidade.
3. Implementar `bin/s25_g6_human_code_quality.sh` para rodar linters, typechecks, subset de testes e agregar notas de review manual.
4. Rodar revisões manuais focadas nos domínios da S25, registrando notas em `out/evidence/S25_G6_human_code_quality/review_notes/`.

#### 4.8.3 Execução — Cenários adversariais completos (S25_G7)

1. Completar `docs/sprint_25_threat_scenarios.md` com todos os cenários de Cap. 7.
2. Ampliar `test_scenarios.py` para cobrir tudo.
3. Refinar `bin/s25_g7_threat_model_coverage.sh` para rodar todos os cenários, coletar resultados e gerar scorecard.

#### 4.8.4 Execução — ORR final (S25_G8)

1. Implementar `bin/s25_orr.sh` para consolidar todos os `S25_G*.json`.
2. Rodar ORR, salvar logs e atas em `out/evidence/S25_ORR/`.
3. Registrar decisão GO/NO_GO/GO_WITH_RISKS e próximos passos.

Saída Wave 3: S25_G4, G6, G7, G8 = GO; console operável, código humano aprovado, ThreatModel exercitado, ORR concluído.

---

### 4.9 Rotina diária recomendada

Para sustentar tudo isso sem caos, uma rotina diária enxuta e repetível:

1. **Manhã — Domínio**  
   - Focar em 1 domínio (truth, policies, layers, etc.).  
   - Meta: entregar algo que possa ser testado e revisado no mesmo dia.

2. **Meio do dia — Integração & Gates**  
   - Rodar scripts `bin/s25_gX_*` relacionados ao que mudou.  
   - Corrigir falhas simples imediatamente.

3. **Tarde — Operação & UI**  
   - Trabalhar no Console/Agent Studio/Threat Dashboard.  
   - Atualizar docs (Cap. 3, 4, anexos) para refletir o estado real.

4. **Fim de dia (2–3x/semana) — Hardening**  
   - Rodar `bin/s25_g6_human_code_quality.sh`.  
   - Fazer code review cruzado nos módulos críticos.

---

### 4.10 Evidências, logging e auditoria — sem gambiarra

Desde o primeiro commit da S25, todo bloco de trabalho precisa saber **onde suas provas vão morar**:

- Scorecards: `out/scorecards/S25_GX_*.json`.
- Evidências: `out/evidence/S25_GX_*/` com subpastas `tests/`, `logs/`, `screens/`, `analysis/`, `review_notes/` conforme o gate.

Logs de aplicação (back/front) devem:

- carregar IDs de TruthRecord/DecisionRecord/LayersTrace/Incidents em operações relevantes;
- ser suficientemente claros para reconstruir a narrativa de decisão;
- evitar barulho — log bom ajuda auditoria, não escond

