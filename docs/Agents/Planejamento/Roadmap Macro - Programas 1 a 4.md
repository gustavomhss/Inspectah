# Inspectah — Roadmap Macro v4 (Programas 1–4)

> Versão v4 — revisão v2, pós rodadas de crítica do conselho (Jobs, Lamport, Kleppmann, Percy, Vitalik, Meyer, Pearl, Stonebraker, Norvig, etc.) e alinhada ao DNA v2, Sprint Playbook v2, Lessons Learned e estado atual do projeto (S1–S29 entregues).

---

## 0. Escopo, notação e uso

Este documento é o **mapa macro** dos **Programas 1–4** do Inspectah. Ele não é backlog de sprint, nem spec de implementação; é o "esqueleto" que:

- define **o que** cada Programa precisa entregar para o Inspectah existir como sistema de verdade versionada;
- organiza **épicos estruturais** (incluindo **E40.5 — Núcleo de Lógica & Verificação** e **P3‑E8.5 — Memória Evolutiva / SEDM v1**);
- explicita as **dependências entre Programas** (quem alimenta quem, em que ordem);
- preserva a realidade: **S1–S29 já aconteceram** e não serão reescritas.

### 0.1 Notação de Programas, Épicos e Sprints

- **Programas**: P1, P2, P3, P4 (nomes completos nas seções seguintes).
- **Épicos globais**: `E##` (ex.: E28, E40, **E40.5**). A numeração global é contínua ao longo do projeto e já aparece em vários docs do DNA.
- **Épicos por Programa**: `P{N}-E{X}` (ex.: P1‑E3, P3‑E8.5). Estes são rótulos de leitura local, usados para organizar o texto dentro de cada Programa.
- Quando um épico já tem um **ID global conhecido**, usamos ambos quando fizer sentido, por exemplo: `E40.5 / P3‑E1 — Núcleo de Lógica & Verificação`.

**Sprints** (S1, S2, …) são o ritmo tático de entrega e são planejadas em docs próprios (Sprint Playbook v2). Este roadmap define a **ordem lógica** dos épicos; os mapeamentos finos `Sprint → Trecho de Épico` ficam nos playbooks de cada Sprint.

### 0.2 Situação atual

- S1–S29: consolidadas, com ORR, evidências e histórico.
- Programas 1 e 2: têm partes já implementadas nessas sprints.
- Programas 3 e 4: essencialmente backlog de médio/longo prazo, com alguns conceitos já usados como alinhamento (Truth‑DB, Sistema de Blocos, Debunker v0, etc.).
- Épicos **E40.5 (lógica)** e **P3‑E8.5 (memória)** são **estruturais**, mas **ainda não implementados**; aparecem aqui como norte para S30+.

---

## 1. Decisões estruturantes ("leis da física" do Inspectah)

As decisões abaixo são fundações. Elas restringem o que o Inspectah **não** fará e, portanto, ajudam a cortar escopo e fantasia.

1. **Notícias via news providers**
   - Toda ingestão noticiosa deve passar por agregadores (NewsData, similares). Scrapers HTML são exceções defensivas, com escopo mínimo e monitoramento agressivo.
2. **Social via social providers**
   - O Inspectah não é ferramenta de scraping de rede social. Ele consome social listening/monitoring já prontos e normaliza o output.
3. **Observabilidade em stack pronta**
   - Logs e métricas são responsabilidade do Inspectah; dashboards, storage de métricas, alertas e correlações ficam em stack consolidada (Prometheus, Grafana ou equivalente).
   - Não existe "Inspectah Observability" como produto.
4. **Anchoring via serviços de blockchain**
   - O Inspectah calcula hashes e decide o que ancorar; a interação com redes públicas (Ethereum, etc.) é sempre mediada por serviços/SDKs dedicados.
   - Nada de reinventar consenso, mineração ou node full.
5. **Busca vetorial em vector DB gerenciado**
   - Embeddings vivem em vector DB especializado. O Inspectah decide o que indexar, quais filtros aplicar e como usar, mas não reimplementa índice vetorial.
6. **Comitês de agentes em runtime existente**
   - Interpretação, classificação, análise, debunking e decisão rodam em cima de runtimes (Assistants, LangGraph, etc.).
   - O Inspectah concentra energia em **design de agentes, prompts, ferramentas, fluxos e critérios de decisão**.
