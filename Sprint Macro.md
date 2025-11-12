# Sprint Inspectah v0.1 — 10/10 (Data Hub First++)

## 1) Objetivo e resultado
Entregar o **Inspectah v0.1** pronto para uso interno com nota 10/10 no ORR: cadastro de fontes (RSS e APIs JSON), **Field Designer** completo com transforms, **Explore** rápido (FTS+filtros), **Evidence Vault** com contrato rígido e **JSON Schema**, SLOs com **error budget** e playbooks operacionais, observabilidade rica, backup/restore verificados, legal/ToS automatizado em CI, **fonte sintética + probe** contínuos, **chaos drill** com RTO/RPO e **one‑click demo** de 5 minutos. HTML/snapshots/IPFS e bridges ficam atrás de flags.

## 2) Escopo (DoR→DoD)
**Incluído**
1. Cadastro/edição de fontes (RSS e API JSON) com allowlist, scheduler, rate‑limit, retries/backoff com jitter, auth opcional.
2. **Field Designer**: tipos (string, number, integer, boolean, timestamp, enum, array), mapeamento via JSONPath, transforms (trim, lower/upper, parse_float, parse_int, parse_date, coalesce, regex_extract, split/join, to_enum), validação por tipo/padrão, **dry‑run** por campo e por amostra, versão do extrator.
3. Ingest determinístico: idempotência por `(source_id, canonical_url, content_hash, extractor_version)`; **reindex incremental** quando fields mudarem.
4. Modelo de dados: `sources`, `runs`, `items`, `item_kv`, `manifests`, `audit_log`. **FTS** em título/excerpt/kv selecionados; índices GIN/TSV e B‑tree.
5. **Explore**: filtros por fonte, intervalo, campos tipados, busca FTS, paginação; **export CSV/JSON**.
6. **Evidence Vault**: payloads originais, manifest por item com **JSON Schema**; hashes SHA‑256 e carimbos de tempo múltiplos.
7. Observabilidade (OTel): métricas, logs estruturados, traces por item; dashboards e alertas.
8. Segurança/Legal: RBAC básico; cofre de segredos; DLP guard; **ToS/robots verificados em CI** com hash e evidência.
9. Backup e Restore testados; runbooks para onboarding, incidentes e takedown.
10. **Fonte sintética** para bench (50k itens) e **probe E2E** contínuo para SLOs.
11. **Chaos drill** com falhas de DB/fila; RTO/RPO documentados e evidenciados.
12. **One‑click demo** (bootstrap) criando 3 fontes, executando ingest, explore e export.

**Excluído (atrás de flags)**: extrator HTML (CSS/XPath), screenshots/snapshots, IPFS, bridges (UMA/Reality/MBP), UI pública/billing/KYC.

## 3) Arquitetura e componentes
- **ingestor**: workers por fonte, fila interna com backpressure, circuit breaker, política de shedding; concorrência por fonte e limite global.
- **api**: CRUD de fontes/fields, validação/dry‑run, Explore e export; RBAC; audit‑log; DbC (pré/pós‑condições) em cada endpoint.
- **evidence‑vault**: IO, hashing, versionamento; verificador de integridade.
- **ui‑min**: duas telas (Fontes e Explore) com foco em onboarding ≤ 5 min e consultas ≤ 200 ms p95.

## 4) Modelo de dados (resumo)
- `sources(id, name, domain_allowlist, kind, poll_cron, rate_limit, auth, robots_policy_hash, extractor_version, flags, created_at, updated_at)`
- `runs(id, source_id, started_at, ended_at, status, fetched, indexed, errors, queue_depth_max, notes)`
- `items(id, source_id, canonical_url, title, excerpt, event_time, observed_at, indexed_at, content_hash, extractor_version, payload_ref)`
- `item_kv(item_id, key, type, value_*, created_at)` com índices por `(key,type)` e FTS opcional por chaves selecionadas
- `manifests(item_id, manifest_json, manifest_sha256, created_at)`
- `audit_log(id, actor, action, entity, entity_id, diff_json, created_at)`

## 5) Canonicalização e tempos
- **canonical_url**: normalizar scheme/host, limpar tracking, ordenar query; suportar `etag/last‑modified`.
- Três timestamps: `event_time` (da fonte), `observed_at` (coleta), `indexed_at` (persistência). Regras para reordenação e tolerância de **clock‑skew ±5 min**.

## 6) Evidence Manifest — contrato e JSON Schema
Contrato mínimo por item: `item_id`, `source_id`, `canonical_url`, `event_time`, `observed_at`, `indexed_at`, `timezone`, `extractor_version`, `user_agent`, `allowlist_proof_ref`, `fetched_payload_sha256`, `extracted_fields_sha256`, `fields` (objeto tipado), `hashes` (objeto com algoritmos), `signatures` (opcional v0.1), `integrity_checked_at`.

