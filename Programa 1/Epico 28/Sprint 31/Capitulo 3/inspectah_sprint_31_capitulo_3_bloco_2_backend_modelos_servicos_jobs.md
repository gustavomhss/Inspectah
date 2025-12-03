# Inspectah — Sprint 31 (E28-S3)
## Capítulo 3 — Bloco 2: Backend — Modelos, Serviços & Jobs

### 3.4 Objetivo deste bloco

Este bloco desce um nível na arquitetura da S31 para responder:

- quais **modelos** de backend sustentam o provider-first;
- quais **serviços** orquestram ingestão, normalização e dedupe;
- como os **jobs** e o **scheduler** transformam perfis em execuções reais;
- como isso tudo convive com o que já existe no repositório.

É o mapa que o Codex precisa seguir para não transformar provider-first em um amontoado de scripts soltos.

---

### 3.5 Modelos centrais da S31

A S31 se ancora em três grupos de modelos:

1. **Quem fornece os dados** → `Provider`
2. **Como usamos esses dados** → `IngestionProfile`
3. **O que guardamos de fato** → `ContentItem` (ajustado) + mapeamento em `Source`

#### 3.5.1 Modelo `Provider`

Papel: representar, dentro do Inspectah, cada provedor externo de dados de notícia ou social.

Campos principais (nomes ilustrativos, adaptar ao padrão atual do ORM):

- `id`: chave primária interna.
- `slug`: identificador curto estável (ex.: `newsdata_global`, `social_radar_br`).
- `type`: enum (`NEWS`, `SOCIAL`).
- `base_url`: endpoint raiz da API.
- `regions_supported`: lista ou JSON com regiões/códigos de país suportados.
- `languages_supported`: lista ou JSON com idiomas suportados.
- `categories_supported`: lista ou JSON com categorias/temas principais.
- `status`: enum (`ACTIVE`, `INACTIVE`, `EXPERIMENTAL`).
- `meta`: JSON com detalhes específicos (limites de rate, paginação, anomalias conhecidas, etc.).

Requisitos arquiteturais:

- Nenhuma lógica de negócio forte deve ficar acoplada diretamente ao modelo; ela vive em serviços.
- Provider precisa ser estável: raras alterações, bem documentadas, porque mexer aqui afeta tudo.

#### 3.5.2 Modelo `IngestionProfile`

Papel: definir **recortes de ingestão** em cima de um provider. É a unidade de operação e de custo da S31.

Campos principais:

- `id`: chave primária.
- `name`: nome interno claro (ex.: `BR_PT_HARD_NEWS`, `LATAM_ES_POLITICS`, `SOCIAL_BR_POLITICA_TIMELINE`).
- `provider_id`: FK para `Provider`.
- `filters`: JSON com filtros de ingestão, incluindo combinações de:
  - `countries`, `languages`;
  - `categories` (política, economia, saúde, etc.);
  - `keywords` (listas de termos-chave);
  - `sources` (quando suportado, lista de veículos específicos);
  - janelas temporais padrão (ex.: “últimas 24h” por run).
- `schedule`: representação da frequência (cron ou enum como `HOURLY`, `EVERY_15_MIN`, `DAILY`).
- `budget_limit_calls`: limite de chamadas por período (ex.: dia).
- `status`: (`ACTIVE`, `PAUSED`, `EXPERIMENTAL`).
- `meta`: JSON com flags específicas (ex.: tolerância a erro, nota sobre prioridade editorial).

Requisitos arquiteturais:

- `IngestionProfile` deve ser a porta de entrada **única** para ingestão via provider.
- Qualquer job em fila precisa ser rastreável até um `IngestionProfile` real.

#### 3.5.3 Ajustes em `ContentItem`

Papel: continuar sendo a unidade canônica de conteúdo, agora com proveniência provider-first.

Novos campos esperados:

- `provider_id`: FK opcional para `Provider` (null para conteúdos de fontes legadas sem provider).
- `ingestion_profile_id`: FK opcional para `IngestionProfile` (idem).
- `external_id`: identificador do item no provider (quando disponível).
- `source_domain`: domínio do veículo (ex.: `g1.globo.com`, `nytimes.com`).
- `ingested_at`: timestamp da ingestão pelo Inspectah.

