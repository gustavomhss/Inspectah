# Inspectah — Sprint 31 (E28-S3)
## Capítulo 1 — Contexto, Problemas e Encaixe no Roadmap

### 1.1. Por que a Sprint 31 existe

A Sprint 31 é a peça que faltava para alinhar o código, a operação e o roadmap em torno de uma verdade única:

> A ingestão de notícias e social do Inspectah passa a ser **provider-first**, com scrapers como exceção controlada.

Até a S30, o projeto está num estágio híbrido:

- o **roadmap macro** e o **Programa 1 v3** já assumem um mundo onde o Data Hub é abastecido por `news_providers` e `social_providers`, com perfis de ingestão configuráveis, budgets e observabilidade decente;
- o **código e a operação** ainda carregam muito da herança de fontes diretas e scrapers individuais, com o Console de Fontes pensando em "fonte = site" e não em "fonte = perfil de provider";
- Programas 2 e 3 já foram desenhados supondo uma ingestão limpa, canônica e bem recortada, mas ainda não existe uma trilha 100% confiável dizendo como cada ContentItem entrou no sistema.

A Sprint 31 existe para fechar essa curva. Ela não inventa nada do zero: pega decisões já consolidadas no Roadmap Macro e nos Programas 1–4 e faz o encaixe real no código e na operação. Quando a S31 terminar, o Inspectah precisa conseguir responder sem gaguejar:

- **Como as notícias e menções sociais entram no sistema?**
- **Quais providers e perfis estão ligados agora?**
- **Quanto isso custou em volume/chamadas?**
- **Quais fontes diretas ainda existem e por quê?**

Se essas respostas não forem claras e observáveis, Programas 2–4 ficam construídos em cima de areia.

---

### 1.2. O que já está dado e não pode ser reaberto

A Sprint 31 não discute mais se o modelo é provider-first. Isso já foi decidido em:

- Roadmap Macro v3 dos Programas 1–4, que crava `news_provider` e `social_provider` como pilares de ingestão de conteúdo dinâmico;
- Programa 1 v3, que define o triângulo **Provider → Source → ContentItem** como modelo canônico para Data Hub e ingestão 24/7;
- Programa 2 v3, que espera um fluxo estável de ContentItems com proveniência clara para construir Claims, ClaimGraph e Motor de Sinais;
- Programa 3 v3 e Programa 4 v3, que assumem que FactBlocks, EvidenceBlocks, Cockpits e Fact Cards se apoiam em um Data Hub confiável.

A S31 trabalha **dentro** dessas decisões. Não se discute mais:

- se vamos ou não usar omni-providers de notícia e social;
- se scrapers devem ser exceção e não regra;
- se ContentItem é a unidade canônica de ingestão;
- se precisamos de proveniência rastreável até Provider/Source/URL.

O foco passa a ser: como materializar isso sem quebrar o que já existe e sem criar novos buracos.

---

### 1.3. Problemas concretos que a S31 precisa resolver

#### Problema 1 — Console de Fontes ainda pensa em "fonte = site", não em "fonte = perfil de provider"

Hoje, a camada de UI e boa parte do modelo mental de operação ainda gira em torno de:

- cadastrar uma fonte (RSS, API, scraper);
- ligar/desligar essa fonte unitária;
- eventualmente monitorar o volume daquela fonte.

No mundo provider-first, isso é insuficiente. O operador precisa pensar em **perfis de ingestão**, por exemplo:

- `BR_PT_HARD_NEWS` (Brasil, português, política + economia);
- `LATAM_ES_POLITICS` (América Latina, espanhol, política);
- `GLOBAL_EN_HEALTH` (global, inglês, saúde);
- `SOCIAL_BR_POLITICA_HASHTAGS` (perfil social focado em política BR).

Cada perfil é uma combinação de **provider + filtros + frequência + budget** que traz centenas ou milhares de veículos por trás. A S31 precisa resolver a lacuna entre esse modelo mental e o Console de Fontes atual:

- introduzir **Provider** como entidade de primeira classe na UI;
- introduzir **Profile de Ingestão** como objeto configurável, versionado e observável;
- amarrar esses profiles a Sources derivadas (domínios) sem deixar o operador perdido.

Se esse problema não for resolvido agora, qualquer expansão de ingestão vira gambiarra.

#### Problema 2 — Proveniência e deduplicação frágeis em cenário multi-provider

Sem providers, a dedupe podia se apoiar “só” em URL + corpo. Com omni-providers, surgem novos cenários de caos:

- a mesma notícia chega por dois providers diferentes, com pequenas diferenças de payload;
- parte das fontes continua entrando por canais diretos (RSS, API, scraper);
- Programas 2–4 começam a depender de uma trilha de origem exata para saber quem originou e quem só ecoou uma narrativa.

A S31 precisa colocar ordem nisso, estabelecendo:

- regras canônicas de **hash e dedupe** para ContentItem em contexto de provider;
- como priorizar proveniências (por exemplo, preferir provider X em caso de conflito, ou consolidar metadados de múltiplas origens);
- como representar, no modelo de dados, tanto o `provider_id` quanto o `source_id` e o `external_id` de forma consistente.

Sem isso, ClaimGraph, Sistema de Blocos e Fact Cards vão contar histórias diferentes dependendo do caminho que o dado fez para entrar.

#### Problema 3 — Budgets, quotas e custo ainda são planilha, não sistema

O roadmap já deixou claro: ingestão agressiva de omni-providers custa dinheiro, e bastante. A S31 chega num ponto do projeto em que:

- já discutimos estimativas e envelopes de custo por região/tema;
- já sabemos que não dá para “puxar o mundo inteiro 24/7” sem queimar milhões;
- mas ainda **não temos uma camada operacional** que transforme isso em realidade:
  - perfis com limites de chamadas por dia/mês;
  - métricas e alertas por perfil;
  - visão por operador de “em que estou gastando budget agora?”.

A S31 precisa sair da teoria e entregar:

- controles de budget por profile em nível de código e configuração;
- métricas básicas de volume por provider/profile (itens, chamadas, erros);
- visões no Console e na stack de observabilidade para o time conseguir apertar o freio ou o acelerador com consciência.

Sem isso, qualquer experimento sério com Latam + EUA + UE vira cheque em branco.

#### Problema 4 — Legado de ingestão não está encaixado, está pendurado

S26–S30 já colocaram muita coisa em pé: Console de Fontes, ingestão 2.0, observabilidade, gates, evidências. Mas a virada para provider-first não foi completamente refletida neles. Hoje temos um cenário em que:

- o código suporta uma visão mais moderna de ingestão, mas parte da operação ainda depende de fontes diretas e scrapers;
- os scripts de gates e os scorecards não sabem diferenciar claramente “fluxo legado” de “fluxo via provider”;
- ainda não existe um plano operacional explícito de convivência e aposentadoria do legado.

A S31 precisa transformar esse emaranhado em:

- um modelo claro de **coexistência controlada** (providers + fontes diretas);
- um caminho de migração incremental para cada classe de fonte;
- gates e scorecards que já consigam medir se a ingestão via providers está no nível de qualidade exigido para substituir o legado.

#### Problema 5 — Entrada no ClaimGraph ainda não está alinhada a perfis de ingestão

Programa 2 e o runtime de agentes dependem de recortes claros de ingestão:

- "isso aqui é o feed de política BR que vai alimentar o comitê de política";
- "aquilo ali é o feed de saúde global que vai pro comitê de saúde";
- "essas menções sociais são o radar de narrativa para o caso X".

Sem perfis de ingestão bem definidos e estáveis, o ClaimGraph vira um aglomerado amorfo de conteúdo, difícil de filtrar, amostrar e usar para sinais. A S31 precisa construir os primeiros **perfis oficiais de ingestão por domínio**, conectando-os diretamente aos fluxos de Programa 2, de forma que a partir da S32:

- as pipelines de interpretação e sinais saibam exatamente quais perfis as alimentam;
- qualquer mudança em perfis seja rastreável (e vista como mudança de experimento, não acidente).

---

### 1.4. Domínios, personas e cenários-alvo da Sprint 31

Domínios priorizados nesta sprint

A S31 não tenta cobrir o planeta inteiro. Ela escolhe um conjunto enxuto, mas crítico, de domínios onde o Inspectah precisa “funcionar bonito” primeiro:

- notícias hard (política + economia) para Brasil em PT;
- pelo menos um recorte internacional (Latam ES ou EUA/UE EN) em menor escala, como prova de conceito multi-região;
- social listening focado em política BR e/ou um tema quente com alto valor para o ClaimGraph.

Personas diretamente impactadas

- Operador de Ingestão: ganha um painel onde "ligar Brasil/PT/política" vira um clique em perfil de provider, não uma maratona de cadastrar sites.
- Admin de Fonte/Plataforma: passa a enxergar Providers e perfis como objetos de primeira classe, com contratos claros e caminhos de evolução.
- Squad de Interpretação & Sinais: recebe conteúdo com recortes limpos e rastreáveis, o que simplifica a configuração de pipelines de agentes.
- PO/Conselho de Produto: finalmente pode discutir expansão geográfica e temática em termos de perfis de ingestão e envelopes de custo, não em termos de scripts individuais.

Cenários que guiam decisões

- Cenário A: ligar um perfil `BR_PT_HARD_NEWS` via provider, ver notícias reais entrarem no Data Hub, ver ContentItems canônicos sendo criados, e acompanhar volume/erros/custo em painéis.
- Cenário B: pausar rapidamente um perfil “entretenimento” para preservar budget de política/saúde durante um período de crise, sem tocar em código.
- Cenário C: rodar um backfill controlado (ex.: 30–90 dias de histórico) em um profile piloto e verificar que a dedupe e a proveniência se mantêm corretas.
- Cenário D: abrir um caso piloto em Programa 2 e conseguir mostrar, de forma auditável, que todas as claims vêm de perfis de ingestão bem definidos, com trilha de origem clara.

---

### 1.5. Fora de escopo e bordas da Sprint 31

Para não deixar a sprint inflar indefinidamente, ficam explicitamente fora:

- redesenho de Truth-DB, Sistema de Blocos ou regras de contestação (isso continua no escopo de Programas 3–4 e sprints próprias);
- criação de novos Cockpits finais, Fact Cards ou produtos externos (a S31 fornece insumo melhor para esses produtos, mas não mexe neles diretamente);
- backfills gigantes multi-ano ou multi-continente (a sprint deve preparar tipos de job e contratos, mas os projetos de backfill massivo ganham sprints específicas);
- explosão de novos scrapers: só entram ajustes mínimos para manter o que já existe respirando enquanto a migração para providers acontece.

A Sprint 31 é, no fim do dia, a sprint que torna o **Provider-first Data Hub** uma realidade operacional, não mais um parágrafo bonito no roadmap. A partir dela, qualquer conversa sobre expandir cobertura, rodar backfills agressivos ou plugar Programas 2–4 em escala passa a ter base sólida em código, dados e observabilidade.

