# Inspectah — Sprint 31 (E28-S3)
## Capítulo 1 — Bloco 4: Riscos, Fronteiras e Perguntas de Encerramento

### 4.1 Riscos estratégicos da Sprint 31

Risco 1 — Provider-first virar “mais uma camada”, não o eixo central
O maior risco não é o código quebrar, é o provider-first virar só mais um flavor de ingestão pendurado ao lado de scrapers e fontes diretas. Se, ao final da sprint, operadores, POs e squads ainda enxergarem “providers” como um módulo separado em vez de como o caminho padrão de entrada de notícias e social, a arquitetura segue esquizofrênica. Isso se manifesta quando aumentar cobertura continua significando “cadastrar novos sites” em vez de “criar novos perfis de ingestão em cima de providers existentes”.

Risco 2 — Complexidade invisível para o operador
Há um risco real de esconder a complexidade no código e jogar uma interface confusa na mão do operador. Se a tela de Providers e Perfis virar um painel de configurações crípticas (mil flags, filtros mal explicados, nomes obscuros de profile), o time de operação volta para o modelo mental antigo: pede para alguém “de infra” mexer no YAML, ou aceita uma configuração subótima por medo de tocar em algo que não entende. A Sprint 31 precisa tomar cuidado para que provider-first simplifique a vida de quem opera, não o contrário.

Risco 3 — Custos e quotas continuarem só na teoria
Outro risco é a sprint conectar providers, criar perfis, rodar ingestão, mas não colocar custo e quotas como cidadãos de verdade. Se o sistema conseguir rodar BR + Latam + mais um pedaço de EUA/UE sem nenhum freio programático, o projeto volta para o modo “só vamos descobrir quanto custou quando chegar a fatura”. A S31 pode até entregar a parte funcional e, mesmo assim, falhar do ponto de vista de produto se não deixar mecanismos mínimos de proteção: envelopes por perfil, métricas e alertas básicos.

Risco 4 — Legado ganhar outro ano de vida por indecisão
Sem um framing claro de convivência e migração, o legado vira dívida eterna. O risco aqui é a equipe ter receio de mexer em fontes diretas e scrapers, e a S31 terminar como “implementamos providers, mas ninguém tem coragem de depender deles de verdade”. Esse é o tipo de risco que não explode imediatamente, mas corrói todas as futuras sprints de ingestão e deixa Programas 2–4 em uma zona cinzenta constante.

Risco 5 — Domínio piloto mal escolhido ou mal cuidado
Se o domínio piloto for mal definido (por exemplo, um tema de baixo valor para o Inspectah) ou mal cuidado (sem dados suficientes, sem atenção da equipe), a S31 pode chegar ao fim “verde” em termos de tasks, mas não responder a pergunta que interessa: provider-first funciona mesmo nos domínios que importam? A sprint precisa de um piloto que doa se der errado, para que o aprendizado seja real.

### 4.2 Fronteiras explícitas da Sprint 31

A Sprint 31 não é a sprint que resolve o mundo inteiro. Ela traça algumas fronteiras deliberadas, para que o foco não se dissolva:

Primeiro, a fronteira de escopo funcional. S31 mexe em modelo de dados de Provider, Source, ContentItem; cria perfis de ingestão; integra pelo menos um news_provider e um social_provider reais; coloca jobs de ingestão na fila; adapta o Console de Fontes; pluga métricas e logs básicos. Ela não redesenha Truth-DB, Sistema de Blocos, Contestação, Cockpits finais ou Fact Cards. O objetivo é deixar essas camadas futuras com uma base de ingestão sólida, não reescrevê-las agora.

Segundo, a fronteira de cobertura. A sprint não tenta ligar todos os países, idiomas e temas. Ela escolhe poucos perfis de alto valor (política e economia BR/PT, talvez um piloto Latam ES ou EUA/UE EN, mais um perfil social relevante) e faz esses perfis funcionarem muito bem. Se o sistema não aguentar nem esse recorte, está melhor descobrir isso aqui do que com o planeta inteiro plugado.

Terceiro, a fronteira de migração. O legado não morre na S31. O que a sprint faz é classificar fontes diretas e scrapers em três caixas mentais claras: coisas que já podem ser migradas para providers; coisas que ainda precisam ficar de pé (por exemplo, dados oficiais específicos); e coisas que estão marcadas para aposentadoria em sprints seguintes. Essa lista não precisa estar 100% implementada, mas precisa existir e ser consensual.

### 4.3 Dependências críticas para a S31 não virar papel

Algumas condições precisam estar mínimamente presentes para a Sprint 31 não virar apenas uma especificação bonita:

– Pelo menos um news_provider real escolhido e com contrato de uso claro o suficiente para rodar piloto (limites de chamadas, geografia, temas principais).
– Pelo menos um social_provider ou stack de social listening definida para o recorte social piloto, com acesso operacional viável.
– Time de backend com disponibilidade para tocar migrations e jobs de ingestão sem paralisar outras frentes essenciais.
– Time de frontend com espaço para evoluir o Console de Fontes de forma coerente, em vez de apenas “gambiarra de tela nova” jogada ao lado das antigas.
– Alinhamento explícito com os responsáveis pelos Programas 2 e 3 sobre quais perfis vão alimentar quais pipelines de interpretação e Truth-DB nos pilotos.

Se qualquer uma dessas dependências estiver completamente ausente, a S31 vira uma sprint de maquete: até parece certa por fora, mas não aguenta ninguém subindo a escada.

### 4.4 Perguntas que a Sprint 31 precisa conseguir responder

Ao encerrar o Capítulo 1, é útil colocar em forma de perguntas o que o time deve conseguir responder com naturalidade quando a sprint acabar. Se a resposta para qualquer uma dessas perguntas for “depende, deixa eu ver com fulano”, a tese ainda não fechou.

– Quais providers de notícia e social estão plugados hoje, em produção, e que perfis de ingestão cada um deles expõe no Inspectah?
– Para o domínio piloto (por exemplo, política e economia BR), quais perfis de ingestão estão ligados, quais veículos eles cobrem de forma efetiva e com que frequência?
– Se eu pegar uma notícia específica que entrou no sistema hoje, consigo dizer por qual perfil e provider ela entrou, e quais seriam as rotas alternativas possíveis?
– Consigo ver, em uma visão consolidada, quantas chamadas e quantos itens cada perfil gerou nesta semana, e qual é o meu envelope de budget configurado para esse perfil?
– Sei quais fontes diretas e scrapers ainda são críticas e por quê, e tenho um plano explícito para migrá-las ou aposentá-las em sprints futuras?
– Consigo apontar, para quem cuida de Programas 2–3–4, quais perfis alimentam os casos pilotos desses programas, sem recorrer a “conhecimento oral”?

Se a S31 entregar respostas claras para essas perguntas, mesmo que os recortes ainda sejam pequenos, o Capítulo 1 pode ser encerrado com a sensação de que o risco estrutural de ingestão está caindo, e que a expansão para Latam, EUA, UE e outros domínios deixou de ser sonho de slide e passou a ser uma questão de multiplicar perfis e budgets sobre uma fundação que se comporta bem.

