# Inspectah — Sprint 31 (E28-S3)
## Capítulo 3 — Arquitetura & Filemap da Ingestão Provider-first

### 3.0 Papel deste capítulo

Este capítulo descreve **como** a Sprint 31 se materializa na arquitetura do Inspectah e **onde** cada peça mora no repositório. Ele amarra:

- o modelo provider-first (Provider → Perfil → ContentItem) aos módulos de backend, frontend, jobs e observabilidade;
- a convivência entre ingestão via providers e fluxos legados (RSS/APIs/scrapers);
- o filemap mínimo que o Codex precisa respeitar ao implementar a sprint.

Ao final, qualquer pessoa deve conseguir pegar este capítulo, abrir o repo e enxergar **onde está cada parte da S31**.

---

### 3.1 Visão geral da arquitetura da S31

A Sprint 31 mexe principalmente na camada de ingestão de conteúdo dinâmico (notícias e social), encaixando providers no ecossistema existente. A visão alto nível fica assim:

1. Providers externos
   - News providers (ex.: NewsData/NewsAPI-like) e social providers (ex.: stack de social listening) expõem APIs pagas, com filtros por país/idioma/tema e limites de uso.

2. Camada de configuração do Inspectah
   - Entidade `Provider` descreve cada provider externo (tipo, regiões, credenciais, observações).
   - Entidade `IngestionProfile` (ou equivalente) descreve **perfis de ingestão**: provider + filtros + frequência + budget.
   - Configs são salvas em banco (modelos) e parametrizadas por arquivos YAML/JSON em `config/`.

3. Jobs de ingestão em fila
   - Scheduler converte perfis ativos em jobs `INGEST_NEWS_<profile>` ou `INGEST_SOCIAL_<profile>`.
   - Workers consomem a fila, chamam o provider com parâmetros do perfil e persistem os resultados.

4. Normalização e dedupe
   - Respostas brutas viram estruturas intermediárias (`RawNewsItem`, `RawSocialItem`).
   - Serviço de normalização cria/atualiza `ContentItem` canônico com proveniência completa.
   - Serviço de dedupe garante que o mesmo conteúdo não gera múltiplos ContentItems.

5. Observabilidade
   - Cada run de perfil registra métricas (calls, itens, errors, dedupe_ratio, budget_usage) e logs estruturados.
   - Painéis mostram comportamento por perfil e provider.

6. Integração com Programas 2–3
   - ContentItems de perfis-piloto alimentam pipelines de Programa 2 (Intérprete, Classificador, Claims, ClaimGraph).
   - Claims e evidências selecionadas alimentam Truth-DB/Sistema de Blocos (Programa 3), com trilha Provider → Perfil → ContentItem → Claim → FactBlock.

7. Legado
   - Fluxos legados (RSS/APIs/scrapers) continuam existindo, mas claramente marcados como tais.
   - Há um plano de migração/coexistência que indica o que já migrou, o que não pode migrar e o que será desligado no futuro.

---

### 3.2 Arquitetura de backend (modelos, serviços, jobs)

#### 3.2.1 Modelos principais

Diretório base (sugestivo, adaptar ao padrão atual do repo):

- `app/models/provider.py`
- `app/models/ingestion_profile.py`
- `app/models/content_item.py` (ajustes)
- `app/models/source.py` (ajustes)

Novos modelos/campos:

1. `Provider`
   - Campos típicos:
     - `id`: chave primária interna.
     - `slug`: identificador curto (ex.: `newsdata_global`, `social_radar_br`).
     - `type`: enum (`NEWS`, `SOCIAL`).
     - `base_url`: endpoint raiz.
     - `regions_supported`, `languages_supported`, `categories_supported`.
     - `status`: ativo/inativo.
     - `meta`: JSON com configs específicas.

2. `IngestionProfile`
   - Campos típicos:
     - `id`.
     - `name`: nome interno descritivo (ex.: `BR_PT_HARD_NEWS`).
     - `provider_id`: FK para `Provider`.
     - `filters`: JSON com país, idioma, categorias, keywords, ranges de datas.
     - `schedule`: expressão cron ou enum de frequência.
     - `budget_limit_calls`: limite de chamadas por período.
     - `status`: ativo, pausado, experimental.

3. Ajustes em `ContentItem`
   - Novos campos:
     - `provider_id`: FK opcional para `Provider`.
     - `ingestion_profile_id`: FK opcional para `IngestionProfile`.
     - `external_id`: ID dado pelo provider para a notícia/post.
     - `source_domain`: domínio do veículo (ex.: `g1.globo.com`).
     - `ingested_at`: timestamp da ingestão.
   - Garantias:
     - índices para busca rápida por provider/profile/domínio;
     - constraints que evitem duplicação grosseira (combinação de `provider_id`, `external_id`, `published_at`).