**JSON Schema (versão 1.0)**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://inspectah.local/schemas/evidence_manifest_v1.json",
  "title": "Evidence Manifest",
  "type": "object",
  "required": [
    "item_id","source_id","canonical_url","event_time","observed_at","indexed_at",
    "timezone","extractor_version","user_agent","allowlist_proof_ref",
    "fetched_payload_sha256","extracted_fields_sha256","fields","hashes"
  ],
  "properties": {
    "item_id": {"type":"string"},
    "source_id": {"type":"string"},
    "canonical_url": {"type":"string","format":"uri"},
    "event_time": {"type":"string","format":"date-time"},
    "observed_at": {"type":"string","format":"date-time"},
    "indexed_at": {"type":"string","format":"date-time"},
    "timezone": {"type":"string","pattern":"^[A-Za-z_]+\/[A-Za-z_]+$"},
    "extractor_version": {"type":"string"},
    "user_agent": {"type":"string"},
    "allowlist_proof_ref": {"type":"string"},
    "fetched_payload_sha256": {"type":"string","pattern":"^[a-f0-9]{64}$"},
    "extracted_fields_sha256": {"type":"string","pattern":"^[a-f0-9]{64}$"},
    "fields": {"type":"object","additionalProperties": true},
    "hashes": {
      "type":"object",
      "properties": {
        "payload_sha256": {"type":"string","pattern":"^[a-f0-9]{64}$"},
        "manifest_sha256": {"type":"string","pattern":"^[a-f0-9]{64}$"}
      },
      "required":["payload_sha256","manifest_sha256"]
    },
    "signatures": {
      "type":"array",
      "items": {"type":"string"}
    },
    "integrity_checked_at": {"type":"string","format":"date-time"}
  }
}
```

## 7) DbC — contratos dos endpoints (exemplos)
- **POST /sources**
  - Pré: `domain_allowlist` não vazio; ToS/robots verificados e `robots_policy_hash` presente.
  - Pós: `source_id` criado; auditoria registrada; primeiro `run` agendado ≤ 60 s.
- **POST /sources/{id}/fields**
  - Pré: tipos válidos; JSONPath válido; transforms verificadas; dry‑run ≥ 1 amostra aprovada.
  - Pós: `extractor_version` incrementado; reindex incremental agendado.
- **GET /explore**
  - Pré: filtros válidos; limites de paginação ≤ 200.
  - Pós: `query_latency_p95 ≤ 200 ms` nos painéis sob carga padrão.

## 8) SLOs, error budget e playbooks
- **Onboarding p50 ≤ 5 min**; **Detecção p95 ≤ 2 min**; **Explore p95 ≤ 200 ms / p99 ≤ 400 ms**; **Run success ≥ 99%/24h**; **Evidence completeness = 100%**.
- **Error budget** mensal = 0,1% do tempo (≈ 43,2 minutos/mês). Débito de SLO consome orçamento; ao zerar, congelar mudanças.
- **Playbooks** (gatilhos → ações):
  - Detecção p95 > 2 min por 15 min → revisar fila, elevar consumidores da fonte afetada, checar backpressure e rate‑limit; se persistir 30 min → congelar novas fontes.
  - Explore p99 > 400 ms por 10 min → revisar índices/planos, limitar FTS pesado, criar projeções quentes.
  - Error rate > 1%/5 min → abrir incidente, isolar fonte ruidosa, aplicar retry com jitter, revisar auth.
  - Disk evidence < 15% → arquivar/expandir volume; alerta crítico a 10%.

## 9) Métricas e alertas (mínimo)
- Ingest: `items_fetched_total`, `items_indexed_total`, `ingest_latency_seconds` (hist), `queue_depth`, `queue_age_seconds`, `errors_total{type}`.
- Explore: `query_latency_seconds` (hist), `result_count`, `timeouts_total`.
- Infra: `db_connections_in_use`, `disk_free_bytes` (evidence), `cpu_percent` workers.
- Alertas: detecção p95>2m (15 min), queue_age>10m, error_rate>1%/5m, disk_free<15%.

## 10) Legal/ToS/robots e DLP
- **Allowlist por domínio** com **hash do ToS** e captura da data; parser `robots.txt` (crawl‑delay/disallow) respeitado; **RUNBOOK_TAKEDOWN** e botão **Freeze Source**.
- **DLP guard**: mascarar PII em logs; listas e regex para campos sensíveis; rotação de segredos trimestral.

## 11) Bench, fonte sintética e probe E2E
- **Gerador** de 50k itens JSON com distribuição de campos; script de bench salvando relatório em `out/evidence/T5_bench/`.
- **Probe E2E**: fonte pequena de pulso (1/min) para medir p95 e `queue_age_seconds` continuamente; gráfico dedicado.

## 12) Chaos drill e RTO/RPO
- **Cenários**: queda do DB, pausa na fila, perda parcial de evidências.
- **Metas**: RTO ≤ 20 min; RPO ≤ 5 min.
- **Evidência**: logs de restauração, validação de hashes, screenshots dos painéis.

## 13) Runbooks
- **RUNBOOK_ONBOARDING**: passo a passo para criar fonte, definir fields, validar dry‑run e acompanhar primeiro run.
- **RUNBOOK_INCIDENT**: SLO breach, diagnóstico, rollback de extrator, ampliação de consumidores, congelamento de fontes.
- **RUNBOOK_RESTORE**: procedimentos, checagem de integridade, validação de manifest.
- **RUNBOOK_TAKEDOWN**: jurídico/técnico, registro de evidências, comunicação e freeze.

## 14) Filemap
```
/inspectah/
  docs/
    SPEC.md
    EVIDENCE_SCHEMA.json
    SLOs.md
    PLAYBOOKS.md
    LEGAL_TOS_ALLOWLIST.md
    RUNBOOK_ONBOARDING.md
    RUNBOOK_INCIDENT.md
    RUNBOOK_RESTORE.md
    RUNBOOK_TAKEDOWN.md
  services/
    api/
    ingestor/
    evidence_vault/
    ui_min/
  db/
    migrations/
    schema.sql
    seeds/
  configs/
    prometheus.dev.yml
    grafana/
      dashboards/ingest.json
      dashboards/explore.json
      dashboards/errors.json
    alertmanager/alerts.yml
  scripts/
    bootstrap.sh
    load_sample_sources.sh
    bench_generate_50k.sh
    probe_e2e.sh
    chaos_drill.sh
    backup.sh
    restore.sh
    smoke_ingest.sh
    smoke_explore.sh
  .github/workflows/
    inspectah-ci.yml
    inspectah-orr.yml
  out/
    evidence/
    scorecards/
