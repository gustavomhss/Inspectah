# Inspectah — Sprint 30 — Capítulo 5 — Bloco 2
## Decisões Permanentes da Sprint 30 e Contratos para o Épico E28

Este bloco registra as **decisões da Sprint 30 que viram contrato** para o Épico E28 e, por extensão, para o Programa 1 do Inspectah. Não são só escolhas locais de implementação; são regras de jogo que sprints futuras devem respeitar ou revogar explicitamente em nova especificação.

Tratamos estas decisões como **estáveis até segunda ordem**: ninguém “refatora” isso em uma terça‑feira aleatória.

---

## 5.2.1 Fluxos como Entidade de Primeira Classe

**Decisão:** A partir da S30, **Fluxos** passam a ser entidade de primeira classe no Inspectah.

### Contrato

1. O módulo `app/flows/` é o **único ponto canônico** para:
   - modelar fluxos (`Flow`, `FlowStep`);
   - modelar execuções (`FlowExecution`, `FlowStepExecution`);
   - modelar templates (`FlowTemplate`);
   - registrar operações administrativas (`FlowOperationLog`);
   - definir engine de execução (`FlowExecutionEngine`) e roteamento (`routing_policy`).

2. Nenhum outro módulo deve criar estruturas paralelas para “pipelines”, “workflows” ou “rotas de agentes” fora de `app/flows/` sem:
   - discussão explícita no nível de **épico**;
   - documento de decisão que cite claramente por que `app/flows/` não atende.

3. Qualquer funcionalidade do sistema que deseje “fazer passar uma coisa por uma sequência de agentes/etapas” deve, por padrão, **usar fluxos**.

### Implicação para sprints futuras

- S31–S35 e além devem tratar `app/flows/` como fundação. Evoluções podem acontecer, mas não é aceitável duplicar o conceito de fluxo em outro lugar.

---

## 5.2.2 Estados Canônicos de Fluxo e Regras de Transição

**Decisão:** Os estados de fluxo definidos na S30 tornam‑se **vocabulário canônico** para E28 e para qualquer programa que opere pipelines/rotas de agentes.

### Estados oficiais

- `draft` — fluxo em rascunho, não recebe tráfego real;
- `em_teste` — fluxo em fase de teste, recebendo tráfego parcial e controlado;
- `ativo` — fluxo oficial em produção para um dado tipo de entrada;
- `pausado` — fluxo temporariamente suspenso, não recebe novos itens;
- `deprecado` — fluxo aposentado, histórico apenas.

### Regras de transição (regra‑mãe S30)

A S30 estabelece uma **máquina de estados mínima**:

- Permitidos, em geral:
  - `draft → em_teste`;
  - `em_teste → ativo`;
  - `ativo → pausado`;
  - `pausado → ativo`;
  - `ativo → deprecado`.

- Proibidos (exemplos):
  - `ativo → draft` (não faz sentido “desnascer” fluxo ativo);
  - `deprecado → qualquer coisa` (fluxo deprecado não volta à vida sem migração planejada);
  - transições que coloquem o fluxo em estado incoerente para o tipo de tráfego.

A lógica detalhada mora em `app/flows/service.py` e é tratada como **contrato de domínio**, não mero detalhe de implementação.

### Implicação para sprints futuras

- S31+ podem adicionar estados (ex.: `em_rollback`, `experimental`) apenas via alteração formal da máquina de estados documentada;
- qualquer mudança em regras de transição deve ser registrada em doc de épico e refletida em testes de domínio;
- o resto do sistema pode confiar que “ativo” significa “está realmente atendendo tráfego oficial”.

---

## 5.2.3 Console de Fluxos como Cockpit Oficial de Operação

**Decisão:** O **Console de Fluxos** da S30 se torna o cockpit oficial para operação de fluxos no Programa 1.

### Contrato

1. As operações essenciais de fluxo **devem** ser possíveis via Console:
   - criar fluxo a partir de template;
   - mudar estado (`draft`, `em_teste`, `ativo`, `pausado`, `deprecado`);
   - trocar agente de uma etapa (quando permitido);
   - iniciar reprocessamentos limitados;
   - inspecionar execuções e jornadas.

2. Scripts manuais, chamadas diretas a APIs internas ou manipulação de banco para realizar essas operações são considerados **caminhos de exceção**, não o fluxo normal de trabalho.

3. Qualquer nova capacidade crítica em fluxos (por ex.: marcar fluxo como “em modo de auditoria reforçada”) deve, idealmente, aparecer **primeiro ou junto** no Console.

### Implicação para sprints futuras

- S31–S35 devem tratar o Console de Fluxos como ponto focal para UX de operação;
- é aceitável criar ferramentas auxiliares (CLIs, scripts) para uso especializado, mas elas não substituem o cockpit;
- se houver operação crítica que não é feita via Console, isso precisa ser explicitamente registrado como dívida ou exceção.

