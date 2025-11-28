# Inspectah — Sprint 9
## Runbook oficial de demo (C1–C3)

Este runbook descreve, passo a passo, como reproduzir a demo da Sprint 9 para os cenários C1–C3 sem adivinhações. Siga sempre os invariantes Inv1–Inv4:

1. Use `PYTHONPATH=.` e mantenha `NET=0` em todos os comandos (já garantimos isso nos scripts).
2. Trabalhe a partir da raiz do repositório (`git rev-parse --show-toplevel`).
3. Deixe `INSPECTAH_DATA_DIR` apontar para `out/evidence` (ou um diretório limpo temporário) antes da demo.
4. Nunca pule Admin → User → Pipeline → GPT; todos os passos abaixo reforçam esse fluxo.

### Visão geral rápida

| Cenário | Pergunta oficial | Objetivo real | Fixtures/fontes | Resultado esperado |
|---------|------------------|---------------|------------------|--------------------|
| **C1** | "Qual é o preço médio atual da cesta básica padrão em São Paulo?" | Monitorar cesta “Ministério da Cidadania” em SP | `tests/fixtures/s9_preco_medio/*.json` (Painel SEAE, Pão de Açúcar, Coletor mobile) | Valor médio + intervalo, `num_sources >= 2`, confiança alta |
| **C2** | "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?" | Apoiar compras emergenciais de GLP 13kg para o RJ | `tests/fixtures/s9_comparacao/*.json` (ANP, Sindigás, Secretaria RJ) | Ranking capital×Baixada + diferença percentual + confiança |
| **C3** | "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?" | Checar fala pública da Dep. Carla Fontes | `tests/fixtures/s9_checagem_factual/*.json` (DO BH, Portal Transparência, ANP) | Veredito `negado` + notas e limitações + trilha completa |

Todas as execuções registram o triplo QueryLog ↔ EvidenceBundle ↔ UserResponse em `out/evidence/s9_logs|s9_bundles|s9_responses`, além das métricas em `app/observability/metrics_s9`.

---

## Passos comuns a todos os cenários

1. **Preparar fontes com Admin**
   ```bash
   PYTHONPATH=. python3 - <<'PY'
   from app.admin import service
   for scenario in ("C1", "C2", "C3"):
       service.prepare_scenario_sources(scenario)
       print(f"[admin] {scenario} pronto")
   PY
   ```
   Isso carrega as fixtures oficiais e atualiza `app/core/storage` com `num_sources >= 2`.

2. **Consultar via camada User**
   ```bash
   PYTHONPATH=. python3 - <<'PY'
   from app.user import routes
   scenarios = {
       "C1": "Qual é o preço médio atual da cesta básica padrão em São Paulo?",
       "C2": "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?",
       "C3": "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?",
   }
   for scenario_id, question in scenarios.items():
       response = routes.post_query({"question": question, "scenario_id": scenario_id})["response"]
       print(f"[{scenario_id}] status={response['status']} answer={response['answer_text']}")
   PY
   ```

3. **Verificar trilha de evidência**
   - QueryLog: `out/evidence/s9_logs/<query_id>.json`
   - EvidenceBundle: `out/evidence/s9_bundles/<bundle_id>.json`
   - UserResponse: `out/evidence/s9_responses/<response_id>.json`
   Os IDs são retornados na resposta do User (`query_id`, `summary_card.bundle_id`, `response_id`).

4. **Checar métricas**
   ```bash
   PYTHONPATH=. python3 - <<'PY'
   from app.observability import metrics_s9
   import json
   print(json.dumps(metrics_s9.get_metrics_snapshot(), indent=2, ensure_ascii=False))
   PY
   ```
   Verifique `inspectah_s9_user_queries_total{info_type,scenario,outcome}` e `user_latency_seconds` para confirmar outcomes e p95.

---

## C1 — Preço médio da cesta básica (SP)

- **Fluxo completo**
  ```bash
  PYTHONPATH=. python3 - <<'PY'
  from app.admin import service
  from app.user import routes
  service.prepare_scenario_sources("C1")
  resp = routes.post_query({
      "question": "Qual é o preço médio atual da cesta básica padrão em São Paulo?",
      "scenario_id": "C1",
  })["response"]
  print(resp["answer_text"])
  print(resp["summary_card"])
  print(resp["evidence_links"])
  PY
  ```
