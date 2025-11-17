# Inspectah – Sprint 8 (Capítulo 1)
## Especificação de Objetivos, Escopo, Contratos e Critérios de Sucesso (v4)

---

### 0. One‑liner oficial da Sprint 8

> **“A Sprint 8 coloca de pé o esqueleto funcional do Inspectah como produto: telas mínimas de Admin e Usuário, fluxo end‑to‑end Inspectah → Evidências → GPT → Resposta, já usando apenas dados internos – sem web – com contratos claros de entrada/saída e preparado para evoluir em S9–S12 para Truth‑DB, blockchain e comunidade.”**

Sprint 8 é a passagem do **blueprint** para o **produto vivo mais simples possível**. Depois dela, o time consegue **cadastrar fontes**, **coletar dados reais**, **fazer perguntas em linguagem natural** e **ver respostas do GPT ancoradas em evidências clicáveis** – tudo ainda feio/“dev”, mas sólido o bastante, com contratos explícitos, para ser a base de S9–S12.

---

### 1. Contexto e posição da Sprint 8 no roadmap do Inspectah

- **Inspectah é um produto independente.** Não tem vínculo estrutural com MBP, TrendMarket ou qualquer oráculo externo. Ele é o **Data Hub / Truth Engine** por si só.
- O **blueprint v1.2** define o Inspectah como:
  - uma plataforma interna de **Data Hub first** para **centralizar, provar e consultar** informações de múltiplas fontes;
  - com **Evidence Vault** completo e **Field Designer** flexível para definir campos por fonte;
  - com **Explore & Verify** permitindo consultas rápidas, auditáveis e rastreáveis.
- As decisões recentes de produto estendem essa visão:
  - o Inspectah deve, progressivamente, **absorver o fluxo contínuo de eventos** de N fontes (scrapers/conectores), e não apenas responder on‑demand;
  - o GPT será o **guardião da verdade**: categorizando eventos, agrupando por temas (blocos‑tema), decidindo o que é fato registrável vs. complemento e mantendo uma Truth‑DB própria;
  - verdades consolidadas serão **lacradas em blockchain** e poderão ser contestadas com bond e SLA, envolvendo a comunidade.

Dentro dessa linha do tempo, a Sprint 8 é o **primeiro passo operacional** de Q2:

- **S8** – Esqueleto funcional (esta sprint):
  - telas mínimas para **Admin** e **Usuário**;
  - **primeiro fluxo end‑to‑end** Inspectah → Evidências → GPT → Resposta;
  - tudo usando **apenas dados internos** (sem web) e já com trilha de evidência navegável.
- **S9** – v0 de produto:
  - Admin e Usuário robustos, múltiplos tipos de pergunta e de fonte, observabilidade mínima;
  - GPT com prompts especializados (agregação, comparação, checagem factual).
- **S10** – Truth‑DB & GPT Guardião de Blocos (pré‑blockchain):
  - o Inspectah passa a **organizar conhecimento sozinho**, mantendo blocos‑tema, fatos, complementos, versões e estados.
- **S11** – Blockchain & contestação (v1):
  - verdades ancoradas on‑chain, com bond e primeiro ciclo de disputas.
- **S12** – Ingestão contínua & Comunidade v0:
  - scheduler, ingestão contínua, guardrails de qualidade/anti‑alucinação e primeira experiência de comunidade (Explorer do Inspectah).

A Sprint 8 precisa **preparar o terreno** para tudo isso, sem tentar antecipar o trabalho de S9–S12.

---

### 2. Objetivos da Sprint 8 (o que precisa estar inegociavelmente pronto)

1. **Esqueleto de Admin** (v0, funcional mesmo que feio):
   - Permitir cadastrar pelo menos **1–2 fontes reais** (ex.: uma fonte de preços, uma fonte de notícias/fatos públicos).
   - Permitir definir **campos relevantes** por fonte (mesmo com catálogo reduzido nesta sprint).
   - Permitir ver **status mínimo de ingest**: último fetch, sucesso/erro, contagem aproximada de itens.

2. **Esqueleto de Usuário** (v0, funcional mesmo que feio):
   - Campo único de **pergunta em linguagem natural**.
   - Área de **resposta do GPT** com tom neutro, explicativo e humanizado.
   - Bloco de **resumo estruturado** com o núcleo da resposta (número, intervalo, status, datas, etc.).
   - Acesso em **1–2 cliques** ao mapa de evidências (fonte → item → manifest/artefato).

