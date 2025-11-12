# Inspectah — Sprint Playbook • Bloco 4 (Plano de Execução D1→D7)

> Propósito: transformar os Blocos 1–3 (LOCK) em **execução diária** até o entregável “Inspectah v0.1 funcionando”. Este documento é **manual para o Codex**: descreve o que fazer, em que ordem, quais artefatos gerar e como provar (gates). Sem código; apenas instruções precisas.

## 0) Definição do entregável (o que é “funcionando”)
Para esta sprint, considera‑se **Inspectah v0.1 funcionando** quando:  
1) Serviços sobem localmente (localhost) e operam por 48h: **ingestor**, **api**, **evidence‑vault**, **ui‑min**.  
2) Usuário consegue: (a) **cadastrar uma fonte** (RSS e outra API JSON), (b) **definir campos** via Field Designer, (c) **ver itens** indexados no **Explore**, (d) **exportar CSV/JSON**, (e) **abrir o manifesto** de evidência de 1 item.  
3) **SLOs do Bloco 1** atingidos e **gates T2→T8** aprovados com scorecards `passed=true`.  
4) **One‑click demo** executa em ≤ 5 minutos e gera pacote de release (T8) com checksums válidos.

## 1) Convenções de trabalho
- Branch: `sprint/inspectah-v0_1`. PR‑first, squash merges.  
- Commits: `feat|fix|chore|docs(scope): mensagem`.  
- Scripts: POSIX‑bash; tooling mínimo (jq/sed/awk/grep/sha256sum|shasum/zip); Python 3 stdlib permitido.  
- Portas (sugestão, ajustável): api `:8080`, ui `:8081`, ingestor health `:8082`, metrics `:9464`.

## 2) D0 — Preflight (30–60min)
1) Gerar scaffold do **Bloco 3** (se ainda não gerado).  
2) Completar `docs/EVIDENCE_SCHEMA.json` com o schema do Bloco 1.  
3) Implementar `bin/orr_sanity.sh` conforme Bloco 3 §4 e executar.  
**Saídas**: `out/scorecards/T0_sanity.json (passed=true)`; PR `scaffold+sanity` mergeada.

## 3) D1 — Contratos, OpenAPI e Field Designer (núcleo)
**Objetivo**: travar contratos e entregar **Field Designer** mínimo pronto para testes unitários (T2).  
**Passos**:  
1) Preencher `contracts/api/*.openapi.yaml` (endpoints Bloco 1 §6).  
2) Preencher `contracts/data/item.schema.json` e `contracts/data/source.schema.yaml` (campos mínimos).  
3) Implementar **validador de JSONPath e transforms** (CLI simples em `scripts/`): aceita payload de exemplo e definição de fields, retorna campos tipados e erros; usado pelo dry‑run do Field Designer.  
4) Atualizar `docs/PLAYBOOKS.md` e `docs/SLOs.md` (versões finais).  
5) Preencher **fixtures unit** em `tests/fixtures/unit/*`.  
6) Implementar runners T2 stubs → **expandir** para validar schemas, dry‑run e erros (sem lógica de rede).  
**Gate**: rodar `bin/orr_t2.sh` até `passed=true`.  
**Saídas**: scorecard T2, MANIFEST T2, PR `feature/field-designer+contracts`.

## 4) D2 — API + Evidence Vault (MVP) e Explore (lista)
**Objetivo**: disponibilizar **API** com endpoints CRUD de fontes/fields/dry‑run, e **Evidence Vault** para manifest/payloads; **Explore** com listagem e filtros básicos (sem FTS ainda).  
**Passos**:  
1) Implementar **/sources (POST)**, **/sources/{id}/fields (POST)** com DbC (pré/pós).  
2) Implementar **/sources/validate (POST)** usando o validador de D1 (retorna erros/sucesso).  
3) Implementar **/explore (GET)** com paginação, filtros por fonte/tempo e retorno dos campos tipados.  
4) Implementar **Evidence Vault**: escrita de payload bruto, manifesto JSON conforme schema; cálculo de `fetched_payload_sha256` e `extracted_fields_sha256`.  
5) **UI‑min**: duas telas (“Fontes” e “Explore”) somente leitura + formulários funcionais (sem polimento).  
6) Atualizar testes unitários (T2) e preparar propriedades (T3).  
**Gate**: rodar `bin/orr_t2.sh` (verde) e `bin/orr_t3.sh` (inicia com propriedades simples de hashing/idempotência).  
**Saídas**: scorecards T2/T3 verdes, PR `feature/api+vault+explore`.

## 5) D3 — Ingestor (scheduler, idempotência, backpressure) + Reindex
**Objetivo**: colocar a ingestão para rodar e preencher `items`/`item_kv` com **idempotência**.  
**Passos**:  
1) Implementar **scheduler** por fonte (intervalos, rate‑limit, retries com jitter).  
2) Implementar **dedupe** por `(source_id, canonical_url, content_hash, extractor_version)`.  
3) Implementar **backpressure** (fila interna, métricas `queue_depth` e `queue_age_seconds`).  
4) Implementar **reindex incremental** ao alterar fields (D2).  
5) Completar propriedades T3 (idempotência, ordem temporal, backpressure).  
**Gate**: `bin/orr_t3.sh` verde.  
**Saídas**: scorecard T3, PR `feature/ingestor-core`.

