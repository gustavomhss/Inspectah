# Sprint 5 — Capítulo 2 (v2)
## Gates de Validação da Sprint
### Inspectah Data Hub Core + AI Claim Normalizer v0.1 (por fonte)

> v2 — Versão com rigor 15/10. Cada gate tem entrada oficial (script), insumos, pré-condições, passos, saídas e critérios de PASS/FAIL totalmente mecânicos. Não existe "aprovado com ressalvas". Qualquer FAIL implica NO-GO até correção da causa raiz.

---

## 0. Convenções gerais

- Todos os scripts de gates vivem em `bin/` e começam com `s5_gate_`.
- Todas as evidências de gates vivem em `out/s5_gates/` por subpasta.
- Checklists humanas vivem em `docs/sprint_5/gates/`.
- Resultado de cada gate é registrado em um arquivo JSON de scorecard.

Formato padrão de scorecard:

```json
{
  "gate_id": "G3",
  "status": "PASS" | "FAIL",
  "checked_at": "2025-..T..Z",
  "notes": "...",
  "metrics": {
    "...": 123
  }
}
```

Status permitido: apenas `PASS` ou `FAIL`.

---

## 1. Lista oficial de gates

- **G0 — Spec & DNA Lock**
- **G1 — Schema & Contracts Gate**
- **G2 — Components Gate (Unitário + Contrato)**
- **G3 — Pipeline Gate (End-to-End com Fixtures)**
- **G4 — AI Integration Gate (GPT‑4.1 mini real)**
- **G5 — Operator Journey Gate (UX interna)**
- **G6 — Observability & Metrics Gate**
- **G7 — Stability & GO/NO-GO Final**

Cada gate é definido a seguir em formato totalmente padronizado.

---

## 2. Gate G0 — Spec & DNA Lock

**ID:** G0  
**Nome:** Spec & DNA Lock  
**Script oficial:** `bin/s5_gate_g0_spec_lock.sh`  
**Pasta de evidências:** `out/s5_gates/G0_spec_lock/`  
**Checklist humana:** `docs/sprint_5/gates/G0_spec_lock_checklist.md`

### 2.1 Insumos obrigatórios

- `docs/sprint_5/s5_capitulo_1_core_v6.md` (ou nome equivalente acordado para o Capítulo 1 v6).
- Diretório `docs/sprint_5/` existente.

### 2.2 Pré-condições

- Repositório em estado limpo (`git status` sem pendências).
- Não há arquivos com sufixo `_draft` ou `_wip` em `docs/sprint_5/` relacionados ao Capítulo 1.

### 2.3 Execução

`bin/s5_gate_g0_spec_lock.sh` deve:

1. Verificar presença do Capítulo 1 v6 em local canônico.
2. Checar se não existem versões concorrentes (draft/wip) do Capítulo 1.
3. Verificar consistência básica entre o Capítulo 1 e os schemas (nomes de enums/estados presentes).
4. Gerar scorecard `out/s5_gates/G0_spec_lock/scorecard.json` com status.

### 2.4 Saídas obrigatórias

- `out/s5_gates/G0_spec_lock/scorecard.json` com `status = PASS` ou `FAIL`.
- `docs/sprint_5/gates/G0_spec_lock_checklist.md` preenchido e versionado.

### 2.5 Critérios de PASS/FAIL

- **PASS:**
  - Capítulo 1 v6 presente e sem concorrentes.
  - Nenhuma inconsistência nominal óbvia com schemas (ex.: enum citado no texto ausente do schema).
- **FAIL:**
  - Qualquer ausência de Capítulo 1 v6 em local canônico.
  - Qualquer rascunho concorrente encontrado.
  - Qualquer divergência nominal crítica entre especificação e schemas.

---

## 3. Gate G1 — Schema & Contracts Gate

**ID:** G1  
**Nome:** Schema & Contracts  
**Script oficial:** `bin/s5_gate_g1_schema_contracts.sh`  
**Pasta de evidências:** `out/s5_gates/G1_schema_contracts/`  
**Checklist humana:** `docs/sprint_5/gates/G1_schema_contracts_checklist.md`

### 3.1 Insumos obrigatórios

- Schemas JSON:
  - `schemas/inspectah_item_v0_1.json`
  - `schemas/inspectah_claim_v0_1.json`
- Módulo de equivalence key (ex.: `inspectah/equivalence_key.py`).
- Arquivo de contratos/resumo: `docs/sprint_5/s5_contracts_overview.md`.
- Testes:
  - `tests/test_schema_item.py`
  - `tests/test_schema_claim.py`
  - `tests/test_equivalence_key.py`

### 3.2 Pré-condições

