# Sprint 24 — Capítulo 1
## Contexto, Problemas a Resolver e Enquadramento Geral

### 1.1 Contexto ampliado e “porquê agora”

A Sprint 24 acontece logo após a consolidação de três camadas críticas do Inspectah:

1. O console de fontes e o pipeline de ingestão 2.0 (S21–S22), capazes de trazer notícias, dados oficiais e outras fontes para dentro do sistema de forma estruturada, versionada e monitorável.
2. A camada de interpretação e classificação por comitês de agentes (S23), que transforma conteúdo bruto em claims, decisões de comitê, níveis de incerteza e sinais de risco.
3. A linha do tempo e o XRay (S19–S20), que permitem navegar casos e eventos de forma visual, enxergando o que aconteceu, quando, com qual evidência e com qual estado atual.

Tudo isso, porém, ainda opera sem um “sistema imunológico” explícito: não existe hoje um lugar único, estruturado e governado onde dúvidas sérias, divergências de interpretação e sinais de alerta sejam reunidos, priorizados, analisados por humanos e resolvidos com trilha de auditoria. Em outras palavras, o Inspectah enxerga problemas, mas ainda não tem um Debunker formal que responda: “ok, quem vai cuidar disso, como, com qual prioridade e qual foi a decisão final?”.

É exatamente esse buraco que a Sprint 24 vem preencher.

Nesta sprint, o objetivo central é criar o Debunker v0 com humano-no-loop: um sistema completo, porém enxuto, que conecta saídas da S23 (decisões de comitês, incertezas, divergências) a uma esteira de revisão humana, com estados claros, UI dedicada, critérios de priorização e registro formal das decisões. O foco não é ter a política definitiva de verdade (isso é S25), nem a infraestrutura on-chain (isso é Fase 2), mas garantir que qualquer claim “problemático” encontre um caminho estruturado até um analista humano, e que a decisão desse analista volte para o Inspectah como dado de primeira classe.

Porquê agora:

- O sistema já consegue ingerir, interpretar e exibir informações; sem um Debunker formal, o risco de acumular falsos positivos, falsos negativos e ambiguidades cresce rapidamente.
- A S25, que trata de Governança de Verdade e Truth-DB, depende de ter um fluxo minimamente funcional de contestação interna para definir políticas de promoção/rebaixamento com base em dados reais de disputa.
- A credibilidade do Inspectah como “oráculo de fatos” precisa de um mecanismo claro de dizer: “isso está em contestação, foi revisado, foi rebaixado, foi confirmado”. A Sprint 24 é a fundação operacional desse mecanismo.

### 1.2 Personas, partes interessadas e dores atuais

Principais personas diretamente impactadas pela Sprint 24:

1. Analista de Verdade (Debunker interno)
   - Responsável por revisar DebunkIssues, analisar evidências, ler o histórico dos comitês e decidir se um claim deve ser mantido, contestado, rebaixado, marcado como duvidoso ou encaminhado para investigação adicional.
   - Dores atuais:
     - Não existe hoje uma fila clara de “coisas que precisam de revisão humana”.
     - Sinais de divergência dos comitês ficam espalhados entre logs, métricas e registros técnicos, sem uma visão única e priorizada.
     - Não há uma UI adaptada ao trabalho de debunking: timeline, evidências, decisões anteriores e contexto de caso ficam fragmentados.

2. Líder de Análise / Coordenador de Operações de Verdade
   - Responsável por garantir que o estoque de DebunkIssues está sob controle, que filas não explodem, que casos realmente importantes não ficam esquecidos e que o processo é previsível.
   - Dores atuais:
     - Nenhuma visão agregada de quantas decisões estão pendentes, há quanto tempo, por tipo de claim ou por tema.
     - Não existem métricas operacionais simples (SLA de revisão, idade média de issues, proporção de issues críticas resolvidas) para gerir a operação.
     - Não há um lugar único para entender o impacto das decisões de debunking nas timelines e nos casos.

3. Squad Verdade & Interpretação (Pearl, Stonebraker, Norvig, Percy e time)
   - Responsáveis por desenhar o modelo conceitual, o Truth-DB, as consultas e os comitês de agentes.
   - Dores atuais:
     - Faltam dados reais sobre onde os comitês mais erram, divergem ou geram incerteza alta.
     - Não existe ainda um loop fechado entre “decisão do comitê” → “revisão humana” → “ajuste de política ou parâmetros dos comitês”.
     - Sem o Debunker v0, a S25 corre o risco de se basear em teoria demais e prática de menos.

