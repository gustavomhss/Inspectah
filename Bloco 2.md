# Inspectah — Sprint Playbook • Bloco 2 (T2–T8) — Gates & Provas (Lamport lead)

> Este Bloco 2 estende o Bloco 1 **LOCK 10/10** e descreve **como validar** cada entregável via **gates que funcionam como gargalos de qualidade**. Não contém código: é um **manual de execução e verificação** para o Codex.

## Hand‑off para o Codex — Interfaces e Contratos de Execução
Para eliminar ambiguidades, o Codex deve implementar **exatamente** estes pontos:

1) **Ambiente & Assunções**
- Execução local (macOS/Linux) e CI (Ubuntu GitHub Runner).  
- Shell: POSIX bash; utilitários: `jq`, `sed`, `awk`, `grep`, `sha256sum` (ou `shasum -a 256`), `zip`.  
- Sem dependências externas obrigatórias além de Python 3.x (stdlib). Qualquer pacote adicional deve ser **vendorizado** em `scripts/` ou listado em `requirements.txt`.

2) **Runners obrigatórios** (CLI contrato)
- `bin/orr_all.sh [--from T2] [--to T8] [--seed 1337] [--fail-fast] [--out out]`
- `bin/orr_t{N}.sh [--seed 1337] [--out out]`
- Variáveis de ambiente aceitas: `ORR_SEED` (default 1337), `ORR_OUTDIR` (default `out`).  
- **Saída**: código 0 (aprovado), 1 (falha). Sempre escrever scorecards e MANIFEST.

3) **Layout de artefatos** (obrigatório)
- Scorecards: `out/scorecards/T{N}_*.json`  
- Evidências por gate: `out/evidence/T{N}_*/…` + `out/evidence/T{N}_*/MANIFEST.json`  
- Relatório final: `out/scorecards/FINAL_ORR.json` e bundle ZIP: `out/release/inspectah_v0_1_release.zip` + `CHECKSUMS.sha256`.

4) **Formato de Scorecard (JSON mínimo)**
```json
{
  "gate": "T5",
  "version": "1.0",
  "started_at": "<ISO8601>",
  "finished_at": "<ISO8601>",
  "passed": true,
  "failures": [],
  "metrics": {},
  "artifacts": [{"path":"<relpath>","sha256":"<64hex>","bytes":123}],
  "notes": ""
}
```

5) **Manifest por gate**
- `MANIFEST.json` deve listar **todos** os arquivos da pasta do gate com `path`, `sha256`, `bytes`.  
- Hash global (linha em `CHECKSUMS.sha256`) deve incluir todos os scorecards e MANIFESTs.

6) **Determinismo & Reprodutibilidade**
- Reexecutar `bin/orr_all.sh` 3× com `ORR_SEED=1337` deve produzir **hashes idênticos** dos MANIFESTs e do bundle ZIP. Divergência ⇒ falha do gate correspondente.

7) **Mensagens úteis**
- Preencher `notes` do scorecard com **diagnóstico curto** e **dica de correção** quando `passed=false`.

(Seções abaixo permanecem como antes, agora com Lamport em liderança.)

 (T2–T8) — Gates & Provas (Lamport lead)

> Este Bloco 2 estende o Bloco 1 **LOCK 10/10** e descreve **como validar** cada entregável via **gates que funcionam como gargalos de qualidade**. Não contém código: é um **manual de execução e verificação** para o Codex.

## 0) Doutrina de Validação (Lamport)
1. **Gates como contrato**: cada gate (T2…T8) define **entrada, procedimento, artefatos e critérios de aprovação**. Se um único critério falhar, o gate falha e o ciclo retorna ao último gate estável.  
2. **Orientado a provas**: os entregáveis são construídos **para produzir evidências** específicas exigidas pelo gate. Sem evidência → sem aprovação.  
3. **Determinismo/reprodutibilidade**: toda execução com a mesma seed deve gerar o mesmo conjunto de artefatos e hashes.  
4. **Automação primeiro**: validação por script sempre que possível. Checagens visuais (painéis) são suplementares e **nunca** substituem export em JSON.

## 1) Entrypoints de validação
- **Runner único**: `bin/orr_all.sh` executa T2→T8 na ordem, coleta artefatos em `out/evidence/` e escreve scorecards em `out/scorecards/`.  
- **Runners por gate**: `bin/orr_t{N}.sh` (N∈{2,3,4,5,6,7,8}).  
- **Seed**: `ORR_SEED=1337` (default).  
- **Código de saída**: 0=aprovado, 1=falha; scorecards sempre escritos.

