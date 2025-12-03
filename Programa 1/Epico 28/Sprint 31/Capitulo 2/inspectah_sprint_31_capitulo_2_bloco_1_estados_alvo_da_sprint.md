# Inspectah — Sprint 31 (E28-S3)
## Capítulo 2 — Bloco 1: Estados-Alvo da Sprint 31

### 2.0 Papel deste bloco

Este bloco define **o que precisa ser verdade ao final da Sprint 31** do ponto de vista de produto, operação e arquitetura de ingestão provider-first. Os gates, métricas e invariantes dos próximos blocos servem apenas para responder: *“isso aqui virou realidade, sim ou não?”*.

Cada estado-alvo (S31-SA-0X) deve ser:
- **observável** (dá pra ver em UI, logs, painéis ou consultas);
- **testável** (existe ao menos um gate ou teste cobrindo);
- **relevante para o roadmap** (não é detalhe técnico isolado, e sim algo que destrava Programas 1–4).

---

### 2.1 S31-SA-01 — Provider-first de verdade no Data Hub

**Enunciado**
Ao final da Sprint 31, o Data Hub trata ingestão provider-first como **caminho padrão** para notícias e social no domínio piloto. Não é “mais um módulo”: é o fluxo principal.

**Condutas esperadas no sistema**
- Existem entidades `Provider` persistidas (no mínimo 1 `news_provider` real e 1 `social_provider` real), com configs e estados claros (ativo/inativo, limites, observações).
- Existem **Perfis de Ingestão** que combinam:
  - qual provider será usado;
  - filtros (país, idioma, categorias/temas, keywords);
  - frequência (cron/agendamento) e intensidade;
  - parâmetros de budget (chamadas/dia, volume alvo, etc.).
- ContentItems criados a partir desses perfis trazem **proveniência completa**:
  - `provider_id`;
  - `profile_id` (perfil que gerou a coleta);
  - `source/domain` (veículo concreto, quando aplicável);
  - identificador externo (id da notícia/post no provider) e timestamps coerentes.

**Sinal de que o estado foi atingido**
- Em consultas simples ao banco ou via Explore/Console interno, é possível filtrar ContentItems do domínio piloto por `provider_id` e `profile_id`, ver que a maior parte do fluxo vem de providers, e que esses campos não são raridade.
- Em documentação e visão de arquitetura, quando alguém pergunta “como essas notícias entram?”, a resposta começa em Providers/Perfis, não em scrapers.

---

### 2.2 S31-SA-02 — Ingestão via providers operando fim a fim em perfis-piloto

**Enunciado**
Ao final da S31, a plataforma consegue rodar ingestão provider-first **do início ao fim** para um conjunto pequeno, mas crítico, de perfis-piloto. Não é POC em notebook; é pipeline integrado à fila, workers e observabilidade.

**Perfis mínimos previstos**
- Um perfil `BR_PT_HARD_NEWS` (Brasil, português, política + economia) via `news_provider`.
- Um perfil internacional piloto (por exemplo, `LATAM_ES_POLITICS` ou `US_EU_EN_HARD_NEWS`) em escala menor, também via `news_provider`.
- Pelo menos um perfil `SOCIAL_BR_POLITICA_*` ou equivalente, via `social_provider`, cobrindo um recorte relevante de narrativa (hashtags, contas-chave, etc.).

**Fluxo fim a fim deve cobrir**
1. **Agendamento ou disparo manual** de jobs de ingestão por perfil (via scheduler e/ou Console).
2. **Chamada real ao provider**, com filtros e paginação configurados no perfil.
3. **Normalização** em estruturas intermediárias (`RawNewsItem`, `RawSocialItem` ou similar).
4. **Conversão para ContentItem** canônico, com dedupe.
5. **Registro de logs estruturados** (params, contagens, erros) e métricas mínimas.

**Sinal de que o estado foi atingido**
- Para cada perfil-piloto, existe evidência de runs bem-sucedidos (jobs, logs, ContentItems criados), repetíveis; não é “rodou uma vez num ambiente dev secreto”.
- O time é capaz de acionar manualmente um run de teste de cada perfil-piloto e ver, em poucos minutos, itens novos surgindo associados àquele perfil.

---

### 2.3 S31-SA-03 — Console de Fontes v2: Providers & Perfis como cidadãos de primeira classe

**Enunciado**
Ao final da Sprint 31, o Console de Fontes reflete o modelo mental provider-first. Um operador, sem abrir código, consegue entender e operar Providers e Perfis.

**Capacidades mínimas do Console**
- **Visão de Providers**:
  - listar providers configurados (news/social);
  - ver tipo, status (ativo/inativo), principais parâmetros (regiões, limites gerais, notas);
  - enxergar, por provider, quantos perfis existem e um resumo do que cobrem.
- **Visão de Perfis de Ingestão**:
  - criar e editar perfis vinculados a um provider;
  - configurar filtros básicos (país, idioma, categorias/temas, keywords);
  - configurar frequência (cron/intervalo) e parâmetros de budget (ex. limite diário de chamadas);
  - ver status da última execução (sucesso/erro, volume de itens) e histórico resumido.