4. Usuário final do Inspectah (indireto nesta sprint)
   - Não interage diretamente com o Debunker v0, mas é impactado pela qualidade dos estados de verdade que aparecem em timelines, XRay e consultas.
   - Dores atuais:
     - Pode receber respostas com alto nível de incerteza sem ver claramente que aquilo está “em disputa”.
     - Não há um canal claro, ainda que interno, para tratar temas muito sensíveis com maior rigor.

5. Operações / DevOps / Observabilidade
   - Cuidam para que os pipelines rodem 24/7 com monitoramento, alertas e registro de tudo que acontece.
   - Dores atuais:
     - Não existe ainda uma métrica específica para saúde da fila de debunking (visto que ela ainda não existe).
     - Qualquer tentativa de entender “onde o sistema está mais inseguro” precisa ser reconstruída de logs ou consultas ad hoc.

### 1.3 Mapa de problemas, hipóteses e perguntas orientadoras

Problema central

O Inspectah já enxerga divergência, incerteza e risco, mas não possui um “sistema imunológico” operacional para tratar esses sinais com revisão humana estruturada, priorização, estados claros e trilha de auditoria. Isso ameaça diretamente a credibilidade do sistema como fonte de verdade e impede que a futura Governança de Verdade (S25) se apoie em dados concretos de contestação.

Subproblemas principais

1. Falta de modelo explícito para DebunkIssue
   - Hoje não há uma entidade ou modelo formal que represente “um caso de contestação a ser tratado por um analista”.
   - Não existem estados estáveis para a jornada dessa issue (ex.: NEW, TRIAGED, IN_REVIEW, RESOLVED, ESCALATED, CLOSED_WITH_DOUBT).
   - Não há ligação canônica entre uma DebunkIssue e os artefatos que ela precisa agrupar: claims, CommitteeDecisions, evidências, snapshots de timelines, logs de ingestão, etc.

2. Ausência de mecanismo de detecção e priorização
   - As regras para criar uma DebunkIssue ainda não foram implementadas: divergência forte entre agentes, incerteza alta em temas sensíveis, impacto alto, etc.
   - Não existe uma fila ordenada com critérios claros (risco, impacto, idade, tema) para o analista trabalhar.
   - Sem priorização, o esforço humano pode ser gasto em casos pouco relevantes enquanto temas críticos ficam esquecidos.

3. Falta de UI e fluxo de trabalho para o analista humano
   - Inexistência de uma tela única que combine visão de caso/timeline, claim central, evidências, decisões de comitês e histórico da issue.
   - Não há um fluxo de trabalho desenhado para o analista (ler, marcar pontos críticos, registrar decisão, justificar, anexar comentários ou links externos).
   - Falta ergonomia para decisões rápidas em volume, sem sacrificar explicabilidade.

4. Ausência de trilha de auditoria consolidada
   - As decisões humanas não são hoje primeiros cidadãos no modelo de dados: não há um TruthChangeEvent ou DebunkDecision bem definido e armazenado de forma audível.
   - Não é simples responder perguntas como “quem tomou essa decisão?”, “quando?”, “com base em quais evidências?”
   - Sem trilha consolidada, é difícil revisitar decisões passadas, corrigir erros ou auditar o processo.

5. Lacuna entre contestação e estados de verdade
   - Mesmo que o analista decida algo hoje, não existe ainda um caminho claro para como essa decisão influencia o estado de verdade do claim no Truth-DB (isso é tema principal da S25).
   - Sem esse acoplamento cuidadoso, o sistema corre o risco de acumular decisões humanas “no vazio”, sem impacto visível na experiência do usuário e nas respostas do Inspectah.

Hipóteses orientadoras de design

1. Uma entidade DebunkIssue bem modelada, com estados claros e ligação forte aos artefatos certos, é suficiente para dar forma operacional ao Debunker v0 sem precisar antecipar todas as regras complexas da S25.
2. Regras simples, porém bem escolhidas (divergência de comitê, incerteza alta, impacto alto, temas sensíveis), já são suficientes para gerar um conjunto de issues com boa relação sinal/ruído.
3. Uma UI focada no trabalho diário do analista, com timeline + claim + evidências + decisão em uma única tela, reduz drasticamente o tempo de revisão sem comprometer a qualidade.
4. Registrar cada decisão humana como um evento de verdade (mesmo que ainda não promova automaticamente estados de Truth-DB) cria a base necessária para que a S25 implemente políticas de promoção/rebaixamento realmente baseadas em dados.
5. Métricas simples (idade média de issues, backlog por tema, proporção de issues fechadas com dúvida, taxa de reversão posterior) serão suficientes, neste momento, para guiar ajustes de regras, políticas de comitê e futuras iterações de Debunker.

Perguntas orientadoras da Sprint 24