7. **Identidade via IdP**
   - Tudo que é login/MFA/reset de senha/token é papel de IdP (Auth0, Cognito, Keycloak, etc.).
   - O Inspectah foca em **autorização de negócio** (quem pode ver o quê, em que granularidade).
8. **Jobs assíncronos em fila/worker padrão**
   - Ingestão batch, reprocessamentos, computações pesadas, bundles de evidência e tarefas de memória rodam em fila + worker clássicos.
9. **Lógica formal via Logic Engines (E40.5)**
   - Decisões críticas de verdade/contestação **não podem depender só de LLM**.
   - A partir do Programa 3, transições relevantes de estado passam por um **núcleo de lógica** (Claim Logic Checker + Truth Policy Engine + DSL mínima) — esse é o papel do **E40.5**.
10. **Memória evolutiva via SEDM v1 (P3‑E8.5)**
    - Aprendizado de longo prazo não é alteração mágica de peso de modelo; é uma camada explícita de **Experiências** (trajetórias de casos) com governança forte, acoplada ao Truth‑DB.

Resultado: o Inspectah é claramente a **estação de tratamento de informação e verdade**, não uma cloud provider, nem um novo Twitter, nem um LLM proprietário, nem um blockchain exótico.

---

## 2. Visão macro dos Programas

### 2.1 Resumo em uma frase

- **Programa 1:** trazer o mundo para dentro, limpo e observável.
- **Programa 2:** transformar conteúdo em narrativa estruturada (claims, entidades, sinais).
- **Programa 3:** transformar narrativa em estados de verdade versionados, verificáveis, contestáveis e com memória.
- **Programa 4:** expor tudo isso para humanos e máquinas, com responsabilidade e explicabilidade.

### 2.2 Alimentação em cadeia

A cadeia lógica é:

`Fontes → Data Hub (P1) → Claims & Sinais (P2) → Lógica + Truth‑DB + Memória (P3) → Produtos & UIs/APIs (P4)`

Cada Programa depende estruturalmente do anterior, mas pode ser desenvolvido com sobreposição no tempo.

---

## 3. Linha do tempo macro & fases

Aqui definimos **fases lógicas**. A alocação fina de sprints dentro de cada fase fica a cargo dos playbooks de sprint (S30+).

### 3.1 Fase 0 — Fundação (S1–S29) — já entregue

- Primeiros épicos de **Programa 1**: modelo canônico de fontes, ingestão de notícias/social, algumas fontes oficiais, fila/worker, observabilidade inicial.
- Construção e maturação progressiva de **Programa 2**: agentes básicos, extração de claims, ClaimGraph inicial, primeiros sinais, Debunker v0 em domínios piloto.
- Consolidação do DNA, Sprint Playbook, gates de ORR, pipelines de CI e do próprio conceito de "evidência" no projeto.

O Roadmap v4 **não reescreve** S1–S29. Tudo que diz respeito a E40.5, P3 e P4, Memória Evolutiva, etc. é **camada futura**.

### 3.2 Fase 1 — Programa 2 completo & dobradiça lógica (E40 → E40.5)

Objetivo: fechar Programa 2 e ligar sua saída a um juiz lógico estrutural.

- Fechamento dos épicos finais de **Programa 2 (até E40)**:
  - ClaimGraph robusto e navegável por caso/tema/entidade;
  - Motor de Sinais operando em batch e sob demanda (mentiras em circulação, campo de batalha de versões, radar de silêncio, densidade de espuma, etc.);
  - Debunker v0 plugado no fluxo principal de interpretação;
  - logs de agentes e trilhas de decisão completas.
- Início de **Programa 3** com o épico **E40.5 / P3‑E1 — Núcleo de Lógica & Verificação (Logic Engines)**:
  - criação do **logic‑checker** (Claim Logic Checker + Truth Policy Engine);
  - definição da **Truth Policy DSL** mínima (políticas de verdade/contestação versionadas e auditáveis);
  - contratos P2→E40.5: toda proposta de promoção/contestação relevante vira requisição lógica.

Resultado da fase: a saída de P2 deixa de ir "direto" para Truth‑DB; passa antes pelo E40.5. O sistema ganha uma primeira camada de **invariantes formais**.

### 3.3 Fase 2 — Truth‑DB, Blocos & Contestação v0

Objetivo: materializar o livro‑razão de fatos.

