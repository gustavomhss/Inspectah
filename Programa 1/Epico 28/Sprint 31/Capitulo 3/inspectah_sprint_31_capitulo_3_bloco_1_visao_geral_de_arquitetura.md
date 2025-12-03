# Inspectah — Sprint 31 (E28-S3)
## Capítulo 3 — Bloco 1: Visão Geral da Arquitetura Provider-first

### 3.0 Papel deste bloco

Este bloco responde à pergunta: **“Como a Sprint 31 encaixa o modelo Provider → Perfil de Ingestão → ContentItem dentro do Inspectah?”**

Ele não entra ainda no detalhe de pastas e arquivos; isso fica para os próximos blocos. Aqui o objetivo é:
- fixar a **foto macro** da arquitetura da S31;
- deixar claro **onde começa e onde termina** o fluxo provider-first;
- mostrar **como ele conversa com legado** e com os Programas 1–4.

Se alguém ler só este bloco, precisa sair entendendo o filme inteiro da S31 em alto nível.

---

### 3.1 Linha do tempo Provider-first (fim a fim)

A Sprint 31 organiza a ingestão provider-first em uma linha do tempo clara, que vai do mundo externo até Truth-DB:

1. **Mundo externo — Providers de notícia e social**  
   Plataformas como news providers (estilo NewsData/NewsAPI) e social providers (stack de social listening) oferecem APIs pagas. Elas concentram milhares de veículos e fontes de social em um só lugar, com filtros por país, idioma, tema, palavra-chave, período etc.

2. **Camada de configuração do Inspectah — Provider & Perfil de Ingestão**  
   Dentro do Inspectah, a Sprint 31 introduz duas entidades centrais:
   - `Provider`: descreve *quem* estamos usando (ex.: `news_provider_global`, `social_radar_br`), qual o tipo (NEWS/SOCIAL), regiões/idiomas suportados, status, limites gerais.
   - `IngestionProfile` (Perfil de Ingestão): descreve *como* queremos usar um provider em um recorte específico (ex.: `BR_PT_HARD_NEWS`, `LATAM_ES_POLITICS`, `SOCIAL_BR_POLITICA_TIMELINE`). Cada perfil combina provider + filtros + frequência + budget.

3. **Scheduler & fila de jobs — Transformando perfis em execução**  
   Um scheduler olha para perfis ativos e transforma isso em jobs na fila:
   - para cada perfil ativo, cria jobs do tipo `INGEST_PROFILE::<profile_id>` (news ou social);
   - respeita a frequência (cron/intervalo) e limites de budget;
   - empilha esses jobs para os workers de ingestão.

4. **Workers de ingestão — Chamando providers com cérebro**  
   Workers consomem a fila e, para cada job:
   - carregam o `IngestionProfile` correspondente;
   - conferem se ainda há budget disponível para aquele perfil;
   - chamam o client do provider com os filtros adequados (país, idioma, categorias, keywords, janela de tempo);
   - recebem uma lista de itens brutos (`RawNewsItem`, `RawSocialItem`).

5. **Normalização & dedupe — Virando ContentItem canônico**  
   O pipeline transforma respostas brutas em objetos internos:
   - `normalizer` converte cada item bruto em um `ContentItem` canônico, preenchendo proveniência completa: `provider_id`, `ingestion_profile_id`, `source_domain`, `external_id`, timestamps;
   - `dedupe_service` garante que o mesmo conteúdo (mesma notícia/post) não gere múltiplos ContentItems, usando chaves e hashes de conteúdo/URL;
   - o resultado é um fluxo de ContentItems limpos, prontos para alimentar Claims e Truth-DB.

6. **Observabilidade — Métricas e logs por perfil**  
   Cada run de perfil registra métricas e logs estruturados:
   - quantas chamadas ao provider foram feitas;
   - quantos itens brutos chegaram;
   - quantos viraram ContentItems únicos;
   - quantos erros ocorreram e de que tipo;
   - qual o uso de budget naquele intervalo.

   Painéis de observabilidade consomem essas métricas e permitem ver, por perfil e por provider, se a ingestão está saudável e quanto está “custando”.

