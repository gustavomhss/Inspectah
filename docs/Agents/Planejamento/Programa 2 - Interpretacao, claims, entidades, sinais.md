# Inspectah — Programa 2 v4
## Interpretação, Claims, Entidades & Sinais

> Versão v4 — alinhada ao Roadmap Macro v4 (v2), DNA v2, Sprint Playbook v2 e Lessons Learned. Compatível com o estado atual do projeto (S1–S29 com partes de P2 já entregues) e preparada para conectar diretamente o Data Hub (P1) ao núcleo de lógica & verdade (E40.5 / Programa 3).

---

## 0. Papel do Programa 2 no Inspectah

O Programa 2 é o **córtex de interpretação** do Inspectah. Tudo que entra pelo Data Hub (Programa 1) é, a partir daqui, transformado em:

- **claims atômicas**,
- **entidades e relações**,
- **grafos de narrativa (ClaimGraph)**,
- **sinais de manipulação, coerência e fragilidade**, e
- **trilhas de decisão de agentes**.

Se o Programa 1 responde a "o que chegou" e "de onde veio", o Programa 2 responde a "o que isso está afirmando" e "como isso se conecta com o restante do mundo".

É também no Programa 2 que se prepara o terreno para:

- o **núcleo de lógica & verificação (E40.5)** — garantindo que os dados estejam em formato "logic‑engine‑friendly"; e
- a **Memória Evolutiva (P3‑E8.5)** — registrando trajetórias de interpretação que poderão ser reutilizadas como Experiências.

---

## 1. Visão

Transformar o Data Hub em um **grafo de narrativa estruturado** — um espaço em que claims, entidades, relações e sinais são objetos de primeira classe, com trilha de decisão clara.

O Programa 2 entrega um ambiente onde:

1. Qualquer ContentItem pode ser decomposto em **claims atômicas** com contexto suficiente.
2. **Entidades** (pessoas, organizações, lugares, leis, eventos) são identificadas e ligadas a claims.
3. Um **ClaimGraph** representa a teia de apoio, oposição, dependência, causalidade e variações de narrativa.
4. **Sinais** sintetizam aspectos relevantes de narrativa: mentiras em circulação, campo de batalha de versões, cherry‑picking, densidade de espuma, etc.
5. **Agentes** (LLMs orquestrados) trabalham em comitês, deixando logs reprodutíveis de decisão.

---

## 2. Objetivos do Programa 2

1. **Extrair claims e entidades de forma robusta**
   - Definir pipelines que transformam texto bruto em claims reutilizáveis e entidades bem resolvidas.

2. **Construir um ClaimGraph navegável**
   - Modelar e persistir relações entre claims, entidades e casos/temas para permitir navegação e análise.

3. **Medir e sinalizar padrões de narrativa**
   - Calcular sinais que ajudem a detectar manipulação, inconsistência, incerteza e conflitos relevantes.

4. **Criar trilhas de decisão auditáveis para agentes**
   - Garantir que cada decisão tomada por agentes LLM possa ser rastreada, auditada e eventualmente contestada.

5. **Preparar dados para lógica formal (E40.5)**
   - Estruturar claims, datas, valores numéricos e relações de modo adequado para motores lógicos e para a Truth Policy DSL.

6. **Alimentar a Memória Evolutiva (P3‑E8.5)**
   - Registrar trajetórias de interpretação de modo que possam ser agrupadas e reutilizadas como Experiências.

---

## 3. Escopo macro do Programa 2

O Programa 2 cobre os seguintes aspectos:

1. **Design e operação de agentes LLM e comitês**
2. **Extração de claims e entidades**
3. **Construção e manutenção do ClaimGraph**
4. **Cálculo de sinais e métricas de narrativa**
5. **Logging e auditoria da atuação de agentes**
6. **Preparação lógica para E40.5 e trilhas para P3‑E8.5**

Ficam **fora do escopo** do Programa 2:

- qualquer promoção de estados de verdade — isso é P3 + E40.5;
- contestação formal e fluxos de revisão — P3;
- ancoragem em blockchain — P3;
- exposição de produtos finais, Fact Cards, dashboards e APIs externas — P4 (embora P2 forneça o conteúdo bruto para isso).

---

## 4. Macro‑épicos do Programa 2

Assim como no Programa 1, usamos rótulos locais `P2‑E#`. A numeração global (E28, E29, …, E40) é detalhada no roadmap.

### P2‑E1 — Runtime de agentes & comitês LLM

**Objetivo:** criar a base operacional para rodar agentes LLM em comitês, com orquestração previsível e observável.

**Entregas principais:**

1. **Catálogo de agentes**:
   - intérprete de conteúdo (transforma texto em rascunho de claims);
   - extrator de entidades;
   - agregador de contexto (busca em bases internas/externas);
   - classificador de tipo de claim/caso;
   - debunker v0;
   - analistas de sinais específicos (ex.: gráfico suspeito, cherry‑picking, etc.).

