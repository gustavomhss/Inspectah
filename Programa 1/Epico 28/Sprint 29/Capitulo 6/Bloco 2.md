# Sprint 29 — Capítulo 6
## Bloco 2 — Mapa de riscos da S29 (técnicos, produto/governança, operacionais e de programa)

Este Bloco 2 aprofunda o primeiro dos quatro eixos do Capítulo 6: **riscos**. A ideia é sair do genérico e registrar, de forma concreta, quais são os principais riscos associados à introdução de fluxos de agentes configuráveis na Sprint 29.

Os riscos são organizados em quatro grupos:

- riscos técnicos;
- riscos de produto e governança;
- riscos operacionais;
- riscos de programa/roadmap.

Cada risco importante deve ter, no mínimo:

- descrição;  
- severidade (baixa/média/alta);  
- probabilidade aproximada (baixa/média/alta);  
- mitigação inicial ou recomendada.

Este mapa serve como referência para o ORR, para o plano de mitigação e para o planejamento de E28.x e das sprints de Verdade/Debunker/Comitês.

---

### 2.1. Riscos técnicos

**T1 — Complexidade futura do modelo de fluxo**  

- Descrição: o modelo atual de fluxo (lista linear de steps por domínio) é adequado para a v1, mas pode se tornar limitante quando forem introduzidos branching, condicionais, múltiplas versões ativas, experimentos A/B e integrações mais complexas com Truth-DB e comitês. Existe risco de o modelo precisar ser refeito de forma estrutural, gerando retrabalho em código, migrations e dados.
- Severidade: média-alta.  
- Probabilidade: média.  
- Fatores agravantes:  
  - pressão para "encaixar" features avançadas (condicionais, subfluxos, multi-tenant) sem redesign adequado;  
  - uso crescente de hacks locais para atender casos específicos.
- Mitigação inicial:  
  - documentar as limitações da v1 explicitamente no ORR (Cap. 5);  
  - tratar E28.3 (branching/condicionais) como sprint de **design** antes de código, com envolvimento do squad Verdade & Interpretação;  
  - manter `AgentFlowConfig` extensível (campos opcionais, tabelas auxiliares) para permitir evolução sem migrações destrutivas.

**T2 — Acoplamento forte ao catálogo de papéis de agentes**  

- Descrição: o validador de fluxo, a UI de admin e o runtime dependem de um catálogo de papéis (INTERPRETER, CLASSIFIER, DEBUNKER, DECISION_MAKER, etc.). Se esse catálogo crescer de forma desorganizada ou ficar espalhado em múltiplos lugares (backend, frontend, docs), ajustes se tornam arriscados e propensos a inconsistência.
- Severidade: média.  
- Probabilidade: alta (catálogo tende a crescer com E28.x e S23–S25).  
- Mitigação inicial:  
  - centralizar catálogo em um módulo único no backend (ex.: `app/agents/catalog.py`), usado por validador e serviços;  
  - expor esse catálogo de forma estável para o frontend (via endpoint ou schema), evitando duplicar strings "na mão";  
  - planejar, em E28.2/E28.3, a introdução de tipos/subtipos de papéis, em vez de proliferar rótulos soltos.

**T3 — Performance do runtime em domínios com fluxos mais pesados**  

- Descrição: fluxos configuráveis tornam natural adicionar mais passos e agentes. Em domínios de alto volume, isso pode levar a pipelines lentos, caros ou instáveis (time outs, filas acumuladas, backpressure).
- Severidade: média.  
- Probabilidade: média.  
- Mitigação inicial:  
  - desde a S29, registrar tempos de execução por agente e por fluxo em logs;  
  - definir limites operacionais (por exemplo, número máximo de passos configuráveis por domínio em v1);  
  - tratar E28.4 como sprint focada em métricas e tuning de fluxo, não apenas visualização.

**T4 — Inconsistência entre validações de backend e UX de frontend**  