Requisitos de integridade:

- Para itens de provider:
  - `provider_id`, `ingestion_profile_id`, `external_id` (quando disponível) e `ingested_at` **não podem** estar vazios.
- Índices sugeridos:
  - `(provider_id, external_id)` para lookup rápido;
  - `(ingestion_profile_id, ingested_at)` para métricas por perfil;
  - `(source_domain, published_at)` para debugging e consultas.

#### 3.5.4 Ajustes em `Source`

Papel: continuar representando fontes lógicas do ponto de vista do Inspectah (veículos, órgãos oficiais, etc.), agora podendo ser associadas a domínios vindo de providers.

Ajustes típicos:

- garantir que `Source` consiga mapear domínios (`source_domain`) a entidades internas (ex.: `GLOBO_G1`), inclusive quando o dado entrar via provider;
- opcionalmente, ligar `Source` a `Provider`/`IngestionProfile` quando houver relação estável.

---

### 3.6 Serviços de ingestão, normalização e dedupe

Com os modelos no lugar, a S31 organiza a lógica em serviços especializados. Objetivo: evitar spaghetti de “chamar provider, parsear JSON, salvar no banco” espalhado.

Diretório sugerido (ajustar ao padrão do repo):

- `app/ingestion/providers/…`
- `app/ingestion/normalizer.py`
- `app/ingestion/dedupe_service.py`
- `app/ingestion/profile_runner.py`

#### 3.6.1 Clientes de provider

Arquivos típicos:

- `app/ingestion/providers/base_client.py`
- `app/ingestion/providers/news_provider_client.py`
- `app/ingestion/providers/social_provider_client.py`

Responsabilidades do `base_client`:

- encapsular autenticação, headers, retries e backoff;
- oferecer operações genéricas como:
  - `request(endpoint, params) -> dict` com tratamento padronizado de erros;
  - conversão de códigos HTTP e erros em exceções do domínio (ex.: `RateLimitError`, `AuthError`).

Responsabilidades dos clients específicos (`news_provider_client`, `social_provider_client`):

- implementar métodos de alto nível como:
  - `fetch_news(profile: IngestionProfile, window: TimeWindow) -> list[RawNewsItem]`;
  - `fetch_social(profile: IngestionProfile, window: TimeWindow) -> list[RawSocialItem]`;
- traduzir filtros (`filters` do profile) em parâmetros da API do provider;
- lidar com paginação, limites por request e campos específicos.

#### 3.6.2 Normalização (`normalizer`)

Papel: transformar respostas brutas de cada provider em uma estrutura interna **consistente**, independente do fornecedor.

Responsabilidades principais:

- receber listas de `RawNewsItem`/`RawSocialItem`;
- mapear campos de interesse para o modelo `ContentItem` (título, corpo, autor, URLs, timestamps, tags);
- preencher proveniência (`provider_id`, `ingestion_profile_id`, `external_id`, `source_domain`, `ingested_at`);
- chamar o `dedupe_service` antes de persistir.

Requisitos de qualidade:

- não vazar detalhes de provider para o resto do sistema (quem conversa com ContentItem não deve se importar com qual provider trouxe);
- manter mapeamentos específicos de cada provider bem localizados e testáveis.

#### 3.6.3 Serviço de dedupe (`dedupe_service`)

Papel: evitar que o mesmo conteúdo crie vários ContentItems.

Estratégia minimalista esperada na S31:

- para itens com provider:
  - usar `(provider_id, external_id)` como chave primária de dedupe quando `external_id` for confiável;
  - complementar com hash de URL ou de corpo (trechos) quando necessário.

- para itens sem `external_id` estável:
  - usar combinação de `source_domain + title + published_at` (com normalização básica);
  - aplicar heurísticas simples para títulos muito semelhantes no mesmo período.

Fluxo:

1. Recebe “candidato a ContentItem normalizado”.
2. Procura no banco por item equivalente pelas chaves definidas.
3. Se encontrar:
   - atualiza campos não-críticos (ex.: meta, contadores, tags adicionais);
   - não cria novo registro.
4. Se não encontrar:
   - cria novo ContentItem.

Dedupe não precisa ser perfeito na S31, mas precisa ser **bom o suficiente** para não gerar explosão de duplicatas óbvias.