- Épicos centrais de **Programa 3**:
  - modelo de FactBlock/SubFactBlock/EvidenceBlock/DecisionBlock/AnchorBlock;
  - implementação das máquinas de estado de verdade (`uncertain`, `true`, `false`, `contested`, `under_review`);
  - Contestação v0 (ContestRequest, fluxos de reabertura, novas decisões, vinculação a novas evidências);
  - integração com serviços de anchoring em blockchain.
- **Guardião v0**: orquestração de comitês de agentes (P2) para decisões propostas, sempre submetidas a E40.5 antes de virar DecisionBlocks.

Resultado: o Inspectah passa a ter um Truth‑DB funcional, com histórico de decisões, contestação básica e âncoras externas.

### 3.4 Fase 3 — Casos/Temas estáveis + P3‑E8.5 Memória Evolutiva (SEDM v1)

Objetivo: estabilizar operação por casos/temas prioritários e acoplar uma camada de memória evolutiva.

1. **P3‑E8 — Casos & Temas + Contestação/Guardião v0 estáveis**
   - consolidação de casos/temas como unidades de primeiro nível;
   - contestação v0 operando com métricas de volume, tempo, reversão e abuso;
   - Guardião v0 configurado por domínio, com thresholds e políticas mínimas estáveis.

2. **P3‑E8.5 — Memória Evolutiva do Inspectah (SEDM v1)**
   - definição de **Experiência** como trajetória de resolução de caso/tema ao longo do tempo (ingestão, interpretação, sinais, decisões, contestação, reaberturas, âncoras, mudanças de estado de verdade);
   - **ExperienceStore**: estrutura para armazenar Experiências com indexação forte (domínio, tipo de narrativa, fontes, sinais, decisões e reversões);
   - **Memory Controller**: políticas sobre o que guardar, consolidar, descartar ou reindexar; controles de anonimização quando necessário;
   - **Replay & Retrieval**: capacidade de, dado um novo caso, recuperar Experiências relevantes ("casos parecidos" como templates);
   - **Janitor/Consolidator**: processos periódicos para limpar ruído, colapsar trajetórias redundantes e garantir que a memória seja útil e sustentável.

Restrições: P3‑E8.5 não mexe em pesos de LLM, não redesenha ingestão 2.0, não cria produto final em P4. É infra de memória governada acoplada ao P3.

### 3.5 Fase 4 — Governança avançada & exposição profunda

Objetivo: erguer a camada de governança pesada e exposição rica para diversos perfis de usuário.

- Em **Programa 3**:
  - governança de verdade/fato com conselhos/comitês humanos;
  - políticas de promoção/contestação por domínio sensível;
  - mecanismos de reputação pesada de fontes e atores (linha de crédito de confiança, fragilidade de narrativa, etc.);
  - uso explícito de Experiências (P3‑E8.5) para calibrar políticas.

- Em **Programa 4**:
  - UIs e APIs para explicabilidade (por que uma transição foi aceita/negada, qual política/versão foi aplicada, que invariantes foram checados em E40.5);
  - exposição governada da Memória Evolutiva (playbooks de casos, estratégias típicas de manipulação, etc.);
  - produtos avançados: painéis de governança, simuladores de políticas, perfis de fonte/tema com histórico de acertos/erros.

---

## 4. Programa 1 — Data Hub, Fontes, Ingestão & Operação 24/7

### 4.1 Objetivo consolidado

Construir um **Data Hub 24/7** que ingere, normaliza e torna observável todo conteúdo relevante, com rastreabilidade completo: sabemos **de onde veio**, **como entrou**, **com que qualidade** e **onde está falhando**.

### 4.2 Macro‑épicos (nível Programa)

- **P1‑E1 — Modelo canônico de Provider/Source/ContentItem**
  - Esquemas, relacionamentos, estados de fonte (ativo, pausado, deprecado), tipos de conteúdo e contratos mínimos.

- **P1‑E2 — Ingestão de notícias via news providers**
  - Profiles por país/idioma/tema, normalização, dedupe, tratamento de limites de rate.

- **P1‑E3 — Ingestão social via social providers**
  - Profiles (hashtags, contas, termos), normalização de posts, anexos e métricas.

- **P1‑E4 — Ingestão de fontes oficiais & batch**
  - APIs de governo/agências, diários oficiais, datasets versionados, IBGE, BC, etc.

- **P1‑E5 — Scrapers de exceção & proteção contra quebra**
  - Scrapers apenas para fontes sem alternativa, com monitoramento de layout e fallback.

- **P1‑E6 — Infra de fila/worker & scheduling**
  - Tipos de job, prioridades, retries, backoff, dead letters, agendamentos.