- Descrição: existe risco de a UI permitir combinações de passos ou parâmetros que o backend rejeita, gerando frustração para operadores (ciclo editar → salvar → erro pouco claro).
- Severidade: média.  
- Probabilidade: média.  
- Mitigação inicial:  
  - garantir que a lógica de invariantes viva **somente** no backend, com a UI funcionando como "cliente inteligente" que evita o óbvio usando informações estáticas (ex.: não permitir DECISION_MAKER fora da última posição);  
  - manter testes de API cobrindo invariantes críticos;  
  - alinhar squads de backend/frontend sempre que invariantes forem alteradas.

**T5 — Instrumentação de runtime ainda minimalista**  

- Descrição: a S29 introduz logs de execução de fluxo, mas o conjunto de campos e correlações ainda é mínimo. Isso pode limitar análises futuras ou dificultar investigações de incidentes.
- Severidade: média.  
- Probabilidade: alta (v1 de instrumentação quase sempre é enxuta).  
- Mitigação inicial:  
  - documentar, neste capítulo, quais campos existem hoje e quais são desejáveis no futuro;  
  - tratar o enriquecimento de logs como item explícito de E28.4 (métricas, tuning e painéis de fluxo).

---

### 2.2. Riscos de produto e governança

**P1 — Impacto de mudanças de fluxo em decisões de verdade e reputação**  

- Descrição: alterar o fluxo em domínios sensíveis (política, saúde, mercado financeiro, temas jurídicos) pode mudar quais agentes analisam um item e em que ordem. Configurações inadequadas podem reduzir a robustez do processo de checagem ou introduzir vieses.
- Severidade: alta.  
- Probabilidade: média.  
- Mitigação inicial:  
  - restringir a v1 de fluxos configuráveis a domínios piloto com riscos controlados;  
  - registrar claramente no ORR quais domínios são piloto e sob quais condições;  
  - priorizar E28.2 (versionamento/approvals) como proteção adicional para domínios de alta sensibilidade.

**P2 — Ausência de workflow formal de approvals em v1**  

- Descrição: na S29, qualquer admin com permissão para acessar a feature pode alterar fluxos, sem dupla aprovação formal.
- Severidade: alta para domínios sensíveis, média para demais.  
- Probabilidade: média.  
- Mitigação inicial:  
  - estabelecer, em documentação operacional, quais perfis podem alterar fluxos e para quais domínios;  
  - exigir `change_reason` detalhado, com trilha de auditoria (`updated_by`, `updated_at`);  
  - tratar workflow de approvals como requisito principal de E28.2.

**P3 — Sobrecarga cognitiva para operadores admin**  

- Descrição: operadores podem não ter clareza suficiente sobre o que cada papel de agente faz ou sobre as consequências de alterar a ordem de execução. Isso aumenta o risco de alterações mal calibradas.
- Severidade: média.  
- Probabilidade: alta (especialmente no início do piloto).  
- Mitigação inicial:  
  - produzir documentação curta de "boas práticas de fluxo" com exemplos;  
  - começar com poucos domínios piloto e poucas variações de fluxo;  
  - evitar dar acesso irrestrito à edição de fluxos para perfis sem contexto técnico ou de produto.

**P4 — Expectativa irreal sobre capacidade da v1**  

- Descrição: stakeholders podem assumir que o sistema já suporta versionamento completo, branching complexo e workflows de aprovação, por simplesmente verem uma UI de fluxo configurável.
- Severidade: média.  
- Probabilidade: alta.  
- Mitigação inicial:  
  - usar o ORR e o Capítulo 5 para listar explicitamente o que **não** está incluso na v1;  
  - reforçar, em comunicações internas, que E28.x será necessário para chegar na visão completa.

---

### 2.3. Riscos operacionais

**O1 — Uso silencioso de fallback de fluxo**  

- Descrição: em situações de erro de configuração ou ausência de fluxo para um domínio, o runtime pode recorrer a um fluxo padrão/fallback. Se isso não for bem visível, o time pode acreditar estar usando o fluxo configurado, quando na verdade não está.
- Severidade: média.  
- Probabilidade: média.  
- Mitigação inicial:  
  - registrar explicitamente em log toda vez que fallback for usado (domínio, motivo, flow_id fallback);  
  - criar, mesmo que simples, uma métrica "% de itens que usaram fallback" por domínio;  
  - considerar alertas se esse percentual ultrapassar um limiar em domínios críticos.

**O2 — Janela de inconsistência durante alterações de fluxo**  

