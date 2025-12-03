# Sprint 29 — Capítulo 5
## Bloco 4 — Integração da S29 com o Épico E28 e o Programa 1

Este Bloco 4 amarra a Sprint 29 ao Épico E28 e ao Programa 1. A pergunta que ele responde é:

> "Depois que a S29 termina, exatamente como esse pedaço de fluxo de agentes configurável se encaixa no restante do plano, e o que ele destrava para as próximas sprints de E28?"

O objetivo é tornar explícitas as pontes, dependências e oportunidades, para que o planejamento das próximas E28.x não precise "redescobrir" o que a S29 já decidiu.

---

### 1. Relembrando o papel do Épico E28 no Programa 1

No contexto do Programa 1, o Épico E28 trata da **orquestração de agentes** dentro do Inspectah:

- como as entradas (notícias, dados, declarações) são interpretadas;  
- como são classificadas;  
- como passam por debunking;  
- como chegam a uma decisão final de estado de verdade, risco ou relevância.

Antes da S29, o E28 existia mais como visão conceitual: sabíamos que haveria sequências de agentes, redundâncias, comitês e fluxos específicos para cada tipo de domínio, mas essa orquestração ainda não era uma entidade clara no código nem no produto.

A Sprint 29 é a primeira sprint que concretiza essa visão em uma forma operacional, tornando o fluxo de agentes:

- uma entidade de domínio;  
- uma configuração editável e auditável;  
- uma peça respeitada pelo runtime.

Em outras palavras, a S29 é a sprint que "cola" o Épico E28 no resto do sistema, tirando-o da abstração pura.

---

### 2. O que o E28 passa a ter "resolvido" graças à S29

Com a S29 concluída, algumas partes do Épico E28 deixam de ser itens de backlog genérico e passam a ser consideradas **fundação entregue**:

1. **Modelo de fluxo por domínio**  
   - O conceito de `AgentFlowConfig` (configuração de fluxo por domínio) com steps ordenados, papéis e parâmetros passa a existir de forma concreta no domínio e no banco.

2. **Camada de validação de invariantes**  
   - Regras básicas sobre o que é um fluxo aceitável (não vazio, papéis exigidos para domínios sensíveis, posição do `DECISION_MAKER`, papéis conhecidos) estão implementadas e centralizadas;  
   - o Épico E28 não precisa mais discutir "como impedir configurações absurdas" do zero, apenas estender as invariantes.

3. **Surface de produto mínima para fluxos**  
   - UI de admin e API de admin para criar e atualizar fluxos;  
   - exigência de justificativa e trilha de auditoria mínima;  
   - operadores admin têm um lugar oficial para interagir com E28.

4. **Integração com runtime**  
   - O pipeline de ingestão (ao menos para domínios piloto) passou a usar o fluxo configurado para decidir a sequência de agentes;  
   - isso coloca E28 na linha de frente da operação real, não só em modo "laboratório".

Esses elementos formam a "camada base" de E28. As próximas sprints devem se apoiar nela, não duplicá-la.

---

### 3. Lacunas que permanecem em aberto dentro de E28

Mesmo com a S29 entregue, o Épico E28 ainda tem uma série de aspectos importantes em aberto. Explicitá-los é parte fundamental deste bloco.

Algumas lacunas principais que permanecem:

1. **Versionamento e ciclo de vida de fluxos**  
   - Ainda não há modelo explícito de versões (draft, active, deprecated);  
   - rollback de fluxos ainda é um processo manual (reaplicar config anterior) e não uma operação de alto nível.

2. **Governança de alterações (approvals)**  
   - Qualquer admin autorizado consegue alterar fluxos;  
   - não há workflow que exija múltiplos aprovadores ou segregação de funções em domínios sensíveis;  
   - faltam controles mais ricos de "quem pode mudar o quê".

3. **Branching e fluxos condicionais**  
   - Fluxos são essencialmente listas lineares de passos;  
   - condições do tipo "se a notícia for do tema X, use Debunker A, senão Debunker B" ainda não são representadas como estrutura do fluxo;  
   - decisões condicionais ainda vivem dentro de regras internas de agentes ou de pipelines.

4. **Métricas e tuning sistemáticos**  
   - Há logs de execução de fluxo, mas não há ainda um módulo consolidado que os transforme em métricas para tuning de E28;  
   - ainda não existe "painel de fluxos" que mostre quais configurações estão performando bem ou mal.

5. **Integração profunda com Truth-DB, Debunker e comitês**  
   - A S29 pluga o fluxo em nível de orquestração de agentes;  
   - a maneira como cada passo impacta estados de verdade, contestação, comitês e System of Blocks ainda será refinada nas sprints 23–25 e na evolução de E28.

O papel deste bloco não é resolver essas lacunas, mas marcá-las como **pontos de continuidade natural** para as próximas sprints do Épico.

---

### 4. Trilhas de E28.x habilitadas pela S29

A partir do estado entregue pela S29, algumas trilhas se destacam como próximas candidatas naturais dentro do Épico E28. Este bloco sugere uma decomposição possível em E28.2, E28.3, E28.4, sem fixar sprints específicas, mas organizando o raciocínio.

#### 4.1. Trilho 1 — Versionamento e approvals de fluxos (E28.2)

Objetivo principal:

- transformar fluxos em entidades versionadas e sujeitas a workflow de aprovação, especialmente para domínios sensíveis.

Construído sobre a S29:

- aproveita `AgentFlowConfig` como base para introduzir um campo de estado (draft/active/deprecated) e possivelmente uma entidade "versão" associada;  
- usa a UI de admin de S29 como ponto inicial para exibir histórico de versões e fluxos propostos;  
- estende os logs e metadados de auditoria já existentes.

