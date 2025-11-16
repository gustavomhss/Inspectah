# D9 — Inspectah — Sprint 1 (Spec & Roadmap)  
## Capítulo 1 — Contexto, Objetivos e Entregáveis (v1.1)

> Leslie Lamport no comando: esta sprint existe para tirar o Inspectah da categoria "ideia genial em texto solto" e colocá‑lo na categoria "produto especificado, com mapa claro de execução e sem buracos". Nenhuma linha de código é escrita aqui; o foco é **especificação de qualidade formal**, mas legível para humanos.

---

## 0) TL;DR da Sprint D9 em 10 linhas
1) O Inspectah é o **Data Hub + OracleOps interno**: um lugar único onde o time vê, confia e audita informações vindas de múltiplas fontes (RSS, APIs, HTML simples, etc.).  
2) D9 transforma o blueprint bruto do Inspectah em um **pacote fechado de documentação**: blueprint consolidado, anexos A–D, roadmap e superprompt do Codex.  
3) O foco de D9 é **especificar**, não implementar; a implementação técnica virá em sprints futuras, guiada por estes artefatos.  
4) Tudo que for decidido aqui precisa ser **coerente com o DNA do MBP/Oráculo** (Blocos 0–5), mas sem acoplar Inspectah ao core do mercado ou à lógica de payout/resolução.  
5) O resultado de D9 deve permitir que um time de engenharia leia os docs, aplique o superprompt no Codex e **gere o esqueleto do Inspectah v0 sem dúvidas estruturais**.  
6) Cada entregável de D9 precisa ter um papel claro dentro do ecossistema: por que existe, que **pergunta responde**, que tipo de evidência ou contrato produz.  
7) A sprint só é considerada concluída quando todas as peças **encaixam nos gates do Capítulo 2** (coerência, ausência de gaps, consistência de termos, navegabilidade e testabilidade).  
8) D9 não resolve integrações profundas com oráculos externos (UMA/Reality); ela apenas **delimita o contorno** e o modo de plugar essas coisas no futuro, sempre como plugins opt‑in.  
9) D9 também define um **roadmap de versões (v0, v1, v1.x)** com critérios explícitos de salto de versão, encaixando o Inspectah no plano maior de CE/MBP, sem dependências circulares.  
10) Ao fim, o Inspectah passa a ter um **mini‑DNA próprio**, compatível com o DNA principal, e pronto para virar código com ajuda do Codex.

---

## 1) Contexto: onde o Inspectah entra no filme

### 1.1 Dor atual e mantra do produto
Hoje, sem o Inspectah, o time sofre com:

- informações espalhadas em dezenas de abas, planilhas, portais e APIs;
- verificações repetitivas ("o que mudou em X desde ontem?") feitas na mão, sem histórico nem evidência consolidada;
- decisões importantes baseadas em prints soltos, links quebrados ou dados difíceis de reproduzir;
- dificuldade em plugar novas fontes de dados de forma segura, auditável e reaproveitável.

**Mantra:**  
> *“Inspectah é o painel de controle de evidências do ecossistema CE/MBP.”*

Ele é o lugar onde se responde, com confiança: "de onde veio esse número?", "o que mudou?" e "qual é a evidência por trás desta decisão?".

### 1.2 De MBP/Oráculo → Inspectah
Os Blocos 0–5 descrevem o MBP/Oráculo como um sistema completo de mercado de previsões: AMM, jornadas de compra/venda, liquidez, oráculo, smart contracts. Em vários pontos, fica implícita a necessidade de um **hub interno de dados** que:

- concentre informações vindas de fontes externas (notícias, APIs, dados de mercado, etc.);
- permita **explorar e auditar evidências** usadas na tomada de decisão (resoluções, limites de risco, post‑mortems);
- sirva como **ponte opcional** entre o mundo de dados off‑chain e os componentes on‑chain do MBP e de outros oráculos.

O Inspectah nasce para ser esse hub. Ele não é o oráculo em si, nem contém lógica de payout/resolução do MBP; ele é o "**cérebro de dados e evidências**" que alimenta oráculos, analistas e módulos de risco.

### 1.3 D8, D9 e o corte de sprint
Até D8, o foco estava em consolidar observabilidade, scorecards e ORR do stack principal (MBP/Oráculo). O Inspectah aparecia mais como uma ideia poderosa do que como um produto estruturado.

