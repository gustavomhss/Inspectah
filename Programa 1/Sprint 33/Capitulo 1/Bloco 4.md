# Sprint 33 — Capítulo 1

## Bloco 4 — Escopo, recorte e fronteiras da Sprint 33

A Sprint 33 foi desenhada para atacar um conjunto específico de dores operacionais sem tentar “abraçar o mundo” de uma vez. Depois de trinta e tantas sprints, o Inspectah já é um sistema complexo, com múltiplos programas, épicos e camadas; a S33 precisa, por definição, escolher um recorte claro para não se perder em ambição difusa. Este bloco explicita o que está dentro, o que está fora e quais são as fronteiras estruturantes da sprint, no mesmo espírito de disciplina que marcou a evolução da S29.

O ponto de partida é simples: a S33 tem como foco o **OracleOps Cockpit v1** e o **Fluxo de Incidentes v1**, em cima de um subconjunto cuidadosamente escolhido de fontes, pipelines e componentes críticos do Programa 1. A sprint não existe para reinventar ingestão, agentes ou Truth‑DB; existe para tornar a operação desses elementos visível, controlável e auditável. Isso significa que o escopo é definido mais por _como_ olhamos para o sistema do que por _quais_ novas funcionalidades técnicas são adicionadas.

### 4.1 Escopo positivo — o que a S33 se compromete a entregar

Em termos de produto interno, a S33 inclui:

1) **OracleOps Cockpit v1 focado em um recorte de criticidade.**  
   O cockpit que nasce nesta sprint não é um painel genérico para todos os componentes do Inspectah; ele é, deliberadamente, um console voltado para:
   - um conjunto explícito de fontes críticas (por exemplo, algumas fontes oficiais e feeds estruturantes para o Data Hub),
   - um conjunto de pipelines que vão de ingestão a Truth‑DB em caminhos representativos,
   - um subconjunto de APIs internas que sustentam a operação e o próprio cockpit.
   O escopo da S33 é fazer com que, para esse recorte, a experiência de operação seja qualitativamente diferente do status atual.

2) **Fluxo de Incidentes v1 implantado para o recorte monitorado.
**   A sprint se compromete a implementar o modelo de incidente como entidade de domínio, com ciclo de vida definido e integração com o cockpit, para incidentes que afetem os componentes cobertos pelo recorte acima. Isso inclui a capacidade de:
   - abrir incidentes associados a componentes e SLOs específicos,
   - acompanhar mudanças de estado com identificação de quem tomou cada ação,
   - registrar um pós‑mortem minimalista para incidentes selecionados.

3) **SLOs mínimos instrumentados e visíveis para o recorte escolhido.**  
   A S33 assume a responsabilidade de tirar do papel um conjunto enxuto de SLOs — recência de dados em fontes críticas, latência de pipelines representativos, disponibilidade de APIs internas vitais — e levá‑los até o ponto em que:
   - possuem métricas concretas associadas,
   - podem ser verificados via consultas em stack de observabilidade,
   - em alguns casos, disparam alertas mínimos,
   - aparecem sintetizados dentro do cockpit.

4) **Runbooks e bundles de evidência integrados ao fluxo de operação.**  
   Para os cenários de incidente que dizem respeito ao recorte da sprint, a S33 se compromete a:
   - produzir runbooks claros, versionados, armazenados em local padronizado no repositório,
   - integrá‑los ao cockpit via links contextuais,
   - produzir pelo menos um bundle de evidência completo (real ou simulado) que demonstre o ciclo incidente → resposta → pós‑mortem → aprendizado.

### 4.2 Anti‑escopo — o que a S33 explicitamente não tenta resolver

Para preservar foco e sanidade, a Sprint 33 não inclui:

1) **Cobertura total de todas as fontes, pipelines e serviços do Inspectah.**  
   Embora a visão de longo prazo do OracleOps seja cobrir toda a plataforma, a S33 não tenta universalizar o cockpit ou o fluxo de incidentes. A cobertura é propositalmente parcial, mas representativa. A regra é: preferimos um fluxo sólido para um recorte bem escolhido a um fluxo superficial para tudo.