7. **Programas 2 e 3 — Claims, ClaimGraph e Truth-DB**  
   ContentItems de perfis-piloto alimentam o runtime de Programa 2:
   - Intérprete e Classificador extraem claims, entidades, relações e sinais;
   - ClaimGraph organiza alegações e narrativas por caso/tema.

   Programa 3 consome Claims e ContentItems para montar FactBlocks e EvidenceBlocks:
   - Truth-DB e Sistema de Blocos passam a registrar fatos baseados em conteúdo com proveniência clara;
   - é possível reconstruir Provider → Perfil → ContentItem → Claim → FactBlock para casos piloto.

8. **Programa 4 — Exposição e produto final**  
   Mesmo que a S31 não implemente telas finais de Programa 4, ela garante que, quando Cockpits, Fact Cards e APIs forem construídos, eles encontrem:
   - ContentItems com origem explicável;
   - casos com trilhas de evidência rastreáveis;
   - métricas suficientes para mostrar “de onde vem” o que está na UI.

---

### 3.2 Como a S31 se encaixa no desenho maior do Inspectah

A Sprint 31 não recria o Inspectah; ela encaixa providers na estrutura que o projeto já vem construindo desde as Sprints anteriores.

1. **Com o Programa 1 (Data Hub, Fontes, Ingestão & Operação)**  
   - A S31 pega o Data Hub v1, que já sabe lidar com fontes diretas e fluxos em fila, e adiciona a camada provider-first como **caminho principal** para notícias e social.
   - O Console de Fontes ganha telas e APIs específicas para Providers e Perfis, substituindo a visão “fonte = site” por “fonte = perfil de ingestão em cima de providers omni-fonte”.

2. **Com o Programa 2 (Claims, Entidades, Sinais & Comitês)**  
   - Para que Claims e ClaimGraph funcionem, o sistema precisa saber qual universo de conteúdo está olhando. Perfis de ingestão viram essa unidade de universo.
   - A S31 garante que Programas 2 e 3 possam dizer: “este caso/painel usa principalmente perfis X, Y, Z”, em vez de ter uma sopa de fontes difíceis de explicar.

3. **Com o Programa 3 (Truth-DB & Sistema de Blocos)**  
   - Truth-DB precisa guardar fatos com âncoras em evidência clara. Sem proveniência confiável em ContentItems, o Sistema de Blocos fica em areia movediça.
   - A S31 fornece ContentItems com trilhas completas, permitindo que FactBlocks apontem para evidências cujo caminho de ingestão é transparente.

4. **Com o Programa 4 (Exposição, Cockpits, APIs e Uso Responsável)**  
   - Qualquer Cockpit de Caso, painel de narrativa ou Fact Card que a equipe montar depois pode explicar “como esse conteúdo entrou aqui”.
   - A S31 é o pedaço que garante que, quando o usuário final clicar em “ver fonte”, o Inspectah saiba, de fato, o que responder.

5. **Com o legado (RSS/APIs/scrapers)**  
   - A Sprint 31 trata o legado como **exceção controlada**, não como fluxo principal.
   - Fontes diretas e scrapers continuam existindo onde necessário (dados oficiais, nichos sem provider), mas com:
     - sanidade checada em gates;
     - plano de migração/coexistência documentado;
     - clareza sobre o que ainda é crítico e o que está em rota de aposentadoria.

---

### 3.3 O que muda antes e depois da S31

Antes da Sprint 31, o padrão era:
- pensar ingestão em termos de **fonte individual** (site X, feed Y, scraper Z);
- adicionar cobertura significava cadastrar novas fontes e scripts específicos;
- explicar origem de um conteúdo exigia navegar por múltiplos caminhos paralelos.

Depois da Sprint 31, o padrão passa a ser:
- pensar ingestão em termos de **perfis** construídos em cima de providers omni-fonte;
- adicionar cobertura significa criar ou ajustar perfis, não inventar novos scrapers toda vez;
- explicar origem de um conteúdo vira um caminho natural Provider → Perfil → ContentItem → Claim → FactBlock.

Este bloco fixa essa visão geral. Nos próximos blocos do Capítulo 3, a arquitetura desce de nível: modelos, serviços, APIs, telas e filemap concreto para o Codex transformar essa visão em código e scripts verificáveis.

