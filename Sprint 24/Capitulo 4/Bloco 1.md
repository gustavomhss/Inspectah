# 4.1 – Contexto & Problemas a Resolver (Execução) – v2

Este subcapítulo 4.1 detalha, em nível operacional e conceitual, **por que** a execução desta sprint existe, **quais problemas concretos ela precisa resolver** e **como ela se encaixa no Sprint Playbook v2 de 6×4 capítulos**. Ele não é um resumo do Capítulo 4; é a especificação de contexto que guia todas as decisões de execução, dos scripts em `bin/` até o desenho dos scorecards em `out/scorecards/`.

A partir deste 4.1, qualquer pessoa da equipe deve conseguir responder, sem ambiguidade:
- qual é o papel desta sprint no arco S21–S25 do Inspectah;
- quais dores históricas e riscos estruturais de execução ela precisa mitigar;
- que premissas de ambiente, dados e ferramentas são assumidas como obrigatórias;
- quais são os objetivos de execução **não negociáveis**, e o que explicitamente NÃO entra como meta agora.

---

## 4.1.1 – Posição do Capítulo 4 no Sprint Playbook v2 (6×4)

O Sprint Playbook v2 organiza cada sprint em 6 capítulos macro, cada um com 4 subcapítulos fixos (Contexto & Problemas; Gates & Métricas & DoD; Arquitetura & Filemap; Execução & Evidências). O Capítulo 4 é o capítulo macro de **Execução & Evidências**, e o 4.1 é a sua “cabeça”: explica o cenário em que a execução acontece e os problemas de execução que precisam ser atacados.

Relação explícita com os outros capítulos:
- **Cap. 1 (Contexto & Produto)**: diz o *porquê* macro da sprint – qual recorte de produto e de visão do Inspectah (dentro do arco S21–S25) está em jogo. O 4.1 herda esse porquê e o traduz em termos de execução: em vez de “queremos ingestão 2.0 para notícias”, passa a ser “precisamos de ao menos X fontes estáveis, Y cenários de ingestão reprodutíveis, Z scripts oficiais que demonstrem esse fluxo”.
- **Cap. 2 (Gates & Métricas & DoD)**: define os contratos de aceitação. O 4.1 assume esses contratos e responde: como a execução precisa ser desenhada para que esses gates sejam exercitáveis, objetivos e reprodutíveis.
- **Cap. 3 (Arquitetura & Modelos & Integrações)**: descreve a anatomia do sistema (entidades, invariantes, APIs, eventos, dependências). O 4.1 foca na “geografia de guerra”: quais partes dessa anatomia entram em jogo nesta sprint de execução, em que ordem, com que riscos, e com qual profundidade.

Em termos práticos, o 4.1 é o lugar onde se faz a ponte entre:
- visão de alto nível (produto e verdade/fato),
- contratos formais (gates e métricas),
- desenho estático (modelo de dados, APIs),
- e o plano concreto de “como tudo isso vai rodar na vida real”.

Sem um 4.1 forte, o restante do Capítulo 4 (4.2–4.4) vira uma lista de comandos soltos sem direção, e a sprint volta a depender de “folclore de time”.

---

## 4.1.2 – Papel específico desta sprint no arco S21–S25

O arco S21–S25 do Inspectah constrói, em camadas, a espinha dorsal Verdade & Interpretação:
- S21: Console de Fontes – cadastro, configuração e health‑check de `Source` e `IngestionConfig`.
- S22: Ingestão 2.0 – orquestração de `IngestionRun`, `IngestionItemRaw` e `IngestionItemNormalized`.
- S23: Cérebro v1 – `InterpretationUnit`, `ClassificationResult` e `Claim` a partir de ingestão.
- S24: Debunker v0 & Comitês – `CommitteeEvaluation`, `CommitteeDecision`, `DebunkIssue`, `DebunkTask`.
- S25: Governança & Truth‑DB – `TruthRecord`, `TruthChangeEvent` e política de promoção/rebaixamento.

Esta sprint (qualquer que seja seu número dentro desse arco) ocupa uma posição concreta ali dentro – por exemplo, “S22 – Ingestão 2.0, v1 do fluxo de ingestão baseado em fontes de notícias” ou “S23 – pipeline mínimo de claims para notícias econômicas”. O 4.1 deve:
- declarar explicitamente **qual camada ou combinação de camadas** é alvo desta sprint;
- deixar claro **qual é o fluxo ponta a ponta mínimo** que precisa funcionar usando as peças dessa camada;
- apontar qual é a fronteira de dependência: o que é assumido como “já está pronto e confiável das sprints anteriores” e o que vai ser construído aqui.

Esse posicionamento evita que a execução tente “resolver o universo inteiro” em uma sprint só e, ao mesmo tempo, evita o oposto: que se faça algo tão isolado que não encaixa no arco de Verdade & Interpretação.