3. **Primeiro fluxo GPT → Verdade local** (apenas com dados internos):
   - Dado um tópico perguntado (preço médio, comparação simples ou checagem factual básica), o Inspectah deve:
     1. localizar os itens relevantes na base interna;
     2. montar um **evidence bundle** minimalista com esses itens;
     3. enviar **pergunta + evidence bundle** para o GPT;
     4. receber uma resposta:
        - **humanizada** (texto amigável, direto, sem jargão),
        - **ancorada** nas evidências fornecidas (sem buscar nada fora do Inspectah),
        - com uma visão clara do que é fato, do que é incerteza e do que é limite de dados.

4. **Contrato de “verdade local” e anti‑alucinação v0:**
   - O GPT **não pode inventar dados externos**; ele só pode operar em cima do pacote de evidências recebido.
   - Se as evidências forem insuficientes ou conflitantes, o GPT deve ser capaz de:
     - responder “não sei com segurança” de modo honesto e didático;
     - listar o que falta (ex.: mais fontes, dados mais recentes) e/ou sugerir ajustes na fonte.
   - Todo request para o GPT deve carregar um **template rígido de prompt** que explicita:
     - que a “verdade oficial” é aquilo que está no evidence bundle;
     - que alucinações são proibidas;
     - que qualquer hipótese/opinião precisa ser marcada como tal.

5. **Experiência “demoável” end‑to‑end:**
   - O time deve conseguir rodar, em ambiente local, um **roteiro de demo** com 2–3 cenários:
     - preço médio de algo em uma cidade;
     - comparação simples (“onde está mais barato?”);
     - checagem factual simples sobre um político ou fato público.
   - Em todos os cenários, a demo deve passar por **Admin → ingestão → Usuário → GPT → resposta + evidências**.

---

### 3. Não‑objetivos da Sprint 8 (para evitar escopo elástico)

Para manter a Sprint 8 **focada e entregável**, ficam explicitamente fora de escopo:

1. **Truth‑DB completa (blocos‑tema, fatos, complementos, versões, estados).**
   - Nesta sprint, podemos ter **protótipos internos** de modelo, mas sem implementar o maquinário de blocos.
   - A Truth‑DB “de verdade” é trabalho de S10.

2. **Blockchain, disputes e comunidade.**
   - Nenhum contrato on‑chain, ancoragem de hashes ou fluxo de bond será implementado em S8.
   - Qualquer menção a contestação, pontos ou leaderboard permanece **conceitual** e documentada, não implementada.

3. **Cadências de ingestão complexas e scheduler global.**
   - S8 pode usar **jobs manuais ou cron simples**; o scheduler unificado e cadências por fonte são S12.

4. **UI refinada, design polido e microinterações ricas.**
   - S8 aceita UI “feia de dev”, desde que **clara, funcional e sem surpresas**.
   - Polimento visual profundo e experiência de comunidade são S9+ e S12.

5. **Suporte a dezenas de tipos de fonte e de pergunta.**
   - S8 mira um **subconjunto bem escolhido**:
     - 1 tipo de fonte de preço/valor numérico;
     - 1 tipo de fonte de notícia/decisão factual;
     - 2–3 tipos de pergunta bem mapeados.

---

### 4. Escopo funcional detalhado (Admin, Usuário, GPT & Pipeline)

#### 4.1. Admin v0 – Cadastro e gestão mínima de fontes

**História central:** “Como operador, quero cadastrar uma fonte e ver se ela está sendo coletada, para que eu possa usar esses dados nas consultas dos usuários.”

O que precisa existir em S8:

1. **Tela Add Source v0 (mínima, mas real):**
   - Formulário para cadastrar uma fonte com campos como:
     - `nome_da_fonte` (texto);
     - `tipo_de_fonte` (ex.: `precos_api_simples`, `noticias_rss_simplificado`);
     - `url_base` ou endpoint;
     - credenciais/token (se necessário) com tratamento seguro mínimo;
     - campos básicos de configuração (intervalo de teste, parâmetros, etc.).
   - Botão **“Testar fonte”** (dry‑run):
     - chama o conector específico;
     - mostra **3–5 itens de amostra** em formato bruto/minimamente normalizado;
     - indica se a fonte é “aceitável” ou se precisa de ajuste.

2. **Seleção de campos relevantes v0:**
   - Para cada fonte, permitir que o Admin marque **quais campos interessam** para S8:
     - ex.: para preços → `produto`, `cidade`, `bairro`, `preco`, `moeda`, `data_coleta`;
     - ex.: para notícias → `titulo`, `data`, `entidades`, `categoria`, `conteudo_texto`.
   - Não é necessário ter o **Field Designer completo** da blueprint; basta um subconjunto coerente que permita montar os evidence bundles dos cenários da sprint.

