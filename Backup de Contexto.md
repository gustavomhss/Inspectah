# Backup de Contexto — SF1 / S35 (ACE Exec) — memória reforçada

## 1) Identidade da sprint e branch
- Sprint SF1 (Programa 1, Épico Fix), waves W0–W5 conforme docs/sf1_tasks_execucao.yml (Plano do Planner).
- Branch de trabalho: s35-ace-exec (não commitar sem alinhamento).
- Raiz do repo: /Users/gustavoschneiter/Documents/Inspectah.

## 2) Estado consolidado por wave/gate (com evidências)
- W0–W1 (baseline, manifest, catálogos, ingest client):
  - Manifest/hash + SLOs: PASS, bundle em out/bundles/inspectah_s35_evidence_bundle.zip; manifest em out/evidence/S35_manifest.txt.
  - Catálogos newsdata/contestação presentes; s35_slos.md no bundle.
  - Ingest client ajustado: size total 50, per-request clamp 10, throttling/backoff 1/2/4s, sem retry em 4xx, dedup/hash, quota diária (~1000 req/dia), meta rica.
- W2 (API/Console baseline):
  - actor/operation_id/catalog_hash obrigatórios já existem; RBAC em ingestion/admin; porém IA/Admin final pendente (menus/histórico/derivadas).
- W3 (Observabilidade real):
  - Scripts bin/s35_g3_obs.sh executados com newsdata real; /metrics e promtool OK; painel export em out/evidence/S35_G3_observabilidade_rollout/; scorecard out/scorecards/S35_G3_obs.json PASS.
  - Alertas ingest incluídos; PromQL salvo em evidência.
- W4 (Pilotos reais):
  - bin/s35_g4_pilotos.sh executado com newsdata real (size per req=10). Evidências em out/evidence/S35_G4_pilotos_rollout/ (datasets, ingest_log, exec_dump, timeline, metrics snapshot, console_screenshots — capturar mais se UI mudar).
  - Scorecard out/scorecards/S35_G4_pilotos.json PASS.
- W5 (ORR/bundle):
  - metrics_summary e bundle rerodados; out/scorecards/S35_metrics_summary.json PASS; out/scorecards/S35_G5_orr.json PASS; bundle em out/bundles/inspectah_s35_evidence_bundle.zip.
- Governança: out/logs/SF1_gov.md com GO parcial (pendência IA/Admin).

## 3) Mudanças de código já aplicadas (essenciais)
- Backend ingest:
  - app/ingestion/services.py: size clamp per-request 10 (total 50), meta inclui attempts, requests_count, domains, throttle_seconds, trigger_origin, error_type; quota diária; limite 3 runs/min; requested_size registrado; per_request_size registrado.
  - app/ingestion/providers/news_provider_client.py: attempt_log com status/backoff/duração; suporte a limit legado; jitter retorna valor.
  - app/api/ingestion/routes.py e app/ingestion/schemas.py: RunSummary/RunDetail carregam meta para API/UI.
  - app/api/ingestion/routes.py: /admin/ingestion/{source}/run exige x-role admin/ops_ingest; newsdata_br usa run_newsdata_ingestion ops-only.
- Front ingest UI:
  - IngestionListPage/IngestionSourceDetailPage: mensagens específicas 429/5xx/4xx; banner ops-only newsdata_br; CTA retry em falha; resumo do último run com meta (size total/por req, requests, throttle, domínios, trigger); modo fixo ops_only para newsdata_br; link “Ver histórico” na tabela; histórico read-only.
  - Modal IngestionRunDetailModal: mostra meta (hash/actor/op_id/catalog_hash se existir), tabela de tentativas/backoff/duração.
  - Renomeação de “Providers v2” -> “Perfis de Fonte” no menu e página de providers.
- Tests:
  - Vitest src/__tests__/ingestion/IngestionPages.test.tsx cobre lista/detail ops-only, meta/modal; MSW handlers usados; executado com sucesso.

## 4) Pendências críticas (deixar pronto para qualquer agente)
1) Modelo provedor newsdata + fontes derivadas (SF1-UX-031..034, SF1-API-035):
   - Provedor newsdata_br (ops-only) mantém CTA real/histórico/meta.
   - Fontes derivadas (domínios do provedor) devem aparecer em UI como catálogo: sem CTA de ingest, sem fetch de runs, status “derivada do provedor” e configuráveis/visíveis.
   - Fontes manuais com ingestion_mode continuam com CTA/histórico.
   - CTA rollout deve apontar para pipeline newsdata_br e registrar histórico (SF1-API-035).
2) Ruído 404 em /admin/ingestion/{id}/runs:
   - Hoje, runs são chamados para todas as fontes; backend responde 404 se não há config. Precisa mudar para 200 com runs=[] ou evitar a chamada para derivadas.
   - Ideal: campo provider_id/kind no payload para identificar derivadas (newsdata_domain). Fallback: ausência de ingestion_mode ⇒ tratar como derivada.
3) Evidências UI/Admin:
   - Capturar screenshots exigidas: lista com provedor + derivadas + banner ops-only; estados empty/429/5xx/4xx; detalhe provedor com meta/backoff/erro; modal de tentativas; histórico global read-only + retry.
   - Salvar em out/evidence/S35_G4_pilotos_rollout/console_screenshots (ou pasta acordada). Se UI mudar, reemitir scorecards/bundle/metrics_summary.

## 5) Plano granular (checklist executável)
### Backend — eliminar 404 e suportar derivadas
- [ ] app/api/ingestion/routes.py: em list_runs/get_run_detail, se fonte/config inexistente → retornar RunsResponse (runs=[], config_mode=None) com 200, não 404.
- [ ] (Opcional) Adicionar campo provider_id/kind ao modelo de fonte/ingestion responses se já disponível; caso contrário, apenas evitar erro.

