# 6.2 – Riscos, Sinais e Mitigações (Verdade & Interpretação / Casos Inspectah) – v2 extremo

Este 6.2 v2 extremo é a versão aprofundada e consolidada do mapa de riscos da trilha **Verdade & Interpretação**, com foco em:

- núcleo de verdade (Truth‑DB, comitês, Debunker);
- Case Layer (`app/cases/`) e configs em `docs/cases/`;
- Casos Inspectah, coleções e cockpit mínimo de produto.

Aqui o squad inteiro alinhou percepção técnica, de produto e de governança. A meta é simples: **deixar muito claro onde o sistema pode falhar e qual é o plano para que isso não vire desastre**.

Estrutura:

- 6.2.1 – Modelo de risco adotado;
- 6.2.2 – Riscos técnicos (RT);
- 6.2.3 – Riscos de dados/verdade (RD);
- 6.2.4 – Riscos de produto/UX (RP);
- 6.2.5 – Riscos organizacionais/processo (RO);
- 6.2.6 – Matriz sintética (probabilidade × impacto × horizonte);
- 6.2.7 – Recomendações finais do squad.

---

## 6.2.1 – Modelo de risco adotado

Para esta sprint, o Squad Verdade & Interpretação adotou um modelo simples e prático:

- **RT*** – riscos técnicos (arquitetura, código, pipelines, observabilidade);
- **RD*** – riscos de dados/verdade (consistência, deriva, integridade factual);
- **RP*** – riscos de produto/UX (como a verdade é percebida e utilizada por A/B/C);
- **RO*** – riscos organizacionais/processo (gente, fluxo, governança de decisão).

Cada risco traz:

- descrição objetiva;
- sintomas/sinais precoces observáveis;
- impacto esperado (técnico, de produto, reputacional);
- mitigações sugeridas (curto prazo – S23–S25; médio prazo – Fase 2: Sistema de Blocos, reputação, comunidade, on‑chain).

---

## 6.2.2 – Riscos técnicos (RT)

### RT1 – Case Layer acoplada demais ao modelo atual da Truth‑DB

**Descrição**  
`app/cases/` depende de invariantes implícitos da Truth‑DB (tipos de estado, relação Claim→TruthRecord, existência de um FACT predominante por claim, formato de eventos). Mudanças na Truth‑DB ou nos comitês podem quebrar a resolução de casos ou gerar timelines incoerentes se não forem coordenadas.

**Sinais precoces**  
- alterações em modelos/estados da Truth‑DB exigindo ajustes manuais e espalhados na Case Layer;
- falhas em testes de casos logo após refactors na Truth‑DB;
- proliferação de condicionais do tipo `if state == "FACT" else ...` por toda a Case Layer.

**Impacto**  
- instabilidade da API de casos/coleções;
- regressões silenciosas (casos aparentemente válidos, mas com dados errados ou incompletos);
- aumento do custo de manutenção e medo de evoluir a Truth‑DB.

**Mitigações (curto prazo – S23–S25)**  
- consolidar `app/cases/resolver.py` como **único ponto** onde a Truth‑DB é interpretada para casos (sem lógica duplicada em outros módulos);
- documentar, em anexo técnico, as invariantes de Truth‑DB assumidas pela Case Layer;
- criar testes de contrato Truth‑DB ↔ Case Layer, rodando em gates futuros (por exemplo, S23/S24);
- incluir automaticamente testes de casos em qualquer change que altere modelos/estados de truth.

**Mitigações (médio prazo – Fase 2)**  
- mover parte das invariantes para contratos formais (ex.: schemas versionados, DSL de estados de truth);
- avaliar introdução de uma camada intermediária (ex.: "Truth View API") entre Truth‑DB e Case Layer, padronizando o que vem de baixo.

---

### RT2 – Observabilidade insuficiente nos endpoints de casos/coleções

