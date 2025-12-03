# Sprint 29 — Capítulo 6
# Riscos, Débitos, Mitigações e Long Tail da S29

## 1. Papel do Capítulo 6 na Sprint 29

Os capítulos 1 a 5 da Sprint 29 responderam:

- o que a S29 quer resolver (Cap. 1);
- como medir GO/NO-GO (Cap. 2);
- onde cada peça vive na arquitetura/filemap (Cap. 3);
- como executar em waves com evidências (Cap. 4);
- como amarrar S29 em produto, ORR e Épico E28 (Cap. 5).

O Capítulo 6 existe para garantir que nada importante fique "debaixo do tapete". Ele registra, de forma explícita e sem romance:

- riscos conhecidos (técnicos, de produto/governança, operacionais e de programa);
- débitos técnicos assumidos na S29;
- plano de mitigação e follow-up (o que fazer, quem puxa, onde registrar);
- critérios de monitoramento pós-sprint, incluindo quando acionar rollback ou limitar escopo;
- como o conhecimento da S29 deve ser carregado como long tail para as próximas sprints de E28 e para S23–S25.

A Sprint 29 só é considerada "encerrada com consciência" quando este Capítulo 6 estiver escrito, entendido e aceito.

---

## 2. Mapa de riscos da Sprint 29

Esta seção registra os principais riscos associados à introdução de fluxos de agentes configuráveis. Eles são agrupados em quatro dimensões:

- riscos técnicos;
- riscos de produto/governança;
- riscos operacionais;
- riscos de programa/roadmap.

Cada risco deve ter: descrição, severidade (baixa/média/alta), probabilidade aproximada (baixa/média/alta) e mitigação recomendada.

### 2.1. Riscos técnicos

1. **Risco T1 — Complexidade futura do modelo de fluxo**

- Descrição: o modelo atual de fluxo (lista linear de steps por domínio) é simples e adequado para v1, mas pode se tornar limitante quando forem introduzidos branching, condicional e versões múltiplas. Existe risco de o modelo precisar ser refeito, causando retrabalho em código e dados.
- Severidade: média-alta.
- Probabilidade: média.
- Fatores agravantes:
  - mudanças apressadas para atender casos complexos sem redesenho cuidadoso;
  - pressão para suportar "tudo" rapidamente (condições, subfluxos, etc.).
- Mitigação inicial:
  - documentar claramente as limitações da v1 no ORR (Cap. 5);  
  - tratar E28.3 (branching) como sprint de design profundo, não apenas implementação incremental;  
  - manter `AgentFlowConfig` modular, permitindo extensão sem ruptura (campos opcionais, tabelas auxiliares para condicionais, etc.).

2. **Risco T2 — Acoplamento forte ao catálogo de papéis**

- Descrição: o validador e a UI dependem de um catálogo de papéis de agentes (INTERPRETER, CLASSIFIER, DEBUNKER, DECISION_MAKER, etc.). Se esse catálogo for muito rígido ou espalhado em vários lugares, a evolução se torna dolorosa.
- Severidade: média.
- Probabilidade: alta (catálogo tende a crescer).
- Mitigação inicial:
  - centralizar catálogo em módulo único (ex.: `app/agents/catalog.py`) e reusar em validador e UI;  
  - evitar duplicar strings de papéis no frontend;  
  - planejar, em E28.2/E28.3, como representar papéis customizados ou parametrizados.

3. **Risco T3 — Performance do runtime em domínios com fluxo mais pesado**

- Descrição: a introdução de fluxos configuráveis incentiva a adicionar agentes e passos. Em domínios muito ativos, isso pode gerar pipelines lentos ou caros.
- Severidade: média.
- Probabilidade: média.
- Mitigação inicial:
  - instrumentar tempo de execução por agente e por fluxo desde cedo;  
  - definir limites razoáveis de passos por fluxo em domínios de alto volume;  
  - planejar E28.4 com foco em tuning e métricas, não apenas visualização bonita.

4. **Risco T4 — Falhas de consistência entre back e front**

- Descrição: divergência entre validações no backend (validador) e expectativas da UI (por exemplo, UI permitindo combinação que backend rejeita).
- Severidade: média.
- Probabilidade: média.
- Mitigação inicial:
  - garantir que a UI nunca implemente regras de negócio que não existam também no backend;  
  - tests de API cobrindo invariantes;  
  - comunicação direta entre squads de backend e frontend quando invariantes forem evoluídas.

### 2.2. Riscos de produto e governança

1. **Risco P1 — Mudanças de fluxo com impacto em decisões de verdade**

