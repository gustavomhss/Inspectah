# Sprint 24 – Capítulo 3.1
## Contexto e problemas de arquitetura (Debunker v0, contestação e camada de verdade)

Este subcapítulo define o contexto e os problemas de arquitetura que a Sprint 24 precisa resolver para que o Debunker v0 e a camada de contestação do Inspectah sejam sólidos, auditáveis e integráveis com o restante do ecossistema (S21–S25). A ideia não é ainda desenhar o filemap ou a execução passo a passo, mas alinhar o "terreno" arquitetural: quais blocos existem, como conversam entre si, que dores históricas queremos evitar e quais decisões são inegociáveis na camada de verdade e contestação.

### 1. Posição da Sprint 24 no ecossistema do Inspectah

A Sprint 24 não nasce no vácuo. Ela assume algumas coisas como já existentes ou em consolidação:

1) S21 e S22: console de fontes e ingestão 2.0 já são capazes de registrar, parametrizar e alimentar o sistema com notícias, dados oficiais, séries temporais e demais insumos. Do ponto de vista da arquitetura, isso significa que já existem entidades mínimas de Source, SourceConfig, IngestionJob, IngestionRun e os conectores que trazem conteúdo bruto.

2) S23: camada de interpretação e classificação já define como o Inspectah transforma conteúdo bruto em claims e estruturas semânticas mais organizadas. Já existem ao menos modelos conceituais de Claim, Entity, Event, TimelineUnit e os comitês de agentes responsáveis por leitura, classificação e agregação de informações.

3) S25 (verdade e governança) depende diretamente da Sprint 24: o Truth-DB só pode promover um claim a ESTABLISHED_FACT ou rebaixá-lo a RETRACTED se a camada de contestação estiver bem definida. A arquitetura de S24 precisa ser compatível com o modelo de estados de verdade desenhado pelo Squad Verdade & Interpretação (Pearl, Stonebraker, Norvig, Percy) e não pode introduzir atalhos que quebrem essa governança.

4) Timelines e XRay (S19 em diante): a camada de visualização já coloca uma dívida implícita na arquitetura. Toda contestação, decisão de Debunker, mudança de estado de verdade e inclusão de evidências precisa ser refletida visualmente em timelines e painéis de XRay de maneira coerente e performática, sem consultas impossíveis ou joins monstruosos.

Em resumo, a Sprint 24 é o eixo entre: ingestão + interpretação (S21–S23) de um lado e governança de verdade + Truth-DB + UI de timelines (S19, S25) do outro. A arquitetura que definirmos aqui precisa ser o encaixe limpo entre esses mundos.

### 2. Visão macro da arquitetura alvo da Sprint 24

A partir desse contexto, a arquitetura de S24 precisa convergir para alguns blocos principais, que serão refinados nos demais subcapítulos:

1) Serviço de Debunker v0. Um serviço claro, com fronteiras bem definidas, responsável por receber casos de contestação, orquestrar revisões por comitês de agentes, coordenar humano-no-loop e emitir decisões estruturadas. Este serviço não é um amontoado de funções soltas; é um componente de primeira classe na arquitetura, com modelo de domínio próprio.

2) Modelo de domínio de contestação. Precisamos de entidades formais como DisputeCase, DisputeContext, DisputeAction, DebunkDecision e DebunkOutcome. Essas entidades devem se conectar de maneira natural ao modelo de Claim/Event/Timeline, sem duplicação desnecessária, com chaves e relações claras.

3) Canal de integração com o Truth-DB. A arquitetura precisa prever como decisões do Debunker fluem para a camada de verdade: quais eventos são emitidos, quais tabelas ou coleções são atualizadas, como garantir que mudanças de estado de verdade sejam sempre motivadas por eventos de contestação rastreáveis.

4) Infraestrutura para humano-no-loop. O Debunker v0 é explicitamente humano-no-loop. Isso significa filas, estados de trabalho (open, in_review, waiting_more_evidence, resolved), mecanismos de atribuição de casos, priorização e trilhas de auditoria de decisões humanas associadas a cada caso.

5) Trilhas de auditoria e logs estruturados. Toda decisão tomada por agentes, comitês ou humanos precisa ser registrável em estruturas auditáveis, que possam ser consultadas depois pela UI, por scripts internos e, futuramente, por processos de governança externa (comunidade, revisores, etc.).