D9 representa um **corte explícito**:

- D8 fecha a etapa anterior, focada no oráculo/MBP core e sua observabilidade.  
- D9 assume que o MBP já tem um DNA sólido e cria, para o Inspectah, um **capítulo independente de especificação**.  
- A partir de D9, o Inspectah passa a ter sua própria linha de sprints (v0, v1, v1.x), mas sempre alinhada com o masterplan do MBP.

### 1.4 Personas relevantes para D9
D9 é uma sprint de **documentação estruturante**, não de código. As personas são:

- **Leslie (Arquiteto de Especificação)**: garante consistência, ausência de ambiguidade, clareza de invariantes e coesão entre documentos.  
- **Product Owner (PO do Inspectah)**: garante que a visão de produto (o que o Inspectah precisa ser na prática) está inteiramente capturada.  
- **Engineering Lead (Codex + devs)**: futuro consumidor direto do pacote D9; precisa conseguir gerar uma implementação v0 confiável a partir desses docs.  
- **Audit/Compliance**: interessado em LGPD/ToS, evidências, rastreabilidade e limites de uso de dados.

O Capítulo 1 é escrito para essas quatro personas ao mesmo tempo: legível o suficiente para o PO, preciso o suficiente para Leslie, acionável para engenharia e confortável para audit/compliance.

### 1.5 Camadas do Inspectah
Para alinhar expectativas e separar responsabilidades, o Inspectah é pensado em camadas:

- **Camada de Ideia / Contrato (esta sprint D9)**: visão de produto, requisitos, esquemas, APIs, limites legais, roadmap. Nenhum código, só contratos.  
- **Camada de Serviços (futuras sprints)**: implementação de API, watchers, indexer, Evidence Vault, UI.  
- **Camada de Integração**: como outros sistemas consomem o Inspectah (MBP, scripts internos, BI, plugs de oráculos externos).  
- **Camada de Operação & Observabilidade**: métricas, alertas, ORR, playbooks.

D9 foca exclusivamente na **camada de ideia/contrato**, garantindo que as demais possam ser construídas em cima dela sem ambiguidades.

---

## 2) Objetivo macro da Sprint D9

> Entregar um **pacote fechado de especificação** do Inspectah que permita a qualquer time de engenharia, usando Codex ou não, implementar o **Inspectah v0** com segurança, sem dúvidas estruturais e sem precisar voltar ao ChatGPT para "preencher buracos".

Traduzindo em termos operacionais:

1) Consolidar o **blueprint do Inspectah** em um documento mestre, coerente, navegável e congelado como v1.2.x.  
2) Materializar os **Anexos A–D** (Field Designer, Explore/API, DDL & Migração, LGPD/ToS) num nível de detalhe equivalente aos Blocos 1–5 do MBP.  
3) Produzir um **roadmap de execução** para o Inspectah (v0, v1, v1.x) que se integre ao roadmap geral de CE/MBP, com critérios claros de quando sair de v0 → v1 → v1.x.  
4) Especificar pelo menos um **superprompt de Codex** capaz de gerar o esqueleto técnico do Inspectah v0 (serviços, esquemas, pipelines) respeitando os docs anteriores.  
5) Amarrar tudo isso em um formato que **encaixe diretamente nos gates do Capítulo 2**: cada entregável precisa ter critérios de verificação claros e testáveis.

### 2.1 Critérios de versão (v0, v1, v1.x)

- **v0 — Core Data Hub Operável**  
  - Existe um caminho único para cadastrar fontes RSS/API, rodar watchers, ver itens e evidências básicas.  
  - Métricas mínimas de ingest e Explore estão definidas e mensuráveis (mesmo que com stack simples).  
  - Field Designer funciona em modo mínimo: tipos básicos, transforms essenciais, dry‑run, gravação em ItemKV.

- **v1 — Data Hub Refinado + Observabilidade Forte**  
  - Field Designer com computed fields mais ricos, catálogo de transforms bem definido.  
  - DSL de filtros/consultas mais expressiva.  
  - Observabilidade consolidada: detection_latency, explore_query_latency, field_resolution_success e evidence_completeness com SLOs praticáveis.  
  - Integrações principais (webhooks, exports) estáveis e documentadas.