2) **Redesenho da arquitetura de ingestão, agentes ou Truth‑DB.**  
   Não está no escopo mexer em modelos de dados estruturais, refazer contratos da Truth‑DB, redesenhar o System of Blocks ou alterar de forma profunda o pipeline de agentes. Ajustes pontuais podem ocorrer para expor informações necessárias à operação (por exemplo, adicionar campos de status em modelos ou eventos), mas sem mudanças de paradigma.

3) **Criação de um sistema genérico de incidentes multi‑produto.**  
   O modelo de incidentes da S33 é pensado para o Inspectah. A sprint não tenta construir uma plataforma genérica que possa ser utilizada por outros sistemas. O design busca ser limpo e extensível, mas a prioridade é aderência às necessidades concretas do OracleOps.

4) **Exposição externa de saúde ou incidentes para usuários finais.**  
   Todo o trabalho de S33 é voltado para operação interna. Não há compromissos de criar status pages públicas, consoles de casos acessíveis ao público ou APIs externas de incidentes. Essas ideias pertencem ao roadmap de programas posteriores; aqui o foco é garantir que o “motor da verdade” seja operável por quem está nos bastidores.

5) **Automação completa de resposta a incidentes.**  
   Embora a sprint possa introduzir pequenos automatismos (por exemplo, criação facilitada de incidentes a partir de certos sinais), a S33 não promete um mecanismo de auto‑remediação ou orquestração de runbooks totalmente automatizada. O objetivo é dar visibilidade, estrutura e ferramentas para humanos; automações mais agressivas ficam para ondas posteriores.

### 4.3 Fronteiras com Programas e épicos

Do ponto de vista de fronteiras, a S33 se posiciona assim:

- **Com o Programa 1**, consome o que já existe de ingestão, Console de Fontes, filas e workers, adicionando essencialmente uma camada de observabilidade aplicada e UI de operação. O cockpit não é “mais uma aplicação desconectada”, mas uma lente sobre o que já foi construído.

- **Com o Programa 2**, observa o comportamento de agentes e pipelines de interpretação/classificação, mas não redesenha o modelo de Claims ou de Entidades. A fronteira é clara: a S33 quer enxergar estados e erros desses componentes, não redefinir sua semântica.

- **Com o Programa 3**, monitora jobs e fluxos que impactam Truth‑DB e System of Blocks, mas não altera regras de promoção de fatos, mecanismos de contestação ou estrutura de blocos. Qualquer alteração em Truth‑DB continua pertencendo a épicos próprios.

- **Com o Programa 4**, a S33 produz um produto interno (OracleOps Cockpit) que pode ser visto como parte do portfólio do Programa 4, mas com público‑alvo restrito a operadores e maintainers. Interfaces externas, contratos públicos e produtos voltados a jornalistas ou cidadãos continuam fora do recorte imediato.

- **Com outros épicos além do E28**, a S33 atua como infraestrutura operacional: ela prepara terreno para que épicos futuros encontrem um ambiente em que seja possível acompanhar saúde, reagir a falhas e aprender com incidentes. A sprint, no entanto, não puxa para si escopo de evolução funcional desses épicos.

### 4.4 Critérios para aceitar ou rejeitar mudanças de escopo durante a sprint

Finalmente, a S33 adota alguns critérios explícitos para avaliar propostas de mudança de escopo ao longo da execução:

- Uma mudança é **aceitável** se: 
  - melhora diretamente a capacidade do cockpit de descrever a saúde do recorte escolhido,
  - torna mais nítido o fluxo de incidentes ou elimina ambiguidade crítica nesse fluxo,
  - simplifica a vida do operador em situações de stress, sem introduzir complexidade estrutural desnecessária.

- Uma mudança deve ser **rejeitada ou empurrada para backlog** se:
  - introduz um novo tipo de complexidade (novo serviço, nova camada, novas dependências) sem impacto proporcional na operação do recorte da S33,
  - tenta expandir a cobertura do cockpit/fluxo de incidentes para além do recorte, apenas por ansiedade de “pegar tudo de uma vez”,
  - desvia a equipe para temas de arquitetura profunda ou produto externo que pertencem claramente a outros épicos.

Com esse escopo, recorte e fronteiras explícitos, a Sprint 33 se protege contra o risco clássico de sprints “de operação” que tentam consertar tudo e não conseguem consertar nada. Ela se foca em tornar _operável_ uma parte específica, porém crítica, do Inspectah — e em estabelecer um modelo que possa ser estendido de forma controlada nas sprints seguintes.