- G0 com `status = PASS`.
- Todos os arquivos de schema presentes.

### 3.3 Execução

`bin/s5_gate_g1_schema_contracts.sh` deve:

1. Rodar testes de schema e equivalence_key:
   - `pytest tests/test_schema_item.py tests/test_schema_claim.py tests/test_equivalence_key.py`.
2. Validar que enums `claim_type`, `polarity`, `local_verdict` nos schemas batem 1:1 com o Capítulo 1.
3. Validar que o arquivo `s5_contracts_overview.md` contém pré/pós-condições para Watcher, Evidence Builder, Normalizer, Indexer.
4. Emitir `scorecard.json` com resultados e métricas (número de testes executados, tempo, etc.).

### 3.4 Saídas obrigatórias

- `out/s5_gates/G1_schema_contracts/scorecard.json`.
- Logs de testes unitários em `out/s5_gates/G1_schema_contracts/tests.log`.

### 3.5 Critérios de PASS/FAIL

- **PASS:**
  - 100% dos testes em `tests/test_schema_*.py` e `tests/test_equivalence_key.py` passam.
  - Enums dos schemas são idênticos aos da especificação.
  - `s5_contracts_overview.md` cobre todos os componentes centrais.
- **FAIL:**
  - Qualquer teste falho.
  - Divergência de enums.
  - Ausência de contratos para qualquer componente central.

---

## 4. Gate G2 — Components Gate (Unitário + Contrato)

**ID:** G2  
**Nome:** Components (Core)  
**Script oficial:** `bin/s5_gate_g2_components.sh`  
**Pasta de evidências:** `out/s5_gates/G2_components/`  
**Checklist humana:** `docs/sprint_5/gates/G2_components_checklist.md`

### 4.1 Insumos obrigatórios

- Código dos componentes centrais:
  - Watcher Engine (`inspectah/watchers/*.py` ou equivalente).
  - Evidence Builder (`inspectah/evidence/*.py`).
  - AI Claim Normalizer (`inspectah/normalizer/*.py`).
  - Indexer/Storage (`inspectah/indexer/*.py`).
- Testes de componentes: `tests/components/` (unitários e de contrato).

### 4.2 Pré-condições

- G1 com `status = PASS`.
- Todos os módulos acima presentes.

### 4.3 Execução

`bin/s5_gate_g2_components.sh` deve:

1. Rodar `pytest tests/components/` com cobertura mínima definida (ex.: ≥ 80% para módulos core).
2. Coletar métricas básicas:
   - número de testes,
   - taxa de sucesso,
   - tempo total.
3. Gerar scorecard com resultados.

### 4.4 Saídas obrigatórias

- `out/s5_gates/G2_components/scorecard.json`.
- `out/s5_gates/G2_components/tests.log`.

### 4.5 Critérios de PASS/FAIL

- **PASS:**
  - 100% dos testes de componentes passam.
  - Cobertura mínima atingida para componentes core (threshold definido e medido).
- **FAIL:**
  - Qualquer teste falho.
  - Cobertura para módulos core abaixo do threshold.

---

## 5. Gate G3 — Pipeline Gate (End-to-End com Fixtures)

**ID:** G3  
**Nome:** Pipeline E2E (Fixtures)  
**Script oficial:** `bin/s5_gate_g3_pipeline_fixtures.sh`  
**Pasta de evidências:** `out/s5_gates/G3_pipeline_fixtures/`  
**Checklist humana:** `docs/sprint_5/gates/G3_pipeline_fixtures_checklist.md`

### 5.1 Insumos obrigatórios

- Fixtures de fontes:
  - `fixtures/s5/rss_*`
  - `fixtures/s5/api_*`
  - `fixtures/s5/html_*`
- Golden data:
  - `tests/golden/item_*.json`
- Script de verificação de invariantes:
  - `bin/s5_check_invariants.sh`

### 5.2 Pré-condições

- G2 com `status = PASS`.
- Ambiente configurado para rodar pipeline em modo offline (sem rede externa).

### 5.3 Execução

`bin/s5_gate_g3_pipeline_fixtures.sh` deve:

1. Rodar pipeline S0→S4 usando exclusivamente fixtures.
2. Gerar itens S4 e normalizados gravados em diretórios de teste.
3. Rodar `bin/s5_check_invariants.sh`.
4. Comparar itens normalizados com golden data (diff semântico).
5. Emitir scorecard com contagens de itens, violações e diffs.

### 5.4 Saídas obrigatórias

- `out/s5_gates/G3_pipeline_fixtures/scorecard.json`.
- `out/s5_gates/G3_pipeline_fixtures/invariants_report.json`.
- `out/s5_gates/G3_pipeline_fixtures/golden_diff.json`.

