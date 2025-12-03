# Inspectah — Sprint 30 — Capítulo 1 — Bloco 2
## Problemas Específicos, Hipóteses de Solução e Direção de Resultado

### 1. Decomposição do Problema Central em Problemas Específicos

Partindo do problema central da S30 — “para o caso de notícias, o Console de Fluxos ainda não é o cockpit operacional definitivo” — o squad de Fluxos & Orquestração decompôs a dor em quatro problemas específicos, cada um com sintomas claros e impactos diretos na operação 24/7 do Inspectah.

#### 1.1. Estados de fluxo não têm força de lei sobre o roteamento

Hoje, embora o modelo já preveja estados como `draft`, `em_teste`, `ativo`, `pausado` e `deprecado`, o comportamento real do sistema ainda não é rigidamente subordinado a esses estados.

Sintomas observáveis:
- Um fluxo marcado como `em_teste` pode, na prática, processar mais tráfego do que deveria, porque a regra de roteamento não é única, centralizada e auditável.
- A noção de “fluxo ativo” para um determinado tipo de entrada (por exemplo, `noticia_texto`) ainda está parcialmente espalhada entre configuração, código e convenção.
- A ação de “pausar” um fluxo não é, hoje, uma garantia formal de que ele deixará de receber novos eventos — há caminhos alternativos, ou zonas cinzentas, que podem inadvertidamente continuar usando aquele fluxo.

Impacto direto:
- O operador não consegue confiar que o console é a fonte de verdade sobre o que está rodando em produção.
- Experimentos com fluxos em teste correm o risco de contaminarem tráfego real além do planejado.

#### 1.2. Inexistência de um template oficial e versionado para fluxo de notícias

O fluxo de notícias é, ao mesmo tempo, um dos mais críticos e um dos mais frequentes no Inspectah. Mesmo assim, não há ainda um **template versionado** que diga, de forma inequívoca, como um “Fluxo_Noticias_Geral_v1” deve ser:

Sintomas observáveis:
- Fluxos de notícias atuais são frutos de arranjos específicos, feitos caso a caso, com decisões que residem em código ou em memória tribal.
- Não existe um artefato canônico que descreva a cadeia mínima (intérprete → classificador de tipo → analista(s) → debunker(s) → decision maker) com parâmetros ajustáveis, mas esqueleto fixo.
- Criar um novo fluxo de notícias “parecido com aquele outro” ainda é uma operação manual, sujeita a divergências e esquecimento de etapas.

Impacto direto:
- Dificuldade em manter coerência entre múltiplos fluxos de notícias.
- Dificuldade em evoluir a topologia do fluxo de maneira controlada (por exemplo, subir uma nova versão do fluxo sem quebrar contratos).

#### 1.3. Console ainda não substitui o desenvolvedor nas operações do fluxo

Mesmo após a S29, várias operações cruciais ainda exigem envolvimento direto de desenvolvimento ou scripts manuais:

Sintomas observáveis:
- Para trocar o agente de uma etapa crítica (por exemplo, o classificador de tipo de notícia), é comum alterar código ou configuração em arquivos internos, em vez de usar o Console.
- Para promover um fluxo de `em_teste` para `ativo`, na prática, ainda se recorre a ajustes de configuração que não passam pelo console.
- Operações de pausa, retomada ou reprocessamento fazem uso de ferramentas fora do fluxo normal de operação (scripts, comandos diretos em filas, etc.).

Impacto direto:
- A operação 24/7 fica dependente de engenheiros, e não de operadores.
- A fronteira entre “configuração” e “implementação” permanece borrada, o que dificulta dividir responsabilidades entre squads.

#### 1.4. Rastreabilidade e observabilidade do fluxo de notícias são insuficientes

Sem uma trilha de execução clara por notícia e sem métricas por fluxo, a equipe opera parcialmente às cegas:

Sintomas observáveis:
- Dado o ID de uma notícia, não é trivial, hoje, reconstruir a sequência de etapas que ela percorreu, quais agentes foram chamados e qual foi o resultado em cada etapa.
- Métricas consolidadas por fluxo — como contagem de execuções, taxas de erro, latência p95, backlog em etapas críticas — não estão claramente expostas em um ponto único.
- É difícil responder a perguntas como “o fluxo de notícias está saudável?” ou “onde está o gargalo?” sem caçar evidências em múltiplos logs e dashboards genéricos.

