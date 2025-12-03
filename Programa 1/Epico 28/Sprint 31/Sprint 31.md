# Inspectah — Sprint 31 (E28-S3) — Ingestão via Providers v1

## 0. TL;DR da Sprint 31

Sprint 31 é a sprint complementar do Épico E28 focada em **encaixar, de verdade, o modelo de omni-providers de notícia e social dentro do produto que já existe**. Ela faz o "retrofit" da camada de ingestão e operação (o que foi iniciado em E26, E27 e no começo de E28) para o novo desenho baseado em:

- `news_provider` como fonte agregadora de milhares de veículos;
- `social_provider` como fonte agregadora de menções/redes sociais;
- redução drástica de scrapers ad hoc como espinha dorsal;
- controle fino de perfis de ingestão (country/language/topic) e budgets;
- integração total com Console de Fontes e com a stack de observabilidade.

Ao final da Sprint 31, o Inspectah deve operar, em produção, com pelo menos **um news_provider e um social_provider reais plugados**, atendendo a um conjunto inicial de perfis críticos (por exemplo, BR/PT/política+economia), de forma estável, observável e governável via Console de Fontes, sem quebrar o que já vem das sprints anteriores.

---

## 1. Contexto e relação com o roadmap

### 1.1 Posição no roadmap

- Programa 1: Data Hub, Fontes, Ingestão & Operação 24/7.
- Programas 2–3: já assumem, conceitualmente, que a ingestão de notícias e social migra para o modelo de omni-providers.
- Sprints 26–30: construíram/vêm construindo o Console de Fontes, a base do Data Hub e partes da ingestão com o modelo anterior.
- **Sprint 31**: é a sprint que faz a ponte entre o mundo antigo (scraper-heavy, fonte a fonte) e o novo mundo (providers + fontes diretas de exceção), na prática.

Ela pertence ao Épico E28 (que trata de amadurecimento e consolidação de ingestão/plataforma), como a 3ª sprint desse épico (E28-S3), mas na numeração global do projeto ela é a Sprint 31.

### 1.2 Problema que a Sprint 31 resolve

Sem esta sprint, o código e a operação continuariam presos a:

- uma explosão de conectores específicos de site;
- dificuldade para escalar volume de fontes/países/idiomas;
- alto custo operacional de manter scrapers e adaptadores customizados;
- desalinhamento entre o que o roadmap diz (omni-providers) e o que o sistema de fato faz.

Sprint 31 resolve isso ao:

- introduzir o suporte real a `news_provider` e `social_provider` na camada de ingestão;
- adaptar o Console de Fontes para tratar providers como **fontes de primeira classe**;
- migrar parte das fontes existentes para o modelo de perfis de provider;
- garantir observabilidade, testes e gates que blindem essa nova rota.

---

## 2. Objetivos da Sprint 31

1. **Modelagem e persistência**: consolidar o modelo de dados de `Provider`, `Source` e `ContentItem` no código e no banco, incluindo tipos `news_provider` e `social_provider`, com migração segura a partir do estado pós-S30.
2. **Conectores de providers**: implementar adaptadores de ingestão para pelo menos:
   - um `news_provider` real (ex.: NewsData ou mediastack);
   - um `social_provider` real (via ferramenta de social listening ou API equivalente).
3. **Perfis de ingestão**: permitir configurar perfis de ingestão em nível de provider, com filtros (país, idioma, categorias, keywords) e budgets por perfil.
4. **Integração com fila/worker**: encaixar jobs de ingestão via provider na stack de fila/worker já usada (S26+), com tipos de job claros (`INGEST_NEWS_{profile}`, `INGEST_SOCIAL_{profile}`).
5. **Console de Fontes v2 (providers)**: expandir o Console de Fontes para:
   - exibir e configurar Providers;
   - exibir e configurar perfis de ingestão ligados a Providers;
   - mostrar métricas básicas por provider/profile.
