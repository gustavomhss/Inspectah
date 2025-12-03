# Inspectah — Sprint 30 — Capítulo 5 — Bloco 4
## Continuidade da Sprint 30 no Épico E28 (S31–S35) e no Programa 1

Este bloco posiciona a Sprint 30 dentro da trajetória maior do **Épico E28** e do **Programa 1**. A pergunta aqui é: 

> “O que muda estruturalmente depois da S30 e como as próximas sprints devem se apoiar nisso sem reinventar a roda?”

A ideia é transformar a S30 em **piso**, não em experimento isolado.

---

## 5.4.1 O que passa a ser verdade e não precisa mais ser discutido em S31–S35

Após a Sprint 30, as próximas sprints do Épico E28 podem assumir, como fatos estabelecidos:

1. **Existe um fluxo‑pivô de notícias operável via console**
   - O fluxo de notícias:
     - é definido no módulo `app/flows/`;
     - tem template canônico em `FlowTemplate`;
     - possui estados e transições estáveis (S30);
     - pode ser criado, ativado, pausado, deprecado e reprocessado via Console de Fluxos.

2. **Existe uma engine de fluxos integrada à ingestão**
   - Eventos de ingestão para notícias (`tipo_entrada = noticia_texto`) são roteados para fluxos via `routing_policy`;
   - A engine de execução (`FlowExecutionEngine`) já orquestra etapas de intérprete, classificador, analistas, debunkers e decision maker para o fluxo‑pivô.

3. **Existe um cockpit funcional para operar fluxos**
   - O Console de Fluxos lista fluxos, mostra detalhes, execuções e jornadas;
   - Operações básicas (state change, reprocessamento limitado, troca de agente) estão implementadas e testadas.

4. **Existe telemetria mínima obrigatória de fluxos**
   - Métricas de execução, falha e latência de fluxos estão disponíveis;
   - Logs estruturados permitem reconstruir jornadas de execução do fluxo de notícias;
   - Há um cenário E2E documentado para fluxo de notícias, com evidências guardadas.

5. **Existe um modelo de sprint replicável para E28**
   - Gates numerados e scripts em `bin/s30_g*.sh`;
   - Scorecards e bundle de evidências;
   - Ritual de ORR e decisão GO/NO‑GO baseada em artefatos.

Tudo isso passa a ser **infra de referência** para S31–S35.

---

## 5.4.2 Linhas naturais de evolução para as próximas sprints do E28

O Épico E28 cobre S29–S35. A S29 e a S30 estabelecem as fundações. As sprints seguintes podem ser pensadas em grandes linhas (não é spec, é mapa de tendência):

### Linha 1 — Generalização de fluxos (S31)

Foco provável:
- sair do caso único “notícia de texto” e permitir fluxos para outros tipos de entrada, por exemplo:
  - dados numéricos/estruturados;
  - documentos longos (relatórios, decisões judiciais, etc.);
  - entradas já pré‑estruturadas pela ingestão (por tema/caso);
- fortalecer o modelo de **tipos de entrada** e **gramática de fluxos** sem quebrar o fluxo‑pivô de notícias.

Como S31 se apoia na S30:
- reutiliza a engine, o modelo de estados, o console e a telemetria;
- adiciona, no máximo, novas parametrizações e templates, não uma segunda “engine paralela”.

### Linha 2 — Integração com Verdade, Casos e Evidências (S32)

Foco provável:
- conectar execuções de fluxo (`FlowExecution`, `FlowStepExecution`) com:
  - casos (entidades que representam “questões investigadas” no Inspectah);
  - evidências (documentos, dados, citações);
  - decisões de verdade/falsidade e graus de incerteza.

Como S32 se apoia na S30:
- usa `flow_id`, `exec_fluxo_id` e `exec_etapa_id` como chaves para amarrar fluxos a casos e evidências;
- utiliza o fluxo‑pivô de notícias como **exemplo concreto** de como uma notícia vira um conjunto de evidências e decisões;
- não precisa reimplementar orquestração, apenas plugar camadas de verdade/casos em cima.

### Linha 3 — Cockpit avançado e visão multi‑fluxo (S33)

Foco provável:
- evoluir o Console de Fluxos para:
  - visão agregada de múltiplos fluxos e suas saúdes;
  - filtros por tipo de entrada, estado, taxa de erro, latência;
  - comparações entre fluxos (A/B de pipelines);
  - alertas e indicadores de risco operacional.

Como S33 se apoia na S30:
- usa o Console atual como base, expandindo componentes e rotas;
- reutiliza as métricas e logs de fluxo como fontes para dashboards;
- mantém o fluxo‑pivô de notícias como “primeiro cidadão” que deve continuar totalmente operável.

### Linha 4 — Replay, simulação e experimentação (S34)