- **O que checar**
  - `summary_card.main_value ≈ 221.58 BRL`, `range.min/max ≈ 218–225`, `num_sources=3`, `confidence_level="high"`.
  - `evidence_links.bundle_path` aponta para `out/evidence/s9_bundles/<bundle>.json` com itens das três fontes.
  - QueryLog `out/evidence/s9_logs/<query_id>.json` contém `scenario_tag="C1"`, `error_code=null`, `status="ok"`.
  - Métrica `inspectah_s9_user_queries_total{info_type="C1", outcome="ok"}` incrementa; `user_latency_seconds` traz p95 ≪ 1,5s.

## C2 — Comparação GLP 13kg (RJ)

- **Fluxo completo**
  ```bash
  PYTHONPATH=. python3 - <<'PY'
  from app.admin import service
  from app.user import routes
  service.prepare_scenario_sources("C2")
  question = "Onde o botijão de gás 13kg está mais barato nesta semana, capital ou Baixada Fluminense?"
  resp = routes.post_query({"question": question, "scenario_id": "C2"})["response"]
  print(resp["answer_text"])
  print(resp["summary_card"])
  print(resp["evidence_links"])
  PY
  ```
- **O que checar**
  - `summary_card.best_location` deve ser Baixada (ex.: “Centro/Nova Iguaçu”), `best_value ≈ 95 BRL`, `num_sources=3`.
  - Se houver divergência >5%, `confidence_level` cai para “medium” e `confidence_reasons` explicam o motivo.
  - Evidências: `out/evidence/s9_bundles/<bundle>.json` contém preços ANP+Sindigás+Secretaria.
  - Métricas: `inspectah_s9_user_queries_total{info_type="C2", outcome="ok"}` e `errors_total` sem novos eventos.

## C3 — Checagem factual Diesel (BH)

- **Fluxo completo**
  ```bash
  PYTHONPATH=. python3 - <<'PY'
  from app.admin import service
  from app.user import routes
  service.prepare_scenario_sources("C3")
  question = "O preço médio do diesel caiu 12% em Belo Horizonte nos últimos 30 dias?"
  resp = routes.post_query({"question": question, "scenario_id": "C3"})["response"]
  print(resp["answer_text"])
  print(resp["summary_card"])
  print(resp["evidence_links"])
  PY
  ```
- **O que checar**
  - `summary_card.verdict="negado"`, `negatives=6`, `num_sources=3`, `limitations=[]`.
  - `evidence_links.sources` mostram DO BH + Portal Transparência + ANP; verifique `out/evidence/s9_bundles/<bundle>.json` para confirmar os itens.
  - Métricas: outcome `ok` em `inspectah_s9_user_queries_total{info_type="C3"}` e zero erros críticos em `inspectah_s9_errors_total`.

---

## Script de atalho — `bin/s9_demo.sh`

Execute `PYTHONPATH=. bin/s9_demo.sh` para reproduzir automaticamente o roteiro acima. O script:
1. Resolve a raiz, força `NET=0` e permite configurar `INSPECTAH_DATA_DIR` (padrão `out/evidence/s9_demo`).
2. Chama `prepare_scenario_sources` para C1, C2 e C3.
3. Executa as queries oficiais na camada User.
4. Exibe no terminal: pergunta, status, `main_value/best_location/verdict`, `num_sources`, confiança, limitações, `bundle_path`, `query_log_path` e um snapshot resumido das métricas (`user_queries_total`, `user_latency_seconds`).

---

## Observabilidade durante a demo

- **Logs**: acompanhe `out/evidence/s9_logs/` para ver a trilha completa. Cada arquivo inclui `error_code`, `scenario_tag` e paths de bundle/resposta.
- **Métricas**: rode `PYTHONPATH=. python3 -m app.observability.metrics_s9` (ver snippet acima) para observar p50/p95 e outcomes imediatamente após cada query.
- **Scorecards relevantes**: T4, T5 e T6 usam exatamente este runbook; reexecute `bin/s9_ci.sh` sempre que quiser garantir que tudo continua verde após ajustes de demo.

Qualquer alteração estrutural nas queries, fontes ou formato de resposta exige que este runbook, os fixtures e os capítulos 1–4 sejam atualizados imediatamente. Sem isso, o gate T0 falha automaticamente.