6. **Observabilidade**: adicionar métricas e logs específicos para ingestão via providers e expô-los em painéis de saúde.
7. **Sanidade e compatibilidade**: garantir que fontes diretas existentes continuam funcionando e que o retrofit não quebra ingestão, Data Hub ou Programas 2–3.

---

## 3. Escopo e não-escopo

### 3.1 Escopo da Sprint 31

- Implementar e/ou consolidar no código o modelo de `Provider` com campos mínimos (id, name, kind, config, auth, limits, status).
- Implementar entidades e migrações necessárias para ligar `Provider` ↔ `Source` ↔ `ContentItem` (inclusive para fontes existentes que passam a ser derived_sources de providers).
- Implementar adaptador de ingestão para um news_provider escolhido.
- Implementar adaptador de ingestão para um social_provider (mesmo que em escopo reduzido, mas real).
- Implementar camada de **profiles de ingestão** (ex.: `BR_PT_HARD_NEWS`, `LATAM_ES_POLITICS`) com parâmetros configuráveis e associação a Providers.
- Integrar jobs de ingestão de providers à fila/worker (novos tipos de job com contratos claros) e ao scheduler.
- Evoluir o Console de Fontes para expor cadastro e configuração de Providers e perfis.
- Conectar ingestão via providers à stack de observabilidade (logs estruturados, métricas, painéis mínimos).

### 3.2 Fora de escopo (para futuras sprints)

- Multiplicar providers para outros domínios (dados de mercado etc.) além dos pilotos de notícia/social.
- Substituir todos os scrapers legados – apenas uma parte deles será migrada para provider ou marcada como candidata a desativação.
- Otimizações avançadas de custo (por exemplo, malha de priorização multi-provider, autoscaling de workers etc.).
- Exposição externalizada de dados de providers para clientes (licenciamento, compliance detalhado) – isso entra mais forte em sprints de produto/comercial.

---

## 4. Deliverables principais

### 4.1 Código e modelo de dados

- Modelos e migrations para `Provider` e campos adicionais em `Source` e `ContentItem`:
  - `provider` (FK opcional) em `Source`;
  - `provider` (FK opcional) em `ContentItem`;
  - enums/constantes para `provider_kind` (news_provider, social_provider, etc.).
- Repositórios/serviços para CRUD básico de Providers.

### 4.2 Conectores de providers

- Módulo `news_provider_client` capaz de:
  - autenticar com provider;
  - chamar endpoints de notícia com filtros (country, language, category, keywords, date range);
  - tratar paginação e limites;
  - normalizar resposta em uma estrutura intermediária `RawNewsItem`.
- Módulo `social_provider_client` capaz de:
  - autenticar com provider social;
  - chamar endpoints de posts/menções com filtros relevantes;
  - normalizar em `RawSocialItem`.
- Funções de conversão `RawNewsItem` → `ContentItem` e `RawSocialItem` → `ContentItem` com dedupe.

### 4.3 Jobs de ingestão e scheduling

- Tipos de job definidos:
  - `INGEST_NEWS_{profile}`;
  - `INGEST_SOCIAL_{profile}`.
- Implementação de workers para esses jobs:
  - leitura de config de perfil (provider, filtros, limites);
  - chamada ao client do provider;
  - normalização, dedupe, persistência;
  - logging e métricas.
- Configuração mínima do scheduler (ex.: cronjobs ou equivalente) para:
  - rodar perfis críticos (ex.: BR/PT/política+economia) com frequência X;
  - rodar perfis secundários com frequência maior.

### 4.4 Console de Fontes v2 (providers)

- Tela/fluxo para cadastro/edição de Providers:
  - nome, tipo, config padrão, status;
  - placeholders seguros para auth (sem exibir secrets em claro).
- Tela/fluxo para cadastro/edição de perfis de ingestão:
  - vínculo com provider;
  - filtros (país, idioma, categorias, keywords);
  - frequência e budgets;
  - botão de "rodar agora" (trigger manual) para testes.