6) Interfaces com outros squads. A arquitetura da Sprint 24 precisa nascer desde o início com fronteiras limpas em relação a:
- Squad de Ingestão e Fontes (como enviar casos de contestação originados de ingestão ou problemas com fontes).
- Squad de Interpretação e Classificação (como consumir claims e gerar casos de contestação a partir de inconsistências entre fontes).
- Squad UI/Timeline/XRay (como expor estados e eventos de contestação de forma eficiente para consultas e visualização).
- Squad de Governança de Verdade (como alinhar estados de contestação com estados de verdade do Truth-DB).

### 3. Problemas de arquitetura que a Sprint 24 precisa resolver

Com esse cenário, a Sprint 24 precisa responder, em nível de arquitetura, a um conjunto de problemas bem concretos. Nos próximos subcapítulos (3.2–3.4) eles serão transformados em gates, filemap e plano de execução, mas aqui o foco é deixá-los cristalinos.

3.1) Como representar contestação sem quebrar o modelo de blocos do Truth-DB.
Hoje já existe um modelo de blocos, timelines e truth records em evolução. O Debunker v0 não pode inventar um universo paralelo de entidades que depois seja impossível de reconciliar. Precisamos de uma modelagem em que uma contestação seja sempre:
- ligada a um claim ou conjunto de claims;
- representada por eventos claros (DisputeOpened, EvidenceAttached, DebunkOpinionIssued, HumanDecisionRecorded, TruthStateUpdated);
- compatível com a estrutura de blocos e sub-blocos, aproveitando o que já foi definido para rastreabilidade.

3.2) Como garantir que todo caminho de decisão seja reproduzível.
Se o sistema receber hoje um conjunto de evidências e agentes e, daqui a seis meses, alguém quiser reconstituir a linha de raciocínio, a arquitetura precisa suportar isso. Não basta guardar "resultado final". Precisamos de:
- estrutura para registrar qual comitê foi acionado, qual configuração de prompts, versões de modelo, thresholds e votos;
- trilha de decisões humanas (quem decidiu, quando, com base em que evidências);
- vínculos claros entre evidências, opiniões de Debunker e mudança de estado na linha do tempo.

3.3) Como isolar e limitar o impacto dos agentes GPT.
Os comitês de agentes não podem ser caixas pretas acopladas diretamente na camada de storage. A arquitetura precisa garantir que:
- agentes só leem dados através de uma camada de orquestração, nunca diretamente das tabelas nucleares;
- agentes só escrevem "propostas" de decisão (opinions, scores, recommended_actions), nunca estados finais;
- toda alteração em Truth-DB ou na timeline passe por um componente determinístico, audível e testável (governance/transition engine), mesmo que tenha sido motivada por um comitê de agentes.

3.4) Como materializar humano-no-loop de forma escalável e simples.
Humano-no-loop não pode ser um hack de UI. A arquitetura precisa contar com:
- filas internas ou estados de workflow para casos em revisão;
- mecanismos para divisão e priorização de trabalho entre revisores humanos;
- forma consistente de registrar a decisão humana como um evento de primeira classe, não apenas como "nota" em um registro.

3.5) Como manter o sistema performático e economicamente viável.
Contestação e Debunker são operações naturalmente pesadas: muitos documentos, múltiplas evidências, consultas cruzadas. A arquitetura precisa equilibrar:
- armazenamento transacional consistente (para não quebrar integridade do Truth-DB);
- caminhos de leitura otimizados para a UI (timelines, histórico de disputas, painéis analíticos);
- estratégias de arquivamento ou compactação de histórico para evitar que a base operacional exploda.

3.6) Como garantir que falhas parciais não corrompam verdades.
Não podemos ter um cenário em que:
- o Debunker registra uma decisão;
- o Truth-DB muda o estado de um claim;
- a timeline não recebe o evento correspondente;
- ou algum desses passos falha no meio e o sistema fica em estado inconsistente.

A arquitetura precisa prever padrões como:
- operações idempotentes;
- escrita em duas fases (prepare + commit) quando necessário;
- eventos de compensação e mecanismos de verificação periódica de consistência entre Debunker, Truth-DB e timelines.

3.7) Como expor todo esse universo de forma consultável e simples para outros squads.
Stonebraker e Norvig vão exigir que a arquitetura suporte consultas como:
- "Liste todas as disputas abertas sobre claims relacionados a este político nas últimas 48 horas";
- "Mostre todos os casos em que um comitê de agentes recomendou X, mas o humano decidiu Y";
- "Mostre todas as timelines que tiveram mudança de estado de verdade causada por uma decisão de Debunker na última semana".

