# Sprint 24 – Capítulo 2 (v2)
## Gates, Validação e Evidências do Debunker v0 + Humano‑no‑Loop

### 2.0. Propósito e papel deste capítulo dentro do Sprint Playbook v2

Este capítulo define, de forma exaustiva e operacional, **como a Sprint 24 prova que o Debunker v0 + pipeline humano‑no‑loop está pronto para operar em ambiente real do Inspectah**, sem depender da memória do time nem de interpretações subjetivas.

Ele é o documento‑mãe de validação da Sprint 24 e se encaixa na estrutura do Sprint Playbook v2 da seguinte forma:

- Capítulo 1 (já definido): foca em **contexto macro, escopo e narrativa de produto** da Sprint 24.
- **Capítulo 2 (este documento)**: foca em **gates, critérios de aceitação, métricas, scorecards e evidências**, amarrando tudo o que será considerado “prova objetiva” de que o Debunker v0 está em condições de participar do processo de verdade do Inspectah.
- Capítulos 3–6: se apoiarão neste capítulo para desenhar arquitetura, filemap, execução e ORR, usando os gates aqui descritos como fonte de verdade.

Na prática, este capítulo responde a três perguntas centrais:

1. **Quais perguntas críticas sobre o Debunker v0 a Sprint 24 precisa responder?** (Por exemplo: o sistema sabe quando acionar humano? As decisões são boas? A fila não apodrece? É auditável?)
2. **Quais gates formais S24_G* vão garantir que essas perguntas sejam respondidas de forma objetiva, com métrica, scorecard e evidência armazenada?**
3. **Como esses gates se conectam com S23 (interpretação/classificação) e S25 (Truth‑DB/governança), garantindo que ninguém “fure a fila” da verdade?**

Este capítulo é escrito para ser usado por:

- **Squad Verdade & Interpretação** (Pearl, Stonebraker, Norvig, Percy + PO), como contrato de qualidade da Sprint 24.
- **Squad de Ingestão (S21–S22)** e **Squad Timeline/XRay (S19–S20)**, como referência de integração de casos e visualização.
- **Conselho do Inspectah** (Jobs, Kleppmann, Vitalik, etc.) no momento de GO/NO‑GO da Sprint 24, como fonte única de verdade para avaliação de maturidade do Debunker v0.

A partir deste capítulo, **nenhuma entrega da Sprint 24 será considerada DONE se não tiver um gate associado (S24_G0…S24_G6) com scorecard verde e evidência registrada nas pastas oficiais**.

---

### 2.1. Visão formal dos gates S24_G0…S24_G6

A Sprint 24 terá **sete gates principais**, numerados de S24_G0 a S24_G6. Eles cobrem, em conjunto, três dimensões:

- Dimensão **estrutural** (modelo de truth, fila, escopo de casos).  
- Dimensão de **qualidade de decisão** (Debunker + humano, sob métricas objetivas).  
- Dimensão **operacional** (observabilidade, demo integrada e sanidade de operação).

A seguir, cada gate é descrito em nível macro, com foco em propósito, perguntas que responde, responsabilidades e pontos de integração. Os detalhes numéricos (thresholds, datasets mínimos, comandos exatos, filemap completo) serão aprofundados nos subcapítulos 2.1 a 2.4.

#### S24_G0 – Escopo, trilha de casos e alinhamento S23/S24/S25

**Objetivo:** garantir que a Sprint 24 está validando o Debunker v0 em cima de um **recorte de casos representativo e bem definido**, alinhado com a macro‑visão de S23 (interpretação/classificação), S24 (debunking + humano‑no‑loop) e S25 (Truth‑DB/governança).

Perguntas que este gate responde:

- O conjunto de casos que alimenta a validação da Sprint 24 reflete o tipo de problema que o Debunker v0 vai encontrar em produção?  
- As fronteiras entre S23, S24 e S25 estão claras: o que é trabalho de interpretação, o que é trabalho do Debunker, o que é responsabilidade do Truth‑DB/governança?  
- A trilha de casos (desde a ingestão até a decisão final de verdade) está bem mapeada, com estados e transições que possam ser reconstituídos depois?

Responsáveis diretos:

- Pearl (semântica de claims e estados de verdade envolvidos nos casos).  
- Stonebraker (onde esses casos vivem, como são versionados e consultados).  
- PO da Sprint 24 (garantia de representatividade de negócio: notícias, dados oficiais, eventos políticos, etc.).