- Integração visual com status/métricas por profile (última execução, itens trazidos, erros).

### 4.5 Observabilidade

- Logs estruturados por job de provider contendo:
  - provider, profile, parâmetros de chamada;
  - contagem de itens recebidos, novos, duplicados;
  - tempo de execução e erros.
- Métricas básicas:
  - itens por minuto/hora por provider/profile;
  - taxa de erro por provider/profile;
  - backlog de jobs de provider;
  - consumo aproximado de quotas de provider.
- Painéis iniciais na stack de observabilidade para acompanhar ingestão via providers.

### 4.6 Evidências e scorecards

- Pasta `out/evidence/S31_*` com logs e artefatos de execução dos gates.
- Scorecards em `out/scorecards/S31_*.json` para cada gate principal (G0..G3, por exemplo), registrando PASS/FAIL, métricas e links para evidências.

---

## 5. Gates e critérios de GO/NO-GO

### 5.1 G0 — Escopo e baseline

- Documento de escopo da Sprint 31 (este + Capítulo 1 específico) validado.
- Lista de providers e perfis pilotos decididos (pelo menos 1 news_provider + 1 social_provider, com recorte BR/PT bem definido).
- Plano de migração incremental acordado (quais fontes antigas migram para perfis de provider nesta sprint, quais ficam para depois).

### 5.2 G1 — Modelo de dados e migrações

- Migrations para `Provider` e campos em `Source`/`ContentItem` aplicadas sem perda de dados.
- Scripts de migração populando Providers iniciais e ligando Sources relevantes.
- Testes automatizados cobrindo o modelo de dados básico.

### 5.3 G2 — Ingestão via providers (funcional)

- Jobs `INGEST_NEWS_{profile}` e `INGEST_SOCIAL_{profile}` executando fim-a-fim em ambiente de teste:
  - trazendo itens reais de provider;
  - gerando ContentItems canônicos;
  - registrando logs e métricas.
- Deduplicação funcionando (sem explosão de duplicatas quando rodar mais de uma vez).

### 5.4 G3 — Console de Fontes v2 + Observabilidade

- Console de Fontes exibindo e permitindo editar Providers e perfis.
- Capacidade de disparar ingestão manual de um perfil via Console e ver o resultado nas métricas.
- Painel de observabilidade mostrando ingestão via providers (métricas-chave por provider/profile).

### 5.5 Gx — Sanidade com Programas 2–3

- Confirmação de que Programas 2–3 (claims, grafos, blocos) continuam funcionando com ContentItems oriundos de providers (mesma estrutura esperada).
- Amostras de claims e blocos gerados a partir de conteúdo vindo de providers.

GO da sprint exige todos os gates críticos (G0–G3 + sanidade P2/P3) em PASS.

---

## 6. Filemap (nível sprint)

### 6.1 Código e modelo

- `app/models/provider.py` (ou equivalente): modelo Provider.
- `app/models/source.py`: ajustes para FK opcional para Provider.
- `app/models/content_item.py`: ajustes para FK opcional para Provider.
- `migrations/versions/XXXX_s31_providers.py`: migrations desta sprint.
- `app/ingestion/providers/news_provider_client.py`: client de news_provider.
- `app/ingestion/providers/social_provider_client.py`: client de social_provider.
- `app/ingestion/jobs/ingest_news.py`: worker/job para `INGEST_NEWS_*`.
- `app/ingestion/jobs/ingest_social.py`: worker/job para `INGEST_SOCIAL_*`.

### 6.2 Console de Fontes

- `frontend/inspectah-ui/src/features/sources/ProvidersPage.tsx`;
- `frontend/inspectah-ui/src/features/sources/ProfilesPage.tsx`;
- componentes compartilhados para cards/listas de providers e perfis.

### 6.3 Observabilidade

