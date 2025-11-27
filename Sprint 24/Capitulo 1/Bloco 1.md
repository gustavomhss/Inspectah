Sprint 24 – Capítulo 1.1
Contexto e objetivos gerais de Verdade (Debunker v0 & Humano-no-Loop)

Este subcapítulo define, de forma rigorosa, o papel da Sprint 24 dentro da camada de Verdade do Inspectah. Aqui não estamos falando apenas de “mais um módulo”, mas do ponto em que o sistema assume explicitamente que toda informação relevante pode ser contestada, revisada e eventualmente revertida. A S24 é o lugar onde a desconfiança vira objeto de domínio, com nomes, estados, regras e responsabilidades claras.

1. Posição da Sprint 24 no ecossistema de Verdade

Para entender o que a S24 precisa fazer, é importante enxergar o ecossistema como uma cadeia contínua.

Primeiro bloco, ingestão e fontes. S21 e S22 garantem que o Inspectah saiba de onde as coisas vêm, como entram e com qual qualidade. As fontes são cadastradas, tipadas, monitoradas. A ingestão 2.0 transforma “um monte de dados entrando” em ContentItems, IngestionRuns, estatísticas e painéis que mostram o que está saudável e o que está falhando. Nada chega “do nada”: sempre existe uma origem rastreável.

Segundo bloco, interpretação multiagente. S23 recebe esse conteúdo e o transforma em algo que o sistema consegue raciocinar: claims, entidades, relações, temas, níveis de confiança, incerteza, divergência entre agentes. Cada item ingerido ganha uma visão de comitê. Não existe mais “um único modelo dizendo algo”, mas um conjunto de agentes, com papéis e perspectivas diferentes, produzindo uma CommitteeDecision com labels, scores e explicações.

Terceiro bloco, contestação humana estruturada. A S24 entra exatamente aqui. Ela olha para o que S23 produziu e responde a uma pergunta simples e brutal: o que, dentre tudo isso, é arriscado demais para ser aceito sem uma revisão humana explícita? O resultado dessa pergunta não é uma sensação, é um conjunto de objetos formais: DebunkIssues, DebunkDecisions, evidências adicionais, racionales e estados claros de revisão.

Quarto bloco, verdade estável e governança. A S25, mais à frente, só vai promover algo para estados como ESTABLISHED_FACT se, além da ingestão consistente (S21–S22) e da interpretação coerente do comitê (S23), existir um histórico de contestação saudável na S24: ou porque não houve nada a contestar segundo as políticas definidas, ou porque houve contestação e ela foi resolvida de forma explícita, com decisão humana registrada.

Assim, a Sprint 24 é a ponte entre “coisas que parecem verdade” e “coisas que o Inspectah trata como verdade estável”. Tudo que passar desse ponto sem um olhar humano adequado estará violando, por definição, o espírito de Verdade do sistema.

2. Relação detalhada da S24 com S21–S23, S19–S20 e S25

Com ingestão (S21–S22), a relação é de rastreabilidade e contexto. Toda DebunkIssue precisa ser capaz de responder, de forma direta: de quais fontes e quais ContentItems isso veio? Qual IngestionRun colocou isso dentro do sistema? Qual a saúde dessa fonte naquele período? Houve falhas recentes naquele canal? A S24 não existe no vácuo: cada caso contestado precisa puxar, como rastro, a história da ingestão que o colocou ali.

Com interpretação (S23), a relação é de gatilho e critério. Quem decide que algo é um candidato a contestação é uma combinação de regras de negócio, métricas de incerteza e sinais do comitê de agentes. Exemplos de critérios típicos: divergência forte entre agentes sobre o mesmo claim, nível de confiança abaixo de um limiar para temas sensíveis, presença de entidades de alto impacto (governos, autoridades, empresas sistêmicas) combinada com incerteza, conflito direto com fatos já estabelecidos em outras partes do sistema. A S24 consome CommitteeDecisions, labels e explicações e os converte em “motivos formalizados de desconfiança”.

Com UI de timeline e raio-x (S19–S20), a relação é de explicação visual. Quando alguém abre a timeline de um caso, não pode ver apenas uma sequência de eventos como se tudo fosse neutro. A presença de DebunkIssues, estados de contestação, decisões humanas e mudanças de entendimento precisa aparecer como parte da narrativa daquele caso: aqui o sistema passou a duvidar, aqui alguém revisou, aqui a decisão mudou, aqui um claim deixou de ser confiável. A S24 fornece os objetos que a UI precisa para contar essa história de forma honesta e inteligível.

Com governança de Verdade (S25), a relação é de pré-requisito. As políticas de promoção e rebaixamento de estados de verdade só podem operar com segurança se souberem, para cada claim e para cada caso, se existe contestação em aberto, se já houve revisão humana, qual foi a decisão, com quais evidências e em qual data. A S24 precisa modelar esses elementos como primeira classe: sem isso, a S25 ou se torna cega, ou precisa improvisar em cima de logs soltos, o que é inaceitável em um sistema que se propõe a ser auditable-by-design.

3. Princípios de Verdade que a S24 precisa cristalizar

A equipe inteira converge em alguns princípios que a S24 não pode ignorar.