### 5.5 Critérios de PASS/FAIL

- **PASS:**
  - `s5_check_invariants.sh` reporta zero violações.
  - Diffs contra golden são apenas em campos esperados (se houver) e documentados na checklist; idealmente, zero diffs.
- **FAIL:**
  - Qualquer violação de invariante.
  - Diffs não explicados em golden data.

---

## 6. Gate G4 — AI Integration Gate (GPT‑4.1 mini real)

**ID:** G4  
**Nome:** AI Integration (Real)  
**Script oficial:** `bin/s5_gate_g4_ai_integration.sh`  
**Pasta de evidências:** `out/s5_gates/G4_ai_integration/`  
**Checklist humana:** `docs/sprint_5/gates/G4_ai_integration_checklist.md`

### 6.1 Insumos obrigatórios

- Configuração segura de IA (`config/ai_gpt_4_1mini.yaml`).
- Conjunto de itens reais para teste (ex.: `fixtures/s5/real_texts/*.txt`).

### 6.2 Pré-condições

- G3 com `status = PASS`.
- Credenciais válidas para IA configuradas via env/secret.

### 6.3 Execução

`bin/s5_gate_g4_ai_integration.sh` deve:

1. Rodar normalização com GPT‑4.1 mini em um conjunto de N itens reais (N definido em config, ex.: 100).
2. Medir:
   - % de respostas JSON válidas;
   - % de itens relevantes com pelo menos 1 claim;
   - latência média e p95;
   - tokens médios por chamada.
3. Gerar amostra de K itens (ex.: 20) para revisão manual, marcada em `out/s5_gates/G4_ai_integration/sample_review/`.
4. Emitir scorecard com métricas e links para amostra.

### 6.4 Saídas obrigatórias

- `out/s5_gates/G4_ai_integration/scorecard.json`.
- `out/s5_gates/G4_ai_integration/raw_calls_log.jsonl` (logs de chamadas censurados de segredos).
- Amostra de revisão humana: `sample_review/`.

### 6.5 Critérios de PASS/FAIL

- **PASS:**
  - ≥ 95% das respostas são JSON válidos aderentes ao schema.
  - ≥ 90% dos itens relevantes têm ao menos um claim.
  - Revisão manual não encontra invenções grosseiras (claims sem suporte no texto) acima de um limiar mínimo (ex.: ≤ 5% da amostra).
- **FAIL:**
  - Qualquer métrica abaixo dos thresholds.
  - Invenções graves detectadas na amostra acima do limite.

---

## 7. Gate G5 — Operator Journey Gate (UX interna)

**ID:** G5  
**Nome:** Operator Journey  
**Script oficial:** `bin/s5_gate_g5_operator_journey.sh` (orquestração do teste)  
**Pasta de evidências:** `out/s5_gates/G5_operator_journey/`  
**Checklist humana:** `docs/sprint_5/gates/G5_operator_journey_checklist.md`

### 7.1 Insumos obrigatórios

- UI Admin & Explore v0 funcionando.
- Roteiro de teste: `docs/sprint_5/gates/G5_operator_scenario.md`.

### 7.2 Pré-condições

- G4 com `status = PASS`.
- Operador de teste selecionado (não autor do código).

### 7.3 Execução

`bin/s5_gate_g5_operator_journey.sh` (script de apoio) deve:

1. Inicializar ambiente com base de dados limpa.
2. Criar usuário de operador de teste (se necessário).
3. Abrir instruções do cenário.
4. Registrar tempos de início/fim do fluxo.

O operador deve, seguindo o cenário:

1. Cadastrar uma nova fonte simples via UI.
2. Ativar a fonte.
3. Disparar um run ou aguardar.
4. Abrir Explore, localizar itens.
5. Abrir item, visualizar evidência + texto + claims.

### 7.4 Saídas obrigatórias

- `out/s5_gates/G5_operator_journey/report.md` com:
  - passos realizados;
  - tempo total;
  - pontos de confusão ou bloqueio.
- `scorecard.json` com status.

### 7.5 Critérios de PASS/FAIL

- **PASS:**
  - Operador conclui o fluxo **sem ajuda do autor do código**.
  - p50 do tempo para fonte simples ≤ 5 minutos.
  - Operador responde "Sim" à pergunta: "Você entendeu claramente o que a fonte disse e como isso apareceu em claims?".
- **FAIL:**
  - Necessidade de ajuda técnica não documentada.
  - Operador não consegue completar o fluxo.
  - Interface gera confusão grave (campos sem explicação, labels obscuros etc.).

---

## 8. Gate G6 — Observability & Metrics Gate