**Descrição**  
A observabilidade atual prioriza ingestão, pipelines de truth, Debunker e comitês. A Case Layer e seus endpoints (`/api/cases*`, `/api/collections*`) ainda não têm métricas e logs dedicados suficientes para antecipar problemas.

**Sinais precoces**  
- relatos de lentidão ao carregar `/cases`/`/collections` sem dados objetivos de latência;
- dificuldade de identificar payloads gigantes (casos com timelines enormes, coleções com muitos casos);
- erro 500 genérico em casos específicos, com logs pouco estruturados.

**Impacto**  
- degradação invisível da experiência de produto (especialmente para A/B);
- dificuldade de distinguir problemas da Case Layer de problemas em ingestão/Truth‑DB;
- maior risco de incidentes em demos e pilotos com usuários reais.

**Mitigações (curto prazo – S23–S25)**  
- adicionar métricas específicas: latência (p95/p99), taxa de erro, tamanho médio de payload para `/api/cases*` e `/api/collections*`;
- instrumentar logs estruturados de resolução de casos: contagem de claims carregadas, eventos na timeline, chamadas a Truth‑DB por caso;
- criar pelo menos um painel básico focado na Case Layer, separado dos painéis de ingestão.

**Mitigações (médio prazo – Fase 2)**  
- incluir métricas de uso (casos mais acessados, coleções mais vistas, endpoints mais pressionados) como entrada para priorização de curadoria e UI;
- conectar métricas de produto (Cap. 5) com observabilidade (ex.: correlação entre crescimento de casos e aumento de latência).

---

### RT3 – Scripts de check/metrics ainda não cobrem cenários extremos

**Descrição**  
`sXX_cases_check` e `sXX_cases_metrics` validam integridade básica e geram métricas iniciais, mas ainda não exercitam limites (casos muito grandes, coleções enormes, combinações exóticas de estados).

**Sinais precoces**  
- casos específicos quebrando UI ou API sem serem sinalizados pelos scripts;
- coleções com dezenas/centenas de casos degradando usabilidade e performance sem alertas;
- necessidade recorrente de correção manual de casos após incidentes em demonstrações.

**Impacto**  
- sensação de que gates de produto estão “verdes demais” comparado à realidade;
- maior risco de incidentes em ambiente real;
- retrabalho de curadoria e desenvolvimento após falhas visíveis para usuários.

**Mitigações (curto prazo – S23–S25)**  
- expandir checks para incluir limites claros: número máximo de eventos por caso, tamanho de campos, número máximo de casos por coleção, etc.;
- criar cenários artificiais de stress (casos e coleções extremos) e garantir que scripts os exercitem;
- registrar incidentes reais como casos de teste para alimentar novas regras.

**Mitigações (médio prazo – Fase 2)**  
- integrar checks de limites com o planejamento de curadoria (por exemplo, sinalizar coleções que estão crescendo demais e sugerir reestruturação).

---

## 6.2.3 – Riscos de dados/verdade (RD)

### RD1 – "Case drift": casos saindo de fase com a Truth‑DB

**Descrição**  
A Truth‑DB é dinâmica: novas evidências chegam, comitês revisitam decisões, Debunker levanta issues. Se casos canônicos não forem reconciliados periodicamente, permanecem mostrando versões antigas ou parciais da verdade.

**Sinais precoces**  
- diferenças entre o estado de truth exibido na `CaseDetail` e o estado retornado diretamente pela Truth‑DB para a mesma claim;
- curadores anotando, de forma informal, que “esse caso não reflete mais o que sabemos hoje”;
- evidências destacadas em um caso que já foram refutadas ou rebaixadas internamente.

**Impacto**  
- erosão da confiança: usuários atentos percebem divergências;
- risco de decisões externas (artigos, análises, reportagens) baseadas em estados defasados;
- mais difícil defender o Inspectah como referência de verdade atualizada.