Resultados esperados:

- possibilidade de preparar novas versões de fluxo sem afetar o atual até que sejam aprovadas;  
- rollback de fluxo como operação normal (troca de versão ativa);  
- maior segurança operacional em domínios de alto impacto.

#### 4.2. Trilho 2 — Branching e fluxos condicionais (E28.3)

Objetivo principal:

- permitir fluxos que respondem de forma diferente a contextos distintos, sem explodir a complexidade.

Construído sobre a S29:

- reusa o conceito de steps do fluxo, adicionando condições associadas a cada step ou a blocos de steps;  
- aproveita o runtime que já consulta a configuração e passa a considerar condições adicionais;  
- evolui a UI de admin de lista linear para uma representação mais expressiva (condições, grupos, etc.).

Resultados esperados:

- fluxos adaptativos por tipo de item ou de subdomínio;  
- controle mais fino de como diferentes agentes são aplicados, sem proliferar domínios artificiais apenas para representar variantes de fluxo.

#### 4.3. Trilho 3 — Métricas, tuning e painel de fluxos (E28.4)

Objetivo principal:

- transformar logs em inteligência para ajuste de fluxos, de forma contínua.

Construído sobre a S29:

- usa os logs de execução de fluxo (flow_id, papéis executados, tempo, sucesso/falha) como base;  
- introduz agregações e dashboards mostrando:  
  - quais fluxos estão mais carregados;  
  - tempos médios por agente;  
  - incidência de erros ou quedas de confiança;  
- cria mecanismos, possivelmente semi-automatizados, para sugerir ajustes de fluxo (por exemplo, remover agentes redundantes ou adicionar redundância em pontos frágeis).

Resultados esperados:

- melhoria contínua dos fluxos baseada em dados;  
- capacidade de justificar, com evidências, mudanças de configuração de E28.

---

### 5. Convergência com as sprints de Verdade, Debunker e Comitês (S23–S25)

O Épico E28 não vive isolado: ele é um pedaço da história maior que inclui as sprints 23, 24 e 25 focadas em Verdade, Debunker, Comitês e Governança.

O estado pós-S29 cria convergências importantes:

1. **Papéis do fluxo como pontos de integração**  
   - Papéis como DEBUNKER, CLASSIFIER, DECISION_MAKER, COMMITTEE_MEMBER passam a ser explicitamente configurados no fluxo;  
   - isso permite que as sprints de Verdade/Comitês tratem esses papéis como "portas de entrada" para suas lógicas (Truth-DB, Evidence Vault, comitês humanos ou mistos).

2. **Configuração de fluxo como política operacional**  
   - As decisões sobre quais agentes entram em qual sequência passam a ser políticas configuradas, não apenas detalhes de implementação;  
   - isso facilita alinhar essas políticas com as políticas de promoção de verdade, de contestação, de reputação de fonte.

3. **Evidências de execução de fluxo como insumo de confiança**  
   - Logs de runtime que mostram que um item passou por um determinado Debunker, por um certo Comitê, etc., viram evidências dentro do System of Blocks;  
   - a S29 já prepara parte dessa trilha de evidência ao registrar execução por flow_id e papéis.

Estas convergências sugerem que trabalho futuro em E28 deve ser coordenado com as decisões e requisitos que surgirem de S23–S25.

---

### 6. Diretrizes para planejamento futuro dentro de E28

A partir da integração mapeada acima, este bloco recomenda algumas diretrizes de planejamento:

1. **Não reabrir fundamentos de fluxo sem motivo forte**  
   - `AgentFlowConfig`, o validador básico e a UI de admin introduzidos pela S29 devem ser tratados como fundação;  
   - mudanças futuras devem estender, não invalidar, esse núcleo, salvo descoberta de falha estrutural grave.

2. **Sempre amarrar novas features de E28 a evidências**  
   - Qualquer nova funcionalidade de fluxo (versionamento, branching, etc.) deve, desde o início, ter um plano claro de evidências e logs (quem mudou, quando, que fluxo foi usado, com que resultado);  
   - isso mantém a coerência com a visão de Inspectah como sistema auditável de verdade.

3. **Planejar E28.x em torno de perguntas de produto, não só técnicas**  
   - E28.2/E28.3/E28.4 devem ser formuladas a partir de perguntas como:  
     - "Quem precisa aprovar uma mudança de fluxo?"  
     - "Como saber se um fluxo está funcionando melhor que outro?"  
     - "Que tipos de casos exigem fluxos condicionais?"  
   - e não apenas "o que é elegante tecnicamente".

4. **Manter domínios piloto como campo de experimentação disciplinado**  
   - Novas capacidades de E28 devem ser introduzidas primeiro nos domínios piloto já usados na S29;  
   - só depois de validadas é que se expande para outros domínios.

---

### 7. Resumo do Bloco 4

Este Bloco 4 posiciona a S29 como:

- a sprint que "abre" o Épico E28 no mundo real, dando corpo ao conceito de fluxo de agentes configurável;
- a responsável por entregar a fundação técnica e de produto sobre a qual E28.2, E28.3, E28.4 e as sprints de Verdade/Debunker/Comitês vão se apoiar;
- o ponto a partir do qual fluxos deixam de ser um detalhe interno do código e se tornam uma camada configurável, auditável e alinhada à visão do Inspectah como sistema de verdade.

A partir daqui, o Bloco 5 do Capítulo 5 se encarrega de transformar essa visão integrada em recomendações formais de ORR (GO/NO-GO, uso piloto vs amplo, prioridades de E28.x), fechando o Capítulo 5 e a história da S29 sob a ótica de produto e de programa.

