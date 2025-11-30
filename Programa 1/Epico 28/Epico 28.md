# Épico E28 — Fluxo de Agentes Configurável v1 (Orquestração Operacional)

> Programa 1 — Consolidação & Consoles Full  
> Dono lógico: Squad Fluxos & Orquestração (Percy Liang, Michael Stonebraker, Kelsey Hightower, Charity Majors, Kent Beck, Steve Jobs)

---

## 1. Identidade do épico

**Código:** E28  
**Nome curto:** Fluxo de Agentes Configurável v1  
**Programa:** Programa 1 — Consolidação & Consoles Full (S26–S32)  
**Status:** Em design  

**Resumo em uma frase:**

> E28 garante que o Inspectah tenha um modelo único, configurável e operável de fluxos de agentes — um "pipeline lógico" onde interpretadores, classificadores, analistas, debunkers e decision makers são conectados em sequência, com estados visíveis e botões claros para operar, pausar, reprocessar e versionar esses fluxos.

---

## 2. Problema

Sem E28, o risco é que o "cérebro de agentes" do Inspectah nasça como um amontoado de prompts e scripts difíceis de rastrear:

- Cada agente (intérprete, classificador, organizador, debunker, etc.) pode ser instanciado de forma isolada, sem um modelo unificado de fluxo.  
- A ordem em que agentes são chamados, as condições de passagem e os estados intermediários tendem a morar na cabeça de quem implementou, não em uma estrutura clara.  
- Operadores não têm visibilidade sobre "o que acontece com uma notícia" da entrada até a decisão final – muito menos controle operacional (pausar um trecho do fluxo, desviar, reprocessar, trocar um nó).  
- Ajustes finos (ex.: trocar um classificador por outro, introduzir um segundo debunker em paralelo) implicam mexer em código, não em uma configuração estável.  
- Auditoria e explicabilidade ficam fracas: é difícil provar qual caminho uma entrada seguiu, quais agentes a tocaram, quais outputs foram usados para a decisão final.

E28 existe para matar esse caos antes que ele vire normal. Ele cria o **modelo de Fluxo de Agentes v1** e a camada de orquestração operacional: quem chama quem, em que ordem, como versionar e como enxergar isso.

Importante: E28 não tenta resolver a "inteligência" interna de cada agente (prompts, políticas, comitês complexos) – isso é Programa 2. Aqui o foco é **pipe, wiring, estado e operação**.

---

## 3. Visão & Estado-alvo do épico

### 3.1 Frase de visão

> Quando E28 estiver completo, qualquer operador consegue abrir o Console de Fluxos de Agentes e ver um diagrama lógico com entradas, etapas e saídas, sabendo quais agentes compõem cada etapa, qual o estado atual do fluxo, quais execuções passaram por ali e quais botões pode apertar para operar esse fluxo com segurança.

### 3.2 Estados-alvo (lista canônica)

Ao final de E28, será verdade que:

1. **Existe um modelo único de Fluxo de Agentes v1**, com entidades claras (Fluxo, Etapa, Nó de Agente, Entrada, Saída, Estado de Execução).
2. **Cada tipo de informação processada pelo Inspectah** (ex.: notícia de fonte RSS, documento oficial, contestação de fato, etc.) está ligado a **um ou mais fluxos declarados**, em vez de roubar caminhos ad hoc em código.
3. **O Console de Fluxos de Agentes** exibe, para cada fluxo, a sequência de etapas e quais agentes compõem cada etapa, com estados (ativo, pausado, em teste, deprecado).
4. **Execuções de fluxo são rastreáveis**, com logs básicos de passagem por cada etapa: qual agente respondeu o quê, qual foi o status e qual foi a próxima etapa tomada.
5. **Operadores podem pausar, retomar e forçar reprocessamentos em fluxos específicos**, respeitando limites de segurança e sem precisar tocar código.
6. **Trocas simples na topologia de um fluxo** (ex.: substituir um classificador, acrescentar um segundo debunker em paralelo) podem ser feitas via configuração controlada, com versionamento e rollback, não via patch manual em múltiplos serviços.
7. **O estado de saúde dos fluxos de agentes é visível**, com métricas mínimas (sucesso/falha por etapa, latência, backlog de itens em cada etapa, etc.), integrado à camada de observabilidade de Programa 7.