**Mitigações (curto prazo – S23–S25)**  
- rodar `sXX_cases_check` de forma programada em staging/produção, com relatórios de divergência;
- guardar, em cada `ResolvedCase`, metadados de última reconciliação com Truth‑DB (timestamp, versão de regras de comitê);
- criar um status “precisa revisão” para casos, alimentado automaticamente por jobs de reconciliação;
- priorizar esses casos em ciclos de curadoria.

**Mitigações (médio prazo – Fase 2)**  
- registrar reconciliações de casos também no Sistema de Blocos (quando existir), criando trilha imutável de revisões de verdade;
- mostrar na UI um indicador mais forte de “este caso está alinhado com estado X da Truth‑DB (âncora Y)”.

---

### RD2 – Divergência entre regras de comitê/Debunker e narrativa de caso

**Descrição**  
Casos são construídos em cima de decisões de comitê e ações do Debunker. Se regras de comitê ou critérios do Debunker evoluem, mas a narrativa do caso não é atualizada, aparecem inconsistências entre “como decidimos” e “como contamos”.

**Sinais precoces**  
- texto de casos que transmite segurança/certeza diferente daquela indicada pelos estados atuais de truth;
- logs e documentos internos de comitê/Debunker falando em incerteza ou disputa, enquanto o caso sugere resolução plena;
- auditores internos relatando dificuldade de conciliar narrativa de caso com trilhas de decisão.

**Impacto**  
- perda de confiança em casos como explicação fiel do processo de decisão;
- risco reputacional em temas sensíveis, com acusação de maquiagem ou viés;
- dificuldade de usar casos como material de transparência em auditorias externas.

**Mitigações (curto prazo – S23–S25)**  
- versionar explicitamente regras de comitê e critérios do Debunker e vincular essa versão a casos canônicos;
- quando regras forem alteradas de forma relevante, gerar lista automática de casos potencialmente impactados;
- revisar esses casos como parte de um mini‑ciclo de curadoria orientado a regras.

**Mitigações (médio prazo – Fase 2)**  
- integrar na Case Layer um resumo curto de “por que o comitê chegou a essa conclusão” com referência explícita às regras em vigor à época;
- ancorar em Sistema de Blocos as decisões de comitê relevantes, com hash de regras aplicadas.

---

### RD3 – Incerteza e disputa mal representadas na superfície de casos

**Descrição**  
A Truth‑DB é capaz de representar estados intermediários, incerteza, disputa, contestação e revisão. A camada de casos, porém, corre o risco de “achatar” isso em uma narrativa mais linear e confiante do que a realidade justifica.

**Sinais precoces**  
- casos que aparentam uma confiança alta em temas onde a Truth‑DB marca disputa ou incerteza;
- pouca ou nenhuma indicação de atores ou fontes em desacordo;
- perguntas recorrentes de usuários sobre “onde aparecem as dúvidas?” ou “quem discorda disso?”.

**Impacto**  
- percepção de que o Inspectah “escolhe um lado” e esconde zonas cinzentas;
- perda de nuance essencial em temas científicos/políticos de alta complexidade;
- aumento de ceticismo em relação ao sistema em públicos mais críticos.

**Mitigações (curto prazo – S23–S25)**  
- definir um vocabulário de estados e rótulos visuais/textuais para incerteza, disputa e revisão (badges, cores, frases padrões);
- garantir que a Case Layer exponha, nos payloads, sinais de disputa (ex.: flags, contagem de evidências conflitantes);
- incluir, nos critérios de curadoria, a obrigação de tornar visível a existência de disputas relevantes.

**Mitigações (médio prazo – Fase 2)**  
- modelar views de caso específicas para cenários de alta disputa (ex.: “visão conflito” com foco em divergências);
- integrar com mecanismos públicos de contestação e reputação (quem contestou, com que histórico, com quais evidências).

---

## 6.2.4 – Riscos de produto/UX (RP)

### RP1 – Usuário lendo o caso como "veredicto final" e não como "estado atual"