Impacto direto:
- A capacidade de operar o Inspectah como um sistema 24/7 e de reagir rapidamente a problemas em fluxos de notícias fica seriamente limitada.

---

### 2. Hipóteses de Solução (em Linguagem de Resultado)

Para cada um dos problemas específicos, a S30 assume hipóteses claras de solução, sempre formuladas em termos de **estado desejado** e não de “tarefa técnica”.

#### 2.1. Tornar o estado de fluxo um contrato operacional rígido

Hipótese:
> “Se o roteamento de notícias para fluxos for governado por uma camada única de decisão, que lê exclusivamente o estado de cada fluxo (`em_teste`, `ativo`, `pausado`) e regras declarativas, então o comportamento real do sistema se alinhará ao que o Console mostra, e o operador poderá confiar que mudar o estado no console muda, de fato, o tráfego.”

Tradução prática para S30:
- Definir, implementar e testar uma política única de escolha de fluxo para cada tipo de entrada.
- Amarrar essa política aos estados de fluxo, de forma que qualquer divergência entre estado e tráfego se torne um bug evidente, não um “jeitinho” aceitável.

#### 2.2. Criar um template oficial, versionado e utilizável de Fluxo de Notícias v1

Hipótese:
> “Se houver um template oficial e versionado de ‘Fluxo_Noticias_Geral_v1’, que reflita a topologia mínima acordada pelo squad, então novos fluxos de notícias poderão ser criados de forma consistente, auditável e rápida, reduzindo divergências e facilitando a evolução controlada.”

Tradução prática para S30:
- Formalizar o template como entidade de primeira classe (com identificação, versão, estrutura de etapas, tipos de agentes por etapa).
- Permitir que o Console de Fluxos crie novos fluxos de notícias a partir desse template, exigindo apenas parâmetros essenciais (por exemplo, qual agente concreto usar em cada papel).

#### 2.3. Substituir intervenções de código por operações via Console para o fluxo de notícias

Hipótese:
> “Se as operações de ciclo de vida do fluxo (criar a partir de template, colocar em teste, promover para ativo, pausar, retomar, trocar agente de etapa) forem expostas no Console com trilha de auditoria, então o operador poderá gerenciar o fluxo de notícias sem depender de alterações de código, e a responsabilidade operacional ficará claramente alocada ao squad de operação.”

Tradução prática para S30:
- Mapear o conjunto mínimo de operações que precisam existir no Console para que o operador possa gerir o fluxo de notícias.
- Implementar essas operações de forma que sejam a **rota principal** e não um “atalho opcional”; mudanças por fora passam a ser exceção, não regra.

#### 2.4. Elevar rastreabilidade e observabilidade do fluxo de notícias a um patamar utilizável

Hipótese:
> “Se cada notícia processada pelo fluxo‑pivô deixar uma trilha clara de execuções de etapa, associada a métricas consolidadas por fluxo, então o squad conseguirá diagnosticar problemas, identificar gargalos e tomar decisões informadas em operação 24/7.”

Tradução prática para S30:
- Garantir que execuções de fluxo e de etapa para notícias sejam registradas em estrutura consultável (via Console e/ou APIs internas).
- Expor um conjunto pequeno, mas poderoso, de métricas por fluxo que permitam avaliar saúde e capacidade (contagem de execuções, taxa de falhas, latências, backlog).

---

### 3. Direção de Resultado: o que precisa ser verdade ao final da S30

Juntando os problemas específicos e as hipóteses de solução, o squad definiu a seguinte condição de vitória para a Sprint 30, num nível de exigência 9.9/10:

> “Para o caso de notícias, existe um fluxo‑pivô criado a partir de template oficial, cujo ciclo de vida é inteiramente gerido pelo Console (da criação à promoção, pausa e retomada), cujo comportamento real segue rigidamente os estados de fluxo e cuja jornada por notícia é rastreável e observável em nível suficiente para operar 24/7 sem recorrer a gambiarras.”

Se essa frase não for verdadeira, de forma demonstrável e verificável, a S30 deve ser considerada NO‑GO, independentemente da quantidade de commits, telas ou refactors produzidos.

Este Bloco 2 fecha a análise fina do problema e das hipóteses. Nos blocos seguintes do Capítulo 1, o squad detalhará objetivos mensuráveis, métricas de sucesso, fora de escopo e riscos/trade‑offs, sempre apontando na direção dessa condição de vitória.