---

## 4.1.3 – Dores históricas de execução que este capítulo precisa atacar

Do ponto de vista da equipe e da história de sprints anteriores, existem dores recorrentes que o Capítulo 4 (e especificamente o 4.1) tem a obrigação de endereçar de forma explícita:

1. **Execução tribal**
   - Sintoma: cada dev tem seu próprio conjunto secreto de comandos, fixtures e hacks; “rodar a sprint” significa perguntar para a pessoa que fez.
   - Risco: reprodutibilidade baixa, entrada de novos membros demorada, bugs que só aparecem em ambiente limpo ou no CI.
   - Resposta do 4.1: deixar claro que o produto final da execução não é só código, mas um **conjunto padronizado de scripts, cenários e scorecards** que qualquer pessoa consegue rodar.

2. **Diferença entre “funcionar uma vez” e “ser estável”**
   - Sintoma: há um fluxo que “funcionou na demo”, mas não há scripts para repetir aquilo de forma mecânica.
   - Risco: regressões invisíveis, bugs que reaparecem, dificuldade de saber se uma mudança quebrou algo importante.
   - Resposta do 4.1: explicitar que **todo fluxo importante de negócio** precisa ter um reflexo em cenários executáveis (scripts + testes), e que o Cap. 4 vai descrever quais são esses fluxos.

3. **Ambientes divergentes (local, CI, futuro staging)**
   - Sintoma: comandos diferentes para rodar as mesmas coisas em ambientes diferentes; CI usando scripts que não existem localmente; local usando ferramentas que não estão disponíveis no runner.
   - Risco: pipelines quebrando sem motivo aparente, necessidade de “rituais” de acerto toda vez que se abre uma nova máquina.
   - Resposta do 4.1: estabelecer como premissa que **os scripts oficiais em `bin/` são a fonte única da verdade** para execução e que o Cap. 4 será a documentação desses scripts e de seus efeitos.

4. **Dependência mal modelada de fontes externas e LLMs**
   - Sintoma: testes que falham porque o portal de notícias mudou HTML, porque a API externa ficou lenta, ou porque o modelo LLM deu uma resposta diferente.
   - Risco: instabilidade crônica, dificuldade de dizer se o problema é do Inspectah ou da fonte/LLM.
   - Resposta do 4.1: definir desde o contexto que a execução precisa prever **modos de teste e dados de referência** que sejam mais estáveis: snapshots em Evidence Vault, fixtures, modos simulados de agentes.

5. **Estados de verdade incoerentes**
   - Sintoma: claims com mais de um TruthRecord ativo, eventos de `TruthChangeEvent` faltando, ou estados que não batem com decisões de comitê.
   - Risco: quebra do princípio fundamental do Inspectah: verdade precisa ser coerente, auditável e difícil de corromper.
   - Resposta do 4.1: marcar como prioridade que a execução desta sprint precisa incluir **sanity checks de Truth‑DB**, mesmo que a sprint atual não seja “a sprint da Truth‑DB” oficialmente.

O 4.1 registra essas dores não como lista genérica, mas como **riscos concretos desta sprint**. Isso orienta quais cenários de execução devem ser priorizados e quais gates precisam ser endurecidos.

---

## 4.1.4 – Premissas de ambiente e ferramentas

Para que os subcapítulos 4.2–4.4 façam sentido, o 4.1 fixa premissas sobre o ambiente padrão de desenvolvimento e execução da sprint. Essas premissas não são detalhes “técnicos demais”; são parte do contrato de execução.

Premissas mínimas:

1. **Stack de infraestrutura levantável por script**
   - Banco relacional (por exemplo, Postgres) com schemas apropriados para o domínio da sprint.
   - Mensageria (Kafka, Redis Streams, SQS ou equivalente) com tópicos/filas previstos no Cap. 3.4.
   - Stack de observabilidade mínima: coleta de logs estruturados, métricas e, quando suportado, tracing.
   - Opcionalmente, um docker‑compose ou conjunto de scripts que suba tudo isso de forma padronizada.

2. **Configuração e segredos**
   - Variáveis de ambiente padronizadas para DSNs de banco, endpoints da mensageria, chaves de API de fontes externas.
   - Um mecanismo explícito de documentação dessas variáveis (por exemplo, `.env.example` versionado sem segredos reais). O 4.1 sinaliza que o 4.3/4.4 vão detalhar isso.

3. **Ferramentas de desenvolvimento e execução**
   - Linguagem e versão (por exemplo, Python 3.x com virtualenv ou Poetry, Node para frontend se aplicável).
   - Ferramentas de linting, formatação e teste (pytest, mypy, etc.), já posicionadas em Cap. 2 mas aqui assumidas como presentes.