**Descrição**  
Personas A e, principalmente, B podem interpretar Casos Inspectah como veredictos finais, sem internalizar que se trata de **estado atual da verdade**, sujeito a revisão.

**Sinais precoces**  
- críticas do tipo “o Inspectah errou” em situações onde a verdade foi atualizada posteriormente;
- uso de screenshots de casos em debates como se fossem sentenças definitivas;
- baixa atenção a timestamps ou qualquer indicação de temporalidade.

**Impacto**  
- frustração e acusação de “incoerência” quando casos são revisados;
- dificuldade de educar usuários sobre natureza dinâmica da verdade factual;
- ruído reputacional em temas que evoluem rápido.

**Mitigações (curto prazo – S23–S25)**  
- sempre exibir, de forma destacada, data/hora do estado de truth que o caso está mostrando;
- incluir pequenas notas explicando que casos podem ser revisados à luz de novas evidências;
- quando o sistema tiver histórico de versões de caso, começar a expor isso nem que seja em forma simplificada.

**Mitigações (médio prazo – Fase 2)**  
- oferecer uma view de "histórico do caso" com comparação entre estados anteriores e atuais;
- permitir que usuários naveguem por “versões” ancoradas em blocos (quando Sistema de Blocos estiver ativo).

---

### RP2 – Sobrecarga cognitiva em casos e coleções densos

**Descrição**  
Casos com muitas entidades, eventos e evidências, bem como coleções muito grandes, podem se tornar difíceis de ler, mesmo que tecnicamente corretos.

**Sinais precoces**  
- usuários relatando dificuldade em entender “o que importa” em um caso;
- scroll muito longo em coleções, com cards de caso pouco diferenciados;
- baixa retenção de informação em testes com personas.

**Impacto**  
- abandono da camada de casos/coleções em favor de consultas mais diretas;
- percepção de que o Inspectah é “cansativo” de usar;
- desperdício do esforço de curadoria em materiais que poucos conseguem digerir.

**Mitigações (curto prazo – S23–S25)**  
- reforçar resumos curtos e blocos de destaque ("o que mudou", "por que isso importa");
- limitar a quantidade de informação mostrada inicialmente, oferecendo expansões (accordion, tabs) para detalhes;
- paginar coleções grandes e organizar casos por subtema ou prioridade.

**Mitigações (médio prazo – Fase 2)**  
- introduzir visualizações mais ricas (gráficos, timelines interativas, mapas de relação entre entidades) especialmente em casos complexos;
- permitir que usuários escolham o nível de detalhe (visão rápida vs visão aprofundada).

---

### RP3 – Portfólio de casos desconectado da agenda real

**Descrição**  
Se a seleção de casos canônicos continuar muito centrada em exemplos didáticos, sem levar em conta o que o pipeline de ingestão mostra como mais crítico, o Inspectah corre o risco de ser percebido como irrelevante para o debate público.

**Sinais precoces**  
- usuários perguntando frequentemente por temas que não têm casos dedicados;
- pipeline de ingestão apontando alto volume de menções/conflitos em temas que não aparecem nas coleções;
- dificuldade em responder "o que o Inspectah diz sobre X?" para assuntos quentes.

**Impacto**  
- baixa adoção do sistema por analistas, imprensa e públicos engajados;
- perda de oportunidade de demonstrar o valor do motor de verdade em temas de alto impacto;
- percepção de que o projeto vive em um “laboratório” e não em cima da realidade.

**Mitigações (curto prazo – S23–S25)**  
- usar métricas e sinais do pipeline (menções, conflitos, gaps entre discurso e dados) para alimentar uma lista de temas candidatos a caso;
- reservar, por sprint, capacidade explícita para pelo menos 1–2 casos ligados a temas prioritários;
- revisar trimestralmente o portfólio de casos à luz da agenda pública.

**Mitigações (médio prazo – Fase 2)**  
- integrar melhor ingestão, curadoria e comunidade, permitindo que sinais externos (feedbacks, consultas, contestação) influenciem a priorização de casos.

