# Sprint 29 — Capítulo 1
## Bloco 1 — Contexto geral do Inspectah e posição da S29 no Programa 1

O Inspectah nasceu como um projeto de **ingestão e organização de informação em larga escala**, com uma ambição clara: não ser apenas mais um coletor de dados, mas evoluir para um **motor de verdade** — capaz de receber notícias, dados oficiais, documentos e sinais diversos, tratá‑los com rigor e, ao final, produzir um estado coerente do mundo, auditável e resistente a manipulações.

As sprints iniciais construíram as fundações técnicas do sistema: pipelines de ingestão, modelos básicos de dados, interfaces mínimas para administração e um esqueleto para evidências e scorecards. Aos poucos, o projeto deixou de ser um conjunto de scripts e passou a se organizar como um produto com:

- **Console de Fontes** (S21), onde o operador cadastra, categoriza e monitora as fontes de informação;
- **Ingestão 2.0** (S22), que transforma a coleta de dados em um fluxo mais previsível, observável e padronizado;
- **Camadas de agentes, debunkers e comitês** (S23–S25), que definem o “quem faz o quê” na análise, verificação e promoção de itens a fato/verdade;
- **Admin e design system mais robustos** (S26), preparando o terreno para consoles mais ricos, consistentes e escaláveis.

Com essas peças no lugar, o projeto entra em uma nova fase: **não basta ter agentes inteligentes e pipelines sofisticados; é preciso governar o comportamento desses agentes como parte do produto**. Essa mudança de mentalidade é o ponto de partida do **Programa 1**, que organiza a evolução do Inspectah em épicos que tratam de:

- transformar decisões internas de código em **configuração explícita**, operável e auditável;
- expor alavancas para produto/ops intervirem em tempo real, sem depender de ciclos completos de desenvolvimento e deploy;
- construir a base para uma governança séria sobre como o sistema interpreta, julga e decide sobre o mundo.

Dentro desse programa, o **Épico E28 — Fluxo de Agentes Configurável v1** ocupa uma posição estratégica: ele é o elo entre o que já foi desenhado nas sprints de agentes (S23–S25) e a capacidade prática de **ajustar o cérebro do sistema por domínio**, sem tocar em código. Até aqui, a maior parte das decisões sobre ordem de agentes, papéis envolvidos e sequência de análise estava embutida em:

- dicionários e enums espalhados pelo código;
- condicionais ad hoc que determinavam qual agente entra em cena em qual etapa;
- convenções implícitas conhecidas apenas por quem escreveu os módulos originais.

Essa abordagem até funciona em um laboratório, mas não se sustenta em um produto que precisa:

- responder rapidamente a eventos do mundo (eleições, crises sanitárias, desinformação coordenada);
- ser auditável por terceiros (parceiros, órgãos reguladores, comunidade);
- manter coerência quando novos domínios, fontes e políticas de verdade forem sendo adicionados.

A **Sprint 29** é o momento em que o E28 deixa de ser um slide em um roadmap e passa a existir como **infraestrutura concreta**. Ela posiciona a S29 como a sprint que:

1. **Abre o Épico E28** com entregas tangíveis: modelos, APIs, UI mínima e integração com o runtime.
2. Conecta diretamente o que foi construído em S21–S26 com a visão de um **fluxo de agentes configurável por domínio**, em vez de codificado.
3. Dá ao Inspectah sua **primeira alavanca real de controle sobre o fluxo de agentes**, ainda que em versão v1, linear e deliberadamente simples.

Na prática, isso significa que, ao final da S29, o projeto deve ter respondido a perguntas como:

- “Onde eu vejo, em uma única tela, qual é o fluxo de agentes que trata notícias de política no Brasil?”
- “Como eu mudo a ordem dos passos analíticos para um domínio específico, sem abrir o editor de código?”
- “Como eu registro que endureci o fluxo de agentes de um domínio durante um período sensível, com justificativa clara?”

Ao posicionar a Sprint 29 nesse contexto, o Programa 1 ganha um degrau bem definido: depois de construir fontes, ingestão, agentes e admin, o time passa a tratar o **fluxo em si** — a coreografia entre esses agentes — como um **objeto de primeira classe** do produto. A partir daqui, as discussões deixam de ser “como está o código de tal pipeline?” e passam a ser “como está o fluxo de agentes deste domínio, e por que ele foi desenhado assim?”.

Esse é o pano de fundo do Bloco 1 do Capítulo 1: explicar onde o Inspectah está, para onde o Programa 1 quer levá‑lo, e por que a Sprint 29 é o ponto exato em que o fluxo de agentes deixa de ser detalhe interno e passa a ser parte explícita da linguagem de produto, de operação e de governança da plataforma.