## 6) D4 — Goldens + Explore (FTS) + Export
**Objetivo**: travar **reprodutibilidade** com goldens e entregar FTS e export.  
**Passos**:  
1) Preencher `tests/fixtures/goldens/rss/*` e `api/*` (2 itens cada conjunto).  
2) Implementar **comparadores** e normalização canônica (ordem estável; remoção de ruído).  
3) Implementar **FTS** (no mínimo em título/excerpt) e **/explore/export (POST)** produzindo CSV/JSON.  
4) Validar 100% dos manifests contra `docs/EVIDENCE_SCHEMA.json`.  
**Gate**: `bin/orr_t4.sh` verde.  
**Saídas**: scorecard T4, PR `feature/goldens+fts+export`.

## 7) D5 — Bench de Performance + Probe E2E
**Objetivo**: medir SLOs e coletar séries.  
**Passos**:  
1) Implementar `scripts/bench_generate_50k.sh` (dataset sintético).  
2) Criar **probe E2E** (1/min) para medir p95 e queue age.  
3) Executar bench e registrar `summary.json`, `series_explore.json`, `series_ingest.json`.  
**Gate**: `bin/orr_t5.sh` verde (p95 ≤ 200 ms; p99 ≤ 400 ms; sem perdas; queue_age≤600).  
**Saídas**: scorecard T5, PR `feature/bench+probe`.

## 8) D6 — Observabilidade + CI/GitHub (parcial T7)
**Objetivo**: dashboards/alertas e CI executando T2–T6.  
**Passos**:  
1) Expor **métricas** listadas no Bloco 1/2; preencher `configs/grafana/dashboards/*.json`.  
2) Configurar **alertas** mínimos (detecção p95>2m/15m; queue_age>10m; error_rate>1%/5m; disco<15%).  
3) Ajustar pipelines em `.github/workflows/` para rodar `bin/orr_t2..t6.sh` e publicar artefatos.  
4) Verificador de **ToS/robots** em CI (hashes em `docs/LEGAL_TOS_ALLOWLIST.md`).  
**Gates**: `bin/orr_t6.sh` verde; `bin/orr_t7.sh` parcial verde.  
**Saídas**: scorecards T6/T7, PR `feature/obs+ci`.

## 9) D7 — ORR Final (48h) + Release + One‑click demo
**Objetivo**: consolidar operação, gerar bundle e executar demo.  
**Passos**:  
1) Rodar **48h** com ≥ 10 fontes ativas; probe E2E ativo.  
2) Gerar `out/release/inspectah_v0_1_release.zip` e `CHECKSUMS.sha256`.  
3) Executar `scripts/bootstrap.sh` (**one‑click demo**): criar 3 fontes, definir fields, iniciar ingest, executar 3 buscas no Explore e exportar CSV/JSON.  
4) Gravar **screenshots** de dashboards e incluir no bundle.  
**Gate**: `bin/orr_t8.sh` verde; `out/scorecards/T8_final.json` com `passed=true`.  
**Saídas**: scorecard T8, pacote de release, PR `release/v0_1`.

## 10) Roteiro de verificação (resumo por gate)
- **T2**: unit + DbC + validation contra schemas + dry‑run Field Designer.  
- **T3**: propriedades (idempotência, determinismo, ordering, backpressure, reindex).  
- **T4**: goldens RSS/API, manifests 100%.  
- **T5**: p95/p99 Explore; ingest sem perda; fila sob controle.  
- **T6**: métricas/dashboards/alertas exportados (JSON+PNG).  
- **T7**: CI executando T2–T6; verificador ToS/robots.  
- **T8**: 48h estáveis + bundle e checksums.

## 11) Hand‑off explícito (para o Codex)
Executar, nesta ordem: `D0 → D1 → … → D7`. A cada dia:  
1) Abrir PR com o nome do dia.  
2) Rodar `bin/orr_t{N}.sh` do gate correspondente.  
3) Coletar scorecards/ evidências.  
4) Se `passed=false`, **stop‑the‑line** e corrigir antes de seguir.

## 12) Critérios de aceite do Bloco 4 (Lock)
- Todos os dias **D0–D7** concluídos em PRs separados com artefatos completos.  
- `bin/orr_all.sh` roda **de ponta a ponta** com `--fail-fast` e gera `FINAL_ORR.json` consolidado.  
- “One‑click demo” executa em ≤ 5 min (log incluído no bundle) e reproduz os passos básicos do usuário final (Add Source → Fields → Ingest → Explore → Export → Manifest).

## 13) Revisão do comitê (pré‑lock)
- **Jobs**: sequência operacional clara e centrada no usuário; demo em 5 min — OK.  
- **Lamport**: gates como gargalo efetivo, determinismo e stop‑the‑line — OK.  
- **Meyer**: DbC nos endpoints e runners; PR‑first e contratos travados — OK.  
- **Pérez**: bench/probe/artefatos em JSON com seeds — OK.  
- **Buterin**: bridges fora (flag), contrato pronto para plug — OK.