Esses estados são o contrato do épico. Sprints que mexerem com Fluxos de Agentes devem sempre apontar para quais dessas frases estão tornando verdade.

---

## 4. Escopo IN / OUT

### 4.1 Escopo IN

E28 cobre, no mínimo:

- Definição do **Modelo de Fluxo de Agentes v1**:
  - Entidades: Fluxo, Etapa, Nó de Agente, Conexões, Entrada, Saída, Execução de Fluxo, Execução de Etapa.  
  - Propriedades mínimas de cada entidade (ver seção 7).

- Modelagem dos **fluxos principais** (v1) do Inspectah, por exemplo:
  - Fluxo "Notícia política": Intérprete → Classificador de tipo → Classificador de entidades → Analistas (3) → Debunkers (2) → Decision Maker.  
  - Fluxo "Contestação de verdade": Intake → Normalizador → Debunker 1 → Debunker 2 → Comitê → Registro no Truth-DB (escopo Fase 2, mas caminho já descrito).  
  - Fluxo "Evento de dados quantitativos" (ex.: IBGE): Ingestão → Normalização → Validador de consistência → Anotador de metadados.

- Criação do **Console de Fluxos de Agentes** (UI/Admin), aderente a E26:
  - Lista de fluxos (nome, tipo de entrada, dono, estado, última execução, saúde).  
  - Tela de detalhe com diagrama lógico (etapas em sequência, ligações, nós de agente).  
  - Visualização básica de execuções recentes (timeline de etapas, status, erros principais).

- Definição das **operações básicas de fluxo**:
  - criar fluxo novo a partir de templates;  
  - alterar topologia de fluxo (dentro de limites de segurança definidos);  
  - pausar/retomar fluxo;  
  - marcar fluxo como "em teste" (sandbox) vs "produção";  
  - disparar reprocessamento limitado de itens (com proteção de volume).

- Integração com **agentes concretos** enquanto "caixas pretas":
  - E28 trata agentes como nós com contratos simples (input, output, erro);  
  - detalhes de prompt, temperatura, comitês internos pertencem a Programa 2, mas E28 precisa ter um ID/descritor estável para cada agente.

### 4.2 Escopo OUT

E28 **não** cobre:

- Design interno dos agentes (prompts, políticas, heurísticas, comitês complexos) – isso é Programa 2 (Agent Brain & Committees).  
- Sistema de versões avançado de pipelines em produção com canary, experimentos A/B e rollout progressivo – isso é Programa 7.  
- UI avançada de explicabilidade (árvore de raciocínio detalhada) – parte cai em Programas 3 e 5.  
- Integração com múltiplos provedores de LLM e seleção dinâmica de modelo – isso é Fase posterior.

---

## 5. Personas & casos de uso

### 5.1 Personas

- **Arquiteto de Fluxos de Agentes** — define como eventos de informação são processados, qual a sequência de agentes, que estados intermediários são gerados.
- **Operator de Fluxos** — acompanha estado operacional dos fluxos, trata erros e faz ajustes pequenos (pausar, retomar, reprocessar).
- **Debunker / Analista** — se beneficia de ver o caminho que uma entrada percorreu, mesmo não configurando fluxos diretamente.
- **SRE/Observability** — precisa correlacionar problemas de fluxo com infra, ingestão, LLMs e bancos.

### 5.2 Casos de uso principais