2. **Runtime de comitês**:
   - definição de fluxos: quem é chamado quando, com que input/output;
   - padronização de chamadas para LLMs (prompt, ferramentas, limites);
   - mecanismos de retry e fallback mínimos.

3. **Logging básico de agentes**:
   - armazenar inputs importantes, outputs e metadados (sem violar privacidade e sem registrar tokens brutos quando não for necessário).

**Critérios de pronto:**

- Pelo menos um fluxo completo de comitê (interpretação básica) rodando ponta‑a‑ponta;
- Logs mínimos disponíveis para reconstruir o caminho de decisão em casos piloto.

---

### P2‑E2 — Extração de claims & entidades

**Objetivo:** transformar ContentItems em claims atômicas, com entidades identificadas e contexto suficiente.

**Entregas principais:**

1. **Esquema de Claim**:
   - texto da claim;
   - tipo (factual, normativo, previsão, citação, etc.);
   - escopo (quem/onde/quando);
   - grau de especificidade;
   - referência ao(s) ContentItem(s) de origem.

2. **Esquema de Entidade** e vinculação a claims:
   - pessoas, organizações, lugares, leis, eventos, instrumentos financeiros, etc.;
   - relações claim‑entidade (sujeito, objeto, local, agente, paciente, etc.).

3. **Pipelines de extração**:
   - rodando sobre ContentItems de tipo notícia, social e oficiais;
   - com mecanismos básicos de dedupe de claims idênticas.

**Critérios de pronto:**

- Conjunto de claims e entidades disponíveis para pelo menos 1–2 domínios temáticos;
- Ligações claim↔ContentItem e claim↔entidade funcionando em consultas simples.

---

### P2‑E3 — ClaimGraph & casos/temas iniciais

**Objetivo:** organizar claims e entidades em grafos de narrativa, por caso/tema.

**Entregas principais:**

1. **Modelo de ClaimGraph**:
   - nós: claims, entidades, casos/temas;
   - arestas: apoio, oposição, dependência, temporalidade, causalidade hipotética, refutação explícita, repetição.

2. **Modelo de Caso/Tema**:
   - agrupamento de claims e entidades em torno de um assunto específico;
   - critério inicial de clustering (por entidade, por assunto, por fonte, etc.).

3. **Operações básicas**:
   - explorar um caso/tema (claims pró/contra, principais entidades, fontes principais);
   - ver cadeia de citações e derivação (quem citou quem, quem distorceu o quê).

**Critérios de pronto:**

- ClaimGraph funcionando para alguns casos piloto;
- Queries básicas (listar claims de um caso, ver claims que contradizem outra claim) respondendo em tempo aceitável.

---

### P2‑E4 — Debunker v0 & sinais de suspeita

**Objetivo:** criar um primeiro nível de debunking automático e detecção de suspeita.

**Entregas principais:**

1. **Agentes debunkers v0**:
   - orientados a encontrar inconsistências óbvias, extrapolações, frases sem base em evidência, uso de estatísticas sem fonte, etc.;
   - operação sempre com log de raciocínio (em nível apropriado) e referência a fontes.

2. **Sinais de suspeita**:
   - flags para claims e ContentItems com indicações de exagero, manipulação óbvia ou lacuna grande de contexto;
   - definição de categorias de suspeita (ex.: clickbait, cherry‑picking de estatísticas, gráficos enganosos).

3. **Integração com ClaimGraph**:
   - registrar sinais no grafo para uso posterior por P3 e por UI de P4.

**Critérios de pronto:**

- Debunker v0 operando em domínios piloto com métricas básicas de performance;
- Sinais sendo gerados e consumidos em pelo menos um fluxo UI ou relatório interno.

---

### P2‑E5 — Motor de Sinais (campo de batalha, mentiras em circulação, etc.)

**Objetivo:** sintetizar, a partir do ClaimGraph e histórico de ContentItems, sinais agregados sobre o estado da narrativa em torno de temas/casos.

**Entregas principais:**

1. **Definição de sinais agregados** (exemplos):
   - mentiras em circulação agora;
   - campo de batalha de versões/narrativas;
   - radar de silêncio (ausência anômala de cobertura);
   - fragilidade de narrativa;
   - densidade de espuma (opinião/reação vs núcleo de dados);
   - índice de cherry‑picking;
   - distorção em tradução entre original e republicações.

2. **Pipelines de cálculo de sinais**:
   - batch (jobs periódicos por caso/tema);
   - on‑demand (consulta sob demanda para casos prioritários).

3. **Armazenamento e exposição interna de sinais**:
   - modelos de dados para sinais por claim/entidade/caso/tema;
   - APIs internas para P3 e P4 consultarem.

**Critérios de pronto:**

- Pelo menos 3–4 sinais implementados e úteis em domínios piloto;
- Documentação clara de como cada sinal é calculado e limitações conhecidas.

---

### P2‑E6 — Logs de agentes & auditoria de fluxos