---

### RP4 – Ausência de canais estruturados de feedback e contestação na UI

**Descrição**  
Hoje, não há mecanismos diretos na interface de casos para que usuários reportem erros, dúvidas ou apresentem evidências alternativas.

**Sinais precoces**  
- feedback chegando por canais informais (e‑mail, redes sociais, conversas privadas);
- dificuldade de rastrear e priorizar sugestões ou denúncias feitas por usuários;
- sensação de “muro” entre quem consome um caso e quem pode corrigi‑lo.

**Impacto**  
- menor sensação de transparência e abertura;
- tempo maior para corrigir problemas reais em casos;
- terreno pouco preparado para uma futura contestação pública estruturada.

**Mitigações (curto prazo – S23–S25)**  
- incluir, mesmo que de forma simples, pontos de entrada para feedback por caso (ex.: botão "reportar problema" que gera issue interna);
- integrar esses feedbacks a Debunker e curadoria com triagem mínima (quem vê, em quanto tempo, qual SLA interna);
- registrar feedbacks de forma que possam alimentar métricas (ex.: número de reports por caso).

**Mitigações (médio prazo – Fase 2)**  
- evoluir esses canais para fluxos formais de contestação, com visibilidade pública controlada, regras de participação e integração com reputação.

---

## 6.2.5 – Riscos organizacionais e de processo (RO)

### RO1 – Dependência de “heróis curadores”

**Descrição**  
A qualidade e o ritmo de criação/atualização de casos canônicos hoje dependem de poucas pessoas com conhecimento profundo do sistema e do domínio.

**Sinais precoces**  
- filas de trabalho de curadoria concentradas em 1–2 nomes;
- dificuldade de treinar novos curadores sem longos períodos de shadowing;
- sprints pressionadas por indisponibilidade desses “heróis”.

**Impacto**  
- risco de burnout;
- limitação no crescimento do catálogo de casos;
- maior probabilidade de viés involuntário (poucos filtros humanos).

**Mitigações (curto prazo – S23–S25)**  
- documentar o fluxo de curadoria como runbook passo‑a‑passo (Cap. 5.4 e 6.1 já iniciam isso);
- padronizar templates de casos para cenários recorrentes (ex.: dado oficial vs discurso, série histórica vs claim pontual);
- criar uma trilha de onboarding para curadores, com exemplos anotados de casos “bem resolvidos”.

**Mitigações (médio prazo – Fase 2)**  
- apoiar curadoria com ferramentas (Case Builder, agentes internos) que reduzam dependência de conhecimento tácito;
- desenhar um modelo de comunidade/curadoria ampliada com reputação e revisão em camadas.

---

### RO2 – Falta de processo formal de revisão periódica de casos

**Descrição**  
Ainda não existe um ritual estruturado para revisitar casos à luz de nova evidência, mudança de regras ou foco temático.

**Sinais precoces**  
- casos antigos permanecendo “intocados” por longos períodos;
- revisões emergenciais feitas às pressas quando um caso volta à pauta pública;
- pouca visibilidade sobre qual parte do catálogo está mais desatualizada.

**Impacto**  
- acúmulo de "dívida de verdade" no catálogo;
- risco de incidentes em temas antigos que voltam ao debate;
- mais esforço necessário para grandes faxinas futuras.

**Mitigações (curto prazo – S23–S25)**  
- instituir ciclos de revisão (por tema, por idade, por criticidade) com metas modestas, porém constantes;
- usar métricas de idade e drift (RD1) para selecionar prioridades;
- registrar revisões como eventos de processo (não apenas commits soltos), indicando quem revisou e por quê.

**Mitigações (médio prazo – Fase 2)**  
- integrar esses ciclos de revisão ao Sistema de Blocos, marcando revisões importantes como eventos ancorados;
- permitir que a comunidade sinalize casos “velhos demais” ou desatualizados.

---

### RO3 – Governança difusa para casos sensíveis