### Front — UI provedor vs derivadas
- [ ] Definir identificação de derivadas: usar provider_id='newsdata_br' ou kind='newsdata_domain'; se não existir, usar ausência de ingestion_mode como sinal.
- [ ] Página /admin/ingestion:
   - Seção provedor newsdata_br: CTA ops_only, histórico, meta, banner existente.
   - Seção fontes derivadas: tabela sem CTA, sem fetch de runs, status “Derivada do provedor (sem pipeline individual)”.
   - Fontes com ingestion_mode (manuais) continuam com CTA/histórico.
   - Ajustar filtros/banners para deixar hierarquia clara.
- [ ] Página /admin/ingestion/sources/:sourceId:
   - Derivada: não chamar runs; CTA desabilitado; texto “controlada pelo provedor newsdata_br”; histórico read-only vazio.
   - Provedor: manter CTA + meta/tentativas/backoff.

### Evidências e governança
- [ ] Capturar screenshots (lista, detalhe provedor, modal, erros 429/5xx/4xx, histórico read-only + retry).
- [ ] Atualizar out/logs/SF1_gov.md se IA/Admin fechada; reemitir out/scorecards/S35_G4_pilotos.json, out/scorecards/S35_G5_orr.json, out/bundles/inspectah_s35_evidence_bundle.zip se UI mudar.

### Tests
- [ ] Ajustar MSW para derivadas: retornar runs 200 vazio; evitar 404; atualizar testes se UI splitar provedor/derivadas.
- [ ] Rerodar `npm test -- --watch=false src/__tests__/ingestion/IngestionPages.test.tsx` após ajustes.

## 6) Caminhos de referência
- Scorecards: out/scorecards/S35_G*.json, out/scorecards/S35_metrics_summary.json
- Evidências: out/evidence/S35_G3_observabilidade_rollout/, out/evidence/S35_G4_pilotos_rollout/, out/bundles/inspectah_s35_evidence_bundle.zip
- Logs: out/logs/SF1_baseline.md, out/logs/SF1_gov.md
- Plano: docs/sf1_tasks_execucao.yml, docs/sf1_cap_4_4_tasks_e_waves.md
- Código UI ingest relevante: frontend/inspectah-ui/src/modules/ingestion/pages/*.tsx, components/*.tsx, api/ingestionApi.ts, hooks/useIngestionSources.ts, tests em src/__tests__/ingestion/IngestionPages.test.tsx
- Backend ingest relevante: app/ingestion/services.py, providers/news_provider_client.py, app/api/ingestion/routes.py, app/ingestion/schemas.py

## 7) Riscos/Gaps anotados
- Identificação de derivadas sem campo explícito é frágil; preferir provider_id/kind no payload.
- UI/Admin mudanças podem exigir reexecução de scorecards/bundle.
- Ruído 404 atual é log de ausência de config; esperado eliminar após mudança 200 runs=[] ou evitando fetch.

## 8) Handoff ultra-curto (se contexto truncar)
- Prioridade imediata: (1) backend 200 runs=[] para fontes sem ingest; (2) front split provedor (newsdata_br) vs derivadas (sem CTA/run), identificação por provider_id/kind ou ausência de ingestion_mode; (3) capturar screenshots e reemitir scorecards/bundle se UI alterar.
- Tests Vitest devem continuar verdes (ajustar MSW). Evidências finais em console_screenshots + scorecards atualizados.***

## 9) Atualização pós UI/derivadas (novas decisões)
- Backend: list_runs agora não deve 404 (tratar ConfigNotFound/SourceNotFound como runs=[]); meta de runs segue igual.
- Front: IngestionMode ganha valor DERIVED; Badge mostra “Derivada (prov.)”. Hooks:
  - useIngestionSources marca isProvider (newsdata_br) e isDerived (sem ingestion_mode e não provider) → não chama runs API para derivadas, saúde=Derivada, CTA desabilitado, modo DERIVED.
  - useIngestionRuns aceita enabled=false para pular fetch/poll.
- UI list/detail:
  - Tabela: derivadas sem CTA/run, texto “Controlada pelo provedor newsdata_br”; histórico indisponível; botões desabilitados.
  - Detalhe: derivadas não mostram resumo de run nem timeline; CTA desabilitado com aviso; progress/histórico read-only placeholder.
  - Ops-only/provedor newsdata_br permanece com CTA real e meta.
- Bug do Vite “Identifier Card” resolvido renomeando import (UiCard).
- Vitest atualizado (src/__tests__/ingestion/IngestionPages.test.tsx) para fontes com ingestion_mode, mantendo cenários ops_only; testes passam (somente warnings de act).

## 10) Pendências ainda abertas após ajustes
1. Capturar screenshots de UI (lista com provedor + derivadas, detalhe provedor com meta/backoff/erros, modal de tentativas, estados 429/5xx/4xx, histórico read-only + retry) em out/evidence/S35_G4_pilotos_rollout/console_screenshots.
2. Confirmar se backend 404 sumiu; se persistir, revisar outro router ou endpoint (/admin/ingestion/runs) para retornar vazio.
3. Avaliar se precisamos enriquecer modelo de fonte com provider_id/kind real vindo do backend (hoje opcional e não usado pelo fetch). Se Planner/Spec exigir, adicionar no AdminSource e ajustar fetchSources para mapear campos reais.
4. Caso UI mude, rerodar scorecards G4/G5 e bundle.
5. Atualizar out/logs/SF1_gov.md e checklist final conforme DoD após screenshots.
