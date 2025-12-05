# Sprint 33 — Capítulo 5

## Bloco 1 — Posição da S33 no estado da arte de operação

Este bloco aprofunda a seção 5.1 do capítulo, detalhando como a Sprint 33 se posiciona em relação ao estado da arte em operação de sistemas. A pergunta central é: em que sentido o OracleOps v1 está alinhado com as melhores práticas modernas, e em que sentido ele começa a empurrar a fronteira quando o assunto é operar um sistema de verdade, não apenas de infraestrutura.

A S33 não nasce no vácuo. Ela se apoia em quatro tradições contemporâneas principais:

1. SRE (Site Reliability Engineering) e gestão moderna de confiabilidade.
2. Observabilidade de alta maturidade (métricas, logs, traces, eventos, correlação).
3. Gestão de incidentes como disciplina formal.
4. Cockpits e control planes para operação de plataformas complexas.

O que a S33 faz é pegar essas tradições e adaptá‑las a um domínio diferente: o de um sistema que ingere, interpreta, contesta e consolida alegações sobre o mundo, com a ambição de formar uma base de verdade auditável.

---

### 5.1.1 Convergência com SRE e confiabilidade moderna

Sob a ótica de SRE, a Sprint 33 traz para o Inspectah vários conceitos que hoje são considerados básicos em sistemas de grande porte:

Primeiro, a ideia de SLO como contrato operacional. A S33 não se contenta com "estar de pé"; ela define metas explícitas de saúde para o recorte da sprint (por exemplo, recência máxima de ingestão para certas fontes, latência aceitável em APIs internas, janela de tempo para conclusões de incidentes). Esses SLOs não ficam só em um documento: ganham representação em código (`ops_slos`) e um serviço de avaliação (`ops_slo_evaluator`), de forma muito semelhante ao modelo descrito em práticas de SRE.

Segundo, a formalização de incidentes. Em vez de tratar incidentes como tickets livres, a S33 define um modelo `Incident` com estados e transições válidas, refletidos em testes de domínio. Isso espelha a prática moderna em que incidentes são entidades com ciclo de vida, não apenas campos de texto.

Terceiro, a noção de revisão de prontidão. A ORR operacional (G5) é a versão da S33 para reviews de prontidão comuns em plataformas maduras, onde se verifica, com roteiro e critérios, se o sistema está de fato pronto para ser operado no novo cenário.

A principal diferença é de foco: enquanto o SRE tradicional costuma proteger métricas como uptime e latência, a S33 prepara o terreno para proteger também propriedades ligadas à recência e integridade de informação, colocando a operação a serviço da verdade.

---

### 5.1.2 Convergência com observabilidade moderna

A S33 assume que um sistema complexo só é operável se for observável. Nesse sentido, ela ecoa o movimento de observabilidade moderna, que enfatiza a combinação de métricas, logs, traces e eventos para entender o comportamento de sistemas distribuídos.

Na prática, isso aparece em alguns pontos fundamentais do design da S33:

O domínio de componentes (`ops_components`) não fala apenas em serviços genéricos, mas em componentes que já carregam metadados de observabilidade: links para dashboards, tipos de métrica relevantes, criticidade. O objetivo é que o operador nunca fique no escuro sobre onde olhar ao investigar um problema.

O serviço `ops_slo_evaluator` é explicitamente pensado como ponte entre definições de SLO e a stack de observabilidade. Ele é responsável por transformar SLOs declarativos em consultas concretas, retornando estados que o cockpit consegue exibir e que operadores conseguem interpretar.

A estrutura de evidências da S33 (especialmente em G3 e G4) inclui capturas de dashboards, resultados de queries e logs recortados para incidentes. Isso aproxima a operação do Inspectah das plataformas em que observabilidade não é apenas um painel paralelo, mas parte integrada do fluxo de resposta a incidentes.

---

### 5.1.3 Convergência com gestão moderna de incidentes

Na disciplina de gestão de incidentes, ferramentas e práticas modernas convergem em alguns pontos: fluxos claros de abertura e encerramento, severidades padronizadas, comunicação estruturada, aprendizado via postmortem. A S33 traz vários desses elementos para dentro do Inspectah.

O modelo `Incident` com lifecycle explícito é o centro dessa convergência. Estados, transições, timestamps e vínculo com componentes e SLOs fazem de Incident uma unidade de observação e aprendizado operacional, e não apenas um registro de “algo ruim aconteceu”.

Os bundles de incidentes em `out/evidence/S33_G4_incidents/` são a forma como a S33 codifica o equivalente a um postmortem enxuto, mas versionado e automatizado: timeline, logs, prints do cockpit, contexto de SLO, runbook aplicado. Isso cria cápsulas de verdade operacional que podem ser revisitadas, estudadas e até usadas como base para automação futura.

A ORR, por sua vez, funciona como um grande incidente simulado e guiado: um cenário controlado em que a equipe observa como a combinação cockpit + SLOs + runbooks se comporta sob pressão, capturando fricções reais.

---

### 5.1.4 Convergência com cockpits e control planes de plataformas complexas

Em plataformas modernas, é comum haver uma camada de "control plane" ou cockpit que concentra visibilidade e ação: painéis de clusters de Kubernetes, consoles de gestão de dados, painéis de orquestradores de workflow.

O OracleOps v1, desenhado na S33, é a encarnação dessa ideia para o Inspectah. Ele define um espaço claro no frontend para operação: rotas dedicadas, páginas específicas, componentes de apoio, cliente de API focado.

Essa convergência aparece na forma como o cockpit responde a perguntas operacionais reais: saúde do recorte, estado de componentes, incidentes ativos, SLOs em risco, caminhos para ação via runbooks. O cockpit não é um painel de marketing; é um console funcional que aproxima o Inspectah das melhores práticas de control planes contemporâneos.

---

### 5.1.5 O twist: operar verdade, não só infraestrutura

Apesar de toda essa convergência, o contexto do Inspectah é peculiar. O sistema não está apenas preocupado em entregar bytes; está preocupado em entregar **verdades bem suportadas por evidência, com trilhas auditáveis e espaço para contestação**.

Essa natureza muda o eixo de operação. O que está em jogo não é apenas se um serviço está de pé, mas se a cadeia que leva de uma alegação a um fato está íntegra, atual e transparente. A S33 prepara o terreno para medir e operar essa cadeia.

Ao introduzir SLOs que podem ser ligados a recência de fontes, latência de promoção de alegações, tempos de reação a contestação; ao tratar componentes como etapas nomeadas na jornada da informação; e ao encapsular incidentes em bundles de evidência, a S33 começa a desenhar um modo de operação em que confiabilidade técnica e confiabilidade epistemológica andam juntas.

Nesse sentido, a Sprint 33 não apenas acompanha o estado da arte: ela aponta para uma extensão dele. É um primeiro passo em direção a um campo onde SRE, observabilidade e gestão de incidentes passam a ser aplicados não só a serviços, mas a sistemas de verdade.

Este Bloco 1 estabelece esse enquadramento. Os blocos seguintes do Capítulo 5 descem para os padrões concretos incorporados, as diferenças específicas do Inspectah e as trilhas de evolução que se abrem a partir da S33.