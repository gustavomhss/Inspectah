# Inspectah — Sprint Playbook • Bloco 3 (Filemap/Scaffold) — (Jobs + Lamport + Meyer)

> Objetivo: especificar o **scaffold completo** do repositório para que o Codex gere, sem ambiguidade, toda a estrutura, arquivos mínimos e contratos necessários para cumprir o Bloco 1 e habilitar os **Gates & Provas** do Bloco 2.

## 0) Princípios do Scaffold
1) **Fidelidade 1:1** ao Filemap do Bloco 1 (§10).  
2) **Orientado a gates**: tudo que os runners do Bloco 2 esperam deve existir (paths, nomes, formatos).  
3) **Determinismo**: artefatos gerados têm caminhos e nomes imutáveis; scripts não imprimem ruído.  
4) **DbC básico**: arquivos essenciais possuem conteúdo mínimo válido (esquemas JSON/YAML válidos; markdowns com cabeçalhos).  
5) **Sem dependências opacas**: scripts POSIX‑bash + Python stdlib; utilitários: `jq`, `sed`, `awk`, `grep`, `sha256sum|shasum -a 256`, `zip`.

## 1) Estrutura do Repositório (árvore final)
```
/inspectah/
  README.md
  .gitignore
  .editorconfig
  .gitattributes
  Makefile
  bin/
    orr_all.sh
    orr_t2.sh
    orr_t3.sh
    orr_t4.sh
    orr_t5.sh
    orr_t6.sh
    orr_t7.sh
    orr_t8.sh
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
  contracts/
    api/
      explore.openapi.yaml
      sources.openapi.yaml
    data/
      item.schema.json
      source.schema.yaml
  services/
    api/README.md
    ingestor/README.md
    evidence_vault/README.md
    ui_min/README.md
  db/
    migrations/
    schema.sql
    seeds/
  tests/
    unit/
      field_designer_test.txt
      evidence_manifest_test.txt
      canonical_url_test.txt
      api_contracts_test.txt
      export_test.txt
      rbac_audit_test.txt
    property/
      ingest_idempotency_prop.txt
      hash_determinism_prop.txt
      reindex_incremental_prop.txt
      time_ordering_prop.txt
      backpressure_prop.txt
    fixtures/
      unit/sample_payloads/example.json
      unit/sample_fields/example.yaml
      unit/manifests/example.json
      goldens/rss/news_001/feed.xml
      goldens/rss/news_001/expected/items.jsonl
      goldens/rss/news_001/expected/item_kv.jsonl
      goldens/rss/news_001/expected/manifests/example.json
      goldens/api/store_001/input/sample.json
      goldens/api/store_001/expected/items.jsonl
      goldens/api/store_001/expected/item_kv.jsonl
      goldens/api/store_001/expected/manifests/example.json
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
  configs/
    prometheus.dev.yml
    grafana/
      dashboards/ingest.json
      dashboards/explore.json
      dashboards/errors.json
    alertmanager/alerts.yml
  .github/
    workflows/
      inspectah-ci.yml
      inspectah-orr.yml
  out/
    evidence/.keep
    scorecards/.keep
    release/.keep
```

## 2) Conteúdo mínimo (exato) dos arquivos essenciais
> O Codex deve criar **exatamente** estes conteúdos mínimos. São válidos, auto‑descritivos e habilitam os gates.

### 2.1 Raiz
**README.md**
```
# Inspectah — Data Hub First (v0.1)
Este repositório contém o Inspectah. Os contratos e SLOs estão em `docs/`. A validação da sprint ocorre via `bin/orr_all.sh`.
```

**.gitignore**
```
out/
.env
.DS_Store
```

**.editorconfig**
```
root = true
[*]
end_of_line = lf
insert_final_newline = true
charset = utf-8
indent_style = space
indent_size = 2
```

**.gitattributes**
```
* text=auto eol=lf
```

