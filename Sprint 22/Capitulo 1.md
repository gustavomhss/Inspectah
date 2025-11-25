# Inspectah — Sprint 22 — Capítulo 1 (v2)

## 1. Contexto e ponto de partida

A Sprint 22 começa em um momento em que o Inspectah já deixou de ser apenas uma ideia e passou a ter um esqueleto concreto de produto. A Sprint 21 entregou um Console de Fontes funcional, capaz de cadastrar e manter fontes de vários tipos (por exemplo notícias via RSS ou HTML parseável, dados oficiais expostos como APIs, bases estatísticas, feeds de preços e outros formatos que façam sentido para a Fase 1). Essas fontes possuem tipos bem definidos, estados claros (ativa, desabilitada, deprecada) e um mínimo de metadados para que o sistema consiga tratá‑las como entidades de primeira classe.

Esse console resolve um problema fundamental: o Inspectah agora sabe quais são as fontes que importam, como elas se chamam, que tipo de dado entregam e em que estado se encontram. Porém, do ponto de vista de fluxo real de dados, ainda estamos numa fase pré‑industrial: não existe uma camada contínua e confiável de ingestão por fonte. Hoje, na prática, o sistema não se comporta como um organismo vivo que puxa dados o tempo todo. Ele se parece mais com um cadastro bem organizado esperando que alguém faça algo com ele.

É exatamente esse abismo entre “saber que a fonte existe” e “de fato buscar, registrar e expor o que veio dessa fonte” que a Sprint 22 precisa fechar. Ela representa a transição do Inspectah de catálogo de fontes para sistema que ingere, registra e permite operar ingestão em ritmo de produção.

## 2. Propósito da Sprint 22

O propósito central da Sprint 22 é criar a camada de Ingestão 2.0 por fonte. Em termos simples, isso significa que, ao final da sprint, o Inspectah deve ser capaz de:

(a) para cada fonte cadastrada e ativa, possuir uma configuração explícita de ingestão;  
(b) executar ingestões manuais e automáticas de forma controlada;  
(c) registrar cada execução como uma entidade de primeira classe, com estado e histórico;  
(d) expor, para operadores humanos, uma visão clara do que está acontecendo e do que já aconteceu.

A Sprint 22 não é sobre interpretação, classificação, debunking ou promoção de verdades. Ela é sobre encanamento. Trata dos canos, válvulas, relógios de pressão e manômetros que vão permitir que, mais tarde, os agentes de interpretação (S23), o Debunker v0 (S24) e a camada de governança de verdade/fato (S25) se apoiem em um fluxo de dados contínuo, auditável e previsível.

A partir desta sprint, o Inspectah precisa ser capaz de responder, com segurança e sem improviso, perguntas como: “quando foi a última vez que buscamos dados desta fonte?”, “isso aqui falhou ou nunca foi executado?”, “quantos itens foram ingeridos no último ciclo?”, “por que essa fonte está sem dados recentes?”. Responder a essas perguntas é indispensável antes de sequer pensar em verdade ou mentira.

## 3. Visão de fim de Sprint

No fim da Sprint 22, a visão de alvo pode ser descrita da seguinte forma.

Para cada fonte cadastrada e ativa no Console de Fontes existe um objeto de configuração de ingestão associado, daqui em diante chamado de IngestionConfig. Essa configuração informa, de forma explícita, se a ingestão está habilitada, qual o modo de operação (automático ou apenas manual), qual intervalo desejado entre execuções e quais os limites básicos de tentativas e timeouts. IngestionConfig só pode existir para fontes válidas e não pode entrar em estados contraditórios com o console (por exemplo, uma fonte marcada como deprecada não pode aparecer como habilitada para ingestão automática).

Além disso, cada tentativa concreta de ingestão é registrada como uma entidade IngestionRun. Essa entidade tem atributos mínimos obrigatórios: fonte, timestamps de início e fim, estado final, quantidade lógica de itens processados, possibilidade de armazenar mensagens de erro estruturadas e um identificador estável que permita futuro vínculo com evidências, casos e blocos de verdade. Estados devem seguir uma máquina simples, algo como: PENDING, RUNNING, SUCCESS, PARTIAL_SUCCESS ou FAIL. Ao terminar, nenhum run pode ficar sem estado final coerente com o que aconteceu.

Do ponto de vista da operação, o administrador consegue, a partir da interface de admin, enxergar para cada fonte: se está habilitada para ingestão, em qual modo, qual foi a última execução, qual o estado dessa última execução, qual a duração e um atalho para o histórico de runs. Consegue acionar uma ingestão manual pontual para uma fonte específica, pausar a ingestão automática ou migrar uma fonte de modo automático para manual somente, respeitando invariantes de consistência. A interface ainda não precisa ser refinada visualmente, mas deve ser compreensível e utilizável por alguém que não participou da implementação.