Saídas esperadas:

- Lista de **datasets de casos** usados para validação da Sprint 24, com rótulos como:
  - `S24_CASESET_GOLDEN_NEWS_v1` (conjunto de notícias com ground truth histórico consolidado).  
  - `S24_CASESET_CONTROVERSIAL_POLITICS_v1` (casos com alta ambiguidade, para testar disputa).  
  - `S24_CASESET_FAKE_VS_REAL_v1` (casos misturando desinformação clara, meia‑verdade e fato sólido).
- Documento de fronteira S23/S24/S25 para estes casesets, indicando:
  - Quais artefatos vêm prontos de S23 (claims interpretados, entidades, relações, rascunho de estado inicial).  
  - Quais decisões são exclusivas do Debunker v0 (abrir disputa, pedir mais evidência, rebaixar estado etc.).  
  - Quais eventos são entregues à S25 como verdades consolidadas ou mudanças de estado.
- Um **scorecard S24_G0_scope_alignment.json** contendo, no mínimo: id dos casesets, contagens, distribuição aproximada por tipo de caso, checklist de fronteiras validadas e assinatura (digital ou lógica) do squad responsável.

#### S24_G1 – Modelo de estados de verdade em operação no Debunker v0

**Objetivo:** verificar se o Debunker v0 consegue operar **sem violar o modelo formal de estados de verdade** definido em S23/S25, tanto nas estruturas de dados quanto nas transições em tempo de execução.

Este gate responde, entre outras, a estas perguntas:

- O Debunker v0 só usa estados válidos (por exemplo: UNDER_REVIEW, PROVISIONAL, ESTABLISHED_FACT, UNDER_DISPUTE, RETRACTED, ARCHIVED…)?  
- As transições de estado acionadas pelo Debunker (automatizadas e humanas) respeitam o grafo de transições permitido definido por Pearl e pelo Squad Verdade & Interpretação?  
- Logs e eventos emitidos pelo Debunker (ex.: TruthChangeEvents, DebunkerDecisionEvents) estão semanticamente corretos e sincronizados com o Truth‑DB de S25?

Responsáveis diretos:

- Pearl (modelo formal de estados, invariantes de verdade e regras de transição).  
- Stonebraker (persistência desses estados, impacto em tabelas, índices, histórico).  
- Percy (interface entre comitês de agentes e estados de verdade – ex.: como o resultado de um comitê vira sugestão de transição).

Saídas esperadas:

- Testes automatizados cobrindo:
  - Cenários válidos de mudança de estado (ex.: PROVISIONAL → ESTABLISHED_FACT após reforço de evidências + Debunker verde + humano concordando).  
  - Cenários proibidos (ex.: RETRACTED → ESTABLISHED_FACT sem um caminho de reconciliação especial explicitamente permitido).  
  - Cenários de fallback (ex.: detecção de inconsistência entre versão do estado no Debunker e no Truth‑DB, com rastro claro do conflito).
- Especificação de um **grafo de transição de estados** (podendo ser em formato declarativo – YAML/JSON – versionado em `docs/truth_model/…`, com invariantes explicitados, para servir tanto à implementação quanto à revisão futura).
- Scorecard `out/scorecards/S24_G1_truth_states_model.json` com:
  - Lista de invariantes validados,  
  - Casos de teste mapeados,  
  - Indicação de cobertura mínima acordada (por tipo de transição),  
  - Resultado final (GO/NO‑GO) para o gate.

#### S24_G2 – Fila de casos, orquestração humano‑no‑loop e SLA de triagem

**Objetivo:** garantir que o Debunker v0 gerencia a fila de casos de forma saudável, prioriza corretamente, e aciona humanos no loop com SLAs minimamente aceitáveis.

Perguntas que esse gate endereça:

- A fila de casos do Debunker tem estados internos bem definidos (novo, aguardando agente, aguardando humano, aguardando evidência extra, fechado) e transições coerentes?  
- Em condições normais de carga, qual é o tempo p95 entre um caso ser marcado como “precisa de humano” e receber, de fato, a primeira ação humana?  
- Há mecanismos para evitar que casos fiquem “esquecidos” na fila (starvation)?  
- A priorização leva em conta risco, impacto, relevância (ex.: claims com potencial impacto político maior não ficam atrás de casos triviais)?

Responsáveis diretos:

- Percy (lógica de priorização e integração com comitês de agentes).  
- Norvig (como a fila é consultada, como as queries de operação funcionam, como os humanos navegam a fila).  
- Stonebraker (estrutura física de fila em banco, índices e estratégias para evitar gargalos – ex.: partições por tipo de caso ou data de criação).

Saídas esperadas:

- Definição formal dos **estados da fila** e transições possíveis, versionada em doc técnico e espelhada na implementação.  
- Métricas operacionais de fila, como:
  - `debunker_queue_time_to_first_human_action_p95`  
  - `debunker_queue_open_cases_count_by_priority`  
  - `debunker_queue_stale_cases_over_threshold` (casos acima de um limite de tempo definido).
- Scorecard `out/scorecards/S24_G2_human_loop_queue.json` com:
  - Valores medidos em ambiente de teste e/ou staging,  
  - Comparação com thresholds pactuados na Sprint (por exemplo, p95 < X horas em cenário de carga simulada Y),  
  - Checklist de cenários de starvation e priorização.

#### S24_G3 – Qualidade das decisões (Debunker + humano) em cima de casos goldens e reais

**Objetivo:** medir, com números e não com opinião, se as decisões do Debunker v0 (com apoio humano) são suficientemente boas em comparação com um padrão de verdade de referência.

Aqui entram dois tipos de dataset:

- **Golden set** – casos cuidadosamente curados, em que o estado de verdade e as decisões esperadas já são conhecidos e foram validados pelo Squad Verdade & Interpretação.  
- **Real set** – casos reais, com ruído, ambiguidade e falta de informação, usados para verificar comportamento em situações de incerteza genuína.

Perguntas a responder:

- Para o golden set:
  - Qual a taxa de concordância entre decisões do Debunker v0 (agentes + humano) e as decisões de referência?  
  - Qual a taxa de **erro grave** (por exemplo: aceitar como fato algo que deveria ser contestado, ou rebaixar/retirar algo que é fato histórico consolidado)?
- Para o real set:
  - O Debunker consegue identificar corretamente quando **não tem evidência suficiente** para decidir?  
  - Há sinais de viés sistemático (ex.: contestar demais um tipo específico de claim, ser leniente demais com outro)?

Responsáveis diretos:

- Pearl (definição do que constitui “erro grave” e do que é aceitável como desacordo tolerável).  
- Percy (configuração de comitês de agentes, prompts, critérios de consenso e escalonamento para humano).  
- Norvig (metodologia de amostragem de casos e análises estatísticas de resultados).

Saídas esperadas:

- Documentação dos datasets `S24_CASESET_*` usados neste gate, com:
  - Origem dos casos,  
  - Critérios de seleção,  
  - Labels de referência (para o golden set).
- Métricas como, por exemplo:
  - `debunker_decision_agreement_rate_golden` (proporção de decisões do Debunker alinhadas com referência).  
  - `debunker_decision_severe_misjudgement_rate` (erros graves).  
  - `debunker_decision_uncertainty_flag_rate` (casos em que o sistema corretamente sinaliza “não sei” e pede mais evidências).  
  - Distribuição de tipos de decisão: contestar, manter, pedir mais evidência, rebaixar estado, etc.
- Scorecard `out/scorecards/S24_G3_decision_quality.json` com resumo numérico, links para relatórios detalhados e exemplos de casos relevantes (positivos e negativos).

#### S24_G4 – UX do Debunker, explicabilidade e trilha de evidências (UI + logs)

**Objetivo:** garantir que um humano (analista interno, auditor, stakeholder externo) consegue **entender por que uma decisão do Debunker foi tomada**, navegar a trilha de evidências associadas e verificar a coerência com o modelo de verdade.

Perguntas que esse gate precisa responder:

- A UI do Debunker/humano‑no‑loop permite ver, para cada caso:
  - Claim original e contexto,  
  - Estados de verdade anteriores e atual,  
  - Evidências associadas (links, blocos de dados, referências),  
  - Histórico de ações de agentes e humanos (quem fez o quê, quando e com qual justificativa)?
- As explicações geradas pelos comitês de agentes (quando presentes) são:
  - Linguisticamente claras,  
  - Ancora das em evidências concretas (não apenas em opinião do modelo),  
  - Coerentes com a decisão tomada?
- Os logs estruturados permitem reconstruir toda a cadeia de decisão **sem depender da UI** (ex.: para auditoria off‑line, export ou investigação posterior)?

