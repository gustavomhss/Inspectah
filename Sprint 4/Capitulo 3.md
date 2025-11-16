# Inspectah — Sprint 4 — Capítulo 3  
**Plano de Execução — Trilhas, Gates, Artefatos e PRs (Versão 10/10)**

> Este capítulo transforma a visão (Capítulo 1) e os gates (Capítulo 2) em um **plano de execução operacional**, sem lacunas: quem faz o quê, em qual ordem, gerando quais artefatos, para colocar T0–T8 em PASS com evidência impecável.

Capítulo 1 = **o que** a Sprint 4 precisa ser.  
Capítulo 2 = **como provar** que chegamos lá (gates T0–T8).  
Capítulo 3 = **como construir**, dia a dia, para que isso aconteça.

---

## 0. Como usar este capítulo

- **PO:** usa como painel de comando: nunca cobra “tarefas soltas”, apenas **entregáveis por trilha/gate**.  
- **Codex / Engenheiros:** usam como **backlog estruturado**: cada linha diz qual gate, quais artefatos, quais tags de PR e quais SLOs/invariantes estão em jogo.  
- **Comitê:** usa como check‑list de execução: se não está aqui, não é oficialmente Sprint 4.

---

## 1. Norte operacional da Sprint 4

Pergunta única da Sprint 4:

> "O Inspectah consegue operar **Fontes P0 reais**, com **Evidências completas**, **Observabilidade confiável** e um **Explore M0** que nunca mostra Item sem Evidência — **validado por T0–T8**?"

Para responder "sim", precisamos encadear, **sem atalhos**:

1. Modelo de dados + invariantes sólidos.  
2. Registry P0 + Field Designer corretos.  
3. Fixtures reais e goldens estáveis.  
4. Vault robusto sob repetição.  
5. Observabilidade por fonte com SLOs medidos (onboarding, detecção, latência de consulta, taxa de sucesso, completude de evidência).  
6. ORR S4 (T0–T7) reprodutível.  
7. T8 GO/NO_GO baseado em fatos.

---

## 2. Trilhas de trabalho e gates-alvo

### 2.1 Visão geral das trilhas

1. **Trilha A — Modelo & Registry & Field Designer**  
   - Gates: T0, T1, T2.  
   - Foco: objetos, invariantes, Fontes P0 e Field Designer.

2. **Trilha B — Fixtures reais & Goldens**  
   - Gates: T3, T4.  
   - Foco: dados reais + comportamento estável.

3. **Trilha C — Vault & Repetição**  
   - Gate: T5.  
   - Foco: integridade do Vault sob repetição.

4. **Trilha D — Observabilidade & SLOs**  
   - Gate: T6.  
   - Foco: métricas, logs, saúde por fonte, experimentos SLO.

5. **Trilha E — ORR / CI S4**  
   - Gate: T7.  
   - Foco: entrypoint único, index de scorecards, reprodutibilidade.

6. **Trilha F — Wrap & T8**  
   - Gate: T8.  
   - Foco: agregação final, decisão de sprint, wrap humano.

---

## 3. Quadro mestre — Trilha × Gate × Artefatos × Tags de PR

> Tabela para o Codex/PO usar como mapa diário. Linhas = blocos de trabalho; colunas = gate, artefatos e marcação de PR.