3. **Status de ingestão v0:**
   - Painel simples por fonte, mostrando:
     - `ultimo_fetch_em` (timestamp local);
     - `resultado_ultimo_fetch` (sucesso/erro);
     - contagem aproximada de itens disponíveis no período recente (ex.: últimas 24h).
   - Link para abrir um **preview dos últimos itens** (lista curta) com indicação do que foi indexado.

#### 4.2. Usuário v0 – Perguntas em linguagem natural + resposta ancorada

**História central:** “Como usuário, quero fazer uma pergunta simples e receber uma resposta clara, com evidências que posso inspecionar, sem precisar saber nada sobre as fontes.”

O que precisa existir em S8:

1. **Campo de pergunta em linguagem natural:**
   - Input simples com placeholder do tipo “Pergunte algo, ex.: ‘qual o preço médio de X em SP?’”.

2. **Área de resposta do GPT:**
   - Bloco que exibe a resposta textual, organizada em 1–3 parágrafos:
     - frase de abertura respondendo diretamente à pergunta;
     - breve explicação de como o valor foi obtido (média, comparação, checagem factual);
     - nota sobre confiabilidade e limitações.

3. **Resumo estruturado da resposta:**
   - Card logo abaixo da resposta contendo, por exemplo:
     - valor principal (ex.: preço médio, “sim/não”, status de condenação);
     - intervalo ou distribuição (min/máx ou bairro mais barato/caro);
     - data/intervalo temporal dos dados usados;
     - número de fontes e itens considerados.

4. **Mapa de evidências em 1–2 cliques:**
   - Link ou botão “Ver evidências” que leve a:
     - lista de fontes usadas (nome, tipo);
     - para cada fonte, itens relevantes (ex.: título, data, valor chave);
     - link interno para o manifest/artefato bruto (quando existir).

#### 4.3. Pipeline Inspectah → Evidências → GPT → Resposta (v0)

O fluxo mínimo da Sprint 8 deve seguir esta sequência, de forma determinística, com contratos explícitos.

**Contrato geral do pipeline (Design by Contract):**

- **Pré‑condições (antes do pipeline rodar):**
  - Pelo menos uma fonte relevante está cadastrada e com último fetch bem‑sucedido.
  - A pergunta do usuário não é vazia e está em um idioma suportado (por ora, PT/EN).
  - O tipo de pergunta derivado está entre os suportados em S8 (`agregacao_simples`, `comparacao_simples`, `checagem_factual_simples`).

- **Pós‑condições de sucesso:**
  - Existe um `evidence_bundle` persistido para a requisição.
  - Toda resposta exibida ao usuário é
    - derivada exclusivamente dos dados contidos no `evidence_bundle`;
    - acompanhada de um resumo estruturado consistente com o texto;
    - rastreável até os itens/artefatos usados como evidência.

- **Pós‑condições em caso de falha controlada:**
  - O usuário recebe mensagem clara sobre o tipo de falha (dados insuficientes, erro de fonte, erro de IA etc.).
  - O sistema registra um log estruturado do erro, com contexto suficiente para reexecução/debug.

**Etapas do pipeline:**

1. **Parsing da pergunta (camada de aplicação, sem depender de LLM):**
   - Identificar o tipo de pergunta:
     - `agregacao_simples` (ex.: “qual o preço médio de X em Y?”);
     - `comparacao_simples` (ex.: “onde está mais barato?”);
     - `checagem_factual_simples` (ex.: “Político X foi condenado no caso Y?”).
   - Extrair sinais óbvios (entidades, cidade, produto) usando **regras determinísticas** ou ferramentas clássicas de NLP, quando fizer sentido.

2. **Busca na base interna:**
   - Localizar itens relevantes nas fontes cadastradas:
     - para agregação/comparação → itens com campos numéricos e geográficos;
     - para checagem factual → notícias/documentos com menções ao nome e ao caso.

3. **Montagem do evidence bundle v0:**
   - Construir um pacote estruturado contendo:
     - metadados de consulta (tipo de pergunta, termos extraídos, filtros);
     - até N itens por fonte (N pequeno, ex.: 10–20) com campos principais;
     - caminhos para manifest/artefato bruto.
   - O evidence bundle deve ter formato **estável** e incluir um `evidence_bundle_id` que permita rastrear a resposta.