Responsáveis diretos:

- Norvig (experiência de consulta e explicabilidade).  
- Percy (estrutura das explicações geradas pelos agentes, formato de “racional” associado à decisão).  
- Stonebraker (schema de logs e eventos, formato armazenado no Truth‑DB ou em stores auxiliares).

Saídas esperadas:

- Inventário das telas e fluxos da UI do Debunker relevantes para explicabilidade (ex.: “Visão de Caso”, “Histórico de Decisão”, “Comparação de Evidências”).  
- Padronização mínima de texto de explicação, por exemplo: blocos como “Resumo da decisão”, “Principais evidências usadas”, “Incertezas e limitações”, “Recomendações futuras”.  
- Logs estruturados, por exemplo, em formato JSON, contendo:
  - ids de caso,  
  - id de decisão,  
  - tipo de ator (agente, humano),  
  - justificativa,  
  - referência para evidências,  
  - nova transição de estado.
- Scorecard `out/scorecards/S24_G4_explainability_and_ui.json` contendo:
  - Checklist de telas e fluxos avaliados,  
  - Resultado de sessões de teste com analistas humanos,  
  - Registro de problemas encontrados e resolvidos durante a Sprint.

#### S24_G5 – Observabilidade, métricas e resistência a regressões

**Objetivo:** garantir que o Debunker v0 não é uma “caixa preta”: se algo quebrar ou começar a se comportar de forma estranha, o sistema expõe sinais claros para o time de operação e para os próprios squads.

Perguntas centrais:

- Existem métricas mínimas expostas e acompanhadas, relacionadas ao Debunker v0?  
- É possível detectar rapidamente:
  - Fila parada,  
  - Crescimento anômalo de casos em disputa,  
  - Aumento abrupto de erros de agentes,  
  - Atraso na ação humana?  
- Há testes de regressão que garantem que alterações futuras no Debunker não apagam funcionalidades críticas validadas nesta Sprint?

Responsáveis diretos:

- Stonebraker (exposição e armazenamento de métricas – integração com o stack de observabilidade).  
- Norvig (dashboards e formas de consulta de métricas).  
- Percy (testes de regressão ligados ao comportamento dos comitês de agentes e fluxos da fila).

Saídas esperadas:

- Lista de métricas obrigatórias na Sprint 24 (com nome, descrição, tipo – counter, gauge, histogram – e local onde são expostas).  
- Ao menos um dashboard mínimo para o Debunker v0, com foco em operação diária.  
- Suite de testes de regressão associada ao Debunker (unitários e/ou end‑to‑end), com comandos explícitos e integração em um gate de CI ligado a S24_G5.
- Scorecard `out/scorecards/S24_G5_observability.json` contendo:
  - Lista de métricas implementadas,  
  - Evidence de dashboards funcionando,  
  - Resultados de testes de regressão relevantes.

#### S24_G6 – Demo integrada e sanity check com stakeholders

**Objetivo:** executar uma **demo end‑to‑end do Debunker v0 + humano‑no‑loop**, usando casos reais e goldens, perante stakeholders chave (PO, Squad Verdade & Interpretação, representantes de outros squads), com registro estruturado de feedback e decisão GO/NO‑GO.

Perguntas a responder:

- A experiência de ponta a ponta (do claim ingerido até a decisão final e atualização da timeline) faz sentido, sem “gambiarras manuais” escondidas?  
- Os stakeholders conseguem entender, ao assistir a demo e navegar os casos, como o Debunker toma decisões e quando chama humano?  
- Problemas encontrados durante a demo são de natureza aceitável para uma v0 (ajustes de UX, pequenos refinamentos) ou revelam buracos estruturais (violação de modelo de verdade, impossibilidade de auditar decisões, etc.)?

Responsáveis diretos:

- PO da Sprint 24 (planejamento do roteiro da demo, seleção de casos ilustrativos).  
- Squad Verdade & Interpretação completo (avaliação técnica e conceitual do comportamento).  
- Representantes de squads de Ingestão, Timeline/XRay e Governança (avaliação de integração e impacto no restante do sistema).

Saídas esperadas:

- Roteiro formal da demo (documento versionado), descrevendo:
  - Casos a serem mostrados,  
  - Caminhos a serem percorridos na interface,  
  - Pontos em que o Debunker interage com humano, timeline, Truth‑DB.  
