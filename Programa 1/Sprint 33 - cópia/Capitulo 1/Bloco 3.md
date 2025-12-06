# Sprint 33 — Capítulo 1

## Bloco 3 — Objetivos e estados‑alvo da Sprint 33

A Sprint 33 tem um propósito central: transformar um conjunto de capacidades técnicas já existentes — ingestão 2.0, Console de Fontes, agentes, Truth‑DB, System of Blocks, observabilidade básica, gates e bundles — em **capacidade de operação real e repetível**. Em vez de adicionar novas peças ao sistema, a S33 reorganiza o que já existe em torno de quatro objetivos estratégicos e de um conjunto enxuto, mas claro, de estados‑alvo. Esses objetivos e estados‑alvo são a régua pela qual a sprint deve ser julgada.

### 3.1 Objetivo 1 — Criar o OracleOps Cockpit v1 como fonte única de verdade operacional interna

O primeiro objetivo é fazer nascer o **OracleOps Cockpit v1**: um console interno que funcione como ponto de partida e de chegada para qualquer sessão de operação do Inspectah.

Estados‑alvo associados a este objetivo:

- **SA‑33‑1.1 — Visão geral única de saúde.**  
  Existe uma página de overview no OracleOps Cockpit que consolida, em uma única tela, a visão de saúde do sistema, incluindo: 
  - status de ingestão por fonte (OK, lento, falhando, desativado),
  - backlog e latência de filas e workers relevantes,
  - estado dos principais pipelines de agentes (interpretação, classificação, debunking, Truth‑DB),
  - indicadores de erro em APIs internas críticas.
  Essa visão é alimentada por dados reais, derivados de métricas, logs ou registros de jobs, sem indicadores “fake” ou puramente decorativos.

- **SA‑33‑1.2 — Navegação por fontes e pipelines críticos.**  
  A partir da visão geral, o operador consegue navegar para telas focadas em: 
  - uma fonte específica (por exemplo, uma fonte oficial de dados), 
  - um pipeline específico (por exemplo, ingestão → agentes → Truth‑DB) 
  e visualizar, para esse recorte, estado, histórico recente, links para dashboards externos e logs associados.

- **SA‑33‑1.3 — Integração mínima com observabilidade existente.**  
  Para cada componente monitorado (fontes, filas, pipelines, APIs), o cockpit oferece links diretos para dashboards e ferramentas de observabilidade já existentes, com convenções mínimas de naming pactuadas. O operador não precisa “caçar” o dashboard correto; ele parte do cockpit.

### 3.2 Objetivo 2 — Instituir o Fluxo de Incidentes v1 como modelo oficial de resposta a falhas

O segundo objetivo é transformar o tratamento de incidentes de um processo informal para um fluxo explícito, com entidades, estados e trilhas de auditoria claras.

Estados‑alvo associados a este objetivo:

- **SA‑33‑2.1 — Modelo de incidente como entidade de domínio.**  
  Incidentes passam a existir como objetos persistidos no sistema, com campos mínimos: id, estado, severidade, componentes afetados (fontes, pipelines, serviços), SLOs relacionados, timestamps relevantes e observações.

- **SA‑33‑2.2 — Ciclo de vida de incidentes definido.**  
  Existe um ciclo de vida oficial de incidentes (por exemplo: aberto → em triagem → mitigado → resolvido → pós‑mortem pendente → concluído), implementado e refletido tanto na UI quanto na API. Mudanças de estado são registradas com quem tomou a ação e quando.

- **SA‑33‑2.3 — Integração com o cockpit.**  
  A visão de overview do OracleOps Cockpit exibe pelo menos: 
  - lista de incidentes ativos, 
  - indicadores de incidentes recentes por severidade, 
  - atalhos para abrir novos incidentes a partir de sinais (ex.: um SLO violado, um componente marcado como crítico, um healthcheck falho).

- **SA‑33‑2.4 — Registro mínimo de pós‑mortem.**  
  Para incidentes selecionados dentro do recorte da sprint, o fluxo permite registrar uma síntese de pós‑mortem: hipótese de causa raiz, ações definitivas, débitos técnicos gerados. Não é um sistema de relatórios complexo, mas um registro simples e versionado, suficiente para reaproveitar aprendizado em sprints futuras.

### 3.3 Objetivo 3 — Tornar SLOs operacionais praticáveis, não apenas declarados

O terceiro objetivo é levar uma fração bem definida dos SLOs do papel para a realidade operacional, ainda que em recorte.

