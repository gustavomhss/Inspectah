# Sprint 24 – Capítulo 2.1
## Gates, métricas e critérios de aprovação da Sprint 24 – Versão 2 (Playbook v2)

### 1. Visão geral do papel dos gates na S24

A Sprint 24 existe para tirar o Debunker v0 e o fluxo humano-no-loop do papel, com agentes de interpretação, classificação e contestação funcionando em cima de casos reais, mas ainda em modo protegido. Os gates deste capítulo não são apenas um checklist de “passou/falhou”. Eles são a espinha dorsal que garante três coisas ao mesmo tempo: segurança epistemológica (nada perigoso escapa), previsibilidade operacional (ninguém se perde no fluxo) e auditabilidade extrema (qualquer decisão pode ser reconstituída em detalhes).

Neste subcapítulo 2.1, o objetivo é responder de forma inequívoca à pergunta: “O que significa, de forma concreta e mensurável, dizer que a Sprint 24 foi BEM-SUCEDIDA?”. A resposta se materializa em três camadas: desenho detalhado dos gates T0 a T8 específicos da S24, definição das métricas associadas a cada gate e critérios de GO/NO-GO tanto por gate quanto na consolidação final da sprint.

Tudo que será implementado nos capítulos seguintes (arquitetura, filemap, execução, evidências) precisa apontar para estes gates. Se não existe um gate associado, ou uma métrica clara, aquele trabalho é considerado “ornamental” e deve ser removido ou postergado.

### 2. Mapa dos gates T0–T8 específico da Sprint 24

Nesta sprint, os gates T0–T8 seguem a filosofia do Sprint Playbook v2, mas são especializados para o contexto Debunker v0 + humano-no-loop. O mapa conceitual é o seguinte.

T0 – Gate de sanidade de escopo, riscos e alinhamento com a S23 e S25. Garante que o que estamos chamando de “Debunker v0” não é nem um brinquedo acadêmico simplista nem um monstro impossível de operar. T0 valida que o escopo se mantém dentro do envelope: sistema funcional de contestação com comitês de agentes e humano-no-loop, aplicado a timelines de casos, integrado ao que S23 produziu e consistente com o que S25 vai formalizar como Truth-DB e governança de verdade.

T1 – Gate de design de fluxo e entidades. Avalia se o fluxo Debunker v0 está totalmente especificado: entradas, estados, transições, papéis humanos, papéis dos agentes, tipos de evidência, contratos de interface com o restante do Inspectah. T1 responde à pergunta: “Se eu der apenas este capítulo para uma equipe externa, eles conseguiriam desenhar o mesmo fluxo, com os mesmos estados e responsabilidades, sem improvisar?”

T2 – Gate de arquitetura técnica e filemap. Verifica se a arquitetura proposta, os componentes, os acoplamentos e o filemap estão completos, consistentes e realistas. Aqui se mede se a Sprint 24 tem uma decomposição saudável em serviços, módulos, pastas, testes, scripts e pipelines, de forma a reduzir a chance de refatorações destrutivas nas próximas sprints.

T3 – Gate de implementação de fluxo mínimo funcional. Garante que o Debunker v0 funciona de ponta a ponta, ainda que com casos controlados, em um modo “laboratório supervisionado”. Desde a chegada de um caso contestável até a geração de uma decisão (manter, rebaixar, promover, marcar como disputado), passando pelos comitês de agentes e pelas interações com humanos revisores, tudo precisa ser navegável, demonstrável e reproduzível.

T4 – Gate de qualidade epistêmica e segurança contra erro grosseiro. Aqui se mede se o sistema realmente ajuda a reduzir erro de interpretação, fake news, leitura tendenciosa e confusão de evidências, e se impõe restrições claras para que nenhuma decisão potencialmente danosa seja tomada sem evidência suficiente e sem trilha de responsabilidade.

T5 – Gate de UX, explainability e fluxo do revisor humano. Avalia se o revisor humano enxerga o necessário para tomar boas decisões e se o sistema não sufoca o operador com ruído, tampouco “esconde” a complexidade de forma enganosa. É o gate que garante que o humano continua sendo o adulto na sala, com clareza e controle.

T6 – Gate de observabilidade, métricas e scorecards de operação. Verifica se o Debunker v0 nasce já com telemetria adequada: métricas de volume, tempo de ciclo, taxa de contestação, erro detectado, divergência entre agentes, reversões de decisão, tudo consolidado em scorecards claros para operação e governance.

T7 – Gate de integração com o pipeline de ingestão e timelines. Avalia se o Debunker v0 se encaixa sem fricção no fluxo maior do Inspectah: ingestão S21–S22, classificação S23, timelines e XRay S19, e a futura Truth-DB da S25. Este gate testa se as interfaces de entrada e saída do Debunker são concretas, documentadas e robustas.

T8 – Gate de GO/NO-GO conceitual, ético e operacional. O último gate consolida todos os anteriores e responde a três perguntas: podemos ligar o Debunker v0 para casos reais sob um regime de uso limitado e supervisionado? Sabemos exatamente o que ele pode e não pode fazer? Sabemos como desligá-lo, reverter decisões e aprender com os erros sem perder rastreabilidade?

