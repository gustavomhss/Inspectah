# Inspectah — Programa 1 v4
## Data Hub, Fontes, Ingestão & Operação 24/7

> Versão v4 — alinhada ao Roadmap Macro v4, DNA v2, Sprint Playbook v2 e Lessons Learned. Compatível com o estado atual do projeto (S1–S29 já executadas) e preparada para alimentar diretamente os Programas 2, 3 e 4.

---

## 0. Papel do Programa 1 no Inspectah

O Programa 1 é o **aparelho circulatório** do Inspectah. Tudo o que o sistema sabe sobre o mundo começa aqui, como conteúdo bruto, e precisa entrar de forma:

- **confiável** (sem fontes fantasma, scraping tosco ou formatos imprevisíveis),
- **normalizada** (modelo canônico de Provider/Source/ContentItem),
- **observável** (métricas, logs, trilha de ingestão),
- **operável 24/7** (fila/worker, retries, backfill, controle fino de fontes).

Se o Programa 1 falha, o restante do sistema (claims, lógica, Truth‑DB, memória, produtos) fica construído em cima de um pântano. Este Programa existe para garantir que **isso não aconteça**.

---

## 1. Visão

Construir um **Data Hub 24/7** que torna irrelevante o "como" o conteúdo chegou (news provider, social provider, API oficial, dataset batch, scraper de exceção) e centraliza o "o que" chegou em um modelo único, rastreável e observável.

O Programa 1 entrega um ambiente onde:

1. **Fontes** são entidades explícitas (Provider, Source), com estados, contratos e configurações claros.
2. **Conteúdos** são sempre representados como **ContentItems canônicos**, com metadados ricos (fonte, tempo, idioma, localização, tipo, qualidade).
3. **Ingestão** funciona 24/7 com fila/worker, retries, backoff e backfill, em cima de jobs previsíveis.
4. **Operadores** têm um **Console de Fontes** que permite operar o sistema sem tocar código.
5. **Observabilidade** permite diagnosticar problemas em minutos, não em semanas.

---

## 2. Objetivos do Programa 1

1. **Unificar modelos de entrada**
   - Transformar todas as entradas externas (news APIs, social, oficiais, batch, scrapers) em um único modelo de dados (ContentItem) com metadados consistentes.

2. **Garantir ingestão contínua e confiável**
   - Construir pipelines de ingestão resilientes, com filas, workers e políticas de retries/backoff, capazes de operar 24/7 sem supervisão manual constante.

3. **Tornar o sistema operável via Console de Fontes**
   - Permitir que operadores liguem/desliguem fontes, mudem frequência de coleta, vejam incidentes e tomem decisões sem depender de engenheiros.

4. **Fornecer metadados ricos para Programas 2 e 3**
   - Garantir que Programas 2 (claims & sinais) e 3 (lógica & Truth‑DB) tenham informação suficiente para sanidade lógica, contexto de fonte e caracterização de Experiências.

5. **Dar visibilidade de saúde e custos de ingestão**
   - Entregar painéis e métricas de ingestão por fonte, país, domínio, tipo de conteúdo, para permitir decisões de escopo e custo.

---

## 3. Escopo macro do Programa 1

O Programa 1 cobre **apenas** os aspectos abaixo. Qualquer coisa fora desta lista deve ser explicitamente rejeitada ou tratada como Programa futuro.

1. **Modelagem de Provider/Source/ContentItem**
   - Esquemas, relacionamentos, estados, tipos de conteúdo, contratos de ingestão.

2. **Conectores de ingestão**
   - News providers, social providers, APIs oficiais, ingestão batch (CSV/JSON/parquet/etc.), scrapers de exceção com monitoramento.

3. **Infra de ingestão assíncrona**
   - Fila, workers, agendamento, retries, backoff, dead letters, backfill.

4. **Observabilidade de ingestão**
   - Logs estruturados, métricas, painéis, alertas, drill‑down por fonte.

5. **Console de Fontes e operação 24/7**
   - UI + APIs para gestão de fontes, perfis de coleta, incidentes e histórico.

**Fora do escopo:** qualquer tipo de interpretação semântica, extração de claims, classificação, construção de ClaimGraph, decisões de verdade/contestação, lógica formal e memória evolutiva. Tudo isso começa no **Programa 2** e é aprofundado em **Programas 3 e 4**.

---

## 4. Macro‑épicos do Programa 1

Nesta seção, usamos rótulos locais `P1‑E#`. O mapeamento para a numeração global de épicos (E1, E2, …) é tratado nos docs de roadmap.

### P1‑E1 — Modelo canônico de Provider/Source/ContentItem

**Objetivo:** estabelecer um modelo de dados único e estável para tudo que entra no Inspectah.

**Entregas principais:**

1.
   - **Provider**: entidade que representa um agregador ou provedor de dados (ex.: NewsData, provedor de social, órgão oficial com múltiplas APIs).
   - **Source**: unidade de configuração específica dentro de um Provider (ex.: "NewsData — notícias Brasil economia", "SocialProvider — tweets sobre tema X").
