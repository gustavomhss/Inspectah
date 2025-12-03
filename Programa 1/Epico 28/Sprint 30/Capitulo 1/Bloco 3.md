# Inspectah — Sprint 30 — Capítulo 1 — Bloco 3
## Objetivos Concretos, Métricas de Sucesso e Critério de GO/NO-GO

### 1. Objetivo Central (reafirmação em formato de contrato)

Ao final da Sprint 30, precisa ser verdade — de maneira demonstrável — o seguinte enunciado:

> “Existe um fluxo‑pivô de notícias, criado a partir de um template oficial versionado, cujo ciclo de vida (criar, testar, promover, pausar, retomar, trocar agentes críticos) é integralmente gerido pelo Console de Fluxos, cujo comportamento real de roteamento respeita rigidamente os estados de fluxo e cuja jornada por notícia é rastreável e observável em nível suficiente para operar 24/7 sem recorrer a gambiarras de código ou scripts paralelos.”

Esse enunciado é o contrato da S30. Todos os objetivos específicos, métricas e decisões de escopo abaixo existem para tornar esse contrato verdade.

---

### 2. Objetivos Específicos da Sprint 30

Os objetivos abaixo são formulados como estados desejados (não como tarefas). A sprint é bem‑sucedida apenas se todos eles estiverem cumpridos com qualidade ≥ 9.9/10 segundo o squad responsável.

#### 2.1. Template oficial de Fluxo de Notícias v1

Ao final da sprint:

1. Existe um artefato canônico chamado, por exemplo, `Fluxo_Noticias_Geral_v1`, com:
   - identificação e versão explícitas;
   - topologia mínima acordada (cadeia de etapas e papéis de agentes);
   - parâmetros configuráveis claramente separados de estrutura fixa.
2. Esse template está armazenado em local de referência (código + docs) e é reconhecido como “fonte de verdade” pelo squad de Fluxos & Orquestração.
3. O Console de Fluxos é capaz de instanciar um novo fluxo de notícias a partir desse template sem exigir edição de código.

#### 2.2. Semântica de estados de fluxo aplicada ao fluxo de notícias

Ao final da sprint:

1. Para o domínio de notícias, existe uma regra única, clara e auditável que define qual fluxo em estado `ativo` recebe 100% do tráfego daquele tipo de entrada.
2. Fluxos em estado `em_teste` recebem apenas a fração de tráfego definida em configuração (ex.: 5–10%), com comportamento verificável em testes.
3. Um fluxo em estado `pausado` não recebe novos eventos; qualquer evento elegível é desviado para fluxo alternativo ou queda controlada.
4. Estado `draft` é claramente entendido como “não recebe tráfego”, e não há caminhos acidentais que o utilizem em produção.

#### 2.3. Ciclo de vida do fluxo de notícias operável via Console

Ao final da sprint:

1. Um operador treinado consegue, exclusivamente pelo Console de Fluxos:
   - criar um novo fluxo de notícias a partir do template oficial;
   - configurá‑lo (atribuir agentes concretos a cada papel);
   - marcá‑lo como `em_teste` e direcionar parte do tráfego para ele;
   - promovê‑lo a `ativo` para um determinado tipo de entrada;
   - pausar e retomar o fluxo, com efeitos imediatos e visíveis.
2. A troca de pelo menos um agente crítico de etapa (por exemplo, o classificador de tipo de notícia) é feita via Console, com persistência e histórico mínimo, sem alteração de código ou arquivos internos.
3. Toda alteração de ciclo de vida e de configuração relevante deixa uma trilha de auditoria consultável (quem fez, o que fez, quando).

#### 2.4. Rastreabilidade ponta a ponta para o fluxo de notícias‑pivô

Ao final da sprint:

1. Para qualquer notícia processada pelo fluxo‑pivô, é possível responder, via Console e/ou APIs oficiais:
   - qual fluxo a processou;
   - quais etapas foram executadas e em que ordem;
   - qual agente executou cada etapa;
   - qual foi o output e o status de cada etapa;
   - qual o status final da execução do fluxo para aquela notícia.
2. Essa rastreabilidade é utilizável na prática: o squad consegue, em minutos, reconstruir a jornada de uma notícia sem recorrer a logs brutos dispersos.