**Makefile**
```
.PHONY: orr all t2 t3 t4 t5 t6 t7 t8
orr: all
all: t2 t3 t4 t5 t6 t7 t8
	bin/orr_all.sh --fail-fast
t2:
	bin/orr_t2.sh
t3:
	bin/orr_t3.sh
# demais metas similares
```

### 2.2 Runners (bin/) — contratos de CLI
Todos começam com `#!/usr/bin/env bash` + `set -euo pipefail`. Devem aceitar `--seed`, `--out` e honrar `ORR_SEED` e `ORR_OUTDIR`. Devem **sempre** escrever um scorecard JSON e um `MANIFEST.json` no diretório do gate. Saída 0=passou, 1=falhou.

**bin/orr_all.sh** (mínimo)
```
#!/usr/bin/env bash
set -euo pipefail
OUT=${ORR_OUTDIR:-out}
SEED=${ORR_SEED:-1337}
FROM=${1:-}
# chamada sequencial dos bin/orr_t{N}.sh; se qualquer um falhar, interrompe
mkdir -p "$OUT/scorecards"
# implementação completa no Bloco 4; aqui apenas a casca e roteamento
```

**bin/orr_t2.sh** (mínimo análogo aos demais gates)
```
#!/usr/bin/env bash
set -euo pipefail
OUT=${ORR_OUTDIR:-out}
DIR="$OUT/evidence/T2_unit"
mkdir -p "$DIR"
SC="$OUT/scorecards/T2_unit.json"
# escrever MANIFEST.json vazio e scorecard com passed=false até implementação
printf '{"files":[]}' > "$DIR/MANIFEST.json"
printf '{"gate":"T2","version":"1.0","passed":false,"failures":["not-implemented"],"metrics":{},"artifacts":[],"notes":""}' > "$SC"
exit 1
```

Os arquivos `bin/orr_t3.sh` … `bin/orr_t8.sh` repetem a casca acima, variando `T{N}_*` e mensagens. O Bloco 4 substituirá os stubs pela lógica completa.

### 2.3 Docs (docs/)
**docs/SPEC.md**
```
# SPEC — Inspectah v0.1 (Data Hub First)
Escopo e SLOs no Bloco 1. Este SPEC referencia `docs/EVIDENCE_SCHEMA.json` e os gates do Bloco 2.
```

**docs/EVIDENCE_SCHEMA.json** — JSON Schema válido (versão 1.0). O schema já descrito no Bloco 1 deve ser copiado **na íntegra** aqui.

**docs/SLOs.md**
```
# SLOs e Error Budget
Onboarding p50 ≤ 5 min; Detecção p95 ≤ 2 min; Explore p95 ≤ 200 ms/p99 ≤ 400 ms; Run success ≥ 99%/24h; Evidence 100%.
```

**docs/PLAYBOOKS.md**, **docs/LEGAL_TOS_ALLOWLIST.md**, **docs/RUNBOOK_*md** — cabeçalhos com sumário e tabelas mínimas conforme Bloco 1; conteúdos completos serão preenchidos no Bloco 4.

### 2.4 Contracts (OpenAPI/JSON Schema)
**contracts/api/explore.openapi.yaml** — OpenAPI 3.0 com pelo menos os endpoints `GET /explore` e `POST /explore/export` (esqueleto com componentes `schemas` vazios).  
**contracts/api/sources.openapi.yaml** — OpenAPI 3.0 com `POST /sources`, `POST /sources/{id}/fields`, `POST /sources/validate`.  
**contracts/data/item.schema.json** — schema mínimo de Item (campos principais).  
**contracts/data/source.schema.yaml** — schema YAML de Fonte com `fields[]`.

### 2.5 Services (README mínimos)
Cada serviço tem README com escopo, entradas/saídas e métricas expostas (nomes sugeridos no Bloco 1/2).

### 2.6 DB
`db/schema.sql` — cabeçalho com as tabelas principais (`sources`, `runs`, `items`, `item_kv`, `manifests`, `audit_log`). Pastas `migrations/` e `seeds/` vazias.