- Descrição: dependendo de como as alterações são aplicadas, pode haver uma breve janela em que requests diferentes veem configurações diferentes (especialmente em sistemas distribuídos ou com caches).
- Severidade: baixa/média.  
- Probabilidade: baixa/média.  
- Mitigação inicial:  
  - aplicar alterações de fluxo de forma atômica (substituição completa da configuração dentro de uma transação);  
  - evitar alterar fluxos em horários de pico para domínios de muito tráfego;  
  - documentar recomendações operacionais no ORR.

**O3 — Falta de visibilidade centralizada de fluxos configurados**  

- Descrição: se a UI ou APIs não oferecerem visão clara de quais domínios têm fluxos customizados e como estão, operações podem perder o controle da "paisagem" de fluxo.
- Severidade: média.  
- Probabilidade: média.  
- Mitigação inicial:  
  - garantir que a página principal de fluxos (AgentFlowsPage) ofereça visão global (domínio, número de passos, última alteração);  
  - no futuro, considerar um relatório exportável ou painel agregado de fluxos.

---

### 2.4. Riscos de programa e roadmap

**R1 — Estagnação do Épico E28 na v1 de fluxo**  

- Descrição: há risco de o sistema se acomodar na versão inicial de fluxos configuráveis e não avançar para versionamento, approvals, condicionais e métricas, ficando em um meio termo permanente.
- Severidade: média.  
- Probabilidade: média.  
- Mitigação inicial:  
  - registrar E28.2, E28.3 e E28.4 como trilhas explícitas no Capítulo 5 e no ORR;  
  - priorizar pelo menos uma dessas trilhas no planejamento seguinte;  
  - tratar o tema "fluxos configuráveis" como eixo estratégico do Programa 1, não como detalhe cosmético.

**R2 — Desalinhamento entre E28 e sprints de Verdade/Debunker/Comitês (S23–S25)**  

- Descrição: decisões sobre fluxos podem entrar em conflito com decisões de sprints focadas em Truth-DB, Debunker, comitês e governança se esses esforços não conversarem entre si.
- Severidade: alta.  
- Probabilidade: média.  
- Mitigação inicial:  
  - usar os papéis do fluxo (DEBUNKER, DECISION_MAKER, etc.) como pontos formais de integração com os squads Verdade & Interpretação;  
  - garantir que políticas de promoção de verdade e contestação definidas em S23–S25 sejam refletidas nas invariantes de fluxo;  
  - agendar revisões conjuntas periódicas entre os squads responsáveis por E28 e por Verdade/Debunker/Comitês.

**R3 — Proliferação de fluxos "exóticos" sem governança clara**  

- Descrição: com o tempo, pode haver pressão para criar fluxos muito específicos para casos ou usuários particulares, que desviem dos padrões e aumentem a complexidade de manutenção.
- Severidade: média.  
- Probabilidade: média/alta.  
- Mitigação inicial:  
  - definir, em política de produto, critérios para criação de novos fluxos por domínio;  
  - incentivar reutilização de padrões, em vez de customizações únicas;  
  - usar métricas e incidentes como base para justificar fluxos realmente diferenciados.

---

### 2.5. Amarração do Bloco 2

Com este Bloco 2, o Capítulo 6 ganha um **mapa de riscos** claro para a Sprint 29:

- riscos técnicos que podem afetar a evolução do modelo de fluxo e a performance do runtime;  
- riscos de produto e governança ligados a quem mexe em fluxos, impacto em decisões de verdade e expectativas sobre a v1;  
- riscos operacionais relacionados a fallback, janelas de inconsistência e visibilidade da paisagem de fluxos;  
- riscos de programa que podem comprometer a evolução saudável do Épico E28 e sua integração com Verdade/Debunker/Comitês.

Nos blocos seguintes do Capítulo 6, estes riscos serão conectados a:

- uma lista de **débitos técnicos** conscientemente assumidos na S29;  
- um **plano de mitigação e follow-up** (curto e médio prazo);  
- critérios de **monitoramento pós-sprint, rollback e expansão de escopo**;  
- e ao **long tail** da S29, garantindo que nada disso se perca quando o foco migrar para E28.2, E28.3, E28.4 e S23–S25.