Primeiro princípio, verdade é sempre contextual, datada e revisável. Nenhuma DebunkDecision vale por si só fora do contexto: qual era o conjunto de evidências no momento da decisão, quais políticas estavam ativas, quais interpretações a S23 havia produzido, quais fontes eram consideradas saudáveis. O papel da S24 é registrar esse contexto de maneira que, no futuro, uma pessoa consiga reconstruir a linha de raciocínio e decidir se aquilo ainda faz sentido.

Segundo princípio, a redundância tripla não é detalhe, é filosofia. A visão-alvo da S25 é clara: promoção a fato estável só acontece quando três pilares estão alinhados. Um, múltiplas fontes independentes e saudáveis apontando na mesma direção. Dois, comitê de agentes produzindo interpretação coerente e não conflitiva. Três, pelo menos uma decisão humana bem documentada na S24, sem DebunkIssues críticas em aberto e com rationale mínimo aceitável. A S24 é o lugar onde esse terceiro pilar ganha forma.

Terceiro princípio, modelos ajudam, humanos decidem. Na S24, agentes GPT podem listar inconsistências, sugerir hipóteses, organizar evidências, apontar trechos suspeitos e até sugerir decisões preliminares. Mas a assinatura final é de uma pessoa. Isso precisa ficar claro no modelo de dados, na UI e na forma como o sistema responde perguntas: recomendações de IA nunca podem ser confundidas com decisões humanas.

Quarto princípio, auditabilidade pesa mais que conveniência. Se um fluxo de contestação é “rápido” mas não deixa rastro suficiente para reconstruir o que aconteceu, ele está errado. Cada DebunkIssue e cada DebunkDecision precisa ser localizável, legível e acompanhada de metadados suficientes: quem, quando, por que, com base em quais evidências e em qual estado do sistema. A S24 é o lugar onde sacrificamos um pouco de conforto em nome de rastreabilidade.

Quinto princípio, contestação é backlog de risco, não caixa de entrada caótica. A S24 precisa tratar contestação como um backlog vivo, com estados, prioridade e métricas. Quantas DebunkIssues estão abertas? Quantas são críticas? Há quantas semanas existe uma disputa sem decisão? Quantas decisões foram revertidas nos últimos meses? Sem esse tipo de visibilidade, a contestação vira um buraco negro.

4. Objetivos gerais da Sprint 24 para a camada de Verdade

A partir desses princípios e das dependências com outras sprints, o Squad Verdade & Interpretação define quatro objetivos gerais para a S24.

Primeiro objetivo, transformar desconfiança em entidade de domínio. Ao final da sprint, “tem algo estranho aqui” deixa de ser uma frase solta e passa a ser um objeto concreto: DebunkIssue, com identificador, ligação explícita a casos e claims, motivo de abertura, origem do gatilho (regra automática, analista, comitê de agentes), estado, prioridade e histórico de alterações.

Segundo objetivo, criar um fluxo operacional saudável de revisão humana. Analistas precisam conseguir entrar no sistema, ver rapidamente quais casos exigem atenção, filtrar por criticidade, entender de cara por que algo entrou na fila, inspecionar evidências e interpretações, registrar uma decisão e seguir adiante. Não pode exigir navegação labiríntica nem depender de conhecimento tribal. O fluxo de trabalho precisa ser simples o suficiente para ser adotado, mas estruturado o bastante para ser auditável.

Terceiro objetivo, preparar a S25 para focar apenas em máquina de estados de verdade. A S25 deve poder assumir que contestação já está resolvida em termos de modelo de dados, entidades, relacionamento com casos e claims e fluxo básico de trabalho. Isso significa que a S24 precisa sair com uma estrutura estável de DebunkIssue, DebunkDecision, links para evidências e ligações com o ecossistema de ingestão, interpretação e timeline. A S25 então pode se concentrar em definir estados de verdade, regras declarativas de promoção e rebaixamento e registro de TruthChangeEvents sem precisar reinventar a base de contestação.

Quarto objetivo, elevar o padrão de explicabilidade da camada de Verdade. Depois da S24, perguntas como “por que este claim está em disputa?”, “quem decidiu isso?” e “o que mudou desde a última decisão?” precisam ter respostas sistemáticas, não improvisadas. Parte dessa explicabilidade virá da própria modelagem de entidades e parte virá da integração com timeline e raio-x, mostrando claramente onde a contestação entrou na história do caso.

Quinto objetivo, institucionalizar a ideia de que toda verdade é contestável. A S24 é o músculo que permite ao Inspectah sustentar, na prática, o discurso de que verdade é tratada com cautela, revisões e possibilidade de reversão. Ela mostra, no código e no banco de dados, que antes de algo chegar ao status de “fato estável” existe sempre a fase em que aquilo foi apenas um claim, sujeito a contestação, revisão e mudança de entendimento.

Este subcapítulo 1.1 define o contexto e os objetivos gerais da Sprint 24 na camada de Verdade. Os próximos subcapítulos deste Capítulo 1 detalharão a visão de sucesso da S24 em termos de produto, os recortes de escopo para a Fase 1, as dependências explícitas com outras sprints e as fronteiras claras com o que ficará para S25 e fases futuras.