2.
   - Representação unificada de itens de conteúdo vindos de qualquer Source.
   - Campos obrigatórios (ID, Source, timestamps, título, corpo, URL, tipo, idioma, país, hash de conteúdo, etc.).
3.
   - Estados de Provider/Source (ativo, pausado, deprecado, erro, etc.).
   - Campos para contratos de ingestão (limites de rate, janelas de tempo, tipos de conteúdo permitidos).

**Critérios de pronto:**

- Esquemas definidos, versionados e documentados.
- Migração inicial aplicada em ambiente de desenvolvimento.
- Exemplo de ContentItems produzidos a partir de pelo menos 2 tipos de fontes diferentes.

---

### P1‑E2 — Ingestão de notícias via news providers

**Objetivo:** ligar o Inspectah a news providers consolidados, cobrindo países/idiomas/temas prioritários.

**Entregas principais:**

1. **Conectores para news providers** selecionados (ex.: NewsData, NewsAPI ou equivalente):
   - Módulos de integração com autenticação, paginação e filtros.
2. **Profiles de ingestão** por país/idioma/tema/domínio:
   - ex.: "Brasil / PT / Economia", "LatAm / ES / Política", etc.
3. **Normalização para ContentItem**:
   - mapeamento de campos da API externa para campos canônicos;
   - cálculo de hash de conteúdo para deduplicação.
4. **Mecanismo de dedupe**:
   - evitar múltiplas entradas idênticas/diferentes apenas em metadado supérfluo.

**Critérios de pronto:**

- Pelo menos um conjunto de profiles de ingestão para Brasil/LatAm configurado.
- Ingestão periódica funcionando em ambiente de teste com logs e métricas visíveis.
- ContentItems chegando com metadados completados e dedupe básico ativo.

---

### P1‑E3 — Ingestão social via social providers

**Objetivo:** trazer sinais de redes sociais (posts, menções, threads relevantes) via social providers.

**Entregas principais:**

1. **Conectores com social providers** (ex.: plataformas de social listening):
   - integração com APIs para coleta de posts, menções, comentários, metadados de engajamento.
2. **Profiles sociais**:
   - por hashtag, termo, conta, lista curada, idioma, país.
3. **Normalização para ContentItem**:
   - representação unificada para posts: conteúdo textual, links, anexos, métricas básicas.
4. **Tratamento de volume e limites de rate**:
   - estratégia de sampling, priorização, filtros mínimos.

**Critérios de pronto:**

- Pelo menos 1–2 domínios temáticos com profiles sociais ativos.
- ContentItems sociais presentes no Data Hub, com distinção clara de origem (tipo de Source) e uso futuro marcado.

---

### P1‑E4 — Ingestão de fontes oficiais & batch

**Objetivo:** conectar o Inspectah a fontes oficiais e datasets batch relevantes.

**Entregas principais:**

1. **Conectores para APIs oficiais** (BC, IBGE, órgãos reguladores, etc.):
   - coleta de séries temporais, tabelas, documentos oficiais.
2. **Ingestão de arquivos batch**:
   - suporte a formatos CSV/JSON/Parquet, com pipelines de carga periódica.
3. **Versionamento de datasets**:
   - forma de registrar versões de datasets com timestamps claros.
4. **Normalização para ContentItem ou entidades auxiliares**:
   - quando couber, representar eventos/dados relevantes como ContentItems; quando não, vincular a ContentItems via referências.

**Critérios de pronto:**

- Pelo menos 2 fontes oficiais estratégicas integradas.
- Pipeline batch funcionando em ambiente de teste, com logs e métricas.

---

### P1‑E5 — Scrapers de exceção & proteção contra quebra

**Objetivo:** lidar com fontes sem API, de forma controlada e segura.

**Entregas principais:**

1. **Framework mínimo de scrapers de exceção**:
   - componentes reutilizáveis para crawling, parsing, detecção de mudanças de layout.
2. **Monitoramento de fragilidade**:
   - métricas de erro por scraper, detecção de quebra de layout.
3. **Políticas de uso de scrapers**:
   - critérios para autorizar um scraper (falta de API, importância da fonte, limites de acesso, respeito a robots.txt onde aplicável).

**Critérios de pronto:**

- Pelo menos um scraper de exceção configurado como prova de conceito.
- Indicadores de fragilidade e quebra visíveis em painéis.

---

### P1‑E6 — Infra de fila/worker & scheduling

**Objetivo:** padronizar a forma como jobs de ingestão são executados, escalonados e reprocessados.

**Entregas principais:**

1. **Escolha e setup da stack de fila/worker** (ex.: Celery + Redis ou similar).
2. **Modelo de job de ingestão**:
   - campos, prioridades, payloads, estratégia de retries/backoff.
3. **Dead letters e backfill**:
   - filas de jobs que falharam permanentemente;
   - mecanismos para reprocessar períodos de tempo (ex.: "refaça ontem para esta fonte").
4. **Scheduling**:
   - agendamento de jobs recorrentes por Source/profile (cron interno ou serviço de scheduling externo).

**Critérios de pronto:**