4. **Dados de teste e fixtures mínimas**
   - Um conjunto de exemplos canônicos (notícia A, dataset B, claim C) que serão usados em múltiplos cenários de execução.
   - Preferência por dados públicos ou fictícios, com snapshots armazenados em Evidence Vault, para não depender da disponibilidade ou mutabilidade das fontes externas.

Se qualquer uma dessas premissas ainda não estiver garantida no repositório, o 4.1 deixa explícito que uma parte da sprint será gasta em “infra de execução” e que isso é objetivo declarado de entrega, não um “favor paralelo”.

---

## 4.1.5 – Objetivos de execução não negociáveis

Com o contexto, dores e premissas estabelecidos, o 4.1 traz para o plano da sprint uma pequena lista de objetivos de execução que **não são negociáveis**. Esses objetivos são o fio condutor dos subcapítulos seguintes.

1. **Fluxo ponta a ponta mínimo e reprodutível**
   - Deve existir pelo menos um cenário oficial que percorra, do início ao fim, o recorte da sprint (por exemplo, `Source` → `IngestionRun` → `IngestionItemNormalized` → `InterpretationUnit` → `Claim` → `CommitteeDecision` → `TruthRecord`).
   - Esse cenário precisa estar implementado como script ou conjunto de scripts em `bin/`, com descrição clara no Cap. 4.4.

2. **Gates exercitáveis, com scorecards legíveis**
   - Todo gate definido no Cap. 2 para esta sprint precisa ter um comando oficial que o rode e gere scorecards em `out/scorecards/`.
   - Os scorecards devem expor métricas e estados em formato legível (tipicamente JSON), sem campos mágicos.

3. **Sanidade estrutural de dados garantida**
   - Independente do recorte da sprint, invariantes críticas descritas no Cap. 3.3 (cadeias de origem, unicidade de truth ativo, etc.) devem ser verificadas via scripts de sanidade.
   - Esses scripts fazem parte da execução e são tratados como “first‑class citizens”, não como utilitários de bastidor.

4. **Execução simétrica entre local e CI**
   - Qualquer comando considerado oficial para “rodar a sprint” precisa funcionar, sem ajustes semânticos, tanto em ambiente local quanto no CI.
   - Ajustes de configuração (variáveis de ambiente, DSNs) são tolerados; divergências de comportamento não.

5. **Registro de evidências como produto**
   - Logs, dumps, snapshots de dados e bundles de evidência não são “lixo de build”; são parte do produto da sprint.
   - O 4.1 explicita que a sprint só é considerada completa quando existe um bundle de evidências que conte, de forma verificável, a história de execução.

---

## 4.1.6 – Fora de escopo (explícito) desta execução

Tão importante quanto dizer o que a execução **vai** fazer é dizer o que **não** entra agora, mesmo que esteja no horizonte do Inspectah.

Exemplos de fora de escopo que o 4.1 pode fixar para esta sprint específica:

- **Reputação avançada de fontes ou de agentes**: o foco é fazer a pipeline core funcionar; reputação vem em sprints da Fase 2.
- **Blockchain e Sistema de Blocos completo**: embora a Truth‑DB seja desenhada para suportar futura ancoragem, a execução desta sprint não inclui registrar nada on‑chain.
- **UI avançada / Cockpit definitivo**: esta sprint pode expor APIs e dumps de dados, mas não é o momento de construir dashboards finais; o foco é backoffice e observabilidade interna.
- **Comitês V2/V3 altamente sofisticados**: a meta é montar um comitê mínimo confiável; estruturas complexas de votação, pesos e multi‑comitês ficam para depois.

Registrar explicitamente o fora de escopo evita frustração e garante que as evidências de execução não sejam cobradas por metas que pertencem a outras sprints.

---

## 4.1.7 – Saídas esperadas deste subcapítulo

Ao finalizar a leitura do 4.1, o time deve ter:

- um entendimento compartilhado do **porquê operacional** da sprint;
- a lista de dores e riscos de execução que precisam ser mitigados;
- clareza sobre as premissas de ambiente, dados e ferramentas que os subcapítulos 4.2, 4.3 e 4.4 vão assumir;
- um conjunto pequeno, mas firme, de objetivos de execução incontornáveis e de itens explicitamente fora de escopo.

Esse subcapítulo é, portanto, o contrato de contexto do Capítulo 4. Se, em qualquer momento da sprint, surgir dúvida sobre “vale a pena criar mais um script?”, “precisamos mesmo desse cenário de falha?”, “podemos deixar sanidade de truth para depois?”, a resposta deve ser buscada aqui: **o 4.1 é o norte que protege a execução contra atalhos perigosos e contra ambições desnecessárias**.