Foco provável:
- permitir que operadores e squads de verdade/experimentos:
  - rodem **replays** de execuções usando fluxos novos, sem impactar produção;
  - simulem novas topologias de fluxo com base em dados históricos;
  - comparem saídas de fluxos diferentes para o mesmo conjunto de entradas.

Como S34 se apoia na S30:
- reutiliza o modelo de execuções e logs como base para replays;
- reaproveita IDs e telemetria para reproduzir jornadas sem ambiguidade;
- pode introduzir um “modo simulação” na engine e no console.

### Linha 5 — Escalabilidade, resiliência e custos (S35)

Foco provável:
- otimizar desempenho e custo dos fluxos em produção:
  - dimensionar pipelines para tráfego real de notícias;
  - otimizar armazenamento de execuções e logs;
  - introduzir mecanismos de backpressure e retenção inteligente.

Como S35 se apoia na S30:
- usa as métricas S30+ como base para decisões de tuning;
- mantém compatibilidade com contratos de telemetria e IDs;
- refina a engine e o console sem quebrar o fluxo‑pivô ou os artefatos de evidência.

---

## 5.4.3 Regras de compatibilidade para sprints futuras (S31–S35)

Para evitar que as próximas sprints desarmonizem o que a S30 construiu, estabelecemos um conjunto de **regras de compatibilidade mínima**:

1. **Compatibilidade de dados e IDs**
   - S31–S35 não podem invalidar, sem migração planejada:
     - tabelas de fluxo e execuções criadas na S30;
     - semantics de `flow_id`, `exec_fluxo_id`, `exec_etapa_id`;
     - ligações com `FlowTemplate` e `FlowOperationLog`.

2. **Compatibilidade de telemetria**
   - Métricas `inspectah_flow_*` introduzidas na S30:
     - devem continuar existindo ou ser substituídas por métricas com mapeamento claro;
     - não podem simplesmente “sumir” quebrando painéis ou ORR;
   - logs estruturados devem preservar pelo menos o conjunto mínimo de campos.

3. **Compatibilidade de Console**
   - O Console de Fluxos deve permanecer capaz de:
     - listar o fluxo‑pivô de notícias;
     - operar seus estados;
     - exibir suas execuções;
     - acionar reprocessamento dentro das regras;
   - qualquer redesign grande deve manter essas capacidades ou fornecer rota de migração.

4. **Compatibilidade de gates e bundles**
   - Cada sprint de E28 (S31–S35) deve:
     - definir e implementar seus próprios gates G0–G*;
     - emitir scorecards e bundle de evidências;
     - manter o padrão de decisão GO/NO‑GO ancorada nesses artefatos.

5. **Compatibilidade de contratos de fronteira**
   - Fronteiras ingestão→fluxos e fluxos→Verdade/Casos devem ser tratadas como **APIs internas formais**;
   - qualquer alteração nessas fronteiras precisa aparecer em Cap. 3 e 5 da sprint que faz a mudança.

---

## 5.4.4 Como usar a S30 como “pacote base” em novas sprints

Para squads que vão trabalhar em S31–S35, a S30 deve ser tratada como um **pacote base**:

1. Antes de especificar qualquer novo fluxo ou cockpit relacionado, a sprint futura deve:
   - ler os Capítulos 1, 3 e 5 da S30;
   - entender os contratos de fluxos, estados, telemetria e console;
   - verificar o bundle de evidências da S30 para ver exemplos concretos.

2. A spec de uma nova sprint deve ter uma seção explícita:
   - “Dependências e compatibilidade com S30 (Fluxos & Cockpit)”;
   - listando o que será reutilizado, estendido ou ajustado.

3. Qualquer alteração de contrato estabelecido pela S30 precisa ser:
   - justificada em nível de épico/programa;
   - acompanhada de plano de migração (dados, telemetria, UX);
   - refletida em novos testes e em docs atualizados.

---

## 5.4.5 Regra de ouro para continuidade

A regra de ouro que amarra S30 e as próximas sprints de E28 é:

> “Nenhuma sprint de E28 deve fingir que S30 não existiu.”

Traduzindo:
- não é aceitável que S31–S35 redesenhem fluxo de notícias “do zero” ignorando a base da S30;
- refinamentos e generalizações são bem‑vindos, desde que respeitem os contratos estabelecidos ou tragam migrações claras;
- o Programa 1 passa a enxergar a S30 como **primeiro tijolo fixo** do edifício de fluxos.

---

Com isso, o Bloco 4 fecha o Capítulo 5 da Sprint 30, posicionando claramente a S30 como fundação do Épico E28: um fluxo‑pivô de notícias operável, observável e auditável, sobre o qual as próximas sprints podem construir sem medo de estar pisando em areia movediça.