- Registro estruturado do feedback dos stakeholders (por exemplo, em um arquivo `out/evidence/S24_G6_demo_feedback.json`), contendo:
  - Itens de elogio (aspectos que já estão fortes e não devem ser quebrados nas próximas sprints).  
  - Itens de preocupação (pontos que precisam ser tratados antes de considerar “produção” real).  
  - Decisão final da demo (GO, GO com ressalvas, NO‑GO).
- Scorecard `out/scorecards/S24_G6_demo_and_sanity.json` com o resultado da sessão, linkado aos feedbacks e, se houver, aos planos de follow‑up.

---

### 2.2. Relação destes gates com os subcapítulos 2.1–2.4

Seguindo o Sprint Playbook v2, este Capítulo 2 será aprofundado em quatro subcapítulos independentes, cada um como um documento próprio:

- **2.1 – Contexto e problemas de validação a resolver (eixo gates)**  
  Foco em explicar, de forma narrativa e orientada a risco, _por que_ cada gate S24_G0…S24_G6 existe, quais problemas de negócio/técnicos ele previne e quais anti‑objetivos ficam explícitos (o que **não** será coberto na Sprint 24).

- **2.2 – Gates, métricas e DoD detalhados**  
  Foco em transformar a descrição macro de cada gate em um conjunto de critérios numéricos e checklists objetivos: thresholds, tamanho de amostra, cenários obrigatórios, donos, condições de GO/NO‑GO por gate.

- **2.3 – Arquitetura de scorecards e filemap de evidências (Capítulo 2)**  
  Foco em especificar a estrutura exata dos arquivos de scorecard e evidência por gate (nomes, caminhos, formatos, campos mínimos), incluindo integração com scripts de CI e ferramentas de verificação local.

- **2.4 – Execução e validação manual (runbooks de gates)**  
  Foco em mostrar, passo a passo, como qualquer pessoa da equipe consegue rerodar a bateria de gates da Sprint 24: comandos, pré‑requisitos, como interpretar resultados, como reagir a falhas.

Este documento (Capítulo 2 macro) é a **visão de alto nível e o contrato conceitual**. Os subcapítulos 2.1–2.4 são a concretização operacional, cada um com profundidade máxima na sua dimensão.

---

### 2.3. Integração com S23, S25 e com o restante do Inspectah

Para evitar que a Sprint 24 vire um “módulo isolado”, os gates S24_G* são desenhados explicitamente para se alinhar com as sprints diretamente anterior e posterior e com a infraestrutura já existente.

#### Integração com Sprint 23 – Interpretação & Classificação

Os gates da Sprint 24 assumem que:

- S23 produz, para cada caso relevante, um pacote estruturado contendo:
  - Claim(s) interpretados,  
  - Entidades e relações identificadas (pessoas, organizações, eventos, fontes),  
  - Sinal inicial de estado de verdade (por exemplo, UNDER_REVIEW ou PROVISIONAL),  
  - Metadados de risco/impacto (por exemplo, se envolve saúde pública, política, economia etc.).
- S23 já passou por seus próprios gates de qualidade, garantindo que **erros triviais de interpretação** não dominam o pipeline.

Dentro deste contexto:

- **S24_G0** verifica se a forma como esses artefatos chegam ao Debunker está consistente com o esperado (campos, tipos, invariantes).  
- **S24_G1** valida que o Debunker respeita os estados e transições que emergem da saída de S23.  
- **S24_G3** mede situações em que o Debunker corrige ou complementa interpretações de S23, registrando isso de maneira rastreável.

Resultado: ao término da Sprint 24, qualquer análise de erro de decisão deve conseguir responder rapidamente: _“Isso foi culpa de S23 (interpretação errada), S24 (decisão errada) ou S21/S22 (ingestão problemática)?”_.

#### Integração com Sprint 25 – Truth‑DB & Governança

Os outputs principais da Sprint 24 são **decisões** que impactam o estado de verdade dos claims. Esses outputs são consumidos pela Sprint 25 para alimentar o Truth‑DB e o modelo de governança.

No desenho dos gates:

- **S24_G1** garante que as transições de estados aplicadas pelo Debunker são compatíveis com o grafo de Truth‑DB desenhado em S25.  
- **S24_G3** produz métricas e registros de qualidade que servirão como base para políticas de governança (por exemplo, quando reverter decisões, como lidar com histórico de erros, como ponderar confiança em um determinado tipo de decisão).  
- **S24_G4** garante que as explicações e trilhas de evidência estejam em formato adequado para serem referenciadas pelo Truth‑DB.