4. **Chamada ao GPT com contrato rígido:**
   - Prompt deixa cristalino que:
     - o GPT **só** pode usar os dados presentes no evidence bundle;
     - se um dado não está no bundle, ele **não existe** para fins de resposta;
     - ele deve responder de forma **neutra, imparcial, técnica** e human friendly;
     - ele deve distinguir explicitamente:
       - o que é **fato consolidado**;
       - o que é **incerteza**;
       - o que é **limite de dado**;
       - qualquer hipótese/opinião (rotulada como tal).

5. **Geração da resposta + resumo estruturado:**
   - A camada de aplicação recebe a saída do GPT e a encaixa em:
     - resposta textual (área de resposta);
     - resumo estruturado (card com números/estados).

6. **Persistência mínima para rastreio (logs & storage):**
   - Registrar em storage interno (ex.: `out/evidence/s8_queries/` + tabela/log):
     - pergunta original;
     - tipo de pergunta derivado;
     - `evidence_bundle_id` e caminho do bundle;
     - IDs de fontes/itens usados;
     - resposta do GPT (texto + estrutura);
     - timestamp e status (sucesso/falha controlada);
     - código de erro, se houver.
   - Esses registros formam a base de evidência que será consumida por S10 (Truth‑DB) e por gates T6/T7/T8.

---

### 5. Experiências obrigatórias de demo (cenários da Sprint 8)

Para considerar a Sprint 8 pronta, pelo menos **três roteiros de demo** precisam estar funcionais e reprodutíveis em ambiente local:

1. **Cenário Preço Médio:**
   - Admin cadastra uma fonte de preços para um produto X em uma cidade Y.
   - Usuário pergunta: “Qual o preço médio de X em Y?”.
   - Sistema:
     - busca os itens;
     - monta o evidence bundle;
     - chama o GPT;
     - retorna:
       - valor médio,
       - intervalo min/máx (se disponível),
       - período dos dados,
       - número de fontes / itens.
   - Usuário consegue ver as evidências usadas em 1–2 cliques.

2. **Cenário Comparação Simples (“onde está mais barato?”):**
   - Admin cadastra fontes de preços para o mesmo produto X em diferentes bairros/regiões.
   - Usuário pergunta: “Onde X está mais barato em Y?”.
   - Sistema retorna:
     - bairro/região mais barata;
     - diferença em relação à média (se fizer sentido);
     - notas de cobertura (ex.: “não há dados para tais bairros”).
   - Evidências mostram, para cada bairro usado, os preços coletados.

3. **Cenário Checagem Factual Simples:**
   - Admin cadastra fonte(s) de notícias/decisões judiciais.
   - Usuário pergunta: “Político X foi condenado na investigação/caso Y?”
   - Sistema:
     - localiza notícias/documentos relevantes;
     - monta evidence bundle;
     - GPT responde:
       - “Sim/Não/Não é possível afirmar com segurança”,
       - explicando em linguagem simples o que as fontes dizem;
       - destacando onde há consenso ou conflito.
   - Usuário consegue abrir as matérias/decisões usadas como evidência.

---

### 6. Critérios de sucesso (DoD – Definition of Done da Sprint 8)

A Sprint 8 só é considerada **concluída** quando todos os critérios abaixo forem verdadeiros:

1. **Funcionalidade:**
   - Admin consegue cadastrar pelo menos **duas fontes reais** (uma de preço, uma de notícias) e ver status mínimo de ingestão.
   - Usuário consegue executar, com sucesso, os **três cenários de demo** descritos (preço médio, comparação simples, checagem factual simples).

2. **Integração GPT ↔ Evidências:**
   - Em todos os cenários de demo, o GPT responde **sem usar dados externos**, apenas o evidence bundle.
   - Pelo menos um caso de **dados insuficientes** é tratado corretamente, com resposta honesta e explicação do porquê.

3. **Rastreabilidade:**
   - Dada uma resposta, é possível:
     - encontrar o `evidence_bundle_id` correspondente;
     - listar fontes e itens usados;
     - abrir os artefatos principais (ou seu manifest) em até 2 cliques.

4. **Qualidade da experiência (mesmo “feia”):**
   - UI pode ser visualmente simples, mas precisa:
     - ser clara sobre o estado das operações (“coletando dados”, “IA analisando”, “resposta pronta”);
     - explicar falhas de forma legível (ex.: fonte com erro, dados insuficientes, timeouts);
     - evitar ações sem feedback.