| ID | Trilha | Gate(s) foco | Artefatos principais | Tags sugeridas de PR |
|----|--------|--------------|----------------------|----------------------|
| A1 | A | T0/T1 | `docs/sprint_4_modelo_dados_invariantes.md`, `docs/sprint_4_invariantes_matriz_gates.md`, `docs/sprint_4_t0_checklist.md`, `out/scorecards/S4_T0_discovery.json`, `out/scorecards/S4_T1_specs.json` | `S4-A-T0-T1-modelo-invariantes` |
| A2 | A | T2 | `config/sources/sprint_4/fontes_p0/*.yaml`, `config/field_designer/sprint_4/*.yaml`, `out/evidence/S4_T2_sources/validation.log`, `out/scorecards/S4_T2_sources.json` | `S4-A-T2-registry-field-designer` |
| B1 | B | T3 | `fixtures/sprint_4/fontes_p0/<source_id>/*`, `tests/sprint_4/T3_*.spec.*`, `out/evidence/S4_T3_fixtures/report.txt`, `out/scorecards/S4_T3_fixtures.json` | `S4-B-T3-fixtures-tests` |
| B2 | B | T4 | `goldens/sprint_4/fontes_p0/<source_id>/*.json`, `out/evidence/S4_T4_goldens/report.txt`, `out/scorecards/S4_T4_goldens.json` | `S4-B-T4-goldens` |
| C1 | C | T5 | `out/evidence/S4_T5_repetition/vault_snapshot_before.json`, `.../vault_snapshot_after.json`, `.../vault_diff.txt`, `out/scorecards/S4_T5_repetition.json` | `S4-C-T5-vault-repetition` |
| D1 | D | T6 (métricas/logs) | `out/evidence/S4_T6_observability/metrics_snapshot.json`, `logs_sample.log`, `health_matrix.json`, `out/scorecards/S4_T6_observability.json` | `S4-D-T6-observabilidade` |
| D2 | D | T6 (experimentos SLO) | `out/evidence/S4_T6_observability/onboarding_experiments.json`, `detection_experiments.json`, `explore_queries_bench.json` | `S4-D-T6-experimentos-SLO` |
| E1 | E | T7 | entrypoint ORR S4 (script/workflow), `out/evidence/S4_T7_integration/orr_run.log`, `scorecards_index.json`, `out/scorecards/S4_T7_integration.json` | `S4-E-T7-orr-ci` |
| F1 | F | T8 | `out/scorecards/S4_T8_go_no_go.json`, `docs/sprint_4_orr_summary.md` | `S4-F-T8-wrap-go-no-go` |

Todos os PRs da Sprint 4 devem apontar para **um ID dessa tabela**.

---

## 4. Encadeamento temporal e prioridades entre trilhas

### 4.1 Ordem canônica (macro)

1. **Primeiro estabilizar Trilha A (T0/T1/T2)**  
   - Sem modelo + registry + Field Designer, ninguém mexe em fixtures, goldens ou observabilidade.  
   - **Regra:** nenhum PR marcado com `B*`, `C*`, `D*`, `E*`, `F*` é mergeado enquanto A1 (T0/T1) e A2 (T2) não tiverem scorecards PASS.

2. **Depois abrir Trilha B (T3/T4)**  
   - Com Fontes P0 definidas e configuradas, começamos a capturar fixtures reais e construir goldens.  
   - **Regra:** Trilha C (Vault) e D (Observabilidade) começam apenas quando B1 (T3) estiver funcional (mesmo que com fixtures iniciais).

3. **Na sequência, Trilha C (T5) e D (T6)**  
   - Trilha C prova robustez do Vault.  
   - Trilha D mede SLOs e saúde de fontes com dados vivos.  
   - **Regra:** não consolidar T7 enquanto T5 e T6 não estiverem em estado minimamente estável.

4. **Por fim, Trilha E (T7) e F (T8)**  
   - T7 monta a ORR S4 ponta a ponta.  
   - T8 consolida a decisão da sprint.  
   - **Regra:** T8 só é implementado ou ajustado após termos uma primeira execução bem-sucedida de T7.

### 4.2 Sugestão de ritmo semanal (exemplo)

- **Semana 1:**  
  - Foco total em A1, A2.  
  - Entregar T0/T1/T2 em PASS, com modelo de dados, invariantes, registry e Field Designer prontos.

- **Semana 2:**  
  - Abrir B1 (fixtures + testes) e B2 (goldens).  
  - Começar C1 (esqueleto de snapshot do Vault).  
  - Objetivo: T3 PASS e T4 parcialmente populado.

- **Semana 3:**  
  - Consolidar B2 (T4 PASS).  
  - Fechar C1 (T5 PASS).  
  - Abrir D1 (métricas/logs) e D2 (primeiros experimentos SLO).  
  - Começar integração de T7 (E1) em paralelo.

- **Semana 4:**  
  - Fechar D1/D2 (T6 PASS).  
  - Estabilizar E1 (T7 PASS).  
  - Rodar T8, escrever wrap, fechar F1.

(As semanas são ilustração: o importante é a **ordem de dependência**, não o calendário exato.)

---

## 5. Trilha A — Modelo & Registry & Field Designer (T0/T1/T2)

### 5.1 Objetivo

Dar base conceitual e de configuração para toda a sprint:

- Objetos (Fonte, Run, Item, Evidência, Consulta) **claros**.  
- Invariantes mapeados a gates e evidências.  
- Fontes P0 reais definidas e configuradas sem segredos.

### 5.2 Entregáveis

- `docs/sprint_4_modelo_dados_invariantes.md`  
- `docs/sprint_4_invariantes_matriz_gates.md`  
- `docs/sprint_4_t0_checklist.md`  
- `config/sources/sprint_4/fontes_p0/*.yaml`  
- `config/field_designer/sprint_4/*.yaml`  
- `out/scorecards/S4_T0_discovery.json`  
- `out/scorecards/S4_T1_specs.json`  
- `out/scorecards/S4_T2_sources.json`