- **v1.x — Extensões e Bridges Opt‑in**  
  - Snapshots HTML/print, conectores para UMA/Reality e outros oráculos, UX mais refinada.  
  - Qualquer mudança em v1.x não pode quebrar os contratos base de v1; são incrementos compatíveis.

A sprint D9 não implementa nenhum destes estados, mas define os **contratos** que permitem saber, mais tarde, quando o Inspectah alcançou v0, v1 ou v1.x.

---

## 3) Recorte de Escopo (IN / OUT)

### 3.1 Escopo IN (o que D9 cobre)

- Definição formal do Inspectah como **produto de Data Hub + OracleOps interno**: objetivos, limitações, uso recomendado.  
- Especificação completa das **capacidades core de v0**:
  - registro de fontes (RSS/API, HTML simples mais tarde);
  - pipeline de ingestão com watchers agendados;
  - Evidence Vault (HTML, texto, manifest JSON, hashes);
  - Field Designer mínimo (tipos, transforms, computed fields básicos, dry‑run);
  - Explore & Verify (FTS, filtros, paginação, export CSV/JSON);
  - métricas e SLOs mínimos (detection_latency, explore_query_latency, evidence_completeness, field_resolution_success).
- Design de **interfaces de integração** (APIs, exports, webhooks) necessárias para o Inspectah conversar com MBP e outros sistemas internos.  
- Definição das **fronteiras legais e éticas** de uso de dados (LGPD/ToS) no contexto do Inspectah.  
- Mapeamento das versões v0, v1 e v1.x em termos de funcionalidades e riscos endereçados.  
- Definição de um **superprompt Codex v1** para levantar o esqueleto v0 do Inspectah.  
- Amarração de cada métrica citada (ex.: detection_latency, explore_query_latency) a um ponto de medição futuro (ex.: API, watcher, auditor), ainda que os detalhes finos fiquem em anexos e sprints posteriores.

### 3.2 Escopo OUT (o que D9 não faz)

- Não implementa código, containers, pipelines CI/CD nem dashboards.  
- Não define em detalhe os **watchers ORR/observabilidade** específicos do Inspectah (isso será escopo de uma futura sprint focada em operação).  
- Não projeta integrações profundas com UMA/Reality ou outros oráculos de terceiros; define apenas o **contorno e o modelo de plugin**, mantendo qualquer lógica de payout/resolução fora do Inspectah.  
- Não substitui o DNA do MBP nem reescreve Blocos 0–5; apenas referencia e complementa onde necessário.  
- Não congela decisões de UX fina (cores, microcopy, layout pixel‑perfect); define apenas os **fluxos críticos** de uso (ex.: como cadastrar fonte, como explorar itens, como ver evidência).

Este recorte evita que D9 se torne um "mini‑projeto infinito". O objetivo é sair com um **pacote de especificação completo o bastante** para uma primeira implementação segura, sabendo que refinamentos visuais e profundidade de observabilidade virão depois.

---

## 4) Entregáveis de D9 (visão geral)

> Todos os entregáveis aqui são documentos ou artefatos de especificação. O Capítulo 2 vai transformar esta lista em gates e critérios de validação.

### D9.0 — Inspectah Blueprint Consolidado (v1.2.x)

**O que é:**  
Documento mestre do Inspectah, integrando o blueprint v1.2.1 atual com ajustes finais de clareza, cortes de escopo e alinhamento com o Sprint Playbook.

**Para que serve:**  
- É o equivalente, para o Inspectah, do conjunto Blocos 0–5 para o MBP.  
- Serve como "ponto de verdade" sobre o que é o Inspectah, quais problemas resolve, e quais são seus KPIs/SLOs.  
- É o documento que qualquer pessoa lê para entender o produto antes de entrar em anexos e roadmap.

**Como funciona / como é usado:**  
- Referenciado por todos os outros entregáveis de D9.  
- Usado por engenharia para entender o contexto de alto nível antes de ver esquemas e APIs.  
- Usado por stakeholders para validar se o Inspectah, como produto, faz sentido.

### D9.1 — Overview Human‑Friendly do Inspectah

**O que é:**  
Um resumo curto (1–2 páginas) do Inspectah, em linguagem ultra human‑friendly, no mesmo espírito do Bloco 0 do MBP.

**Para que serve:**  
- Onboard rápido de novos membros do time.  
- Explicação de "o que é o Inspectah" sem precisar abrir o blueprint completo.