5. **Operacionalidade local:**
   - O time consegue subir o sistema em ambiente local (dev) e seguir um **roteiro de execução** documentado (ex.: `bin/s8_demo.sh` + passos manuais mínimos), chegando ao fim das 3 demos.

6. **Alinhamento com o futuro (S9–S12):**
   - O formato de evidence bundle, as estruturas de log e as decisões de modelagem **não entram em conflito** com o que está planejado para:
     - Truth‑DB e guardião de blocos (S10);
     - ancoragem em blockchain e disputa com bond (S11);
     - ingestão contínua e comunidade (S12).

---

### 7. Gates T0–T8 e evidências esperadas (visão de alto nível)

Sem entrar ainda no Capítulo 2, o Capítulo 1 define o papel dos gates da Sprint 8:

- **T0 – Descoberta & alinhamento:**
  - Evidência: este Capítulo 1 aprovado + mapa de histórias e cenários de demo.

- **T1 – Qualidade estática:**
  - Evidência: árvore de arquivos, contratos básicos de módulos (incluindo contratos do pipeline) e checagens estáticas passando.

- **T2/T3 – Testes e propriedades básicas:**
  - Evidência: testes cobrindo parsing de perguntas, montagem de evidence bundle e contratos simples de entrada/saída.

- **T4/T5 – Goldens & performance mínima:**
  - Evidência: roteiros de demo em forma de testes/goldens (input de pergunta → evidence bundle esperado → saída textual e estruturada consistente).

- **T6 – Observabilidade e logs:**
  - Evidência: diretórios/tabelas de logs e bundles (`out/evidence/s8_*`) preenchidos, com exemplos reais.

- **T7 – CI local/remote:**
  - Evidência: pipeline automatizado rodando todos os checks anteriores.

- **T8 – GO/NO‑GO da sprint:**
  - Evidência: scorecard consolidado indicando se os critérios de sucesso deste Capítulo 1 foram atendidos.

Essas definições servem como ponte para o Capítulo 2 (plano de execução detalhado e filemap), evitando lacunas entre visão e implementação.

---

### 8. Riscos principais e como mitigá‑los na Sprint 8

1. **Escopo escorregar para “Truth‑DB completa” antes da hora.**
   - Mitigação: manter qualquer modelagem de blocos/fatos/complementos como **experimento interno**, sem acoplar ao código de produção. Tudo que for além do mínimo para S8 vai para o backlog de S10.

2. **GPT alucinar ou misturar dados internos com conhecimento genérico.**
   - Mitigação:
     - templates de prompt explicitando que **apenas o evidence bundle** é verdade;
     - testes manuais com casos adversos (poucos dados, dados conflitantes, perguntas capciosas) antes de dar S8 como concluída;
     - logs estruturados de decisões, permitindo revisão rápida.

3. **Admin UI virar um mini Field Designer completo antes do tempo.**
   - Mitigação: limitar o número de tipos de campo e de transformações disponíveis em S8; o catálogo rico fica oficialmente para S9+.

4. **Performance ruim já na primeira versão.**
   - Mitigação: mesmo sem otimizar tudo, garantir limites sensatos de tamanho do evidence bundle (por tipo de pergunta) e logs para entender gargalos.

5. **Divergência entre demo e produto real planejado.**
   - Mitigação: manter Capítulo 1 sempre alinhado com o blueprint geral do Inspectah e com os overviews das S9–S12; qualquer hack puramente de demo deve estar **claramente identificado** como tal nos arquivos de código/config.

---

### 9. “Barra de qualidade” da Sprint 8

- **Clareza:** qualquer engenheiro(a) novo(a) deve conseguir ler este capítulo, abrir o repositório e entender **o que a Sprint 8 entrega** e **o que ela não entrega**.
- **Foco:** tudo que não ajuda diretamente a colocar o **esqueleto de Admin/Usuário + fluxo GPT ancorado** no ar é adiado para S9–S12.
- **Rastreabilidade:** nenhuma resposta sem evidência; nenhum “milagre” escondido em chamadas mágicas de LLM.
- **Contratos:** o pipeline central tem pré‑ e pós‑condições explícitas; erros são tratados de forma previsível e logados.
- **Preparação para o futuro:** nomes, estruturas e contratos são compatíveis com o papel do Inspectah como **Truth‑DB + blockchain + comunidade** nas Sprints 10–12.

Este Capítulo 1 (v4) é considerado a versão de referência para a execução da Sprint 8, servindo como contrato com o time e briefing para o Codex, sem lacunas críticas e com o nível de rigor esperado pelo projeto.