### 5.3 Ligações formais

- **Gates:** T0, T1, T2.  
- **Invariantes:** rastreabilidade de evidência, nenhum ajuste estrutural apenas em código.  
- **SLOs:** base para onboarding_p50_min (definição, complexidade das Fontes P0).

### 5.4 Critérios de aceite (PO)

- Modelo de dados sem ambiguidade, exemplos concretos.  
- 100% das invariantes mapeadas.  
- Fontes P0 válidas, sem segredos, com Field Designer coerente.  
- T0/T1/T2 em PASS.

---

## 6. Trilha B — Fixtures reais & Goldens (T3/T4)

### 6.1 Objetivo

Mostrar que o Inspectah realmente **entende** dados reais das Fontes P0 e que o comportamento é reprodutível.

### 6.2 Entregáveis

- Fixtures reais por fonte: `fixtures/sprint_4/fontes_p0/<source_id>/*`.  
- Testes de parsing/normalização: `tests/sprint_4/T3_*.spec.*`.  
- Goldens: `goldens/sprint_4/fontes_p0/<source_id>/*.json`.  
- Relatórios e scorecards:  
  - `out/evidence/S4_T3_fixtures/report.txt`, `out/scorecards/S4_T3_fixtures.json`.  
  - `out/evidence/S4_T4_goldens/report.txt`, `out/scorecards/S4_T4_goldens.json`.

### 6.3 Ligações formais

- **Gates:** T3, T4.  
- **Invariantes:** “Nenhum Item P0 sem Evidência completa”; “Fixtures do ORR vêm de dados reais e são versionadas”.  
- **SLOs:** evidence_completeness_rate.

### 6.4 Critérios de aceite

- Cada Fonte P0 com fixtures representativas (normal + edge cases).  
- Testes T3 todos em PASS.  
- Goldens estáveis; mudanças registradas em T4.  
- T3/T4 em PASS.

---

## 7. Trilha C — Vault & Repetição (T5)

### 7.1 Objetivo

Garantir que o Vault funciona como um **repositório sólido de verdade**, sem se corromper sob repetição.

### 7.2 Entregáveis

- Snapshot antes/depois do Vault:  
  - `out/evidence/S4_T5_repetition/vault_snapshot_before.json`  
  - `out/evidence/S4_T5_repetition/vault_snapshot_after.json`  
- Diff: `out/evidence/S4_T5_repetition/vault_diff.txt`.  
- Scorecard: `out/scorecards/S4_T5_repetition.json`.

### 7.3 Ligações formais

- **Gate:** T5.  
- **Invariantes:** nenhum Item P0 sem Evidência; ausência de perdas/duplicações.  
- **SLOs:** impacta stability da evidence_completeness_rate sob repetição.

### 7.4 Critérios de aceite

- N execuções repetidas sem perdas nem duplicações injustificadas.  
- T5 em PASS, com diff claro e auditável.

---

## 8. Trilha D — Observabilidade & SLOs (T6)

### 8.1 Objetivo

Tornar a saúde das Fontes P0 **visível e mensurável**, incluindo experimentos SLO com arquivos e timing explícitos.

### 8.2 Entregáveis

1. **Matriz de saúde por Fonte P0**  
   - `out/evidence/S4_T6_observability/health_matrix.json`.

2. **Snapshot de métricas e logs**  
   - `metrics_snapshot.json`, `logs_sample.log` em `out/evidence/S4_T6_observability/`.

3. **Experimentos SLO documentados**  
   - `onboarding_experiments.json` — usados na **Semana 3**, medindo onboarding_p50_min.  
   - `detection_experiments.json` — Semana 3/4, medindo detection_latency_p95_min.  
   - `explore_queries_bench.json` — Semana 3/4, medindo explore_query_p95_ms (consultas típicas).  
   - Todos em `out/evidence/S4_T6_observability/`.

4. **Scorecard T6**  
   - `out/scorecards/S4_T6_observability.json`.

### 8.3 Ligações formais

- **Gate:** T6.  
- **Invariantes:** nenhuma Fonte P0 ativa invisível; quebras detectadas em tempo finito.  
- **SLOs diretamente ligados:**  
  - onboarding_p50_min;  
  - detection_latency_p95_min;  
  - run_success_rate;  
  - explore_query_p95_ms (parte observável).

### 8.4 Critérios de aceite