**Como funciona / como é usado:**  
- Fica como "Bloco 0" do Inspectah.  
- Pode ser colado em apresentações, README e documentos introdutórios.

### D9.2 — Anexo A: Field Designer

**O que é:**  
Especificação detalhada do Field Designer do Inspectah: tipos de campo, transforms, regras de validação, linguagem de computed fields, comportamento em caso de erro.

**Para que serve:**  
- Define com precisão como o Inspectah transforma dados brutos em campos estruturados.  
- Evita divergência entre implementação e intenção de produto (sem "jeitinhos" no código).  
- Dá ao Codex um conjunto claro de contratos para implementar.

**Como funciona / como é usado:**  
- Usado diretamente pelo time de engenharia ao implementar o módulo de Field Designer e o pipeline de indexação.  
- Serve como referência para quem for criar novas fontes e campos (Operators).  
- Será base para futuros testes automatizados de transformação.

### D9.3 — Anexo B: Explore API & Superfícies de Integração

**O que é:**  
Documento definindo as APIs, contratos e superfícies de integração do Inspectah: endpoints de busca, filtros, paginação, export, webhooks e views para consumo por outros sistemas.

**Para que serve:**  
- Garante que o Inspectah é, desde o v0, um **bom cidadão de integração** dentro do ecossistema CE/MBP.  
- Permite que engenheiros de outros módulos planejem integrações sem depender de implementações ad‑hoc.

**Como funciona / como é usado:**  
- Serve de contrato entre Inspectah e consumidores (MBP, scripts internos, BI).  
- Alimenta o superprompt Codex com a lista de endpoints e suas semânticas esperadas.  
- Base para geração de SDKs internos, se necessário.

### D9.4 — Anexo C: Data Model, DDL & Migração

**O que é:**  
Especificação do modelo de dados do Inspectah: esquemas de Source, Item, ItemKV, FTS, Evidence Vault, índices e plano de migração de SQLite v0 para Postgres.

**Para que serve:**  
- Evita decisões improvisadas de modelagem em tempo de implementação.  
- Garante que o modelo suporta os casos de uso definidos no blueprint e nos anexos.  
- Define desde o início caminhos de migração e retenção.

**Como funciona / como é usado:**  
- Base direta para scripts de migration e definição de ORM (se usado).  
- Usado por quem for cuidar de performance, backup/restore e observabilidade.  
- Referenciado por testes de integridade e por qualquer análise de impacto futuro.

### D9.5 — Anexo D: LGPD, ToS & Envelope de Risco

**O que é:**  
Documento definindo as fronteiras legais e éticas de uso do Inspectah: o que pode e o que não pode ser coletado, limites de retenção, tratamento de dados pessoais, respeito a robots.txt e termos de uso.

**Para que serve:**  
- Impede que o Inspectah seja desenhado de forma que dependa de scraping agressivo ou uso indevido de dados.  
- Dá parâmetros claros para decisões de negócio (quais fontes são aceitáveis, quais precisam de acordo formal, etc.).

**Como funciona / como é usado:**  
- Referência obrigatória antes de adicionar uma nova fonte ou tipo de dado.  
- Serve de insumo para contratos, ToS internos e trilhas de auditoria.  
- Orienta futuras sprints de observabilidade e governança.

### D9.6 — Roadmap Inspectah v0 / v1 / v1.x

**O que é:**  
Documento de roadmap específico do Inspectah, descrevendo as ondas de entrega (v0, v1, v1.x), suas metas e dependências, encaixado dentro do roadmap geral de CE/MBP.

**Para que serve:**  
- Tira a especificação do plano abstrato e coloca em **sequência executável de sprints**.  
- Permite priorização explícita (o que entra em v0, o que fica para v1, etc.).

**Como funciona / como é usado:**  
- Usado por PO e engineering lead para planejar sprints futuras.  
- Reforça o corte de escopo IN/OUT decidido neste Capítulo 1.  
- Alimenta o Capítulo 2 com contexto para gates de "pronto para implementar".

### D9.7 — Superprompt Codex v1 — Inspectah v0 (Core Data Hub)

**O que é:**  
Texto de superprompt desenhado para o Codex, descrevendo com precisão o que deve ser implementado no Inspectah v0: serviços, módulos, scripts, testes e convenções, sempre referenciando os documentos D9.0–D9.6.