- **Ação operacional simple**:
  - acionar “rodar agora” um perfil-piloto a partir do Console e ver o resultado refletido em logs/metrics.

**Sinal de que o estado foi atingido**
- Um operador que entende o negócio (mas não o código) consegue, vendo apenas o Console, responder:
  - “quais perfis de ingestão de notícias para Brasil estão ligados hoje?”;
  - “quais perfis sociais estamos usando para política BR?”;
  - “qual foi o último run desse perfil e quantos itens ele trouxe?”.

---

### 2.4 S31-SA-04 — Observabilidade & budgets v1 por perfil de ingestão

**Enunciado**
Ao final da S31, os perfis-piloto de ingestão estão **instrumentados o bastante** para não dependermos de feeling ou planilha externa quando o assunto é volume e custo.

**O que precisa existir por perfil-piloto**
- Métricas básicas, por janela de tempo, incluindo pelo menos:
  - `provider_calls_total` (nº de chamadas ao provider);
  - `items_ingested_total` (itens brutos recebidos do provider);
  - `contentitems_created_total` (ContentItems únicos após dedupe);
  - `provider_errors_total` (chamadas com erro, por tipo);
  - `dedupe_ratio` (proporção de itens aproveitados);
  - `budget_limit_calls` (limite configurado de chamadas no período);
  - `budget_usage_ratio` (uso do limite).
- Painel ou visão consolidada que permita:
  - ver essas métricas por perfil;
  - identificar perfis que estão batendo no teto de budget;
  - enxergar perfis com erro crônico ou dedupe estranho.

**Sinal de que o estado foi atingido**
- Ninguém precisa “abrir log cru” para responder “quanto esse perfil está puxando” ou “estamos chegando no limite de chamadas?”.
- Em uma reunião de ORR, é possível mostrar, em uma tela, como se comportaram os perfis-piloto na sprint (em volume, erros e uso de budget).

---

### 2.5 S31-SA-05 — Legado encaixado, não pendurado

**Enunciado**
Ao final da S31, providers convivem com fontes diretas e scrapers de forma **controlada e documentada**. O legado não some, mas deixa de ser uma nuvem amorfa.

**Condições mínimas**
- Migrations e mudanças de modelo **não quebram** fluxos de ingestão legados apontados como críticos.
- Existe uma **tabela de coexistência/migração** mapeando:
  - classes de fontes que já podem ser totalmente migradas para providers;
  - fontes que precisam continuar diretas (ex.: alguns dados oficiais específicos);
  - fontes marcadas para aposentadoria em sprints futuras, com racional simples.
- Gates de S31 incluem pelo menos um sanity que roda ingestão antiga + nova, garantindo que nada crítico ficou para trás.

**Sinal de que o estado foi atingido**
- Quando alguém pergunta “o que ainda depende de scrapers? o que já migrou? o que vamos matar e quando?”, há um documento e uma visão convergente, não versões contraditórias na cabeça de cada dev.

---

### 2.6 S31-SA-06 — Domínio piloto amarrado a perfis de ingestão e Programas 2–3

**Enunciado**
Ao final da S31, pelo menos um domínio piloto (tendendo a ser **política/economia BR**) está amarrado de ponta a ponta, do provider ao Truth-DB.

**Condições mínimas**
- Para esse domínio piloto, há uma lista explícita dos perfis de ingestão que o alimentam (news + social).
- O pipeline de Programa 2 (interpretação, claims, sinais) está configurado para consumir **esses** perfis como entrada principal.
- Existe pelo menos **um caso piloto** em Programa 3 (Truth-DB/Sistema de Blocos) cuja cadeia de origem possa ser reconstruída como:
  - Provider → Perfil de Ingestão → ContentItem → Claim → FactBlock → (eventual Contestação).

**Sinal de que o estado foi atingido**
- Em uma demo interna, alguém consegue abrir o caso piloto e, com poucos cliques/consultas, mostrar “este fato veio desses perfis, que usam esses providers, com esses filtros”, sem recorrer a explicação oral ou investigação de código.

---

### 2.7 Resumo dos estados-alvo

Em forma compacta, a Sprint 31 só pode ser considerada **provider-first de verdade** se, ao final, pudermos afirmar:

- (S31-SA-01) Providers e perfis existem como entidades centrais no Data Hub, e ContentItems de piloto carregam essa proveniência.
- (S31-SA-02) Ingestão via providers roda fim a fim em perfis-piloto de notícia e social, com fluxo repetível.
- (S31-SA-03) O Console de Fontes mostra Providers e Perfis de forma clara, operável por humanos normais.
- (S31-SA-04) Perfis-piloto têm observabilidade mínima decente, incluindo budget e volume.
- (S31-SA-05) Legado convive com providers de forma controlada e com plano de migração em vista.
- (S31-SA-06) Pelo menos um domínio piloto já está amarrado Provider → Perfil → ContentItem → Claim → FactBlock.

Os blocos seguintes do Capítulo 2 vão dizer como provar isso (gates, métricas, invariantes). Este bloco fixa **o alvo** que todos vamos mirar durante a execução da sprint.