4. Ajustes em `Source`
   - Permitir mapear domínios/veículos a sources internas, eventualmente ligadas a providers.

#### 3.2.2 Clientes de provider

Diretório sugerido:

- `app/ingestion/providers/base_client.py`
- `app/ingestion/providers/newsdata_client.py` (exemplo)
- `app/ingestion/providers/social_client.py`

Responsabilidades:

- Encapsular autenticação, paginação, retry e mapeamento de erros.
- Expor métodos genéricos, por exemplo:
  - `fetch_news(profile: IngestionProfile, window: TimeWindow) -> list[RawNewsItem]`
  - `fetch_social(profile: IngestionProfile, window: TimeWindow) -> list[RawSocialItem]`

#### 3.2.3 Serviço de ingestão por perfil

Diretório sugerido:

- `app/ingestion/profile_runner.py`
- `app/ingestion/dedupe_service.py`
- `app/ingestion/normalizer.py`

Responsabilidades:

- `profile_runner`:
  - ler config do perfil;
  - verificar budget (chamadas disponíveis);
  - chamar o client do provider correspondente;
  - registrar métricas de chamadas e erros;
  - enviar itens brutos para normalização.

- `normalizer`:
  - converter `RawNewsItem`/`RawSocialItem` em `ContentItem` canônico;
  - preencher campos de proveniência;
  - delegar dedupe ao `dedupe_service`.

- `dedupe_service`:
  - calcular hash de conteúdo/URL;
  - checar se já existe ContentItem equivalente;
  - atualizar ou criar novo conforme regra definida.

#### 3.2.4 Jobs & scheduler

Diretórios sugeridos:

- `app/jobs/provider_ingestion.py`
- `app/jobs/scheduler.py`

Responsabilidades:

- Scheduler:
  - ler perfis ativos e sua frequência;
  - enfileirar jobs `INGEST_PROFILE::<profile_id>`.

- Job de ingestão:
  - ler `profile_id` da fila;
  - chamar `profile_runner.run(profile_id, window)`;
  - registrar logs estruturados (parâmetros, contagens, erros).

---

### 3.3 Arquitetura de frontend (Console de Fontes v2)

Diretório base sugerido do frontend:

- `frontend/inspectah-ui/src/pages/console/providers/`
- `frontend/inspectah-ui/src/pages/console/ingestion_profiles/`
- `frontend/inspectah-ui/src/components/console/` (componentes compartilhados)

Principais telas:

1. Lista de Providers
   - Caminho: `/console/providers`.
   - Mostra: nome, tipo (news/social), status, principais regiões/idiomas.
   - Ações: ver detalhes, ativar/desativar.

2. Detalhe de Provider
   - Caminho: `/console/providers/:providerId`.
   - Mostra: metas, limitações, documentação interna, lista de perfis associados.

3. Lista de Perfis de Ingestão
   - Caminho: `/console/ingestion-profiles`.
   - Mostra: nome do perfil, provider, domínio principal (ex.: BR/PT/política), status, últimas execuções.

4. Edição/Criação de Perfil
   - Caminho: `/console/ingestion-profiles/:profileId/edit` ou `/console/ingestion-profiles/new`.
   - Permite configurar: provider, filtros principais, schedule, budget_limit_calls.

5. Execução manual & detalhes de execução
   - Botão “Rodar agora” por perfil.
   - Modal ou tela com últimas execuções (hora, duração, itens, erros, uso de budget).

APIs associadas (backend):

- `GET /api/console/providers`;
- `GET /api/console/providers/{id}`;
- `GET /api/console/ingestion-profiles`;
- `POST /api/console/ingestion-profiles`;
- `PATCH /api/console/ingestion-profiles/{id}`;
- `POST /api/console/ingestion-profiles/{id}/run-now`.

Implementações API sugeridas em:

- `app/api/console_providers.py`;
- `app/api/console_ingestion_profiles.py`.

---

### 3.4 Observabilidade & logs

Diretórios e arquivos sugeridos:

- `app/metrics/ingestion_provider_metrics.py`
- `app/logging/ingestion_provider_logger.py`
- Dashboards em infra (ex.: `infra/observability/dashboards/s31_provider_ingestion.json`).

Mínimo de instrumentação:

- Métricas por perfil: calls, itens brutos, ContentItems criados, erros, dedupe_ratio, budget_usage_ratio, latency_p95.
- Logs estruturados por run de perfil, com campos: profile_id, provider_id, janela temporal, contagens, status.

Integração com gates:

- Scripts S31-G2 e S31-G3 leem essas métricas/logs para gerar scorecards.

---

### 3.5 Convivência com legado

A arquitetura S31 não remove de imediato a ingestão legada. Em vez disso:

- Mantém módulos existentes em:
  - `app/ingestion/rss_legacy.py`;
  - `app/ingestion/scrapers/…`;
  - `app/jobs/legacy_ingestion.py` (nomes ilustrativos).