- `app/ingestion/logging.py` ou equivalente: helpers de logs estruturados para jobs de providers.
- `app/ingestion/metrics.py`: definição de métricas de ingestão via providers.
- Configs de dashboards em `infra/observability/dashboards/s31_providers_*.json`.

### 6.4 Gates e scripts

- `bin/s31_g0_scope_and_baseline.sh`;
- `bin/s31_g1_models_and_migrations.sh`;
- `bin/s31_g2_provider_ingestion.sh`;
- `bin/s31_g3_console_and_observability.sh`;
- `bin/s31_bundle.sh` para zipar evidências/scorecards da sprint.

### 6.5 Docs

- `docs/sprint_31_capitulo_1_contexto.md`;
- `docs/sprint_31_capitulo_2_gates_e_scorecards.md`;
- `docs/sprint_31_capitulo_3_filemap.md` (convergente com esta seção);
- `docs/sprint_31_capitulo_4_execucao_e_evidencias.md`.

---

## 7. Plano de execução (alto nível)

### Fase 1 — Preparação (D0–D1)

- Refinar e congelar escopo da sprint (este doc + Capítulo 1).
- Escolher providers concretos para piloto (news + social) e definir perfis iniciais.
- Planejar estratégias de migração de fontes existentes.

### Fase 2 — Modelo e migrações (D1–D3)

- Implementar modelo Provider e migrations.
- Ajustar Source/ContentItem.
- Escrever e rodar testes de modelo.

### Fase 3 — Clients e jobs (D3–D6)

- Implementar `news_provider_client` e `social_provider_client`.
- Implementar jobs `INGEST_NEWS_*` e `INGEST_SOCIAL_*`.
- Integrar com fila/worker.
- Rodar ingestão em ambiente de teste com perfis-piloto.

### Fase 4 — Console & observabilidade (D5–D8)

- Evoluir o Console de Fontes para suportar providers e perfis.
- Integrar logs e métricas dos jobs de provider.
- Construir painel mínimo de ingestão via providers.

### Fase 5 — Validação integrada (D8–D10)

- Rodar gates G0–G3.
- Validar sanidade com Programas 2–3 (claims e blocos gerados a partir de conteúdo vindo via providers).
- Ajustar arestas.

---

## 8. Riscos e mitigação

### 8.1 Dependência de providers externos

Risco: instabilidade ou dificuldade de integração com o provider escolhido.

Mitigação:

- encapsular provider em client isolado;
- preparar fallback mínimo para lidar com indisponibilidade temporária;
- manter testes isolados e bem instrumentados.

### 8.2 Quebra de ingestão existente

Risco: migrations ou mudanças de código quebrarem ingestão de fontes diretas.

Mitigação:

- testes de regressão sobre fluxos já existentes;
- validação em ambiente de staging com fontes antigas + novas.

### 8.3 Explosão de volume/custo

Risco: configuração ruim de perfis gera ingestão excessiva.

Mitigação:

- budgets fortes por perfil;
- métricas e alertas de volume;
- perfis-piloto bem restritos na sprint.

---

## 9. Critério de sucesso da Sprint 31

Sprint 31 é considerada sucesso quando:

1. Providers de notícia e social estão modelados e armazenados no banco, com migrações aplicadas sem problemas.
2. Pelo menos um news_provider e um social_provider reais estão integrados, trazendo conteúdo em perfis-piloto.
3. ContentItems gerados via providers são indistinguíveis (do ponto de vista de Programas 2–3) dos itens vindos das fontes antigas.
4. Console de Fontes permite cadastrar e operar providers e perfis de ingestão, e é usado para acionar ingestão-piloto.
5. Métricas e logs de ingestão via providers são visíveis e úteis em painéis de observabilidade.
6. Gates G0–G3 estão em PASS, com evidências em `out/evidence/S31_*` e scorecards em `out/scorecards/S31_*.json`.

A partir desse patamar, sprints seguintes podem expandir o número de providers, perfis, países, idiomas e temas, sem mudanças estruturais no sistema de ingestão.

