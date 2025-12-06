# Sprint 33 — Capítulo 6

## Bloco 3 — Como a S33 redefine o que é operar o Inspectah

Este bloco aprofunda a seção 6.3, detalhando **como a Sprint 33 muda, na prática, a definição de “operar o Inspectah”**. A ideia é sair da visão tradicional de operação (manter serviços de pé) e cristalizar uma visão em que operar significa, sobretudo, **cuidar da cadeia de verdade**.

---

### 6.3.1 Operar como garantir integridade da cadeia de verdade

Em muitos sistemas, operar significa algo próximo de:

> “garantir que os serviços respondam rápido e fiquem disponíveis”.

No Inspectah, a S33 explicita uma definição ampliada:

> Operar o Inspectah é garantir que a cadeia ingestão → interpretação → contestação → Truth‑DB → exposição se mantenha íntegra, atual, auditável e observável.

Isso implica uma mudança de foco:

- **de** “está respondendo?”  
- **para** “o que está respondendo é um retrato fiel e atualizado do que o sistema deveria saber sobre o mundo?”.

Na prática, essa mudança se materializa em três eixos:

1. **Integridade da cadeia:** se uma etapa da jornada da informação falha (por exemplo, ingestão de uma fonte crítica ou atualização de blocos de verdade), o sistema precisa detectar, sinalizar e permitir ação.

2. **Atualidade da verdade:** não basta que o pipeline esteja “em pé” — é necessário que ele esteja produzindo um estado de verdade condizente com o que se sabe naquele momento.

3. **Auditabilidade do processo:** deve ser possível, olhando para o OracleOps, reconstruir o que aconteceu com a verdade em determinado período (quais fontes estavam saudáveis, quais incidentes afetaram quais casos, que SLOs estavam violados).

A S33 define OracleOps v1 como o mecanismo que torna essa definição operável, e não apenas aspiracional.

---

### 6.3.2 Componentes, SLOs e incidentes como linguagem única de operação

Para que essa visão ampliada funcione, a S33 precisa de uma **linguagem comum** que consiga representar, ao mesmo tempo:

- aspectos técnicos (serviços, filas, bases, APIs);
- aspectos informacionais (fontes, blocos de verdade, casos, contestação).

Essa linguagem é construída em torno de três entidades de domínio:

1. **Componentes (`ops_components`)**  
   Cada componente é uma peça nomeada da jornada de informação: uma fonte, um pipeline, um passo do Truth‑DB, uma API de exposição. Em vez de falar apenas em “serviço X caiu”, a operação passa a falar em “componente Y da cadeia de verdade está comprometido”.

2. **SLOs (`ops_slos`)**  
   SLOs deixam de ser apenas alvos de desempenho e passam a ser guardas da integridade informacional. Ainda que a S33 implemente um subconjunto inicial (focado em recência e saúde de pipelines), a estrutura já comporta SLOs que medem:
   - recência de atualização de fontes;
   - latência para refletir novos dados em casos;
   - tempo de resposta a contestação.

3. **Incidentes (`Incident`)**  
   Incident vira o “átomo” que codifica eventos em que a cadeia de verdade saiu do trilho. Ele é vinculado a componentes e SLOs, de forma que seja possível responder a perguntas como:
   - “quais incidentes afetaram essa fonte?”;
   - “quais incidentes contribuíram para esse caso ficar desatualizado por tanto tempo?”.

Essa tríade permite convergir conversa técnica e conversa epistemológica em um mesmo vocabulário operacional.

---

### 6.3.3 Cockpit como janela para o estado da verdade, não só da infra

O cockpit `oracleops` da S33 não é apenas um painel de CPU/latência. Ele é desenhado para responder, em poucos cliques, a perguntas como:

- “qual é a saúde geral do recorte que a S33 está operando?”;
- “quais componentes críticos estão em risco ou incidentados?”;
- “quais incidentes recentes podem estar afetando a confiança em certas partes da Truth‑DB?”;
- “quais runbooks e SLOs estão relacionados a esse problema?”.

Isso se traduz em escolhas concretas de UX:

1. **Overview orientada à cadeia de verdade**  
   Em vez de listar apenas serviços, a `OverviewPage` mostra componentes agrupados por papel na jornada de informação (fontes, ingestão, interpretação, Truth‑DB, exposição). O operador enxerga o mapa da cadeia, não um conjunto de caixas sem contexto.

2. **Drill‑down que conecta técnica e semântica**  
   Ao entrar num componente específico, o operador vê não só métricas técnicas, mas também sua posição na cadeia de verdade, seus SLOs associados e incidentes recentes.

3. **Visões especiais para incidentes e SLOs**  
   Páginas dedicadas permitem explorar incidentes em detalhe (timeline, vínculos, evidências) e SLOs em risco. Isso garante que problemas informacionais não sejam engolidos por ruído técnico.

Na prática, a S33 redefine “abrir o cockpit” de “ver se serviços estão de pé” para “entender a saúde da verdade naquele recorte do sistema”.

---

### 6.3.4 Runbooks e bundles como memória operacional da verdade

Outra redefinição importante está na forma como a S33 trata o aprendizado operacional:

- **Runbooks** deixam de ser apenas listas de comandos para reiniciar serviços e passam a incluir passos para verificar integridade de dados, recência de casos e consistência de verdade exposta.

- **Bundles de incidentes** (em `out/evidence/S33_G4_incidents/`) funcionam como cápsulas de memória que contam, para cada incidente relevante:
   - o que aconteceu com a infraestrutura;  
   - o que aconteceu com a cadeia de verdade (por exemplo, quais casos, fontes ou blocos foram afetados ou ficaram desatualizados);
   - como o operador navega do sintoma técnico ao impacto epistemológico.

Com isso, a memória operacional deixa de ser puramente técnica e passa a carregar, também, **história da verdade do sistema**.

---

### 6.3.5 ORR como exame prático da capacidade de operar a verdade

A ORR operacional (G5) é, talvez, a expressão mais explícita dessa nova definição de operação.

Em muitos contextos, uma readiness review verifica se:

- serviços sobem;
- alarmes disparam;
- documentação existe.

Na S33, a ORR é desenhada como um **exame prático** para responder a perguntas muito específicas:

- uma pessoa que não desenvolveu a S33 consegue, via cockpit, entender o que o sistema sabe sobre o recorte operado?;
- essa pessoa consegue identificar, sozinha, quando algo na cadeia de verdade está errado ou em risco?;
- ela consegue seguir runbooks e usar bundles para sair de um sintoma até uma ação concreta que melhora a integridade da verdade?;
- os atritos encontrados são aceitáveis para produção ou indicam NO_GO?

A S33 considera que, se a resposta honesta a essas perguntas for “não”, então o sistema **não está operável**, independentemente de quanto código novo foi entregue.

---

### 6.3.6 Síntese: da operação centrada em serviço à operação centrada em verdade

A redefinição proposta pela S33 pode ser resumida assim:

- Antes:  
  Operar = garantir que serviços e pipelines estejam respondendo, com métricas técnicas sob controle.

- Depois da S33:  
  Operar = garantir que a cadeia completa que leva alegações a fatos esteja íntegra, atual, observável e auditável — e que problemas nessa cadeia sejam detectáveis, rastreáveis e tratáveis via cockpit, incidentes, SLOs e runbooks.

Essa mudança de definição é o núcleo do que este Bloco 3 registra. Ela é o referencial pelo qual todas as decisões da S33 (e das sprints seguintes que toquem OracleOps) devem ser julgadas: **estamos realmente operando a verdade do sistema, ou apenas mantendo serviços funcionando?**