```

## 15) Gates ORR (T0–T8) com pass criteria
- **T0**: SPEC completo; filemap fechado; 10–15 fontes listadas com ToS/robots evidenciados.
- **T1**: schema/índices aprovados; EVIDENCE_SCHEMA.json publicado; contratos DbC; RBAC e DLP definidos.
- **T2**: unit para JSONPath, transforms, validação, dry‑run, dedupe, RBAC, export.
- **T3**: invariantes — idempotência e evidence sempre presente; reindex incremental medido.
- **T4**: goldens RSS/API com expected (items, kv, manifest) e verificação de hashes.
- **T5**: bench 50k; Explore p95/p99 e ingest sob spike; relatório em `out/evidence/T5_bench/`.
- **T6**: métricas, logs, traces; dashboards/alertas de pé; prova de probe E2E.
- **T7**: CI verde; verificador de ToS/robots em CI; geração de `out/evidence/T*` e `out/scorecards/T*.json`.
- **T8**: 48h estáveis; pacote de release; decisão Go com RTO/RPO e one‑click demo gravados.

## 16) Cronograma (7 dias)
- **D1 – T0/T1**: SPEC, filemap, schema/índices, contratos DbC, EVIDENCE_SCHEMA.json, ToS/robots.
- **D2 – T2**: Field Designer + dry‑run; API de fontes/fields; auditoria; seeds/migrações.
- **D3 – T2/T3**: ingestor com fila/backpressure; dedupe; reindex incremental; invariantes; UI: Fontes.
- **D4 – T4**: goldens; Explore, FTS e filtros; export; UI: Explore.
- **D5 – T5**: bench 50k; ajustes de índices; probe E2E; relatórios.
- **D6 – T6/T7**: métricas/logs/traces; dashboards/alertas; CI completo; verificador ToS/robots; backup/restore; chaos drill.
- **D7 – T8**: 48h de ensaio; coleta final de evidências; pacote de release e decisão Go.

## 17) One‑click demo (5 min)
- `scripts/bootstrap.sh` cria DB, aplica migrações, sobe serviços, registra 3 fontes de exemplo, define fields, inicia ingest, executa 3 consultas no Explore e exporta CSV/JSON para `out/`.
- Saídas esperadas: itens indexados, manifests válidos, dashboards com tráfego, arquivos de export prontos.

## 18) Critérios de aceite
1. 10–15 fontes ativas, onboarding ≤ 5 min cada, com ToS/robots evidenciados.
2. Detecção p95 ≤ 2 min e Explore p95 ≤ 200 ms/p99 ≤ 400 ms (50k itens).
3. Evidence completeness 100% com **EVIDENCE_SCHEMA.json** validado; verificador de integridade verde.
4. Reindex incremental funcional em 3 fontes após mudança de field.
5. Dashboards/alertas publicados; probe E2E ativo; error budget monitorado.
6. Backup/restore e chaos drill com RTO ≤ 20 min e RPO ≤ 5 min, evidenciados.
7. CI verde com verificação automática de ToS/robots; `out/evidence/` e `out/scorecards/` completos.
8. One‑click demo executada e gravada; pacote de release aprovado no T8.