#### 2.5. Observabilidade mínima, mas sólida, do fluxo de notícias

Ao final da sprint:

1. Existem métricas consolidadas por fluxo para o fluxo‑pivô de notícias, incluindo, no mínimo:
   - número total de execuções;
   - taxa de sucesso x falha;
   - latência p95 (ou equivalente) do fluxo;
   - se aplicável, algum indicador de backlog/gargalo por etapa.
2. Essas métricas estão expostas em pelo menos um painel ou endpoint de inspeção usado pelo squad de operação.
3. Com base nessas métricas, o squad consegue responder perguntas como:
   - “o fluxo de notícias está saudável neste momento?”;
   - “onde está o gargalo principal?”;
   - “houve degradação relevante nas últimas horas/dias?”.

#### 2.6. Reconhecimento explícito do Console como cockpit pelo squad

Ao final da sprint:

1. Os membros do Squad Fluxos & Orquestração executaram cenários reais (ou simulados com dados realistas) operando o fluxo de notícias exclusivamente via Console.
2. Cada membro do squad atribui nota ≥ 9.9/10 à afirmação:
   > “Para o caso de notícias, o Console de Fluxos é hoje o cockpit operacional; eu consigo operar o fluxo sem tocar em código nem pedir ajuda para um desenvolvedor.”

---

### 3. Métricas de Sucesso da S30

As métricas abaixo complementam os objetivos e servem de checklist quantitativo/qualitativo para o GO/NO-GO.

#### 3.1. Métricas funcionais

1. Existem pelo menos **N≥3** ciclos completos registrados de:
   - criação de fluxo de notícias a partir de template;
   - execução em modo `em_teste` com tráfego parcial;
   - promoção do fluxo a `ativo`.
2. Foram executadas, e registradas, pelo menos **N≥3** operações de pausa/retomada de fluxo de notícias via Console, com verificação de impacto em tráfego.
3. Houve pelo menos **N≥2** trocas de agente em etapa crítica feitas via Console, com efeito observado na operação do fluxo.

#### 3.2. Métricas de observabilidade

1. As métricas de fluxo de notícias aparecem em painel/endpoint dedicado e são atualizadas em tempo compatível com operação quase real (ex.: granularidade de minutos).
2. Em uma sessão de revisão, o squad é capaz de usar exclusivamente esse painel/endpoint para diagnosticar:
   - um cenário de fluxo saudável;
   - um cenário de aumento de erros;
   - um cenário de aumento de latência ou backlog.

#### 3.3. Métricas de percepção do squad

1. Nota média do squad para a afirmação “o Console é o cockpit do fluxo de notícias” ≥ 9.9/10.
2. Nenhum membro do squad aponta, como condição indispensável para operar, alguma ferramenta fora do conjunto Console + painéis oficiais + APIs previstas. Se isso ocorrer, a lacuna deve ser registrada como dívida explícita e tratada no máximo nas sprints seguintes do E28.

---

### 4. Critério de GO/NO-GO da Sprint 30

A Sprint 30 é **GO** apenas se todas as condições abaixo forem verdadeiras ao mesmo tempo:

1. O contrato central do fluxo‑pivô de notícias (enunciado na Seção 1) está cumprido e demonstrado com dados/execuções reais ou fortemente realistas.
2. Todos os objetivos específicos das Seções 2.1 a 2.6 foram atendidos sem atalhos frágeis ou soluções provisórias disfarçadas de definitivo.
3. As métricas da Seção 3 foram verificadas em sessão formal de revisão com o squad e, quando aplicável, com o conselho técnico.
4. Não há “atalho escondido” que dependa de alterar código em produção para operar o fluxo de notícias em situações normais.

Se qualquer um desses pontos falhar, a S30 deve ser declarada **NO-GO** do ponto de vista de E28, e a continuação do épico (S31+) deve carregar explicitamente as pendências como parte do plano, sem rebaixar a barra de excelência.

Este Bloco 3 completa o triângulo do Capítulo 1: problema central (Bloco 1), decomposição e hipóteses (Bloco 2) e agora objetivos e métricas em formato de contrato. Os blocos seguintes vão detalhar escopo negativo, riscos e alinhamento com o restante do Programa 1 e dos épicos correlatos.

