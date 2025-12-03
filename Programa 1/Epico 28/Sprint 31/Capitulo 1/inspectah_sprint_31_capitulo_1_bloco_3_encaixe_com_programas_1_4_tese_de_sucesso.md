# Inspectah — Sprint 31 (E28-S3)
## Capítulo 1 — Bloco 3: Encaixe com Programas 1–4 e Tese de Sucesso

### 3.1 Como a Sprint 31 conversa com os quatro Programas

Programa 1 é o centro de gravidade direto da Sprint 31. A sprint pega o que o Programa 1 descreve como Data Hub, Fontes, Ingestão e Operação 24/7 e torna isso coerente com o modelo provider-first. Em termos práticos, S31 consolida o triângulo Provider → Profile de Ingestão → ContentItem como caminho principal de entrada de notícias e social. É aqui que o Data Hub deixa de ser uma colcha de retalhos de scrapers e endpoints pontuais e passa a se comportar como uma infraestrutura de ingestão organizada por perfis.

Programa 2 depende dessa arrumação para conseguir respirar. Claims, ClaimGraph, Motor de Sinais e os comitês de agentes só funcionam bem se a entrada de conteúdo for minimamente estável, rastreável e configurável. A Sprint 31 garante que, ao falar de um domínio como “política BR” ou “economia BR”, exista um conjunto explícito de perfis de ingestão que define o universo de conteúdo considerado. Isso reduz ruído no ClaimGraph, melhora a qualidade dos sinais e permite que ajustes de ingestão sejam interpretados como experimentos, e não como bugs ou acidentes.

Programa 3 sente o impacto da Sprint 31 na base de evidências que sustenta Truth-DB e Sistema de Blocos. FactBlocks e EvidenceBlocks precisam se apoiar em ContentItems cuja proveniência seja clara. Quando o projeto precisar responder onde essa afirmação apareceu pela primeira vez, quais veículos ecoaram, qual o contexto temporal, a camada provider-first e os perfis de ingestão já precisam estar resolvidos. S31, portanto, é uma pré-condição silenciosa para que o Sistema de Blocos não vire um castelo em cima de dados de origem nebulosa.

Programa 4 é o rosto do produto, e também herda os efeitos da S31. Cockpits de Casos, Fact Cards, painéis de narrativa, Truth API e dashboards só terão credibilidade se, ao abrir um caso ou um fato, for possível ver claramente a cadeia de origem: perfis de ingestão, providers, fontes derivadas, tempos, contextos. A Sprint 31 não constrói as telas finais, mas define o que elas poderão mostrar amanhã. Se a ingestão provider-first for bem feita, o Programa 4 nasce em um mundo onde “como o dado entrou” é uma pergunta trivial, não uma investigação forense.

A S31, portanto, é uma sprint do Programa 1 com efeitos imediatos no Programa 2 e efeitos estruturantes nos Programas 3 e 4.

### 3.2 Hipóteses fortes da Sprint 31

A primeira hipótese forte é que o modelo provider-first é, de fato, o único viável para escalar ingestão de notícias e social em múltiplos países, idiomas e temas sem afundar em complexidade e custo operacional. Se essa hipótese estiver errada, S31 vai expor isso rapidamente, porque ao tentar fazer perfis pilotos de Brasil e mais uma região ficará claro se o modelo facilita ou atrapalha.

A segunda hipótese é que perfis de ingestão são a unidade operacional certa. Em vez de operadores pensarem em “fonte X, fonte Y, fonte Z”, a aposta é que pensar em “perfil Brasil PT política, perfil Latam ES política, perfil global saúde” encaixa melhor na realidade de quem gerencia budget, risco e prioridades editoriais. Se, ao final da sprint, os operadores continuarem preferindo trabalhar diretamente em nível de site e caminho técnico, algo no desenho de perfis ficou errado.

A terceira hipótese é que dá para encaixar providers no ecossistema já existente sem reescrever meio sistema. S31 assume que é possível evoluir modelos, migrations, Console de Fontes, fila e observabilidade de forma incremental, mantendo compatibilidade com fontes diretas e scrapers enquanto a migração acontece. Se, na prática, cada ajuste em provider quebrar meia dúzia de fluxos legados, o projeto vai aprender que precisa de uma estratégia mais radical para matar o legado.

A quarta hipótese é que um domínio piloto bem escolhido (por exemplo, política e economia BR em PT, com um recorte internacional menor) é suficiente para validar arquitetura. Não é necessário cobrir o mundo inteiro para saber se a lógica provider → perfil → ContentItem → ClaimGraph está funcionando. Se mesmo num piloto a experiência for confusa e cara, tentar escalar só vai amplificar o problema.

### 3.3 O que significa sucesso para a Sprint 31

Sucesso na Sprint 31 não é só ter código rodando. Significa que, em um domínio piloto, a história fim a fim ficou simples de explicar. Um operador deve conseguir abrir o Console de Fontes, apontar para um conjunto de perfis de ingestão, mostrar que esses perfis estão ligados a um ou mais providers, acionar ingestão e ver ContentItems canônicos aparecendo com proveniência clara. Em seguida, o time precisa conseguir acompanhar, em painéis, quantos itens estão entrando, quantas chamadas foram feitas ao provider, quanto erro está ocorrendo e se os budgets estão sendo respeitados.

Do lado de Programas 2 e 3, sucesso significa que, ao abrir o ClaimGraph e um caso piloto, é possível rastrear claims e evidências até perfis de ingestão específicos, sem investigação manual. A pergunta “quais perfis estão alimentando esse caso?” precisa ter resposta direta. Quando alguém contestar um fato, a trilha de origem não pode ser um emaranhado de rotas obscuras; deve ser possível reconstruir a linha Provider → Perfil → ContentItem → Claim → FactBlock de forma reprodutível.

Finalmente, sucesso significa que o time se sente seguro para planejar a expansão. Se, ao término da S31, a equipe conseguir dizer com confiança “sabemos o que fazer para adicionar mais três perfis de ingestão, o impacto em custo é previsível, e o risco de quebrar o que já funciona é baixo”, a sprint terá cumprido seu papel. Se, em vez disso, a sensação for de que o sistema ficou ainda mais frágil, a S31 funcionará como alerta antecipado de que a arquitetura precisa de ajustes antes de encarar Latam, EUA, UE e o resto do mundo em escala.

### 3.4 O que seria um fracasso útil

Existe também a noção de fracasso útil. A Sprint 31 será considerada um fracasso útil se, mesmo com esforço de implementação, ficar claro que algum pilar da hipótese provider-first está mal posicionado nesta fase do produto. Por exemplo, se ficar evidente que o tipo de provider escolhido não se encaixa bem nos contratos que o Inspectah precisa, ou que a granularidade dos perfis precisa ser revista, ou ainda que certos domínios exigem um caminho alternativo.

Nesse cenário, S31 ainda entrega valor: ela traz dados duros e aprendizados para recalibrar o roadmap, ajustar Programas 1–4 e, se necessário, redesenhar a forma como providers se encaixam no sistema. A única forma de fracasso inaceitável é terminar a sprint sem respostas claras, com meio código no ar, meio código legado e uma sensação geral de “não sabemos se isso funciona”.

Este Bloco 3 encerra o Capítulo 1 colocando a Sprint 31 no lugar certo: uma sprint de infraestrutura de ingestão que amarra os quatro Programas entre si e define, de forma explícita, o que significa dizer que o Inspectah é realmente provider-first na prática, e não só no discurso.