Os scorecards e evidências produzidos aqui serão insumos diretos para o Capítulo 2 da Sprint 25, que tratará de **gates de verdade/global** (promoção definitiva de fatos, políticas de contestação e reconciliação, etc.).

#### Integração com ingestão (S21–S22) e UI/Timeline/XRay (S19–S20)

Os gates S24_G* também assumem:

- Que a ingestão 2.0 (S21/S22) consegue enfileirar casos para o Debunker com metadados adequados (fonte, tipo, carimbo temporal, identificadores estáveis).  
- Que a timeline e o XRay (S19/S20) são capazes de exibir:
  - Estado atual de verdade,  
  - Histórico de decisões,  
  - Indicações de disputa,  
  - Pistas visuais de que houve intervenção do Debunker (automática ou humana).

Os gates mais diretamente afetados:

- **S24_G2** depende de uma fila que consuma **eventos da ingestão** e devolva sinais para que esses eventos apareçam corretamente na timeline de casos.  
- **S24_G4** verifica se a UI/TL/XRay está refletindo adequadamente a realidade do Debunker, evitando descompasso entre “o que o sistema sabe” e “o que o usuário vê”.  
- **S24_G6** usa cenários de timeline/XRay já existentes como parte da demo integrada.

---

### 2.4. Diretrizes de qualidade, riscos e anti‑padrões deste capítulo

Para garantir que o Capítulo 2 não vire apenas uma lista de intenções vagas, o Squad Verdade & Interpretação estabelece as seguintes diretrizes de qualidade:

1. **Todo gate S24_G* precisa responder a uma pergunta clara de risco.**  
   Se não for possível formular a pergunta em uma frase direta (por exemplo, “Como sabemos que X não acontecerá?”), o gate deve ser redesenhado.

2. **Não há gate sem métrica ou evidência.**  
   Cada gate deve:
   - Ter pelo menos uma métrica relacionada (mesmo que qualitativa, no caso de UX/demo).  
   - Ter pelo menos um scorecard JSON e um diretório de evidências associado.

3. **Gates são ortogonais, mas não independentes.**  
   - G0, G1 e G2 lidam com fundação estrutural (escopo, modelo de estados, fila).  
   - G3 e G4 lidam com qualidade de decisão e explicabilidade.  
   - G5 e G6 lidam com operação e sanidade final.  
   Um gate posterior não pode “compensar” falha estrutural em um gate anterior; nesses casos, a Sprint deve considerar NO‑GO.

4. **Nada de “passar no grito”.**  
   A decisão de GO/NO‑GO da Sprint 24 deve estar ancorada nos scorecards e evidências deste capítulo, não em percepção subjetiva.

5. **Anti‑padrões a evitar:**  
   - Gates cujo único critério é “rodou sem erro e pronto”.  
   - Scorecards sem dados mensuráveis, apenas texto genérico.  
   - Evidências soltas fora da estrutura `out/scorecards/` e `out/evidence/`, dificultando reexecução e auditoria futura.

---

### 2.5. Próximos passos a partir deste capítulo

Com este Capítulo 2 v2 estabelecido, os próximos passos são:

1. **Produzir os subcapítulos 2.1, 2.2, 2.3 e 2.4 da Sprint 24** como documentos independentes, usando este texto como fonte única de verdade conceitual.  
2. **Refinar, para cada gate S24_G0…S24_G6, seus thresholds, datasets mínimos, comandos oficiais e formatos exatos de scorecard** (serão descritos detalhadamente em 2.2 e 2.3).  
3. **Alinhar com S23 e S25 o contrato de entrada/saída de decisões do Debunker** para que não haja retrabalho nas próximas sprints.  
4. **Instrumentar CI/CD e scripts locais** para que rodar os gates S24_G* seja um processo repetível, documentado e confiável.

Quando estes passos estiverem concluídos, a Sprint 24 terá um arcabouço de validação digno de um sistema que pretende tratar verdade como infraestrutura crítica: com perguntas claras, métricas objetivas, evidências versionadas e um caminho transparente entre “um claim chegou” e “o Inspectah decidiu, de forma responsável, o que é verdade, o que está em disputa e o que deve ser retratado.”