### 2.7 Tests
Arquivos `.txt` vazios atuam como sentinelas de caminho. As pastas de fixtures contêm exemplos mínimos reais:
- `tests/fixtures/goldens/rss/news_001/feed.xml` — RSS válido curto, com 2 items.  
- Correspondentes `expected/*.jsonl` com 2 linhas (itens e kv).  
- `tests/fixtures/goldens/api/store_001/input/sample.json` — JSON simples com 2 objetos; `expected/` idem.  
- Um manifest exemplo por conjunto em `expected/manifests/` com campos obrigatórios do Evidence.

### 2.8 Scripts (stubs executáveis)
Todos com `#!/usr/bin/env bash` + `set -euo pipefail` e `echo "stub"`. Serão implementados no Bloco 4.

### 2.9 Configs
- `configs/prometheus.dev.yml` — scrape básico.  
- `configs/grafana/dashboards/*.json` — JSON `{}` inicial (válido).  
- `configs/alertmanager/alerts.yml` — roteamento mínimo.

### 2.10 Workflows CI
`inspectah-ci.yml` e `inspectah-orr.yml` existem, mas **não** executam lógica de gates ainda; apenas criam `out/` e um artefato. O Bloco 4 detalhará os jobs reais.

## 3) Regras de Nomenclatura e Paths (obrigatórias)
- Gates: `T2_unit`, `T3_property`, `T4_golden`, `T5_bench`, `T6_obs`, `T7_ci`, `T8_final`.  
- Scorecards: `out/scorecards/T{N}_*.json`.  
- Evidências: `out/evidence/T{N}_*/… + MANIFEST.json`.  
- Release: `out/release/inspectah_v0_1_release.zip` + `CHECKSUMS.sha256`.

## 4) Validação do Scaffold (script de sanidade)
O Codex deve prover um script `bin/orr_sanity.sh` que:
1) Verifica existência exata de todos os caminhos desta árvore.  
2) Garante arquivos essenciais **não vazios**: `README.md`, `docs/SPEC.md`, `docs/EVIDENCE_SCHEMA.json`, OpenAPIs e Schemas em `contracts/`.  
3) Checa JSONs válidos (`jq -e .`), YAMLs parseáveis e que `bin/orr_t{N}.sh` sejam executáveis.  
4) Escreve `out/scorecards/T0_sanity.json` com `passed=true` se tudo ok.

## 5) Critérios de Aceite do Bloco 3 (Lock)
1) `bin/orr_sanity.sh` retorna 0 e produz `T0_sanity.json` com `passed=true`.  
2) Todos os `bin/orr_t{N}.sh` existem, são executáveis e escrevem um scorecard e `MANIFEST.json` (stub).  
3) `docs/EVIDENCE_SCHEMA.json` é um JSON Schema **válido** (cópia do Bloco 1).  
4) `contracts/*` existem e passam validação mínima (parse).  
5) Workflows presentes e válidos (YAML parse OK).  
6) `tests/fixtures/goldens/*` têm exemplos mínimos coerentes.

## 6) Hand‑off para o Codex (procedimento)
1) Gerar o scaffold exatamente como acima.  
2) Preencher `docs/EVIDENCE_SCHEMA.json` com o schema do Bloco 1.  
3) Criar `bin/orr_sanity.sh` conforme §4.  
4) Executar `bin/orr_sanity.sh` → deve gerar `out/scorecards/T0_sanity.json` (passed=true).  
5) Comitar e abrir PR “scaffold: repo skeleton + sanity (Bloco 3)”.

## 7) Revisão e Lock
- **Jobs**: clareza e ergonomia — 10/10.  
- **Lamport**: invariantes de paths e presença de MANIFEST/scorecards — 10/10.  
- **Meyer**: DbC aplicado aos runners e contratos presentes — 10/10.  
- **Status**: pronto para **LOCK** do Bloco 3.

