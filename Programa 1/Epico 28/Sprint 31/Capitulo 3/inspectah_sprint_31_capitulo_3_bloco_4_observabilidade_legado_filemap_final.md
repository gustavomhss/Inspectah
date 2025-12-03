# Inspectah — Sprint 31 (E28-S3)
## Capítulo 3 — Bloco 4: Observabilidade, Legado & Filemap Final

### 3.17 Objetivo deste bloco

Este bloco fecha a arquitetura da S31 em três frentes:

1. **Observabilidade** específica para ingestão provider-first (métricas, logs, dashboards).
2. **Convivência fina com legado** (RSS/APIs/scrapers) em nível de arquitetura.
3. **Filemap final** consolidado, amarrando tudo que a sprint toca.

É o "onde está o quê" que permite ao Codex, ao time e ao Conselho navegarem o repo sem adivinhação.

---

### 3.18 Observabilidade da ingestão provider-first

A observabilidade da S31 serve a dois propósitos complementares:

- permitir que operadores enxerguem **saúde e custo** por perfil e provider;
- alimentar os scripts de gates (G2, G3, G5) com dados confiáveis para scorecards.

#### 3.18.1 Métricas técnicas por perfil

Módulo sugerido: `app/metrics/ingestion_provider_metrics.py`

Responsabilidades:

- Expor helpers para registrar as métricas mínimas por run de perfil:
  - `provider_calls_total`
  - `items_ingested_total`
  - `contentitems_created_total`
  - `provider_errors_total`
  - `dedupe_ratio`
  - `budget_limit_calls`
  - `budget_usage_ratio`
  - `latency_p95`

- Padronizar labels:
  - `profile_id`
  - `provider_id`
  - `provider_type` (NEWS/SOCIAL)
  - `domain_tag` (ex.: `BR_PT_HARD_NEWS` vs `GLOBAL_EN_GENERAL`)

Integração no código:

- `profile_runner` chama funções deste módulo ao finalizar um run;
- jobs registram início/fim e durações para cálculo de latência.

#### 3.18.2 Logs estruturados

Módulo sugerido: `app/logging/ingestion_provider_logger.py`

Formato mínimo de log por run de perfil (linha ou evento JSON):

- `timestamp`
- `level`
- `profile_id`
- `provider_id`
- `window_from` / `window_to`
- `calls`
- `items_raw`
- `contentitems_created`
- `errors` (lista resumida por tipo)
- `status` (SUCCESS / PARTIAL / FAIL)

Uso:

- `profile_runner` cria um evento por run;
- scripts G2/G3 podem amostrar esses logs como evidência e, quando necessário, gerar relatórios sintéticos em `out/evidence`.

#### 3.18.3 Dashboards

Diretório sugerido: `infra/observability/dashboards/s31_provider_ingestion.json` (ou estrutura equivalente ao stack atual).

Painéis mínimos:

1. **Visão por perfil**  
   - gráfico de `provider_calls_total` vs `contentitems_created_total` por dia;
   - `dedupe_ratio` ao longo do tempo;
   - `budget_usage_ratio` e alertas quando > 0.9.

2. **Visão por provider**  
   - total de chamadas na sprint;
   - taxa de erro média;
   - top 5 perfis por consumo de chamadas e por volume de conteúdo útil.

3. **Visão de erros**  
   - gráfico com contagem de erros por tipo (rate limit, timeout, auth);
   - correlação com janelas de horários (ajuda a descobrir congestão previsível).

Conexão com gates:

- G2/G3 podem simplesmente validar que painéis foram gerados e que dados parecem consistentes com os logs/DB para perfis-piloto.

---

### 3.19 Convivência e migração do legado

A Sprint 31 não desliga o legado, mas o coloca em seu lugar certo na arquitetura.

#### 3.19.1 Catálogo de fluxos legados

Arquivo sugerido: `docs/sprint_31_legacy_migration_plan.md`

Conteúdo mínimo:

- tabela com colunas:
  - `fluxo_legacy_id` (ex.: `RSS_G1_POLITICA`, `SCRAPER_PORTAL_X`)
  - tipo (RSS/API/SCRAPER);
  - domínio/tema principal;
  - status (`CRITICAL`, `IMPORTANT`, `CAN_RETIRE`);
  - relação com providers (ex.: "coberto por profile Y", "sem equivalente");
  - decisão S31 (manter, migrar futuramente, iniciar desligamento).

Uso:

- G4 lê este documento e garante que fluxos marcados como `CRITICAL` foram testados após migrations.

#### 3.19.2 Adaptador de legado

Arquivo sugerido: `app/ingestion/legacy_adapter.py`

Responsabilidades:

- Encapsular chamada de fluxos legados críticos para uso em gates (sanity);
- fornecer funções como:
  - `run_legacy_feed(feed_id: str) -> LegacyRunResult`;
  - `list_critical_legacy_feeds() -> list[LegacyFeedInfo]`.

Integração com G4:

- `bin/s31_g4_legacy_and_compat.sh` chama o adaptador com a lista de fluxos críticos e verifica se todos passam.

#### 3.19.3 Caminho de migração

A S31 não precisa executar a migração inteira, mas precisa:

- marcar fluxos que já podem ser mapeados para providers/perfis;
- registrar em `docs/sprint_31_legacy_migration_plan.md` quais perfis pretendem substituí-los em sprints futuras;
- garantir que, quando um fluxo legado for aposentado, haverá uma trilha de comunicação mínima (nota em docs + mudanças rastreáveis em config).

---

### 3.20 Filemap final consolidado da Sprint 31

Este é o filemap **pós-revisão**, consolidando o que S31 deve tocar/criar. Os nomes podem ter pequenas variações para se alinhar ao padrão do repo, mas a estrutura lógica deve ser esta.

#### 3.20.1 Documentação

- `docs/sprint_31_capitulo_1_contexto.md`
- `docs/sprint_31_capitulo_2_gates_metricas_invariantes.md`
- `docs/sprint_31_capitulo_3_arquitetura_filemap.md`
- `docs/sprint_31_capitulo_4_execucao_e_evidencias.md`
- `docs/sprint_31_legacy_migration_plan.md`

#### 3.20.2 Modelos & domínio

- `app/models/provider.py`
- `app/models/ingestion_profile.py`
- `app/models/content_item.py` (ajustes S31)
- `app/models/source.py` (ajustes S31)

#### 3.20.3 Ingestão provider-first

- `app/ingestion/providers/base_client.py`
- `app/ingestion/providers/news_provider_client.py`
- `app/ingestion/providers/social_provider_client.py`
- `app/ingestion/profile_runner.py`
- `app/ingestion/normalizer.py`
- `app/ingestion/dedupe_service.py`

#### 3.20.4 Jobs & scheduler

- `app/jobs/provider_ingestion.py`
- `app/jobs/scheduler.py`

#### 3.20.5 Console de Fontes v2 (backend)

- `app/api/console_providers.py`
- `app/api/console_ingestion_profiles.py`

#### 3.20.6 Console de Fontes v2 (frontend)

- `frontend/inspectah-ui/src/pages/console/providers/index.tsx`
- `frontend/inspectah-ui/src/pages/console/providers/[id].tsx`
- `frontend/inspectah-ui/src/pages/console/ingestion-profiles/index.tsx`
- `frontend/inspectah-ui/src/pages/console/ingestion-profiles/edit.tsx`
- `frontend/inspectah-ui/src/pages/console/ingestion-profiles/[id].tsx`
- `frontend/inspectah-ui/src/components/console/ProviderList.tsx`
- `frontend/inspectah-ui/src/components/console/IngestionProfileForm.tsx`
- (opcional) componentes de métricas, ex.: `ProfileMetricsCard.tsx`

#### 3.20.7 Configuração

- `config/providers.yml`
- `config/ingestion_profiles.yml`

#### 3.20.8 Observabilidade

- `app/metrics/ingestion_provider_metrics.py`
- `app/logging/ingestion_provider_logger.py`
- `infra/observability/dashboards/s31_provider_ingestion.json`

#### 3.20.9 Legado & migração

- `app/ingestion/rss_legacy.py` (já existente)
- `app/ingestion/scrapers/...` (já existente)
- `app/ingestion/legacy_adapter.py` (novo)

#### 3.20.10 Migrations (ilustrativo)

- `migrations/versions/31xx_add_provider_and_ingestion_profile.py`
- `migrations/versions/31xy_add_provider_fields_to_content_item.py`

#### 3.20.11 Gates & ORR

- `bin/s31_g0_scope_and_baseline.sh`
- `bin/s31_g1_models_and_migrations.sh`
- `bin/s31_g2_provider_ingestion.sh`
- `bin/s31_g3_console_and_observability.sh`
- `bin/s31_g4_legacy_and_compat.sh`
- `bin/s31_g5_p2_p3_integration.sh`
- `bin/s31_orr.sh`

#### 3.20.12 Evidências & scorecards

- `out/evidence/S31_G0_scope/...`
- `out/evidence/S31_G1_models_and_migrations/...`
- `out/evidence/S31_G2_provider_ingestion/...`
- `out/evidence/S31_G3_console/...`
- `out/evidence/S31_G4_legacy/...`
- `out/evidence/S31_G5_p2_p3/...`
- `out/evidence/S31_ORR/...`

- `out/scorecards/S31_G0_scope_and_baseline.json`
- `out/scorecards/S31_G1_models_and_migrations.json`
- `out/scorecards/S31_G2_provider_ingestion.json`
- `out/scorecards/S31_G3_observabilidade.json`
- `out/scorecards/S31_G4_legacy_and_compat.json`
- `out/scorecards/S31_G5_p2_p3_integration.json`
- `out/scorecards/S31_ORR_overview.json`

---

### 3.21 Fecho do Capítulo 3

Com este bloco, o Capítulo 3 fica completo:

- a observabilidade da S31 deixa de ser abstrata e vira módulos, métricas e dashboards concretos;
- o legado ganha um lugar explícito na arquitetura, com plano de convivência e migração;
- o filemap final vira um contrato operacional entre especificação e implementação.

A partir daqui, o Capítulo 4 pode pegar esse mapa e traduzi-lo em plano de execução: comandos, ordem de implementação, checagens e evidências necessárias para carimbar a Sprint 31 como GO ou NO-GO em provider-first para o primeiro domínio piloto.

