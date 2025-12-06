# Inspectah — Programa 3 v4
## Truth‑DB, Sistema de Blocos, Lógica, Contestação & Memória Evolutiva

> Versão v4 — alinhada ao Roadmap Macro v4 (v2), DNA v2, Sprint Playbook v2 e Lessons Learned. Compatível com o estado atual do projeto (S1–S29 já executadas em P1/P2) e planejada para S30+.

---

## 0. Papel do Programa 3 no Inspectah

O Programa 3 é o **coração jurídico‑lógico** do Inspectah. Ele transforma o que o Programa 2 produz (claims, entidades, ClaimGraph, sinais, logs de agentes) em:

- **estados de verdade versionados**,
- **blocos de fato/evidência/decisão/âncora**,
- **fluxos formais de contestação**,
- **decisões verificadas por lógica formal (E40.5)**,
- **memória evolutiva governada (P3‑E8.5 / SEDM v1)**.

Se o Programa 1 responde a "o que chegou" e o Programa 2 a "o que está sendo afirmado", o Programa 3 responde a "o que o Inspectah considera verdadeiro, falso, incerto ou contestado — e por quê".

---

## 1. Visão

Construir um **Truth‑DB** — um livro‑razão de fatos — em que cada estado de verdade:

1. é derivado de claims e sinais estruturados,
2. respeita **invariantes lógicos** (E40.5),
3. é **versionado e rastreável** por meio de blocos (FactBlocks, EvidenceBlocks, DecisionBlocks, AnchorBlocks),
4. pode ser **contestado, revisado e reancorado**,
5. passa a compor uma **Memória Evolutiva** reutilizável (SEDM v1), feita de Experiências.

O Programa 3 é, ao mesmo tempo:

- uma máquina de estado de verdade;
- um sistema de contestação e revisão;
- um executor de políticas de verdade/contestação;
- um repositório de memória de longo prazo sobre "como chegamos a cada decisão".

---

## 2. Objetivos do Programa 3

1. **Criar o núcleo de lógica & verificação (E40.5)**
   Garantir que decisões críticas de promoção/contestação de verdade não dependam apenas de LLM, mas passem por um **logic‑checker** com políticas formais.

2. **Modelar e implementar o Sistema de Blocos e o Truth‑DB**
   Representar fatos, evidências, decisões e âncoras como blocos versionados, com consultas eficientes.

3. **Definir máquinas de estado de verdade e invariantes**
   Formalizar estados (`uncertain`, `true`, `false`, `contested`, `under_review`) e transições permitidas, supervisionadas por E40.5.

4. **Implementar fluxos de contestação e revisão**
   Permitir que alegações sejam contestadas, reabertas, reavaliadas e reancoradas com trilhas de auditoria fortes.

5. **Criar o Guardião v0**
   Orquestrar comitês de agentes do Programa 2 sob supervisão lógica para tomar decisões de alto impacto.

6. **Acoplar uma camada de Memória Evolutiva (P3‑E8.5 / SEDM v1)**
   Transformar trajetórias de casos em **Experiências** reutilizáveis, com governança forte, sem tocar em pesos de LLM.

7. **Preparar o terreno para governança avançada e Programas futuros**
   Entregar uma base em que conselhos, políticas sofisticadas e meta‑inteligência possam operar com segurança.

---

## 3. Escopo macro do Programa 3

O Programa 3 cobre:

1. **Núcleo de lógica & verificação (E40.5)**
2. **Modelo de blocos e Truth‑DB**
3. **Máquinas de estado de verdade & invariantes**
4. **Fluxos de contestação e revisão**
5. **Anchoring de estados/blocos em blockchain via serviços externos**
6. **Guardião v0 (comitês + lógica)**
7. **Casos/Temas como unidades de primeiro nível**
8. **Memória Evolutiva / SEDM v1 (P3‑E8.5)**
9. **Base para governança avançada de verdade/fato**

Ficam **fora do escopo** de P3:

- ingestão de conteúdo (P1);
- interpretação e construção de ClaimGraph / sinais (P2);
- exposição de UIs/APIs externas (P4);
- definição de políticas públicas, recomendações ou cenários (produtos de camada superior);
- treinamento/tuning de LLMs proprietários.

---

## 4. Macro‑épicos do Programa 3

Usamos rótulos locais `P3‑E#`, com menção ao ID global quando aplicável.