- Descrição: alteração de fluxos em domínios sensíveis (política, mercado financeiro, saúde pública) pode modificar profundamente o caminho de debunking e decisão de verdade. Erros de configuração ou mudanças apressadas podem gerar decisões menos confiáveis.
- Severidade: alta.
- Probabilidade: média.
- Mitigação inicial:
  - restringir inicialmente a S29 a domínios piloto com menor impacto crítico ou sob monitoramento próximo;  
  - exigir `change_reason` detalhado;  
  - registrar explicitamente, no ORR, que E28.2 (versionamento + approvals) é prioridade alta para domínios de alta sensibilidade.

2. **Risco P2 — Ausência de approvals formais**

- Descrição: na v1, um único admin com acesso à feature pode alterar fluxos, sem dupla checagem formal.
- Severidade: alta para domínios sensíveis, média para domínios menos críticos.
- Probabilidade: média.
- Mitigação inicial:
  - política operacional: definir quem pode mexer em quais domínios (fora do código) e registrar isso em documentação interna;  
  - tratar workflow de approvals como foco explícito de E28.2;  
  - considerar logs e audit trails como mecanismo temporário de dissuasão/investigação.

3. **Risco P3 — Sobrecarga cognitiva para operadores**

- Descrição: operadores podem não ter modelo mental claro sobre o que cada agente faz e sobre efeitos de mudar a ordem.
- Severidade: média.
- Probabilidade: alta.
- Mitigação inicial:
  - incluir documentação de "guia rápido" de fluxos na própria UI ou em docs adjacentes;  
  - começar com poucas opções e papéis principais, expandindo gradualmente;  
  - em domínios piloto, recomendar alterações apenas por pessoas que acompanham também os efeitos em runtime.

### 2.3. Riscos operacionais

1. **Risco O1 — Falha silenciosa de fallback de fluxo**

- Descrição: em caso de ausência ou erro na configuração de fluxo, o sistema pode usar fallback padrão (ou fluxo antigo), e isso acontecer sem visibilidade clara.
- Severidade: média.
- Probabilidade: média.
- Mitigação inicial:
  - logar explicitamente quando fallback é usado (incluindo domínio, motivo e fluxo aplicado);  
  - incluir métrica simples "% de itens que usaram fallback de fluxo";  
  - considerar alerta se esse percentual subir demais.

2. **Risco O2 — Janela de inconsistência durante alterações de fluxo**

- Descrição: enquanto uma alteração está sendo feita (especialmente se o fluxo for pesado), pode haver uma janela breve em que requests diferentes veem configurações diferentes.
- Severidade: baixa/média (dependendo do domínio).
- Probabilidade: baixa/média.
- Mitigação inicial:
  - preferir operações atômicas (substituir conjunto completo de steps em transação única);  
  - evitar editar fluxos em horários de maior carga para domínios críticos;  
  - registrar recomendação operacional no ORR.

### 2.4. Riscos de programa/roadmap

1. **Risco R1 — E28 ficar "parado" na v1 de fluxo**

- Descrição: o sistema começa a usar o fluxo configurável v1 e não há energia ou prioridade para evoluir E28 (versionamento, branching, métricas), gerando um meio-termo perene.
- Severidade: média.
- Probabilidade: média.
- Mitigação inicial:
  - registrar explicitamente, no Cap. 5 e no ORR, trilhas de E28.2, E28.3 e E28.4;  
  - priorizar ao menos uma dessas trilhas no planejamento seguinte;  
  - tratar o "fluxo configurável" como eixo estratégico, não apenas conveniência interna.

2. **Risco R2 — Divergência entre E28 e sprints de Verdade/Debunker/Comitês (S23–S25)**

- Descrição: decisão em E28 sobre fluxo de agentes pode entrar em conflito ou ficar desalinhada com decisões nas sprints de verdade, debunker e comitês.
- Severidade: alta.
- Probabilidade: média.
- Mitigação inicial:
  - usar papéis de fluxo como pontos explícitos de integração com os squads Verdade & Interpretação;  
  - garantir que decisões de S23–S25 sobre comitês, promoção de verdade, evidência etc. se reflitam em invariantes de fluxo;  
  - criar momentos de revisão conjunta E28 ↔ S23–S25.

---

## 3. Débitos técnicos assumidos na Sprint 29

Além dos riscos, a S29 inevitavelmente deixa alguns débitos técnicos. Esta seção lista débitos explícitos, para não virarem "fantasmas" no código.

### 3.1. Débitos no backend

1. **D1 — Cobertura parcial de testes em cenários extremos**

- Situação: testes de validador e API cobrem casos principais, mas podem não cobrir combinatórias de papéis mais exóticas ou limites de tamanho de fluxo.
- Impacto: bugs só aparecem em casos de fluxo muito grandes ou incomuns.
- Follow-up sugerido: criar, em E28.2 ou E28.3, uma suíte de testes focada em limites (tamanho máximo de fluxo, número máximo de domínios, etc.).

