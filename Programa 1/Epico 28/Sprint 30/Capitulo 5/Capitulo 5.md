# Inspectah — Sprint 30 — Capítulo 5
## Governança, Squad, Decisões Permanentes e Continuidade no Épico E28

Este Capítulo 5 amarra a Sprint 30 em três dimensões que vão além do código:

1. **Quem é responsável pelo quê** (squad, papéis e áreas de dono);
2. **Quais decisões da S30 viram lei** para as próximas sprints do Épico E28;
3. **Como a S30 se encaixa na linha de continuidade** (S31–S35) e no Programa 1 do Inspectah.

Capítulos 1–4 explicam o que a S30 faz, como provar que funciona e onde tudo mora no repo. O Capítulo 5 explica **como isso se torna parte da anatomia do produto** e das próximas sprints, sem depender de memória de ninguém.

---

## 5.1 Squad da Sprint 30 e Áreas de Responsabilidade

A Sprint 30 roda dentro do contexto do **Épico E28** (Fluxo de Agentes Configurável) e do **Programa 1** (núcleo de ingestão e operação do Inspectah). Ela herda a estrutura de squads definida para o Inspectah, mas com foco específico em fluxos.

### 5.1.1 Squad principal da S30 (Fluxos & Console)

**Nome sugerido:** Squad Fluxos & Cockpit

**Mandato:**
- Tornar o fluxo‑pivô de notícias **configurável** e **operável** via Console;
- Garantir que esse fluxo é observável, auditável e pronto para 24/7.

**Áreas de dono dentro da sprint:**
- **Domínio e dados de Fluxos**  
  Donos diretos de:
  - `app/flows/models.py`;
  - `app/flows/service.py`;
  - `app/flows/routing_policy.py`;
  - `app/flows/execution_engine.py`;
  - `app/flows/instrumentation.py`;
  - migrations de S30 (`0030_s30_flow_model_v15.py` etc.).

- **Console de Fluxos (APIs + UI)**  
  Donos diretos de:
  - `app/api/flow_console_routes.py`;
  - `frontend/inspectah-ui/src/features/flows/*`;
  - testes de backend e frontend do console.

- **Gates, métricas e bundle S30**  
  Donos diretos de:
  - `bin/s30_g*.sh`;
  - `bin/s30_metrics_summary.sh`;
  - `bin/s30_bundle.sh`;
  - scorecards `S30_G*` e `S30_metrics_summary.json`;
  - bundle `inspectah_s30_evidence_bundle.zip`.

O Squad Fluxos & Cockpit responde por **todo o ciclo de vida S30**, da spec ao ORR, e é a referência primária quando o assunto é fluxo‑pivô de notícias.

### 5.1.2 Interfaces com outros squads

Embora a S30 tenha um squad principal, ela precisa conversar bem com outras frentes do Inspectah.

- **Squad Ingestão 2.0**  
  Interface: `app/orchestration/dispatcher.py` e modelo de `IngestionEvent`.
  - Acordos:
    - ingestão produz eventos com `tipo_entrada` consistente (ex.: `noticia_texto`);
    - dispatcher chama `route_event_to_flow` usando contrato estável;
    - qualquer mudança em `tipo_entrada` ou forma de roteamento precisa ser combinada entre os squads.

- **Squad Observabilidade & Infra**  
  Interface: sistema de métricas, logs estruturados e dashboards.
  - Acordos:
    - nome dos métricos `inspectah_flow_*` são considerados API interna estável;
    - campos mínimos de logs (`flow_id`, `exec_fluxo_id`, etc.) são obrigatórios;
    - painéis específicos para fluxos de notícias são mantidos e evoluídos em conjunto.

- **Squad Verdade & Interpretação** (Debunker, Truth‑DB, Casos)  
  Interface: IDs de execução de fluxo, links para casos futuros e evidências.
  - Acordos:
    - `FlowExecution.id` e `FlowStepExecution.id` passam a ser **identificadores de referência** para futuras ligações com casos e evidências;
    - nenhum redesign futuro desses IDs pode quebrar essa relação sem migração planejada.