**Descrição**  
Casos que tratam de temas altamente sensíveis (política, crises, temas identitários, etc.) exigem critérios claros de aprovação, mudança e escalonamento. Ainda não há um modelo formal consolidado para isso.

**Sinais precoces**  
- discussões longas e informais sobre alterar ou não um caso sensível;
- falta de registro claro de quem aprovou a forma final de determinado caso;
- incerteza entre curadores sobre quando levar uma mudança para um comitê de governança mais amplo.

**Impacto**  
- risco de percepção de arbitrariedade ou interferência indevida;
- insegurança por parte de curadores na hora de mexer em temas delicados;
- dificuldade de defender decisões em auditorias externas ou perante a comunidade.

**Mitigações (curto prazo – S23–S25)**  
- classificar casos por nível de sensibilidade (baixa, média, alta) com critérios claros;
- definir trilhas de aprovação diferenciadas para casos de alta sensibilidade (ex.: exigência de revisão por mais de um curador, envolvimento do comitê de governança do projeto);
- registrar decisões de alteração/aprovação de casos sensíveis com justificativa sucinta.

**Mitigações (médio prazo – Fase 2)**  
- integrar governança de casos sensíveis com mecanismos de reputação e contestação, mantendo trilhas públicas claras sobre quem decidiu o quê e com base em quais regras.

---

## 6.2.6 – Matriz sintética (probabilidade × impacto × horizonte)

Para priorizar ações, o squad sintetiza os riscos em uma matriz qualitativa:

- **Alta prioridade imediata (S23–S25)**: RT1, RT2, RD1, RD3, RP1, RP3, RO1, RO2.
- **Média prioridade (S23–S25, com desdobramentos em Fase 2)**: RT3, RD2, RP2, RP4, RO3.
- **Principalmente Fase 2 (mas já mapeados)**: aprofundamento de RD3, RP4 e todos os aspectos que envolvem Sistema de Blocos, reputação e contestação pública.

Essa matriz deve aparecer no Cap. 2 (Gates & Métricas) como parte dos riscos e ser revisitada ao final de cada sprint relevante.

---

## 6.2.7 – Recomendações finais do Squad Verdade & Interpretação

1. **Blindar o elo Truth‑DB ↔ Case Layer**  
   Antes de expandir agressivamente o catálogo de casos, garantir que as mudanças em Truth‑DB e comitês passem por contratos claros e testes de contrato na Case Layer.

2. **Tratar "drift de caso" como inimigo nº 1 da confiança**  
   Uma vez que casos são a face pública da verdade, manter casos alinhados à Truth‑DB é obrigatório. RD1 precisa de mitigação estruturada (jobs, métricas, UI) já nas próximas sprints.

3. **Trazer produto/UX para o centro da discussão de risco**  
   Riscos como RP1–RP3 não são "detalhes de tela": eles impactam diretamente como o Inspectah é percebido como projeto civilizatório de verdade. Devem aparecer em ORR e decisões de GO/NO‑GO.

4. **Reduzir dependência de heróis e criar processo vivo de curadoria**  
   RO1 e RO2 deixam claro que, sem processo e ferramentas, a camada de casos não escala. Investir em Case Builder, documentação, trilhas de revisão periódica e formação de curadores é tão estratégico quanto evoluir o backend.

5. **Usar a Fase 2 para atacar riscos que exigem comunidade e âncoras fortes**  
   Riscos ligados a reputação, contestação, governança de casos sensíveis e imutabilidade devem ser tratados como objetivos explícitos da Fase 2 (Sistema de Blocos + reputação + comunidade), não como “nice to have”.

Este 6.2 v2 extremo é, em essência, o mapa de onde o Inspectah pode falhar justamente porque está tentando levar a verdade a sério. Ele complementa o Cap. 5 e o 6.1: mostra que, ao mesmo tempo em que o sistema ganha potência, ele também precisa ganhar responsabilidade em como lida com seus próprios pontos fracos.

