# Inspectah — Sprint 30 — Capítulo 5 — Bloco 3
## Riscos Estruturais, Trade-offs Assumidos e Plano de Monitoração Contínua

Este bloco registra, de forma explícita, os **riscos estruturais** e os **trade-offs conscientes** assumidos pela Sprint 30, além de um plano de monitoração contínua pós‑GO.

Ideia central: se em algum momento o comportamento do sistema começar a doer, este bloco deve explicar **por que aquilo foi considerado aceitável na S30**, o que precisa ser observado e quais são os sinais de que chegou a hora de intervir.

---

## 5.3.1 Complexidade do Modelo de Fluxos v1.5

### O risco

O modelo de fluxos v1.5 não é minimalista: temos `Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog`, engine, roteamento, console, telemetria. Esse conjunto forma uma camada de orquestração relativamente densa.

Riscos decorrentes:
- **Curva de aprendizado alta** para pessoas novas no projeto;
- **Maior superfície de bugs** (mais estados, mais integrações, mais caminhos);
- Tentação futura de criar “atalhos” fora de `app/flows/` para resolver casos específicos, gerando **sistemas paralelos**.

### Por que aceitamos esse risco na S30

A S30 tem como missão transformar fluxos em **entidade de primeira classe** e cockpit em **ferramenta real de operação**. Um modelo simplista demais obrigaria a refazer a base inteira em S31–S35, o que seria mais caro e mais arriscado a longo prazo.

Em outras palavras: preferimos pagar o custo de complexidade **agora**, com um modelo coerente e centralizado, do que fragmentar o conceito de fluxo nas próximas sprints.

### Como monitorar

Sinais de que a complexidade saiu da faixa saudável:
- aumento recorrente de bugs relacionados a fluxos (especialmente em estados/execuções);
- dificuldade de explicar o modelo de fluxos para novos membros em tempo razoável;
- aparecimento de “fluxos alternativos” fora de `app/flows/`.

Ações recomendadas se esses sinais aparecerem:
- registrar incidentes e bugs em um **log de dores de fluxo** centralizado;
- se o padrão persistir, planejar uma sprint de refino de modelo de fluxos dentro do próprio E28;
- reforçar a documentação em `docs/` com diagramas mais didáticos.

---

## 5.3.2 Acoplamento com Ingestão e Dispatcher

### O risco

A S30 ancora o fluxo‑pivô de notícias na combinação:
- `IngestionEvent` com `tipo_entrada = noticia_texto`;
- dispatcher chamando `route_event_to_flow(event)`;
- roteamento baseado em estado de fluxo e política de teste.

Riscos principais:
- Mudanças na forma como ingestão emite eventos podem quebrar o roteamento de fluxos (e vice‑versa);
- Divergência entre contrato de ingestão e contrato de fluxos pode produzir situações onde eventos ficam “no limbo”.

### Por que aceitamos esse risco na S30

Para que o fluxo‑pivô de notícias seja real, é necessário **acoplar ingestão e fluxos** em algum ponto. A S30 escolhe uma fronteira relativamente simples e explícita (evento de ingestão → roteamento para fluxo) como lugar desse acoplamento.

Essa decisão permite:
- manter ingestão e fluxos como módulos distintos, com contrato claro;
- testar ponta a ponta (ingestão → fluxo) sem espalhar conhecimento de fluxos dentro do módulo de ingestão.

### Como monitorar

Sinais de que o acoplamento ficou perigoso:
- erros recorrentes do tipo “tipo_entrada inesperado em route_event_to_flow”;
- mudanças frequentes na estrutura de `IngestionEvent` quebrando testes de fluxo;
- necessidade de condicionalidades complexas em `routing_policy` para lidar com casos de ingestão.

Ações recomendadas:
- documentar sempre que `IngestionEvent` for alterado, com impacto explícito em fluxos;
- manter contratos de ingestão e fluxos descritos em Cap. 3 de cada sprint relevante;
- se a fronteira começar a ficar “suja”, considerar uma sprint específica para redesign da interface ingestão→fluxos.

---

## 5.3.3 Risco Operacional de Reprocessamento

### O risco

Reprocessamento é uma ferramenta poderosa e perigosa. Um comando mal parametrizado pode:
- reexecutar muitos itens de uma vez;
- gerar carga artificial enorme em agentes e banco;
- distorcer métricas e logs em janelas de tempo curtas.

### Como a S30 lida com isso

A S30 assume um posicionamento conservador:
- `reprocess_items` tem **limites por padrão** (número máximo de itens, janela máxima de tempo, filtros obrigatórios);
- operações de reprocessamento são **logadas em FlowOperationLog** com parâmetros utilizados;
- APIs de reprocessamento são expostas via Console com UX que desencoraja ações descontroladas (mensagens claras, campos obrigatórios, possivelmente confirmações extras).

### Trade-off

- **Pró:** reduz o risco de “explosão acidental” de reprocessamento;
- **Contra:** pode ser percebido como “amarrado” por operadores avançados que desejam reprocessar grandes volumes em situações de emergência.

### Como monitorar

Sinais a observar:
- tentativas frequentes de reprocessamento negadas pelos limites padrão (pode indicar que os limites precisam ser calibrados);
- aumento repentino e não planejado em métricas de execuções de fluxo vindas de reprocessamento;
- relatos de operação de que o reprocessamento é “inútil” porque os limites são rígidos demais.