1. **Criar um fluxo padrão para notícias**
   - Arquiteto abre Console de Fluxos.  
   - Cria novo fluxo "Notícias gerais" baseado em template (entrada: notícia; etapas: intérprete → classificador de tipo → analista → debunker → decisão).  
   - Escolhe agentes específicos para cada etapa, dentro de um catálogo existente.  
   - Marca fluxo como "em teste" e direciona um subconjunto de inputs para ele.

2. **Entender por que uma notícia foi marcada como "falsa"**
   - Debunker abre detalhe da notícia em outro console (E29/E30).  
   - Clica em "Ver fluxo de agentes".  
   - Vê a trilha de etapas percorridas, com outputs resumidos de cada agente.  
   - Consegue apontar um possível erro de configuração ou inferência.

3. **Pausar fluxo que está gerando decisões ruins**
   - Operador vê que determinado fluxo está com muitos erros/decisões contestadas.  
   - Abre o fluxo no Console de Fluxos.  
   - Usa ação "Pausar" (novo conteúdo não passa por esse fluxo até nova ordem).  
   - Redireciona entradas para fluxo alternativo ou caminho de fallback.

4. **Trocar agente de uma etapa sem reescrever o sistema**
   - Arquiteto percebe que classificador atual performa mal em certo domínio.  
   - No Console, edita configuração da etapa de classificação, trocando agente A por agente B.  
   - Salva nova versão do fluxo e, se for permitido, aplica imediatamente ou agenda troca.

---

## 6. Modelo conceitual de Fluxo de Agentes v1

### 6.1 Entidades principais

- **Fluxo**  
  Representa um pipeline lógico completo (ex.: Fluxo_Noticias_Politica_v1).

- **Etapa**  
  Representa um passo dentro do fluxo (ex.: Interpretação, Classificação de tipo, Debunking).

- **Nó de Agente**  
  Representa uma instância lógica de agente em uma etapa (ex.: `agent_interpreter_v1`, `agent_classifier_v2`).

- **Conexão**  
  Regras de passagem entre etapas (ex.: sempre, condicional, em paralelo).

- **Execução de Fluxo**  
  Representa o caminho real de uma entrada pelo fluxo (instância). 

- **Execução de Etapa**  
  Representa o resultado de uma etapa específica na execução de fluxo.

### 6.2 Propriedades mínimas (nível lógico)

**Fluxo**