Por fim, a arquitetura de ingestão resultante da S22 se torna o ponto único de verdade sobre ingestões para as próximas sprints. S23 passa a consumir dados a partir de artefatos produzidos pela ingestão, S24 passa a localizar evidências cruas por run e por fonte, e S25 passa a enxergar estatísticas de ingestão (taxas de erro, atraso crônico, fontes problemáticas) como sinais para decisões de promoção de verdade. A Sprint 22 não implementa essa lógica, mas entrega a base confiável sobre a qual ela será construída.

## 4. Escopo: o que entra e o que fica de fora

O escopo da Sprint 22 é intencionalmente estreito em termos de semântica, e amplo em termos de confiabilidade operacional.

Dentro do escopo da S22 estão: modelagem de IngestionConfig e IngestionRun, amarradas ao modelo de Fonte da Sprint 21; implementação de um fluxo de ingestão 2.0 que respeita pré‑condições simples, registra o que aconteceu e conclui em estados bem definidos; exposição de endpoints e serviços internos para disparar ingestões (manuais e compatíveis com agendamentos); criação de uma camada mínima de telemetria e logging orientada à operação; e uma UI de admin para operar essas funções sem precisar de acesso de desenvolvedor.

Considera‑se também dentro do escopo garantir que os dados produzidos pela ingestão sejam armazenados de forma que possam ser consumidos, em sprints futuras, por interpretadores, classificadores e pelo Sistema de Blocos, sem exigir migrações traumáticas. Isso não significa desenhar o modelo de dados final da Truth‑DB ou dos blocos, mas sim evitar decisões que impeçam esse futuro.

Ficam explicitamente fora de escopo da Sprint 22: qualquer lógica de interpretação de texto, classificação de conteúdo, resumo, extração de entidades ou aplicação de agentes GPT; qualquer aspecto de reputação de fonte, pesos de confiança ou modelos estatísticos de credibilidade; qualquer forma de contestação, votação, governança ou promoção direta de verdades e fatos; qualquer integração com blockchain, ancoragem de evidências ou uso completo do Sistema de Blocos. Essas capacidades pertencem a S23, S24, S25 e, em especial, à Fase 2 do projeto, na qual o blueprint do Sistema de Blocos completo e os capítulos de contratos e TLA ganham vida.

Também fica fora de escopo implementar um super‑scheduler distribuído ou uma arquitetura de orquestração clusterizada. A Sprint 22 mira uma v1 robusta em ambiente único, com jobs previsíveis, sem precisar resolver desde já o problema de alta escala geográfica. O desenho, porém, deve ser compatível com uma evolução futura para algo mais distribuído.

## 5. Stakeholders, squads e responsabilidades

A Sprint 22 é propriedade primária do Squad 2 – Ingestão 2.0, responsável pelo desenho da camada de ingestão contínua e por garantir que ela se comporte como um sistema de estados bem definido, não como uma coleção de scripts soltos. Esse squad responde tecnicamente pela modelagem de IngestionConfig e IngestionRun, pela implementação das regras de transição de estados e pela integração com o Console de Fontes da Sprint 21.

Do ponto de vista da revisão conceitual, Leslie Lamport é o guardião da correção: a expectativa é que a ingestão seja tratada como um pequeno sistema distribuído, ainda que em processo local, com invariantes claros, ausência de estados zumbis e rastreabilidade de causa e efeito. Martin Kleppmann contribui na visão de log de eventos e auditabilidade, garantindo que o histórico de runs possa ser entendido como um fluxo de eventos no tempo, consultável e resistente a adulterações acidentais. Bret Victor se preocupa com a capacidade de um humano enxergar e entender o que está acontecendo sem ter que ler código ou logs brutos.

Os squads futuros também são stakeholders fortes. O Squad 3 (interpretação e classificação), o Squad 4 (Debunker v0 e humano no loop) e o Squad 5 (governança, verdade/fato e política de promoção) dependem diretamente da qualidade da ingestão. Se a S22 errar, essas sprints herdarão um solo instável. Por isso, requisitos de consumo futuro devem ser considerados desde já, mesmo sem implementar suas capacidades nesta sprint.

## 6. Princípios de engenharia e requisitos não funcionais

A Sprint 22 formaliza e aplica, na camada de ingestão, alguns princípios que já aparecem na DNA do projeto Inspectah.