- health_matrix cobre 100% das Fontes P0, com estados coerentes.  
- Experimentos SLO executados e registrados nos arquivos indicados.  
- T6 em PASS.

---

## 9. Trilha E — ORR / CI S4 (T7)

### 9.1 Objetivo

Ter um **entrypoint único** para rodar T0–T6 e consolidar scorecards, local e em CI.

### 9.2 Entregáveis

- Entrypoint ORR S4 (script/workflow).  
- `out/evidence/S4_T7_integration/orr_run.log`.  
- `out/evidence/S4_T7_integration/scorecards_index.json`.  
- `out/scorecards/S4_T7_integration.json`.

### 9.3 Ligações formais

- **Gate:** T7.  
- **Invariantes:** todos (garante integração).  
- **SLOs:** reusa dados de T3–T6; serve de base para T8.

### 9.4 Critérios de aceite

- Uma execução do entrypoint gera todos os scorecards e evidências esperados.  
- Duas execuções consecutivas produzem resultados consistentes.  
- T7 em PASS.

---

## 10. Trilha F — Wrap & T8 (GO/NO_GO)

### 10.1 Objetivo

Fechar a Sprint 4 com decisão clara, rastreável e documentada.

### 10.2 Entregáveis

- `out/scorecards/S4_T8_go_no_go.json`.  
- `docs/sprint_4_orr_summary.md` (wrap humano completo).

### 10.3 Ligações formais

- **Gate:** T8.  
- **Invariantes/SLOs:** todos.  
- Respeita curto‑circuito do Capítulo 2.

### 10.4 Critérios de aceite

- T8 decide GO/NO_GO obedecendo regras do Capítulo 2.  
- Wrap humano consistente com scorecards e SLOs.  
- Sprint 4 se torna auditável apenas olhando arquivos.

---

## 11. Estratégia de PRs (modo guerra)

### 11.1 Regra de ouro

Nenhum PR é “geral”. Todo PR deve:

- Apontar para **um ID da tabela** (A1, A2, B1, …).  
- Declarar explicitamente gate(s) alvo e artefatos tocados.  
- Rodar localmente a parte relevante da ORR antes do push.

### 11.2 Checklist de PR

Antes de marcar como pronto:

1. **Gate(s) alvo descritos no título/descrição.**  
2. **Artefatos listados** (docs, configs, fixtures, goldens, evidências, scorecards).  
3. **Comando(s) rodados** (ex.: “rodei ORR S4 T3/T4 localmente, todos PASS”).  
4. **Impacto em invariantes/SLOs explicado** em 2–3 linhas.  
5. **Respeito aos contratos anti‑gambiarra** (Capítulo 2): sem despromover fonte, sem alterar fixture/golden sem motivo, sem afrouxar SLO em silêncio.

---

## 12. Riscos de execução e defesas (refinados)

1. **Risco:** sprint virar “fábrica de código” e não de artefatos de validação.  
   **Defesa:** PO só aceita entregas que resultem em arquivos indicados neste capítulo + scorecards/gates verdes.

2. **Risco:** trilhas abrirem fora de ordem, gerando retrabalho.  
   **Defesa:** respeitar ordem macro do item 4; bloquear merges de PRs de trilhas posteriores enquanto gates base não estiverem PASS.

3. **Risco:** SLOs virarem enfeite (sem experimento real).  
   **Defesa:** exigir os arquivos `onboarding_experiments.json`, `detection_experiments.json`, `explore_queries_bench.json` como pré‑requisito para T6 PASS.

4. **Risco:** evidências espalhadas fora de `out/evidence` e `out/scorecards`.  
   **Defesa:** revisão de PR travando qualquer evidência fora desses caminhos canônicos (salvo justificativa forte e update deste capítulo).

---

## 13. Fechamento do Capítulo 3 (versão 10/10)

Com este upgrade, o Capítulo 3 deixa de ser apenas um texto descritivo e vira um **quadro operacional**:

- O quadro mestre Trilha × Gate × Artefatos × Tags de PR guia o dia a dia.  
- A ordem entre trilhas evita retrabalho e garante respeito às dependências.  
- Os experimentos SLO têm arquivos, timing e vínculos claros com T6/T8.  
- O Codex sabe exatamente como fatiar PRs e quais artefatos entregar.  
- O PO sabe onde cobrar, e o comitê sabe como auditar.

Capítulos 1, 2 e 3, juntos, são o **manual supremo** da Sprint 4 do Inspectah: visão, validação e execução alinhadas, sem espaços para improviso irresponsável.