- Cria um adaptador de convivência, por exemplo:
  - `app/ingestion/legacy_adapter.py`, que:
    - documenta quais fluxos legados são críticos;
    - chama jobs antigos como parte de sanity (S31-G4);
    - oferece utilitários para mapear fontes legadas a potenciais perfis de provider.

- Documenta a matriz de migração em:
  - `docs/sprint_31_legacy_migration_plan.md` (apontado por G4).

---

### 3.6 Filemap detalhado da Sprint 31

Abaixo, um filemap mínimo esperado para a S31 (nomes podem ser ajustados ao padrão real, mas a estrutura deve ser equivalente):

Docs
- `docs/sprint_31_capitulo_1_contexto.md`
- `docs/sprint_31_capitulo_2_gates_metricas_invariantes.md`
- `docs/sprint_31_capitulo_3_arquitetura_filemap.md` (este capítulo)
- `docs/sprint_31_capitulo_4_execucao_e_evidencias.md`
- `docs/sprint_31_legacy_migration_plan.md`

Backend — modelos & serviços
- `app/models/provider.py`
- `app/models/ingestion_profile.py`
- `app/models/content_item.py` (ajustes S31)
- `app/models/source.py` (ajustes S31)
- `app/ingestion/providers/base_client.py`
- `app/ingestion/providers/news_provider_client.py`
- `app/ingestion/providers/social_provider_client.py`
- `app/ingestion/profile_runner.py`
- `app/ingestion/normalizer.py`
- `app/ingestion/dedupe_service.py`
- `app/ingestion/legacy_adapter.py`
- `app/jobs/provider_ingestion.py`
- `app/jobs/scheduler.py`

Backend — APIs Console
- `app/api/console_providers.py`
- `app/api/console_ingestion_profiles.py`

Frontend
- `frontend/inspectah-ui/src/pages/console/providers/index.tsx`
- `frontend/inspectah-ui/src/pages/console/providers/[id].tsx`
- `frontend/inspectah-ui/src/pages/console/ingestion-profiles/index.tsx`
- `frontend/inspectah-ui/src/pages/console/ingestion-profiles/edit.tsx`
- `frontend/inspectah-ui/src/components/console/ProviderList.tsx`
- `frontend/inspectah-ui/src/components/console/IngestionProfileForm.tsx`

Config
- `config/providers.yml`
- `config/ingestion_profiles.yml`

Metrics & logs
- `app/metrics/ingestion_provider_metrics.py`
- `app/logging/ingestion_provider_logger.py`
- `infra/observability/dashboards/s31_provider_ingestion.json`

Migrations (nomes ilustrativos)
- `migrations/versions/31xx_add_provider_and_ingestion_profile.py`
- `migrations/versions/31xy_add_provider_fields_to_content_item.py`

Gates & ORR
- `bin/s31_g0_scope_and_baseline.sh`
- `bin/s31_g1_models_and_migrations.sh`
- `bin/s31_g2_provider_ingestion.sh`
- `bin/s31_g3_console_and_observability.sh`
- `bin/s31_g4_legacy_and_compat.sh`
- `bin/s31_g5_p2_p3_integration.sh`
- `bin/s31_orr.sh`

Saídas da sprint
- `out/evidence/S31_G0_scope/…`
- `out/evidence/S31_G1_models_and_migrations/…`
- `out/evidence/S31_G2_provider_ingestion/…`
- `out/evidence/S31_G3_console/…`
- `out/evidence/S31_G4_legacy/…`
- `out/evidence/S31_G5_p2_p3/…`
- `out/evidence/S31_ORR/…`
- `out/scorecards/S31_G0_scope_and_baseline.json`
- `out/scorecards/S31_G1_models_and_migrations.json`
- `out/scorecards/S31_G2_provider_ingestion.json`
- `out/scorecards/S31_G3_observabilidade.json`
- `out/scorecards/S31_G4_legacy_and_compat.json`
- `out/scorecards/S31_G5_p2_p3_integration.json`
- `out/scorecards/S31_ORR_overview.json`

---

### 3.7 Fecho do Capítulo 3

Com esta arquitetura e este filemap, a Sprint 31 deixa de ser apenas uma ideia e passa a ser um conjunto concreto de pastas, arquivos e responsabilidades. Provider-first ganha:

- modelos claros;
- serviços bem recortados;
- UI específica no Console;
- instrumentação mínima;
- pontos de integração definidos com Programas 2 e 3;
- um plano explícito de convivência com o legado.

Os próximos capítulos (Execução & Evidências) vão dizer **como** colocar tudo isso de pé, em qual ordem, com quais comandos e quais provas precisam ser guardadas para o Conselho bater o martelo em GO / GO_COM_RESSALVAS / NO_GO.