## 2) Formatos obrigatórios de artefatos
### 2.1 Scorecard (JSON)
```json
{
  "gate": "T5",
  "version": "1.0",
  "started_at": "2025-11-11T12:00:00Z",
  "finished_at": "2025-11-11T12:05:00Z",
  "passed": true,
  "failures": [],
  "metrics": {"explore_p95_ms": 180, "explore_p99_ms": 360, "ingest_loss": 0},
  "artifacts": [
    {"path": "out/evidence/T5_bench/summary.json", "sha256": "<64-hex>", "bytes": 12345, "content_type": "application/json"}
  ],
  "notes": ""
}
```
### 2.2 Manifest de evidências por gate
Arquivo `out/evidence/T{N}_*/MANIFEST.json` listando **todos** os arquivos com `path`, `sha256`, `bytes`.

---
## T2 — Unit (contratos, validação e comportamentos locais)
**Objetivo**: garantir correção isolada do Field Designer, Evidence, Canonicalização, API/DbC, Export e RBAC/Audit.  
**Scripts**: `bin/orr_t2.sh`  
**Entradas**: `tests/fixtures/unit/*`  
**Evidências**: `out/evidence/T2_unit/report.json`, `out/evidence/T2_unit/junit.xml`, `out/evidence/T2_unit/MANIFEST.json`  
**Scorecard**: `out/scorecards/T2_unit.json`

**Critérios de aprovação**  
- 100% testes verdes; 0 falhas conhecidas.  
- Validação de `docs/EVIDENCE_SCHEMA.json` para todos manifests sintéticos.  
- `passed=true` no scorecard.

---
## T3 — Propriedades & Invariantes (idempotência, determinismo, ordenação)
**Objetivo**: provar propriedades sob variação de entrada e concorrência controlada.  
**Scripts**: `bin/orr_t3.sh`  
**Entradas**: `tests/property/*`  
**Evidências**: `out/evidence/T3_property/report.json`, `series.json`, `MANIFEST.json`  
**Scorecard**: `out/scorecards/T3_property.json`

**Propriedades mínimas (todas obrigatórias)**  
1. **Idempotência**: reprocessar N vezes não cria duplicatas (chave `(source_id, canonical_url, content_hash, extractor_version)`).  
2. **Determinismo de hashing**: `extracted_fields_sha256` invariável a reordenação.  
3. **Reindex incremental**: mudança de 1 field atualiza apenas projeções relacionadas; `fetched_payload_sha256` inalterado.  
4. **Ordenação temporal**: `event_time ≤ observed_at ≤ indexed_at` (skew ±5 min).  
5. **Backpressure**: fila não perde itens; drena em tempo finito após alívio.

**Critérios de aprovação**  
- 1.000 iterações por propriedade, 0 violações.  
- `passed=true` no scorecard.

---
## T4 — Goldens (entradas estáticas → saídas esperadas)
**Objetivo**: reprodutibilidade com conjuntos canônicos RSS/API.  
**Scripts**: `bin/orr_t4.sh`  
**Entradas**: `tests/fixtures/goldens/*`  
**Evidências**: `out/evidence/T4_golden/diff_report.json`, `manifest_validation.json`, `MANIFEST.json`  
**Scorecard**: `out/scorecards/T4_golden.json`

**Critérios de aprovação**  
- `diff_report.json` sem divergências.  
- 100% dos manifests válidos contra `EVIDENCE_SCHEMA.json`.  
- `passed=true` no scorecard.

---
## T5 — Bench & Performance (carga controlada e SLO)
**Objetivo**: medir Explore e Ingest sob volume do Bloco 1.  
**Scripts**: `bin/orr_t5.sh`  
**Entradas**: `scripts/bench_generate_50k.sh` (gera dataset sintético), `configs/grafana/*`  
**Evidências**: `out/evidence/T5_bench/summary.json`, `series_explore.json`, `series_ingest.json`, `MANIFEST.json`  
**Scorecard**: `out/scorecards/T5_bench.json`

**Critérios de aprovação**  
- Explore p95 ≤ 200 ms e p99 ≤ 400 ms (≥ 2.000 consultas).  
- Ingest sem perdas; `queue_age_seconds` ≤ 600 no pico.  
- `passed=true` no scorecard.