**Para que serve:**  
- É a "ponte" entre especificação e código.  
- Garante que o Codex não precise adivinhar contexto, endpoints, esquema de dados ou regras de negócio.  
- Dá ao time um ponto de partida replicável para gerar código de alta qualidade.

**Como funciona / como é usado:**  
- Colado diretamente no Codex (VS Code) em uma nova conversa.  
- Pode ser versionado junto com os demais docs de D9.  
- Futuras versões podem ser geradas (v1, v2) mantendo compatibilidade com a base.

### D9.8 — Mini‑Playbook de Evolução do Inspectah

**O que é:**  
Documento curto descrevendo como evoluir o Inspectah após v0: como propor mudanças de schema, como versionar APIs, como introduzir novas fontes e campos sem quebrar o que existe.

**Para que serve:**  
- Evita que o Inspectah vire um "Frankenstein" após as primeiras implementações.  
- Traz para o contexto do Inspectah os aprendizados de governança do MBP.

**Como funciona / como é usado:**  
- Guia para futuras sprints (ex.: quando alguém quiser adicionar novos watchers, novos campos, novas integrações).  
- Referenciado no Capítulo 4 (Lessons Learned) para manter o ciclo virtuoso de melhoria contínua.

---

## 5) Como os entregáveis se encaixam

### 5.1 Mapa D9.x → Pergunta que responde → Verificação futura

| Entregável | Pergunta principal que responde                                           | Este doc prova o quê / viabiliza qual verificação?                      |
|-----------|----------------------------------------------------------------------------|-------------------------------------------------------------------------| 
| D9.0      | "O que é exatamente o Inspectah e quais são seus objetivos/KPIs?"        | Que há uma visão única e consistente do produto, alinhada ao DNA MBP.   |
| D9.1      | "Como explico o Inspectah para alguém novo em 5 minutos?"                | Que o produto é comunicável e compreensível sem ler 50 páginas.        |
| D9.2      | "Como os dados brutos viram campos estruturados de forma segura?"        | Que existe um contrato claro de transformação e validação de campos.    |
| D9.3      | "Como outros sistemas e pessoas consomem os dados do Inspectah?"        | Que há contratos de integração bem definidos (APIs, exports, webhooks). |
| D9.4      | "Como os dados do Inspectah são modelados, indexados e migrados?"       | Que o modelo de dados suporta os casos de uso sem improvisos.           |
| D9.5      | "O que é permitido em termos de dados e de uso de fontes?"              | Que o uso do Inspectah respeita LGPD/ToS e tem limites claros de risco. |
| D9.6      | "Em que ordem construímos tudo isso e o que entra em cada versão?"      | Que existe uma sequência racional de entrega (v0, v1, v1.x).            |
| D9.7      | "Como transformamos esses contratos em código inicial de forma confiável?" | Que há uma ponte robusta entre especificação e implementação.       |
| D9.8      | "Como evoluímos o Inspectah sem destruí‑lo?"                            | Que há uma estratégia explícita de evolução controlada.                 |

### 5.2 Pré‑condições e pós‑condições por grupo de entregáveis

- **Grupo 1 — Visão Macro (D9.0–D9.1)**  
  - Pré‑condições: Blocos 0–5 do MBP consolidados; decisão explícita de que Inspectah é Data Hub + OracleOps interno e não produto público.  
  - Pós‑condições: qualquer pessoa consegue explicar o Inspectah, seus objetivos e KPIs, sem recorrer a conversas soltas; todos os demais entregáveis referenciam essa visão.

- **Grupo 2 — Núcleo Técnico de Dados (D9.2–D9.4)**  
  - Pré‑condições: D9.0–D9.1 escritos e estáveis.  
  - Pós‑condições: há contratos claros para transformação de dados, consumo via APIs e modelagem/armazenamento; engenharia consegue desenhar um schema e um pipeline sem improviso.

- **Grupo 3 — Limites de Risco e Legal (D9.5)**  
  - Pré‑condições: visão macro (D9.0–D9.1) definida; noção inicial de quais fontes se pretende usar.  
  - Pós‑condições: fica claro quais tipos de fonte são aceitáveis, quais exigem acordos formais e quais são proibidas; qualquer decisão de "puxar dados de X" pode ser checada contra este doc.