- **P1‑E7 — Observabilidade da ingestão & saúde de fontes**
  - Métricas por fonte, latência, vazão, erros, dashboards de saúde, alertas.

- **P1‑E8 — Console de Fontes & Operação 24/7**
  - UI de cadastro, edição, pausa, histórico de mudança e tracking de incidentes.

### 4.3 Interfaces & dependências

- Entrega principal: **ContentItems canônicos** + metadados ricos para P2.
- Metadados de fonte, país, idioma, tempo, tipo de conteúdo, saúde e histórico de incidentes são consumidos por:
  - **E40.5** (sanidade lógica básica: datas possíveis, intervalos coerentes, valores numéricos plausíveis);
  - **P3‑E8.5** (caracterização de Experiências por tipo de fonte e comportamento histórico).

---

## 5. Programa 2 — Interpretação, Claims, Entidades & Sinais

### 5.1 Objetivo consolidado

Transformar o Data Hub em um **grafo de narrativa** — claims atômicas, entidades, relações e sinais de manipulação/consistência — com trilha de decisão auditável.

### 5.2 Macro‑épicos (nível Programa)

- **P2‑E1 — Runtime de agentes & comitês LLM**
  - Papéis de agentes, prompts, ferramentas, fluxos, orchestration e logging básico.

- **P2‑E2 — Extração de claims & entidades**
  - Pipelines para decompor ContentItems em claims atômicas, entidades e relações.

- **P2‑E3 — ClaimGraph & casos/temas iniciais**
  - Grafo de claims por caso/tema, com tipos de relação (apoio, oposição, dependência, temporalidade, causalidade hipotética).

- **P2‑E4 — Debunker v0 & sinais de suspeita**
  - Agentes focados em detectar incoerências, lacunas, cherry‑picking, distorção gráfica, cortinas de fumaça, etc.

- **P2‑E5 — Motor de Sinais (campo de batalha, mentiras em circulação, etc.)**
  - Cálculo de sinais batch e on‑demand por claim/entidade/caso/tema (mentiras em circulação agora, campo de batalha de versões, radar de silêncio, fragilidade de narrativa, densidade de espuma, etc.).

- **P2‑E6 — Logs de agentes & auditoria de fluxos**
  - Estrutura de logs que permite reconstruir quem rodou o quê, com quais inputs/outputs, sob quais condições.

- **P2‑E7 — Preparação lógica para E40.5**
  - Garantir que claims, entidades, datas, valores numéricos e relações saiam de P2 em formato "logic‑engine‑friendly" para o Claim Logic Checker.

### 5.3 Interfaces & dependências

- P2 consome P1 (ContentItems) e produz para P3:
  - claims estruturadas, ClaimGraph;
  - sinais;
  - trilhas de decisão de agentes.

- **E40.5** consome diretamente esses outputs para:
  - sanidade lógica de claims/casos;
  - aplicação da Truth Policy DSL em transições de estado.

- **P3‑E8.5** consome as trajetórias de P2 como parte de cada Experiência armazenada.

---

## 6. Programa 3 — Truth‑DB, Sistema de Blocos, Contestação, Lógica & Memória

### 6.1 Objetivo consolidado

Transformar o ClaimGraph e sinais em um **livro‑razão de fatos**: estados de verdade versionados, contestáveis, auditáveis, verificados logicamente e com memória evolutiva governada.

### 6.2 Macro‑épicos (nível Programa)

- **E40.5 / P3‑E1 — Núcleo de Lógica & Verificação (Logic Engines)**
  - Serviço logic‑checker com:
    - Claim Logic Checker (validações lógicas sobre claims/casos);
    - Truth Policy Engine (execução de políticas da Truth Policy DSL);
  - Integração com P2 para receber propostas de promoção/contestação;
  - Contrato: transições críticas de estado **não acontecem** sem passar por E40.5.

- **P3‑E2 — Modelo de blocos & Truth‑DB base**
  - Implementação de FactBlock, SubFactBlock, EvidenceBlock, DecisionBlock, AnchorBlock;
  - Persistência, versionamento e consultas básicas.

- **P3‑E3 — Máquinas de estado de verdade & invariantes**
  - Estados `uncertain`, `true`, `false`, `contested`, `under_review`;
  - Transições válidas e invariantes, em conjunto com E40.5.

- **P3‑E4 — Contestação v0 & revisão**
  - ContestRequest, reaberturas, nova decisão, vinculação a novas evidências, trilha de contestação.