### 3. Métricas centrais por gate (camada quantitativa e qualitativa)

Cada gate terá indicadores primários e secundários. Para este subcapítulo, o objetivo não é entrar no nível de fórmula de cada métrica, mas garantir que a Sprint 24 tenha um esqueleto quantitativo sólido o bastante para guiar o design detalhado dos capítulos seguintes.

Para o T0, as métricas centrais são: grau de alinhamento com o escopo aprovado no macro da S24, número de dependências críticas com outras sprints ainda não resolvidas, clareza documentada de in e out do Debunker v0. A saída esperada é um scorecard de sanidade que mostra se o escopo está compacto, coerente e livre de dependências impossíveis.

Para o T1, medimos o nível de completude do fluxo de estados e transições, a clareza dos papéis (quem faz o quê, humano versus agente), a consistência das entidades de dados e a ausência de “caixas mágicas” não especificadas. Uma métrica prática aqui é: quantos estados e transições ainda são descritos de maneira vaga ou com termos ambíguos.

No T2, o foco é em métricas de arquitetura: acoplamento entre componentes, número de fronteiras bem definidas, proporção de módulos com contratos claros (interfaces, tipos, schemas) versus módulos “não tipados”, clareza do filemap (arquivos de código, testes, scripts e docs de suporte). A meta é que a maior parte da complexidade esteja explicitamente documentada e particionada.

Para o T3, as métricas giram em torno de funcionamento end-to-end: taxa de sucesso de um conjunto de cenários de teste de contestação, tempo de ciclo de um caso (do registro à decisão), taxas de erro do fluxo (exceções, estados inválidos, falhas de chamadas entre módulos). Também se avalia a cobertura de cenários: pelo menos um caso para cada tipo de contestação relevante.

No T4, medimos qualidade epistêmica: taxa de decisões revisadas pelo humano por falta de evidência, quantidade de vezes em que os agentes divergem de forma extrema, número de decisões revertidas após revisão por serem logicamente inconsistentes. O objetivo é reduzir decisões frágeis e garantir que a configuração default do sistema seja “errar para o lado da cautela”.

Em T5, o foco é no humano: clareza de telas, densidade de informação apropriada, número de cliques até a visão completa de um caso contestado, nitidez das explicações dos agentes e do histórico de decisões. Idealmente, o revisor deve conseguir entender “onde estou, o que aconteceu, o que os agentes sugerem, o que posso decidir” em poucos segundos.

No T6, as métricas incluem: completude do conjunto de métricas instrumentadas, presença de dashboards úteis, facilidade de exportar dados para auditoria, latência de coleta de métricas em relação aos eventos reais, clareza dos scorecards automáticos gerados para a sprint.

Em T7, medimos integração: número de falhas de integração em cenários reais, compatibilidade de schemas entre Debunker, ingestão, classificação e timelines, ausência de transformações ad hoc e caminhos paralelos. Não pode haver “bypass” ou atalhos manuais que fujam ao fluxo oficial.

Por fim, no T8, medimos prontidão global: quantos gates passaram com folga versus “no limite”, nível de confiança da equipe responsável, clareza dos limites de uso do Debunker v0, existência de um plano explícito de rollback ou fallback para antes da S24 caso algo dê errado.

### 4. Critérios de GO/NO-GO e relação com os demais capítulos da S24

Os critérios de GO/NO-GO da S24 não são puramente numéricos. Eles combinam métricas objetivas com juízo de valor do Squad Verdade & Interpretação e do conselho ampliado do Inspectah. Ainda assim, a regra é clara: nenhuma decisão estratégica de GO pode ser tomada sem scorecards, evidências e explicações alinhadas com este capítulo.

Para cada gate T0–T7, os critérios são definidos como um conjunto de condições obrigatórias e condições desejáveis. Condições obrigatórias são aquelas que, se não forem atendidas, travam a sprint ou reduzem explicitamente o escopo. Condições desejáveis entram como débito técnico registrado, com donos e prazos claros.

O T8 consolida tudo e exige três artefatos: um scorecard final da Sprint 24, um relatório narrativo de riscos e limitações conhecidas do Debunker v0 e um mapa de integração com a S25, mostrando como os estados e decisões desta sprint serão traduzidos para a Truth-DB e para a política de promoção de verdade.

A relação com os demais capítulos é direta. O Capítulo 1 (macro) definiu o porquê e o que da Sprint 24. Este Capítulo 2.1 define o “como vamos saber que chegamos lá”. O Capítulo 2.2 detalhará a tabela de métricas, formatos e local de armazenamento. O Capítulo 2.3 amarrará os gates à arquitetura e ao filemap concreto. O Capítulo 2.4 descreverá o plano de execução e as evidências necessárias para comprovar o cumprimento destes gates.

Nenhuma linha de código, nenhum endpoint, nenhum painel e nenhum fluxo de UX da Sprint 24 deve existir sem ser rastreável para ao menos um gate aqui definido. Se algo não se alinha a nenhum gate, deve ser repensado, reescopado ou removido. Esta é a armadura de qualidade da S24.