Se a arquitetura não for pensada com isso em mente, S25 ficará preso a consultas ad hoc, improdutivas e frágeis.

### 4. Decisões inegociáveis de arquitetura para a Sprint 24

Com base nas lições aprendidas até aqui (S1–S22, Sistema de Blocos, Truth-DB, timelines) e nas exigências do Squad Verdade & Interpretação, algumas decisões de arquitetura são consideradas inegociáveis para a Sprint 24:

1) Contestação como cidadão de primeira classe. DisputeCase, suas ações e decisões não são "anexos" de claims. Eles são entidades de domínio com vida própria, com IDs, estados, eventos e relacionamentos formais.

2) Nenhuma mudança de estado de verdade sem evento rastreável. Qualquer transição de estado em Truth-DB (por exemplo, PROVISIONAL_FACT → ESTABLISHED_FACT ou ESTABLISHED_FACT → UNDER_DISPUTE) deve estar amarrada a um evento de contestação ou revisão, com referência explícita ao caso e às evidências.

3) Agentes GPT nunca escrevem diretamente no Truth-DB. Eles produzem deliberações, não mutações. Quem aplica mutação é sempre um componente determinístico, seguindo regras estáveis e versionadas, potencialmente sob decisão final humana.

4) Logs estruturados e idempotência como padrão. Chamadas de API, eventos internos, decisões de Debunker e alterações de estado precisam ser logadas de forma estruturada (correlation IDs, timestamps, tipos de evento) e pensadas desde o início para serem reprocessáveis sem duplicar efeitos.

5) Arquitetura preparada para a Fase 2 (blockchain, reputação avançada, sistema de blocos completo), mas sem antecipar implementação. A Sprint 24 deve produzir um desenho que não impeça, no futuro, o ancoramento de decisões em blockchain e a adoção plena do sistema de blocos, mas sem trazer essa complexidade agora para a camada operacional.

### 5. Itens explicitamente fora de escopo de arquitetura para S24

Para manter o foco e a sanidade, a Sprint 24 não tentará resolver tudo de uma vez. Do ponto de vista de arquitetura, ficam explicitamente fora de escopo:

1) Implementação do sistema completo de reputação de usuários, fontes ou revisores. Podem existir ganchos (campos e eventos) para reputação futura, mas o cálculo e uso de reputação não entram como requisito arquitetural obrigatório de S24.

2) Design detalhado de ancoragem em blockchain das decisões de Debunker. O modelo deve ser compatível com o futuro ancoramento, mas os contratos on-chain, formatos de prova e rotinas de publicação pertencem à Fase 2.

3) Consolidação de todas as possíveis interfaces externas (APIs públicas para terceiros consumirem disputas, por exemplo). A prioridade é servir os próprios squads internos (UI, Truth-DB, ingestão, interpretação). APIs públicas ficam como derivadas, não como eixo central de S24.

4) Ferramentas avançadas de analytics em cima de disputas. Dashboards complexos, relatórios avançados e análises históricas profundas podem ser desenhadas como futuro, mas a arquitetura base precisa apenas garantir que os dados necessários estarão disponíveis e bem estruturados.

### 6. Resultado esperado deste subcapítulo

Ao final deste subcapítulo 3.1, o que fica estabelecido é o quadro de referência para os próximos passos de Arquitetura & Filemap na Sprint 24:

1) Entendemos claramente onde a Sprint 24 se encaixa na sequência S21–S25.
2) Sabemos quais blocos arquiteturais precisam existir: serviço de Debunker, modelo de domínio de contestação, canais formais com Truth-DB, infraestrutura para humano-no-loop, trilhas de auditoria e interfaces com outros squads.
3) Listamos, em linguagem concreta, os problemas de arquitetura que precisam ser resolvidos (representação de contestação, reprodutibilidade de decisões, isolamento de agentes, humano-no-loop, performance, consistência, consultas avançadas).
4) Estabelecemos decisões inegociáveis e limites de escopo para que os subcapítulos 3.2 (Gates & DoD), 3.3 (Arquitetura & Filemap detalhado) e 3.4 (Execução e evidências) possam operar com clareza, sem ambiguidade.

Os próximos subcapítulos deste Capítulo 3 vão descer da visão de contexto e problemas para critérios verificáveis (gates), para o desenho concreto de arquivos, módulos e contratos internos e, finalmente, para o plano de execução e evidências necessárias para declarar o Capítulo 3, e portanto a arquitetura da Sprint 24, como verdadeiramente "GO".