- **Grupo 4 — Tempo e Evolução (D9.6–D9.8)**  
  - Pré‑condições: D9.0–D9.5 em versão suficientemente estável para planejar em cima.  
  - Pós‑condições: existe uma sequência de sprints e versões para o Inspectah; propostas de mudança futuras têm um lugar e um processo para existir (mini‑playbook).

### 5.3 Métricas citadas no Capítulo 1 e como serão medidas

- **detection_latency** (ex.: detection_latency_p95)  
  - Medida entre o timestamp da fonte (quando disponível) ou da coleta e o momento em que o item é indexado; instrumentada no watcher/indexer.  
- **explore_query_latency** (ex.: explore_query_p95/p99)  
  - Medida como duração de requisições às APIs de Explore; instrumentada no backend.  
- **evidence_completeness**  
  - Proporção de itens considerados "válidos" que possuem HTML/texto/manifest/hash; auditada por scripts de verificação.  
- **field_resolution_success**  
  - Proporção de campos que foram resolvidos com sucesso vs. total de resoluções tentadas; medido no pipeline de Field Designer.

Os detalhes finos (nomes de métricas, buckets, exemplos de dashboards) ficam nos documentos de blueprint/observabilidade, mas o Capítulo 1 garante que **toda métrica citada tem um ponto de medição pensado desde já**.

---

## 6) Exemplos concretos de uso (histórias rápidas)

Para tornar o Capítulo 1 mais tangível, três exemplos simples de como o Inspectah é usado no dia a dia:

1) **Preço médio de um item em diferentes fontes**  
   - Pergunta: "Quanto está, em média, o prato feito na região X nas últimas 2 semanas?"  
   - Uso: Operator cadastra fontes RSS/API de apps de delivery, configura campos `price`, `city`, `category` via Field Designer, e o Requestor usa Explore para filtrar por `category = prato_feito`, `city = X`, intervalo de datas, e exporta um CSV com os preços.  
   - Evidência: cada registro tem manifest + HTML/texto, permitindo auditar de onde saiu cada preço.

2) **Comparar o que mudou em uma fonte específica**  
   - Pergunta: "O que mudou no regulamento da bolsa Y entre ontem e hoje?"  
   - Uso: uma fonte RSS/HTML do regulamento é acompanhada; o Inspectah mantém histórico de itens e evidências; o Requestor filtra por fonte e intervalo de datas e usa a tela de detalhe/diff para ver alterações.  
   - Evidência: snapshots HTML/texto (quando habilitados) permitem comparar versões.

3) **Suporte a uma decisão de resolução de mercado**  
   - Pergunta: "Quais foram as notícias e dados usados para resolver o mercado Z?"  
   - Uso: antes da resolução, o analista monta um conjunto de fontes relevantes (notícias, dados oficiais, APIs); o Inspectah coleta, estrutura e guarda evidências. Na hora da resolução, o oráculo (ou plug-in UMA/Reality, no futuro) referencia os itens do Inspectah como base de evidência.  
   - Evidência: em caso de disputa ou auditoria, é possível ver exatamente quais fontes e versões foram consultadas.

---

## 7) Fechamento do Capítulo 1

Para Leslie (estrutura e coerência):

- D9.0 e D9.1 definem a **visão macro** do produto e sua narrativa.  
- D9.2–D9.5 definem os **subsistemas centrais** (campos, APIs, dados, legal), cada um com pergunta principal e tipo de verificação associado.  
- D9.6 e D9.8 definem o **tempo** (roadmap) e a **evolução** ao longo do tempo, com pré/pós‑condições explícitas.  
- D9.7 é a ponte de especificação → implementação, garantindo que nada se perca na transição.

Para o Sprint Playbook:

- O Capítulo 1 define **contexto, objetivos, escopo e entregáveis**, com exemplos concretos e critérios de versão.  
- O Capítulo 2 (a ser escrito depois) pegará D9.0–D9.8 e os transformará em **gates concretos**: o que significa "feito", como validar, quais evidências guardar.  
- Capítulos 3 e 4 (ORR / Lessons Learned da sprint Inspectah) vão fechar o ciclo, garantindo que tudo que foi aprendido aqui seja reaproveitado no resto do projeto.

Este Capítulo 1 v1.1 serve, portanto, como a "árvore de requisitos" de D9: qualquer trabalho feito nesta sprint deve apontar claramente para pelo menos um dos entregáveis D9.0–D9.8 e, por consequência, para o objetivo macro de levar o Inspectah de ideia a especificação implementável.