---

## 5.2 Decisões Permanentes da Sprint 30

Nem tudo que uma sprint faz deve virar lei, mas algumas decisões da S30 **precisam** ser tratadas como permanentes (até que outra spec, em outro épico, as derrube explicitamente).

### 5.2.1 Fluxos como entidade de primeira classe

Decisão: **Fluxos passam a ser entidade de primeira classe no Inspectah**.

Concretamente, isso significa:
- Existe um módulo dedicado (`app/flows/`) com models, serviços e engine;
- `Flow`, `FlowStep`, `FlowExecution`, `FlowStepExecution`, `FlowTemplate`, `FlowOperationLog` são modelos oficiais;
- Nenhum outro módulo deve reinventar estruturas paralelas para “pipelines”, “workflows” ou “rotas de agentes” sem passar por esse módulo.

### 5.2.2 Estados canônicos de fluxo

Decisão: Os estados de fluxo da S30 viram **vocabulário canônico** para E28 e futuros programas que lidarem com operação de pipelines:

- `draft` — fluxo ainda em construção, não recebe tráfego real;
- `em_teste` — fluxo recebendo tráfego parcial/experimental;
- `ativo` — fluxo em produção, recebendo tráfego oficial;
- `pausado` — fluxo temporariamente suspenso;
- `deprecado` — fluxo aposentado, mantido apenas para histórico.

Regras de transição definidas na S30 não podem ser relaxadas em sprints futuras sem revisão formal em doc de épico/programa.

### 5.2.3 Console de Fluxos como cockpit padrão

Decisão: **Qualquer operação relevante em fluxos deve ser possível via Console de Fluxos**, não apenas por scripts ou acesso direto ao banco.

Implica:
- A criação de fluxos a partir de templates sempre será exposta via console;
- Mudança de estado, reprocessamento e troca de agente precisam continuar acessíveis via UI;
- Ops “esotéricas”, se necessárias, devem ser justificadas como operações de segundo nível.

### 5.2.4 Telemetria mínima obrigatória

Decisão: Métricas e logs definidos na S30 formam o **piso mínimo de observabilidade** para fluxos.

- Métricas `inspectah_flow_executions_*` e `inspectah_flow_latency_seconds` passam a ser linha de base;
- Logs estruturados com `flow_id`, `exec_fluxo_id`, `exec_etapa_id`, `item_id`, `tipo_entrada`, `status` são obrigatórios em execuções de fluxo;
- Futuras sprints podem adicionar mais campos ou métricas, mas não remover o que foi estabelecido aqui sem substituto claro.

### 5.2.5 Scorecards, gates e bundles como padrão de sprint

Decisão: O modelo de **gates + scorecards + bundle de evidências** adotado na S30 é o padrão para as demais sprints de E28.

- S31–S35 devem adotar o mesmo padrão de nomeação (`S31_G*`, `S32_G*`, etc.);
- Cada sprint deve produzir um bundle `inspectah_sXX_evidence_bundle.zip` equivalente;
- ORR passa a ser rito fixo, não exceção.

---

## 5.3 Riscos Estruturais, Trade-offs e Monitoração Contínua

Nem tudo é perfeito: a S30 faz escolhas. Este bloco explicita os principais **riscos estruturais e trade‑offs** assumidos, e como monitorá‑los.

### 5.3.1 Complexidade do modelo de fluxos

Risco:
- O modelo de fluxos v1.5 já nasce relativamente rico (steps, templates, execuções, logs de operação). Isso aumenta a curva de aprendizado e a superfície de bugs.

Mitigação:
- Manter documentação de fluxos sempre atualizada (Cap. 1 e 3 como fonte);
- Garantir que testes de serviço (`tests/flows/test_service.py`) cubram casos complexos;
- Tratar qualquer tentativa de criar pipelines paralelos como **cheiro forte de dívida técnica**.

### 5.3.2 Acoplamento com ingestão

