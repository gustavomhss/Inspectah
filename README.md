# Inspectah — Data Hub First (v0.1)
Repositório oficial do Inspectah v0. Os contratos e SLOs estão em `docs/`. A validação integral da Sprint 2 é reproduzida via `bin/run_inspectah_v0_e2e.sh` (detalhes abaixo) e pela suíte `PYTHONPATH=$PWD ./.venv/bin/pytest`.

## Ambiente de desenvolvimento v0

1. Clone e entre no repositório:
   ```bash
   git clone <repo> inspectah
   cd inspectah
   ```
2. Suba o ambiente local (cria `.venv`, instala dependências declaradas em `pyproject.toml`, reinicia o banco e inicia FastAPI/uvicorn em `127.0.0.1:8000`):
   ```bash
   bin/dev_up.sh
   ```
   - Logs: `out/logs/dev_api.log`
   - PID: `out/dev/inspectah.pid`
   - Banco SQLite: `inspectah.db`
3. Verifique rapidamente a API (sem dados ainda):
   ```bash
   curl -s http://127.0.0.1:8000/explore/items | jq '.items'
   ```
4. Derrube o ambiente quando terminar:
   ```bash
   bin/dev_down.sh
   ```
   O script encerra apenas o PID registrado e preserva os logs em `out/logs/dev_api.log`.

Todos os comandos são idempotentes: `bin/dev_up.sh` sempre usa o `.venv` local. Em ambientes sandbox sem internet/sockets, o script registra avisos e entra em modo *idle* aguardando `bin/dev_down.sh`; em uma máquina normal o servidor uvicorn ficará acessível em `http://127.0.0.1:8000`.

## Ingest demo (rss_news_minimal)

Com o ambiente ligado (`bin/dev_up.sh`):

```bash
./scripts/ingest_source_demo.sh
```

Saída esperada:

```
{"source_id": "rss_news_minimal", "items_ingested": 2}
```

O script usa o pipeline oficial (`inspectah.ingest.pipeline.run_ingest_pipeline`) para ingerir o fixture `tests/fixtures/rss_sample.xml`, aplicando o schema publicado via Field Designer. O comando é idempotente: reexecutá-lo acumula itens apenas se o conteúdo for novo.

## Explore API — exemplos reais

Após rodar o ingest demo:

```bash
# Lista paginada
curl -s "http://127.0.0.1:8000/explore/items?page=1&page_size=5" | jq '.items[0]'

# Consulta com filtro por source
curl -s "http://127.0.0.1:8000/explore/items?source_id=rss_news_minimal" | jq '.items | length'

# Detalhe por ID
ITEM_ID=$(curl -s http://127.0.0.1:8000/explore/items | jq '.items[0].item_id')
curl -s "http://127.0.0.1:8000/explore/items/${ITEM_ID}"

# Lista de fontes
curl -s http://127.0.0.1:8000/explore/sources | jq '.sources'
```

Todos os endpoints respeitam o rate limit v0 (120 req/min, burst 240) e retornam erro padronizado `429 RATE_LIMITED` com cabeçalhos `X-RateLimit-*` se o limite for excedido.

## Evidence Vault v0 (CLI)

Sem necessidade de subir o dev server:

```bash
echo '{"demo":true}' > /tmp/evidence_demo.json
PYTHONPATH=$PWD ./.venv/bin/python -m inspectah.evidence_vault.cli write \
  --file /tmp/evidence_demo.json \
  --source-id smoke_manual \
  --evidence-type json_blob \
  --lgpd-tag lgpd.personal
# -> {"evidence_id": "...", ...}

PYTHONPATH=$PWD ./.venv/bin/python -m inspectah.evidence_vault.cli read --id <ID_ANTERIOR>
```

O write calcula SHA256, usa o backend `local_stub` (S3-like, `sa-east-1`, SSE-KMS lógico) e persiste metadados em `evidence_records`. O read retorna metadados e, se desejado, o payload (`--with-payload`). Para um teste completo com logs e fixtures prontos:

```bash
./scripts/evidence_vault_smoke.sh
```

Esse script gerencia `bin/dev_up.sh/bin/dev_down.sh`, gera uma evidência e imprime logs/cabeçalhos relevantes em ambientes com rede habilitada.

## Fluxo E2E v0 (script oficial)

```bash
./bin/run_inspectah_v0_e2e.sh
```

Etapas automatizadas:

1. `bin/dev_up.sh`
2. Ingest demo (pipeline oficial)
3. Consulta aos endpoints `/explore/items` + métricas (`inspectah_ingest_*`, `inspectah_explore_queries_total`)
4. Validação de manifest/evidência
5. `bin/dev_down.sh`

Saída típica:

```
{'stage': 'ingest', 'items_ingested': 2}
{'stage': 'explore', 'items_count': 2, 'first_item_id': 1}
{'stage': 'metrics', 'ingest_items_total': {'count': 2.0, ...}, 'explore_queries_total': {'count': 1.0, ...}}
{'stage': 'manifest', 'manifest_path': '.../manifest.json', 'source_id': 'rss_news_minimal', ...}
```

## Métricas em tempo de execução

Com o ambiente ativo, é possível inspecionar o snapshot atual:

```bash
PYTHONPATH=$PWD ./.venv/bin/python - <<'PY'
from inspectah.metrics import get_snapshot
print(get_snapshot())
PY
```

Os contadores relevantes expostos são:

- `inspectah_ingest_items_total`
- `inspectah_ingest_errors_total`
- `inspectah_explore_queries_total`
- `inspectah_explore_requests_total`
- `inspectah_explore_rate_limited_total`

Esses valores também aparecem no script E2E e no gate S2-G4.