1. Qual é o modelo mínimo, mas robusto, de DebunkIssue que permite representar qualquer tipo de contestação relevante para o Inspectah?
2. Quais sinais da S23 (e eventualmente de outras partes do sistema) são fortes o suficiente para acionar automaticamente a criação de uma issue, sem explodir o backlog?
3. Como desenhar uma UI de debunking que permita revisão profunda quando necessário, mas também decisões rápidas em casos triviais?
4. Que campos, comentários e justificativas devem ser obrigatórios em uma decisão humana para que ela seja realmente audível e útil para futuras políticas de verdade?
5. Quais métricas operacionais e de qualidade devem ser coletadas desde o v0 para alimentar a S25 e as próximas iterações do Debunker?
6. Como garantir que o Debunker v0 fique estritamente limitado ao contexto interno (analistas e time), sem ainda abrir contestação pública ou mecanismos sociais complexos?

### 1.4 Escopo, anti-escopo e critérios de sucesso de negócio

Escopo da Sprint 24

1. Definir e implementar o modelo de DebunkIssue e seus estados principais, incluindo associação clara a:
   - claims e CommitteeDecisions gerados na S23,
   - casos/timelines e entidades relevantes,
   - evidências e artefatos necessários para análise (links, anexos, referências internas).

2. Implementar um mecanismo inicial de detecção automática de issues, com regras configuráveis, capaz de:
   - criar issues a partir de divergência de comitê, alta incerteza ou impacto alto,
   - evitar duplicações óbvias para o mesmo claim/caso,
   - produzir uma fila priorizada por risco/impacto/idade.

3. Entregar uma UI dedicada para analistas internos, que permita:
   - visualizar a fila de DebunkIssues com filtros por tema, estado, prioridade, idade;
   - abrir uma issue em modo detalhado (timeline, claim central, evidências, decisões de comitê, histórico da própria issue);
   - registrar uma decisão humana com justificativa, comentários e, quando necessário, marcações especiais (ex.: ainda em dúvida, precisa de mais evidência, etc.).

4. Registrar decisões humanas como eventos rastreáveis, com trilha de auditoria mínima:
   - quem decidiu, quando, com qual resultado e em qual contexto de dados;
   - guardar essas decisões em estrutura compatível com o futuro Truth-DB da S25.

5. Instrumentar métricas e logs básicos da operação do Debunker v0:
   - contagem de issues por estado, tema e prioridade;
   - idade média de issues abertas;
   - tempo médio até primeira decisão;
   - distribuição de resultados (confirmado, rebaixado, mantido em dúvida, etc.).

Anti-escopo explícito (o que NÃO entra na S24)

1. Políticas definitivas de verdade/fato, estados finais do Truth-DB e lógica de promoção/rebaixamento de claims — isso é responsabilidade da S25.
2. Qualquer tipo de contestação pública, reputação de usuários finais ou mecanismos sociais avançados.
3. Integração com blockchain, Sistema de Blocos on-chain ou mecanismos de ancoragem externa; a S24 deve apenas produzir dados que possam ser ancorados futuramente.
4. Regras complexas baseadas em machine learning adicional para detecção de issues; o foco aqui são regras declarativas e configuráveis, com alta transparência.
5. Automatismos agressivos que mudem estados de verdade sem revisão humana; todo impacto relevante deve continuar mediado por humanos nesta sprint.

Critérios de sucesso de negócio (visto pelo PO e pelo Squad Verdade & Interpretação)

1. Qualquer claim marcado como problemático pelos comitês (divergente, altamente incerto ou de alto impacto) passa a ter um caminho claro até um analista humano, com fila visível, priorizada e operável.
2. Analistas conseguem, na prática, revisar issues usando apenas a UI do Debunker v0, sem depender de consultas manuais, scripts paralelos ou coleta manual de evidências.
3. Cada decisão humana relevante gera um registro audível e estruturado, que pode ser consultado posteriormente por caso, por claim, por tema ou por analista.
4. O sistema passa a ter métricas básicas, porém confiáveis, sobre o “estoque de incerteza” e o ritmo de resolução de issues, permitindo que S25 e sprints futuras tomem decisões informadas.
5. A entrega de S24 reduz o risco de a Governança de Verdade (S25) ser desenhada apenas em cima de teoria: haverá dados concretos de contestação, decisões e dificuldades reais dos analistas trabalhando em cima de claims ambíguos.

Este Capítulo 1 estabelece, portanto, o enquadramento estratégico da Sprint 24: o Debunker v0 não é um adendo opcional, mas o órgão vital que transforma sinais de incerteza em decisões humanas rastreáveis. Os capítulos seguintes detalharão as métricas de validação (Capítulo 2), a arquitetura e o filemap (Capítulo 3), o plano de execução (Capítulo 4) e os desdobramentos específicos para UI, pipelines e Truth-DB (Capítulos 5 e 6).