- Pelo menos 2 tipos de job (news/social/batch) rodando via fila.
- Dashboards básicos de fila (fila atual, taxa de sucesso/erro, latência de processamento).

---

### P1‑E7 — Observabilidade da ingestão & saúde de fontes

**Objetivo:** tornar a ingestão transparente e diagnosticável.

**Entregas principais:**

1. **Logs estruturados** para ingestão:
   - por job, por Source, com correlação para ContentItems gerados.
2. **Métricas**:
   - taxa de itens por Source, erros por tipo, latência por job, backlog de fila.
3. **Dashboards**:
   - visão macro (volume por tipo de fonte, erros globais);
   - visão por Source (saúde individual, incidentes recentes).
4. **Alertas**:
   - thresholds para taxa de erro, ausência de dados, explosões de volume, etc.

**Critérios de pronto:**

- Pelo menos um conjunto de dashboards funcionais em stack de observabilidade.
- Alertas mínimos configurados para fontes críticas.

---

### P1‑E8 — Console de Fontes & Operação 24/7

**Objetivo:** dar ao time de operação uma UI para controlar ingestão sem editar código.

**Entregas principais:**

1. **UI de Fontes**:
   - listar Providers e Sources, com estados, últimas execuções, erros recentes;
   - filtros por tipo, país, idioma, tema.
2. **Ações operacionais**:
   - ativar/pausar fontes;
   - ajustar frequência de coleta;
   - solicitar backfill para janelas de tempo específicas;
   - abrir e registrar incidentes.
3. **Histórico e audit trail**:
   - registrar quem mudou o quê, quando, com que justificativa.
4. **APIs do Console de Fontes**:
   - para automação e integração com outros sistemas internos.

**Critérios de pronto:**

- Operadores conseguem, via Console, ligar/desligar fontes, ajustar perfis e solicitar reprocessamentos.
- Mudanças são registradas com audit trail.

---

## 5. Interfaces com Programas 2, 3 e 4

### 5.1 Com Programa 2 — Interpretação, Claims, Entidades & Sinais

- P2 consome:
  - ContentItems canônicos;
  - metadados de fonte (Provider/Source, país, idioma, tipo);
  - timestamps de publicação/coleta;
  - indicadores básicos de saúde de fonte.
- P1 deve garantir que:
  - ContentItems estejam em formato estável e versionado;
  - campos essenciais para interpretação (texto, título, URL, idioma, país) sejam sempre preenchidos ou marcados como ausentes;
  - seja possível reproduzir "de onde veio" um ContentItem.

### 5.2 Com Programa 3 — Truth‑DB, Sistema de Blocos, Lógica & Memória

- **E40.5** consome do Programa 1, indireta ou diretamente:
  - informações de tempo (publicação, coleta, validade);
  - metadados de origem (tipo de fonte, confiabilidade, histórico de incidentes);
  - que auxiliam sanidade lógica (datas possíveis, intervalos, repetição de eventos).

- **P3‑E8.5 (Memória Evolutiva)** usa metadados de fonte para:
  - caracterizar Experiências por mix de fontes envolvidas;
  - correlacionar padrões de erro de fonte com tipos de narrativa/manipulação.

### 5.3 Com Programa 4 — Exposição, Produtos, APIs & Uso Responsável

- P4 pode usar dados de Programa 1 para:
  - mostrar saúde de fontes na UI (Console de Fontes, painéis públicos ou semi‑públicos);
  - expor histórico de ingestão de um caso/tema (quais fontes participaram, em que momentos);
  - dar contexto sobre confiabilidade operacional de fontes em relatórios.

---

## 6. Restrições e não‑objetivos

1. P1 não faz interpretação semântica nem atribui estados de verdade;
2. P1 não constrói ClaimGraph, não calcula sinais e não roda logic engines;
3. P1 não gerencia políticas de verdade/contestação (isso é P3 + E40.5);
4. P1 não define produtos finais nem APIs externas de verdade (isso é P4);
5. P1 não constrói infraestrutura de observabilidade do zero — ele se integra a uma stack existente.

---

## 7. Critérios macro de "pronto" do Programa 1

Consideramos o Programa 1 "pronto" (em sua v1 estruturante) quando:

1. **Modelo canônico** de Provider/Source/ContentItem estiver estável e em uso por todas as ingestões;
2. **Fontes principais** (news providers, social providers, algumas fontes oficiais) estiverem plugadas e gerando ContentItems em produção;
3. **Fila/worker** estiverem operando ingestão 24/7 com retries, backoff, dead letters e backfill básico;
4. **Observabilidade** permitir responder rapidamente "o que quebrou, onde, quando e por quê" na ingestão;
5. **Console de Fontes** permitir ao time de operação controlar ingestão sem intervenção de engenharia;
6. Programas 2, 3 e 4 declararem que recebem de P1 **dados suficientes e confiáveis** para seus próprios objetivos (interpretar, verificar, registrar verdade, expor produtos).

A partir daqui, qualquer sprint futura que alegar depender de "ingestão" ou "fontes" deve se apoiar nesse Programa como base, em vez de reinventar pipelines.