**ID:** G6  
**Nome:** Observability & Metrics  
**Script oficial:** `bin/s5_gate_g6_observability.sh`  
**Pasta de evidências:** `out/s5_gates/G6_observability/`  
**Checklist humana:** `docs/sprint_5/gates/G6_observability_checklist.md`

### 8.1 Insumos obrigatórios

- Endpoint de métricas ou logs estruturados.
- Configuração de painel mínimo (`dashboards/s5_inspectah_core.json` ou equivalente).

### 8.2 Pré-condições

- G5 com `status = PASS`.
- Sistema em execução (dev ou staging).

### 8.3 Execução

`bin/s5_gate_g6_observability.sh` deve:

1. Consultar endpoint de métricas e verificar presença de:
   - métricas de ingestão,
   - métricas de evidência,
   - métricas de normalização,
   - métricas de estados.
2. Validar que o painel mínimo está carregável e contém gráficos esperados.
3. Gerar screenshot ou snapshot dos gráficos principais (mesmo se textualizado).

### 8.4 Saídas obrigatórias

- `out/s5_gates/G6_observability/metrics_snapshot.json`.
- `out/s5_gates/G6_observability/dashboard_snapshot.md`.
- `scorecard.json`.

### 8.5 Critérios de PASS/FAIL

- **PASS:**
  - Todas as métricas definidas no Capítulo 1 estão disponíveis.
  - Painel mínimo apresenta visão por fonte, por estado e por normalização.
- **FAIL:**
  - Ausência de métricas centrais.
  - Painel mínimo incompleto ou inexistente.

---

## 9. Gate G7 — Stability & GO/NO-GO Final

**ID:** G7  
**Nome:** Stability & Final Decision  
**Script oficial:** `bin/s5_gate_g7_stability_go_no_go.sh`  
**Pasta de evidências:** `out/s5_gates/G7_stability/`  
**Checklist humana:** `docs/sprint_5/gates/G7_stability_checklist.md`

### 9.1 Insumos obrigatórios

- Sistema rodando em ambiente representativo (dev/staging).
- Scripts de replay/simulações, se necessário.

### 9.2 Pré-condições

- G0–G6 com `status = PASS`.

### 9.3 Execução

`bin/s5_gate_g7_stability_go_no_go.sh` deve:

1. Rodar o sistema por um período equivalente a 7 dias (real ou simulado via replay).
2. Coletar séries temporais das métricas principais:
   - ingest_latency_p95;
   - explore_query_p95;
   - evidence_verification_failures_total;
   - watcher_success_rate;
   - normalize_failures_total.
3. Calcular estatísticas e comparar com thresholds definidos.
4. Emitir `scorecard.json` com `status` e resumo.

### 9.4 Saídas obrigatórias

- `out/s5_gates/G7_stability/metrics_timeseries.json`.
- `out/s5_gates/G7_stability/scorecard.json`.
- `docs/sprint_5/s5_wrap_exec.md` (wrap executivo da sprint).

### 9.5 KPIs bloqueantes (tabela)

| Métrica                            | Condição PASS                          |
|------------------------------------|----------------------------------------|
| ingest_latency_p95                 | ≤ limite definido (ex.: 2s)            |
| explore_query_p95                  | ≤ limite definido (ex.: 500ms)         |
| evidence_verification_failures_tot | = 0 ao final da janela                 |
| watcher_success_rate               | ≥ 99% no período                       |
| normalize_failures_total           | estável e dentro de faixa aceitável    |

Os valores exatos dos limites são definidos no Capítulo 1 e parametrizados em config, mas o gate deve compará-los de forma mecânica.

### 9.6 Critérios de PASS/FAIL

- **PASS:**
  - Todos os KPIs bloqueantes atendem às condições da tabela.
  - Não houve incidentes de perda de dados ou corrupção de evidência.
  - Wrap executivo documenta riscos e próximos passos de forma honesta.
- **FAIL:**
  - Qualquer KPI bloqueante fora da faixa.
  - Falhas graves não corrigidas.

---

## 10. Regras globais dos gates

1. Nenhum gate pode ser ignorado ou "adiado" para depois da sprint.
2. Todos os gates produzem `scorecard.json` e evidências em `out/s5_gates/`.
3. Qualquer `status = FAIL` em um gate implica NO-GO até correção.
4. Mudanças estruturais futuras em componentes centrais exigem rerun de pelo menos G1–G3.
5. Os gates são estáveis: só podem ser alterados através de atualização consciente do Capítulo 2 + scripts correspondentes.

Este Capítulo 2 (v2) é a régua final da Sprint 5 do Inspectah. A implementação deve ser planejada para passar por esses gates; se algo "não cabe" neles, o problema está na implementação, não nos gates.