### P3‑E1 / E40.5 — Núcleo de Lógica & Verificação (Logic Engines)

Objetivo: criar o **juiz lógico estrutural** do Inspectah.

Entregas principais:

1. Serviço **logic‑checker** com dois componentes centrais:
   - Claim Logic Checker: validações lógicas sobre claims e casos (consistência temporal, relações básicas, incompatibilidades diretas, coerência mínima entre claims);
   - Truth Policy Engine: executor da **Truth Policy DSL**, que define políticas de promoção/contestação por domínio.

2. Truth Policy DSL mínima:
   - linguagem declarativa simples para expressar regras do tipo:
     - "não promover a `true` sem pelo menos N fontes independentes";
     - "não rebaixar de `true` para `false` sem evidência de contradição forte";
     - "em domínios sensíveis, exigir revisão humana antes da promoção";
   - versionamento explícito (Policy v1, v2, etc.), com histórico de mudanças.

3. Contratos P2 → E40.5 → P3:
   - formato de requisições de sanidade lógica e de aplicação de política;
   - respostas (PASS/FAIL, violações, regras aplicadas, versionamento da policy).

Critérios de pronto:

- Transições críticas de estado em P3 já podem ser negadas ou aprovadas com base em E40.5;
- Há exemplos de políticas reais aplicadas via DSL;
- Logs de E40.5 permitem reconstruir "por que" uma decisão foi tomada ou bloqueada.

---

### P3‑E2 — Modelo de blocos & Truth‑DB base

Objetivo: criar a estrutura de dados que materializa o Truth‑DB.

Entregas principais:

1. Modelo de blocos:
   - FactBlock: representa um fato ou conjunto de fatos atômicos;
   - SubFactBlock: desdobramentos ou componentes de um FactBlock;
   - EvidenceBlock: evidências (documentos, dados, medições) que sustentam FactBlocks;
   - DecisionBlock: decisões de verdade/fato, com referência a políticas aplicadas, resultados de E40.5 e agentes envolvidos;
   - AnchorBlock: registros de ancoragem em blockchain/serviços externos.

2. Estrutura do Truth‑DB:
   - como blocos são armazenados (tabelas/coleções, índices);
   - como são versionados (quem substitui quem, quem complementa quem).

3. APIs internas para CRUD básico de blocos:
   - criar, atualizar (de forma append‑only), consultar por caso/tema/entidade/estado.

Critérios de pronto:

- É possível criar e consultar FactBlocks/EvidenceBlocks/DecisionBlocks para casos piloto;
- O desenho de dados é estável o suficiente para suportar P3‑E3…E8.5.

---

### P3‑E3 — Máquinas de estado de verdade & invariantes

Objetivo: formalizar o ciclo de vida de estados de verdade.

Entregas principais:

1. Definição de estados de verdade:
   - `uncertain`, `true`, `false`, `contested`, `under_review`.

2. Gráficos de transição:
   - quais transições são permitidas (ex.: `uncertain → true`, `true → contested`);
   - quais exigem intervenção humana;
   - quais exigem âncoras adicionais;
   - quais são proibidas.

3. Invariantes em conjunto com E40.5:
   - pré‑condições para cada transição;
   - pós‑condições (o que deve ser verdadeiro depois da transição).

4. Implementação de máquinas de estado:
   - funções/serviços que aplicam transições, chamando E40.5 quando necessário;
   - registro automático em DecisionBlocks.

Critérios de pronto:

- Transições de estado passam por um conjunto mínimo de invariantes formais;
- É possível rejeitar transições inválidas automaticamente com explicação.

---

### P3‑E4 — Contestação v0 & revisão

Objetivo: permitir que estados de verdade sejam contestados e revisados de forma rastreável.

Entregas principais:

1. Modelo de ContestRequest:
   - quem contesta, o que contesta (FactBlock/DecisionBlock), com qual justificativa;
   - anexos de evidência, se houver.

2. Fluxos de contestação:
   - estados de uma ContestRequest (aberta, em análise, aceita, rejeitada, arquivada);
   - relação com novos EvidenceBlocks/DecisionBlocks.

3. Integração com E40.5 e Guardião v0:
   - aplicação de políticas específicas de contestação (ex.: taxas de abuso, prioridades por domínio);
   - orquestração de comitês para casos críticos.