Resposta sugerida:
- ajustar limites em parâmetros configuráveis (não hard‑code) quando houver contexto e evidência;
- manter o padrão conservador como default, mas permitir perfis ou modos de operação mais permissivos com guard rails adicionais (ex.: confirmação dupla, aprovação).

---

## 5.3.4 Risco de “Cockpit em Slide”

### O risco

Existe o risco clássico de o Console de Fluxos virar um “cockpit de slide”: bonito, mas não usado na operação real, com o time recorrendo a scripts, SQL direto e chamadas internas para resolver problemas.

Consequências desse risco:
- divergência entre o que o cockpit mostra e o que realmente é usado no dia a dia;
- perda do valor de ter um ponto único de operação;
- aumento de dependência de conhecimento tácito (só quem conhece os scripts sabe operar).

### Como a S30 tenta mitigar

A Sprint 30 decidiu que o Console de Fluxos é o **cockpit oficial** para fluxos de notícias, e implementou:
- operações essenciais via UI (criar, ativar, pausar, reprocessar, inspecionar execuções);
- um cenário E2E onde tudo é feito pelo console, não por caminhos ocultos;
- evidências de que o console funciona como ferramenta real, não só como prova de conceito.

### Como monitorar

Sinais de que o cockpit virou slide:
- operações críticas sendo feitas via SQL/script e não registradas como operações de fluxo;
- evidências de ORR ou post‑mortems mostrando que, na prática, ninguém usou o console em incidentes reais;
- backlog de UX de console não tratado enquanto scripts proliferam.

Ações recomendadas:
- adotar política explícita: operações em produção **devem** usar o console, com scripts como exceção rara e auditada;
- incluir perguntas sobre uso do console em post‑mortems e revisões de sprint;
- priorizar melhorias de UX no console quando o time aponta fricções reais.

---

## 5.3.5 Risco de Divergência entre Fluxo‑Pivô e Demais Fluxos Futuros

### O risco

S30 foca no fluxo‑pivô de notícias. Há o risco de que, no futuro, outros fluxos sejam implementados com variações ad‑hoc, gerando uma família de fluxos pouco coerente:
- fluxos com estados diferentes;
- fluxos com semânticas de erro/reprocessamento divergentes;
- fluxos com telemetria incompleta.

### Por que isso é relevante

O Épico E28 pretende criar um **sistema de fluxos configuráveis e generalizáveis**. Se cada sprint “grudar” o seu fluxo ao modelo, sem linha mestra, a promessa de generalidade se perde.

### Como a S30 prepara o terreno

- Define um modelo de fluxo **suficientemente geral** para servir de base a outros tipos de entrada;
- Cria um Console de Fluxos orientado a múltiplos fluxos, mesmo que inicialmente só o de notícias exista;
- Estabelece contratos de estados, telemetria e IDs de execução como canônicos.

### Como monitorar

Sinais de alerta:
- cada novo fluxo introduz estados extra sem discutir impacto global;
- fluxos diferentes exigem painéis de métricas radicalmente distintos, sem sobreposição;
- aumenta o número de condicionais “se fluxo X, então Y” espalhados pelo código.

Ações recomendadas:
- exigir, em specs futuras, uma seção explícita de “compatibilidade com fluxo‑pivô de notícias”;
- chamar o Squad Fluxos & Cockpit para revisar qualquer nova topologia de fluxo como guardião de coerência;
- se a divergência se acumular, propor uma sprint dedicada à “unificação de gramática de fluxos”.

---

## 5.3.6 Plano de Monitoração Contínua Pós‑GO

Para que os riscos mapeados não virem surpresa, a S30 recomenda um plano mínimo de monitoração nos ciclos imediatamente após o GO.

### Janela recomendada

- Primeiras **2–4 semanas** após GO da S30.

### Indicadores a acompanhar

1. **Saúde do fluxo de notícias**
   - taxa de erro por fluxo (`inspectah_flow_executions_failure_total` / `inspectah_flow_executions_total`);
   - latência p95 de execução de fluxo;
   - estabilidade do roteamento (ausência de eventos sem fluxo destino).

2. **Uso de reprocessamento**
   - volume diário de itens reprocessados por fluxo;
   - frequência de operações recusadas por limites de segurança;
   - impacto de reprocessamentos na carga total do sistema.

3. **Uso real do Console de Fluxos**
   - número de operações de fluxo originadas via console vs. caminhos alternativos (quando rastreável);
   - feedback qualitativo de operadores sobre facilidade/dor no uso do console;
   - incidentes em que o console ajudou (ou falhou em ajudar) a resolver problemas.

4. **Fluxos de bugs e incidentes relacionados a fluxos**
   - quantidade de bugs/incident reports envolvendo fluxos, roteamento e console;
   - classificações por causa raiz (modelo, lógica de estado, UX, performance, etc.).

### Ritual sugerido

- Realizar, no mínimo, um **check quinzenal** durante a janela inicial pós‑GO, com:
  - revisão rápida de métricas e logs de fluxo de notícias;
  - revisão do log de reprocessamentos;
  - discussão dos incidentes e feedbacks de operação;
  - registro de aprendizados em um documento de “post‑mortem positivo da S30”.

Esse material alimenta futuras sprints de E28, especialmente as focadas em generalização, resiliência e UX de cockpit.

---

Com isso, o Bloco 3 do Capítulo 5 torna explícito que a S30 não é cega aos próprios riscos: ela os assume de forma consciente, define como monitorá‑los e oferece trilhas claras de reação. O próximo bloco fecha o capítulo encaixando a S30 na continuidade S31–S35 do Épico E28 e no Programa 1 como um todo.