2. **D2 — Catálogo de papéis ainda simplificado**

- Situação: catálogo em v1 suporta papéis principais, sem estrutura para tipos/subtipos ou hierarquias complexas.
- Impacto: possíveis duplicações ou gambiarras futuras se o catálogo crescer sem redesign.
- Follow-up sugerido: planejar um redesign do catálogo em conjunto com sprints de Verdade/Debunker, mantendo compatibilidade com fluxo.

3. **D3 — Instrumentação mínima em runtime**

- Situação: logs de execução de fluxo existem, mas podem não ter ainda todos os campos desejáveis (correlação com casos, IDs de comitê, etc.).
- Impacto: menos poder de análise inicial do que o ideal.
- Follow-up sugerido: tratar o enriquecimento de logs como parte de E28.4 (métricas e tuning).

### 3.2. Débitos no frontend

1. **D4 — UX básica do editor de fluxo**

- Situação: o editor v1 é baseado em lista, com controles básicos de adicionar/remover/mover.
- Impacto: pode não ser ótimo para fluxos maiores ou para operadores menos técnicos.
- Follow-up sugerido: em E28.3/E28.4, explorar visualizações mais avançadas (agrupamentos, níveis, possivelmente grafos simples).

2. **D5 — Validação limitada no client**

- Situação: parte da validação é delegada ao backend (corretamente), mas a UX ainda pode não antecipar todos os erros (ex.: posição do DECISION_MAKER) antes do envio.
- Impacto: experiência um pouco mais trial-and-error, especialmente para usuários novos.
- Follow-up sugerido: adicionar validações client-side que não dupliquem lógica de negócio, mas usem informações estáticas (por exemplo, não permitir DECISION_MAKER em posição diferente da última na UI).

### 3.3. Débitos de documentação

1. **D6 — Documentação de operação ainda mínima**

- Situação: o ORR e o Cap. 5 registram o estado do produto, mas podem não ser suficientes como "manual de operador".
- Impacto: onboarding mais difícil para novos admins.
- Follow-up sugerido: criar um doc curto estilo "Como editar fluxos de agentes" com screenshots, dicas e armadilhas a evitar.

2. **D7 — Ausência de exemplos completos de fluxos por domínio**

- Situação: não há ainda catálogo de exemplos canônicos de fluxo por tipo de domínio (política, economia, saúde etc.).
- Impacto: cada operador precisa inferir sozinho o que é um fluxo "sensato".
- Follow-up sugerido: em E28.2/E28.3, construir uma lista de fluxos de referência junto com o squad Verdade & Interpretação.

---

## 4. Plano de mitigação e follow-up

Aqui o Capítulo 6 transforma riscos e débitos em um mini-plano de ação.

### 4.1. Itens críticos (curto prazo)

1. **Governança mínima de quem pode alterar fluxos**

- Ação: definir, em documento de operação, quais papéis de usuário podem editar fluxos em domínios piloto, e com quais restrições.
- Dono sugerido: squad de Produto + squad de Operações/Plataforma.
- Prazo sugerido: imediatamente após o merge da S29.

2. **Monitoramento de fallback de fluxo**

- Ação: configurar pelo menos uma métrica simples de uso de fallback de fluxo e uma forma de inspecionar logs associados.
- Dono sugerido: squad de Observabilidade/Plataforma.
- Prazo sugerido: até o fim do ciclo de piloto.

3. **Comunicação interna sobre limitações da v1**

- Ação: apresentar o ORR da S29 e o resumo de limitações para stakeholders relevantes (produto, engenharia, operação, conselho técnico).
- Dono sugerido: PO/PM do Programa 1.
- Prazo sugerido: logo após o ORR formal.

### 4.2. Itens de médio prazo (E28.2/E28.3)

1. **Versionamento e approvals**

- Ação: entrar como primeiro candidato forte de escopo para E28.2, com foco em domínios sensíveis.

2. **Branching e fluxos condicionais**

- Ação: preparar descoberta e design em conjunto com squads de Verdade, Debunker e Comitês (S23–S25), antes de implementar, para evitar modelo mal encaixado.

3. **Métricas e painel de fluxos**

- Ação: incluir em E28.4 (ou equivalentemente numerada) um foco em observabilidade e tuning.

---

## 5. Monitoramento pós-sprint, rollback e escopo

A S29 introduz uma camada sensível no pipeline. O Capítulo 6 define critérios mínimos para:

- acompanhar o comportamento do sistema após a sprint;
- decidir quando recuar (rollback ou escopo reduzido);
- decidir quando ampliar o uso da feature.

### 5.1. Indicadores de saúde a observar

Sugestões de indicadores:

1. **Erro de pipeline associado a fluxo**