Estados‑alvo associados a este objetivo:

- **SA‑33‑3.1 — Conjunto enxuto de SLOs priorizados.**  
  Existe uma lista explícita de SLOs da S33, cobrindo pelo menos: 
  - recência de dados de um conjunto de fontes críticas,
  - tempo máximo de processamento para um pipeline de ingestão + agentes + Truth‑DB,
  - disponibilidade mínima de uma ou duas APIs internas essenciais para o cockpit.
  Esses SLOs são descritos com métrica, limiar, janela de observação e tipo de objetivo.

- **SA‑33‑3.2 — Instrumentação conectada a dados reais.**  
  Para cada SLO da lista, existe uma métrica implementada na stack de observabilidade (ou equivalente), com consultas definidas e verificadas, de forma que seja possível observar, a qualquer momento, se o SLO está sendo cumprido.

- **SA‑33‑3.3 — Alertas mínimos configurados.**  
  Para pelo menos um subconjunto dos SLOs (os mais críticos), há alertas configurados com limiares e canais mínimos acordados. Esses alertas não precisam cobrir todos os casos futuros, mas precisam provar que o ciclo “SLO → métrica → alerta → operador” está funcionando.

- **SA‑33‑3.4 — SLOs visíveis no cockpit.**  
  O OracleOps Cockpit exibe, de forma resumida, o estado dos SLOs priorizados: por exemplo, “SLO de recência da fonte X: dentro/fora do alvo”, “SLO de latência do pipeline Y: estável/degradado”. Não é necessário um motor genérico, mas uma visualização funcional para o recorte da sprint.

### 3.4 Objetivo 4 — Elevar runbooks e evidência de operação a primeiro cidadão do repositório

O quarto objetivo é tirar o conhecimento operacional do campo da memória e de documentos dispersos, trazendo‑o para perto do fluxo real de trabalho de quem opera o sistema.

Estados‑alvo associados a este objetivo:

- **SA‑33‑4.1 — Catálogo mínimo de runbooks priorizados.**  
  A S33 define um conjunto enxuto de cenários de incidente prioritários (por exemplo: falha em fonte oficial crítica, saturação de filas de ingestão, atraso em pipeline de Truth‑DB, indisponibilidade de API interna do cockpit) e produz runbooks para cada um deles, em linguagem clara, com passos, comandos e critérios de sucesso/falha.

- **SA‑33‑4.2 — Runbooks versionados e acessíveis.**  
  Esses runbooks são armazenados em local padrão no repositório, versionados junto com o código e referenciados a partir do OracleOps Cockpit (por exemplo, links contextuais na visão de incidentes ou de componentes).

- **SA‑33‑4.3 — Evidência de incidentes real ou realisticamente simulada.**  
  Para pelo menos um incidente real ou simulado de forma realista, existe um bundle de evidência que reúna: 
  - registros de mudança de estado do incidente,
  - prints ou exportações de dashboards relevantes,
  - trechos de logs ou referências a logs,
  - nota de pós‑mortem minimalista.
  Esse bundle pode ser reaproveitado em ORR e em documentação futura.

- **SA‑33‑4.4 — Integração com o ciclo de aprendizado.**  
  A especificação da S33 amarra explicitamente como incidentes e runbooks alimentam o ciclo de melhoria contínua: aprendizados relevantes viram entradas claras para backlog de sprints futuras (debêntes técnicos, ajustes de SLO, melhorias em observabilidade ou design de fluxos).

### 3.5 Resultado esperado em termos de mudança de estado do sistema

Se a Sprint 33 cumprir seus objetivos e alcançar os estados‑alvo descritos, o Inspectah sai desta sprint em um patamar operacional diferente:

- A pergunta “o sistema está saudável agora?” deixa de ser respondida com “depende, deixa eu olhar algumas coisas” e passa a ter uma resposta concreta dentro do OracleOps Cockpit.
- Incidentes deixam de ser casos isolados e passam a seguir um fluxo padronizado, com estados, trilha e aprendizado reaproveitável.
- SLOs deixam de ser promessas em documentos e passam a se manifestar como métricas, alertas e elementos visíveis na rotina de operação.
- Runbooks e evidência de operação deixam de ser artefatos periféricos e viram parte da rotina de quem opera o sistema.

Em termos práticos, a S33 deve deixar a organização em condição de operar um subconjunto bem escolhido de fontes e pipelines críticos com um nível de previsibilidade e transparência que não existia antes — criando um modelo que possa ser expandido nas sprints seguintes sem refatorações traumáticas.