Risco:
- Se as regras de roteamento em `routing_policy` dependerem demais de detalhes da ingestão, uma mudança em ingestão pode quebrar fluxos ou vice‑versa.

Mitigação:
- Manter fronteira clara: ingestão entrega **eventos** com contrato estável (`IngestionEvent`), fluxos decidem o resto;
- Documentar o contrato ingestão→fluxos no Cap. 3 e mantê‑lo versionado;
- Monitorar erros onde `tipo_entrada` inesperado chega a `route_event_to_flow`.

### 5.3.3 Risco operacional de reprocessamento

Risco:
- Reprocessamento mal usado pode criar carga artificial enorme, saturando o sistema.

Mitigação:
- Limites conservadores por padrão em `reprocess_items` (N máximo, janelas de tempo estreitas);
- Observabilidade dedicada para reprocessamentos (métricas de volume por fluxo e por período);
- Logs de operação ricos (`FlowOperationLog`) para detectar abuso ou uso inadequado.

### 5.3.4 Risco de “cockpit em slide”

Risco:
- Console de Fluxos virar uma UI bonita, mas pouco usada na operação real (pessoal de operações preferindo scripts customizados).

Mitigação:
- Exigir que qualquer operação crítica em produção use o console como caminho principal;
- Ajustar UX continuamente a partir de feedback de operação;
- Tratar o uso de scripts diretos como exceção auditável, não default.

### 5.3.5 Planos de monitoramento pós‑GO

Após GO da S30, recomenda‑se:
- acompanhar por 2–4 semanas:
  - taxa de erro de fluxos de notícias;
  - latência p95 de execução por fluxo;
  - volume de reprocessamento por dia;
- registrar aprendizados em um pequeno **post‑mortem positivo** (o que funcionou, o que doeu, o que mudou na operação).

---

## 5.4 Continuidade: S30 como Base para S31–S35 no Épico E28

Por fim, este bloco posiciona a S30 dentro da trajetória completa do Épico E28.

### 5.4.1 O que S31 não precisa mais discutir

Graças à S30, as próximas sprints do E28 **não precisam rediscutir**:
- se fluxos existem — já existem e estão implementados;
- se há cockpit — já há um Console de Fluxos funcional para notícias;
- se há telemetria básica — já existem métricas e logs padronizados;
- se há padrão de gates/scorecards/bundle — já foi estabelecido e rodou em produção de sprint.

S31+ podem partir do pressuposto de que **fluxo‑pivô de notícias é infra disponível**.

### 5.4.2 Possíveis focos para S31–S35

Exemplos de linhas de continuidade (não são spec, mas hints):

- **S31 — Generalização de fluxos**  
  Expandir modelo para outros tipos de entrada (dados diretos, casos de verificação específica) reaproveitando o que a S30 criou.

- **S32 — Integração profunda com Debunker e Truth‑DB**  
  Conectar `FlowExecution` e `FlowStepExecution` com casos, evidências e decisões de verdade.

- **S33 — Cockpit avançado**  
  Adicionar visão multi‑fluxo, alertas, painéis agregados e ferramentas de comparação de fluxos.

- **S34 — Ferramentas de replay e simulação**  
  Permitir replays controlados de execuções antigas para testar novas configurações de fluxo.

- **S35 — Endurecimento e escalabilidade**  
  Otimizar performance, resiliência e custo operacional dos fluxos em larga escala.

### 5.4.3 Regra de compatibilidade para sprints futuras

Todas as sprints S31–S35 que alterarem o modelo de fluxos ou o Console devem respeitar:
- compatibilidade com migrations e dados produzidos pela S30;
- preservação (ou migração explícita) de IDs de execução e etapas já gerados;
- manutenção do padrão de métricas e logs (ou substituição documentada);
- continuidade do bundle de evidências por sprint.

---

Com isso, o Capítulo 5 da Sprint 30 garante que o trabalho não morre no merge. Ele vira **infraestrutura institucionalizada**: com donos claros, decisões permanentes explícitas, riscos mapeados e um caminho direto para as próximas sprints do Épico E28.