Primeiro, nada de magia. Cada fluxo de ingestão deve ter pré‑condições explícitas, passos claramente identificáveis e pós‑condições verificáveis. Não pode existir situação em que um run some ou mude de estado sem trilha de explicação. Se algo falha, isso deve ser refletido em IngestionRun de forma inequívoca, com mensagens de erro suficientes para análise posterior.

Segundo, logs, estados e métricas precisam conversar entre si. Se uma ingestão falhou, o estado é FAIL ou PARTIAL_SUCCESS, os logs da execução precisam bater com essa realidade e as métricas derivadas não podem contar uma história alternativa. Essa coerência entre camadas é um requisito de sanidade: o sistema não pode mentir para si mesmo.

Terceiro, a ingestão precisa nascer compatível com o ideal de redundância e auditabilidade do Inspectah, mesmo que ainda não implemente a tripla redundância completa e a ancoragem criptográfica. Isso significa adotar desde já uma mentalidade de trilha de auditoria: tudo o que for importante para recontar a história de uma ingestão deve estar registrado em algum lugar estável e consultável.

Por fim, a S22 precisa garantir uma operação 24 por 7 conceitualmente possível, ainda que o volume inicial de fontes e execuções seja modesto. A ingestão não deve depender de operações manuais contínuas para sobreviver; o modo manual é uma ferramenta de operação, não a base da arquitetura.

## 7. Dependências, riscos e decisões tomadas

A principal dependência da Sprint 22 é o Console de Fontes entregue na Sprint 21. Tudo o que a S22 fizer parte do pressuposto de que fontes são cadastradas, tipadas e mantidas lá. Em termos de decisões de projeto, foi estabelecido que a ingestão trata o console como fonte única de verdade sobre o universo de fontes. Se uma fonte está deprecada ou desabilitada no console, ela não pode, por definição, participar da ingestão automática.

Existem riscos claros caso a S22 seja mal executada. O primeiro é a criação de scripts de ingestão que burlam ou ignoram o Console de Fontes, criando uma segunda verdade paralela. O segundo é o risco de estados inconsistentes, em que jobs são executados mas IngestionRun não reflete o que aconteceu, quebrando a auditabilidade. O terceiro é o risco de a telemetria ser tratada como detalhe opcional, deixando a operação cega.

Houve também decisões conscientes sobre o que não fazer agora. Blockchain, reputação avançada de fontes, comunidades de contestação e o Sistema de Blocos completo ficam, por desenho, na Fase 2. O objetivo é evitar paralisia por ambição e garantir que, neste momento, a energia vá para construir uma ingestão simples, resistente e compreensível.

## 8. Relação com as Sprints 21 a 25 e com a Fase 2

A Sprint 21 estabeleceu o universo de fontes. A Sprint 22 passa a colocar essas fontes em movimento, trazendo dados de forma contínua. A Sprint 23 vai consumir esse fluxo de dados para produzir interpretações, classificações e resumos estruturados. A Sprint 24 vai introduzir Debunker v0 e humano no loop, usando as ingestões como trilha bruta de evidências. A Sprint 25 começa a escrever regras de governança e modelos simples de promoção de verdade e fato, apoiando‑se em estatísticas e históricos de ingestão.

Mais à frente, na Fase 2, entra em cena o Sistema de Blocos completo, a Truth‑DB com ancoragem criptográfica e as políticas avançadas de reputação e contestação. Quando isso acontecer, a ingestão construída na S22 será a camada que alimenta os blocos com dados brutos e metadados de origem, tempo e estado. Por isso, o capítulo 1 da Sprint 22 enfatiza que esta sprint não é uma peça descartável; ela é um componente permanente da arquitetura do Inspectah.

## 9. Definição de sucesso do Capítulo 1

O Capítulo 1 da Sprint 22 é considerado bem‑sucedido se conseguir cumprir três papéis.

Primeiro, alinhar toda a equipe sobre o que a S22 é e o que ela não é, removendo ambiguidades sobre interpretação, reputação, blockchain e temas futuros. Segundo, fixar uma visão concreta de fim de sprint, na qual um observador externo é capaz de entender como a ingestão funciona apenas olhando para modelos de dados, telas de admin e exemplos de runs. Terceiro, fundamentar os capítulos seguintes da sprint, que irão detalhar gates de validação, arquitetura de arquivos, plano de execução e critérios de GO, sem precisar renegociar o propósito no meio do caminho.

Se, ao ler este capítulo, o Squad 2 e os demais stakeholders conseguirem responder de forma consistente à pergunta “para que exatamente serve a Sprint 22 e como saberemos que ela deu certo?”, então o Capítulo 1 cumpriu sua função e a sprint pode seguir para a definição de gates, filemap e plano de execução com segurança conceitual.