#### 3.6.4 Runner de perfil (`profile_runner`)

Papel: é o “motor” que toma um `IngestionProfile` e executa um ciclo de ingestão.

Responsabilidades:

- carregar o perfil e verificar se está `ACTIVE`;
- validar se há espaço de budget (chamadas restantes para o período);
- determinar a janela temporal a ser buscada (ex.: últimas X horas);
- chamar o client apropriado (`news_provider_client` ou `social_provider_client`);
- passar os itens brutos para o `normalizer`;
- registrar métricas do run (calls, itens brutos, ContentItems criados, erros);
- serializar logs estruturados com parâmetros e resultados.

Interface típica (conceitual):

```python
run_profile(profile_id: str, window: TimeWindow | None = None) -> RunResult
```

`RunResult` inclui contagens, erros e metadados usados em métricas e scorecards.

---

### 3.7 Jobs, fila e scheduler

A S31 não inventa uma nova infraestrutura de jobs; ela usa o padrão já adotado no projeto (fila + workers), mas define contratos claros.

Diretórios/arquivos sugeridos:

- `app/jobs/provider_ingestion.py`
- `app/jobs/scheduler.py`

#### 3.7.1 Scheduler

Papel: traduzir perfis ativos em jobs na fila.

Responsabilidades:

- periodicamente (por cron ou serviço contínuo):
  - buscar `IngestionProfile` com `status = ACTIVE`;
  - avaliar se chegou a hora de rodar (com base em `schedule` e última execução);
  - enfileirar jobs do tipo `INGEST_PROFILE::<profile_id>`;
- respeitar políticas globais (ex.: máximo de perfis simultâneos, ordem de prioridade por tipo de conteúdo).

Requisitos:

- logar perfis agendados e motivos (para debugging);
- evitar “tempestade de jobs” na virada de janelas, respeitando limites globais.

#### 3.7.2 Workers & job `INGEST_PROFILE`

Papel: executar o trabalho pesado para cada perfil individual.

Fluxo típico do job:

1. Recebe mensagem da fila com `profile_id` e, opcionalmente, parâmetros de janela (`from`, `to`).
2. Carrega o `IngestionProfile` correspondente.
3. Chama `profile_runner.run_profile(profile_id, window)`.
4. Atualiza metadados de última execução do perfil (timestamp, contagens básicas, status).
5. Registra logs estruturados (para G2 e G3).

Requisitos de robustez:

- tratamento decente de erros de provider (rate limit, auth, timeouts);
- retries com backoff e registro de falhas permanentes;
- não explodir o worker se provider estiver instável — marcar run como falho, mas manter serviço vivo.

---

### 3.8 Convivência com fluxo legado no backend

Fluxos legados (RSS, APIs diretas, scrapers específicos) continuam existindo, mas sob controle.

Diretório/arquivos típicos:

- `app/ingestion/rss_legacy.py`
- `app/ingestion/scrapers/…`
- `app/jobs/legacy_ingestion.py`
- `app/ingestion/legacy_adapter.py` (novo na S31)

Papel do `legacy_adapter` na S31:

- expor uma lista programática de fluxos legados críticos;
- fornecer utilitários para rodar sanity de ingestão legada (G4);
- mapear, quando possível, fontes legadas a potenciais `IngestionProfile` que possam substituir ou complementar.

Garantia mínima:

- migrations e novos serviços **não quebram** esses fluxos;
- G4 roda jobs legados selecionados e salva logs para comparação.

---

### 3.9 Fecho do Bloco 2

Com os modelos (`Provider`, `IngestionProfile`, `ContentItem` ajustado), serviços (`providers_client`, `normalizer`, `dedupe_service`, `profile_runner`) e jobs (`scheduler`, `INGEST_PROFILE`) bem definidos, o backend da Sprint 31 ganha uma forma clara:

- qualquer ingestão via provider passa pelo mesmo caminho previsível;
- proveniência deixa de ser detalhe e vira parte do modelo;
- dedupe deixa de ser gambiarra e vira serviço explícito;
- budget e métricas se acoplam naturalmente ao fluxo de execução.

Nos próximos blocos do Capítulo 3, o foco muda para frontend (Console de Fontes v2), observabilidade e filemap completo, amarrando esse backend ao resto do sistema.