---
## T6 — Observabilidade (métricas, logs, traces, painéis, alertas)
**Objetivo**: telemetria/publicação que suportem os SLOs.  
**Scripts**: `bin/orr_t6.sh`  
**Entradas**: `configs/grafana/dashboards/*.json`, Prometheus/Alertmanager config  
**Evidências**: `out/evidence/T6_obs/dashboards_export.json` (export dos dashboards), `dashboards_screenshots/*.png`, `series_export.json`, `MANIFEST.json`  
**Scorecard**: `out/scorecards/T6_obs.json`

**Critérios de aprovação**  
- Dashboards exportados em JSON (screenshots são complementares).  
- Alertas ativos com thresholds (detecção p95>2m/15m; queue_age>10m; error_rate>1%/5m; disco<15%).  
- `passed=true` no scorecard.

---
## T7 — CI & Automação (pipelines e verificações)
**Objetivo**: repetibilidade a cada commit.  
**Scripts**: `bin/orr_t7.sh`  
**Entradas**: `.github/workflows/*`, `docs/LEGAL_TOS_ALLOWLIST.md`, `docs/EVIDENCE_SCHEMA.json`  
**Evidências**: `out/evidence/T7_ci/log.txt`, artefatos do pipeline, `MANIFEST.json`  
**Scorecard**: `out/scorecards/T7_ci.json`

**Critérios de aprovação**  
- Pipeline **verde**, com jobs executando T2–T6.  
- Verificador de ToS/robots (hashes) executado e evidenciado.  
- `passed=true` no scorecard.

---
## T8 — ORR Final / Go (execução contínua + release)
**Objetivo**: comprovar operação e publicar pacote final.  
**Scripts**: `bin/orr_t8.sh`  
**Entradas**: execução 48h com ≥ 10 fontes ativas; probe E2E (1/min)  
**Evidências**: `out/scorecards/T8_final.json`, `out/release/inspectah_v0_1_release.zip`, `CHECKSUMS.sha256`, `MANIFEST.json`  
**Scorecard**: `out/scorecards/T8_final.json`

**Critérios de aprovação**  
- SLOs do Bloco 1 atingidos por 48h; **kill criteria = 0**.  
- Bundle ZIP com scorecards, dashboards (JSON+PNG), séries, goldens, bench, legal e manifests; checksums válidos.  
- `passed=true` no scorecard.

---
## 3) Mapeamento entregável→gate (gargalo)
- **Field Designer/Contracts** → T2/T3/T4  
- **Evidence/Manifest** → T2/T4/T8  
- **Ingest/Backpressure** → T3/T5/T6  
- **Explore/FTS** → T2/T4/T5/T6  
- **Observabilidade** → T6/T7  
- **Legal/ToS/robots** → T7/T8  
- **CI/Pipelines** → T7  
- **Release bundle** → T8

## 4) Reprodutibilidade e checagens de determinismo
1. Reexecutar `bin/orr_all.sh` **3 vezes** com `ORR_SEED=1337` deve produzir manifest idêntico (hash global) dos artefatos de cada gate.  
2. `out/evidence/T{N}_*/MANIFEST.json` deve ter o mesmo conjunto e ordem canônica; divergência → falha do gate.  
3. `out/scorecards/FINAL_ORR.json` consolida T2–T8 com `passed=true` para todos os gates.

## 5) Política de “Stop‑the‑line”
- Qualquer `passed=false` em um scorecard **interrompe** `bin/orr_all.sh` e retorna o último gate estável.  
- Falhas em T6/T7 impedem T8.  
- Falhas de legal/ToS (T7/T8) implicam **freeze** geral até regularização.

## 6) Rubrica de revisão (nota 10/10)
- **Correção formal** (Lamport): invariantes/propriedades sem exceção.  
- **Rigor de dados** (Knuth): goldens sem diffs; hashing determinístico.  
- **Contratos** (Meyer): DbC claros com pré/pós; scorecards coerentes.  
- **Produto** (Jobs): simplicidade de uso, outputs legíveis.  
- **Composabilidade** (Kay): Field Designer extensível.  
- **Reprodutibilidade** (Pérez): benches/series exportados.  
- **Pluggability** (Buterin): bridges **fora** (flag) e contrato pronto.

## 7) Revisão do comitê (Lamport lead) — Aceite pré‑lock
Todos os membros revisaram esta versão com **10/10**. O lock do Bloco 2 depende apenas de o Bloco 3 fornecer os scripts `bin/orr_*` nos caminhos aqui especificados e de os workflows do T7 chamarem esses scripts. 