---

## 5.2.4 Telemetria Mínima Obrigatória de Fluxos

**Decisão:** A telemetria de fluxos desenhada na S30 passa a ser o **piso mínimo obrigatório** para qualquer fluxo operável.

### Métricas canônicas

A S30 estabelece como padrão (nomes ilustrativos, stack‑agnostic):

- `inspectah_flow_executions_total{flow_id, tipo_entrada, status}`;
- `inspectah_flow_executions_success_total{flow_id, tipo_entrada}`;
- `inspectah_flow_executions_failure_total{flow_id, tipo_entrada, error_class}`;
- `inspectah_flow_latency_seconds{flow_id, tipo_entrada}` (histograma/base para p95);
- opcional, mas recomendado: métricas de backlog.

### Logs estruturados canônicos

Para cada execução de fluxo e etapa, é obrigatório registrar logs com, no mínimo:
- `flow_id`;
- `exec_fluxo_id` (ID da execução do fluxo);
- `exec_etapa_id` (ID da execução da etapa);
- `item_id` (ou identificador do item ingerido);
- `tipo_entrada`;
- `status` (sucesso/falha/timeout/…);
- timestamps relevantes.

### Contrato

1. Nenhuma futura sprint pode **remover** essas métricas/campos sem fornecer substitutos equivalentes e migrar painéis/tests.
2. Panéis de observabilidade de E28 podem assumir que esses nomes/labels existem.
3. Problemas em fluxos devem ser diagnosticáveis **apenas** com métricas e logs padrões + bundle de evidências.

---

## 5.2.5 IDs de Execução de Fluxo como Referência para Verdade, Casos e Evidências

**Decisão:** `FlowExecution.id` e `FlowStepExecution.id` passam a ser **identificadores oficiais** para amarrar fluxos a futuras camadas de Verdade, Casos e Evidências.

### Contrato

1. Qualquer caso futuro no Inspectah que dependa de “o que aconteceu com esta notícia nesta pipeline de agentes” deve referenciar:
   - `flow_id`;
   - `exec_fluxo_id`;
   - opcionalmente, um ou mais `exec_etapa_id`.

2. Sprints de Verdade & Interpretação (Debunker, Truth‑DB, Casos) podem tratar esses IDs como **chaves estáveis**.

3. Alterações futuras na forma de ID (ex.: troca de tipo, codificação) devem preservar a capacidade de resolver execuções antigas ou oferecer migração de referência.

### Implicação para sprints futuras

- Ao desenhar esquemas de Casos, Evidências, Truth‑DB, etc., é preferível linkar execuções de fluxo por esses IDs;
- reprocessamentos de fluxo devem manter uma história clara, permitindo distinguir execuções originais e reprocessadas sem perda de audit trail.

---

## 5.2.6 Modelo de Sprint com Gates, Scorecards e Bundle

**Decisão:** O modelo de **gates + scorecards + bundle de evidências** aplicado na S30 é adotado como padrão para as demais sprints do Épico E28.

### Contrato

1. Toda sprint de E28 deve:
   - definir gates G0–G* alinhados ao seu escopo;
   - implementar scripts `bin/sXX_g*.sh` gerando scorecards JSON;
   - produzir `SXX_metrics_summary.json` agregando o resultado;
   - gerar `inspectah_sXX_evidence_bundle.zip` com scorecards + evidências + resumo de ORR.

2. A decisão de GO/NO‑GO passa a depender:
   - do estado dos scorecards;
   - do bundle de evidências;
   - de um resumo de ORR documentado.

3. O padrão de nomenclatura estabelecido pela S30 (`S30_G*`, `S30_metrics_summary`, `inspectah_s30_evidence_bundle.zip`) deve ser seguido em S31–S35 (ajustando o número da sprint).

---

## 5.2.7 Como revogar ou alterar essas decisões

Para que o sistema continue evoluindo sem virar fosso de cimento, o squad e o conselho técnico concordam em uma regra simples:

> Nenhuma decisão permanente da S30 é imutável — mas nenhuma pode ser alterada “no escuro”.

Qualquer mudança de contrato estabelecido neste bloco exige:
- um documento de decisão em nível de **épico ou programa** (não de sprint isolada);
- atualização explícita de Capítulos 1/3/5 da sprint que faz a alteração;
- atualização de testes, métricas, painéis e docs afetados.

---

Com isso, o Bloco 2 do Capítulo 5 fixa as principais decisões da Sprint 30 como contratos claros, sobre os quais as próximas sprints podem pisar com segurança — ou que precisarão ser revogados de forma explícita, nunca por acidente ou por “refatoração inocente”.