- Número de falhas de processamento por domínio piloto atribuíveis a fluxo (por exemplo, falha em agente, timeout);
- taxa antes/depois de ativar fluxos configuráveis.

2. **Uso de fallback**

- Percentual de itens por domínio piloto que usam fallback de fluxo, em vez de fluxo configurado.

3. **Tempo médio de processamento por item**

- Comparação antes/depois da S29 para domínios piloto;
- foco em outliers (itens que demoram muito mais após mudanças de fluxo).

4. **Incidentes de produto atribuídos a alteração de fluxo**

- Casos em que uma mudança de fluxo é apontada como causa provável de decisões de verdade equivocadas, atrasadas ou inconsistentes.

### 5.2. Critérios de rollback

Não faz sentido ter uma feature pilotando domínios críticos se não houver critérios claros de recuo. Exemplos de critérios:

- aumento súbito e sustentado de erros de pipeline após alteração de fluxo em um domínio piloto;
- incidentes de alto impacto associados claramente a erro de fluxo;
- comportamento inesperado em domínios altamente sensíveis, mesmo sem falhas técnicas graves.

Rollback, neste contexto, pode significar:

- voltar temporariamente para um fluxo padrão fixo;
- desativar a edição de fluxos para um domínio específico até mitigação ser implementada;
- em casos extremos, suspender o uso de fluxos configuráveis até E28.2.

### 5.3. Critérios para ampliar escopo

Por outro lado, se o piloto estiver saudável, o Capítulo 6 recomenda critérios para ampliar uso:

- período mínimo de operação estável (por exemplo, algumas semanas) em domínios piloto sem incidentes relevantes;
- evidência de que a capacidade de configurar fluxo trouxe valor (por exemplo, ajustar pipeline para reduzir ruído ou melhorar velocidade de decisão);
- operadores confortáveis com a ferramenta e com entendimento razoável das consequências das mudanças.

---

## 6. Long tail da S29 — como carregar esse conhecimento para frente

A S29 não deve ser tratada como um evento isolado. Este Capítulo 6 define o que precisa ser carregado adiante como "long tail" da sprint.

### 6.1. Artefatos que viram referência de longo prazo

1. **`docs/sprint_29_orr_summary.md`**

- Referência principal para entender o estado do produto após S29.

2. **Capítulos 3–6 da S29**

- Cap. 3: arquitetura e filemap do fluxo de agentes;  
- Cap. 4: plano de execução em waves;  
- Cap. 5: ORR, estado de produto, integração com E28;  
- Cap. 6: este mapa de riscos/débitos/mitigações.

3. **Bundle de evidências `inspectah_s29_evidence_bundle.zip`**

- Prova concreta de como a sprint foi executada (tests, logs, gates, etc.).

### 6.2. Decisões que não podem ser esquecidas

Algumas decisões de S29 precisam ser lembradas em sprints futuras:

- fluxo de agentes v1 é **linear e por domínio**, sem branching explícito;  
- a exigência de `change_reason` é parte do contrato de governança, não uma "opção";  
- papéis como DEBUNKER e DECISION_MAKER devem estar presentes e em posições específicas em domínios sensíveis;
- fluxos configuráveis são introduzidos em **escopo piloto**, com critérios claros de ampliação e rollback.

### 6.3. Pontos de atenção para squads futuros

Squads que forem trabalhar em E28.2/E28.3/E28.4, S23–S25 ou outras sprints que mexam em fluxo devem:

- ler pelo menos o Cap. 3 (arquitetura), Cap. 5 (estado de produto) e Cap. 6 (riscos/mitigações);  
- tratar `AgentFlowConfig` e seu ecossistema como fundação, questionando mudanças radicais apenas com forte justificativa;  
- reforçar a integração entre fluxo de agentes e política de verdade/contestação, em vez de criar novos atalhos.

---

## 7. Resumo do Capítulo 6

O Capítulo 6 encerra a Sprint 29 sob a ótica de riscos, débitos, mitigação e long tail. Em termos práticos, ele garante que:

- os perigos de ter fluxos configuráveis em domínios sensíveis foram reconhecidos e não varridos para baixo do tapete;
- os débitos técnicos não vão desaparecer na névoa de commits futuros, mas estão registrados para orientar E28.x;
- há um plano básico de mitigação (curto e médio prazo), com candidatos claros de escopo para próximas sprints;
- há critérios racionais tanto para rollback quanto para expansão de escopo;
- o conhecimento da S29 é carregado como referência, e não refeito do zero em cada nova sprint.

Com isso, a Sprint 29 deixa de ser apenas "a sprint que criou a UI de fluxo de agentes" e passa a ser um bloco sólido no Programa 1: especificada, executada, medida, julgada e com riscos e débitos explicitamente sob controle.