Critérios de pronto:

- Qualquer decisão relevante pode ser contestada com fluxo mínimo funcionando;
- Há registro claro de como uma contestação alterou (ou não) estados de verdade.

---

### P3‑E5 — Anchoring externo

Objetivo: criar ancoragem externa para estados/blocos.

Entregas principais:

1. Seleção de o que ancorar:
   - quais FactBlocks/DecisionBlocks/versões de caso merecem anchoring;
   - critérios por domínio/impacto.

2. Integração com serviços de anchoring:
   - cálculo de hashes;
   - chamadas a APIs/SDKs de anchoring;
   - captura de recibos (tx hashes, proofs).

3. AnchorBlocks:
   - representação interna de ancoragens, com link para blocos ancorados.

Critérios de pronto:

- Há pelo menos um fluxo ponta‑a‑ponta que realiza anchoring para casos piloto;
- É possível provar que um determinado estado de verdade existia em um tempo passado.

---

### P3‑E6 — Guardião v0 & comitês de validação

Objetivo: orquestrar comitês de agentes do Programa 2 para decisões críticas, supervisionadas por E40.5.

Entregas principais:

1. Definição de papéis no Guardião v0:
   - quem propõe decisões;
   - quais agentes participam de cada tipo de decisão;
   - quando exigir revisão humana.

2. Fluxos de decisão:
   - como uma proposta sai de P2 (via signals/logs) e vira uma proposta de promoção/contestação;
   - como o Guardião estrutura a deliberação;
   - como o resultado passa por E40.5 e vira DecisionBlock.

3. Métricas do Guardião v0:
   - tempo médio de decisão;
   - taxa de reversão;
   - domínios com maior volume de contestação.

Critérios de pronto:

- Decisões em domínios piloto passam pelo Guardião v0 em vez de serem tomadas de forma ad‑hoc;
- Há transparência sobre quem decidiu o quê e com base em quais políticas.

---

### P3‑E8 — Casos & Temas estáveis + Contestação/Guardião v0

Objetivo: estabilizar o uso do Truth‑DB por casos/temas prioritários.

Entregas principais:

1. Modelagem de casos/temas como unidades de primeiro nível no Truth‑DB:
   - associação de FactBlocks/EvidenceBlocks/DecisionBlocks a casos/temas;
   - métricas por caso/tema (volume de claims, decisões, contestação, reversão).

2. Operação do Guardião v0 em regime estável:
   - políticas mínimas calibradas por domínio;
   - monitoramento de abuso de contestação.

3. Contestação v0 em produção para domínios prioritários:
   - fluxo ponta‑a‑ponta funcionando para um conjunto significativo de casos.

Critérios de pronto:

- Casos/temas prioritários têm ciclo completo operando (claims → blocos → decisões → contestação → revisão);
- Métricas mínimas de qualidade e desempenho estão sendo coletadas.

---

### P3‑E8.5 — Memória Evolutiva do Inspectah (SEDM v1)

Objetivo: acoplar uma camada de **Memória Evolutiva** ao Truth‑DB, baseada em **Experiências**, sem alterar pesos de LLM.

Entregas principais:

1. Definição de **Experiência**:
   - trajetória de resolução de um caso/tema, incluindo:
     - ingestão relevante (ContentItems);
     - interpretações e claims chave (P2);
     - sinais relevantes (mentiras em circulação, fragilidade, etc.);
     - decisões de verdade (DecisionBlocks), contestação, revisões e anchoring;
     - contexto de fonte (tipos de fontes envolvidas, histórico).

2. **ExperienceStore**:
   - modelo de armazenamento de Experiências;
   - indexação por domínio, tipo de narrativa, padrão de evolução, atores, resultados.

3. **Memory Controller**:
   - políticas de retenção (o que guardar, por quanto tempo);
   - critérios de consolidação (como colapsar Experiências redundantes);
   - mecanismos de anonimização/mascaramento quando necessário.

4. **Replay & Retrieval**:
   - APIs internas para recuperar Experiências relevantes dado um novo caso;
   - mecanismos para sugerir "trajetórias prováveis" ou "armadilhas já vistas".

5. **Janitor/Consolidator**:
   - processos periódicos para limpeza e reindexação da memória;
   - garantia de que a memória permanece útil, enxuta e auditável.

Restrições fortes:

- Nenhuma atualização de pesos de LLM;
- Nenhuma alteração da ingestão 2.0 (P1) ou dos contratos semânticos de P2;
- Nenhum produto final novo em P4 — apenas superfícies internas que P4 **pode** expor mais tarde.

Critérios de pronto:

- É possível registrar e recuperar Experiências para casos piloto;
- O uso da memória é governado (há políticas claras de retenção, uso e privacidade).

---

### P3‑E9+ — Governança avançada de verdade/fato

Objetivo: fornecer base para governança sofisticada em cima de Truth‑DB + E40.5 + SEDM v1.

Entregas principais (nível Programa):

1. Estrutura de conselhos/comitês humanos para domínios sensíveis.
2. Políticas de promoção/contestação por domínio específicas, expressas na Truth Policy DSL.
3. Mecanismos de reputação pesada de fontes/atores (linha de crédito de confiança, histórico de acertos/erros, fragilidade de narrativa, etc.).
4. Controles anti‑captura e anti‑abuso (limites de contestação, proteção contra brigadas coordenadas, etc.).

Critérios de pronto (nível macro):

- É possível definir e aplicar políticas sofisticadas de verdade/fato em domínios prioritários sem violar invariantes;
- O sistema continua auditável e explicável.

---

## 5. Interfaces com Programas 1, 2 e 4

### 5.1 Com Programa 1 — Data Hub

P3 consome de P1, direta ou indiretamente:

- metadados de fonte (Provider/Source);
- país, idioma, tipo de conteúdo;
- timestamps de publicação/coleta e, quando houver, validade;
- indicadores de saúde de fonte.

Essas informações alimentam E40.5 (sanidade básica) e P3‑E8.5 (caracterização de Experiências).

### 5.2 Com Programa 2 — Interpretação, Claims, Entidades & Sinais

P3 é alimentado por P2 com:

- claims estruturadas e ClaimGraph;
- sinais (campo de batalha, mentiras em circulação, fragilidade de narrativa, etc.);
- logs de agentes e trilhas de decisão;
- modelagem de casos/temas.

E40.5 depende de P2 para montar requisições de sanidade e aplicação de política. P3‑E8.5 usa as trajetórias de P2 como parte do tecido de cada Experiência.

### 5.3 Com Programa 4 — Exposição, Produtos, APIs & Uso Responsável

P3 fornece a P4:

- estados de verdade por claim/caso/tema;
- blocos (Fact, Evidence, Decision, Anchor) para UIs e APIs;
- histórico de contestação e revisão;
- resultados de E40.5 (motivos de PASS/FAIL, políticas aplicadas);
- Experiências (via P3‑E8.5) para superfícies avançadas.

P4 decide **como** expor isso, com quais salvaguardas e para quais perfis de usuário.

---

## 6. Restrições e não‑objetivos

1. P3 não faz ingestão de conteúdo — isso é P1.
2. P3 não faz interpretação semântica detalhada nem constrói ClaimGraph — isso é P2.
3. P3 não expõe UIs/APIs externas de produto — isso é P4.
4. P3 não faz tuning de LLMs; usa modelos como serviço.
5. P3 não substitui governança humana; ele a suporta com base lógica, evidencial e de memória.

---

## 7. Critérios macro de "pronto" do Programa 3

Consideramos o Programa 3 "pronto" (v1 estruturante) quando:

1. O núcleo de lógica (E40.5) estiver operando como gate obrigatório para transições críticas de verdade/contestação;
2. O modelo de blocos e o Truth‑DB estiverem estáveis e em uso por casos/temas prioritários;
3. Máquinas de estado de verdade estiverem implementadas e protegidas por invariantes claros;
4. Contestação v0 e Guardião v0 estiverem operando em produção para pelo menos alguns domínios;
5. Anchoring externo estiver disponível para estados/blocos críticos;
6. P3‑E8.5 (Memória Evolutiva / SEDM v1) tiver uma primeira versão funcional, com Experiências registradas e reusadas em casos piloto;
7. Programas 2 e 4 confirmarem que P3 fornece, respectivamente, um backbone sólido de verdade/fato e insumos adequados para explicabilidade e exposição responsável.

A partir daí, sprints futuras passam a focar refinamentos de política, governança avançada, otimização de custo/latência e expansão da Memória Evolutiva, sem quebrar a arquitetura base.