**Objetivo:** garantir que decisões de agentes possam ser auditadas, reproduzidas e contestadas.

**Entregas principais:**

1. **Modelo de log de agente**:
   - identificação do agente, do fluxo/comitê, do input e do output;
   - metadados de contexto (versão de prompt, ferramentas chamadas, erros);
   - vínculos a ContentItems, claims e casos afetados.

2. **Persistência de logs**:
   - estratégia para balancear custos (o que guardar, por quanto tempo);
   - mecanismos de consulta por caso/tema/claim/agente.

3. **Integração com P3**:
   - fornecer material para que decisões de verdade/contestação possam ser ligadas a trajetórias de interpretação.

**Critérios de pronto:**

- É possível reconstruir o caminho de interpretação de um caso piloto a partir dos logs;
- Há política mínima de retenção e anonimização/mascaramento quando necessário.

---

### P2‑E7 — Preparação lógica para E40.5

**Objetivo:** garantir que o output de P2 esteja pronto para ser consumido pelo núcleo de lógica & verificação.

**Entregas principais:**

1. **Normalização de datas e valores numéricos**:
   - datas em formatos estruturados, com fuso e granularidade conhecidos;
   - valores numéricos com unidades e tipos bem definidos.

2. **Explicitação de relações simples**:
   - "X aconteceu antes de Y", "X implica Y", "X contradiz Y", etc., marcadas de forma clara.

3. **Especificação de contratos P2→E40.5**:
   - formato de requisições de sanidade lógica (por claim/caso);
   - campos obrigatórios e opcionais.

4. **Testes de sanidade pré‑E40.5**:
   - pequenos checks locais (não formais) para reduzir sujeira antes de chegar ao logic‑checker.

**Critérios de pronto:**

- O time de P3 consegue consumir claims/casos de P2 para alimentar E40.5 sem precisar "adivinhar" formatos;
- Erros recorrentes de formatação/ausência de campos críticos foram reduzidos a um nível aceitável.

---

## 5. Interfaces com Programas 1, 3 e 4

### 5.1 Com Programa 1 — Data Hub

- P2 depende de P1 para:
  - ContentItems canônicos com metadados completos;
  - informações de origem (Source/Provider, país, idioma, timestamps);
  - indicadores básicos de saúde de fonte.

- P2 deve ser tolerante a ruído, mas pode recusar/baixar prioridade de ContentItems com metadados insuficientes.

### 5.2 Com Programa 3 — Verdade, lógica & memória

- P3 (incluindo E40.5 e P3‑E8.5) depende de P2 para:
  - claims estruturadas e ClaimGraph;
  - sinais agregados;
  - logs de agentes;
  - representação clara de casos/temas.

- E40.5 consome:
  - claims, relações e valores para sanidade lógica;
  - descrições de casos/temas para aplicar políticas da Truth Policy DSL.

- P3‑E8.5 consome:
  - trajetórias de interpretação (sequência de ContentItems, claims, decisões de agentes, sinais) como matéria‑prima para Experiências.

### 5.3 Com Programa 4 — Exposição & produtos

- P4 consome de P2:
  - ClaimGraph para visualizações de narrativa;
  - sinais para painéis (mentiras em circulação, campo de batalha, etc.);
  - logs de agentes para telas de auditoria.

- P2 não decide **como** esses dados são expostos; apenas garante que estão consistentes e consultáveis.

---

## 6. Restrições e não‑objetivos

1. P2 não decide estados de verdade (`true/false/uncertain/...`). Isso é P3 + E40.5.
2. P2 não implementa sistemas de votação ou governança de verdade. Isso é P3.
3. P2 não gerencia âncoras em blockchain. Isso é P3.
4. P2 não expõe APIs externas de produto (Truth Twin, Explore API, etc.). Isso é P4.
5. P2 não faz tuning próprio de modelos LLM proprietários; usa modelos como serviço.

---

## 7. Critérios macro de "pronto" do Programa 2

Consideramos o Programa 2 "pronto" (em v1 estruturante) quando:

1. ContentItems relevantes de P1 são sistematicamente convertidos em claims/entidades;
2. ClaimGraph funciona para casos/temas prioritários, permitindo navegação básica;
3. Debunker v0 opera com sinais de suspeita úteis em pelo menos alguns domínios;
4. Motor de Sinais produz sinais agregados claros e documentados;
5. Logs de agentes permitem reconstruir o caminho de interpretação de casos relevantes;
6. O núcleo de lógica (E40.5) consegue consumir claims/casos de P2 sem retrabalho estrutural;
7. O Programa 3 (Truth‑DB) e o Programa 4 (Exposição) confirmam que recebem de P2 matéria‑prima suficiente para seus próprios objetivos.

A partir daqui, Programas 3 e 4 devem tratar o Programa 2 como base estabelecida. Qualquer evolução futura de P2 deve respeitar estes contratos em vez de recomeçar do zero.