- **P3‑E5 — Anchoring externo**
  - Seleção de blocos/estados para anchoring, cálculo de hashes, integração com serviços de blockchain.

- **P3‑E6 — Guardião v0 & comitês de validação**
  - Orquestração de comitês de agentes (P2) para decisões, supervisionados por E40.5, com logging forte.

- **P3‑E8 — Casos & Temas estáveis + Contestação/Guardião v0**
  - Estabilização da operação por casos/temas prioritários;
  - Métricas de uso, reversão, abuso e tempo de revisão;
  - Hardening de política mínima por domínio.

- **P3‑E8.5 — Memória Evolutiva do Inspectah (SEDM v1)**
  - Definição de Experiência, ExperienceStore, Memory Controller, Replay & Retrieval, Janitor/Consolidator (como descrito na Fase 3);
  - Restrições fortes: sem mexer em pesos de LLM, sem redesenhar ingestão, sem produto novo em P4.

- **P3‑E9+ — Governança avançada de verdade/fato & políticas sofisticadas**
  - Conselhos, reputação pesada, políticas por domínio, anti‑captura, etc., sempre construídos sobre Truth‑DB + E40.5 + P3‑E8.5.

### 6.3 Interfaces & dependências

- P3 é alimentado por P2 e supervisionado por E40.5.
- Depende de P1 para metadados de fonte/tempo e de P2 para ClaimGraph/sinais.
- **Experiências de P3‑E8.5** alimentam futuras decisões de P3 e superfícies avançadas de P4.

---

## 7. Programa 4 — Exposição, Produtos, APIs & Uso Responsável

### 7.1 Objetivo consolidado

Tornar o Inspectah **usável, auditável e seguro** para humanos e sistemas externos, sem trair a filosofia de verdade versionada, contestável e explicável.

### 7.2 Macro‑épicos (nível Programa)

- **P4‑E1 — Identidade, autenticação & autorização fina**
- **P4‑E2 — Gateways de API & contratos**
- **P4‑E3 — Cockpits internos (Fontes, Casos, Operação)**
- **P4‑E4 — Truth Twin API, Explore API & APIs de casos/verdades/sinais**
- **P4‑E5 — Produtos derivados (Fact Cards, relatórios, dashboards)**
- **P4‑E6 — Uso responsável & salvaguardas**
- **P4‑E7 — Explicabilidade de decisões & exposição do logic‑checker (E40.5)**
  - Mostrar razões de PASS/FAIL, políticas aplicadas, versão da política, invariantes avaliados.
- **P4‑E8 — Exposição de Memória Evolutiva (P3‑E8.5)**
  - Expor, quando habilitado:
    - histórico de aprendizado por caso/tema;
    - Experiências similares usadas como referência;
    - padrões de narrativa/estratégia identificados.

### 7.3 Interfaces & dependências

- P4 depende de:
  - P1 para visão de ingestão e saúde de fontes;
  - P2 para grafos e sinais (campo de batalha, radar de silêncio, etc.);
  - P3 para estados de verdade, blocos, decisões, contestação e âncoras;
  - E40.5 para resultados do logic‑checker;
  - P3‑E8.5 para superfícies de Memória Evolutiva.

---

## 8. Critérios macro de "pronto" deste Roadmap v4

Este roadmap macro é considerado consistente quando:

1. Programas 1–4 têm objetivos claros, escopos não sobrepostos e macro‑épicos identificáveis.
2. E40.5 aparece como **épico estrutural de entrada do Programa 3**, sempre que se fala em transição crítica de verdade/contestação.
3. P3‑E8.5 aparece como **épico intermediário de Memória Evolutiva**, sempre que se fala em aprendizado estruturado de longo prazo.
4. Programas 1 e 2 são descritos como **fornecedores de matéria‑prima** (dados, claims, sinais, trilhas) para lógica (E40.5) e memória (P3‑E8.5), sem inflar escopo.
5. Programa 4 reconhece que explicabilidade e governança incluem **resultados do logic‑checker** e, quando existir, **Memória Evolutiva**.
6. Nenhum trecho contradiz ou reescreve S1–S29; tudo que depende de E40.5 e P3‑E8.5 é explicitamente futuro.
7. A narrativa inteira é compatível com o DNA v2, Sprint Playbook v2 e Lessons Learned, e pode servir de base para planejar Programas e Sprints sem gerar ambiguidades grosseiras.