- `id`  
- `nome`  
- `slug`  
- `tipo_entrada` (ex.: `noticia_texto`, `contestacao`, `evento_dado`)  
- `versao`  
- `estado` (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`)  
- `owner` (squad/responsável)  
- `created_at`, `updated_at`.

**Etapa**

- `id`  
- `fluxo_id`  
- `ordem` (ou estrutura de grafo com topologia mais rica)  
- `tipo` (`interpretacao`, `classificacao`, `analise`, `debunking`, `decisao`, etc.)  
- `descricao`  
- `nodo_principal_id` (Nó de Agente default)  
- `nodos_auxiliares_ids` (opcional: agentes em paralelo, comitês, etc.).

**Nó de Agente**

- `id`  
- `tipo` (`gpt_llm`, `rule_engine`, `script_custom`)  
- `agent_ref` (referência estável para definição do agente em Programa 2)  
- `config_execucao` (timeout, limites de token, política de retry, etc.).

**Execução de Fluxo**

- `id`  
- `fluxo_id`  
- `entrada_ref` (referência para item de dados: notícia, contestação, etc.)  
- `timestamp_inicio`, `timestamp_fim`  
- `status` (`sucesso`, `falha`, `parcial`, `cancelado`)  
- `etapa_final_id`  
- `motivo_falha` (quando aplicável).

**Execução de Etapa**

- `id`  
- `exec_fluxo_id`  
- `etapa_id`  
- `nodo_agente_id`  
- `timestamp_inicio`, `timestamp_fim`  
- `status`  
- `resumo_output` (texto sintético ou referência)  
- `erro` (quando falha).

---

## 7. Requisitos funcionais

### 7.1 Console de Fluxos de Agentes

- Tela de **lista de fluxos**, com:
  - nome;  
  - tipo de entrada;  
  - versão;  
  - estado;  
  - owner;  
  - health_status (quando aplicável);  
  - data da última execução e status agregado (sucesso/falha).  
- Filtros por estado, tipo de entrada, owner, criticidade, health_status.

- Ações rápidas por fluxo: abrir detalhe, pausar, retomar, clonar, marcar como em teste.

### 7.2 Detalhe do fluxo (diagrama lógico)

- Visualização textual/diagramática da sequência de etapas.  
- Para cada etapa:  
  - tipo, agente principal, agentes auxiliares;  
  - se gera estados intermediários persistidos;  
  - se tem condições de roteamento (ex.: se output X → etapa Y, senão → Z).

- Aba de **execuções recentes**:  
  - listar últimas N execuções, com status, tempo, erro principal (se houver);  
  - permitir abrir uma execução para ver etapa por etapa.

### 7.3 Operações sobre fluxos

- Criar fluxo novo (possivelmente a partir de template).  
- Editar fluxo:  
  - adicionar/remover etapas;  
  - trocar agente de uma etapa;  
  - alterar parâmetros operacionais (timeout, política de retry).  
- Pausar/retomar fluxo (não processar novas entradas enquanto pausado).  
- Marcar fluxo como "em teste" e gerenciar roteamento parcial de entradas (ex.: 5% das notícias passam pelo fluxo de teste).  
- Clonar fluxo (criar nova versão a partir da atual).

### 7.4 Rastreamento de execuções

- A partir de um item (ex.: notícia), deve ser possível:
  - ver qual fluxo a processou;  
  - ver quais etapas foram executadas;  
  - ver outputs/resumos de cada agente (com nível de detalhe compatível com Fase 1);  
  - identificar em qual etapa ocorreu falha (se ocorreu).

- A partir do Console de Fluxos, deve ser possível:
  - abrir uma execução específica;  
  - navegar pelas etapas com timestamps e status.

---

## 8. Requisitos não funcionais

### 8.1 Observabilidade

- Métricas mínimas por fluxo:
  - `fluxo_execucoes_total`;  
  - `fluxo_execucoes_falha_total`;  
  - `fluxo_execucoes_sucesso_total`;  
  - `fluxo_latencia_p95`;  
  - `fluxo_backlog_itens` (quando aplicável).

- Métricas mínimas por etapa:
  - latência média/p95;  
  - taxa de falha por etapa.

- Logs estruturados por execução de etapa, com correlação via IDs.

### 8.2 Resiliência

- Proteções contra:
  - loops de fluxo (ciclos não intencionais);  
  - tempestades de retries;  
  - fluxos que consomem recursos demais (limites por fluxo).

### 8.3 Consistência com E26

- O Console de Fluxos deve seguir a gramática de UI/Admin de E26:  
  - mesma estrutura base;  
  - mesma linguagem de estados (ativo, pausado, erro);  
  - componentes de tabela, cards, states reaproveitados.

---

## 9. Métricas de sucesso do épico

- **Porcentagem de fluxos operando via modelo E28** (vs lógica ad hoc em código).  
- **Tempo médio para um operador entender um fluxo** (do zero até conseguir explicá-lo) – deve cair com o Console de Fluxos.  
- **Tempo para pausar/retomar um fluxo problemático** (sem deploy) – alvo de minutos, não horas.  
- **Quantidade de incidentes de "fluxo caixa preta"** reduzida.  
- **Número de mudanças de topologia de fluxo por configuração** (sem toque em código) – indicador de flexibilidade do modelo.

---

## 10. Decomposição em sprints

### 10.1 Entregas sugeridas

- **E28.1 — Modelo de Fluxo v1 + entidades básicas + API interna**  
  - Definição de entidades Fluxo, Etapa, Nó de Agente, Execução de Fluxo/Etapa;  
  - endpoints básicos para listar/criar/editar fluxos;  
  - sem UI avançada ainda.

- **E28.2 — Console de Fluxos + visualização de execuções**  
  - UI/Admin aderente a E26;  
  - listagem de fluxos, detalhe com diagrama textual, execuções recentes;  
  - ações básicas de pausar/retomar.

- **E28.3 — Operação diária & pequenas mutações de topologia**  
  - templates de fluxo;  
  - troca de agentes por configuração;  
  - flags de "em teste" vs "produção";  
  - integrações com observabilidade básica.

### 10.2 Relação com sprints S26–S32

- S26–S27: podem entregar E28.1 (modelo + APIs internas), já acoplado a um fluxo simples de notícias.
- S28–S29: focam em E28.2 (Console de Fluxos aderente a E26, visualização de execuções).  
- S30–S32: refinam E28.3 e alinham o modelo de fluxos com o desenho mais profundo de agentes/committees do Programa 2.

---

## 11. Riscos, decisões e anti-objetivos

### 11.1 Riscos

- **Complexidade exagerada cedo demais**: tentar modelar todos os casos de fluxo (incluindo branching complexo, loops avançados, dynamic routing pesado) e nunca sair do papel.  
- **Acoplamento forte com Programa 2**: misturar detalhes de inteligência do agente com o modelo de fluxo, travando ambos.
- **UI de fluxo que tenta ser um editor visual completo** (tipo "draw.io embutido"), sem necessidade real neste momento.

### 11.2 Decisões de design esperadas

- Começar com modelo de fluxo **sequencial com branching simples**, deixando features mais avançadas como Fase 2.  
- Tratar detalhes de agente como **referência opaca** (ID/nome) neste épico; Programa 2 enriquece isso depois.  
- Fazer o Console de Fluxos ser mais um **visor e painel de controle** do que um "IDE visual" completo.

### 11.3 Anti-objetivos

- E28 **não** quer reinventar Airflow, Prefect ou similares; o foco é um modelo de fluxo específico para agentes GPT e componentes do Inspectah.  
- E28 **não** pretende resolver governança completa de versões de fluxo, experimentos e deploy gradual – isso é para Programas futuros.

---

## 12. Conexão com outros épicos e programas

- **E26 — Console Full & Coerência de UI/Admin:** o Console de Fluxos é mais um console admin e deve ser exemplar em seguir E26.
- **E27 — Fontes & Ingestão 2.0:** eventos de ingestão podem acionar fluxos de agentes; o modelo de fluxo precisa conversar bem com eventos vindos de fontes.
- **E29 — Debunker v1:** fluxo de debunking quase certamente será um dos primeiros fluxos modelados; E28 fornece trilho para E29 andar.
- **E30–E32 (Truth Console, Evidence Vault, Case Cockpit):** dependem de rastreabilidade de decisões, o que passa por Execuções de Fluxo de agentes modeladas aqui.
- **Programa 2 (Agent Brain & Committees):** usa o modelo de Fluxo v1 para encaixar agentes concretos mais sofisticados.

---

## 13. Notas finais

Este documento é a constituição do **Épico E28 — Fluxo de Agentes Configurável v1 (Orquestração Operacional)**.

Sprints que tocarem fluxos de agentes devem referenciar este épico:

- No Cap.1 do Sprint Playbook (contexto e states-of-truth de E28 que serão atacados).  
- No Cap.2 (gates e métricas associadas a Fluxos de Agentes).  
- No Cap.3 (modelagem e filemap de entidades de fluxo e APIs internas).  
- No Cap.4 (tasks específicas na Execution Matrix que implementam E28.1, E28.2 ou E28.3).

Mudanças profundas na forma de orquestrar agentes devem ser refletidas aqui antes de aparecerem em novas sprints ou no Programa 2.